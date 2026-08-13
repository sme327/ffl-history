"""Champions page — all-time title holders.

Derivation lives in utils.data.get_champions_view(); this file renders it.
"""
from __future__ import annotations
import streamlit as st
from utils.data import CURRENT_SEASON, get_champions_view
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="Champions · The Long Game",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("champions")

view = get_champions_view()
totals = view["totals"]
trivia = view["trivia"]
pain = view["pain"]
top = view["top_manager"]
current = view["current_champion"]

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
st.markdown(
    f"""
    <div style="text-align:center;padding:0.75rem 0 1.25rem;">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.2rem;color:#A7B0BC;letter-spacing:4px;line-height:2.2;">
            {totals['seasons']} SEASONS &nbsp;·&nbsp; {totals['titles_awarded']} CHAMPIONS CROWNED &nbsp;·&nbsp; ONLY {totals['unique_managers']} MANAGERS HAVE EVER LIFTED THE TROPHY
        </div>
        <div style="display:flex;justify-content:center;gap:5rem;margin-top:1rem;flex-wrap:wrap;">
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:4px;text-transform:uppercase;margin-bottom:0.2rem;">Most Championships</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#D4AF37;letter-spacing:3px;">{top['emoji']}&nbsp;{top['manager']} &nbsp;—&nbsp; {top['championships']}</div>
            </div>
            <div>
                <div style="font-family:'Inter',sans-serif;font-size:0.58rem;color:#A7B0BC;letter-spacing:4px;text-transform:uppercase;margin-bottom:0.2rem;">Reigning Champion</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#D4AF37;letter-spacing:3px;">{current['emoji']}&nbsp;{current['champion_manager']} &nbsp;—&nbsp; {CURRENT_SEASON}</div>
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
    leaders = view["manager_leaders"]
    for i, (col, row) in enumerate(zip(st.columns(min(3, len(leaders))), leaders)):
        with col:
            st.markdown(
                f"""<div class="tl-trophy-card {"gold-border" if i == 0 else ""}">
                    <div style="font-size:2.5rem;">{row['emoji']}</div>
                    <div>
                        <div class="tl-trophy-count">{row['championships']}</div>
                        <div class="tl-trophy-name">{row['manager']}</div>
                        <div class="tl-trophy-years">{row['years']}</div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.64rem;color:#A7B0BC;margin-top:0.3rem;">{row['finals_apps']} Finals &nbsp;·&nbsp; {row['win_pct']:.0%} Win Rate</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    if len(leaders) > 3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            html_table(
                ["Manager", "Championships", "Years", "Finals (Win%)"],
                [
                    [
                        row["manager"],
                        (str(row["championships"]), "gold"),
                        (row["years"], "muted"),
                        (f'{row["finals_apps"]} ({row["win_pct"]:.0%})', "muted"),
                    ]
                    for row in leaders[3:]
                ],
            ),
            unsafe_allow_html=True,
        )

else:  # Franchises
    franchises = view["franchise_leaders"]
    for i, (col, row) in enumerate(zip(st.columns(min(3, len(franchises))), franchises)):
        with col:
            st.markdown(
                f"""<div class="tl-trophy-card {"gold-border" if i == 0 else ""}">
                    <div style="font-size:2.5rem;">{row['emoji']}</div>
                    <div>
                        <div class="tl-trophy-count">{row['championships']}</div>
                        <div class="tl-trophy-name">{row['franchise_id']}</div>
                        <div class="tl-trophy-years">Current: {row['current_manager']}</div>
                        <div class="tl-trophy-years">{row['years']}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    if len(franchises) > 3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            html_table(
                ["Franchise", "Current Manager", "Championships", "Years"],
                [
                    [
                        (row["franchise_id"], "gold"),
                        row["current_manager"],
                        (str(row["championships"]), "gold"),
                        (row["years"], "muted"),
                    ]
                    for row in franchises[3:]
                ],
            ),
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── CHAMPIONSHIP TIMELINE ──────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Chronological View</div>'
    '<div class="tl-section-title">Championship Timeline</div>',
    unsafe_allow_html=True,
)

tl_html = '<div style="padding:0.25rem 0;">'
for entry in view["chronological"]:
    pill_cls = "tl-year-dot-gold" if entry["championships"] > 1 else "tl-year-dot-solo"
    pills = "".join(f'<span class="{pill_cls}">{yr}</span>' for yr in entry["year_list"])
    tl_html += (
        f'<div class="tl-chron-entry">'
        f'<div class="tl-chron-mgr-col">'
        f'<span style="font-size:1rem;">{entry["emoji"]}</span><span>{entry["manager"]}</span>'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#A7B0BC;font-weight:400;">({entry["championships"]})</span>'
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

dynasties = view["dynasties"]
if dynasties:
    per_row = min(4, len(dynasties))
    for start in range(0, len(dynasties), per_row):
        batch = dynasties[start:start + per_row]
        if start > 0:
            st.markdown("<br>", unsafe_allow_html=True)
        for col, d in zip(st.columns(len(batch)), batch):
            plural = "s" if d["championships"] != 1 else ""
            with col:
                st.markdown(
                    f"""<div class="tl-dynasty-card">
                        <div style="font-size:2.8rem;margin-bottom:0.6rem;">{d['emoji']}</div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#D4AF37;letter-spacing:3px;line-height:1;">{d['manager']}</div>
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:3.5rem;color:#F5F5F5;line-height:1;margin:0.35rem 0 0.1rem;">{d['championships']}</div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin-bottom:0.75rem;">Championship{plural}</div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#A7B0BC;line-height:1.5;">{d['era_desc']}</div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.68rem;color:#A7B0BC;margin-top:0.15rem;">{d['titles']} titles in {d['finals_apps']} finals appearances</div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.7rem;color:#D4AF37;margin-top:0.6rem;letter-spacing:1px;">{d['years']}</div>
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


def trivia_card(label, headline, sub):
    return f"""
    <div class="tl-card">
        <div class="tl-section-label">{label}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{headline}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">{sub}</div>
    </div>"""


big, close, most_ru = trivia["biggest_blowout"], trivia["closest_final"], trivia["most_runner_up"]
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(trivia_card("Biggest Blowout", str(big["season"]),
        f'{big["champion_team"]} won by {big["margin"]:.2f} pts'), unsafe_allow_html=True)
with c2:
    st.markdown(trivia_card("Closest Title Game", str(close["season"]),
        f'{close["champion_team"]} survived by {close["margin"]:.2f} pts'), unsafe_allow_html=True)
with c3:
    st.markdown(trivia_card("Most Runner-Up Finishes", most_ru["manager"],
        f'{most_ru["count"]}× runner-up — still waiting'), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

high, low, most_finals = trivia["highest_scoring_final"], trivia["lowest_scoring_final"], trivia["most_finals"]
c4, c5, c6 = st.columns(3)
with c4:
    st.markdown(trivia_card("Highest-Scoring Final", str(high["season"]),
        f'{high["champion_score"]:.2f} + {high["runner_up_score"]:.2f} = {high["combined"]:.2f} combined'), unsafe_allow_html=True)
with c5:
    st.markdown(trivia_card("Defensive Masterclass", str(low["season"]),
        f'Only {low["combined"]:.2f} pts combined — {low["champion_team"]} edged it'), unsafe_allow_html=True)
with c6:
    st.markdown(trivia_card("Most Finals Appearances", most_finals["manager"],
        f'{most_finals["finals_apps"]} trips to the title game '
        f'({most_finals["titles"]}W–{most_finals["runner_ups"]}L)'), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

b2b, best_score, first = trivia["back_to_back"], trivia["highest_winning_score"], trivia["first_champion"]
c7, c8, c9 = st.columns(3)
with c7:
    if b2b:
        st.markdown(trivia_card("Back-to-Back Champion", b2b["manager"],
            f'Repeated in {b2b["season"]} with {b2b["team"]}'), unsafe_allow_html=True)
    else:
        st.markdown(trivia_card("Back-to-Back", "No Repeat Yet",
            "Nobody has successfully defended their title"), unsafe_allow_html=True)
with c8:
    st.markdown(trivia_card("Highest Winning Score", str(best_score["season"]),
        f'{best_score["champion_team"]} dropped {best_score["champion_score"]:.2f} pts in the final'), unsafe_allow_html=True)
with c9:
    st.markdown(trivia_card("The Original", str(first["season"]),
        f'{first["champion_team"]} — {first["champion_manager"]} — the first to hoist it'), unsafe_allow_html=True)

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


ru, third, waiting = pain["most_runner_up"], pain["most_third"], pain["still_waiting"]
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown(_pain_card(
        "💔", "Most Runner-Up Finishes",
        f'{ru["emoji"]} {ru["manager"]} — {ru["count"]}×',
        f'Runner-up in {", ".join(str(y) for y in ru["years"])}. Every trip to the final ended the same way.',
    ), unsafe_allow_html=True)
with p2:
    if third:
        st.markdown(_pain_card(
            "🥉", "Most Third-Place Finishes",
            f'{third["emoji"]} {third["manager"]} — {third["count"]}×',
            f'Close enough to feel it. Not close enough to win it. '
            f'Third place in {", ".join(str(y) for y in third["years"])}.',
        ), unsafe_allow_html=True)
with p3:
    if waiting:
        st.markdown(_pain_card(
            "⏳", "Most Appearances, Still Waiting",
            f'{waiting["emoji"]} {waiting["manager"]} — {waiting["playoff_apps"]} Trips',
            f'{waiting["playoff_apps"]} playoff appearances. Zero championships. '
            f'The trophy has been tantalizingly close.',
        ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

closest_loss, biggest_loss, best_rs = pain["closest_loss"], pain["biggest_loss"], pain["best_rs_no_title"]
p4, p5, p6 = st.columns(3)
with p4:
    st.markdown(_pain_card(
        "😤", "Closest Championship Loss",
        f'{closest_loss["runner_up_manager"]} · {closest_loss["season"]}',
        f'{closest_loss["runner_up_team"]} lost to {closest_loss["champion_team"]} '
        f'by just {closest_loss["margin"]:.2f} points. The cruelest margin in league history.',
        color="#F59E0B",
    ), unsafe_allow_html=True)
with p5:
    st.markdown(_pain_card(
        "💀", "Biggest Championship Blowout Loss",
        f'{biggest_loss["runner_up_manager"]} · {biggest_loss["season"]}',
        f'{biggest_loss["runner_up_team"]} lost by {biggest_loss["margin"]:.2f} points. '
        f'The most one-sided championship game in league history.',
        color="#EF4444",
    ), unsafe_allow_html=True)
with p6:
    if best_rs:
        st.markdown(_pain_card(
            "📈", "Best Regular Season, No Title",
            f'{best_rs["emoji"]} {best_rs["manager"]} · {best_rs["season"]}',
            f'{best_rs["wins"]}-{best_rs["losses"]} regular season record — the best that year. '
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

st.markdown(
    html_table(
        ["Season", "Champion", "Manager", "Score", "Runner-Up", "Manager", "Score", "Margin"],
        [
            [
                (str(f["season"]), "gold"),
                f'{f["emoji"]} {f["champion_team"]}',
                f["champion_manager"],
                (f'{f["champion_score"]:.2f}', ""),
                f["runner_up_team"],
                f["runner_up_manager"],
                (f'{f["runner_up_score"]:.2f}', "muted"),
                (f'{f["margin"]:.2f}', ""),
            ]
            for f in view["finals"]
        ],
    ),
    unsafe_allow_html=True,
)

st.markdown('<div class="tl-section-label">Continue Exploring</div>', unsafe_allow_html=True)

for col, (href, icon, title, desc) in zip(st.columns(3), [
    ("/franchise_profiles", "🏟️", "Franchise Dynasties", "Which franchises built the championship foundations? Lineage, stewardship, and legacies."),
    ("/keeper_hall", "🔑", "Keeper Legacy", "The players behind the dynasties — who was kept, who won, and what it meant."),
    ("/manager_profiles", "👤", "Manager Profiles", "Career records and Hall of Fame plaques for every competitor in league history."),
]):
    col.markdown(
        f'<a href="{href}" target="_self" style="display:block;background:#0F1B2D;border:1px solid #1E2D40;'
        f'border-radius:6px;padding:16px;text-decoration:none;">'
        f'<span style="display:block;font-size:1.5rem;margin-bottom:6px;">{icon}</span>'
        f'<span style="display:block;font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#D4AF37;letter-spacing:2px;">{title}</span>'
        f'<span style="display:block;font-family:\'Inter\',sans-serif;font-size:0.65rem;color:#A7B0BC;margin-top:4px;line-height:1.5;">{desc}</span>'
        f'</a>',
        unsafe_allow_html=True,
    )

render_page_footer(
    href="/league_timeline",
    cta="EXPLORE THE TIMELINE",
    tagline="EVERY SEASON.<br>EVERY MOMENT.<br>EVERY UPSET.",
)
