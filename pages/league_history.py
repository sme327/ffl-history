"""League History — The Evolution of the League.

Derivation lives in utils.data.get_league_history_view(); this file renders it.
"""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils.data import (
    CURRENT_SEASON, FOUNDED, MANAGER_EMOJI, get_all_time_manager_stats,
    get_league_history_view,
)
from utils.styles import inject_css, render_nav, render_page_footer, html_table

st.set_page_config(
    page_title="The Evolution of the League · The Long Game",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("league_history")

view = get_league_history_view()
scoring = view["scoring"]
balance = view["balance"]
records = view["records"]


def _why_it_matters(label: str) -> str:
    return (
        f'<div style="background:rgba(212,175,55,0.06);border-left:2px solid rgba(212,175,55,0.4);'
        f'padding:6px 10px;margin-top:8px;border-radius:0 4px 4px 0;">'
        f'<span style="font-size:0.58rem;color:#D4AF37;letter-spacing:2px;font-family:\'Inter\',sans-serif;'
        f'text-transform:uppercase;">WHY IT MATTERS</span>'
        f'<div style="font-size:0.68rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;margin-top:3px;">{label}</div>'
        f'</div>'
    )


def _fact_card(label, headline, sub, why):
    return (
        f'<div class="tl-card">'
        f'<div class="tl-section-label">{label}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{headline}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">{sub}</div>'
        f'{_why_it_matters(why)}'
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

# ── SECTION 1 — LEAGUE ERAS ────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Chapters in League History</div>'
    '<div class="tl-section-title">The Four Eras</div>'
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;'
    'margin:-0.5rem 0 1.5rem;">Every league has chapters. These are ours.</p>',
    unsafe_allow_html=True,
)

for era in view["eras"]:
    color = era["color"]
    yr_list = " · ".join(
        f"<strong style='color:{color};'>{c['season']}</strong> {c['emoji']} {c['manager']}"
        for c in era["champions"]
    )

    st.markdown(
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:6px solid {color};'
        f'border-radius:8px;padding:28px 32px;margin-bottom:20px;">'
        f'<div style="display:flex;align-items:baseline;gap:16px;flex-wrap:wrap;margin-bottom:12px;">'
        f'<span style="font-size:2rem;">{era["icon"]}</span>'
        f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:2rem;color:{color};letter-spacing:4px;">{era["name"]}</span>'
        f'<span style="font-family:\'Inter\',sans-serif;font-size:0.72rem;color:#A7B0BC;letter-spacing:2px;">{era["years"]}</span>'
        f'</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.2rem;color:#F5F5F5;letter-spacing:2px;margin-bottom:10px;">{era["headline"]}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.78rem;color:#A7B0BC;line-height:1.75;max-width:680px;margin-bottom:18px;">{era["body"]}</div>'
        f'<div style="display:flex;gap:24px;flex-wrap:wrap;margin-bottom:16px;">'
        f'<div style="text-align:center;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:{color};">{era["titles_awarded"]}</div>'
        f'<div style="font-size:0.55rem;color:#6B7280;letter-spacing:2px;text-transform:uppercase;">Titles Awarded</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:{color};">{era["unique_champions"]}</div>'
        f'<div style="font-size:0.55rem;color:#6B7280;letter-spacing:2px;text-transform:uppercase;">Unique Champions</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.8rem;color:{color};">{era["avg_score"]:.0f}</div>'
        f'<div style="font-size:0.55rem;color:#6B7280;letter-spacing:2px;text-transform:uppercase;">Avg Weekly PF</div>'
        f'</div>'
        f'</div>'
        f'<div style="font-size:0.58rem;color:#A7B0BC;letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">Champions of the Era</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#A7B0BC;line-height:1.9;">{yr_list if yr_list else "Data not yet available."}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SECTION 2 — SCORING EVOLUTION ──────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">25 Years of Weekly Scoring</div>'
    '<div class="tl-section-title">Scoring Evolution</div>',
    unsafe_allow_html=True,
)

by_season = scoring["by_season"]
seasons = [s["season"] for s in by_season]

fig = go.Figure()

# Era shading — bands come from LEAGUE_ERAS, not a second hardcoded list
for band in view["era_bands"]:
    fig.add_vrect(
        x0=band["start"] - 0.5, x1=band["end"] + 0.5,
        fillcolor=band["fill"], line_width=0,
        annotation_text=band["label"],
        annotation_position="top left",
        annotation_font=dict(size=9, color="#6B7280"),
    )

fig.add_trace(go.Scatter(
    x=seasons + seasons[::-1],
    y=[s["high"] for s in by_season] + [s["low"] for s in by_season][::-1],
    fill="toself", fillcolor="rgba(184,144,46,0.08)",
    line=dict(color="rgba(0,0,0,0)"),
    hoverinfo="skip", name="High–Low Range",
))
fig.add_trace(go.Scatter(
    x=seasons, y=[s["avg"] for s in by_season],
    mode="lines+markers",
    line=dict(color="#D4AF37", width=2.5),
    marker=dict(color="#D4AF37", size=6),
    name="League Average",
    hovertemplate="<b>%{x}</b> · Avg: %{y:.1f}<extra></extra>",
))
if scoring["champion_points"]:
    fig.add_trace(go.Scatter(
        x=[c["season"] for c in scoring["champion_points"]],
        y=[c["points_for"] for c in scoring["champion_points"]],
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

peak, lean = scoring["peak"], scoring["lean"]
se1, se2, se3 = st.columns(3)
with se1:
    st.markdown(
        f'<div class="tl-card">'
        f'<div class="tl-section-label">Peak Scoring Era</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{peak["season"]} Season</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">League average {peak["avg"]:.1f} pts — the most prolific scoring year in history.</div>'
        f'{_why_it_matters("Scoring peaks often align with rule changes or the emergence of elite offensive players in the NFL. The highest-scoring seasons tell you when the game changed.")}'
        f'</div>',
        unsafe_allow_html=True,
    )
with se2:
    st.markdown(
        f'<div class="tl-card">'
        f'<div class="tl-section-label">Lean Era</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">{lean["season"]} Season</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">League average {lean["avg"]:.1f} pts — the most defensive year on record.</div>'
        f'{_why_it_matters("Low-scoring years reward depth. The manager with the most reliable weekly floor tends to outperform the one chasing upside.")}'
        f'</div>',
        unsafe_allow_html=True,
    )
with se3:
    st.markdown(
        f'<div class="tl-card">'
        f'<div class="tl-section-label">25-Year Scoring Rise</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;color:#D4AF37;letter-spacing:2px;">+{scoring["rise"]:.1f} pts/week</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.75rem;color:#A7B0BC;margin-top:0.2rem;">Average weekly scoring increased by {scoring["rise"]:.1f} pts from the league\'s lowest to highest era.</div>'
        f'{_why_it_matters("The NFL became a scoring-first league. This league followed. Draft strategies that worked in 2004 are obsolete in 2024.")}'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SECTION 3 — COMPETITIVE BALANCE ────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Who Competed, Who Dominated</div>'
    '<div class="tl-section-title">Competitive Balance</div>',
    unsafe_allow_html=True,
)

consistent = balance["most_consistent"]
for col, val, lbl in zip(
    st.columns(4),
    [
        balance["unique_champions"],
        balance["playoff_managers_ever"],
        f'{balance["diversity_rate"]:.0%}',
        f'{consistent["appearances"] if consistent else 0}',
    ],
    [
        "Unique Champions",
        "Managers to Make Playoffs",
        "Championship Diversity Rate",
        f'Playoff Apps — {consistent["emoji"] if consistent else ""} {consistent["manager"] if consistent else "—"}',
    ],
):
    col.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{val}</div>'
        f'<div class="tl-metric-label">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

titles = balance["title_counts"]
fig_titles = go.Figure()
fig_titles.add_trace(go.Bar(
    x=[t["manager"] for t in titles],
    y=[t["titles"] for t in titles],
    marker_color="#D4AF37",
    text=[str(t["titles"]) for t in titles],
    textposition="outside",
    textfont=dict(color="#D4AF37", size=11),
    hovertemplate="<b>%{x}</b><br>%{y} title(s)<extra></extra>",
))
fig_titles.update_layout(
    paper_bgcolor="#081120", plot_bgcolor="#0F1B2D",
    font=dict(family="Inter", color="#A7B0BC", size=11),
    margin=dict(l=0, r=0, t=20, b=0), height=220,
    xaxis=dict(tickangle=-30, tickfont=dict(size=10)),
    yaxis=dict(gridcolor="rgba(184,144,46,0.12)", title="Championships"),
    showlegend=False,
)
st.plotly_chart(fig_titles, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    f'<p style="font-family:\'Inter\',sans-serif;font-size:0.68rem;color:#A7B0BC;margin-top:-0.5rem;">'
    f'The top manager holds {balance["top1_pct"]}% of all championships. '
    f'The top 3 managers account for {balance["top3_pct"]}% of titles. '
    f'{balance["unique_champions"]} different managers have won at least once across '
    f'{balance["total_seasons"]} seasons.</p>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SECTION 4 — LEAGUE FACTS ───────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Records That Define the League</div>'
    '<div class="tl-section-title">By the Numbers</div>',
    unsafe_allow_html=True,
)

wk, blow, close = records["week_high"], records["blowout"], records["closest"]
rec, pts = records["best_record"], records["best_points"]

lf1, lf2, lf3 = st.columns(3)
with lf1:
    st.markdown(_fact_card(
        "Single-Week Scoring Record",
        f'{wk["points"]:.2f} pts',
        f'{wk["manager"]} · {wk["team"]} · {wk["season"]} Wk{wk["week"]}',
        "The single highest weekly score in 25 years. Everything went right that week.",
    ), unsafe_allow_html=True)
with lf2:
    st.markdown(_fact_card(
        "Biggest Regular Season Blowout",
        f'+{blow["margin"]:.2f} pts',
        f'{blow["manager"]} · {blow["season"]} Week {blow["week"]}',
        "The most dominant single-game performance in league history. Some weeks it just isn't fair.",
    ), unsafe_allow_html=True)
with lf3:
    st.markdown(_fact_card(
        "Closest Regular Season Game",
        f'+{close["margin"]:.2f} pts',
        f'{close["manager"]} edged {close["loser"]} · {close["season"]} Week {close["week"]}',
        "Fantasy football decided by fractions. One more yard from a backup RB would have changed everything.",
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
lf4, lf5, lf6 = st.columns(3)
with lf4:
    st.markdown(_fact_card(
        "Best Single-Season Record",
        f'{rec["wins"]}-{rec["losses"]}',
        f'{rec["manager"]} · {rec["team"]} · {rec["season"]}',
        "The most dominant regular season in league history. Not necessarily the championship — but the clearest statement of excellence.",
    ), unsafe_allow_html=True)
with lf5:
    st.markdown(_fact_card(
        "Most Points in a Season",
        f'{pts["points_for"]:.1f} pts',
        f'{pts["manager"]} · {pts["team"]} · {pts["season"]}',
        "This team was on fire all season. Volume, consistency, and probably a few lucky bounces.",
    ), unsafe_allow_html=True)
with lf6:
    st.markdown(_fact_card(
        "Highest-Scoring Season",
        str(peak["season"]),
        f'League average {peak["avg"]:.1f} pts/team — the most explosive year on record',
        "This was the year the NFL's scoring explosion fully translated to fantasy. Every lineup was dangerous.",
    ), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SECTION 5 — ALL-TIME STANDINGS ─────────────────────────────────────────────
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

ats_rows = []
for _, r in get_all_time_manager_stats().iterrows():
    emoji = MANAGER_EMOJI.get(r["canonical_name"], "")
    champ_s = ("🏆 " * int(r["championships"])).strip() if r["championships"] > 0 else "—"
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
st.markdown('<div class="tl-section-label">Continue Exploring</div>', unsafe_allow_html=True)

for col, (href, icon, title, desc) in zip(st.columns(3), [
    ("/champions", "🏆", "Trophy Room", "Every championship. The dynasties that defined each era."),
    ("/league_timeline", "📅", "Timeline", "The spine of the museum. Every event, every turning point."),
    ("/season_archive", "📖", "Season Archive", "Dive into any individual season — the story, the champion, the NFL context."),
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
    href="/season_archive",
    cta="BROWSE THE SEASON ARCHIVE",
    tagline="RECORDS SHOW WHAT HAPPENED.<br>THE ARCHIVES SHOW WHY IT MATTERED.",
)
