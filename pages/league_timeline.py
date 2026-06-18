"""League Timeline — every season, every moment, 25 years of history."""
import streamlit as st
from utils.data import get_timeline_events, CURRENT_SEASON, FOUNDED, MANAGER_EMOJI
from utils.styles import inject_css, render_nav, render_page_footer

st.set_page_config(
    page_title="Timeline · The Long Game",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("league_timeline")

# ── EVENT META ───────────────────────────────────────────────────────────────────
# (icon, hex_color, display_label)
EVENT_META: dict[str, tuple[str, str, str]] = {
    "championship": ("🏆", "#D4AF37", "Championship"),
    "dynasty":      ("👑", "#F5C518", "Dynasty"),
    "runner_up":    ("🥈", "#A7B0BC", "Runner-Up"),
    "steward_change": ("🔄", "#60A5FA", "Franchise Change"),
    "record":       ("⚡", "#F59E0B", "Record"),
    "milestone":    ("🏛️", "#34D399", "Milestone"),
    "heartbreak":   ("💔", "#F87171", "Heartbreak"),
    "breakthrough": ("🎯", "#10B981", "Breakthrough"),
    "collapse":     ("📉", "#EF4444", "Collapse"),
    "rivalry":      ("⚔️", "#FB923C", "Rivalry"),
    "draft":        ("📋", "#818CF8", "Draft"),
    "keeper":       ("🔒", "#A78BFA", "Keeper"),
    "rule_change":  ("📜", "#9CA3AF", "Rule Change"),
    "alumni":       ("👤", "#6B7280", "Alumni"),
    "note":         ("📝", "#9CA3AF", "Note"),
}

FILTER_GROUPS: dict[str, list[str]] = {
    "Championships": ["championship", "dynasty", "runner_up"],
    "Franchise Changes": ["steward_change", "milestone", "alumni"],
    "Records": ["record"],
    "Moments": ["heartbreak", "breakthrough", "collapse", "rivalry", "note"],
    "Draft & Keepers": ["draft", "keeper", "rule_change"],
}
ALL_TYPES = [t for types in FILTER_GROUPS.values() for t in types]

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

# ── LOAD DATA ────────────────────────────────────────────────────────────────────
all_events = get_timeline_events()
total_events = len(all_events)
total_seasons = all_events["season"].nunique()

# ── FILTERS ──────────────────────────────────────────────────────────────────────
fc1, fc2, fc3 = st.columns([3, 1, 1])

with fc1:
    selected_groups = st.multiselect(
        "FILTER BY CATEGORY",
        options=list(FILTER_GROUPS.keys()),
        default=list(FILTER_GROUPS.keys()),
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
active_types = [t for g in selected_groups for t in FILTER_GROUPS.get(g, [])]
if not selected_groups:
    active_types = ALL_TYPES

filtered = all_events[
    all_events["event_type"].isin(active_types) &
    all_events["show_on_league_timeline"].astype(bool)
].copy()

if importance_filter == "High only":
    filtered = filtered[filtered["importance"] == "high"]
elif importance_filter == "High + Medium":
    filtered = filtered[filtered["importance"].isin(["high", "medium"])]

# ── QUICK STATS ROW ───────────────────────────────────────────────────────────────
n_shown = len(filtered)
n_editorial = int((filtered["source"] == "editorial").sum())

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{total_seasons}</div>'
        f'<div class="tl-metric-label">Seasons</div></div>',
        unsafe_allow_html=True,
    )
with s2:
    st.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{n_shown}</div>'
        f'<div class="tl-metric-label">Events Shown</div></div>',
        unsafe_allow_html=True,
    )
with s3:
    st.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{total_events - len(all_events[all_events["source"]=="editorial"])}</div>'
        f'<div class="tl-metric-label">Computed Events</div></div>',
        unsafe_allow_html=True,
    )
with s4:
    st.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{n_editorial}</div>'
        f'<div class="tl-metric-label">Editorial Notes</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

if len(filtered) == 0:
    st.markdown(
        '<p style="color:#A7B0BC;text-align:center;padding:2rem;">No events match the current filters.</p>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── EVENT CARD RENDERER ───────────────────────────────────────────────────────────
def _event_card(row) -> str:
    etype = str(row.get("event_type", "note"))
    meta = EVENT_META.get(etype, ("📝", "#6B7280", etype.replace("_", " ").title()))
    icon, color, label = meta
    imp = str(row.get("importance", "medium"))
    source = str(row.get("source", "computed"))
    title = str(row.get("title", ""))
    desc = str(row.get("description", ""))
    mgr = str(row.get("manager", ""))
    mgr_emoji = MANAGER_EMOJI.get(mgr, "") if mgr else ""
    fid = str(row.get("franchise_id", ""))

    # Border weight by importance
    border_w = "4px" if imp == "high" else "3px" if imp == "medium" else "2px"
    bg = "rgba(212,175,55,0.04)" if imp == "high" else "#0F1B2D"
    title_size = "0.92rem" if imp == "high" else "0.87rem"

    editorial_badge = '<span class="tl-editorial-badge">✦ EDITORIAL</span>' if source == "editorial" else ""

    desc_html = "" if not desc or desc == "nan" else f'<div class="tl-event-desc">{desc}</div>'

    mgr_line = ""
    if mgr and mgr != "nan":
        mgr_line = (
            f'<div class="tl-event-mgr">'
            f'{mgr_emoji} {mgr}'
            f'{(" &nbsp;·&nbsp; " + fid) if fid and fid != "nan" else ""}'
            f'</div>'
        )

    return (
        f'<div class="tl-event-card" style="border-left:{border_w} solid {color};background:{bg};">'
        f'  <div style="font-size:1.3rem;flex-shrink:0;margin-top:1px;">{icon}</div>'
        f'  <div class="tl-event-card-body">'
        f'    <div class="tl-event-card-meta">'
        f'      <span class="tl-event-type-tag" style="color:{color};">{label.upper()}</span>'
        f'      {editorial_badge}'
        f'    </div>'
        f'    <div class="tl-event-title" style="font-size:{title_size};">{title}</div>'
        f'    {desc_html}'
        f'    {mgr_line}'
        f'  </div>'
        f'</div>'
    )

# ── TIMELINE RENDER ───────────────────────────────────────────────────────────────
seasons = sorted(filtered["season"].unique(), reverse=(sort_order == "Newest first"))

for season in seasons:
    szn_events = filtered[filtered["season"] == season].sort_values(
        by=["importance"],
        key=lambda s: s.map({"high": 0, "medium": 1, "low": 2}).fillna(1)
    )
    n_ev = len(szn_events)
    n_editorial_szn = int((szn_events["source"] == "editorial").sum())

    count_label = f"{n_ev} event{'s' if n_ev != 1 else ''}"
    if n_editorial_szn:
        count_label += f" · {n_editorial_szn} editorial"

    st.markdown(
        f"""<div class="tl-tl-year-header">
            <div class="tl-tl-year-num">{season}</div>
            <div class="tl-tl-year-line"></div>
            <div class="tl-tl-year-count">{count_label}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Separate high-importance events into wider display, rest into 2-col
    high_events = szn_events[szn_events["importance"] == "high"]
    other_events = szn_events[szn_events["importance"] != "high"]

    # High importance: full width
    for _, row in high_events.iterrows():
        st.markdown(_event_card(row), unsafe_allow_html=True)

    # Medium/low: two columns
    if len(other_events) > 0:
        rows_list = list(other_events.iterrows())
        for j in range(0, len(rows_list), 2):
            pair = rows_list[j:j+2]
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(_event_card(pair[0][1]), unsafe_allow_html=True)
            if len(pair) > 1:
                with col_b:
                    st.markdown(_event_card(pair[1][1]), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)
st.markdown(
    f'<div style="text-align:center;font-family:\'Inter\',sans-serif;font-size:0.62rem;'
    f'color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;padding:0.5rem 0 1rem;">'
    f'{total_events} TOTAL EVENTS &nbsp;·&nbsp; COMPUTED FROM LEAGUE DATA &nbsp;·&nbsp; '
    f'EDITORIAL ANNOTATIONS ADDED BY LEAGUE HISTORIAN</div>',
    unsafe_allow_html=True,
)

render_page_footer(
    href="/league_history",
    cta="SEE THE LEAGUE RECORDS",
    tagline="THE MOMENTS ARE RECORDED.<br>THE NUMBERS TELL ANOTHER STORY.",
)
