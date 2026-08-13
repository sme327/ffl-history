"""League Timeline — every season, every moment, 25 years of history.

Event enrichment and season grouping live in utils.data; the taxonomy lives in
utils.narratives. This file filters and renders.
"""
import streamlit as st
from utils.data import (
    CURRENT_SEASON, FOUNDED, get_timeline_view, group_timeline_by_season,
)
from utils.styles import inject_css, render_nav, render_page_footer

st.set_page_config(
    page_title="Timeline · The Long Game",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("league_timeline")

view = get_timeline_view()
stats = view["stats"]
filter_groups = view["filter_groups"]

# ── PAGE HEADER ──────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-page-title">League Timeline</div>
    <div class="tl-page-subtitle">
        {CURRENT_SEASON - FOUNDED + 1} seasons &nbsp;·&nbsp;
        {CURRENT_SEASON - FOUNDED + 1} champions crowned &nbsp;·&nbsp;
        every moment that mattered
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── FILTERS ──────────────────────────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns([3, 1, 1])

with fc1:
    selected_groups = st.multiselect(
        "FILTER BY CATEGORY",
        options=list(filter_groups.keys()),
        default=list(filter_groups.keys()),
        label_visibility="collapsed",
        placeholder="Filter categories…",
    )

with fc2:
    importance_filter = st.selectbox(
        "IMPORTANCE",
        ["All", "High only", "High + Medium"],
        label_visibility="collapsed",
        index=0,
    )

with fc3:
    sort_order = st.radio(
        "ORDER",
        ["Newest first", "Oldest first"],
        horizontal=True,
        label_visibility="collapsed",
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── APPLY FILTERS ────────────────────────────────────────────────────────────────
active_types = [t for g in selected_groups for t in filter_groups.get(g, [])]
if not selected_groups:
    active_types = view["all_types"]

filtered = [
    e for e in view["events"]
    if e["event_type"] in active_types and e["show_on_league_timeline"]
]

if importance_filter == "High only":
    filtered = [e for e in filtered if e["importance"] == "high"]
elif importance_filter == "High + Medium":
    filtered = [e for e in filtered if e["importance"] in ("high", "medium")]

# ── QUICK STATS ROW ───────────────────────────────────────────────────────────────
n_shown = len(filtered)
n_editorial = sum(1 for e in filtered if e["is_editorial"])

for col, value, label in zip(
    st.columns(4),
    [stats["total_seasons"], n_shown, stats["computed_events"], n_editorial],
    ["Seasons", "Events Shown", "Computed Events", "Editorial Notes"],
):
    with col:
        st.markdown(
            f'<div class="tl-metric"><div class="tl-metric-value">{value}</div>'
            f'<div class="tl-metric-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

if not filtered:
    st.markdown(
        '<p style="color:#A7B0BC;text-align:center;padding:2rem;">No events match the current filters.</p>',
        unsafe_allow_html=True,
    )
    st.stop()


# ── EVENT CARD RENDERER ───────────────────────────────────────────────────────────
def _event_card(event: dict) -> str:
    color = event["color"]
    is_major = event["importance"] == "high"

    # Visual weight by importance
    border_w = "5px" if is_major else "3px" if event["importance"] == "medium" else "2px"
    bg = (
        f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06)"
        if is_major and color.startswith("#") and len(color) == 7
        else "#0F1B2D"
    )
    title_sz = "1.0rem" if is_major else "0.87rem"
    icon_sz = "1.8rem" if is_major else "1.3rem"

    editorial_badge = (
        '<span class="tl-editorial-badge" style="background:rgba(167,139,250,0.15);'
        'color:#A78BFA;border:1px solid rgba(167,139,250,0.4);padding:1px 6px;'
        'border-radius:3px;font-size:0.55rem;letter-spacing:2px;">✦ EDITORIAL</span>'
        if event["is_editorial"] else ""
    )
    imp_badge = (
        f'<span style="font-size:0.58rem;font-weight:700;letter-spacing:2px;'
        f'color:{color};background:{color}18;padding:2px 6px;border-radius:3px;">'
        f'{event["importance_label"]}</span>'
    )
    desc_html = (
        f'<div class="tl-event-desc" style="margin-top:6px;">{event["description"]}</div>'
        if event["description"] else ""
    )
    mgr_line = ""
    if event["manager"]:
        franchise = f' &nbsp;·&nbsp; {event["franchise_id"]}' if event["franchise_id"] else ""
        mgr_line = (
            f'<div class="tl-event-mgr" style="margin-top:6px;">'
            f'{event["manager_emoji"]} {event["manager"]}{franchise}'
            f'</div>'
        )

    return (
        f'<div class="tl-event-card" style="border-left:{border_w} solid {color};background:{bg};'
        f'{"padding:18px 20px;" if is_major else ""}">'
        f'  <div style="font-size:{icon_sz};flex-shrink:0;margin-top:2px;">{event["icon"]}</div>'
        f'  <div class="tl-event-card-body">'
        f'    <div class="tl-event-card-meta" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">'
        f'      {imp_badge}'
        f'      <span class="tl-event-type-tag" style="color:{color};font-size:0.6rem;">{event["label"].upper()}</span>'
        f'      {editorial_badge}'
        f'    </div>'
        f'    <div class="tl-event-title" style="font-size:{title_sz};{"font-weight:600;" if is_major else ""}">{event["title"]}</div>'
        f'    {desc_html}'
        f'    {mgr_line}'
        f'  </div>'
        f'</div>'
    )


# ── TIMELINE RENDER ───────────────────────────────────────────────────────────────
for block in group_timeline_by_season(filtered, newest_first=(sort_order == "Newest first")):
    era = block["era"]
    era_badge = (
        f'<span style="font-size:0.55rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
        f'color:{era["color"]};background:{era["color"]}20;border:1px solid {era["color"]}50;'
        f'padding:2px 8px;border-radius:3px;margin-left:10px;">{era["name"]}</span>'
        if era["name"] else ""
    )

    st.markdown(
        f"""<div class="tl-tl-year-header">
            <div class="tl-tl-year-num">{block["season"]}{era_badge}</div>
            <div class="tl-tl-year-line"></div>
            <div class="tl-tl-year-count">{block["count_label"]}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # High importance: full width
    for event in block["high"]:
        st.markdown(_event_card(event), unsafe_allow_html=True)

    # Medium/low: two columns
    others = block["other"]
    for j in range(0, len(others), 2):
        pair = others[j:j + 2]
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(_event_card(pair[0]), unsafe_allow_html=True)
        if len(pair) > 1:
            with col_b:
                st.markdown(_event_card(pair[1]), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)
st.markdown(
    f'<div style="text-align:center;font-family:\'Inter\',sans-serif;font-size:0.62rem;'
    f'color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;padding:0.5rem 0 1rem;">'
    f'{stats["total_events"]} TOTAL EVENTS &nbsp;·&nbsp; COMPUTED FROM LEAGUE DATA &nbsp;·&nbsp; '
    f'EDITORIAL ANNOTATIONS ADDED BY LEAGUE HISTORIAN</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="margin:2.5rem 0 1.5rem;">
        <div style="font-family:'Playfair Display',Georgia,serif;font-size:0.65rem;
            letter-spacing:4px;color:#A7B0BC;text-transform:uppercase;margin-bottom:1rem;">
            EXPLORE THE ARCHIVE
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <a href="/champions" style="flex:1;min-width:160px;background:#0F1B2D;
                border:1px solid rgba(212,175,55,0.3);border-radius:8px;padding:14px 16px;
                text-decoration:none;display:block;">
                <div style="font-size:1.1rem;margin-bottom:4px;">🏆</div>
                <div style="font-family:'Playfair Display',serif;font-size:0.78rem;
                    color:#D4AF37;font-weight:600;">Trophy Room</div>
                <div style="font-size:0.72rem;color:#A7B0BC;margin-top:3px;">
                    Every championship, every dynasty
                </div>
            </a>
            <a href="/league_history" style="flex:1;min-width:160px;background:#0F1B2D;
                border:1px solid rgba(52,211,153,0.3);border-radius:8px;padding:14px 16px;
                text-decoration:none;display:block;">
                <div style="font-size:1.1rem;margin-bottom:4px;">📖</div>
                <div style="font-family:'Playfair Display',serif;font-size:0.78rem;
                    color:#34D399;font-weight:600;">League History</div>
                <div style="font-size:0.72rem;color:#A7B0BC;margin-top:3px;">
                    The eras, the evolution, the numbers
                </div>
            </a>
            <a href="/season_archive" style="flex:1;min-width:160px;background:#0F1B2D;
                border:1px solid rgba(96,165,250,0.3);border-radius:8px;padding:14px 16px;
                text-decoration:none;display:block;">
                <div style="font-size:1.1rem;margin-bottom:4px;">📅</div>
                <div style="font-family:'Playfair Display',serif;font-size:0.78rem;
                    color:#60A5FA;font-weight:600;">Season Archive</div>
                <div style="font-size:0.72rem;color:#A7B0BC;margin-top:3px;">
                    Deep-dive into any individual season
                </div>
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_page_footer(
    href="/league_history",
    cta="SEE THE LEAGUE RECORDS",
    tagline="THE MOMENTS ARE RECORDED.<br>THE NUMBERS TELL ANOTHER STORY.",
)
