"""League Timeline — every season, every moment, 25 years of history."""
import streamlit as st
from utils.data import get_timeline_events, CURRENT_SEASON, FOUNDED, MANAGER_EMOJI
from utils.styles import inject_css, render_nav, render_page_footer
from utils.narratives import LEAGUE_ERAS

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

# Era lookup: season → (era_name, era_color)
_ERA_BY_SEASON: dict[int, tuple[str, str]] = {}
for _era in LEAGUE_ERAS:
    for _yr in range(_era["start"], min(_era["end"], CURRENT_SEASON) + 1):
        _ERA_BY_SEASON[_yr] = (_era["short"], _era["color"])

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
_IMP_LABELS = {"high": "MAJOR", "medium": "NOTABLE", "low": "MINOR"}

def _event_card(row, force_full_width: bool = False) -> str:
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

    # Visual weight by importance
    is_major = imp == "high"
    border_w  = "5px" if is_major else "3px" if imp == "medium" else "2px"
    bg        = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06)" if is_major and color.startswith("#") and len(color)==7 else "#0F1B2D"
    title_sz  = "1.0rem" if is_major else "0.87rem"
    icon_sz   = "1.8rem" if is_major else "1.3rem"
    imp_label = _IMP_LABELS.get(imp, "MINOR")

    editorial_badge = (
        '<span class="tl-editorial-badge" style="background:rgba(167,139,250,0.15);'
        'color:#A78BFA;border:1px solid rgba(167,139,250,0.4);padding:1px 6px;'
        'border-radius:3px;font-size:0.55rem;letter-spacing:2px;">✦ EDITORIAL</span>'
        if source == "editorial" else ""
    )
    imp_badge = (
        f'<span style="font-size:0.58rem;font-weight:700;letter-spacing:2px;'
        f'color:{color};background:{color}18;padding:2px 6px;border-radius:3px;">{imp_label}</span>'
    )
    desc_html = "" if not desc or desc == "nan" else f'<div class="tl-event-desc" style="margin-top:6px;">{desc}</div>'
    mgr_line  = ""
    if mgr and mgr != "nan":
        mgr_line = (
            f'<div class="tl-event-mgr" style="margin-top:6px;">'
            f'{mgr_emoji} {mgr}'
            f'{(" &nbsp;·&nbsp; " + fid) if fid and fid != "nan" else ""}'
            f'</div>'
        )

    return (
        f'<div class="tl-event-card" style="border-left:{border_w} solid {color};background:{bg};'
        f'{"padding:18px 20px;" if is_major else ""}">'
        f'  <div style="font-size:{icon_sz};flex-shrink:0;margin-top:2px;">{icon}</div>'
        f'  <div class="tl-event-card-body">'
        f'    <div class="tl-event-card-meta" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">'
        f'      {imp_badge}'
        f'      <span class="tl-event-type-tag" style="color:{color};font-size:0.6rem;">{label.upper()}</span>'
        f'      {editorial_badge}'
        f'    </div>'
        f'    <div class="tl-event-title" style="font-size:{title_sz};{"font-weight:600;" if is_major else ""}">{title}</div>'
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

    era_name, era_color = _ERA_BY_SEASON.get(season, ("", "#6B7280"))
    era_badge = (
        f'<span style="font-size:0.55rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;'
        f'color:{era_color};background:{era_color}20;border:1px solid {era_color}50;'
        f'padding:2px 8px;border-radius:3px;margin-left:10px;">{era_name}</span>'
        if era_name else ""
    )

    st.markdown(
        f"""<div class="tl-tl-year-header">
            <div class="tl-tl-year-num">{season}{era_badge}</div>
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
