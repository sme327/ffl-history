"""League History — The Evolution of the League."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data import (
    load_all, get_champions, get_all_time_manager_stats,
    MANAGER_EMOJI, MANAGER_COLORS, FOUNDED, CURRENT_SEASON,
)
from utils.styles import inject_css, render_nav, render_page_footer, html_table
from utils.narratives import LEAGUE_ERAS, NFL_CONTEXT

st.set_page_config(
    page_title="The Evolution of the League · The Long Game",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("league_history")

data      = load_all()
champions = get_champions()
standings = data["standings"]
wm        = data["weekly_matchups"]
tnh       = data["team_name_history"]
ls        = data["league_settings"]
_tnh_lkp  = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

# ── PRE-COMPUTE ────────────────────────────────────────────────────────────────
season_scoring = (
    standings.groupby("season")["points_for"]
    .agg(avg="mean", high="max", low="min")
    .reset_index().sort_values("season")
)
_rs_all  = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
_std_all = standings.copy()
_std_all["gp"]  = _std_all["wins"] + _std_all["losses"] + _std_all["ties"]
_std_all["wpc"] = _std_all["wins"] / _std_all["gp"].replace(0, float("nan"))

def _era_data(start: int, end: int) -> dict:
    era_ch  = champions[(champions["season"] >= start) & (champions["season"] <= end)]
    top_mgrs = era_ch.groupby("champion_manager").size().sort_values(ascending=False)
    era_szn  = season_scoring[(season_scoring["season"] >= start) & (season_scoring["season"] <= end)]
    era_rs   = _rs_all[_rs_all["season"].between(start, end)]
    return {
        "champ_count": len(era_ch),
        "unique_champs": era_ch["champion_manager"].nunique(),
        "top_mgrs": top_mgrs,
        "avg_score": float(era_szn["avg"].mean()) if len(era_szn) else 0.0,
        "high_score": float(era_rs["team_score"].max()) if len(era_rs) else 0.0,
        "seasons": list(range(start, min(end, CURRENT_SEASON) + 1)),
    }

def _why_it_matters(label: str) -> str:
    return (
        f'<div style="background:rgba(212,175,55,0.06);border-left:2px solid rgba(212,175,55,0.4);'
        f'padding:6px 10px;margin-top:8px;border-radius:0 4px 4px 0;">'
        f'<span style="font-size:0.58rem;color:#D4AF37;letter-spacing:2px;font-family:\'Inter\',sans-serif;'
        f'text-transform:uppercase;">WHY IT MATTERS</span>'
        f'<div style="font-size:0.68rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;margin-top:3px;">{label}</div>'
        f'</div>'
    )

# ── PAGE HEADER ────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-page-title">The Evolution of the League</div>
    <div class="tl-page-subtitle">
        {FOUNDED}–{CURRENT_SEASON} &nbsp;·&nbsp; 25 Seasons &nbsp;·&nbsp;
        Four eras. One league. An unbroken thread.
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.8rem;'
    'max-width:720px;line-height:1.75;margin-bottom:1.5rem;">'
    'This is not a statistics page. It\'s a history page. '
    'The numbers exist to support the story of how this league changed over 25 years — '
    'how strategy evolved, how scoring shifted, how a simple group of friends built something '
    'worth documenting.'
    '</p>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — LEAGUE ERAS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="tl-section-label">Chapters in League History</div>'
    '<div class="tl-section-title">The Four Eras</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;'
    'margin:-0.5rem 0 1.5rem;">Every league has chapters. These are ours.</p>',
    unsafe_allow_html=True,
)

for era in LEAGUE_ERAS:
    start_yr = era["start"]
    end_yr   = min(era["end"], CURRENT_SEASON)
    ed       = _era_data(start_yr, end_yr)
    color    = era["color"]
    icon     = era["icon"]
    top_mgrs = ed["top_mgrs"]

    # Champions in era
    era_ch_df = champions[(champions["season"] >= start_yr) & (champions["season"] <= end_yr)]

    # Championship title list for era
    yr_list = " · ".join(
        f"<strong style='color:{color};'>{int(r['season'])}</strong> {MANAGER_EMOJI.get(r['champion_manager'],'🏆')} {r['champion_manager']}"
        for _, r in era_ch_df.sort_values("season").iterrows()
    )

    st.markdown(
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:6px solid {color};'
        f'border-radius:8px;padding:28px 32px;margin-bottom:20px;">'

        # Era header
        f'<div style="display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:12px;">'
        f'<span style="font-size:2rem;">{icon}</span>'
        f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;color:{color};letter-spacing:4px;">{era["name"]}</span>'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#A7B0BC;letter-spacing:2px;">{era["years"]}</span>'
        f'</div>'

        # Headline
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.2rem;color:#F5F5F5;letter-spacing:2px;margin-bottom:10px;">{era["headline"]}</div>'

        # Body copy
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.78rem;color:#A7B0BC;line-height:1.75;max-width:680px;margin-bottom:18px;">{era["body"]}</div>'

        # Stats row
        f'<div style="display:flex;gap:24px;flex-wrap:wrap;margin-bottom:16px;">'
        f'<div style="text-align:center;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:{color};">{ed["champ_count"]}</div>'
        f'<div style="font-size:0.55rem;color:#6B7280;letter-spacing:2px;text-transform:uppercase;">Titles Awarded</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:{color};">{ed["unique_champs"]}</div>'
        f'<div style="font-size:0.55rem;color:#6B7280;letter-spacing:2px;text-transform:uppercase;">Unique Champions</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:{color};">{ed["avg_score"]:.0f}</div>'
        f'<div style="font-size:0.55rem;color:#6B7280;letter-spacing:2px;text-transform:uppercase;">Avg Weekly PF</div>'
        f'</div>'
        f'</div>'

        # Champions
        f'<div style="font-size:0.58rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">Champions of the Era</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#A7B0BC;line-height:1.9;">{yr_list if yr_list else "Data not yet available."}</div>'

        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — SCORING EVOLUTION
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="tl-section-label">25 Years of Weekly Scoring</div>'
    '<div class="tl-section-title">Scoring Evolution</div>',
    unsafe_allow_html=True,
)

champ_season_pf = []
for _, ch in champions.iterrows():
    sr = standings[(standings["season"] == ch["season"]) & (standings["team_name"] == ch["champion_team"])]
    if len(sr) > 0:
        champ_season_pf.append({"season": int(ch["season"]), "pf": float(sr.iloc[0]["points_for"])})
champ_pf_df = pd.DataFrame(champ_season_pf) if champ_season_pf else pd.DataFrame(columns=["season", "pf"])

fig = go.Figure()

# Era shading
ERA_SHADES = [
    (2001, 2004, "rgba(212,175,55,0.06)", "Founding"),
    (2005, 2009, "rgba(34,197,94,0.06)",  "Workhorse"),
    (2010, 2015, "rgba(167,139,250,0.06)","Keeper Rev."),
    (2016, CURRENT_SEASON, "rgba(59,130,246,0.06)", "Modern"),
]
for s_start, s_end, fill, era_lbl in ERA_SHADES:
    fig.add_vrect(
        x0=s_start - 0.5, x1=min(s_end, CURRENT_SEASON) + 0.5,
        fillcolor=fill, line_width=0,
        annotation_text=era_lbl,
        annotation_position="top left",
        annotation_font=dict(size=9, color="#6B7280"),
    )

# Shaded range band
fig.add_trace(go.Scatter(
    x=list(season_scoring["season"]) + list(season_scoring["season"])[::-1],
    y=list(season_scoring["high"].round(1)) + list(season_scoring["low"].round(1))[::-1],
    fill="toself", fillcolor="rgba(184,144,46,0.08)",
    line=dict(color="rgba(0,0,0,0)"),
    hoverinfo="skip", name="High–Low Range",
))
# Average line
fig.add_trace(go.Scatter(
    x=season_scoring["season"], y=season_scoring["avg"].round(1),
    mode="lines+markers",
    line=dict(color="#D4AF37", width=2.5),
    marker=dict(color="#D4AF37", size=6),
    name="League Average",
    hovertemplate="<b>%{x}</b> · Avg: %{y:.1f}<extra></extra>",
))
# Champion stars
if len(champ_pf_df) > 0:
    fig.add_trace(go.Scatter(
        x=champ_pf_df["season"], y=champ_pf_df["pf"].round(1),
        mode="markers",
        marker=dict(color="#D4AF37", size=10, symbol="star", line=dict(color="#081120", width=1)),
        name="Champion's Season Total",
        hovertemplate="<b>%{x}</b> · Champion: %{y:.1f}<extra></extra>",
    ))

fig.update_layout(
    paper_bgcolor="#081120", plot_bgcolor="#0F1B2D",
    font=dict(family="Inter", color="#A7B0BC", size=11),
    margin=dict(l=0, r=0, t=30, b=0), height=280,
    legend=dict(orientation="h", x=0, y=1.1, font=dict(size=10, color="#A7B0BC"), bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A7B0BC"), tickmode="linear", dtick=2),
    yaxis=dict(showgrid=True, gridcolor="rgba(184,144,46,0.12)", zeroline=False, tickfont=dict(color="#A7B0BC")),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# Scoring era interpretation cards
_peak_season   = int(season_scoring.loc[season_scoring["avg"].idxmax(), "season"])
_peak_avg      = float(season_scoring["avg"].max())
_lowest_season = int(season_scoring.loc[season_scoring["avg"].idxmin(), "season"])
_lowest_avg    = float(season_scoring["avg"].min())
_score_rise    = _peak_avg - _lowest_avg

se1, se2, se3 = st.columns(3)
with se1:
    st.markdown(
        f'<div class="tl-card">'
        f'<div class="tl-section-label">Peak Scoring Era</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{_peak_season} Season</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">League average {_peak_avg:.1f} pts — the most prolific scoring year in history.</div>'
        f'{_why_it_matters("Scoring peaks often align with rule changes or the emergence of elite offensive players in the NFL. The highest-scoring seasons tell you when the game changed.")}'
        f'</div>',
        unsafe_allow_html=True,
    )
with se2:
    st.markdown(
        f'<div class="tl-card">'
        f'<div class="tl-section-label">Lean Era</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{_lowest_season} Season</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">League average {_lowest_avg:.1f} pts — the most defensive year on record.</div>'
        f'{_why_it_matters("Low-scoring years reward depth. The manager with the most reliable weekly floor tends to outperform the one chasing upside.")}'
        f'</div>',
        unsafe_allow_html=True,
    )
with se3:
    st.markdown(
        f'<div class="tl-card">'
        f'<div class="tl-section-label">25-Year Scoring Rise</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">+{_score_rise:.1f} pts/week</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">Average weekly scoring increased by {_score_rise:.1f} pts from the league\'s lowest to highest era.</div>'
        f'{_why_it_matters("The NFL became a scoring-first league. This league followed. Draft strategies that worked in 2004 are obsolete in 2024.")}'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — COMPETITIVE BALANCE
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="tl-section-label">Who Competed, Who Dominated</div>'
    '<div class="tl-section-title">Competitive Balance</div>',
    unsafe_allow_html=True,
)

# Compute per-season unique playoff managers
pg = data["playoff_games"]
pg_champ = pg[pg["bracket"] == "championship"]
pl_mgr_per_season = {}
for szn in sorted(champions["season"].unique()):
    pg_szn = pg_champ[pg_champ["season"] == szn]
    teams = set(pg_szn["team_1"].tolist() + pg_szn["team_2"].tolist())
    mgrs = {_tnh_lkp.get((int(szn), t), t) for t in teams}
    pl_mgr_per_season[szn] = mgrs

all_pl_mgrs = [m for mgrs in pl_mgr_per_season.values() for m in mgrs]
unique_pl_mgrs_ever = len(set(all_pl_mgrs))
top_pl_mgr = pd.Series(all_pl_mgrs).value_counts()
_most_consistent = top_pl_mgr.index[0] if len(top_pl_mgr) > 0 else "—"
_most_consistent_n = int(top_pl_mgr.iloc[0]) if len(top_pl_mgr) > 0 else 0

total_seasons_ct = CURRENT_SEASON - FOUNDED + 1
unique_champs_ct = int(champions["champion_manager"].nunique())

cb1, cb2, cb3, cb4 = st.columns(4)
for col, val, lbl in [
    (cb1, unique_champs_ct, "Unique Champions"),
    (cb2, unique_pl_mgrs_ever, "Managers to Make Playoffs"),
    (cb3, f"{unique_champs_ct/total_seasons_ct:.0%}", "Championship Diversity Rate"),
    (cb4, f"{_most_consistent_n}", f"Playoff Apps — {MANAGER_EMOJI.get(_most_consistent,'')} {_most_consistent}"),
]:
    col.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{val}</div>'
        f'<div class="tl-metric-label">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Win concentration chart (Lorenz-style: top N managers' share of total titles)
champ_share = champions.groupby("champion_manager").size().sort_values(ascending=False)
cumulative_pct = (champ_share.cumsum() / len(champions) * 100).values
n_mgrs_axis = list(range(1, len(cumulative_pct) + 1))

fig_lorenz = go.Figure()
fig_lorenz.add_trace(go.Bar(
    x=[m for m in champ_share.index],
    y=champ_share.values,
    marker_color="#D4AF37",
    text=[f"{v}" for v in champ_share.values],
    textposition="outside",
    textfont=dict(color="#D4AF37", size=11),
    hovertemplate="<b>%{x}</b><br>%{y} title(s)<extra></extra>",
))
fig_lorenz.update_layout(
    paper_bgcolor="#081120", plot_bgcolor="#0F1B2D",
    font=dict(family="Inter", color="#A7B0BC", size=11),
    margin=dict(l=0, r=0, t=20, b=0), height=220,
    xaxis=dict(tickangle=-30, tickfont=dict(size=10)),
    yaxis=dict(gridcolor="rgba(184,144,46,0.12)", title="Championships"),
    showlegend=False,
)
st.plotly_chart(fig_lorenz, use_container_width=True, config={"displayModeBar": False})

# Concentration callout
top1_pct = int(champ_share.iloc[0] / len(champions) * 100)
top3_pct = int(champ_share.iloc[:3].sum() / len(champions) * 100)
st.markdown(
    f'<p style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#A7B0BC;margin-top:-0.5rem;">'
    f'The top manager holds {top1_pct}% of all championships. '
    f'The top 3 managers account for {top3_pct}% of titles. '
    f'{unique_champs_ct} different managers have won at least once across {total_seasons_ct} seasons.</p>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — LEAGUE FACTS (with Why It Matters)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="tl-section-label">Records That Define the League</div>'
    '<div class="tl-section-title">By the Numbers</div>',
    unsafe_allow_html=True,
)

_rs_wins_df  = _rs_all[_rs_all["result"] == "Win"].copy()
_rs_wins_df["margin"] = _rs_wins_df["team_score"] - _rs_wins_df["opponent_score"]
_wk_high     = _rs_all.loc[_rs_all["team_score"].idxmax()]
_wk_high_mgr = _tnh_lkp.get((int(_wk_high["season"]), _wk_high["team_name"]), _wk_high["team_name"])
_blowout     = _rs_wins_df.loc[_rs_wins_df["margin"].idxmax()]
_blowout_mgr = _tnh_lkp.get((int(_blowout["season"]), _blowout["team_name"]), _blowout["team_name"])
_close       = _rs_wins_df.loc[_rs_wins_df["margin"].idxmin()]
_close_mgr   = _tnh_lkp.get((int(_close["season"]), _close["team_name"]), _close["team_name"])
_close_loser = _tnh_lkp.get((int(_close["season"]), _close["opponent"]), _close["opponent"])
_best_rec    = _std_all.loc[_std_all["wpc"].idxmax()]
_best_rec_mgr= _tnh_lkp.get((int(_best_rec["season"]), _best_rec["team_name"]), _best_rec["team_name"])
_best_pf     = standings.loc[standings["points_for"].idxmax()]
_best_pf_mgr = _tnh_lkp.get((int(_best_pf["season"]), _best_pf["team_name"]), _best_pf["team_name"])

def _fact_card(label, headline, sub, why):
    return (
        f'<div class="tl-card">'
        f'<div class="tl-section-label">{label}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{headline}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">{sub}</div>'
        f'{_why_it_matters(why)}'
        f'</div>'
    )

lf1, lf2, lf3 = st.columns(3)
with lf1:
    st.markdown(_fact_card(
        "Single-Week Scoring Record",
        f"{_wk_high['team_score']:.2f} pts",
        f"{_wk_high_mgr} · {_wk_high['team_name']} · {int(_wk_high['season'])} Wk{int(_wk_high['week'])}",
        "The single highest weekly score in 25 years. Everything went right that week.",
    ), unsafe_allow_html=True)
with lf2:
    st.markdown(_fact_card(
        "Biggest Regular Season Blowout",
        f"+{_blowout['margin']:.2f} pts",
        f"{_blowout_mgr} · {int(_blowout['season'])} Week {int(_blowout['week'])}",
        "The most dominant single-game performance in league history. Some weeks it just isn't fair.",
    ), unsafe_allow_html=True)
with lf3:
    st.markdown(_fact_card(
        "Closest Regular Season Game",
        f"+{_close['margin']:.2f} pts",
        f"{_close_mgr} edged {_close_loser} · {int(_close['season'])} Week {int(_close['week'])}",
        "Fantasy football decided by fractions. One more yard from a backup RB would have changed everything.",
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
lf4, lf5, lf6 = st.columns(3)
with lf4:
    st.markdown(_fact_card(
        "Best Single-Season Record",
        f"{int(_best_rec['wins'])}-{int(_best_rec['losses'])}",
        f"{_best_rec_mgr} · {_best_rec['team_name']} · {int(_best_rec['season'])}",
        "The most dominant regular season in league history. Not necessarily the championship — but the clearest statement of excellence.",
    ), unsafe_allow_html=True)
with lf5:
    st.markdown(_fact_card(
        "Most Points in a Season",
        f"{_best_pf['points_for']:.1f} pts",
        f"{_best_pf_mgr} · {_best_pf['team_name']} · {int(_best_pf['season'])}",
        "This team was on fire all season. Volume, consistency, and probably a few lucky bounces.",
    ), unsafe_allow_html=True)
with lf6:
    _peak_s   = int(season_scoring.loc[season_scoring["avg"].idxmax(), "season"])
    _peak_avg = float(season_scoring["avg"].max())
    st.markdown(_fact_card(
        "Highest-Scoring Season",
        str(_peak_s),
        f"League average {_peak_avg:.1f} pts/team — the most explosive year on record",
        "This was the year the NFL's scoring explosion fully translated to fantasy. Every lineup was dangerous.",
    ), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — ALL-TIME STANDINGS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="tl-section-label">The Complete Record</div>'
    '<div class="tl-section-title">All-Time Manager Stats</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#6B7280;margin:-0.5rem 0 1rem;">'
    'Raw data lives here. The stories live above.</p>',
    unsafe_allow_html=True,
)

ats = get_all_time_manager_stats()
ats_rows = []
for _, r in ats.iterrows():
    emoji   = MANAGER_EMOJI.get(r["canonical_name"], "")
    champ_s = ("🏆 " * int(r["championships"])).strip() if r["championships"] > 0 else "—"
    best    = f"#{int(r['best_finish'])}" if r.get("best_finish") and not pd.isna(r["best_finish"]) else "—"
    worst   = f"#{int(r['worst_finish'])}" if r.get("worst_finish") and not pd.isna(r["worst_finish"]) else "—"
    ats_rows.append([
        f"{emoji} {r['canonical_name']}",
        (str(int(r["seasons"])), "muted"),
        f"{int(r['rs_wins'])}-{int(r['rs_losses'])}",
        (f"{r['rs_pf']:,.1f}", ""),
        (f"{r['rs_pa']:,.1f}", "muted"),
        f"{int(r['pl_wins'])}-{int(r['pl_losses'])}",
        (str(int(r["playoff_apps"])), ""),
        (str(int(r["finals_apps"])), ""),
        (champ_s, "gold"),
        (f"{best} / {worst}", "muted"),
    ])

st.markdown(
    html_table(
        ["Manager", "Seasons", "RS W-L", "RS PF", "RS PA", "PL W-L", "Playoffs", "Finals", "Titles", "Best/Worst"],
        ats_rows,
    ),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── CROSS-PAGE CONNECTIONS ─────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Continue Exploring</div>',
    unsafe_allow_html=True,
)
xp_cols = st.columns(3)
_xp = [
    ("/champions",    "🏆", "Trophy Room",       "Every championship. The dynasties that defined each era."),
    ("/league_timeline", "📅", "Timeline",        "The spine of the museum. Every event, every turning point."),
    ("/season_archive",  "📖", "Season Archive",  "Dive into any individual season — the story, the champion, the NFL context."),
]
for col, (href, icon, title, desc) in zip(xp_cols, _xp):
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
    href="/season_archive",
    cta="BROWSE THE SEASON ARCHIVE",
    tagline="RECORDS SHOW WHAT HAPPENED.<br>THE ARCHIVES SHOW WHY IT MATTERED.",
)
