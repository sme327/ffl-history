"""Season Archive page — drill into any individual season."""
from __future__ import annotations
import streamlit as st
from utils.data import load_all, get_champions, get_playoff_result_for_team, MANAGER_EMOJI, CURRENT_SEASON
from utils.styles import inject_css, render_nav, render_page_footer, html_table
from utils.narratives import NFL_CONTEXT, SEASON_HOOKS

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

# ── SEASON TITLE + STORY ───────────────────────────────────────────────────────
champ_row = champions[champions["season"] == season]

# Compute context for title generation
_prev_champ_row = champions[champions["season"] == season - 1]
_prev_champ_mgr = _prev_champ_row.iloc[0]["champion_manager"] if len(_prev_champ_row) else None
_prev_champs_for_mgr = int((champions[champions["season"] < season]["champion_manager"] ==
    champ_row.iloc[0]["champion_manager"]).sum()) if len(champ_row) else 0

def _season_title(szn, c_mgr, c_team, ru_mgr, margin, is_repeat, prior_titles):
    if szn == 2001:
        return "The Beginning"
    if is_repeat:
        return "The Repeat"
    if prior_titles == 0:
        if margin < 5:
            return "The Breakthrough"
        if margin > 60:
            return "The Coronation"
        return "The Breakthrough"
    if margin < 3:
        return "Down to the Wire"
    if margin > 70:
        return "No Contest"
    if prior_titles >= 3:
        return "The Dynasty Continues"
    return f"The {szn} Championship"

def _season_narrative(szn, c_mgr, c_team, ru_mgr, ru_team, c_score, ru_score, is_first):
    margin = c_score - ru_score
    if is_first:
        opener = f"{c_mgr} had been working toward this moment."
    elif _prev_champ_mgr == c_mgr:
        opener = f"Back-to-back. {c_mgr} didn't let go of the trophy."
    else:
        opener = f"{c_mgr} knew what it took."
    if margin < 5:
        closer = (f"{c_team} survived {ru_team} by just {margin:.2f} points — "
                  f"the kind of margin that keeps you up at night if you're {ru_mgr}.")
    elif margin > 60:
        closer = (f"It wasn't close. {c_team} dismantled {ru_team} by {margin:.2f} points "
                  f"in one of the most dominant championship performances in league history.")
    else:
        closer = (f"{c_team} handled {ru_team} in the final, "
                  f"{c_score:.2f}–{ru_score:.2f}. {ru_mgr} came up just short.")
    return f"{opener} {closer}"

if len(champ_row):
    c = champ_row.iloc[0]
    _is_repeat = (_prev_champ_mgr == c["champion_manager"])
    _season_ttl = _season_title(
        season, c["champion_manager"], c["champion_team"],
        c["runner_up_manager"], c["champion_score"] - c["runner_up_score"],
        _is_repeat, _prev_champs_for_mgr,
    )
    _hook = SEASON_HOOKS.get(season, "")
    _narrative = _season_narrative(
        season, c["champion_manager"], c["champion_team"],
        c["runner_up_manager"], c["runner_up_team"],
        c["champion_score"], c["runner_up_score"], _prev_champs_for_mgr == 0,
    )
    _nfl_bullets = NFL_CONTEXT.get(season, [])

    # Layout: season title left, NFL context right
    story_col, nfl_col = st.columns([3, 2])
    with story_col:
        emoji = MANAGER_EMOJI.get(c["champion_manager"], "🏆")
        st.markdown(
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#A7B0BC;'
            f'letter-spacing:4px;text-transform:uppercase;margin-bottom:0.3rem;">{season} Season</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:3rem;color:#D4AF37;'
            f'letter-spacing:5px;line-height:1;margin-bottom:0.5rem;">{_season_ttl}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
            f'font-style:italic;margin-bottom:1rem;">{_hook}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#F5F5F5;'
            f'line-height:1.7;margin-bottom:1.25rem;">{_narrative}</div>'
            f'<div style="background:#0F1B2D;border:1px solid #B8902E;border-radius:6px;'
            f'padding:16px 20px;display:inline-block;">'
            f'<div style="font-size:2rem;margin-bottom:4px;">{emoji}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.55rem;color:#A7B0BC;'
            f'letter-spacing:4px;text-transform:uppercase;">🏆 {season} Champion</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;color:#D4AF37;'
            f'letter-spacing:3px;line-height:1;margin:0.2rem 0;">{c["champion_team"]}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.85rem;color:#F5F5F5;'
            f'font-weight:600;">{c["champion_manager"]}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#A7B0BC;'
            f'margin-top:0.4rem;">{c["champion_score"]:.2f} – {c["runner_up_score"]:.2f} '
            f'over {c["runner_up_team"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with nfl_col:
        st.markdown(
            f'<div style="background:#081120;border:1px solid #1E2D40;border-radius:6px;'
            f'padding:20px 22px;height:100%;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
            f'letter-spacing:3px;margin-bottom:12px;">NFL IN {season}</div>',
            unsafe_allow_html=True,
        )
        for bullet in _nfl_bullets:
            st.markdown(
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#F5F5F5;'
                f'line-height:1.6;padding:8px 0;border-bottom:1px solid #1E2D40;">🏈 {bullet}</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown(
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.5rem;color:#D4AF37;'
        f'letter-spacing:5px;">{season}</div>',
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
