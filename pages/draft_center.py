"""Draft Center — 25 years of picks, patterns, and obsessions."""
from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data import (
    get_draft_picks_with_pos, get_position_trends_data,
    get_draft_records, get_player_ownership, get_manager_stats,
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

def _mgr_color(mgr):
    return MANAGER_COLORS.get(mgr, "#6B7280")

def _mgr_emoji(mgr):
    return MANAGER_EMOJI.get(mgr, "👤")

def _pos_badge(pos):
    c = POS_COLORS.get(pos or "Other", "#6B7280")
    return (
        f'<span style="background:{c};color:#000;font-weight:700;font-size:0.58rem;'
        f'padding:2px 5px;border-radius:3px;letter-spacing:1px;">{pos or "?"}</span>'
    )

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
dpw      = get_draft_picks_with_pos()
rec      = get_draft_records()
po       = get_player_ownership()
ms       = get_manager_stats()
real     = dpw[~dpw["is_keeper"]].copy()
keepers  = dpw[dpw["is_keeper"]].copy()
r1_real  = real[real["round"] == 1].copy()
ms_idx   = ms.set_index("canonical_name")

# Player-level aggregates (skill positions only, real drafts)
_skill_po = po[po["position"].isin(SKILL_POS)].copy()
player_legend = (
    _skill_po.groupby("player_name")
    .agg(
        total_drafts=("draft_count", "sum"),
        unique_managers=("manager", "nunique"),
        first_season=("first_season", "min"),
        last_season=("last_season", "max"),
        position=("position", "first"),
    )
    .reset_index()
)
# Count distinct seasons actually drafted — avoids inflating spans for common names
# that span multiple NFL players (e.g. "Mike Williams" = Detroit 2005, TB 2010-13, LAC 2017-24)
_seasons_per_player = dpw.groupby("player_name")["season"].nunique()
player_legend["career_span"] = player_legend["player_name"].map(_seasons_per_player).fillna(0).astype(int)

# Most loyal manager per player (most total seasons with this player)
_loyal = (
    _skill_po.sort_values("total_seasons", ascending=False)
    .drop_duplicates("player_name")[["player_name", "manager"]]
    .set_index("player_name")["manager"]
    .to_dict()
)
player_legend["most_loyal"] = player_legend["player_name"].map(_loyal)

# Per-player total league ownership (proxy for player quality)
player_seasons_total = po.groupby("player_name")["total_seasons"].sum().to_dict()

# Best R1 pick per manager: their R1 skill-position pick with most total league ownership
_r1_skill = r1_real[r1_real["position"].isin(SKILL_POS)]
best_r1_map = {}
for _mgr, _grp in _r1_skill.groupby("manager"):
    _players = _grp["player_name"].unique()
    if len(_players) > 0:
        best_r1_map[_mgr] = max(_players, key=lambda p: player_seasons_total.get(p, 0))

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-page-title">Draft Center</div>
    <div class="tl-page-subtitle">
        {rec['total_picks']:,} picks &nbsp;·&nbsp;
        {rec['total_keepers']} keepers &nbsp;·&nbsp;
        {rec['total_unique_players']:,} unique players &nbsp;·&nbsp;
        25 seasons of draft decisions, obsessions, and mistakes
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

s1, s2, s3, s4 = st.columns(4)
for col, val, lbl in [
    (s1, rec["total_picks"], "Total Draft Picks"),
    (s2, rec["total_unique_players"], "Unique Players Drafted"),
    (s3, int(r1_real["player_name"].nunique()), "Players Ever Taken Round 1"),
    (s4, int(player_legend["career_span"].max()), "Longest Player Career (seasons)"),
]:
    col.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{val:,}</div>'
        f'<div class="tl-metric-label">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — THE ONES THEY COULDN'T QUIT
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE ONES THEY COULDN'T QUIT", "The League's Most Coveted Players"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Some players became league institutions — not because they were always good, but because nobody could stop drafting them.</p>',
    unsafe_allow_html=True,
)

_pos_adj = {"QB": "quarterback", "RB": "running back", "WR": "receiver", "TE": "tight end"}

def _cant_quit_story(name, drafts, managers, career, first_s, last_s, loyal_mgr, pos):
    pa = _pos_adj.get(pos, "player")
    if career >= 18:
        line1 = f"A {career}-year presence in this league — from {first_s} to {last_s}."
    elif career >= 12:
        line1 = f"Appearing from {first_s} to {last_s}. {career} seasons of relevance."
    else:
        line1 = f"A {career}-season run, from {first_s} to {last_s}."
    if drafts >= 16:
        line2 = f"Drafted {drafts} times. Nobody could leave this {pa} on the board."
    elif drafts >= 12:
        line2 = f"Drafted {drafts} times. The obsession was league-wide."
    else:
        line2 = f"Drafted {drafts} times across the league."
    if managers >= 10:
        line3 = f"Touched {managers} different rosters — nearly every manager in league history."
    elif managers >= 7:
        line3 = f"{managers} different managers couldn't resist."
    else:
        line3 = f"Owned by {managers} managers."
    loyal_str = f" {loyal_mgr} was the most devoted." if loyal_mgr else ""
    return f"{line1} {line2} {line3}{loyal_str}"

top_legends = player_legend.sort_values("total_drafts", ascending=False).head(8)

cant_quit_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:0;">'
for _, row in top_legends.iterrows():
    story = _cant_quit_story(
        row["player_name"], row["total_drafts"], row["unique_managers"],
        row["career_span"], row["first_season"], row["last_season"],
        row["most_loyal"], row["position"]
    )
    pos = str(row["position"]) if row["position"] else "?"
    pb = _pos_badge(pos)
    pc = POS_COLORS.get(pos, "#6B7280")

    # Manager dots: which managers drafted this player?
    mgr_drafters = po[(po["player_name"] == row["player_name"]) & (po["draft_count"] > 0)]
    mgr_dots = ""
    for _, md_row in mgr_drafters.iterrows():
        _md_mgr = md_row["manager"]
        _md_cnt = md_row["draft_count"]
        _md_clr = _mgr_color(_md_mgr)
        _md_emj = _mgr_emoji(_md_mgr)
        mgr_dots += (
            f'<span title="{_md_mgr} ({_md_cnt}×)" '
            f'style="display:inline-block;width:16px;height:16px;border-radius:50%;'
            f'background:{_md_clr};font-size:0.55rem;line-height:16px;'
            f'text-align:center;margin:1px;">{_md_emj}</span>'
        )

    cant_quit_html += (
        f'<div style="background:#0F1B2D;border:1px solid {pc}33;border-left:4px solid {pc};'
        f'border-radius:6px;padding:16px 18px;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#F5F5F5;'
        f'letter-spacing:3px;">{row["player_name"]}</div>'
        f'{pb}</div>'
        f'<div style="display:flex;gap:16px;margin-bottom:8px;flex-wrap:wrap;">'
        f'<span style="font-size:0.68rem;font-weight:700;color:{pc};">{row["total_drafts"]} drafts</span>'
        f'<span style="font-size:0.68rem;color:#A7B0BC;">{row["unique_managers"]} managers</span>'
        f'<span style="font-size:0.68rem;color:#A7B0BC;">{row["career_span"]}-season run</span>'
        f'</div>'
        f'<div style="font-size:0.68rem;color:#A7B0BC;line-height:1.5;margin-bottom:10px;">{story}</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:2px;">{mgr_dots}</div>'
        f'</div>'
    )
cant_quit_html += '</div>'
st.markdown(cant_quit_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — PLAYER LOYALTY
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE OBSESSIONS", "Player Loyalty"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1rem;">'
    'Who did managers keep coming back to, season after season? Every dot is a year of ownership. ⭐ = keeper season.</p>',
    unsafe_allow_html=True,
)

# Position filter
_pos_opts = ["All Players", "QB", "RB", "WR", "TE", "K", "DEF", "Keepers Only"]
_filt = st.selectbox("Filter by position", _pos_opts, index=0,
                     label_visibility="collapsed", key="loyalty_pos_filter")

# Build ownership map
ownership_map = {}
for _, _row in dpw.iterrows():
    ownership_map[(_row["player_name"], int(_row["season"]))] = (
        _row["manager"], bool(_row["is_keeper"]), str(_row["position"]) if _row["position"] else "?"
    )

# Filter players
if _filt == "All Players":
    _po_filt = po[po["position"] != "DEF"]
elif _filt == "Keepers Only":
    _po_filt = po[(po["keeper_count"] > 0) & (po["position"] != "DEF")]
else:
    _po_filt = po[po["position"] == _filt]

top_players = (
    _po_filt.groupby("player_name")
    .agg(total=("total_seasons", "sum"), pos=("position", "first"),
         first=("first_season", "min"), last=("last_season", "max"))
    .sort_values("total", ascending=False)
    .head(25)
)

tp_set = set(top_players.index)
relevant_seasons = sorted({szn for (pl, szn), _ in ownership_map.items() if pl in tp_set})

tl_html = (
    '<div style="overflow-x:auto;">'
    '<table style="border-collapse:collapse;font-family:\'Inter\',sans-serif;font-size:0.65rem;width:100%;">'
    '<thead><tr>'
    '<th style="text-align:left;padding:4px 8px;color:#A7B0BC;min-width:160px;border-bottom:1px solid #1E2D40;">PLAYER</th>'
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
    total = int(prow["total"])
    pb = _pos_badge(pos)
    tl_html += (
        f'<tr style="background:{bg};">'
        f'<td style="padding:5px 8px;color:#F5F5F5;font-weight:600;white-space:nowrap;">{player}</td>'
        f'<td style="padding:5px 4px;text-align:center;">{pb}</td>'
    )
    for szn in relevant_seasons:
        cell_key = (player, szn)
        if cell_key in ownership_map:
            mgr, is_kp, _ = ownership_map[cell_key]
            c = _mgr_color(mgr)
            em = _mgr_emoji(mgr)
            inner = "⭐" if is_kp else em
            title_attr = f"{'Keeper · ' if is_kp else ''}{mgr} · {szn}"
            tl_html += (
                f'<td style="padding:2px 3px;text-align:center;" title="{title_attr}">'
                f'<span style="display:inline-block;width:22px;height:22px;border-radius:50%;'
                f'background:{c};font-size:0.75rem;line-height:22px;text-align:center;'
                f'{"border:2px solid #D4AF37;" if is_kp else ""}">{inner}</span></td>'
            )
        else:
            tl_html += '<td style="padding:2px 3px;"></td>'
    tl_html += (
        f'<td style="padding:5px 6px;text-align:center;font-weight:700;color:#D4AF37;">'
        f'{total}</td></tr>'
    )

tl_html += '</tbody></table></div>'

shown_mgrs = sorted({ownership_map[k][0] for k in ownership_map if k[0] in tp_set})
legend_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:1rem 0 1rem;">'
for mgr in shown_mgrs:
    c = _mgr_color(mgr)
    em = _mgr_emoji(mgr)
    legend_html += (
        f'<span style="background:{c}22;border:1px solid {c};border-radius:4px;'
        f'padding:2px 8px;font-size:0.62rem;font-family:\'Inter\',sans-serif;color:#F5F5F5;">'
        f'{em} {mgr}</span>'
    )
legend_html += '</div>'

st.markdown(legend_html + tl_html, unsafe_allow_html=True)
st.markdown(
    '<p style="font-size:0.62rem;color:#6B7280;font-family:\'Inter\',sans-serif;margin-top:0.5rem;">'
    '⭐ = Keeper season &nbsp;·&nbsp; Hover a dot for manager + year</p>',
    unsafe_allow_html=True,
)

# Player profile expanders
st.markdown(
    '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
    'letter-spacing:3px;margin:1.5rem 0 0.75rem;">PLAYER PROFILES — EXPAND ANY PLAYER</div>',
    unsafe_allow_html=True,
)

_profile_players = list(top_players.index[:15])
_exp_cols = st.columns(3)
for _idx, _player in enumerate(_profile_players):
    _col = _exp_cols[_idx % 3]
    with _col:
        _player_po = po[po["player_name"] == _player].copy()
        _pos_val = str(_player_po["position"].iloc[0]) if len(_player_po) > 0 and _player_po["position"].notna().any() else "?"
        _total_d = int(_player_po["draft_count"].sum())
        _total_k = int(_player_po["keeper_count"].sum())
        _total_s = int(_player_po["total_seasons"].sum())
        _unique_m = _player_po["manager"].nunique()
        _first_s = int(_player_po["first_season"].min())
        _last_s = int(_player_po["last_season"].max())

        with st.expander(f"{_player} — {_total_s} seasons"):
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:12px;">'
                f'<div style="background:#081120;border-radius:4px;padding:8px;text-align:center;">'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;color:#D4AF37;">{_total_d}</div>'
                f'<div style="font-size:0.55rem;color:#A7B0BC;">DRAFTS</div></div>'
                f'<div style="background:#081120;border-radius:4px;padding:8px;text-align:center;">'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;color:#D4AF37;">{_total_k}</div>'
                f'<div style="font-size:0.55rem;color:#A7B0BC;">KEEPERS</div></div>'
                f'<div style="background:#081120;border-radius:4px;padding:8px;text-align:center;">'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;color:#D4AF37;">{_unique_m}</div>'
                f'<div style="font-size:0.55rem;color:#A7B0BC;">MANAGERS</div></div>'
                f'</div>'
                f'<div style="font-size:0.62rem;color:#A7B0BC;margin-bottom:10px;">'
                f'First appeared: {_first_s} &nbsp;·&nbsp; Last appeared: {_last_s}</div>',
                unsafe_allow_html=True,
            )

            _sorted_po = _player_po.sort_values("total_seasons", ascending=False)
            for _, _pr in _sorted_po.iterrows():
                _c = _mgr_color(_pr["manager"])
                _em = _mgr_emoji(_pr["manager"])
                _d_count = int(_pr["draft_count"])
                _k_count = int(_pr["keeper_count"])
                _yrs = sorted([int(y) for y in _pr["seasons"]])
                _yr_str = " · ".join(str(y) for y in _yrs)
                _detail = []
                if _d_count:
                    _detail.append(f"Drafted {_d_count}×")
                if _k_count:
                    _detail.append(f"Kept {_k_count}×")
                st.markdown(
                    f'<div style="background:#081120;border-left:3px solid {_c};'
                    f'border-radius:4px;padding:6px 10px;margin-bottom:5px;">'
                    f'<div style="font-size:0.68rem;color:#F5F5F5;font-weight:600;">'
                    f'{_em} {_pr["manager"]} — {" · ".join(_detail)}</div>'
                    f'<div style="font-size:0.58rem;color:#6B7280;margin-top:2px;">{_yr_str}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — DRAFT DNA
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE IDENTITY PROFILE", "Draft DNA"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Every manager has tells. This is 25 years of first-round evidence — who they were, '
    'what they valued, and whether it worked.</p>',
    unsafe_allow_html=True,
)

# Build per-manager round-1 breakdown (managers with ≥4 real R1 picks)
r1_q = real[(real["round"] == 1) & real["position"].notna()].copy()
r1_q["pos_group"] = r1_q["position"].apply(lambda p: p if p in SKILL_POS + ["DEF", "K"] else "Other")
r1_counts = r1_q.groupby(["manager", "pos_group"]).size().unstack(fill_value=0)
r1_counts["total"] = r1_counts.sum(axis=1)
r1_qual = r1_counts[r1_counts["total"] >= 4].copy()

for col in ["RB", "WR", "QB", "TE", "DEF", "K", "Other"]:
    if col not in r1_qual.columns:
        r1_qual[col] = 0

# Add keeper rate, success metrics
keeper_rate = keepers.groupby("manager").size() / dpw.groupby("manager").size()
r1_qual["keeper_rate"] = keeper_rate.reindex(r1_qual.index).fillna(0)
r1_qual["champs"] = [int(ms_idx.loc[m, "championships"]) if m in ms_idx.index else 0 for m in r1_qual.index]
_seasons_p = [int(ms_idx.loc[m, "seasons_played"]) if m in ms_idx.index else 1 for m in r1_qual.index]
_playoff_a = [int(ms_idx.loc[m, "playoff_apps"]) if m in ms_idx.index else 0 for m in r1_qual.index]
r1_qual["playoff_rate"] = [pa / max(sp, 1) for pa, sp in zip(_playoff_a, _seasons_p)]

r1_qual = r1_qual.sort_values("RB", ascending=True)

# Stacked bar chart
fig_dna = go.Figure()
for pos in ["Other", "K", "DEF", "TE", "QB", "WR", "RB"]:
    if pos not in r1_qual.columns:
        continue
    pcts = (r1_qual[pos] / r1_qual["total"] * 100).round(1)
    fig_dna.add_trace(go.Bar(
        name=pos, y=r1_qual.index.tolist(), x=pcts.tolist(),
        orientation="h", marker_color=POS_COLORS.get(pos, "#374151"),
        text=[f"{v:.0f}%" if v >= 8 else "" for v in pcts],
        textposition="inside",
        textfont=dict(size=10, color="#0a0a0a", family="Inter"),
        hovertemplate=f"<b>%{{y}}</b><br>{pos}: %{{x:.1f}}%<extra></extra>",
    ))

fig_dna.update_layout(
    barmode="stack",
    plot_bgcolor="#081120", paper_bgcolor="#081120",
    font=dict(family="Inter", color="#F5F5F5", size=11),
    xaxis=dict(title="Round 1 Pick Share (%)", gridcolor="#1E2D40", range=[0, 100]),
    yaxis=dict(tickfont=dict(size=11)),
    legend=dict(orientation="h", y=1.05, x=1, xanchor="right", font=dict(size=11)),
    margin=dict(l=120, r=30, t=40, b=40),
    height=max(320, len(r1_qual) * 28 + 80),
)
st.plotly_chart(fig_dna, use_container_width=True, config={"displayModeBar": False})

# Archetype function — expanded personality labels
def _archetype(row):
    total = row["total"]
    if total == 0:
        return "UNKNOWN", "#6B7280", "Not enough drafts to profile."
    rb = row.get("RB", 0) / total
    wr = row.get("WR", 0) / total
    qb = row.get("QB", 0) / total
    te = row.get("TE", 0) / total
    def_ = row.get("DEF", 0) / total
    kr = row.get("keeper_rate", 0)
    champs = row.get("champs", 0)

    if rb >= 0.65:
        return "HERO-RB PIONEER", "#22C55E", "The bell cow was the answer. Every single year."
    if rb >= 0.50:
        return "RB HOARDER", "#22C55E", "Staked the first round on running backs."
    if wr >= 0.55:
        return "RECEIVER KINGDOM", "#3B82F6", "Receivers win leagues. They built for it."
    if wr >= 0.40 and rb <= 0.20:
        return "ZERO-RB PIONEER", "#60A5FA", "Avoided RBs in round one long before it had a name."
    if qb >= 0.35:
        return "QB LOYALIST", "#EF4444", "Quarterbacks win leagues. They drafted accordingly."
    if qb >= 0.22:
        return "QUARTERBACK WHISPERER", "#F87171", "Always had a QB solution before everyone else."
    if te >= 0.22:
        return "TE ADDICT", "#F59E0B", "Saw the tight end premium before the market caught on."
    if te >= 0.13:
        return "TE FIRST BELIEVER", "#FCD34D", "Would reach for a tight end when the value was right."
    if kr >= 0.10 and champs >= 2:
        return "CHAMPIONSHIP BUILDER", "#D4AF37", "Built to keep. Kept to win. Won."
    if kr >= 0.09:
        return "KEEPER ARCHITECT", "#A78BFA", "Played the long game. Draft to keep, keep to win."
    if def_ >= 0.15:
        return "OLD-SCHOOL DRAFTER", "#9CA3AF", "Defenses were part of the strategy. Old school."
    return "BALANCED ARCHITECT", "#A7B0BC", "No tells. Adapted to the board every single year."

# Enhanced DNA cards
dna_cards_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin:1.5rem 0;">'
for mgr, row in r1_qual.sort_values("total", ascending=False).iterrows():
    label, lcolor, desc = _archetype(row)
    emoji = _mgr_emoji(mgr)
    color = _mgr_color(mgr)
    total = int(row["total"])
    champs = int(row.get("champs", 0))
    pl_rate = float(row.get("playoff_rate", 0))
    best_r1 = best_r1_map.get(mgr, "—")
    champ_str = ("🏆 " * champs).strip() if champs > 0 else ""
    top_pos = max(["RB","WR","QB","TE","DEF","K"], key=lambda p: row.get(p, 0))
    top_pct = int(row.get(top_pos, 0) / total * 100) if total > 0 else 0

    dna_cards_html += (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-top:3px solid {color};'
        f'border-radius:6px;padding:12px 14px;min-width:175px;flex:1;">'
        f'<div style="font-size:1.5rem;">{emoji}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F5F5;'
        f'letter-spacing:2px;margin:4px 0 2px;">{mgr} {champ_str}</div>'
        f'<div style="background:{lcolor}22;border-radius:3px;padding:2px 6px;display:inline-block;'
        f'font-family:\'Bebas Neue\',sans-serif;font-size:0.62rem;color:{lcolor};'
        f'letter-spacing:2px;margin-bottom:5px;">{label}</div>'
        f'<div style="font-size:0.6rem;color:#6B7280;margin-bottom:8px;line-height:1.4;">{desc}</div>'
        f'<div style="border-top:1px solid #1E2D40;padding-top:7px;">'
        f'<div style="font-size:0.62rem;color:#A7B0BC;">Playoff rate: '
        f'<span style="color:#F5F5F5;font-weight:600;">{pl_rate*100:.0f}%</span></div>'
        f'<div style="font-size:0.62rem;color:#A7B0BC;">Top R1 pos: '
        f'<span style="color:{POS_COLORS.get(top_pos,"#A7B0BC")};font-weight:600;">{top_pos} {top_pct}%</span></div>'
        f'<div style="font-size:0.62rem;color:#A7B0BC;">Best R1 find: '
        f'<span style="color:#F5F5F5;">{best_r1}</span></div>'
        f'</div></div>'
    )
dna_cards_html += '</div>'
st.markdown(dna_cards_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — THE LONG VIEW + ERA STORY CARDS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE LONG VIEW", "Position Trends"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'How has round-1 strategy shifted? The rise of the zero-RB. The TE premium. The QB golden age.</p>',
    unsafe_allow_html=True,
)

trends = get_position_trends_data()
fig_trend = go.Figure()
for pos, tcolor, dash in [
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
        line=dict(color=tcolor, width=2.5, dash=dash),
        marker=dict(size=5),
        hovertemplate=f"<b>{pos}</b> %{{y:.1f}}% in %{{x}}<extra></extra>",
    ))

fig_trend.update_layout(
    plot_bgcolor="#081120", paper_bgcolor="#081120",
    font=dict(family="Inter", color="#F5F5F5", size=11),
    xaxis=dict(title="Season", gridcolor="#1E2D40", dtick=2),
    yaxis=dict(title="Share of Round 1 (%)", gridcolor="#1E2D40", range=[0, 90]),
    legend=dict(orientation="h", y=1.05, x=0),
    margin=dict(l=50, r=30, t=40, b=40),
    height=320,
    hovermode="x unified",
)
st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

# Era story cards
_eras = [
    (2001, 2008, "THE QB GOLD RUSH", "#EF4444",
     "Peyton Manning and Brett Favre set the market. QBs went #1 overall in '02, '03, '07. "
     "Elite quarterbacks were the first-round prize before the RB backlash took over."),
    (2009, 2015, "THE RB DOMINANCE ERA", "#22C55E",
     "Ray Rice. Marshawn Lynch. Adrian Peterson. DeMarco Murray. "
     "Running backs took over the first round. The handcuff era. The bell cow era. "
     "RBs averaged over 50% of round-1 selections throughout this stretch."),
    (2016, 2025, "THE WR RENAISSANCE", "#3B82F6",
     "Antonio Brown. Davante Adams. Tyreek Hill. Justin Jefferson. "
     "Receivers began claiming round-1 territory as the NFL went pass-happy. "
     "Zero-RB wasn't just a Twitter strategy — it was league history in the making."),
]
era_c1, era_c2, era_c3 = st.columns(3)
for ecol, (e_start, e_end, e_name, e_color, e_story) in zip([era_c1, era_c2, era_c3], _eras):
    era_data = trends[trends["season"].between(e_start, e_end)]
    if len(era_data) > 0:
        pos_avgs = {p: float(era_data[p].mean()) for p in ["QB","RB","WR","TE"] if p in era_data.columns}
        dom_pos = max(pos_avgs, key=pos_avgs.get) if pos_avgs else "?"
        dom_avg = pos_avgs.get(dom_pos, 0)
        stat_line = f"{dom_pos} avg {dom_avg:.0f}% of R1"
    else:
        stat_line = ""
    ecol.markdown(
        f'<div style="background:#081120;border-left:4px solid {e_color};'
        f'border-radius:5px;padding:14px;height:100%;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:{e_color};'
        f'letter-spacing:3px;">{e_name}</div>'
        f'<div style="font-size:0.62rem;color:#6B7280;margin:2px 0 8px;">{e_start}–{e_end}'
        f'{" · " + stat_line if stat_line else ""}</div>'
        f'<div style="font-size:0.65rem;color:#A7B0BC;line-height:1.5;">{e_story}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — FIRST ROUND HISTORY
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("FIRST ROUND LEGENDS", "Round 1 History"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'The most selected first-round players. The most taken #1 overall picks. '
    'The full history of who the league bet on.</p>',
    unsafe_allow_html=True,
)

r1_left, r1_right = st.columns([3, 2])

with r1_left:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
        'letter-spacing:3px;margin-bottom:0.75rem;">MOST TAKEN IN ROUND 1 (ALL TIME)</div>',
        unsafe_allow_html=True,
    )
    _r1_player_counts = (
        r1_real[r1_real["position"].isin(SKILL_POS)]
        .groupby(["player_name", "position"]).size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(10)
    )
    r1_html = ""
    for rank, (_, pr1) in enumerate(_r1_player_counts.iterrows()):
        medal = ["🥇","🥈","🥉","4.","5.","6.","7.","8.","9.","10."][rank]
        pb = _pos_badge(str(pr1["position"]))
        r1_html += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:5px 0;border-bottom:1px solid #1E2D40;">'
            f'<span style="color:#F5F5F5;font-size:0.72rem;">{medal} {pr1["player_name"]} {pb}</span>'
            f'<span style="color:#D4AF37;font-weight:700;font-size:0.72rem;">{pr1["count"]}×</span>'
            f'</div>'
        )
    st.markdown(
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-radius:6px;padding:14px;">'
        f'{r1_html}</div>',
        unsafe_allow_html=True,
    )

with r1_right:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
        'letter-spacing:3px;margin-bottom:0.75rem;">MOST COMMON #1 OVERALL PICK</div>',
        unsafe_allow_html=True,
    )
    _first_overall = real.sort_values("overall_pick").groupby("season").first().reset_index()
    _fo_counts = _first_overall.groupby("player_name").size().sort_values(ascending=False).head(5)
    fo_html = ""
    for rank, (player, count) in enumerate(_fo_counts.items()):
        pos_val = _first_overall[_first_overall["player_name"] == player]["position"].iloc[0]
        pb = _pos_badge(str(pos_val) if pos_val else "?")
        years_str = " · ".join(
            str(y) for y in sorted(_first_overall[_first_overall["player_name"] == player]["season"].tolist())
        )
        medal = ["🥇","🥈","🥉","4.","5."][rank]
        fo_html += (
            f'<div style="padding:6px 0;border-bottom:1px solid #1E2D40;">'
            f'<div style="display:flex;justify-content:space-between;">'
            f'<span style="color:#F5F5F5;font-size:0.72rem;">{medal} {player} {pb}</span>'
            f'<span style="color:#D4AF37;font-weight:700;font-size:0.72rem;">{count}×</span>'
            f'</div>'
            f'<div style="font-size:0.58rem;color:#6B7280;">{years_str}</div>'
            f'</div>'
        )

    # Notable #1 overall moments
    shawn_fo = _first_overall[_first_overall["manager"] == "Shawn"]
    thomas_fo = _first_overall[_first_overall["manager"] == "Thomas"]
    fo_most_mgr = _first_overall.groupby("manager").size().sort_values(ascending=False)
    fo_top_mgr = fo_most_mgr.index[0]
    fo_top_count = fo_most_mgr.iloc[0]

    fo_html += (
        f'<div style="margin-top:10px;padding:8px;background:#081120;border-radius:4px;">'
        f'<div style="font-size:0.62rem;color:#D4AF37;font-weight:600;margin-bottom:3px;">'
        f'Most #1 Overall Picks</div>'
        f'<div style="font-size:0.7rem;color:#F5F5F5;">{_mgr_emoji(fo_top_mgr)} {fo_top_mgr} — {fo_top_count}× first overall</div>'
        f'</div>'
    )

    st.markdown(
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-radius:6px;padding:14px;">'
        f'{fo_html}</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 6 — THE SUPERLATIVES
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE SUPERLATIVES", "Draft Records"), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

def _rec_block(title, entries, val_suffix="×"):
    rows = ""
    for i, (name, val) in enumerate(entries[:5]):
        medal = ["🥇","🥈","🥉","4.","5."][i]
        rows += (
            f'<div style="display:flex;justify-content:space-between;padding:4px 0;'
            f'border-bottom:1px solid #1E2D40;">'
            f'<span style="color:#F5F5F5;font-size:0.72rem;">{medal} {name}</span>'
            f'<span style="color:#D4AF37;font-weight:700;font-size:0.72rem;">{val}{val_suffix}</span>'
            f'</div>'
        )
    return (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-radius:6px;'
        f'padding:14px;margin-bottom:12px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.78rem;color:#A7B0BC;'
        f'letter-spacing:3px;margin-bottom:8px;">{title}</div>'
        f'{rows}</div>'
    )

def _rec_fact(title, body, color="#D4AF37"):
    return (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-radius:6px;'
        f'padding:14px;margin-bottom:12px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.78rem;color:#A7B0BC;'
        f'letter-spacing:3px;margin-bottom:6px;">{title}</div>'
        f'<div style="color:{color};font-size:0.82rem;font-family:\'Inter\',sans-serif;">{body}</div>'
        f'</div>'
    )

with col1:
    st.markdown(_rec_block("MOST DRAFTED PLAYERS", rec["most_drafted_players"]), unsafe_allow_html=True)
    # Longest draft career
    top_career = player_legend.sort_values("career_span", ascending=False).head(5)
    career_entries = [(r["player_name"], r["career_span"]) for _, r in top_career.iterrows()]
    st.markdown(_rec_block("LONGEST DRAFT CAREER", career_entries, val_suffix=" seasons"), unsafe_allow_html=True)

with col2:
    st.markdown(_rec_block("MOST MANAGERS TO OWN", rec["most_mgrs_one_player"]), unsafe_allow_html=True)
    st.markdown(_rec_block("MOST KEPT PLAYERS", rec["most_kept_players"]), unsafe_allow_html=True)

with col3:
    eq = rec["earliest_qb"][0] if rec["earliest_qb"] else {}
    st.markdown(_rec_fact(
        "EARLIEST QB EVER TAKEN",
        f'{eq.get("player_name","?")} &nbsp;·&nbsp; {eq.get("season","?")} &nbsp;·&nbsp; '
        f'Pick #{eq.get("overall_pick","?")} &nbsp;·&nbsp; {eq.get("manager","?")}',
    ), unsafe_allow_html=True)
    et = rec["earliest_te"][0] if rec["earliest_te"] else {}
    st.markdown(_rec_fact(
        "EARLIEST TE EVER TAKEN",
        f'{et.get("player_name","?")} &nbsp;·&nbsp; {et.get("season","?")} &nbsp;·&nbsp; '
        f'Pick #{et.get("overall_pick","?")} &nbsp;·&nbsp; {et.get("manager","?")}',
    ), unsafe_allow_html=True)
    # Player with most total seasons (drafted + kept)
    total_legend = player_legend.sort_values("career_span", ascending=False).iloc[0]
    st.markdown(_rec_fact(
        "LONGEST-RUNNING PLAYER",
        f'{total_legend["player_name"]} &nbsp;·&nbsp; {int(total_legend["first_season"])}–{int(total_legend["last_season"])} &nbsp;·&nbsp; '
        f'{int(total_legend["career_span"])} seasons &nbsp;·&nbsp; {int(total_legend["total_drafts"])} total drafts',
    ), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 7 — DRAFT HALL OF FAME & SHAME
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE VERDICT", "Draft Hall of Fame & Shame"), unsafe_allow_html=True)

hof_col, hos_col = st.columns(2)

with hof_col:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#D4AF37;'
        'letter-spacing:4px;margin-bottom:1rem;">🏛️ HALL OF FAME</div>',
        unsafe_allow_html=True,
    )

    # Most drafted non-DEF players
    top_hof = player_legend.sort_values("total_drafts", ascending=False).head(3)
    for rank, (_, row) in enumerate(top_hof.iterrows()):
        medal = ["🥇","🥈","🥉"][rank]
        pos = str(row["position"]) if row["position"] else "?"
        pb = _pos_badge(pos)
        loyal = str(row.get("most_loyal", "—"))
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #D4AF37;'
            f'border-radius:6px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<span style="font-size:1.3rem;">{medal}</span>'
            f'<div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F5F5;'
            f'letter-spacing:2px;">{row["player_name"]} {pb}</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'Drafted {int(row["total_drafts"])}× &nbsp;·&nbsp; '
            f'{int(row["unique_managers"])} managers &nbsp;·&nbsp; '
            f'{int(row["career_span"])}-season career &nbsp;·&nbsp; '
            f'Most loyal: {loyal}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )

    # Most kept players as HOF honorees
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.7rem;color:#A7B0BC;'
        'letter-spacing:3px;margin:12px 0 6px;">KEEPER HALL OF FAME ENTRIES</div>',
        unsafe_allow_html=True,
    )
    for rank, (player, count) in enumerate(rec["most_kept_players"][:4]):
        mgr_rows = po[(po["player_name"] == player) & (po["keeper_count"] > 0)]
        mgr_str = " · ".join(
            f'{_mgr_emoji(r["manager"])} {r["manager"]} ({r["keeper_count"]}×)'
            for _, r in mgr_rows.sort_values("keeper_count", ascending=False).iterrows()
        )
        pos = po[po["player_name"] == player]["position"].iloc[0] if len(po[po["player_name"] == player]) > 0 else "?"
        medal = ["🥇","🥈","🥉","🏅"][rank]
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #D4AF37;'
            f'border-radius:6px;padding:10px 14px;margin-bottom:6px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.9rem;color:#F5F5F5;">'
            f'{medal} {player} {_pos_badge(str(pos))}</div>'
            f'<div style="font-size:0.62rem;color:#A7B0BC;margin-top:2px;">'
            f'Kept {count}× &nbsp;·&nbsp; {mgr_str}</div>'
            f'</div>',
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
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;color:#F5F5F5;">'
            f'🚨 {ed["player_name"]} D/ST — Round 1</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'{ed["season"]} · Pick #{ed["overall_pick"]} · '
            f'{_mgr_emoji(ed["manager"])} {ed["manager"]} · A defense. In round one.</div></div>',
            unsafe_allow_html=True,
        )

    # Early kickers
    for ek in rec["earliest_k"][:2]:
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #F59E0B;'
            f'border-radius:6px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;color:#F5F5F5;">'
            f'🦶 {ek["player_name"]} — Round {ek["round"]}</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'{ek["season"]} · Pick #{ek["overall_pick"]} · '
            f'{_mgr_emoji(ek["manager"])} {ek["manager"]}</div></div>',
            unsafe_allow_html=True,
        )

    # Most R1 picks never kept (perpetual disappointment)
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.7rem;color:#F87171;'
        'letter-spacing:3px;margin:10px 0 6px;">NEVER EARNED A KEEPER SPOT</div>',
        unsafe_allow_html=True,
    )
    _kept_set = set(keepers["player_name"].unique())
    _r1_bust = (
        r1_real[r1_real["position"].isin(SKILL_POS)]
        .groupby("player_name")
        .agg(r1_drafts=("manager", "count"), unique_mgrs=("manager", "nunique"))
        .reset_index()
    )
    _r1_bust = _r1_bust[~_r1_bust["player_name"].isin(_kept_set)]
    _r1_bust = _r1_bust.sort_values("r1_drafts", ascending=False).head(4)
    for _, brow in _r1_bust.iterrows():
        pos_b_val = real[real["player_name"] == brow["player_name"]]["position"].iloc[0] if len(real[real["player_name"] == brow["player_name"]]) > 0 else "?"
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #EF4444;'
            f'border-radius:6px;padding:10px 14px;margin-bottom:6px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.9rem;color:#F5F5F5;">'
            f'😬 {brow["player_name"]} {_pos_badge(str(pos_b_val) if pos_b_val else "?")}</div>'
            f'<div style="font-size:0.62rem;color:#A7B0BC;margin-top:2px;">'
            f'Drafted in Round 1 by {brow["r1_drafts"]} managers. '
            f'Never kept. Nobody ever committed.</div></div>',
            unsafe_allow_html=True,
        )

    # Cult DEF pick
    top_shared_def = real[real["position"] == "DEF"].groupby("player_name")["manager"].nunique().sort_values(ascending=False)
    if len(top_shared_def) > 0:
        def_name = top_shared_def.index[0]
        def_mgr_count = int(top_shared_def.iloc[0])
        def_total = int(real[real["player_name"] == def_name].shape[0])
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid #8B5CF6;'
            f'border-radius:6px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.95rem;color:#F5F5F5;">'
            f'🔄 {def_name} D/ST — The Cult Pick</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-top:2px;">'
            f'Drafted {def_total}× by {def_mgr_count} different managers. Nobody could resist.</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

render_page_footer(
    href="/keeper_hall",
    cta="EXPLORE THE KEEPER HALL",
    tagline="SOME PLAYERS WERE TOO GOOD TO LET GO.<br>THIS IS THEIR STORY.",
)
