"""Draft Center — 25 years of picks, patterns, and player loyalty."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data import (
    get_draft_picks_with_pos, get_position_trends_data,
    get_draft_records, get_player_ownership,
    MANAGER_EMOJI, MANAGER_COLORS, CURRENT_SEASON, FOUNDED,
)
from utils.styles import inject_css, render_nav, render_page_footer, section_header

st.set_page_config(
    page_title="Draft Center · The Long Game",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("draft_center")

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
POS_COLORS = {
    "RB": "#22C55E", "WR": "#3B82F6", "QB": "#EF4444",
    "TE": "#F59E0B", "DEF": "#8B5CF6", "K": "#6B7280", "Other": "#374151",
}
SKILL_POS = ["QB", "RB", "WR", "TE"]
ALL_SEASONS = list(range(FOUNDED, CURRENT_SEASON + 1))

def _mgr_color(mgr: str) -> str:
    return MANAGER_COLORS.get(mgr, "#6B7280")

def _mgr_emoji(mgr: str) -> str:
    return MANAGER_EMOJI.get(mgr, "👤")

def _pos_badge(pos: str) -> str:
    c = POS_COLORS.get(pos or "Other", "#6B7280")
    return (
        f'<span style="background:{c};color:#000;font-weight:700;font-size:0.58rem;'
        f'padding:2px 5px;border-radius:3px;letter-spacing:1px;">{pos or "?"}</span>'
    )

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
dpw  = get_draft_picks_with_pos()
rec  = get_draft_records()
po   = get_player_ownership()
real = dpw[~dpw["is_keeper"]].copy()
keepers = dpw[dpw["is_keeper"]].copy()

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-page-title">Draft Center</div>
    <div class="tl-page-subtitle">
        {rec['total_picks']:,} picks &nbsp;·&nbsp;
        {rec['total_keepers']} keepers &nbsp;·&nbsp;
        {rec['total_unique_players']:,} unique players &nbsp;·&nbsp;
        25 seasons of draft decisions
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — DRAFT DNA
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE IDENTITY PROFILE", "Draft DNA"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;'
    'margin:-0.5rem 0 1.5rem;">Every manager has tells. This is 25 years of first-round evidence.</p>',
    unsafe_allow_html=True,
)

# Build per-manager round-1 breakdown (only managers with ≥4 real R1 picks)
r1 = real[(real["round"] == 1) & real["position"].notna()].copy()
r1["pos_group"] = r1["position"].apply(lambda p: p if p in SKILL_POS + ["DEF", "K"] else "Other")
r1_counts = r1.groupby(["manager", "pos_group"]).size().unstack(fill_value=0)
r1_counts["total"] = r1_counts.sum(axis=1)
r1_qual = r1_counts[r1_counts["total"] >= 4].copy()

# Add keeper rate
keeper_rate = keepers.groupby("manager").size() / dpw.groupby("manager").size()
r1_qual["keeper_rate"] = keeper_rate.reindex(r1_qual.index).fillna(0)

# Sort by RB pct descending
for col in ["RB", "WR", "QB", "TE", "DEF", "K", "Other"]:
    if col not in r1_qual.columns:
        r1_qual[col] = 0
r1_qual = r1_qual.sort_values("RB", ascending=True)

# Build stacked Plotly bar
fig_dna = go.Figure()
for pos in ["Other", "K", "DEF", "TE", "QB", "WR", "RB"]:
    if pos not in r1_qual.columns:
        continue
    pcts = (r1_qual[pos] / r1_qual["total"] * 100).round(1)
    fig_dna.add_trace(go.Bar(
        name=pos,
        y=r1_qual.index.tolist(),
        x=pcts.tolist(),
        orientation="h",
        marker_color=POS_COLORS.get(pos, "#374151"),
        text=[f"{v:.0f}%" if v >= 8 else "" for v in pcts],
        textposition="inside",
        textfont=dict(size=10, color="#0a0a0a", family="Inter"),
        hovertemplate=f"<b>%{{y}}</b><br>{pos}: %{{x:.1f}}%<extra></extra>",
    ))

fig_dna.update_layout(
    barmode="stack",
    plot_bgcolor="#081120",
    paper_bgcolor="#081120",
    font=dict(family="Inter", color="#F5F5F5", size=11),
    xaxis=dict(title="Round 1 Pick Share (%)", gridcolor="#1E2D40", range=[0, 100]),
    yaxis=dict(tickfont=dict(size=11)),
    legend=dict(orientation="h", y=1.05, x=0, font=dict(size=11)),
    margin=dict(l=120, r=30, t=40, b=40),
    height=max(320, len(r1_qual) * 28 + 80),
)
st.plotly_chart(fig_dna, use_container_width=True, config={"displayModeBar": False})

# Draft style label generator
def _draft_style(row) -> tuple[str, str]:
    total = row["total"]
    if total == 0:
        return "UNKNOWN", "#6B7280"
    rb_pct = row.get("RB", 0) / total
    wr_pct = row.get("WR", 0) / total
    qb_pct = row.get("QB", 0) / total
    te_pct = row.get("TE", 0) / total
    kr     = row.get("keeper_rate", 0)
    if rb_pct >= 0.55:
        return "RB HOARDER", "#22C55E"
    if wr_pct >= 0.45:
        return "WR COLLECTOR", "#3B82F6"
    if qb_pct >= 0.35:
        return "QB LOYALIST", "#EF4444"
    if te_pct >= 0.15:
        return "TE FIRST BELIEVER", "#F59E0B"
    if kr >= 0.08:
        return "KEEPER MAXIMIZER", "#A78BFA"
    return "BALANCED DRAFTER", "#A7B0BC"

# Manager DNA card grid
mgr_cards_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:1.5rem 0;">'
for mgr, row in r1_qual.sort_values("total", ascending=False).iterrows():
    style_label, style_color = _draft_style(row)
    emoji = _mgr_emoji(mgr)
    color = _mgr_color(mgr)
    total = int(row["total"])
    # top 2 positions
    pos_vals = {p: row.get(p, 0) for p in SKILL_POS + ["DEF", "K"]}
    top2 = sorted(pos_vals.items(), key=lambda x: x[1], reverse=True)[:2]
    pos_lines = "".join(
        f'<div style="font-size:0.65rem;color:#A7B0BC;">'
        f'{p}: <span style="color:{POS_COLORS[p]};font-weight:600;">{int(v)}/{total} '
        f'({v/total*100:.0f}%)</span></div>'
        for p, v in top2 if v > 0
    )
    mgr_cards_html += (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-top:3px solid {color};'
        f'border-radius:6px;padding:10px 14px;min-width:160px;flex:1;">'
        f'  <div style="font-size:1.4rem;">{emoji}</div>'
        f'  <div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;'
        f'color:#F5F5F5;letter-spacing:2px;margin:4px 0 2px;">{mgr}</div>'
        f'  <div style="font-size:0.58rem;color:{style_color};letter-spacing:2px;'
        f'font-family:\'Inter\',sans-serif;font-weight:700;margin-bottom:6px;">{style_label}</div>'
        f'  {pos_lines}'
        f'</div>'
    )
mgr_cards_html += "</div>"
st.markdown(mgr_cards_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — POSITION TRENDS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE LONG VIEW", "Position Trends"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'How has round-1 strategy shifted over 25 seasons? The rise of the zero-RB. The TE premium. The QB slide.</p>',
    unsafe_allow_html=True,
)

trends = get_position_trends_data()
fig_trend = go.Figure()
for pos, color, dash in [
    ("RB", "#22C55E", "solid"),
    ("WR", "#3B82F6", "solid"),
    ("QB", "#EF4444", "dot"),
    ("TE", "#F59E0B", "dash"),
]:
    if pos not in trends.columns:
        continue
    fig_trend.add_trace(go.Scatter(
        x=trends["season"], y=trends[pos], name=pos,
        mode="lines+markers",
        line=dict(color=color, width=2.5, dash=dash),
        marker=dict(size=5),
        hovertemplate=f"<b>{pos}</b> %{{y:.1f}}% in %{{x}}<extra></extra>",
    ))

fig_trend.update_layout(
    plot_bgcolor="#081120",
    paper_bgcolor="#081120",
    font=dict(family="Inter", color="#F5F5F5", size=11),
    xaxis=dict(title="Season", gridcolor="#1E2D40", dtick=2),
    yaxis=dict(title="Share of Round 1 Picks (%)", gridcolor="#1E2D40", range=[0, 90]),
    legend=dict(orientation="h", y=1.05, x=0),
    margin=dict(l=50, r=30, t=40, b=40),
    height=340,
    hovermode="x unified",
)
st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PLAYER LOYALTY
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE OBSESSIONS", "Player Loyalty"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Who did managers keep coming back to, season after season? Every colored dot is a year of ownership. '
    'Stars mark keeper seasons.</p>',
    unsafe_allow_html=True,
)

# Top players by total seasons owned (individual players, no DEF)
top_players = (
    po[po["position"] != "DEF"]
    .groupby("player_name")
    .agg(total=("total_seasons", "sum"), pos=("position", "first"),
         first=("first_season", "min"), last=("last_season", "max"))
    .sort_values("total", ascending=False)
    .head(20)
)

# Build a lookup: (player, season) -> (manager, is_keeper)
ownership_map = {}
for _, row in dpw.iterrows():
    key = (row["player_name"], int(row["season"]))
    ownership_map[key] = (row["manager"], bool(row["is_keeper"]))

# Determine visible seasons (only seasons where ANY top player was owned)
tp_set = set(top_players.index)
relevant_seasons = sorted({
    szn for (pl, szn), _ in ownership_map.items() if pl in tp_set
})

# Build HTML timeline table
tl_html = (
    '<div style="overflow-x:auto;">'
    '<table style="border-collapse:collapse;font-family:\'Inter\',sans-serif;'
    'font-size:0.65rem;width:100%;">'
    '<thead><tr>'
    '<th style="text-align:left;padding:4px 8px;color:#A7B0BC;min-width:160px;'
    'border-bottom:1px solid #1E2D40;">PLAYER</th>'
    '<th style="padding:4px 4px;color:#A7B0BC;border-bottom:1px solid #1E2D40;">POS</th>'
)
for szn in relevant_seasons:
    tl_html += (
        f'<th style="padding:2px 3px;color:#A7B0BC;border-bottom:1px solid #1E2D40;'
        f'text-align:center;min-width:28px;">\'{str(szn)[-2:]}</th>'
    )
tl_html += '<th style="padding:4px 6px;color:#A7B0BC;border-bottom:1px solid #1E2D40;">OWN</th></tr></thead><tbody>'

for i, (player, prow) in enumerate(top_players.iterrows()):
    bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
    pos = prow["pos"] or "?"
    pos_b = _pos_badge(pos)
    total = int(prow["total"])

    tl_html += (
        f'<tr style="background:{bg};">'
        f'<td style="padding:5px 8px;color:#F5F5F5;font-weight:600;white-space:nowrap;">{player}</td>'
        f'<td style="padding:5px 4px;text-align:center;">{pos_b}</td>'
    )
    for szn in relevant_seasons:
        cell_key = (player, szn)
        if cell_key in ownership_map:
            mgr, is_kp = ownership_map[cell_key]
            c = _mgr_color(mgr)
            em = _mgr_emoji(mgr)
            inner = f'⭐' if is_kp else em
            title = f"{'Keeper · ' if is_kp else ''}{mgr} · {szn}"
            tl_html += (
                f'<td style="padding:2px 3px;text-align:center;" title="{title}">'
                f'<span style="display:inline-block;width:22px;height:22px;border-radius:50%;'
                f'background:{c};font-size:0.75rem;line-height:22px;text-align:center;'
                f'{"border:2px solid #D4AF37;" if is_kp else ""}">{inner}</span>'
                f'</td>'
            )
        else:
            tl_html += '<td style="padding:2px 3px;"></td>'
    tl_html += (
        f'<td style="padding:5px 6px;text-align:center;font-weight:700;color:#D4AF37;">'
        f'{total}</td></tr>'
    )

tl_html += "</tbody></table></div>"

# Manager color legend
legend_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:1rem 0 1.5rem;">'
shown_mgrs = sorted({ownership_map[k][0] for k in ownership_map if k[0] in tp_set})
for mgr in shown_mgrs:
    c = _mgr_color(mgr)
    em = _mgr_emoji(mgr)
    legend_html += (
        f'<span style="background:{c}22;border:1px solid {c};border-radius:4px;'
        f'padding:2px 8px;font-size:0.62rem;font-family:\'Inter\',sans-serif;color:#F5F5F5;">'
        f'{em} {mgr}</span>'
    )
legend_html += "</div>"

st.markdown(legend_html + tl_html, unsafe_allow_html=True)
st.markdown(
    '<p style="font-size:0.62rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;margin-top:0.5rem;">'
    '⭐ = Keeper season &nbsp;·&nbsp; Hover a dot for details</p>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DRAFT RECORDS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE SUPERLATIVES", "Draft Records"), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

def _record_block(title: str, entries: list, label_key="player_name", val_key="count") -> str:
    rows_html = ""
    for i, e in enumerate(entries[:5]):
        name = e[0] if isinstance(e, list) else e.get(label_key, "?")
        val  = e[1] if isinstance(e, list) else e.get(val_key, 0)
        medal = ["🥇", "🥈", "🥉", "4.", "5."][i]
        rows_html += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:4px 0;border-bottom:1px solid #1E2D40;">'
            f'<span style="color:#F5F5F5;font-size:0.72rem;">{medal} {name}</span>'
            f'<span style="color:#D4AF37;font-weight:700;font-size:0.72rem;">{val}×</span>'
            f'</div>'
        )
    return (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-radius:6px;padding:14px;margin-bottom:12px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.8rem;color:#A7B0BC;'
        f'letter-spacing:3px;margin-bottom:8px;">{title}</div>'
        f'{rows_html}</div>'
    )

def _record_fact(title: str, body: str, color: str = "#D4AF37") -> str:
    return (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-radius:6px;padding:14px;margin-bottom:12px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.8rem;color:#A7B0BC;'
        f'letter-spacing:3px;margin-bottom:6px;">{title}</div>'
        f'<div style="color:{color};font-size:0.82rem;font-family:\'Inter\',sans-serif;">{body}</div>'
        f'</div>'
    )

with col1:
    st.markdown(_record_block("MOST DRAFTED PLAYERS", rec["most_drafted_players"]), unsafe_allow_html=True)
    st.markdown(_record_block("MOST KEPT PLAYERS", rec["most_kept_players"]), unsafe_allow_html=True)

with col2:
    st.markdown(_record_block("MOST MANAGERS TO OWN SAME PLAYER", rec["most_mgrs_one_player"]), unsafe_allow_html=True)
    # Earliest QB
    eq = rec["earliest_qb"][0] if rec["earliest_qb"] else {}
    st.markdown(_record_fact(
        "EARLIEST QB EVER TAKEN",
        f'{eq.get("player_name","?")} &nbsp;·&nbsp; {eq.get("season","?")} &nbsp;·&nbsp; '
        f'Pick #{eq.get("overall_pick","?")} &nbsp;·&nbsp; {eq.get("manager","?")}',
    ), unsafe_allow_html=True)
    # Earliest TE
    et = rec["earliest_te"][0] if rec["earliest_te"] else {}
    st.markdown(_record_fact(
        "EARLIEST TE EVER TAKEN",
        f'{et.get("player_name","?")} &nbsp;·&nbsp; {et.get("season","?")} &nbsp;·&nbsp; '
        f'Pick #{et.get("overall_pick","?")} &nbsp;·&nbsp; {et.get("manager","?")}',
    ), unsafe_allow_html=True)

with col3:
    # Earliest K
    ek = rec["earliest_k"][0] if rec["earliest_k"] else {}
    st.markdown(_record_fact(
        "EARLIEST KICKER EVER DRAFTED",
        f'{ek.get("player_name","?")} &nbsp;·&nbsp; {ek.get("season","?")} &nbsp;·&nbsp; '
        f'Round {ek.get("round","?")} Pick {ek.get("pick_in_round","?")} &nbsp;·&nbsp; {ek.get("manager","?")}',
        color="#F87171",
    ), unsafe_allow_html=True)
    # DEF in round 1 — the hall of shame teaser
    for ed in rec["earliest_def_r1"][:2]:
        st.markdown(_record_fact(
            "DEFENSE IN ROUND 1",
            f'{ed.get("player_name","?")} &nbsp;·&nbsp; {ed.get("season","?")} &nbsp;·&nbsp; '
            f'Pick #{ed.get("overall_pick","?")} &nbsp;·&nbsp; {ed.get("manager","?")}',
            color="#F87171",
        ), unsafe_allow_html=True)
    # Keeper position breakdown
    kp = rec["keeper_pos_breakdown"]
    total_k = sum(kp.values())
    kp_lines = " &nbsp;·&nbsp; ".join(
        f'<span style="color:{POS_COLORS.get(p,"#A7B0BC")};font-weight:600;">'
        f'{p} {v/total_k*100:.0f}%</span>'
        for p, v in sorted(kp.items(), key=lambda x: -x[1]) if p in ["RB", "WR", "QB", "TE"]
    )
    st.markdown(_record_fact("KEEPER POSITION SPLIT", kp_lines), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — HALL OF FAME & SHAME
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE VERDICT", "Draft Hall of Fame & Shame"), unsafe_allow_html=True)

hof_col, hos_col = st.columns(2)

with hof_col:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#D4AF37;'
        'letter-spacing:4px;margin-bottom:1rem;">🏛️ HALL OF FAME</div>',
        unsafe_allow_html=True,
    )
    # Most-kept players — the ones everyone wanted
    for rank, (player, count) in enumerate(rec["most_kept_players"][:5]):
        mgr_rows = po[(po["player_name"] == player) & (po["keeper_count"] > 0)]
        mgr_str = " · ".join(
            f'{_mgr_emoji(r["manager"])} {r["manager"]} ({r["keeper_count"]}×)'
            for _, r in mgr_rows.sort_values("keeper_count", ascending=False).iterrows()
        )
        pos = po[po["player_name"] == player]["position"].iloc[0] if len(po[po["player_name"] == player]) > 0 else "?"
        medal = ["🥇", "🥈", "🥉", "🏅", "🏅"][rank]
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #D4AF37;'
            f'border-radius:6px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<span style="font-size:1.3rem;">{medal}</span>'
            f'<div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F5F5;'
            f'letter-spacing:2px;">{player} {_pos_badge(pos)}</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'Kept {count}× total &nbsp;·&nbsp; {mgr_str}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )

with hos_col:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F87171;'
        'letter-spacing:4px;margin-bottom:1rem;">💀 HALL OF SHAME</div>',
        unsafe_allow_html=True,
    )
    # DEF in round 1
    for ed in rec["earliest_def_r1"]:
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #F87171;'
            f'border-radius:6px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;color:#F5F5F5;'
            f'letter-spacing:2px;">🚨 {ed["player_name"]} D/ST — Round 1</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'{ed["season"]} · Pick #{ed["overall_pick"]} · {_mgr_emoji(ed["manager"])} {ed["manager"]}'
            f' · A defense. In round one.</div></div>',
            unsafe_allow_html=True,
        )
    # Early kickers
    for ek in rec["earliest_k"][:3]:
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #F59E0B;'
            f'border-radius:6px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;color:#F5F5F5;'
            f'letter-spacing:2px;">🦶 {ek["player_name"]} — Round {ek["round"]}</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'{ek["season"]} · Pick #{ek["overall_pick"]} · {_mgr_emoji(ek["manager"])} {ek["manager"]}'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    # Most managers to draft the same player (DEF) — same D drafted by everyone
    top_shared_def = real[real["position"] == "DEF"].groupby("player_name")["manager"].nunique().sort_values(ascending=False)
    if len(top_shared_def) > 0:
        def_name = top_shared_def.index[0]
        def_mgr_count = top_shared_def.iloc[0]
        def_total = int(real[real["player_name"] == def_name].shape[0])
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #8B5CF6;'
            f'border-radius:6px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;color:#F5F5F5;'
            f'letter-spacing:2px;">🔄 {def_name} D/ST — The Cult Pick</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'Drafted {def_total}× by {def_mgr_count} different managers. '
            f'Nobody could resist.</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

render_page_footer(
    href="/keeper_hall",
    cta="EXPLORE THE KEEPER HALL",
    tagline="SOME PLAYERS WERE TOO GOOD TO LET GO.<br>THIS IS THEIR STORY.",
)
