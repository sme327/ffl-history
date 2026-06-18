"""Franchise Profiles page — 25-year franchise lineages."""
import streamlit as st
import pandas as pd
from utils.data import (
    load_all, get_franchise_stats, get_franchise_steward_periods,
    get_champions, get_playoff_result_for_team,
    MANAGER_EMOJI, CURRENT_SEASON,
)
from utils.styles import inject_css, render_nav, metric_card, html_table

st.set_page_config(
    page_title="Franchises · The Long Game",
    page_icon="🏟️",
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
    summary_rows.append([
        (champ_str, "gold"),
        f"{emoji} {mgr}",
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

selected_mgr = st.selectbox(
    "SELECT FRANCHISE",
    options=sorted(option_map.keys()),
    format_func=lambda n: f"{MANAGER_EMOJI.get(n, '')}  {n}  ·  {option_map[n]}",
    label_visibility="collapsed",
)

franchise_id = option_map[selected_mgr]
fstat = franchise_stats[franchise_stats["franchise_id"] == franchise_id].iloc[0]
periods = steward_periods[steward_periods["franchise_id"] == franchise_id].reset_index(drop=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FRANCHISE DATA COMPUTATION
# ══════════════════════════════════════════════════════════════════════════════

fh_this = fh[fh["franchise_id"] == franchise_id].sort_values("season")
all_fran_seasons = sorted(fh_this["season"].unique().tolist())
est = int(fstat["established"])
curr_mgr = str(fstat["current_manager"]) if pd.notna(fstat.get("current_manager")) else periods.iloc[-1]["manager_name"]
first_mgr = periods.iloc[0]["manager_name"]

# Build franchise team-season mapping
fms_rows = []
for _, frow in fh_this.iterrows():
    s = int(frow["season"])
    mgr = frow["manager_name"]
    tn = tnh[(tnh["canonical_name"] == mgr) & (tnh["season"] == s)]
    if len(tn) == 0:
        continue
    fms_rows.append({"season": s, "mgr": mgr, "team_name": tn.iloc[0]["team_name"]})
fms_df = pd.DataFrame(fms_rows) if fms_rows else pd.DataFrame(columns=["season", "mgr", "team_name"])

# Regular season matchups for this franchise
fran_rs = (
    wm[~wm["is_bye"] & ~wm["is_playoff"]].merge(
        fms_df[["season", "team_name"]], on=["season", "team_name"], how="inner"
    )
    if len(fms_df) > 0 else pd.DataFrame(columns=wm.columns)
)

# Playoff bracket appearances
pg_champ = pg[pg["bracket"] == "championship"].copy()
pl_t1 = (
    pg_champ.merge(fms_df[["season", "team_name"]].rename(columns={"team_name": "team_1"}),
                   on=["season", "team_1"], how="inner")
    if len(fms_df) > 0 else pg_champ.iloc[0:0]
)
pl_t2 = (
    pg_champ.merge(fms_df[["season", "team_name"]].rename(columns={"team_name": "team_2"}),
                   on=["season", "team_2"], how="inner")
    if len(fms_df) > 0 else pg_champ.iloc[0:0]
)
pl_seasons = set(pl_t1["season"].tolist() + pl_t2["season"].tolist())

# Finals appearances (championship game only)
fin_t1 = pl_t1[pl_t1["game_type"] == "final"]
fin_t2 = pl_t2[pl_t2["game_type"] == "final"]
n_finals_apps = len(set(fin_t1["season"].tolist() + fin_t2["season"].tolist()))

# 3rd place finishes
trd_t1 = pl_t1[(pl_t1["game_type"] == "3rd_place") & (pl_t1["winner"] == pl_t1["team_1"])]
trd_t2 = pl_t2[(pl_t2["game_type"] == "3rd_place") & (pl_t2["winner"] == pl_t2["team_2"])]
fran_3rd_seasons = set(trd_t1["season"].tolist() + trd_t2["season"].tolist())

# Championship and runner-up seasons for this franchise
fran_champ_seasons = sorted(
    fms_df.merge(
        champions[["season", "champion_team"]].rename(columns={"champion_team": "team_name"}),
        on=["season", "team_name"], how="inner",
    )["season"].tolist()
) if len(fms_df) > 0 else []

fran_ru_seasons = sorted(
    fms_df.merge(
        champions[["season", "runner_up_team"]].rename(columns={"runner_up_team": "team_name"}),
        on=["season", "team_name"], how="inner",
    )["season"].tolist()
) if len(fms_df) > 0 else []

# Longest playoff streak
max_streak = 0
cur_streak = 0
for s in all_fran_seasons:
    if s in pl_seasons:
        cur_streak += 1
        max_streak = max(max_streak, cur_streak)
    else:
        cur_streak = 0

# Per-season RS records
szn_records = (
    fran_rs.groupby("season").agg(
        w=("result", lambda x: (x == "Win").sum()),
        l=("result", lambda x: (x == "Loss").sum()),
        pf=("team_score", "sum"),
    ).reset_index()
    if len(fran_rs) > 0 else pd.DataFrame(columns=["season", "w", "l", "pf"])
)
winning_seasons = int((szn_records["w"] > szn_records["l"]).sum()) if len(szn_records) > 0 else 0
best_rec_row = szn_records.loc[szn_records["w"].idxmax()] if len(szn_records) > 0 else None
most_pf_row = szn_records.loc[szn_records["pf"].idxmax()] if len(szn_records) > 0 else None
best_week_row = fran_rs.loc[fran_rs["team_score"].idxmax()] if len(fran_rs) > 0 else None

# Steward championships (inherited from franchise)
champ_by_mgr: dict[str, int] = {}
for _, row in champions.iterrows():
    fh_szn = fh[(fh["franchise_id"] == franchise_id) & (fh["season"] == row["season"])]
    if len(fh_szn) == 0:
        continue
    mgr = fh_szn.iloc[0]["manager_name"]
    tn_row = tnh[(tnh["canonical_name"] == mgr) & (tnh["season"] == row["season"])]
    if len(tn_row) == 0:
        continue
    if tn_row.iloc[0]["team_name"] == row["champion_team"]:
        champ_by_mgr[mgr] = champ_by_mgr.get(mgr, 0) + 1

# Per-steward stats
steward_stats_map: dict[str, dict] = {}
for _, p in periods.iterrows():
    mgr = p["manager_name"]
    mgr_szns = set(fh_this[fh_this["manager_name"] == mgr]["season"].tolist())
    mgr_rs = fran_rs[fran_rs["season"].isin(mgr_szns)]
    w = int((mgr_rs["result"] == "Win").sum())
    l = int((mgr_rs["result"] == "Loss").sum())
    steward_stats_map[mgr] = {
        "w": w, "l": l,
        "pl_apps": len(pl_seasons & mgr_szns),
        "champs": champ_by_mgr.get(mgr, 0),
        "seasons": int(p["years"]),
    }

# Map championship seasons to the steward who earned them
champ_steward_map: dict[int, str] = {}
for s in fran_champ_seasons:
    row_df = fms_df[fms_df["season"] == s]
    if len(row_df) > 0:
        champ_steward_map[s] = row_df.iloc[0]["mgr"]

# Most successful steward
best_steward_name = (
    max(steward_stats_map.items(), key=lambda x: (x[1]["champs"], x[1]["pl_apps"], x[1]["w"]))[0]
    if steward_stats_map else None
)

# Rivalries (RS head-to-head)
if len(fran_rs) > 0:
    fran_rs_r = fran_rs.copy()
    fran_rs_r["opp_mgr"] = fran_rs_r.apply(
        lambda r: opp_lookup.get((int(r["season"]), r["opponent"]), r["opponent"]), axis=1
    )
    rs_rivalry = (
        fran_rs_r.groupby("opp_mgr")
        .agg(games=("result", "count"), wins=("result", lambda x: (x == "Win").sum()))
        .reset_index()
    )
    rs_rivalry["losses"] = rs_rivalry["games"] - rs_rivalry["wins"]
else:
    rs_rivalry = pd.DataFrame(columns=["opp_mgr", "games", "wins", "losses"])

# Playoff head-to-head
pl_game_rows = []
for _, g in pl_t1.iterrows():
    opp = opp_lookup.get((int(g["season"]), g["team_2"]), g["team_2"])
    pl_game_rows.append({"opp_mgr": opp, "won": g["winner"] == g["team_1"]})
for _, g in pl_t2.iterrows():
    opp = opp_lookup.get((int(g["season"]), g["team_1"]), g["team_1"])
    pl_game_rows.append({"opp_mgr": opp, "won": g["winner"] == g["team_2"]})
pl_rivalry_df = pd.DataFrame(pl_game_rows) if pl_game_rows else pd.DataFrame(columns=["opp_mgr", "won"])
pl_rivalry = (
    pl_rivalry_df.groupby("opp_mgr")
    .agg(pl_games=("won", "count"), pl_wins=("won", "sum"))
    .reset_index()
    if len(pl_rivalry_df) > 0 else pd.DataFrame(columns=["opp_mgr", "pl_games", "pl_wins"])
)

# Combined rivalry table (top rivals by games played)
rivalry_combined = (
    rs_rivalry.merge(pl_rivalry, on="opp_mgr", how="left")
    .fillna(0)
    .sort_values("games", ascending=False)
    .head(6)
    .reset_index(drop=True)
)

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
        <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:5px;text-transform:uppercase;">{franchise_id} &nbsp;·&nbsp; Established {est}</div>
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

# Algorithmic story generation
_story_parts: list[str] = []
_n_stewards = len(periods)

def _join_years(yrs):
    strs = [str(y) for y in yrs]
    if len(strs) <= 2:
        return " and ".join(strs)
    return ", ".join(strs[:-1]) + ", and " + strs[-1]

if _n_stewards == 1:
    ss = steward_stats_map.get(first_mgr, {})
    pl, w, l = ss.get("pl_apps", 0), ss.get("w", 0), ss.get("l", 0)
    champs = ss.get("champs", 0)
    _szns_total = len(all_fran_seasons)
    if champs > 0:
        yr_str = _join_years(fran_champ_seasons)
        _story_parts.append(
            f"Founded in {est}, this franchise has been steered by {first_mgr} from its very first season."
        )
        _story_parts.append(
            f"In {_szns_total} seasons, {first_mgr} has built an enduring legacy: "
            f"{champs} championship{'s' if champs > 1 else ''} ({yr_str}), "
            f"{pl} playoff appearances, and a presence that defines the standard in this league."
        )
    else:
        _story_parts.append(
            f"Founded in {est}, this franchise has been managed by {first_mgr} throughout its entire existence."
        )
        if pl >= 4:
            _story_parts.append(
                f"{first_mgr} has kept the franchise in playoff contention with {pl} postseason appearances "
                f"across {_szns_total} seasons, compiling a {w}-{l} regular season record."
            )
        elif pl > 0:
            _story_parts.append(
                f"{first_mgr} has compiled a {w}-{l} regular season record with {pl} playoff appearance{'s' if pl != 1 else ''}."
            )
        else:
            _story_parts.append(
                f"{first_mgr} has compiled a {w}-{l} regular season record across {_szns_total} seasons."
            )
        _story_parts.append("The franchise's first title remains the next chapter yet to be written.")
else:
    _story_parts.append(f"Founded in {est} under {first_mgr}.")
    _had_pl_narrative = False
    _total_champs_so_far = 0

    for idx, (_, _p) in enumerate(periods.iterrows()):
        _mgr = _p["manager_name"]
        _ss = steward_stats_map.get(_mgr, {})
        _szns = _ss.get("seasons", 1)
        _pl = _ss.get("pl_apps", 0)
        _champs = _ss.get("champs", 0)
        _w, _l = _ss.get("w", 0), _ss.get("l", 0)
        _champ_yrs = [s for s in fran_champ_seasons if champ_steward_map.get(s) == _mgr]
        _is_current = (_mgr == curr_mgr)

        if _is_current:
            if _champs > 0:
                _yr_str = _join_years(_champ_yrs)
                if _total_champs_so_far == 0:
                    _story_parts.append(
                        f"{_mgr} delivered the franchise's first championship{'s' if _champs > 1 else ''} ({_yr_str}) and continues to lead today."
                    )
                else:
                    _story_parts.append(
                        f"{_mgr} has added {'another' if _champs == 1 else str(_champs) + ' more'} title{'s' if _champs > 1 else ''} ({_yr_str}), continuing the tradition."
                    )
            elif total_champs == 0:
                _story_parts.append(f"Today the franchise continues under {_mgr}, still searching for its first title.")
            else:
                _story_parts.append(f"Today the franchise continues under {_mgr}.")
            _total_champs_so_far += _champs
            continue

        if idx == 0:
            # First steward — add sentence only for notably strong tenures
            if _champs > 0:
                _yr_str = _join_years(_champ_yrs)
                _story_parts.append(f"{_mgr} launched the franchise with immediate success, winning in {_yr_str}.")
                _total_champs_so_far += _champs
            elif _pl >= 4 and _szns >= 5:
                _story_parts.append(
                    f"The early years under {_mgr} built a competitive foundation with {_pl} playoff appearances across {_szns} seasons."
                )
        else:
            # Middle steward
            if _champs > 0:
                _yr_str = _join_years(_champ_yrs)
                _years_waiting = min(_champ_yrs) - est
                _finally = "finally " if _years_waiting >= 15 and _total_champs_so_far == 0 else ""
                _story_parts.append(
                    f"{_mgr} {_finally}delivered the championship{'s' if _champs > 1 else ''} this franchise had been building toward, winning in {_yr_str}."
                )
                _total_champs_so_far += _champs
            elif _pl >= 6 and not _had_pl_narrative:
                _story_parts.append(
                    f"{_mgr} transformed the franchise into a perennial playoff contender, qualifying {_pl} times across {_szns} seasons."
                )
                _had_pl_narrative = True
            elif _pl >= 6 and _had_pl_narrative:
                _story_parts.append(
                    f"{_mgr} extended that run even further, reaching the postseason {_pl} times in {_szns} seasons — yet the title remained out of reach."
                )
            elif _pl >= 4 and not _had_pl_narrative:
                _story_parts.append(
                    f"Under {_mgr}, the franchise reached the postseason {_pl} times in {_szns} seasons, though a title remained elusive."
                )
                _had_pl_narrative = True
            elif _pl >= 4 and _had_pl_narrative:
                _story_parts.append(
                    f"{_mgr} kept the franchise in contention with {_pl} more playoff appearances across {_szns} seasons."
                )
            elif _pl >= 2 and _szns >= 4:
                _story_parts.append(
                    f"{_mgr} contributed {_szns} seasons and a {_w}-{_l} regular season record to the franchise's history."
                )
            elif _szns >= 5:
                _story_parts.append(f"The {_mgr} era spanned {_szns} seasons of the franchise's evolution.")

_story_parts = _story_parts[:6]

st.markdown(
    f'<div class="tl-franchise-story">{" ".join(_story_parts)}</div>',
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
    champs = champ_by_mgr.get(mgr, 0)
    szns = ss.get("seasons", 0)
    trophy_html = f'<div style="font-size:1rem;margin-top:0.3rem;">{"🏆" * champs}</div>' if champs else ""
    tl_items_html.append(
        f'<div class="tl-steward-rich {curr_cls}">'
        f'<div class="tl-steward-rich-avatar">{e}</div>'
        f'<div class="tl-steward-rich-name">{mgr}</div>'
        f'<div class="tl-steward-rich-years">{yr_range}</div>'
        f'{trophy_html}'
        f'<div class="tl-steward-rich-divider"></div>'
        f'<div style="display:flex;justify-content:space-around;gap:0.3rem;">'
        f'<div><div class="tl-steward-rich-stat-val">{w}-{l}</div><div class="tl-steward-rich-stat-lbl">Record</div></div>'
        f'<div><div class="tl-steward-rich-stat-val">{pl}</div><div class="tl-steward-rich-stat-lbl">Playoffs</div></div>'
        f'<div><div class="tl-steward-rich-stat-val">{szns}</div><div class="tl-steward-rich-stat-lbl">Seasons</div></div>'
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
    champs = champ_by_mgr.get(mgr, 0)
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
    br_w, br_l, br_szn = int(best_rec_row["w"]), int(best_rec_row["l"]), int(best_rec_row["season"])
    rec_cards.append(_record_card("📋", "Best Season Record", f"{br_w}-{br_l}", f"{br_szn} Season"))

if most_pf_row is not None:
    pf_val, pf_szn = float(most_pf_row["pf"]), int(most_pf_row["season"])
    rec_cards.append(_record_card("🎯", "Most Points in a Season", f"{pf_val:,.1f}", f"{pf_szn} Season"))

if best_week_row is not None:
    bw_score, bw_szn, bw_week = float(best_week_row["team_score"]), int(best_week_row["season"]), int(best_week_row["week"])
    bw_team = best_week_row["team_name"]
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
    fp_mgr = fms_df[fms_df["season"] == fp]["mgr"].values[0] if len(fms_df[fms_df["season"] == fp]) > 0 else ""
    milestones.append((fp, "🏈", "First Playoff Appearance", f"{fp_mgr} earns the franchise's first postseason berth"))

if fran_ru_seasons:
    ru0 = fran_ru_seasons[0]
    ru_mgr = fms_df[fms_df["season"] == ru0]["mgr"].values[0] if len(fms_df[fms_df["season"] == ru0]) > 0 else ""
    milestones.append((ru0, "🥈", "First Finals Appearance", f"{ru_mgr} reaches the championship game"))

for i, (_, p) in enumerate(periods.iterrows()):
    if i == 0:
        continue
    milestones.append((int(p["start_season"]), "🔄", f"{p['manager_name']} Era Begins", "Franchise changes hands"))

if best_rec_row is not None:
    br_szn = int(best_rec_row["season"])
    br_mgr = fms_df[fms_df["season"] == br_szn]["mgr"].values[0] if len(fms_df[fms_df["season"] == br_szn]) > 0 else ""
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
        for _, rv in rivalry_combined.iterrows():
            opp = str(rv["opp_mgr"])
            opp_e = MANAGER_EMOJI.get(opp, "👤")
            rs_w, rs_l = int(rv["wins"]), int(rv["losses"])
            rs_games = int(rv["games"])
            pl_g = int(rv.get("pl_games", 0))
            pl_w = int(rv.get("pl_wins", 0))
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
fh_szn_sorted = fh_this.sort_values("season", ascending=False)

for _, frow in fh_szn_sorted.iterrows():
    season = int(frow["season"])
    mgr = frow["manager_name"]
    team_row = tnh[(tnh["canonical_name"] == mgr) & (tnh["season"] == season)]
    if len(team_row) == 0:
        continue
    team = team_row.iloc[0]["team_name"]

    rs = wm[(wm["season"] == season) & (wm["team_name"] == team) & (~wm["is_bye"]) & (~wm["is_playoff"])]
    w = int((rs["result"] == "Win").sum())
    l = int((rs["result"] == "Loss").sum())
    pf = round(float(rs["team_score"].dropna().sum()), 2)

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

# ── FRANCHISE LEGENDS (FUTURE) ───────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Coming Soon</div>'
    '<div class="tl-section-title">Franchise Legends</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="tl-card" style="text-align:center;padding:2rem 1.5rem;border-style:dashed;opacity:0.65;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🏅</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:#A7B0BC;letter-spacing:3px;">Reserved for Player Data</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#A7B0BC;margin-top:0.4rem;line-height:1.6;">
            When roster data is available, this section will surface the players who defined each franchise era —
            the studs drafted, the waiver wire pickups that won titles, the names that made this franchise what it is.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
