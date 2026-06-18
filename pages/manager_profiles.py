"""Manager Profiles page — career history for every manager."""
import streamlit as st
import plotly.graph_objects as go
from utils.data import (
    load_all, get_manager_stats, get_manager_season_history,
    get_manager_h2h, get_champions, MANAGER_EMOJI, CURRENT_SEASON,
)
from utils.styles import inject_css, render_nav, avatar_html, metric_card, html_table

st.set_page_config(
    page_title="Managers · The Long Game",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("manager_profiles")

data = load_all()
manager_stats = get_manager_stats()
champions = get_champions()

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
active = manager_stats[manager_stats["active"]]["canonical_name"].tolist()
former = manager_stats[~manager_stats["active"]]["canonical_name"].tolist()

all_options = active + ["─── Former Members ───"] + former
selected = st.selectbox(
    "SELECT MANAGER",
    options=all_options,
    index=0,
    format_func=lambda n: n,
)

if selected.startswith("───"):
    st.stop()

mgr_name = selected
st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PROFILE HEADER ──────────────────────────────────────────────────────────────
mgr_row = manager_stats[manager_stats["canonical_name"] == mgr_name].iloc[0]
emoji = MANAGER_EMOJI.get(mgr_name, "👤")
is_active = bool(mgr_row["active"])
status_label = f"Active · {mgr_row['first_season']}–Present" if is_active else f"{mgr_row['first_season']}–{mgr_row['last_season']}"

col_avatar, col_info = st.columns([1, 4])
with col_avatar:
    st.markdown(avatar_html(mgr_name, size=100), unsafe_allow_html=True)

with col_info:
    champ_str = "🏆 " * int(mgr_row["championships"]) if mgr_row["championships"] > 0 else ""
    st.markdown(
        f"""
        <div class="tl-profile-name">{mgr_row['display_name']}{' ' + champ_str if champ_str else ''}</div>
        <div class="tl-profile-meta">{status_label} · {int(mgr_row['seasons_played'])} Seasons</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── CAREER METRICS ─────────────────────────────────────────────────────────────
w, l, t = int(mgr_row["wins"]), int(mgr_row["losses"]), int(mgr_row["ties"])
total = w + l + t
win_pct = f"{mgr_row['win_pct']:.3f}" if total > 0 else ".000"
record_str = f"{w}-{l}" + (f"-{t}" if t > 0 else "")

seasons_played = int(mgr_row["seasons_played"])
playoff_apps = int(mgr_row["playoff_apps"])
playoff_rate = f"{playoff_apps/seasons_played:.0%}" if seasons_played > 0 else "0%"

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.markdown(metric_card(str(int(mgr_row["championships"])), "Championships"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card(str(int(mgr_row["runner_ups"])), "Runner-Up Finishes"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card(str(playoff_apps), "Playoff Appearances"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card(playoff_rate, "Playoff Rate"), unsafe_allow_html=True)
with c5:
    st.markdown(metric_card(record_str, "Regular Season Record"), unsafe_allow_html=True)
with c6:
    st.markdown(metric_card(win_pct, "Win Percentage"), unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── PERFORMANCE CHART ─────────────────────────────────────────────────────────
history = get_manager_season_history(mgr_name)

if len(history) > 1:
    history_chart = history.copy().sort_values("Season")
    history_chart["total"] = history_chart["W"] + history_chart["L"] + history_chart["T"]
    history_chart["win_pct"] = (history_chart["W"] / history_chart["total"].replace(0, float("nan"))).round(3)

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

    if metric_choice == "Season Finish":
        def result_cat(r):
            r = str(r)
            if "Champion" in r: return "Champion"
            if "Runner-Up" in r: return "Runner-Up"
            if "3rd" in r or "4th" in r: return "3rd / 4th"
            if r != "—": return "Playoffs"
            return "Missed"

        history_chart["cat"] = history_chart["Result"].apply(result_cat)

        fig = go.Figure()
        for cat in ["Champion", "Runner-Up", "3rd / 4th", "Playoffs", "Missed"]:
            sub = history_chart[history_chart["cat"] == cat]
            if len(sub) == 0:
                continue
            if cat == "Champion":
                fig.add_trace(go.Scatter(
                    x=sub["Season"].tolist(), y=sub["Rank"].tolist(),
                    mode="text", text=["🏆"] * len(sub),
                    textfont=dict(size=20), name=cat,
                    hovertemplate="<b>%{x}</b> · 🏆 Champion<extra></extra>",
                ))
            elif cat == "Runner-Up":
                fig.add_trace(go.Scatter(
                    x=sub["Season"].tolist(), y=sub["Rank"].tolist(),
                    mode="text", text=["🥈"] * len(sub),
                    textfont=dict(size=18), name=cat,
                    hovertemplate="<b>%{x}</b> · 🥈 Runner-Up<extra></extra>",
                ))
            elif cat == "3rd / 4th":
                fig.add_trace(go.Scatter(
                    x=sub["Season"].tolist(), y=sub["Rank"].tolist(),
                    mode="text", text=["🥉"] * len(sub),
                    textfont=dict(size=16), name=cat,
                    customdata=sub["Result"].tolist(),
                    hovertemplate="<b>%{x}</b> · %{customdata}<extra></extra>",
                ))
            elif cat == "Playoffs":
                fig.add_trace(go.Scatter(
                    x=sub["Season"].tolist(), y=sub["Rank"].tolist(),
                    mode="markers",
                    marker=dict(color="#4A90D9", size=10, line=dict(color="#081120", width=1.5)),
                    name=cat,
                    customdata=sub["Result"].tolist(),
                    hovertemplate="<b>%{x}</b> · %{customdata}<extra></extra>",
                ))
            else:  # Missed
                fig.add_trace(go.Scatter(
                    x=sub["Season"].tolist(), y=sub["Rank"].tolist(),
                    mode="markers",
                    marker=dict(symbol="x", color="rgba(220,50,50,0.85)", size=12,
                                line=dict(color="rgba(220,50,50,0.85)", width=2.5)),
                    name="Missed Playoffs",
                    hovertemplate="<b>%{x}</b> · Missed Playoffs<extra></extra>",
                ))
        fig.update_layout(
            paper_bgcolor="#081120",
            plot_bgcolor="#0F1B2D",
            font=dict(family="Inter", color="#A7B0BC", size=11),
            margin=dict(l=0, r=0, t=10, b=0),
            height=240,
            yaxis=dict(
                autorange="reversed",
                showgrid=True, gridcolor="rgba(184,144,46,0.12)",
                zeroline=False, tickfont=dict(color="#A7B0BC"), dtick=1,
                title=dict(text="Finish", font=dict(color="#A7B0BC", size=10)),
            ),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A7B0BC")),
            hovermode="closest",
            showlegend=True,
            legend=dict(
                orientation="h", x=0, y=1.18,
                font=dict(size=9, color="#A7B0BC"),
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    else:
        fig = go.Figure()
        if metric_choice == "Win %":
            fig.add_trace(go.Scatter(
                x=history_chart["Season"],
                y=history_chart["win_pct"],
                mode="lines+markers",
                line=dict(color="#D4AF37", width=2),
                marker=dict(color="#D4AF37", size=7),
                fill="tozeroy",
                fillcolor="rgba(212,175,55,0.06)",
                hovertemplate="<b>%{x}</b><br>Win %: %{y:.3f}<extra></extra>",
            ))
            fig.add_hline(y=0.5, line_dash="dot", line_color="#A7B0BC", opacity=0.4)
            y_range, show_legend = [0, 1], False
        else:  # Points For / Against
            fig.add_trace(go.Scatter(
                x=history_chart["Season"].tolist(),
                y=history_chart["PF"].tolist(),
                mode="lines+markers",
                line=dict(color="#D4AF37", width=2),
                marker=dict(color="#D4AF37", size=7),
                name="Points For",
                hovertemplate="<b>%{x}</b><br>PF: %{y:.2f}<extra></extra>",
            ))
            if "PA" in history_chart.columns:
                fig.add_trace(go.Scatter(
                    x=history_chart["Season"].tolist(),
                    y=history_chart["PA"].tolist(),
                    mode="lines+markers",
                    line=dict(color="#4A90D9", width=1.5, dash="dot"),
                    marker=dict(color="#4A90D9", size=6),
                    name="Points Against",
                    hovertemplate="<b>%{x}</b><br>PA: %{y:.2f}<extra></extra>",
                ))
            y_range, show_legend = None, True
        fig.update_layout(
            paper_bgcolor="#081120",
            plot_bgcolor="#0F1B2D",
            font=dict(family="Inter", color="#A7B0BC", size=11),
            margin=dict(l=0, r=0, t=10, b=0),
            height=200,
            showlegend=show_legend,
            legend=dict(orientation="h", x=0, y=1.15, font=dict(size=9, color="#A7B0BC"), bgcolor="rgba(0,0,0,0)"),
            yaxis=dict(
                showgrid=True, gridcolor="rgba(184,144,46,0.12)",
                zeroline=False, tickfont=dict(color="#A7B0BC"),
                range=y_range if y_range else None,
            ),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color="#A7B0BC")),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── RIVALRIES ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Head-to-Head</div>'
    '<div class="tl-section-title">Rivalries</div>',
    unsafe_allow_html=True,
)

h2h = get_manager_h2h(mgr_name)

if len(h2h) > 0:
    active_mgrs = set(manager_stats[manager_stats["active"]]["canonical_name"].tolist())

    scope = st.radio(
        "Show rivalries against",
        ["Current Members", "All-Time"],
        horizontal=True,
        label_visibility="collapsed",
    )
    h2h_view = h2h[h2h["opp_manager"].isin(active_mgrs)] if scope == "Current Members" else h2h
    h2h_view = h2h_view.reset_index(drop=True)

    if len(h2h_view) == 0:
        st.markdown('<p style="color:#A7B0BC;font-size:0.8rem;">No matchups found for this scope.</p>', unsafe_allow_html=True)
    else:
        # Most-played rival
        most_played = h2h_view.iloc[0]
        mp_emoji = MANAGER_EMOJI.get(most_played["opp_manager"], "👤")

        # Favorite victim / toughest opponent — min 5 games
        eligible = h2h_view[h2h_view["games"] >= 5]
        if len(eligible) > 0:
            victim = eligible.sort_values("win_pct", ascending=False).iloc[0]
            v_emoji = MANAGER_EMOJI.get(victim["opp_manager"], "👤")
            nemesis = eligible.sort_values("win_pct").iloc[0]
            n_emoji = MANAGER_EMOJI.get(nemesis["opp_manager"], "👤")
        else:
            victim = nemesis = None

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(
                f"""<div class="tl-card">
                <div class="tl-section-label">Most Played</div>
                <div style="font-size:2rem;">{mp_emoji}</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#D4AF37;letter-spacing:2px;">{most_played['opp_manager']}</div>
                <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#A7B0BC;">{int(most_played['wins'])}-{int(most_played['losses'])} in {int(most_played['games'])} games</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with rc2:
            if victim is not None:
                st.markdown(
                    f"""<div class="tl-card">
                    <div class="tl-section-label">Favorite Victim</div>
                    <div style="font-size:2rem;">{v_emoji}</div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#D4AF37;letter-spacing:2px;">{victim['opp_manager']}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#A7B0BC;">{int(victim['wins'])}-{int(victim['losses'])} · {victim['win_pct']:.0%} win rate</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        with rc3:
            if nemesis is not None:
                st.markdown(
                    f"""<div class="tl-card">
                    <div class="tl-section-label">Toughest Opponent</div>
                    <div style="font-size:2rem;">{n_emoji}</div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#D4AF37;letter-spacing:2px;">{nemesis['opp_manager']}</div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#A7B0BC;">{int(nemesis['wins'])}-{int(nemesis['losses'])} · {nemesis['win_pct']:.0%} win rate</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # Full H2H table (scoped)
        h2h_rows = []
        for _, r in h2h_view.iterrows():
            opp_emoji = MANAGER_EMOJI.get(r["opp_manager"], "")
            h2h_rows.append([
                f"{opp_emoji} {r['opp_manager']}",
                (str(int(r["games"])), "muted"),
                (f"{int(r['wins'])}-{int(r['losses'])}", "gold"),
                (f"{r['win_pct']:.0%}", ""),
                (f"{r['pf']:,.1f}", ""),
                (f"{r['pa']:,.1f}", "muted"),
            ])
        st.markdown(
            html_table(["Opponent", "GP", "W-L", "Win%", "PF", "PA"], h2h_rows),
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── SEASON-BY-SEASON TABLE ─────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Career History</div>'
    '<div class="tl-section-title">Season by Season</div>',
    unsafe_allow_html=True,
)

table_rows = []
for _, row in history.iterrows():
    rank_str = f"#{int(row['Rank'])}" if row["Rank"] else "—"
    result = str(row["Result"])
    result_class = "gold" if "Champion" in result else ("muted" if result == "—" else "")
    table_rows.append([
        (str(int(row["Season"])), "gold"),
        row["Team Name"],
        f"{int(row['W'])}-{int(row['L'])}" + (f"-{int(row['T'])}" if row["T"] else ""),
        (f"{row['PF']:.2f}", ""),
        (rank_str, "muted"),
        (result, result_class),
    ])

st.markdown(
    html_table(["Season", "Team Name", "Record", "Points For", "Final Rank", "Result"], table_rows),
    unsafe_allow_html=True,
)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ── TEAM NAME HISTORY ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="tl-section-label">Identity</div>'
    '<div class="tl-section-title">Team Name History</div>',
    unsafe_allow_html=True,
)

tnh = data["team_name_history"]
name_hist = tnh[tnh["canonical_name"] == mgr_name].sort_values("season")

# Group consecutive identical names
runs = []
prev_name = None
start = None
prev_season = None
for _, row in name_hist.iterrows():
    if row["team_name"] != prev_name:
        if prev_name is not None:
            runs.append((prev_name, start, prev_season))
        prev_name = row["team_name"]
        start = row["season"]
    prev_season = row["season"]
if prev_name:
    runs.append((prev_name, start, prev_season))

name_rows = []
for team_name, s_start, s_end in runs:
    yr = f"{s_start}" if s_start == s_end else f"{s_start}–{s_end}"
    name_rows.append([(yr, "gold"), team_name])

_, col, _ = st.columns([1, 2, 1])
with col:
    st.markdown(html_table(["Years", "Team Name"], name_rows), unsafe_allow_html=True)
