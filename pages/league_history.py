"""League History page — season-by-season overview."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data import load_all, get_champions, get_all_time_manager_stats, MANAGER_EMOJI, FOUNDED, CURRENT_SEASON
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="League History · The Long Game",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("league_history")

data = load_all()
champions = get_champions()
standings = data["standings"]
wm = data["weekly_matchups"]
tnh = data["team_name_history"]
ls = data["league_settings"]

# ── PAGE TITLE ─────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="tl-page-title">League History</div>
    <div class="tl-page-subtitle">{FOUNDED}–{CURRENT_SEASON} · 25 Seasons of Competition</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── SCORING TREND CHART ────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">The Scoring Era</div>'
    '<div class="tl-section-title">League Scoring Trends by Season</div>',
    unsafe_allow_html=True,
)

season_scoring = (
    standings.groupby("season")["points_for"]
    .agg(avg="mean", high="max", low="min")
    .reset_index()
    .sort_values("season")
)

# Champion's SEASON total PF (from standings) — apples-to-apples with the avg/range
champ_season_pf = []
for _, champ in champions.iterrows():
    std_row = standings[
        (standings["season"] == champ["season"]) &
        (standings["team_name"] == champ["champion_team"])
    ]
    if len(std_row) > 0:
        champ_season_pf.append({"season": int(champ["season"]), "pf": float(std_row.iloc[0]["points_for"])})
champ_pf_df = pd.DataFrame(champ_season_pf) if champ_season_pf else pd.DataFrame(columns=["season", "pf"])

fig = go.Figure()

# Shaded min-max band
fig.add_trace(go.Scatter(
    x=list(season_scoring["season"]) + list(season_scoring["season"])[::-1],
    y=list(season_scoring["high"].round(1)) + list(season_scoring["low"].round(1))[::-1],
    fill="toself",
    fillcolor="rgba(184,144,46,0.08)",
    line=dict(color="rgba(0,0,0,0)"),
    hoverinfo="skip",
    name="High–Low Range",
    showlegend=True,
))
# Average line
fig.add_trace(go.Scatter(
    x=season_scoring["season"],
    y=season_scoring["avg"].round(1),
    mode="lines+markers",
    line=dict(color="#D4AF37", width=2),
    marker=dict(color="#D4AF37", size=6),
    name="League Avg",
    hovertemplate="<b>%{x}</b> · Avg: %{y:.1f}<extra></extra>",
))
# Champion's season total PF
fig.add_trace(go.Scatter(
    x=champ_pf_df["season"],
    y=champ_pf_df["pf"].round(1),
    mode="markers",
    marker=dict(color="#D4AF37", size=10, symbol="star", line=dict(color="#081120", width=1)),
    name="Champion's Season Total",
    hovertemplate="<b>%{x}</b> · Champion total: %{y:.1f}<extra></extra>",
))

fig.update_layout(
    paper_bgcolor="#081120",
    plot_bgcolor="#0F1B2D",
    font=dict(family="Inter", color="#A7B0BC", size=11),
    margin=dict(l=0, r=0, t=10, b=0),
    height=260,
    legend=dict(
        orientation="h", x=0.01, y=1.12,
        font=dict(size=10, color="#A7B0BC"),
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A7B0BC"), tickmode="linear", dtick=2),
    yaxis=dict(showgrid=True, gridcolor="rgba(184,144,46,0.12)", zeroline=False, tickfont=dict(color="#A7B0BC")),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;font-size:0.7rem;color:#A7B0BC;">⭐ Star = champion\'s full-season regular season total &nbsp;|&nbsp; Shaded band = scoring range across all teams &nbsp;|&nbsp; Regular season points only</p>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── LEAGUE FACTS ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">By the Numbers</div>'
    '<div class="tl-section-title">League Facts</div>',
    unsafe_allow_html=True,
)

_tnh_lookup = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
_rs_all = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
_rs_wins = _rs_all[_rs_all["result"] == "Win"].copy()
_rs_wins["margin"] = _rs_wins["team_score"] - _rs_wins["opponent_score"]

# Single-week scoring record
_wk_high = _rs_all.loc[_rs_all["team_score"].idxmax()]
_wk_high_mgr = _tnh_lookup.get((int(_wk_high["season"]), _wk_high["team_name"]), _wk_high["team_name"])

# Biggest blowout
_blowout = _rs_wins.loc[_rs_wins["margin"].idxmax()]
_blowout_mgr = _tnh_lookup.get((int(_blowout["season"]), _blowout["team_name"]), _blowout["team_name"])

# Closest game
_close = _rs_wins.loc[_rs_wins["margin"].idxmin()]
_close_mgr = _tnh_lookup.get((int(_close["season"]), _close["team_name"]), _close["team_name"])
_close_loser = _tnh_lookup.get((int(_close["season"]), _close["opponent"]), _close["opponent"])

# Best single-season record
_std = standings.copy()
_std["gp"] = _std["wins"] + _std["losses"] + _std["ties"]
_std["wpc"] = _std["wins"] / _std["gp"].replace(0, float("nan"))
_best_rec = _std.loc[_std["wpc"].idxmax()]
_best_rec_mgr = _tnh_lookup.get((int(_best_rec["season"]), _best_rec["team_name"]), _best_rec["team_name"])

# Highest single-season PF
_best_pf = standings.loc[standings["points_for"].idxmax()]
_best_pf_mgr = _tnh_lookup.get((int(_best_pf["season"]), _best_pf["team_name"]), _best_pf["team_name"])

# Highest-scoring season (league avg)
_season_avgs = standings.groupby("season")["points_for"].mean()
_peak_season = int(_season_avgs.idxmax())
_peak_avg = _season_avgs.max()

def _lfact(label, headline, sub):
    return f"""<div class="tl-card">
        <div class="tl-section-label">{label}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{headline}</div>
        <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">{sub}</div>
    </div>"""

lf1, lf2, lf3 = st.columns(3)
with lf1:
    st.markdown(_lfact("Single-Week Scoring Record", f"{_wk_high['team_score']:.2f} pts",
        f"{_wk_high_mgr} · {_wk_high['team_name']} · {int(_wk_high['season'])} Wk{int(_wk_high['week'])}"), unsafe_allow_html=True)
with lf2:
    st.markdown(_lfact("Biggest Regular Season Blowout", f"+{_blowout['margin']:.2f}",
        f"{_blowout_mgr} · {int(_blowout['season'])} Week {int(_blowout['week'])}"), unsafe_allow_html=True)
with lf3:
    st.markdown(_lfact("Closest Regular Season Game", f"+{_close['margin']:.2f}",
        f"{_close_mgr} edged {_close_loser} · {int(_close['season'])} Week {int(_close['week'])}"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

lf4, lf5, lf6 = st.columns(3)
with lf4:
    st.markdown(_lfact("Best Single-Season Record",
        f"{int(_best_rec['wins'])}-{int(_best_rec['losses'])}",
        f"{_best_rec_mgr} · {_best_rec['team_name']} · {int(_best_rec['season'])}"), unsafe_allow_html=True)
with lf5:
    st.markdown(_lfact("Most Points in a Season", f"{_best_pf['points_for']:.1f}",
        f"{_best_pf_mgr} · {_best_pf['team_name']} · {int(_best_pf['season'])}"), unsafe_allow_html=True)
with lf6:
    st.markdown(_lfact("Highest-Scoring Season", str(_peak_season),
        f"League avg {_peak_avg:.1f} pts/team — the most explosive year on record"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── ALL-TIME MANAGER STATS ─────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">All-Time Standings</div>'
    '<div class="tl-section-title">Career Stats by Manager</div>',
    unsafe_allow_html=True,
)

ats = get_all_time_manager_stats()
ats_rows = []
for _, r in ats.iterrows():
    emoji = MANAGER_EMOJI.get(r["canonical_name"], "")
    champ_str = ("🏆 " * int(r["championships"])).strip() if r["championships"] > 0 else "—"
    best = f"#{int(r['best_finish'])}" if r.get("best_finish") and not pd.isna(r["best_finish"]) else "—"
    worst = f"#{int(r['worst_finish'])}" if r.get("worst_finish") and not pd.isna(r["worst_finish"]) else "—"
    ats_rows.append([
        f"{emoji} {r['canonical_name']}",
        (str(int(r["seasons"])), "muted"),
        f"{int(r['rs_wins'])}-{int(r['rs_losses'])}",
        (f"{r['rs_pf']:,.1f}", ""),
        (f"{r['rs_pa']:,.1f}", "muted"),
        f"{int(r['pl_wins'])}-{int(r['pl_losses'])}",
        (str(int(r["playoff_apps"])), ""),
        (str(int(r["finals_apps"])), ""),
        (champ_str, "gold"),
        (f"{best} / {worst}", "muted"),
    ])

st.markdown(
    html_table(
        ["Manager", "Seasons", "RS W-L", "RS PF", "RS PA", "PL W-L", "Playoffs", "Finals", "Titles", "Best/Worst"],
        ats_rows,
    ),
    unsafe_allow_html=True,
)

render_page_footer(
    href="/season_archive",
    cta="BROWSE THE SEASON ARCHIVE",
    tagline="RECORDS SHOW WHAT HAPPENED.<br>THE ARCHIVES SHOW HOW.",
)
