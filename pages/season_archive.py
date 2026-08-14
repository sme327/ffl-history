"""Season Archive page — drill into any individual season.

All derivation lives in utils.data.get_season_detail(); this file is
presentation only, so the static build renders the same season from the
same source.
"""
from __future__ import annotations
import streamlit as st
from utils.data import get_all_seasons, get_season_detail
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="Season Archive · The Long Game",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("season_archive")

# ── SEASON SELECTOR ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-page-title">Season Archive</div>
    <div class="tl-page-subtitle">Select any season to explore its complete history.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

season = int(st.selectbox(
    "SELECT SEASON",
    options=get_all_seasons(),
    index=0,
    format_func=lambda s: f"{s} Season",
))

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

detail = get_season_detail(season)
champion = detail["champion"]

# ── SEASON TITLE + STORY ───────────────────────────────────────────────────────
if champion:
    story_col, nfl_col = st.columns([3, 2])
    with story_col:
        st.markdown(
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#A7B0BC;'
            f'letter-spacing:4px;text-transform:uppercase;margin-bottom:0.3rem;">{season} Season</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:3rem;color:#D4AF37;'
            f'letter-spacing:5px;line-height:1;margin-bottom:0.5rem;">{detail["title"]}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
            f'font-style:italic;margin-bottom:1rem;">{detail["hook"]}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#F5F5F5;'
            f'line-height:1.7;margin-bottom:1.25rem;">{detail["narrative"]}</div>'
            f'<div style="background:#0F1B2D;border:1px solid #B8902E;border-radius:6px;'
            f'padding:16px 20px;display:inline-block;">'
            f'<div style="font-size:2rem;margin-bottom:4px;">{champion["emoji"]}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.55rem;color:#A7B0BC;'
            f'letter-spacing:4px;text-transform:uppercase;">🏆 {season} Champion</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;color:#D4AF37;'
            f'letter-spacing:3px;line-height:1;margin:0.2rem 0;">{champion["team"]}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.85rem;color:#F5F5F5;'
            f'font-weight:600;">{champion["manager"]}</div>'
            f'<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#A7B0BC;'
            f'margin-top:0.4rem;">{champion["score"]:.2f} – {champion["runner_up_score"]:.2f} '
            f'over {champion["runner_up_team"]}</div>'
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
        for bullet in detail["nfl_context"]:
            st.markdown(
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#F5F5F5;'
                f'line-height:1.6;padding:8px 0;border-bottom:1px solid #1E2D40;">🏈 {bullet}</div>',
                unsafe_allow_html=True,
            )
        if detail["nfl_league_links"]:
            links = "".join(
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.66rem;color:#A7B0BC;padding:3px 0;">'
                f'<span style="color:#F5F5F5;">{l["player"]}</span> — '
                + ", ".join(f'{m["emoji"]} {m["manager"]}' + (" (kept)" if m["kept"] else "")
                            for m in l["managers"])
                + '</div>'
                for l in detail["nfl_league_links"]
            )
            st.markdown(
                f'<div style="margin-top:10px;padding-top:8px;border-top:1px solid #1E2D40;">'
                f'<div style="font-family:\'Inter\',sans-serif;font-size:0.55rem;color:#A7B0BC;'
                f'letter-spacing:3px;text-transform:uppercase;margin-bottom:4px;">On our rosters</div>'
                f'{links}</div>',
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

std_rows = []
for team in detail["standings"]:
    result_class = "gold" if "Champion" in team["result"] else ("muted" if team["result"] == "—" else "")
    std_rows.append([
        (team["result"], result_class),
        f'{team["emoji"]} {team["team"]}',
        team["manager"],
        f'{team["wins"]}-{team["losses"]}',
        (f'{team["points_for"]:.2f}', ""),
        (f'#{team["rs_rank"]}', "muted center"),
    ])

st.markdown(
    html_table(["Result", "Team", "Manager", "W-L", "Points For", "RS Finish"], std_rows),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PLAYOFF BRACKET ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Postseason</div>'
    '<div class="tl-section-title">Playoff Bracket</div>',
    unsafe_allow_html=True,
)

bracket = detail["bracket"]

if not bracket["rounds"]:
    st.markdown('<p style="color:#A7B0BC;">No playoff data available.</p>', unsafe_allow_html=True)
else:
    def matchup_card(game, highlight_final=False):
        seed1 = f'#{game["seed_1"]}' if game["seed_1"] is not None else ""
        seed2 = f'#{game["seed_2"]}' if game["seed_2"] is not None else ""
        t1_cls = " winner" if game["winner"] == game["team_1"] else ""
        t2_cls = " winner" if game["winner"] == game["team_2"] else ""
        return (
            f'<div class="tl-matchup{" champion-game" if highlight_final else ""}">'
            f'<div class="tl-matchup-team{t1_cls}"><span class="tl-matchup-seed">{seed1}</span>'
            f'<span class="tl-matchup-name">{game["team_1"]}</span>'
            f'<span class="tl-matchup-score">{game["score_1"]:.1f}</span></div>'
            f'<div class="tl-matchup-team{t2_cls}"><span class="tl-matchup-seed">{seed2}</span>'
            f'<span class="tl-matchup-name">{game["team_2"]}</span>'
            f'<span class="tl-matchup-score">{game["score_2"]:.1f}</span></div>'
            f'</div>'
        )

    cols = st.columns(len(bracket["rounds"]))

    for col, rnd in zip(cols, bracket["rounds"]):
        is_final = rnd["type"] == "final"

        # Space QF games apart; bundle championship + 3rd place in the final column
        cards = ""
        for i, game in enumerate(rnd["games"]):
            if is_final:
                margin_style = ' style="margin-top:3rem;"'
            elif i > 0 and rnd["type"] == "quarterfinal":
                margin_style = ' style="margin-top:1.25rem;"'
            else:
                margin_style = ""
            cards += f"<div{margin_style}>" + matchup_card(game, highlight_final=is_final) + "</div>"

        if is_final and bracket["third_place"]:
            cards += (
                '<div style="margin-top:4rem;opacity:0.75;">'
                '<div class="tl-bracket-round-label">3rd Place</div>'
                + matchup_card(bracket["third_place"])
                + "</div>"
            )

        with col:
            st.markdown(
                f'<div class="tl-bracket-round">'
                f'<div class="tl-bracket-round-label">{rnd["label"]}</div>'
                + cards
                + "</div>",
                unsafe_allow_html=True,
            )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── TOP SCORERS ────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Individual Performance</div>'
    '<div class="tl-section-title">Top Scorers</div>',
    unsafe_allow_html=True,
)

scorer_rows = [
    [
        (f'#{s["rank"]}', "muted center"),
        f'{s["emoji"]} {s["team"]}',
        s["manager"],
        (f'{s["points_for"]:.2f}', "gold"),
    ]
    for s in detail["top_scorers"]
]

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
