"""Manager Profiles page — career history for every manager.

Derivation lives in utils.data.get_manager_profile(); this file renders it.
"""
from __future__ import annotations
import plotly.graph_objects as go
import streamlit as st
from utils.data import (
    get_manager_directory, get_manager_profile, manager_h2h_highlights,
)
from utils.styles import (
    avatar_html, html_table, inject_css, metric_card, render_nav, render_page_footer,
)

st.set_page_config(
    page_title="Managers · The Long Game",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("manager_profiles")

# ── PAGE TITLE ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-page-title">Manager Profiles</div>
    <div class="tl-page-subtitle">Career records for every competitor in league history.</div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

# ── MANAGER SELECTOR ───────────────────────────────────────────────────────────
directory = get_manager_directory()
selected = st.selectbox(
    "SELECT MANAGER",
    options=directory["active"] + ["─── Former Members ───"] + directory["former"],
    index=0,
    format_func=lambda n: n,
)

if selected.startswith("───"):
    st.stop()

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

profile = get_manager_profile(selected)
metrics = profile["metrics"]

# ── PROFILE HEADER ──────────────────────────────────────────────────────────────
col_avatar, col_info = st.columns([1, 4])
with col_avatar:
    st.markdown(avatar_html(profile["name"], size=100), unsafe_allow_html=True)

with col_info:
    champ_str = "🏆 " * metrics["championships"]
    st.markdown(
        f"""
        <div class="tl-profile-name">{profile['display_name']}{' ' + champ_str if champ_str else ''}</div>
        <div class="tl-profile-meta">{profile['status_label']} · {metrics['seasons_played']} Seasons</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── CAREER METRICS ─────────────────────────────────────────────────────────────
for col, value, label in zip(
    st.columns(6),
    [
        str(metrics["championships"]),
        str(metrics["runner_ups"]),
        str(metrics["playoff_apps"]),
        f'{metrics["playoff_rate"]:.0%}',
        metrics["record"],
        f'{metrics["win_pct"]:.3f}',
    ],
    ["Championships", "Runner-Up Finishes", "Playoff Appearances",
     "Playoff Rate", "Regular Season Record", "Win Percentage"],
):
    with col:
        st.markdown(metric_card(value, label), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── HALL OF FAME PLAQUE ────────────────────────────────────────────────────────
identity_html = (
    f'<div style="margin-top:10px;font-style:italic;color:#D4AF37;font-size:0.73rem;">'
    f'"{profile["identity"]}"</div>'
) if profile["identity"] else ""

st.markdown(
    f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:5px solid {profile["color"]};'
    f'border-radius:6px;padding:20px 24px;margin-bottom:0;">'
    f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.68rem;color:#A7B0BC;'
    f'letter-spacing:4px;margin-bottom:8px;">HALL OF FAME PLAQUE</div>'
    f'<div style="font-family:\'Inter\',sans-serif;font-size:0.82rem;color:#F5F5F5;'
    f'line-height:1.75;">{profile["plaque"]}</div>'
    f'{identity_html}'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PERFORMANCE CHART ─────────────────────────────────────────────────────────
seasons = profile["seasons"]

if len(seasons) > 1:
    ordered = sorted(seasons, key=lambda s: s["season"])
    years = [s["season"] for s in ordered]

    st.markdown(
        '<div class="tl-section-label">Performance Over Time</div>'
        '<div class="tl-section-title">Season Trends</div>',
        unsafe_allow_html=True,
    )
    metric_choice = st.radio(
        "Chart metric",
        ["Win %", "Points For", "Season Finish"],
        horizontal=True,
        label_visibility="collapsed",
    )

    fig = go.Figure()

    if metric_choice == "Season Finish":
        marker_styles = {
            "Champion": dict(mode="text", text="🏆", size=20),
            "Runner-Up": dict(mode="text", text="🥈", size=18),
            "3rd / 4th": dict(mode="text", text="🥉", size=16),
        }
        for category in ["Champion", "Runner-Up", "3rd / 4th", "Playoffs", "Missed"]:
            subset = [s for s in ordered if s["category"] == category]
            if not subset:
                continue
            x = [s["season"] for s in subset]
            y = [s["rank"] for s in subset]
            if category in marker_styles:
                style = marker_styles[category]
                fig.add_trace(go.Scatter(
                    x=x, y=y, mode="text", text=[style["text"]] * len(subset),
                    textfont=dict(size=style["size"]), name=category,
                    customdata=[s["result"] for s in subset],
                    hovertemplate="<b>%{x}</b> · %{customdata}<extra></extra>",
                ))
            elif category == "Playoffs":
                fig.add_trace(go.Scatter(
                    x=x, y=y, mode="markers",
                    marker=dict(color="#4A90D9", size=10, line=dict(color="#081120", width=1.5)),
                    name=category,
                    customdata=[s["result"] for s in subset],
                    hovertemplate="<b>%{x}</b> · %{customdata}<extra></extra>",
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=x, y=y, mode="markers",
                    marker=dict(symbol="x", color="rgba(220,50,50,0.85)", size=12,
                                line=dict(color="rgba(220,50,50,0.85)", width=2.5)),
                    name="Missed Playoffs",
                    hovertemplate="<b>%{x}</b> · Missed Playoffs<extra></extra>",
                ))
        fig.update_layout(
            yaxis=dict(
                autorange="reversed", showgrid=True, gridcolor="rgba(184,144,46,0.12)",
                zeroline=False, tickfont=dict(color="#A7B0BC"), dtick=1,
                title=dict(text="Finish", font=dict(color="#A7B0BC", size=10)),
            ),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A7B0BC")),
            hovermode="closest", showlegend=True,
            legend=dict(orientation="h", x=0, y=1.18,
                        font=dict(size=9, color="#A7B0BC"), bgcolor="rgba(0,0,0,0)"),
        )
    elif metric_choice == "Win %":
        fig.add_trace(go.Scatter(
            x=years, y=[s["win_pct"] for s in ordered],
            mode="lines+markers",
            line=dict(color="#D4AF37", width=2),
            marker=dict(color="#D4AF37", size=7),
            fill="tozeroy", fillcolor="rgba(212,175,55,0.06)",
            hovertemplate="<b>%{x}</b><br>Win %: %{y:.3f}<extra></extra>",
        ))
        fig.add_hline(y=0.5, line_dash="dot", line_color="#A7B0BC", opacity=0.4)
        fig.update_layout(yaxis=dict(range=[0, 1], showgrid=True, gridcolor="rgba(184,144,46,0.12)",
                                     zeroline=False, tickfont=dict(color="#A7B0BC")),
                          xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A7B0BC")),
                          showlegend=False)
    else:  # Points For
        fig.add_trace(go.Scatter(
            x=years, y=[s["points_for"] for s in ordered],
            mode="lines+markers",
            line=dict(color="#D4AF37", width=2), marker=dict(color="#D4AF37", size=7),
            name="Points For",
            hovertemplate="<b>%{x}</b><br>PF: %{y:.2f}<extra></extra>",
        ))
        if any(s["points_against"] is not None for s in ordered):
            fig.add_trace(go.Scatter(
                x=years, y=[s["points_against"] for s in ordered],
                mode="lines+markers",
                line=dict(color="#4A90D9", width=1.5, dash="dot"),
                marker=dict(color="#4A90D9", size=6),
                name="Points Against",
                hovertemplate="<b>%{x}</b><br>PA: %{y:.2f}<extra></extra>",
            ))
        fig.update_layout(yaxis=dict(showgrid=True, gridcolor="rgba(184,144,46,0.12)",
                                     zeroline=False, tickfont=dict(color="#A7B0BC")),
                          xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A7B0BC")),
                          showlegend=True,
                          legend=dict(orientation="h", x=0, y=1.15,
                                      font=dict(size=9, color="#A7B0BC"), bgcolor="rgba(0,0,0,0)"))

    fig.update_layout(
        paper_bgcolor="#081120", plot_bgcolor="#0F1B2D",
        font=dict(family="Inter", color="#A7B0BC", size=11),
        margin=dict(l=0, r=0, t=10, b=0), height=240,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── HEAD TO HEAD ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Rivalries</div>'
    '<div class="tl-section-title">Head to Head</div>',
    unsafe_allow_html=True,
)

h2h = profile["head_to_head"]
if h2h:
    scope = st.radio(
        "Show rivalries against",
        ["Current Members", "All-Time"],
        horizontal=True,
        label_visibility="collapsed",
    )
    scoped = [r for r in h2h if r["opp_active"]] if scope == "Current Members" else h2h

    if not scoped:
        st.markdown('<p style="color:#A7B0BC;font-size:0.8rem;">No matchups found for this scope.</p>',
                    unsafe_allow_html=True)
    else:
        highlights = manager_h2h_highlights(scoped)

        def _rival_card(label, entry, with_pct: bool) -> str:
            detail = (
                f'{entry["wins"]}-{entry["losses"]} · {entry["win_pct"]:.0%} win rate' if with_pct
                else f'{entry["wins"]}-{entry["losses"]} in {entry["games"]} games'
            )
            return f"""<div class="tl-card">
                <div class="tl-section-label">{label}</div>
                <div style="font-size:2rem;">{entry['opp_emoji']}</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#D4AF37;letter-spacing:2px;">{entry['opp_manager']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#A7B0BC;">{detail}</div>
                </div>"""

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(_rival_card("Most Played", highlights["most_played"], False), unsafe_allow_html=True)
        with rc2:
            if highlights["victim"]:
                st.markdown(_rival_card("Favorite Victim", highlights["victim"], True), unsafe_allow_html=True)
        with rc3:
            if highlights["nemesis"]:
                st.markdown(_rival_card("Toughest Opponent", highlights["nemesis"], True), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            html_table(
                ["Opponent", "GP", "W-L", "Win%", "PF", "PA"],
                [
                    [
                        f'{r["opp_emoji"]} {r["opp_manager"]}',
                        (str(r["games"]), "muted"),
                        (f'{r["wins"]}-{r["losses"]}', "gold"),
                        (f'{r["win_pct"]:.0%}', ""),
                        (f'{r["pf"]:,.1f}', ""),
                        (f'{r["pa"]:,.1f}', "muted"),
                    ]
                    for r in scoped
                ],
            ),
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── DRAFT IDENTITY ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Draft Profile</div>'
    '<div class="tl-section-title">Draft Identity</div>',
    unsafe_allow_html=True,
)

POSITION_COLORS = {"RB": "#22C55E", "WR": "#3B82F6", "QB": "#EF4444",
                   "TE": "#F59E0B", "DEF": "#8B5CF6", "K": "#6B7280"}
draft = profile["draft"]

if draft:
    counts, total = draft["round_one_counts"], draft["round_one_total"]
    left, right = st.columns([2, 1])

    with left:
        bars = ""
        legend = ""
        for pos in ["RB", "WR", "QB", "TE", "DEF", "K"]:
            count = counts.get(pos, 0)
            if not count or not total:
                continue
            pct = count / total * 100
            bars += (
                f'<div style="width:{pct}%;background:{POSITION_COLORS[pos]};'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:0.6rem;font-weight:700;color:#000;" title="{pos} {pct:.0f}%">'
                f'{"" if pct < 10 else pos}</div>'
            )
            legend += (
                f'<span style="font-size:0.62rem;font-family:\'Inter\',sans-serif;'
                f'color:{POSITION_COLORS[pos]};">{pos}: {pct:.0f}% ({count})</span>'
            )
        st.markdown(
            '<div style="margin-bottom:1rem;">'
            '<div style="font-size:0.65rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;margin-bottom:6px;">ROUND 1 PICK BREAKDOWN</div>'
            f'<div style="display:flex;height:18px;border-radius:4px;overflow:hidden;width:100%;">{bars}</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;">{legend}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-top:3px solid {profile["color"]};'
            f'border-radius:6px;padding:12px 14px;">'
            f'<div style="font-size:0.6rem;color:{draft["style_color"]};font-family:\'Inter\',sans-serif;'
            f'font-weight:700;letter-spacing:2px;margin-bottom:8px;">{draft["style"]}</div>'
            f'<div style="font-size:0.67rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;'
            f'margin-bottom:3px;">Most drafted: <span style="color:#F5F5F5;font-weight:600;">'
            f'{draft["most_drafted"]["player"]} ({draft["most_drafted"]["count"]}×)</span></div>'
            f'<div style="font-size:0.67rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;'
            f'margin-bottom:3px;">Most kept: <span style="color:#D4AF37;font-weight:600;">'
            f'{draft["most_kept"]["player"]} ({draft["most_kept"]["count"]}×)</span></div>'
            f'<div style="font-size:0.67rem;color:#A7B0BC;font-family:\'Inter\',sans-serif;">'
            f'Keeper rate: <span style="color:#F5F5F5;font-weight:600;">{draft["keeper_rate"]*100:.1f}%</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<p style="color:#A7B0BC;font-size:0.75rem;font-family:\'Inter\',sans-serif;">'
        'No draft data available for this manager.</p>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div style="margin-top:0.75rem;">'
    '<a href="/draft_center" target="_self" style="font-family:\'Inter\',sans-serif;font-size:0.65rem;'
    'color:#D4AF37;letter-spacing:3px;text-transform:uppercase;text-decoration:none;'
    'border-bottom:1px solid rgba(212,175,55,0.5);padding-bottom:2px;">'
    'FULL DRAFT PROFILE IN DRAFT CENTER →</a></div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SEASON-BY-SEASON TABLE ─────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Career History</div>'
    '<div class="tl-section-title">Season by Season</div>',
    unsafe_allow_html=True,
)

st.markdown(
    html_table(
        ["Season", "Team Name", "Record", "Points For", "Final Rank", "Result"],
        [
            [
                (str(s["season"]), "gold"),
                s["team_name"],
                f'{s["wins"]}-{s["losses"]}' + (f'-{s["ties"]}' if s["ties"] else ""),
                (f'{s["points_for"]:.2f}', ""),
                (f'#{s["rank"]}' if s["rank"] else "—", "muted"),
                (s["result"], "gold" if "Champion" in s["result"] else ("muted" if s["result"] == "—" else "")),
            ]
            for s in seasons
        ],
    ),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── TEAM NAME HISTORY ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Identity</div>'
    '<div class="tl-section-title">Team Name History</div>',
    unsafe_allow_html=True,
)

_, col, _ = st.columns([1, 2, 1])
with col:
    st.markdown(
        html_table(
            ["Years", "Team Name"],
            [[(run["years"], "gold"), run["team_name"]] for run in profile["team_names"]],
        ),
        unsafe_allow_html=True,
    )

st.markdown('<div class="tl-section-label">Continue Exploring</div>', unsafe_allow_html=True)

for col, (href, icon, title, desc) in zip(st.columns(3), [
    ("/franchise_profiles", "🏟️", "Franchise History", "The franchise this manager stewards — who built it before them, and where it goes next."),
    ("/draft_center", "📋", "Draft Identity", "Full draft DNA, player loyalties, and archetype breakdown in the Draft Center."),
    ("/champions", "🏆", "Trophy Room", "The full championship record — who's won, who's been close, and who's still waiting."),
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
    href="/franchise_profiles",
    cta="EXPLORE THE FRANCHISES",
    tagline="MANAGERS COME AND GO.<br>THE FRANCHISES ENDURE.",
)
