"""Home page — The Long Game.

Derivation lives in utils.data.get_home_view(); this file is presentation only.
"""
import streamlit as st
from utils.data import get_home_view, CURRENT_SEASON
from utils.styles import inject_css, render_nav, metric_card

st.set_page_config(
    page_title="The Long Game",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("home")

home = get_home_view()
stats = home["stats"]
storylines = home["storylines"]

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-hero">
        <div class="tl-hero-title">THE LONG GAME</div>
        <div class="tl-hero-subtitle">A Quarter Century of {{insert witty name here}} Glory</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.88rem;color:#A7B0BC;
                    margin-top:1.1rem;letter-spacing:1px;font-style:italic;line-height:1.8;">
            Built by friendship.&nbsp; Defined by competition.&nbsp; Occasionally ruined by a waiver wire mistake.
        </div>
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── CURRENT CHAMPION ──────────────────────────────────────────────────────────
current = home["current_champion"]
if current:
    title_badge = (
        f" &nbsp;·&nbsp; {current['titles_all_time']}× Champion"
        if current["titles_all_time"] > 1 else ""
    )
    st.markdown(
        '<div style="text-align:center;" class="tl-section-label">Reigning Champion</div>',
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 3, 1])
    with col:
        st.markdown(
            f"""
            <div class="tl-champion-card" style="padding:3rem 2.5rem;box-shadow:0 0 80px rgba(212,175,55,0.22);">
                <div style="font-size:4rem;margin-bottom:0.5rem;">{current['emoji']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:6px;text-transform:uppercase;">🏆 {CURRENT_SEASON} League Champion 🏆</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:4.5rem;color:#D4AF37;letter-spacing:5px;line-height:1;margin:0.3rem 0 0.25rem;">{current['team']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:1.05rem;color:#F5F5F5;font-weight:500;">{current['manager']}{title_badge}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.8rem;color:#A7B0BC;margin-top:0.75rem;">{current['score']:.2f} – {current['runner_up_score']:.2f} over {current['runner_up_team']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── LEAGUE METRICS ────────────────────────────────────────────────────────────
for col, value, label in zip(
    st.columns(4),
    [str(stats["seasons"]), str(stats["active_managers"]),
     str(stats["unique_champions"]), f"{stats['total_games']:,}"],
    ["Seasons", "Active Members", "Different Champions", "Matchups Played"],
):
    with col:
        st.markdown(metric_card(value, label), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── RECENT CHAMPIONS ──────────────────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center;" class="tl-section-label">Recent Champions</div>',
    unsafe_allow_html=True,
)

for col, champ in zip(st.columns(5), home["recent_champions"]):
    trophy_html = (
        f'<div class="tl-mini-champ-mgr" style="color:#D4AF37;font-size:0.7rem;">'
        f'{"🏆" * champ["titles_to_date"]} — {champ["titles_to_date"]}× champ</div>'
        if champ["titles_to_date"] > 1 else ""
    )
    with col:
        st.markdown(
            f"""
            <div class="tl-mini-champ">
                <div style="font-size:1.5rem;">{champ['emoji']}</div>
                <div class="tl-mini-champ-year">{champ['season']}</div>
                <div class="tl-mini-champ-team">{champ['team']}</div>
                <div class="tl-mini-champ-mgr">{champ['manager']}</div>
                {trophy_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── LEAGUE LEGENDS ────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label" style="text-align:center;">All-Time</div>'
    '<div style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2rem;'
    'color:#F5F5F5;letter-spacing:4px;margin-bottom:1.25rem;">League Legends</div>',
    unsafe_allow_html=True,
)

top_legends = home["legends"][:4]
drought = home["drought"]
leg_cols = st.columns(max(len(top_legends) + (1 if drought else 0), 1))

for col, legend in zip(leg_cols, top_legends):
    plural = "s" if legend["titles"] != 1 else ""
    with col:
        st.markdown(
            f"""<div class="tl-card" style="text-align:center;padding:1.5rem 1rem;">
                <div style="font-size:2.2rem;margin-bottom:0.4rem;">{legend['emoji']}</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.6rem;color:#D4AF37;letter-spacing:2px;line-height:1;">{legend['titles']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin:0.1rem 0 0.4rem;">Championship{plural}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#F5F5F5;font-weight:600;">{legend['manager']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.64rem;color:#A7B0BC;margin-top:0.15rem;">{legend['years']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if drought:
    with leg_cols[len(top_legends)]:
        st.markdown(
            f"""<div class="tl-card" style="text-align:center;padding:1.5rem 1rem;border-color:rgba(184,144,46,0.4);">
                <div style="font-size:2.2rem;margin-bottom:0.4rem;">{drought['emoji']}</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:2.6rem;color:#A7B0BC;letter-spacing:2px;line-height:1;">{drought['playoff_apps']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.6rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin:0.1rem 0 0.4rem;">Playoff Trips &nbsp;·&nbsp; 0 Titles</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#F5F5F5;font-weight:600;">{drought['manager']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.64rem;color:#A7B0BC;margin-top:0.15rem;">Still waiting...</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── LEAGUE STORYLINES ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label" style="text-align:center;">The Numbers Behind the Legend</div>'
    '<div style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2rem;'
    'color:#F5F5F5;letter-spacing:4px;margin-bottom:1.25rem;">League Storylines</div>',
    unsafe_allow_html=True,
)


def _story(label, headline, sub):
    return (
        f'<div class="tl-card">'
        f'<div class="tl-section-label">{label}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:#D4AF37;'
        f'letter-spacing:2px;line-height:1.1;margin:0.2rem 0;">{headline}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
        f'margin-top:0.35rem;line-height:1.5;">{sub}</div>'
        f'</div>'
    )


most = storylines["most_championships"]
best = storylines["best_season"]
scorer = storylines["top_scorer"]

best_headline = (
    f"{best['record']} ({' & '.join(str(y) for y in best['seasons'])})"
    if len(best["seasons"]) > 1
    else f"{best['record']} in {best['seasons'][0]}"
)

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(_story(
        "Most Championships",
        f"{most['titles']}× — {most['manager']}",
        f"Won in {most['years']}. The benchmark everyone is chasing.",
    ), unsafe_allow_html=True)
with sc2:
    st.markdown(_story("Best Regular Season", best_headline, best["summary"]), unsafe_allow_html=True)
with sc3:
    if drought:
        st.markdown(_story(
            "Most Trips Without a Title",
            f"{drought['playoff_apps']} Appearances",
            f"{drought['manager']} — the playoffs keep calling. The trophy doesn't.",
        ), unsafe_allow_html=True)
with sc4:
    st.markdown(_story(
        "All-Time Scoring Leader",
        f"{scorer['points_for']:,.0f} pts",
        f"{scorer['manager']} — more fantasy points than anyone in league history.",
    ), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider">', unsafe_allow_html=True)

# ── FEATURED EXHIBITS ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label" style="text-align:center;">Museum Destinations</div>'
    '<div style="text-align:center;font-family:\'Bebas Neue\',sans-serif;font-size:2rem;'
    'color:#F5F5F5;letter-spacing:4px;margin-bottom:0.4rem;">Explore the Exhibits</div>'
    '<div style="text-align:center;font-family:\'Inter\',sans-serif;font-size:0.75rem;'
    'color:#6B7280;margin-bottom:1.5rem;">Every section is a destination. Start anywhere.</div>',
    unsafe_allow_html=True,
)

EXHIBITS = [
    [
        ("🏆", "Trophy Room",     "Every champion. Every dynasty. The immortal record of who won and how.", "/champions"),
        ("📅", "Timeline",        "The historical spine of the league — every era, every turning point.",    "/league_timeline"),
        ("🔑", "Keeper Hall",     "25 years of attachment, loyalty, and the players nobody could let go.",   "/keeper_hall"),
    ],
    [
        ("📋", "Draft Legends",   "The obsessions, the archetypes, and the players everyone had to have.",   "/draft_center"),
        ("👤", "Manager Files",   "Career plaques, rivalries, and records for every competitor.",            "/manager_profiles"),
        ("🏟️", "Franchise Files", "Lineages, stewardship eras, and the franchises that built this league.",  "/franchise_profiles"),
    ],
]

for row in EXHIBITS:
    for col, (icon, title, desc, href) in zip(st.columns(3), row):
        with col:
            st.markdown(
                f"""<a href="{href}" class="tl-nav-card" target="_self">
                    <div style="font-size:0.55rem;color:#A7B0BC;letter-spacing:4px;text-transform:uppercase;margin-bottom:0.5rem;">EXHIBIT</div>
                    <div class="tl-nav-card-icon">{icon}</div>
                    <div class="tl-nav-card-title">{title}</div>
                    <div class="tl-nav-card-desc">{desc}</div>
                </a>""",
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

# ── TROPHY ROOM TEASER ────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align:center;padding:3rem 0 2rem;">
        <div style="height:1px;background:linear-gradient(to right,transparent,#D4AF37,transparent);margin:0 auto 2rem;max-width:400px;"></div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.6rem;color:#F5F5F5;letter-spacing:4px;line-height:1.8;">
            25 SEASONS.<br>{stats['unique_champions']} DIFFERENT CHAMPIONS.<br>ONE LEAGUE THAT NEVER QUIT.
        </div>
        <div style="margin-top:1.75rem;">
            <a href="/champions" target="_self"
               style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#D4AF37;
                      letter-spacing:4px;text-transform:uppercase;text-decoration:none;
                      border-bottom:1px solid rgba(212,175,55,0.6);padding-bottom:3px;">
                ENTER THE TROPHY ROOM &nbsp;&rarr;
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
