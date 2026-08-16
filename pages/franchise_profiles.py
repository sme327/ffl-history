"""Franchise Profiles page — 25-year franchise lineages."""
import streamlit as st
import pandas as pd
from utils.data import (
    load_all, get_franchise_stats, get_franchise_steward_periods,
    get_champions, get_playoff_result_for_team,
    get_franchise_legends, get_franchise_profile, get_draft_picks_with_pos,
    MANAGER_EMOJI, MANAGER_COLORS, CURRENT_SEASON,
)
from utils.styles import inject_css, render_nav, render_page_footer, metric_card, html_table

st.set_page_config(
    page_title="Franchises · The Long Game",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("franchise_profiles")

data = load_all()
franchise_stats = get_franchise_stats()
steward_periods = get_franchise_steward_periods()
champions = get_champions()
tnh = data["team_name_history"]
wm = data["weekly_matchups"]
pg = data["playoff_games"]
fh = data["franchise_history"]
std = data["standings"]

opp_lookup = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

# Maps used throughout the page for original vs successor display
_sp_sorted = steward_periods.sort_values(["franchise_id", "start_season"])
_first_mgr_by_fid: dict[str, str] = (
    _sp_sorted.drop_duplicates("franchise_id", keep="first")
    .set_index("franchise_id")["manager_name"]
    .to_dict()
)
_curr_start_by_fid: dict[str, int] = (
    _sp_sorted.drop_duplicates("franchise_id", keep="last")
    .set_index("franchise_id")["start_season"]
    .astype(int)
    .to_dict()
)

# ── PAGE TITLE ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-page-title">Franchise Profiles</div>
    <div class="tl-page-subtitle">Living histories spanning the full 25-year arc of the league.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── ALL-FRANCHISE SUMMARY ────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Overview</div>'
    '<div class="tl-section-title">All Franchises</div>',
    unsafe_allow_html=True,
)

summary_rows = []
for _, fs in franchise_stats.sort_values("championships", ascending=False).iterrows():
    mgr = fs["current_manager"] if fs["current_manager"] and str(fs["current_manager"]) != "nan" else "—"
    emoji = MANAGER_EMOJI.get(mgr, "🏟️")
    champ_str = ("🏆 " * int(fs["championships"])).strip() if fs["championships"] > 0 else "—"
    _fid = fs["franchise_id"]
    _is_original = _first_mgr_by_fid.get(_fid) == mgr
    if _is_original:
        _mgr_cell = f"{emoji} {mgr}"
    else:
        _founder = _first_mgr_by_fid.get(_fid, "?")
        _since = _curr_start_by_fid.get(_fid, "?")
        _mgr_cell = (
            f'{emoji} {mgr}'
            f'<br><span style="font-size:0.68rem;color:#4B5563;font-style:italic;">'
            f'est. by {_founder} &nbsp;·&nbsp; since {_since}</span>'
        )
    summary_rows.append([
        (champ_str, "gold"),
        _mgr_cell,
        str(int(fs["established"])),
        f"{int(fs['wins'])}-{int(fs['losses'])}",
        (f"{fs['win_pct']:.3f}" if fs["win_pct"] and str(fs["win_pct"]) != "nan" else "—", ""),
        (str(int(fs["playoff_apps"])), ""),
    ])

st.markdown(
    html_table(["Titles", "Current Manager", "Est.", "All-Time W-L", "Win%", "Playoffs"], summary_rows),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE SELECTOR (de-emphasized) ──────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label" style="margin-bottom:0.5rem;">Select a Franchise to Explore</div>',
    unsafe_allow_html=True,
)

franchise_options = (
    franchise_stats[["franchise_id", "current_manager"]]
    .dropna()
    .sort_values("current_manager")
)
option_map = dict(zip(franchise_options["current_manager"], franchise_options["franchise_id"]))

_sorted_mgr_keys = sorted(option_map.keys())
_default_mgr_idx = _sorted_mgr_keys.index("Eric") if "Eric" in _sorted_mgr_keys else 0
selected_mgr = st.selectbox(
    "SELECT FRANCHISE",
    options=_sorted_mgr_keys,
    index=_default_mgr_idx,
    format_func=lambda n: (
        f"{MANAGER_EMOJI.get(n, '')}  {n}  ·  est. {franchise_stats[franchise_stats['current_manager'] == n]['established'].iloc[0]:.0f}"
        if _first_mgr_by_fid.get(option_map[n]) == n
        else f"{MANAGER_EMOJI.get(n, '')}  {n}  ·  since {_curr_start_by_fid.get(option_map[n], '?')}"
    ),
    label_visibility="collapsed",
)

franchise_id = option_map[selected_mgr]
fstat = franchise_stats[franchise_stats["franchise_id"] == franchise_id].iloc[0]
periods = steward_periods[steward_periods["franchise_id"] == franchise_id].reset_index(drop=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FRANCHISE DATA — all derivation lives in utils.data.get_franchise_profile()
# ══════════════════════════════════════════════════════════════════════════════

profile = get_franchise_profile(franchise_id)
_totals = profile["totals"]

est = profile["established"]
first_mgr = profile["first_manager"]
curr_mgr = profile["current_manager"]
all_fran_seasons = profile["seasons"]
fran_champ_seasons = profile["championship_seasons"]
fran_ru_seasons = profile["runner_up_seasons"]
fran_3rd_seasons = set(profile["third_place_seasons"])
pl_seasons = set(profile["playoff_seasons"])
n_finals_apps = _totals["finals_apps"]
max_streak = _totals["longest_playoff_streak"]
winning_seasons = _totals["winning_seasons"]
best_steward_name = profile["best_steward"]

mgr_by_season = {r["season"]: r["manager"] for r in profile["season_records"]}
champ_steward_map = {s: mgr_by_season.get(s, "") for s in fran_champ_seasons}

steward_stats_map = {
    st_["manager"]: {
        "w": st_["wins"], "l": st_["losses"],
        "pl_apps": st_["playoff_apps"], "champs": st_["championships"],
        "seasons": st_["seasons"],
    }
    for st_ in profile["stewards"]
}

_peaks = profile["peaks"]
best_rec_row = _peaks["best_record"]
most_pf_row = _peaks["most_points"]
best_week_row = _peaks["best_week"]
rivalry_combined = profile["rivals"]

# ── FRANCHISE HERO CARD ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label" style="margin-bottom:0.5rem;">Franchise Identity</div>',
    unsafe_allow_html=True,
)

hero_emoji = MANAGER_EMOJI.get(curr_mgr, "🏟️")
total_champs = int(fstat["championships"])
years_active = f"{est} – Present"
trophies_html = ("🏆 " * total_champs).strip() if total_champs > 0 else "Still Hunting"

stat_block = lambda val, lbl: (
    f'<div style="text-align:center;min-width:90px;">'
    f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.9rem;color:#D4AF37;line-height:1;">{val}</div>'
    f'<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:2.5px;text-transform:uppercase;margin-top:0.15rem;">{lbl}</div>'
    f'</div>'
)

st.markdown(
    f"""
    <div class="tl-champion-card" style="padding:2.5rem 2rem;">
        <div style="font-size:3.5rem;margin-bottom:0.3rem;">{hero_emoji}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:5px;text-transform:uppercase;">Franchise &nbsp;·&nbsp; Established {est}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:3rem;color:#D4AF37;letter-spacing:4px;line-height:1;margin:0.4rem 0 0.15rem;">The {curr_mgr} Franchise</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.85rem;color:#F5F5F5;margin-bottom:0.25rem;">{trophies_html}</div>
        <hr style="border:none;height:1px;background:rgba(184,144,46,0.3);margin:1.2rem 0 1.4rem;">
        <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;">
            {stat_block(total_champs, "Championships")}
            {stat_block(n_finals_apps, "Finals Apps")}
            {stat_block(int(fstat['playoff_apps']), "Playoff Apps")}
            {stat_block(winning_seasons, "Winning Seasons")}
        </div>
        <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;margin-top:1.1rem;">
            {stat_block(f"{int(fstat['wins'])}-{int(fstat['losses'])}", "All-Time Record")}
            {stat_block(f"{fstat['win_pct']:.3f}" if pd.notna(fstat.get('win_pct')) else '—', "Win Pct")}
            {stat_block(years_active, "Active")}
            {stat_block(f"{max_streak}{'&nbsp;Szns' if max_streak > 0 else ''}" if max_streak > 0 else "—", "Best PO Streak")}
        </div>
        <hr style="border:none;height:1px;background:rgba(184,144,46,0.3);margin:1.4rem 0 1rem;">
        <div style="display:flex;justify-content:center;gap:3rem;flex-wrap:wrap;">
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;">First Steward</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#F5F5F5;font-weight:600;margin-top:0.1rem;">{MANAGER_EMOJI.get(first_mgr, '')} {first_mgr}</div>
            </div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:rgba(184,144,46,0.4);align-self:center;">→</div>
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;">Current Steward</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#D4AF37;font-weight:600;margin-top:0.1rem;">{hero_emoji} {curr_mgr}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE STORY ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Legacy</div>'
    '<div class="tl-section-title">The Story of the Franchise</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="tl-franchise-story">{profile["story"]}</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── STEWARD TIMELINE (expanded) ─────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Franchise Lineage</div>'
    '<div class="tl-section-title">Stewards of the Franchise</div>',
    unsafe_allow_html=True,
)

# Expanded steward cards
tl_items_html = []
for i, (_, p) in enumerate(periods.iterrows()):
    mgr = p["manager_name"]
    is_current = (mgr == curr_mgr)
    curr_cls = "current" if is_current else ""
    e = MANAGER_EMOJI.get(mgr, "👤")
    yr_range = f"{int(p['start_season'])}–Present" if is_current else f"{int(p['start_season'])}–{int(p['end_season'])}"
    ss = steward_stats_map.get(mgr, {})
    w, l = ss.get("w", 0), ss.get("l", 0)
    pl = ss.get("pl_apps", 0)
    champs = steward_stats_map.get(mgr, {}).get("champs", 0)
    szns = ss.get("seasons", 0)
    trophy_html = f'<div style="font-size:1rem;margin-top:0.3rem;">{"🏆" * champs}</div>' if champs else ""
    tl_items_html.append(
        f'<div class="tl-steward-rich {curr_cls}">'
        f'<div class="tl-steward-rich-avatar">{e}</div>'
        f'<div class="tl-steward-rich-name">{mgr}</div>'
        f'<div class="tl-steward-rich-years">{yr_range}</div>'
        f'{trophy_html}'
        f'<div class="tl-steward-rich-divider"></div>'
        f'<div style="display:flex;flex-direction:column;gap:0.35rem;">'
        f'<div style="text-align:center;">'
        f'<div class="tl-steward-rich-stat-val">{w}-{l}</div>'
        f'<div class="tl-steward-rich-stat-lbl">Record</div>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-around;gap:0.3rem;">'
        f'<div><div class="tl-steward-rich-stat-val">{pl}</div><div class="tl-steward-rich-stat-lbl">Playoffs</div></div>'
        f'<div><div class="tl-steward-rich-stat-val">{szns}</div><div class="tl-steward-rich-stat-lbl">Seasons</div></div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    if i < len(periods) - 1:
        tl_items_html.append('<div class="tl-connector" style="margin-top:50px;"></div>')

st.markdown(
    f'<div style="display:flex;align-items:flex-start;gap:0;padding:0.5rem 0;overflow-x:auto;">{"".join(tl_items_html)}</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── STEWARD BREAKDOWN TABLE ──────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">By Steward</div>'
    '<div class="tl-section-title">Era Breakdown</div>',
    unsafe_allow_html=True,
)

steward_rows = []
for _, p in periods.iterrows():
    mgr = p["manager_name"]
    yrs = int(p["years"])
    yr_label = f"{int(p['start_season'])}–Present" if mgr == curr_mgr else f"{int(p['start_season'])}–{int(p['end_season'])}"
    ss = steward_stats_map.get(mgr, {})
    w, l = ss.get("w", 0), ss.get("l", 0)
    pl_apps_era = ss.get("pl_apps", 0)
    win_pct_era = f"{w / (w + l):.3f}" if (w + l) > 0 else "—"
    pl_pct_era = f"{pl_apps_era / yrs:.0%}" if yrs > 0 else "—"
    champs = steward_stats_map.get(mgr, {}).get("champs", 0)
    champ_str = "🏆" * champs if champs else "—"
    e = MANAGER_EMOJI.get(mgr, "")
    steward_rows.append([
        (yr_label, "gold"),
        f"{e} {mgr}",
        str(yrs),
        f"{w}-{l}",
        (win_pct_era, ""),
        (pl_pct_era, ""),
        (champ_str, "gold"),
    ])

_, col, _ = st.columns([1, 3, 1])
with col:
    st.markdown(
        html_table(["Era", "Steward", "Seasons", "Record", "Win%", "Pl%", "Titles"], steward_rows),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE RECORDS ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Trophy Case</div>'
    '<div class="tl-section-title">Franchise Records</div>',
    unsafe_allow_html=True,
)

def _record_card(icon, label, headline, sub=""):
    return (
        f'<div class="tl-card" style="text-align:center;padding:1.5rem 1rem;">'
        f'<div style="font-size:1.6rem;margin-bottom:0.4rem;">{icon}</div>'
        f'<div class="tl-section-label">{label}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.6rem;color:#D4AF37;letter-spacing:2px;line-height:1.1;margin:0.2rem 0;">{headline}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#A7B0BC;margin-top:0.2rem;">{sub}</div>'
        f'</div>'
    )

rec_cards = []

if best_rec_row is not None:
    br_w, br_l, br_szn = best_rec_row["wins"], best_rec_row["losses"], best_rec_row["season"]
    rec_cards.append(_record_card("📋", "Best Season Record", f"{br_w}-{br_l}", f"{br_szn} Season"))

if most_pf_row is not None:
    pf_val, pf_szn = most_pf_row["points_for"], most_pf_row["season"]
    rec_cards.append(_record_card("🎯", "Most Points in a Season", f"{pf_val:,.1f}", f"{pf_szn} Season"))

if best_week_row is not None:
    bw_score, bw_szn, bw_week = best_week_row["points"], best_week_row["season"], best_week_row["week"]
    bw_team = mgr_by_season.get(bw_szn, "")
    rec_cards.append(_record_card("⚡", "Highest Scoring Week", f"{bw_score:.2f}", f"Week {bw_week}, {bw_szn} · {bw_team}"))

if max_streak > 0:
    rec_cards.append(_record_card("🔥", "Longest Playoff Streak", f"{max_streak} Seasons", "Consecutive postseason appearances"))

if best_steward_name:
    bs = steward_stats_map.get(best_steward_name, {})
    bs_champs = bs.get("champs", 0)
    bs_pl = bs.get("pl_apps", 0)
    bs_w, bs_l = bs.get("w", 0), bs.get("l", 0)
    if bs_champs > 0:
        bs_sub = f"{bs_champs} championship{'s' if bs_champs > 1 else ''} · {bs_w}-{bs_l} record"
    else:
        bs_sub = f"{bs_pl} playoff apps · {bs_w}-{bs_l} record"
    rec_cards.append(_record_card("👑", "Most Successful Steward", best_steward_name, bs_sub))

if fran_champ_seasons:
    champ_yr_str = " · ".join(str(y) for y in fran_champ_seasons)
    rec_cards.append(_record_card("🏆", f"{'Only' if len(fran_champ_seasons) == 1 else ''} Championship{'s' if len(fran_champ_seasons) > 1 else ''}", champ_yr_str, f"{total_champs} title{'s' if total_champs != 1 else ''} in franchise history"))

n_rec = len(rec_cards)
if n_rec > 0:
    ncols = min(n_rec, 3)
    for batch_start in range(0, n_rec, ncols):
        batch = rec_cards[batch_start:batch_start + ncols]
        cols = st.columns(len(batch))
        for col, card_html in zip(cols, batch):
            with col:
                st.markdown(card_html, unsafe_allow_html=True)
        if batch_start + ncols < n_rec:
            st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE MILESTONES ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Museum Exhibit</div>'
    '<div class="tl-section-title">Franchise Milestones</div>',
    unsafe_allow_html=True,
)

milestones: list[tuple] = []
milestones.append((est, "🏛️", "Franchise Founded", f"Established under {first_mgr}"))

if pl_seasons:
    fp = min(pl_seasons)
    fp_mgr = mgr_by_season.get(fp, "")
    milestones.append((fp, "🏈", "First Playoff Appearance", f"{fp_mgr} earns the franchise's first postseason berth"))

if fran_ru_seasons:
    ru0 = fran_ru_seasons[0]
    ru_mgr = mgr_by_season.get(ru0, "")
    milestones.append((ru0, "🥈", "First Finals Appearance", f"{ru_mgr} reaches the championship game"))

for i, (_, p) in enumerate(periods.iterrows()):
    if i == 0:
        continue
    milestones.append((int(p["start_season"]), "🔄", f"{p['manager_name']} Era Begins", "Franchise changes hands"))

if best_rec_row is not None:
    br_szn = best_rec_row["season"]
    br_mgr = mgr_by_season.get(br_szn, "")
    milestones.append((br_szn, "📈", "Best Regular Season", f"{br_mgr} posts the franchise's finest regular-season record"))

if fran_champ_seasons:
    for ci, cs in enumerate(fran_champ_seasons):
        cs_mgr = champ_steward_map.get(cs, "")
        label = "First Championship" if ci == 0 else "Championship"
        milestones.append((cs, "🏆", label, f"{cs_mgr} delivers the title"))

# Sort, deduplicate by year+event
seen_keys: set = set()
unique_milestones = []
for m in sorted(milestones, key=lambda x: (x[0], x[2])):
    key = (m[0], m[2])
    if key not in seen_keys:
        seen_keys.add(key)
        unique_milestones.append(m)

# Render in two columns
n_ms = len(unique_milestones)
mid = (n_ms + 1) // 2
left_ms, right_ms = unique_milestones[:mid], unique_milestones[mid:]

def _milestone_html(items):
    html = '<div style="display:flex;flex-direction:column;gap:0;">'
    for j, (year, icon, event, detail) in enumerate(items):
        is_last = (j == len(items) - 1)
        border_style = "" if is_last else "border-left: 2px solid rgba(184,144,46,0.25);"
        html += (
            f'<div class="tl-milestone-item" style="position:relative;">'
            f'<div class="tl-milestone-year">{year}</div>'
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:0;padding:0 0.4rem;">'
            f'<div class="tl-milestone-dot"></div>'
            f'<div style="width:2px;flex:1;background:rgba(184,144,46,0.22);min-height:20px;" class="{("" if is_last else "")}"></div>'
            f'</div>'
            f'<div class="tl-milestone-event" style="padding-bottom:0.6rem;">'
            f'<div style="font-size:1rem;">{icon} <strong style="color:#F5F5F5;">{event}</strong></div>'
            f'<div class="sub">{detail}</div>'
            f'</div>'
            f'</div>'
        )
    html += '</div>'
    return html

lc, rc = st.columns(2)
with lc:
    st.markdown(_milestone_html(left_ms), unsafe_allow_html=True)
with rc:
    st.markdown(_milestone_html(right_ms), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE ACHIEVEMENTS ───────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">At a Glance</div>'
    '<div class="tl-section-title">Franchise Achievements</div>',
    unsafe_allow_html=True,
)

achievements = [
    ("🏆", total_champs, "Championship Seasons", " · ".join(str(y) for y in fran_champ_seasons) if fran_champ_seasons else "—"),
    ("🥈", len(fran_ru_seasons), "Runner-Up Seasons", " · ".join(str(y) for y in fran_ru_seasons) if fran_ru_seasons else "—"),
    ("🥉", len(fran_3rd_seasons), "Third-Place Finishes", " · ".join(str(y) for y in sorted(fran_3rd_seasons)) if fran_3rd_seasons else "—"),
    ("🔥", max_streak, "Best Playoff Streak", "Consecutive postseason appearances"),
    ("📈", winning_seasons, "Winning Seasons", f"Out of {len(all_fran_seasons)} total seasons"),
    ("🏟️", int(fstat["playoff_apps"]), "Total Playoff Appearances", f"{int(fstat['playoff_apps']) / len(all_fran_seasons):.0%} of all seasons"),
]

ach_cols = st.columns(3)
for i, (icon, val, label, detail) in enumerate(achievements):
    with ach_cols[i % 3]:
        st.markdown(
            f'<div class="tl-achievement-item">'
            f'<div class="tl-achievement-icon">{icon}</div>'
            f'<div>'
            f'<div class="tl-achievement-val">{val}</div>'
            f'<div class="tl-achievement-lbl">{label}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.63rem;color:#A7B0BC;margin-top:0.1rem;">{detail}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    if (i + 1) % 3 == 0 and i < len(achievements) - 1:
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE RIVALRIES ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Head to Head</div>'
    '<div class="tl-section-title">Franchise Rivalries</div>',
    unsafe_allow_html=True,
)

if len(rivalry_combined) > 0:
    _, rival_col, _ = st.columns([1, 4, 1])
    with rival_col:
        rival_html = '<div class="tl-card" style="padding:0;">'
        for rv in rivalry_combined:
            opp = rv["opponent"]
            opp_e = MANAGER_EMOJI.get(opp, "👤")
            rs_w, rs_l = rv["wins"], rv["losses"]
            rs_games = rv["games"]
            pl_g = rv["playoff_games"]
            pl_w = rv["playoff_wins"]
            pl_l = pl_g - pl_w
            pl_str = f"Playoffs: {pl_w}-{pl_l}" if pl_g > 0 else "No playoff meetings"
            wpc = rs_w / rs_games if rs_games > 0 else 0
            rec_color = "#D4AF37" if wpc >= 0.5 else "#A7B0BC"
            rival_html += (
                f'<div class="tl-rival-row">'
                f'<div style="display:flex;align-items:center;gap:0.75rem;min-width:160px;">'
                f'<span style="font-size:1.2rem;">{opp_e}</span>'
                f'<span style="font-family:\'Inter\',sans-serif;font-size:0.85rem;color:#F5F5F5;font-weight:600;">{opp}</span>'
                f'</div>'
                f'<div style="text-align:center;">'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.2rem;color:{rec_color};letter-spacing:1px;">{rs_w}–{rs_l}</div>'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:2px;text-transform:uppercase;">{rs_games} RS Games</div>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.7rem;color:#A7B0BC;">{pl_str}</div>'
                f'</div>'
                f'</div>'
            )
        rival_html += '</div>'
        st.markdown(rival_html, unsafe_allow_html=True)
else:
    st.markdown('<p style="color:#A7B0BC;">No rivalry data available.</p>', unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SEASON-BY-SEASON TABLE (enhanced) ───────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Complete Record</div>'
    '<div class="tl-section-title">Season by Season</div>',
    unsafe_allow_html=True,
)

# Steward era color map
_STEWARD_PALETTE = ["#D4AF37", "#7B9FAB", "#A78BFA", "#34D399", "#F59E0B", "#F87171", "#60A5FA", "#FB923C"]
steward_color_map = {
    mgr: _STEWARD_PALETTE[i % len(_STEWARD_PALETTE)]
    for i, mgr in enumerate(periods["manager_name"].tolist())
}

std_lookup = std.set_index(["season", "team_name"])["rank"].to_dict()

szn_rows = []

# Per-season records come from the extracted profile — the page used to
# recompute the same win/loss/points totals here.
for record in sorted(profile["season_records"], key=lambda r: -r["season"]):
    season = record["season"]
    mgr = record["manager"]
    team = record["team_name"]
    w, l, pf = record["wins"], record["losses"], record["points_for"]

    rs_rank = std_lookup.get((season, team), "—")
    seed_str = f"#{rs_rank}" if rs_rank != "—" else "—"

    result = get_playoff_result_for_team(season, team, pg)
    is_champ = "Champion" in result
    is_ru = "Runner-Up" in result
    result_class = "gold" if is_champ else ("" if is_ru else ("muted" if result == "—" else ""))

    era_color = steward_color_map.get(mgr, "#A7B0BC")
    era_dot = f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{era_color};margin-right:4px;"></span>'
    e = MANAGER_EMOJI.get(mgr, "")

    szn_rows.append([
        (f"{season}", "gold"),
        f"{e} {mgr}",
        f"{era_dot}{team}",
        f"{w}-{l}",
        (f"{pf:.2f}", ""),
        (seed_str, "muted center"),
        (result, result_class),
    ])

st.markdown(
    html_table(
        ["Season", "Steward", "Team Name", "Record", "Points For", "Seed", "Result"],
        szn_rows,
    ),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FRANCHISE LEGENDS ────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">The Cornerstones</div>'
    '<div class="tl-section-title">Franchise Legends</div>',
    unsafe_allow_html=True,
)

_fl_legends = get_franchise_legends(franchise_id)
_dpw_fr = get_draft_picks_with_pos()
_POS_C_FR = {"RB":"#22C55E","WR":"#3B82F6","QB":"#EF4444","TE":"#F59E0B","DEF":"#8B5CF6","K":"#6B7280"}

if _fl_legends:
    st.markdown(
        '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.73rem;margin:-0.25rem 0 1.25rem;">'
        'Ranked by franchise investment: draft frequency + keeper frequency (keepers weighted 3×).</p>',
        unsafe_allow_html=True,
    )
    _leg_cols = st.columns(min(4, len(_fl_legends)))
    for _ci, (_leg, _col) in enumerate(zip(_fl_legends, _leg_cols)):
        _pname = _leg["player_name"]
        _pos   = _leg.get("position", "?") or "?"
        _pos_c = _POS_C_FR.get(_pos, "#6B7280")
        _d_cnt = int(_leg["draft_count"])
        _k_cnt = int(_leg["keeper_count"])
        _score = int(_leg["legend_score"])
        _szns  = _leg["seasons"]
        _szn_str = f"{min(_szns)}–{max(_szns)}" if _szns else "—"
        medal = ["🥇","🥈","🥉","🏅","🏅","🏅","🏅","🏅"][_ci]

        # Who from this franchise drafted them (get unique managers)
        _fr_picks = _dpw_fr[
            (_dpw_fr["franchise_id"] == franchise_id) &
            (_dpw_fr["player_name"] == _pname)
        ]
        _fr_mgrs  = _fr_picks["manager"].dropna().unique().tolist()
        _mgr_str  = " → ".join(MANAGER_EMOJI.get(m,"") + " " + m for m in _fr_mgrs)

        _kept_str = "" if _k_cnt == 0 else f" · Kept {_k_cnt}×"
        _mgr_line = (
            f'<div style="font-size:0.58rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;margin-top:4px;">'
            f'{_mgr_str}</div>'
        ) if _mgr_str else ""
        _col.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-top:3px solid {_pos_c};'
            f'border-radius:6px;padding:12px;text-align:center;height:100%;">'
            f'<div style="font-size:1.4rem;margin-bottom:4px;">{medal}</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;color:#F5F5F5;'
            f'letter-spacing:2px;line-height:1.2;margin-bottom:4px;">{_pname}</div>'
            f'<div style="background:{_pos_c};color:#000;font-weight:700;font-size:0.55rem;'
            f'padding:1px 5px;border-radius:3px;display:inline-block;letter-spacing:1px;'
            f'margin-bottom:6px;">{_pos}</div>'
            f'<div style="font-size:0.6rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;">'
            f'Drafted {_d_cnt}×{_kept_str}</div>'
            f'<div style="font-size:0.58rem;color:#6B7280;font-family:\'Inter\',sans-serif;'
            f'margin-top:3px;">{_szn_str}</div>'
            f'{_mgr_line}'
            f'</div>',
            unsafe_allow_html=True,
        )
    # Second row if more than 4
    if len(_fl_legends) > 4:
        _leg_cols2 = st.columns(len(_fl_legends) - 4)
        for _ci2, (_leg, _col) in enumerate(zip(_fl_legends[4:], _leg_cols2)):
            _pname = _leg["player_name"]
            _pos   = _leg.get("position", "?") or "?"
            _pos_c = _POS_C_FR.get(_pos, "#6B7280")
            _d_cnt = int(_leg["draft_count"])
            _k_cnt = int(_leg["keeper_count"])
            _szns  = _leg["seasons"]
            _szn_str = f"{min(_szns)}–{max(_szns)}" if _szns else "—"
            medal = ["🏅","🏅","🏅","🏅"][_ci2]
            _col.markdown(
                f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-top:3px solid {_pos_c};'
                f'border-radius:6px;padding:12px;text-align:center;margin-top:10px;">'
                f'<div style="font-size:1.1rem;margin-bottom:3px;">{medal}</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.88rem;color:#F5F5F5;'
                f'letter-spacing:2px;line-height:1.2;">{_pname}</div>'
                f'<div style="font-size:0.58rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;margin-top:3px;">'
                f'Drafted {_d_cnt}× · Kept {_k_cnt}× · {_szn_str}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
else:
    st.markdown(
        '<p style="color:#A7B0BC;font-size:0.75rem;font-family:\'Inter\',sans-serif;">'
        'No draft history available for this franchise.</p>',
        unsafe_allow_html=True,
    )

render_page_footer(
    href="/champions",
    cta="BACK TO THE TROPHY ROOM",
    tagline="EVERY FRANCHISE.<br>ONE DESTINATION.",
)
