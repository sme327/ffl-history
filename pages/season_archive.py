"""Season Archive page — drill into any individual season."""
import streamlit as st
from utils.data import load_all, get_champions, get_playoff_result_for_team, MANAGER_EMOJI, CURRENT_SEASON
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="Season Archive · The Long Game",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("season_archive")

data = load_all()
champions = get_champions()
standings = data["standings"]
pg = data["playoff_games"]
tnh = data["team_name_history"]
wm = data["weekly_matchups"]

# ── SEASON SELECTOR ────────────────────────────────────────────────────────────
all_seasons = sorted(standings["season"].unique(), reverse=True)

st.markdown(
    """
    <div class="tl-page-title">Season Archive</div>
    <div class="tl-page-subtitle">Select any season to explore its complete history.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

season = st.selectbox(
    "SELECT SEASON",
    options=all_seasons,
    index=0,
    format_func=lambda s: f"{s} Season",
)
season = int(season)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SEASON CHAMPION HERO ───────────────────────────────────────────────────────
champ_row = champions[champions["season"] == season]
if len(champ_row):
    c = champ_row.iloc[0]
    emoji = MANAGER_EMOJI.get(c["champion_manager"], "🏆")
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            f"""
            <div class="tl-champion-card">
                <div style="font-size:2.5rem;">{emoji}</div>
                <div class="tl-champion-season">{season} Champion</div>
                <div class="tl-champion-team">{c['champion_team']}</div>
                <div class="tl-champion-manager">{c['champion_manager']}</div>
                <div class="tl-champion-score">
                    {c['champion_score']:.2f} – {c['runner_up_score']:.2f} over {c['runner_up_team']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── FINAL STANDINGS ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Regular Season</div>'
    '<div class="tl-section-title">Final Standings</div>',
    unsafe_allow_html=True,
)

szn_std = standings[standings["season"] == season].sort_values("rank")
tnh_szn = tnh[tnh["season"] == season].set_index("team_name")["canonical_name"].to_dict()

_result_rank = {
    "🏆 Champion": 1, "🥈 Runner-Up": 2, "🥉 3rd Place": 3, "4th Place": 4,
    "Semifinals": 5, "Playoffs": 6,
}

std_data = []
for _, row in szn_std.iterrows():
    manager = tnh_szn.get(row["team_name"], "—")
    playoff_r = get_playoff_result_for_team(season, row["team_name"], pg)
    rs_rank = int(row["rank"])
    sort_key = _result_rank.get(playoff_r, 100 + rs_rank)
    std_data.append({
        "sort_key": sort_key,
        "result": playoff_r,
        "team": row["team_name"],
        "manager": manager,
        "emoji": MANAGER_EMOJI.get(manager, ""),
        "wins": int(row["wins"]),
        "losses": int(row["losses"]),
        "pf": float(row["points_for"]),
        "rs_rank": rs_rank,
    })
std_data.sort(key=lambda x: x["sort_key"])

std_rows = []
for d in std_data:
    result_class = "gold" if "Champion" in d["result"] else ("muted" if d["result"] == "—" else "")
    std_rows.append([
        (d["result"], result_class),
        f"{d['emoji']} {d['team']}",
        d["manager"],
        f"{d['wins']}-{d['losses']}",
        (f"{d['pf']:.2f}", ""),
        (f"#{d['rs_rank']}", "muted center"),
    ])

st.markdown(
    html_table(
        ["Result", "Team", "Manager", "W-L", "Points For", "RS Finish"],
        std_rows,
    ),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PLAYOFF BRACKET ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Postseason</div>'
    '<div class="tl-section-title">Playoff Bracket</div>',
    unsafe_allow_html=True,
)

szn_pg = pg[(pg["season"] == season) & (pg["bracket"] == "championship")].sort_values(
    ["round", "game_type"]
)

if len(szn_pg) == 0:
    st.markdown('<p style="color:#A7B0BC;">No playoff data available.</p>', unsafe_allow_html=True)
else:
    def matchup_card(g, highlight_final=False):
        t1_win = g["winner"] == g["team_1"]
        t2_win = g["winner"] == g["team_2"]
        s1, s2 = float(g["score_1"]), float(g["score_2"])
        seed1 = f"#{int(g['seed_1'])}" if g.get("seed_1") and str(g["seed_1"]) not in ("nan", "") else ""
        seed2 = f"#{int(g['seed_2'])}" if g.get("seed_2") and str(g["seed_2"]) not in ("nan", "") else ""
        final_cls = " champion-game" if highlight_final else ""
        t1_cls = " winner" if t1_win else ""
        t2_cls = " winner" if t2_win else ""
        return (
            f'<div class="tl-matchup{final_cls}">'
            f'<div class="tl-matchup-team{t1_cls}"><span class="tl-matchup-seed">{seed1}</span>'
            f'<span class="tl-matchup-name">{g["team_1"]}</span>'
            f'<span class="tl-matchup-score">{s1:.1f}</span></div>'
            f'<div class="tl-matchup-team{t2_cls}"><span class="tl-matchup-seed">{seed2}</span>'
            f'<span class="tl-matchup-name">{g["team_2"]}</span>'
            f'<span class="tl-matchup-score">{s2:.1f}</span></div>'
            f'</div>'
        )

    round_order = ["quarterfinal", "semifinal", "final"]
    round_labels = {"quarterfinal": "Quarterfinals", "semifinal": "Semifinals", "final": "Championship"}

    rounds_present = [r for r in round_order if len(szn_pg[szn_pg["game_type"] == r]) > 0]
    third = szn_pg[szn_pg["game_type"] == "3rd_place"]

    num_rounds = len(rounds_present)
    cols = st.columns(num_rounds) if num_rounds > 0 else []

    for col, round_type in zip(cols, rounds_present):
        games = szn_pg[szn_pg["game_type"] == round_type]
        is_final = round_type == "final"

        # Space QF games apart; bundle championship + 3rd place in the final column
        gap_style = ' style="margin-top:1rem;"' if round_type == "quarterfinal" else ""
        cards = ""
        for i, (_, g) in enumerate(games.iterrows()):
            if is_final:
                margin_style = ' style="margin-top:3rem;"'
            elif i > 0 and round_type == "quarterfinal":
                margin_style = ' style="margin-top:1.25rem;"'
            else:
                margin_style = ""
            cards += f'<div{margin_style}>' + matchup_card(g, highlight_final=is_final) + '</div>'

        # Attach 3rd place game below championship in the same column
        if is_final and len(third) > 0:
            cards += (
                '<div style="margin-top:4rem;opacity:0.75;">'
                '<div class="tl-bracket-round-label">3rd Place</div>'
                + matchup_card(third.iloc[0])
                + '</div>'
            )

        round_html = (
            f'<div class="tl-bracket-round">'
            f'<div class="tl-bracket-round-label">{round_labels[round_type]}</div>'
            + cards
            + '</div>'
        )
        with col:
            st.markdown(round_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── TOP SCORERS ────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Individual Performance</div>'
    '<div class="tl-section-title">Top Scorers</div>',
    unsafe_allow_html=True,
)

rs_szn = wm[
    (wm["season"] == season) & (~wm["is_bye"]) & (~wm["is_playoff"])
].copy()

top_pf = (
    rs_szn.groupby("team_name")["team_score"]
    .sum()
    .reset_index(name="points_for")
    .sort_values("points_for", ascending=False)
    .reset_index(drop=True)
)

scorer_rows = []
for i, (_, row) in enumerate(top_pf.iterrows()):
    manager = tnh_szn.get(row["team_name"], "—")
    emoji = MANAGER_EMOJI.get(manager, "")
    scorer_rows.append([
        (f"#{i+1}", "muted center"),
        f"{emoji} {row['team_name']}",
        manager,
        (f"{row['points_for']:.2f}", "gold"),
    ])

_, col, _ = st.columns([1, 2, 1])
with col:
    st.markdown(
        html_table(["Rank", "Team", "Manager", "Total Points"], scorer_rows),
        unsafe_allow_html=True,
    )

render_page_footer(
    href="/manager_profiles",
    cta="MEET THE MANAGERS",
    tagline="SEASONS PASS.<br>THE PEOPLE REMAIN.",
)
