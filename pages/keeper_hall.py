"""Keeper Hall — the players too good to let go."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data import (
    get_draft_picks_with_pos, get_keeper_chains, get_player_ownership,
    get_draft_records, MANAGER_EMOJI, MANAGER_COLORS, CURRENT_SEASON, FOUNDED,
    _KEEPER_SUSPENSION_YEARS,
)
from utils.styles import inject_css, render_nav, render_page_footer, section_header

st.set_page_config(
    page_title="Keeper Hall · The Long Game",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("keeper_hall")

POS_COLORS = {
    "RB": "#22C55E", "WR": "#3B82F6", "QB": "#EF4444",
    "TE": "#F59E0B", "DEF": "#8B5CF6", "K": "#6B7280",
}
KEEPER_SEASONS = list(range(FOUNDED, CURRENT_SEASON + 1))

def _mgr_color(mgr: str) -> str:
    return MANAGER_COLORS.get(mgr, "#6B7280")

def _mgr_emoji(mgr: str) -> str:
    return MANAGER_EMOJI.get(mgr, "👤")

def _pos_badge(pos: str) -> str:
    c = POS_COLORS.get(pos or "?", "#6B7280")
    return (
        f'<span style="background:{c};color:#000;font-weight:700;font-size:0.58rem;'
        f'padding:2px 5px;border-radius:3px;letter-spacing:1px;">{pos or "?"}</span>'
    )

# ── LOAD ──────────────────────────────────────────────────────────────────────
dpw = get_draft_picks_with_pos()
chains = get_keeper_chains()
po = get_player_ownership()
rec = get_draft_records()
keepers = dpw[dpw["is_keeper"]].copy()

total_keepers = len(keepers)
total_keeper_seasons = keepers["season"].nunique()
longest_streak = int(chains["streak_len"].max()) if len(chains) else 0
most_kept_player = keepers.groupby("player_name").size().idxmax() if len(keepers) else "—"
most_kept_count = int(keepers.groupby("player_name").size().max()) if len(keepers) else 0

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-page-title">Keeper Hall</div>
    <div class="tl-page-subtitle">
        {total_keepers} keepers &nbsp;·&nbsp;
        {total_keeper_seasons} seasons with keepers &nbsp;·&nbsp;
        {longest_streak}-season longest streak &nbsp;·&nbsp;
        the players nobody could let go
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── OVERVIEW STATS ────────────────────────────────────────────────────────────
s1, s2, s3, s4 = st.columns(4)
for col, val, lbl in [
    (s1, total_keepers, "Total Keeper Seasons"),
    (s2, keepers["player_name"].nunique(), "Unique Kept Players"),
    (s3, longest_streak, "Longest Keeper Streak"),
    (s4, most_kept_count, f"{most_kept_player} (most kept)"),
]:
    col.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{val}</div>'
        f'<div class="tl-metric-label">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — KEEPER CHAIN HALL OF FAME
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE DYNASTIES OF LOYALTY", "Longest Keeper Streaks"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Consecutive seasons keeping the same player. A ⭐ streak means a suspension-year gap was bridged.</p>',
    unsafe_allow_html=True,
)

top_chains = chains[chains["streak_len"] >= 3].head(16)

# Display in rows of 2
chain_rows = [top_chains.iloc[i:i+2] for i in range(0, len(top_chains), 2)]
for chunk in chain_rows:
    cols = st.columns(2)
    for col, (_, ch) in zip(cols, chunk.iterrows()):
        mgrs = ch["all_managers"]
        fid = ch["franchise_id"]
        seasons = ch["seasons"]
        streak_len = int(ch["streak_len"])
        player = ch["player_name"]
        primary = ch["primary_manager"]
        is_multi = ch["multi_manager"]

        pos = dpw[dpw["player_name"] == player]["position"].iloc[0] if len(dpw[dpw["player_name"] == player]) > 0 else "?"
        pos_b = _pos_badge(pos)
        color = _mgr_color(primary)

        # Check if any suspension year was bridged
        has_bridge = False
        for i in range(1, len(seasons)):
            gap = set(range(seasons[i-1]+1, seasons[i]))
            if gap and gap.issubset(_KEEPER_SUSPENSION_YEARS):
                has_bridge = True
                break

        mgr_display = f'{fid} ({" → ".join(mgrs)})' if is_multi else f'{_mgr_emoji(primary)} {primary}'
        streak_label = f'{streak_len}{"⭐" if has_bridge else ""} consecutive seasons'
        yr_pills = "".join(
            f'<span style="background:{color}22;border:1px solid {color};border-radius:4px;'
            f'padding:1px 6px;font-size:0.62rem;font-family:\'Inter\',sans-serif;color:#F5F5F5;'
            f'margin:1px;">{s}</span>'
            for s in seasons
        )

        col.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid {color};'
            f'border-radius:6px;padding:14px;margin-bottom:10px;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
            f'<div style="font-size:1.8rem;font-family:\'Bebas Neue\',sans-serif;color:{color};'
            f'line-height:1;">{streak_len}</div>'
            f'<div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F5F5;'
            f'letter-spacing:2px;">{player} {pos_b}</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;">{mgr_display}</div>'
            f'</div></div>'
            f'<div style="font-size:0.6rem;color:#A7B0BC;margin-bottom:5px;">{streak_label}</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:2px;">{yr_pills}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — PLAYER KEEPER TIMELINE
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE MOST COVETED", "Player Keeper Timelines"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Top kept players across all seasons. Each colored dot shows which franchise held the keeper rights.</p>',
    unsafe_allow_html=True,
)

# Top kept players (individual, no DEF)
top_kept = (
    keepers[keepers["position"] != "DEF"]
    .groupby("player_name").size()
    .sort_values(ascending=False)
    .head(18)
)

# Keeper seasons that exist
active_keeper_szns = sorted(keepers["season"].unique().astype(int).tolist())

# Build (player, season) -> (manager, franchise_id) lookup for keepers only
keeper_map: dict[tuple, tuple] = {}
for _, row in keepers.iterrows():
    keeper_map[(row["player_name"], int(row["season"]))] = (row["manager"], row["franchise_id"])

# HTML timeline table
tl_html = (
    '<div style="overflow-x:auto;">'
    '<table style="border-collapse:collapse;font-family:\'Inter\',sans-serif;font-size:0.65rem;width:100%;">'
    '<thead><tr>'
    '<th style="text-align:left;padding:4px 8px;color:#A7B0BC;min-width:160px;border-bottom:1px solid #1E2D40;">PLAYER</th>'
    '<th style="padding:4px 4px;color:#A7B0BC;border-bottom:1px solid #1E2D40;">POS</th>'
)
for szn in active_keeper_szns:
    susp = szn in _KEEPER_SUSPENSION_YEARS
    color = "#4B5563" if susp else "#A7B0BC"
    label = "—" if susp else f"'{str(szn)[-2:]}"
    tl_html += (
        f'<th style="padding:2px 3px;color:{color};border-bottom:1px solid #1E2D40;'
        f'text-align:center;min-width:26px;" title="{"Keepers suspended" if susp else szn}">'
        f'{label}</th>'
    )
tl_html += '<th style="padding:4px 6px;color:#A7B0BC;border-bottom:1px solid #1E2D40;">TOTAL</th></tr></thead><tbody>'

for i, (player, count) in enumerate(top_kept.items()):
    bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
    pos_val = keepers[keepers["player_name"] == player]["position"].iloc[0] if len(keepers[keepers["player_name"] == player]) > 0 else "?"
    pos_b = _pos_badge(pos_val)

    tl_html += (
        f'<tr style="background:{bg};">'
        f'<td style="padding:5px 8px;color:#F5F5F5;font-weight:600;white-space:nowrap;">{player}</td>'
        f'<td style="padding:5px 4px;text-align:center;">{pos_b}</td>'
    )
    for szn in active_keeper_szns:
        if szn in _KEEPER_SUSPENSION_YEARS:
            tl_html += '<td style="padding:2px 3px;background:#0A1520;"></td>'
            continue
        cell_key = (player, szn)
        if cell_key in keeper_map:
            mgr, fid = keeper_map[cell_key]
            c = _mgr_color(mgr)
            em = _mgr_emoji(mgr)
            tl_html += (
                f'<td style="padding:2px 3px;text-align:center;" title="{mgr} · {szn}">'
                f'<span style="display:inline-block;width:22px;height:22px;border-radius:50%;'
                f'background:{c};font-size:0.75rem;line-height:22px;text-align:center;">'
                f'{em}</span></td>'
            )
        else:
            tl_html += '<td style="padding:2px 3px;"></td>'
    tl_html += (
        f'<td style="padding:5px 6px;text-align:center;font-weight:700;color:#D4AF37;">'
        f'{int(count)}</td></tr>'
    )
tl_html += "</tbody></table></div>"

# Manager color legend (only managers who appear as keepers)
shown_keeper_mgrs = sorted(keepers[keepers["player_name"].isin(top_kept.index)]["manager"].unique())
legend_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:1rem 0 1.5rem;">'
for mgr in shown_keeper_mgrs:
    c = _mgr_color(mgr)
    em = _mgr_emoji(mgr)
    legend_html += (
        f'<span style="background:{c}22;border:1px solid {c};border-radius:4px;'
        f'padding:2px 8px;font-size:0.62rem;font-family:\'Inter\',sans-serif;color:#F5F5F5;">'
        f'{em} {mgr}</span>'
    )
legend_html += '</div><p style="font-size:0.62rem;color:#4B5563;font-family:\'Inter\',sans-serif;">— = Keeper format suspended</p>'

st.markdown(legend_html + tl_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — KEEPER POSITION ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("WHAT THEY HOARDED", "Keeper Position Analysis"), unsafe_allow_html=True)

pos_col, mgr_col = st.columns([1, 2])

with pos_col:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.8rem;color:#A7B0BC;'
        'letter-spacing:3px;margin-bottom:0.75rem;">LEAGUE-WIDE KEEPER POSITIONS</div>',
        unsafe_allow_html=True,
    )
    kp = rec["keeper_pos_breakdown"]
    total_k = sum(kp.values())
    for pos, count in sorted(kp.items(), key=lambda x: -x[1]):
        if pos not in POS_COLORS:
            continue
        pct = count / total_k * 100
        bar_color = POS_COLORS.get(pos, "#6B7280")
        st.markdown(
            f'<div style="margin-bottom:8px;">'
            f'<div style="display:flex;justify-content:space-between;font-family:\'Inter\',sans-serif;'
            f'font-size:0.72rem;color:#F5F5F5;margin-bottom:3px;">'
            f'<span>{pos}</span><span style="color:{bar_color};">{pct:.1f}% ({count})</span></div>'
            f'<div style="background:#1E2D40;border-radius:4px;height:6px;">'
            f'<div style="width:{pct}%;background:{bar_color};height:6px;border-radius:4px;"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

with mgr_col:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.8rem;color:#A7B0BC;'
        'letter-spacing:3px;margin-bottom:0.75rem;">KEEPER PROFILE BY MANAGER</div>',
        unsafe_allow_html=True,
    )
    # Per-manager keeper position breakdown (managers with ≥3 keepers)
    mgr_keeper_pos = (
        keepers[keepers["position"].isin(POS_COLORS.keys())]
        .groupby(["manager", "position"]).size()
        .unstack(fill_value=0)
    )
    mgr_keeper_pos["total"] = mgr_keeper_pos.sum(axis=1)
    mgr_keeper_pos = mgr_keeper_pos[mgr_keeper_pos["total"] >= 3]

    fig_kp = go.Figure()
    mgr_keeper_pos_sorted = mgr_keeper_pos.sort_values("RB" if "RB" in mgr_keeper_pos.columns else "total", ascending=True)
    for pos in ["K", "DEF", "TE", "QB", "WR", "RB"]:
        if pos not in mgr_keeper_pos_sorted.columns:
            continue
        pcts = (mgr_keeper_pos_sorted[pos] / mgr_keeper_pos_sorted["total"] * 100).round(1)
        fig_kp.add_trace(go.Bar(
            name=pos, y=mgr_keeper_pos_sorted.index.tolist(), x=pcts.tolist(),
            orientation="h", marker_color=POS_COLORS[pos],
            text=[f"{v:.0f}%" if v >= 10 else "" for v in pcts],
            textposition="inside",
            textfont=dict(size=9, color="#0a0a0a"),
            hovertemplate=f"<b>%{{y}}</b><br>{pos}: %{{x:.1f}}%<extra></extra>",
        ))

    fig_kp.update_layout(
        barmode="stack",
        plot_bgcolor="#081120", paper_bgcolor="#081120",
        font=dict(family="Inter", color="#F5F5F5", size=10),
        xaxis=dict(title="Keeper Share (%)", gridcolor="#1E2D40", range=[0, 100]),
        yaxis=dict(tickfont=dict(size=10)),
        legend=dict(orientation="h", y=1.05, x=0, font=dict(size=10)),
        margin=dict(l=100, r=20, t=30, b=30),
        height=max(260, len(mgr_keeper_pos_sorted) * 26 + 70),
    )
    st.plotly_chart(fig_kp, use_container_width=True, config={"displayModeBar": False})

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — MANAGER KEEPER PROFILES
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE KEEPERS OF KEEPERS", "Manager Keeper Profiles"), unsafe_allow_html=True)

# Per-manager: total keepers, most kept player, keeper rate
mgr_k_stats = []
for mgr, kgrp in keepers.groupby("manager"):
    total_mgr_picks = len(dpw[dpw["manager"] == mgr])
    k_count = len(kgrp)
    k_rate = k_count / total_mgr_picks if total_mgr_picks > 0 else 0
    indiv = kgrp[kgrp["position"] != "DEF"]
    fav_k = indiv["player_name"].value_counts().index[0] if len(indiv) > 0 else "—"
    fav_k_n = int(indiv["player_name"].value_counts().iloc[0]) if len(indiv) > 0 else 0
    fav_pos = kgrp[kgrp["position"].isin(POS_COLORS.keys())]["position"].value_counts()
    top_pos = fav_pos.index[0] if len(fav_pos) > 0 else "?"
    mgr_k_stats.append({
        "manager": mgr, "k_count": k_count, "k_rate": k_rate,
        "fav_k": fav_k, "fav_k_n": fav_k_n, "top_pos": top_pos,
    })

mgr_k_stats = sorted(mgr_k_stats, key=lambda x: -x["k_count"])

cards_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:0.5rem;">'
for stat in mgr_k_stats:
    mgr = stat["manager"]
    color = _mgr_color(mgr)
    em = _mgr_emoji(mgr)
    pos_c = POS_COLORS.get(stat["top_pos"], "#6B7280")
    cards_html += (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-top:3px solid {color};'
        f'border-radius:6px;padding:10px 14px;min-width:155px;flex:1;">'
        f'<div style="font-size:1.3rem;">{em}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.9rem;color:#F5F5F5;'
        f'letter-spacing:2px;margin:4px 0 2px;">{mgr}</div>'
        f'<div style="font-size:0.65rem;color:#A7B0BC;margin-bottom:4px;">'
        f'{stat["k_count"]} keepers · {stat["k_rate"]*100:.1f}% rate</div>'
        f'<div style="font-size:0.62rem;color:#A7B0BC;">'
        f'Fav kept: <span style="color:#F5F5F5;">{stat["fav_k"]}'
        f'{(" ×" + str(stat["fav_k_n"])) if stat["fav_k_n"] > 1 else ""}</span></div>'
        f'<div style="font-size:0.62rem;color:#A7B0BC;">Top pos: '
        f'<span style="color:{pos_c};font-weight:600;">{stat["top_pos"]}</span></div>'
        f'</div>'
    )
cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

render_page_footer(
    href="/draft_center",
    cta="BACK TO THE DRAFT CENTER",
    tagline="THE KEEPERS WERE COVETED.<br>THE DRAFT IS WHERE IT STARTED.",
)
