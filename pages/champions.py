"""Champions page — all-time title holders."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from utils.data import (
    load_all, get_champions, get_manager_stats,
    MANAGER_EMOJI, CURRENT_SEASON, FOUNDED,
)
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="Champions · The Long Game",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("champions")

data = load_all()
champions = get_champions()
manager_stats = get_manager_stats()
fh = data["franchise_history"]
tnh = data["team_name_history"]
pg = data["playoff_games"]
std = data["standings"]

# ── DERIVED DATA ──────────────────────────────────────────────────────────────
champ_counts = (
    champions.groupby("champion_manager")
    .agg(
        championships=("season", "count"),
        years=("season", lambda x: ", ".join(str(y) for y in sorted(x))),
        last=("season", "max"),
        first=("season", "min"),
    )
    .sort_values(["championships", "last"], ascending=[False, False])
    .reset_index()
)

# Finals records per manager (champion + runner-up appearances)
_as_champ = (
    champions.groupby("champion_manager").size().rename("champs").reset_index()
    .rename(columns={"champion_manager": "mgr"})
)
_as_ru = (
    champions.groupby("runner_up_manager").size().rename("runner_ups").reset_index()
    .rename(columns={"runner_up_manager": "mgr"})
)
_finals = _as_champ.merge(_as_ru, on="mgr", how="outer").fillna(0)
_finals["titles"] = _finals["champs"].astype(int)
_finals["finals_apps"] = (_finals["champs"] + _finals["runner_ups"]).astype(int)
_finals["win_pct"] = (_finals["titles"] / _finals["finals_apps"]).round(2)
finals_rec = _finals.set_index("mgr")

# Franchise-level championship data
_fh_tnh = fh.merge(
    tnh.rename(columns={"canonical_name": "manager_name"}),
    on=["season", "manager_name"],
    how="left",
)
_champ_teams = champions[["season", "champion_team"]].rename(columns={"champion_team": "team_name"})
_fran_wins = _fh_tnh.merge(_champ_teams, on=["season", "team_name"], how="inner")
_curr_mgrs = (
    fh[fh["season"] == CURRENT_SEASON][["franchise_id", "manager_name"]]
    .rename(columns={"manager_name": "current_manager"})
)
franchise_champ_summary = (
    _fran_wins.groupby("franchise_id")
    .agg(
        championships=("season", "count"),
        years=("season", lambda x: ", ".join(str(y) for y in sorted(x))),
        last=("season", "max"),
    )
    .reset_index()
    .merge(_curr_mgrs, on="franchise_id", how="left")
    .sort_values(["championships", "last"], ascending=[False, False])
    .reset_index(drop=True)
)

total_seasons = CURRENT_SEASON - FOUNDED + 1
unique_mgrs = int(champions["champion_manager"].nunique())
top_champ = champ_counts.iloc[0]
current_champ = champions[champions["season"] == CURRENT_SEASON].iloc[0]

# ── PAGE TITLE ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-page-title">Champions</div>
    <div class="tl-page-subtitle">Every title. Every dynasty. The immortal record.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── HERO STORY ────────────────────────────────────────────────────────────────
top_emoji = MANAGER_EMOJI.get(top_champ["champion_manager"], "")
curr_emoji = MANAGER_EMOJI.get(current_champ["champion_manager"], "")
st.markdown(
    f"""
    <div style="text-align:center;padding:0.75rem 0 1.25rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:#A7B0BC;letter-spacing:4px;line-height:2.2;">
            {total_seasons} SEASONS &nbsp;·&nbsp; {len(champions)} CHAMPIONS CROWNED &nbsp;·&nbsp; ONLY {unique_mgrs} MANAGERS HAVE EVER LIFTED THE TROPHY
        </div>
        <div style="display:flex;justify-content:center;gap:5rem;margin-top:1rem;flex-wrap:wrap;">
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:4px;text-transform:uppercase;margin-bottom:0.2rem;">Most Championships</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#D4AF37;letter-spacing:3px;">{top_emoji}&nbsp;{top_champ['champion_manager']} &nbsp;—&nbsp; {top_champ['championships']}</div>
            </div>
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:4px;text-transform:uppercase;margin-bottom:0.2rem;">Reigning Champion</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#D4AF37;letter-spacing:3px;">{curr_emoji}&nbsp;{current_champ['champion_manager']} &nbsp;—&nbsp; {CURRENT_SEASON}</div>
            </div>
        </div>
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── ALL-TIME LEADERS + TOGGLE ──────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">All-Time</div>'
    '<div class="tl-section-title">Championship Leaders</div>',
    unsafe_allow_html=True,
)

_, t_col, _ = st.columns([3, 1, 3])
with t_col:
    view_mode = st.radio(
        "leaders_view", ["Managers", "Franchises"], horizontal=True,
        label_visibility="collapsed",
    )

st.markdown("<br>", unsafe_allow_html=True)

if view_mode == "Managers":
    cards_data = champ_counts.copy()
    card_cols = st.columns(min(3, len(cards_data)))
    for i, (col, (_, row)) in enumerate(zip(card_cols, cards_data.iterrows())):
        mgr = row["champion_manager"]
        emoji = MANAGER_EMOJI.get(mgr, "👤")
        border = "gold-border" if i == 0 else ""
        fr = finals_rec.loc[mgr] if mgr in finals_rec.index else None
        fin_html = (
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.64rem;color:#A7B0BC;margin-top:0.3rem;">'
            f'{int(fr["finals_apps"])} Finals &nbsp;·&nbsp; {fr["win_pct"]:.0%} Win Rate</div>'
        ) if fr is not None else ""
        with col:
            st.markdown(
                f"""<div class="tl-trophy-card {border}">
                    <div style="font-size:2.5rem;">{emoji}</div>
                    <div>
                        <div class="tl-trophy-count">{row['championships']}</div>
                        <div class="tl-trophy-name">{mgr}</div>
                        <div class="tl-trophy-years">{row['years']}</div>
                        {fin_html}
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    if len(cards_data) > 3:
        st.markdown("<br>", unsafe_allow_html=True)
        tbl_rows = []
        for _, row in cards_data.iloc[3:].iterrows():
            mgr = row["champion_manager"]
            fr = finals_rec.loc[mgr] if mgr in finals_rec.index else None
            fin_str = f"{int(fr['finals_apps'])} ({fr['win_pct']:.0%})" if fr is not None else "—"
            tbl_rows.append([
                mgr,
                (str(row["championships"]), "gold"),
                (row["years"], "muted"),
                (fin_str, "muted"),
            ])
        st.markdown(
            html_table(["Manager", "Championships", "Years", "Finals (Win%)"], tbl_rows),
            unsafe_allow_html=True,
        )

else:  # Franchises
    f_cols = st.columns(min(3, len(franchise_champ_summary)))
    for i, (col, (_, row)) in enumerate(zip(f_cols, franchise_champ_summary.iterrows())):
        mgr = str(row["current_manager"]) if row.get("current_manager") and str(row["current_manager"]) != "nan" else "—"
        emoji = MANAGER_EMOJI.get(mgr, "🏟️")
        border = "gold-border" if i == 0 else ""
        with col:
            st.markdown(
                f"""<div class="tl-trophy-card {border}">
                    <div style="font-size:2.5rem;">{emoji}</div>
                    <div>
                        <div class="tl-trophy-count">{row['championships']}</div>
                        <div class="tl-trophy-name">{row['franchise_id']}</div>
                        <div class="tl-trophy-years">Current: {mgr}</div>
                        <div class="tl-trophy-years">{row['years']}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    if len(franchise_champ_summary) > 3:
        st.markdown("<br>", unsafe_allow_html=True)
        fran_rows = [
            [
                (str(row["franchise_id"]), "gold"),
                str(row.get("current_manager", "—")),
                (str(row["championships"]), "gold"),
                (row["years"], "muted"),
            ]
            for _, row in franchise_champ_summary.iloc[3:].iterrows()
        ]
        st.markdown(
            html_table(["Franchise", "Current Manager", "Championships", "Years"], fran_rows),
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── CHAMPIONSHIP TIMELINE ──────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Chronological View</div>'
    '<div class="tl-section-title">Championship Timeline</div>',
    unsafe_allow_html=True,
)

timeline_data = (
    champ_counts[["champion_manager", "years", "championships", "first"]]
    .sort_values("first")
    .to_dict("records")
)
tl_html = '<div style="padding:0.25rem 0;">'
for entry in timeline_data:
    mgr = entry["champion_manager"]
    n = int(entry["championships"])
    years_list = [y.strip() for y in entry["years"].split(",")]
    emoji = MANAGER_EMOJI.get(mgr, "👤")
    pill_cls = "tl-year-dot-gold" if n > 1 else "tl-year-dot-solo"
    pills = "".join(f'<span class="{pill_cls}">{yr}</span>' for yr in years_list)
    tl_html += (
        f'<div class="tl-chron-entry">'
        f'<div class="tl-chron-mgr-col">'
        f'<span style="font-size:1rem;">{emoji}</span><span>{mgr}</span>'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#A7B0BC;font-weight:400;">({n})</span>'
        f'</div>'
        f'<div class="tl-chron-pills-col">{pills}</div>'
        f'</div>'
    )
tl_html += "</div>"
st.markdown(tl_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── DYNASTIES ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Hall of Fame</div>'
    '<div class="tl-section-title">Dynasties</div>',
    unsafe_allow_html=True,
)

dynasties = champ_counts[champ_counts["championships"] >= 2].to_dict("records")
if dynasties:
    n_per_row = min(4, len(dynasties))
    for batch_start in range(0, len(dynasties), n_per_row):
        batch = dynasties[batch_start : batch_start + n_per_row]
        if batch_start > 0:
            st.markdown("<br>", unsafe_allow_html=True)
        dyn_cols = st.columns(len(batch))
        for col, d in zip(dyn_cols, batch):
            mgr = d["champion_manager"]
            emoji = MANAGER_EMOJI.get(mgr, "👤")
            n = int(d["championships"])
            yrs = d["years"]
            first_yr = int(d["first"])
            last_yr = int(d["last"])
            span = last_yr - first_yr + 1
            years_ints = sorted(int(y.strip()) for y in yrs.split(","))
            is_consec = all(years_ints[j+1] == years_ints[j]+1 for j in range(len(years_ints)-1))
            if is_consec and n > 1:
                era_desc = f"{n} consecutive championships"
            else:
                era_desc = f"{n} titles across {span} seasons ({first_yr}–{last_yr})"
            fr = finals_rec.loc[mgr] if mgr in finals_rec.index else None
            fin_line = (
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#A7B0BC;margin-top:0.15rem;">'
                f'{int(fr["titles"])} titles in {int(fr["finals_apps"])} finals appearances</div>'
            ) if fr is not None else ""
            plural = "s" if n != 1 else ""
            with col:
                st.markdown(
                    f"""<div class="tl-dynasty-card">
                        <div style="font-size:2.8rem;margin-bottom:0.6rem;">{emoji}</div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#D4AF37;letter-spacing:3px;line-height:1;">{mgr}</div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:3.5rem;color:#F5F5F5;line-height:1;margin:0.35rem 0 0.1rem;">{n}</div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin-bottom:0.75rem;">Championship{plural}</div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#A7B0BC;line-height:1.5;">{era_desc}</div>
                        {fin_line}
                        <div style="font-family:'Inter',sans-serif;font-size:0.7rem;color:#D4AF37;margin-top:0.6rem;letter-spacing:1px;">{yrs}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── CHAMPIONSHIP TRIVIA ────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Notes from the Record Book</div>'
    '<div class="tl-section-title">Championship Trivia</div>',
    unsafe_allow_html=True,
)

champions["margin"] = champions["champion_score"] - champions["runner_up_score"]
champions["combined"] = champions["champion_score"] + champions["runner_up_score"]

def trivia_card(label, headline, sub):
    return f"""
    <div class="tl-card">
        <div class="tl-section-label">{label}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{headline}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">{sub}</div>
    </div>"""

# Row 1
biggest = champions.loc[champions["margin"].idxmax()]
closest = champions.loc[champions["margin"].idxmin()]
ru_counts = champions.groupby("runner_up_manager").size().sort_values(ascending=False).reset_index(name="count")
heartbreak = ru_counts.iloc[0]

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(trivia_card("Biggest Blowout", str(biggest["season"]),
        f"{biggest['champion_team']} won by {biggest['margin']:.2f} pts"), unsafe_allow_html=True)
with c2:
    st.markdown(trivia_card("Closest Title Game", str(closest["season"]),
        f"{closest['champion_team']} survived by {closest['margin']:.2f} pts"), unsafe_allow_html=True)
with c3:
    st.markdown(trivia_card("Most Runner-Up Finishes", heartbreak["runner_up_manager"],
        f"{heartbreak['count']}× runner-up — still waiting"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row 2
high_game = champions.loc[champions["combined"].idxmax()]
low_game = champions.loc[champions["combined"].idxmin()]
most_finals_row = finals_rec.sort_values("finals_apps", ascending=False).iloc[0]

c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(trivia_card("Highest-Scoring Final", str(high_game["season"]),
        f"{high_game['champion_score']:.2f} + {high_game['runner_up_score']:.2f} = {high_game['combined']:.2f} combined"), unsafe_allow_html=True)
with c5:
    st.markdown(trivia_card("Defensive Masterclass", str(low_game["season"]),
        f"Only {low_game['combined']:.2f} pts combined — {low_game['champion_team']} edged it"), unsafe_allow_html=True)
with c6:
    st.markdown(trivia_card("Most Finals Appearances", most_finals_row.name,
        f"{int(most_finals_row['finals_apps'])} trips to the title game ({int(most_finals_row['titles'])}W–{int(most_finals_row['runner_ups'])}L)"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Row 3
sorted_champs = champions.sort_values("season").reset_index(drop=True)
back_to_back = None
b2b_streak = 1
for i in range(1, len(sorted_champs)):
    if (sorted_champs.iloc[i]["champion_manager"] == sorted_champs.iloc[i-1]["champion_manager"] and
            sorted_champs.iloc[i]["season"] == sorted_champs.iloc[i-1]["season"] + 1):
        back_to_back = sorted_champs.iloc[i]
        b2b_streak += 1
    else:
        b2b_streak = 1

max_score_row = champions.loc[champions["champion_score"].idxmax()]
first_champ = sorted_champs.iloc[0]

c7, c8, c9 = st.columns(3)
with c7:
    if back_to_back is not None:
        st.markdown(trivia_card("Back-to-Back Champion", back_to_back["champion_manager"],
            f"Repeated in {int(back_to_back['season'])} with {back_to_back['champion_team']}"), unsafe_allow_html=True)
    else:
        st.markdown(trivia_card("Back-to-Back", "No Repeat Yet",
            "Nobody has successfully defended their title"), unsafe_allow_html=True)
with c8:
    st.markdown(trivia_card("Highest Winning Score", str(max_score_row["season"]),
        f"{max_score_row['champion_team']} dropped {max_score_row['champion_score']:.2f} pts in the final"), unsafe_allow_html=True)
with c9:
    st.markdown(trivia_card("The Original", str(first_champ["season"]),
        f"{first_champ['champion_team']} — {first_champ['champion_manager']} — the first to hoist it"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── CHAMPIONSHIP PAIN ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">The Other Side of the Story</div>'
    '<div class="tl-section-title">Championship Pain</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Championships tell one side of the story. The near-misses, the collapses, and the heartbreaks tell the other.</p>',
    unsafe_allow_html=True,
)

# Compute pain metrics
champions["margin"] = champions["champion_score"] - champions["runner_up_score"]
_ru_counts = champions.groupby("runner_up_manager").size().sort_values(ascending=False)
_most_ru = _ru_counts.index[0]
_most_ru_n = int(_ru_counts.iloc[0])

# 3rd place finishes
_champ_pg = pg[pg["bracket"] == "championship"]
_3rd_pg = _champ_pg[_champ_pg["game_type"] == "3rd_place"]
_3rd_winners = pd.concat([
    _3rd_pg[_3rd_pg["winner"] == _3rd_pg["team_1"]][["season","team_1"]].rename(columns={"team_1":"team"}),
    _3rd_pg[_3rd_pg["winner"] == _3rd_pg["team_2"]][["season","team_2"]].rename(columns={"team_2":"team"}),
]).drop_duplicates()
_tnh_lookup = tnh.set_index(["season","team_name"])["canonical_name"].to_dict()
_3rd_mgr = _3rd_winners.copy()
_3rd_mgr["manager"] = _3rd_mgr.apply(lambda r: _tnh_lookup.get((int(r["season"]),r["team"]),r["team"]),axis=1)
_3rd_counts = _3rd_mgr.groupby("manager").size().sort_values(ascending=False)
_most_3rd = _3rd_counts.index[0] if len(_3rd_counts)>0 else "—"
_most_3rd_n = int(_3rd_counts.iloc[0]) if len(_3rd_counts)>0 else 0

# Closest loss (runner-up who lost by the smallest margin)
_closest_loss = champions.loc[champions["margin"].idxmin()]
_biggest_loss  = champions.loc[champions["margin"].idxmax()]

# Best RS team to not win that year (highest win pct in RS that did not win the championship)
_ms_idx = manager_stats.set_index("canonical_name")
_pain_rows = []
for _, champ_row in champions.iterrows():
    szn = int(champ_row["season"])
    szn_std = std[std["season"] == szn].copy()
    tnh_szn = tnh[tnh["season"] == szn].set_index("team_name")["canonical_name"].to_dict()
    szn_std["manager"] = szn_std["team_name"].map(tnh_szn)
    szn_std = szn_std.dropna(subset=["manager"])
    szn_std["gp"] = szn_std["wins"] + szn_std["losses"] + szn_std["ties"]
    szn_std["wpc"] = szn_std["wins"] / szn_std["gp"].replace(0, float("nan"))
    best_rs = szn_std.sort_values("wpc", ascending=False).iloc[0]
    if best_rs["manager"] != champ_row["champion_manager"]:
        _pain_rows.append({"season": szn, "manager": best_rs["manager"],
                            "wins": int(best_rs["wins"]), "losses": int(best_rs["losses"]),
                            "wpc": float(best_rs["wpc"] or 0)})
_best_rs_no_title = pd.DataFrame(_pain_rows).sort_values("wpc", ascending=False)

# Most appearances with zero titles (active managers)
_active_no_title = manager_stats[
    (manager_stats["championships"] == 0) & (manager_stats["playoff_apps"] >= 3)
].sort_values("playoff_apps", ascending=False)

def _pain_card(icon, title, headline, sub, color="#F87171"):
    return (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid {color};'
        f'border-radius:6px;padding:16px 18px;height:100%;">'
        f'<div style="font-size:1.5rem;margin-bottom:6px;">{icon}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.58rem;color:#A7B0BC;'
        f'letter-spacing:3px;text-transform:uppercase;margin-bottom:4px;">{title}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;color:{color};'
        f'letter-spacing:2px;line-height:1.1;margin-bottom:6px;">{headline}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#A7B0BC;'
        f'line-height:1.5;">{sub}</div>'
        f'</div>'
    )

p1, p2, p3 = st.columns(3)
with p1:
    _ru_years = sorted(champions[champions["runner_up_manager"] == _most_ru]["season"].tolist())
    _yr_str = ", ".join(str(y) for y in _ru_years)
    st.markdown(_pain_card(
        "💔", "Most Runner-Up Finishes",
        f"{MANAGER_EMOJI.get(_most_ru,'👤')} {_most_ru} — {_most_ru_n}×",
        f"Runner-up in {_yr_str}. Every trip to the final ended the same way.",
    ), unsafe_allow_html=True)
with p2:
    if len(_3rd_counts) > 0:
        _3rd_yrs = _3rd_mgr[_3rd_mgr["manager"] == _most_3rd]["season"].sort_values().tolist()
        _3rd_yr_str = ", ".join(str(y) for y in _3rd_yrs)
        st.markdown(_pain_card(
            "🥉", "Most Third-Place Finishes",
            f"{MANAGER_EMOJI.get(_most_3rd,'👤')} {_most_3rd} — {_most_3rd_n}×",
            f"Close enough to feel it. Not close enough to win it. Third place in {_3rd_yr_str}.",
        ), unsafe_allow_html=True)
with p3:
    if len(_active_no_title) > 0:
        _hb = _active_no_title.iloc[0]
        st.markdown(_pain_card(
            "⏳", "Most Appearances, Still Waiting",
            f"{MANAGER_EMOJI.get(_hb['canonical_name'],'👤')} {_hb['canonical_name']} — {int(_hb['playoff_apps'])} Trips",
            f"{int(_hb['playoff_apps'])} playoff appearances. Zero championships. "
            f"The trophy has been tantalizingly close.",
        ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
p4, p5, p6 = st.columns(3)
with p4:
    st.markdown(_pain_card(
        "😤", "Closest Championship Loss",
        f"{_closest_loss['runner_up_manager']} · {int(_closest_loss['season'])}",
        f"{_closest_loss['runner_up_team']} lost to {_closest_loss['champion_team']} "
        f"by just {_closest_loss['margin']:.2f} points. The cruelest margin in league history.",
        color="#F59E0B",
    ), unsafe_allow_html=True)
with p5:
    st.markdown(_pain_card(
        "💀", "Biggest Championship Blowout Loss",
        f"{_biggest_loss['runner_up_manager']} · {int(_biggest_loss['season'])}",
        f"{_biggest_loss['runner_up_team']} lost by {_biggest_loss['margin']:.2f} points. "
        f"The most one-sided championship game in league history.",
        color="#EF4444",
    ), unsafe_allow_html=True)
with p6:
    if len(_best_rs_no_title) > 0:
        _bnw = _best_rs_no_title.iloc[0]
        st.markdown(_pain_card(
            "📈", "Best Regular Season, No Title",
            f"{MANAGER_EMOJI.get(_bnw['manager'],'👤')} {_bnw['manager']} · {int(_bnw['season'])}",
            f"{int(_bnw['wins'])}-{int(_bnw['losses'])} regular season record — the best that year. "
            f"Didn't matter when the playoffs started.",
            color="#A78BFA",
        ), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── YEAR-BY-YEAR RECORD ────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Complete Championship Game Record</div>'
    '<div class="tl-section-title">Every Final, Every Score</div>',
    unsafe_allow_html=True,
)

final_rows = []
for _, row in champions.sort_values("season", ascending=False).iterrows():
    emoji = MANAGER_EMOJI.get(row["champion_manager"], "🏆")
    final_rows.append([
        (f"{row['season']}", "gold"),
        f"{emoji} {row['champion_team']}",
        row["champion_manager"],
        (f"{row['champion_score']:.2f}", ""),
        f"{row['runner_up_team']}",
        row["runner_up_manager"],
        (f"{row['runner_up_score']:.2f}", "muted"),
        (f"{row['champion_score'] - row['runner_up_score']:.2f}", ""),
    ])

st.markdown(
    html_table(
        ["Season", "Champion", "Manager", "Score", "Runner-Up", "Manager", "Score", "Margin"],
        final_rows,
    ),
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="tl-section-label">Continue Exploring</div>',
    unsafe_allow_html=True,
)
_xp_cols = st.columns(3)
for _col, _href, _icon, _title, _desc in [
    (_xp_cols[0], "/franchise_profiles", "🏟️", "Franchise Dynasties", "Which franchises built the championship foundations? Lineage, stewardship, and legacies."),
    (_xp_cols[1], "/keeper_hall", "🔑", "Keeper Legacy", "The players behind the dynasties — who was kept, who won, and what it meant."),
    (_xp_cols[2], "/manager_profiles", "👤", "Manager Profiles", "Career records and Hall of Fame plaques for every competitor in league history."),
]:
    _col.markdown(
        f'<a href="{_href}" target="_self" style="display:block;background:#0F1B2D;border:1px solid #1E2D40;'
        f'border-radius:6px;padding:16px;text-decoration:none;">'
        f'<span style="display:block;font-size:1.5rem;margin-bottom:6px;">{_icon}</span>'
        f'<span style="display:block;font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#D4AF37;letter-spacing:2px;">{_title}</span>'
        f'<span style="display:block;font-family:\'Inter\',sans-serif;font-size:0.65rem;color:#A7B0BC;margin-top:4px;line-height:1.5;">{_desc}</span>'
        f'</a>',
        unsafe_allow_html=True,
    )

render_page_footer(
    href="/league_timeline",
    cta="EXPLORE THE TIMELINE",
    tagline="EVERY SEASON.<br>EVERY MOMENT.<br>EVERY UPSET.",
)
