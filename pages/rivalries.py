"""Rivalries — the emotional center of 25 years of competition."""
from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data import (
    get_all_rivalries,
    get_h2h_detail,
    get_franchise_rivalries,
    get_playoff_eliminations,
    get_champions,
    load_all,
    MANAGER_COLORS,
    MANAGER_EMOJI,
    CURRENT_SEASON,
    FOUNDED,
)
from utils.styles import inject_css, render_nav, render_page_footer
from utils.narratives import RIVALRY_PLAQUES

st.set_page_config(
    page_title="Rivalries · The Long Game",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()
render_nav("rivalries")

# ── DATA ─────────────────────────────────────────────────────────────────────
all_rivalries = get_all_rivalries()
elim_df = get_playoff_eliminations()
champs = get_champions()
fran_rivalries = get_franchise_rivalries()
data_raw = load_all()
tnh = data_raw["team_name_history"]
pg = data_raw["playoff_games"]
mgr_lu = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
champ_pg = pg[pg["bracket"] == "championship"].copy()

# All managers who have appeared in rivalry data
all_mgrs = sorted(set(all_rivalries["mgr_a"].tolist() + all_rivalries["mgr_b"].tolist()))

# Finals data for championship section
finals = champ_pg[champ_pg["game_type"] == "final"].copy()
finals["winner_mgr"] = finals.apply(lambda r: mgr_lu.get((r["season"], r["winner"])), axis=1)
finals["loser_team"] = finals.apply(
    lambda r: r["team_2"] if r["winner"] == r["team_1"] else r["team_1"], axis=1
)
finals["loser_mgr"] = finals.apply(
    lambda r: mgr_lu.get((r["season"], r["loser_team"])), axis=1
)
finals["margin"] = (finals["score_1"] - finals["score_2"]).abs()
finals["win_score"] = finals.apply(
    lambda r: float(r["score_1"]) if r["winner"] == r["team_1"] else float(r["score_2"]), axis=1
)
finals["loss_score"] = finals.apply(
    lambda r: float(r["score_2"]) if r["winner"] == r["team_1"] else float(r["score_1"]), axis=1
)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def _color(mgr: str) -> str:
    return MANAGER_COLORS.get(mgr, "#6B7280")


def _emoji(mgr: str) -> str:
    return MANAGER_EMOJI.get(mgr, "👤")


def _plaque(mgr_a: str, mgr_b: str) -> str:
    key = tuple(sorted([mgr_a, mgr_b]))
    return RIVALRY_PLAQUES.get(key, "")


def _win_label(wins: int, losses: int, mgr_a: str, mgr_b: str) -> str:
    if wins > losses:
        return mgr_a
    if losses > wins:
        return mgr_b
    return "Even"


def _record_label(a_wins: int, b_wins: int) -> str:
    return f"{a_wins}–{b_wins}"


def _pct_bar(pct: float, color_a: str, color_b: str, height: int = 8) -> str:
    pct_a = round(pct * 100, 1)
    pct_b = round(100 - pct_a, 1)
    return (
        f'<div style="display:flex;border-radius:4px;overflow:hidden;height:{height}px;margin:6px 0;">'
        f'<div style="width:{pct_a}%;background:{color_a};"></div>'
        f'<div style="width:{pct_b}%;background:{color_b};"></div>'
        f'</div>'
    )


def _rivalry_card(row, rank: int | None = None) -> str:
    mgr_a = row["mgr_a"]
    mgr_b = row["mgr_b"]
    col_a = _color(mgr_a)
    col_b = _color(mgr_b)
    score = int(row["rivalry_score"])
    rs_games = int(row["rs_games"])
    rs_a = int(row["rs_a_wins"])
    rs_b = int(row["rs_b_wins"])
    pl_games = int(row["pl_games"])
    final_games = int(row["final_games"])
    a_pct = float(row["rs_a_pct"])
    plaque = _plaque(mgr_a, mgr_b)
    plaque_html = (
        f'<div style="font-size:0.72rem;color:#CBD5E1;font-style:italic;'
        f'margin-top:10px;line-height:1.5;border-left:3px solid #374151;padding-left:10px;">'
        f'{plaque}</div>'
    ) if plaque else ""

    rank_html = (
        f'<div style="font-size:0.6rem;font-weight:800;letter-spacing:3px;'
        f'color:#D4AF37;text-transform:uppercase;margin-bottom:4px;">#{rank}</div>'
    ) if rank is not None else ""

    pl_badge = (
        f'<span style="font-size:0.6rem;background:rgba(251,146,60,0.15);color:#FB923C;'
        f'padding:2px 7px;border-radius:3px;border:1px solid rgba(251,146,60,0.3);">'
        f'{pl_games} PLAYOFF MTG{"S" if pl_games != 1 else ""}</span>'
    ) if pl_games else ""

    final_badge = (
        f'<span style="font-size:0.6rem;background:rgba(212,175,55,0.15);color:#D4AF37;'
        f'padding:2px 7px;border-radius:3px;border:1px solid rgba(212,175,55,0.3);">'
        f'{final_games} TITLE GAME{"S" if final_games != 1 else ""}</span>'
    ) if final_games else ""

    score_color = "#D4AF37" if score >= 80 else "#34D399" if score >= 60 else "#60A5FA"

    return f"""
    <div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:10px;
        padding:20px;height:100%;box-sizing:border-box;">
        {rank_html}
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
            <div>
                <div style="font-family:'Playfair Display',serif;font-size:1rem;
                    font-weight:700;color:#E2E8F0;line-height:1.3;">
                    <span style="color:{col_a};">{_emoji(mgr_a)} {mgr_a}</span>
                    <span style="color:#6B7280;font-size:0.7rem;margin:0 6px;">VS</span>
                    <span style="color:{col_b};">{_emoji(mgr_b)} {mgr_b}</span>
                </div>
            </div>
            <div style="text-align:right;flex-shrink:0;margin-left:8px;">
                <div style="font-size:1.6rem;font-weight:800;color:{score_color};line-height:1;">{score}</div>
                <div style="font-size:0.5rem;letter-spacing:2px;color:#6B7280;">RIVALRY SCORE</div>
            </div>
        </div>
        {_pct_bar(a_pct, col_a, col_b)}
        <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#94A3B8;margin-bottom:10px;">
            <span><b style="color:{col_a};">{rs_a}</b> wins</span>
            <span style="color:#6B7280;">{rs_games} RS meetings</span>
            <span><b style="color:{col_b};">{rs_b}</b> wins</span>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">
            {pl_badge}{final_badge}
        </div>
        {plaque_html}
    </div>
    """


def _pain_entry(icon: str, title: str, detail: str, why: str = "", color: str = "#EF4444") -> str:
    why_html = (
        f'<div style="margin-top:8px;font-size:0.68rem;color:#D4AF37;'
        f'border-left:2px solid #D4AF37;padding-left:8px;">'
        f'<strong>WHY IT MATTERS:</strong> {why}</div>'
    ) if why else ""
    return f"""
    <div style="background:#0F1B2D;border-left:4px solid {color};border-radius:0 8px 8px 0;
        padding:16px;margin-bottom:12px;">
        <div style="display:flex;gap:12px;align-items:flex-start;">
            <div style="font-size:1.5rem;flex-shrink:0;">{icon}</div>
            <div>
                <div style="font-size:0.65rem;font-weight:700;letter-spacing:2px;
                    color:{color};text-transform:uppercase;margin-bottom:3px;">{title}</div>
                <div style="font-size:0.9rem;color:#E2E8F0;font-weight:500;">{detail}</div>
                {why_html}
            </div>
        </div>
    </div>
    """


# ── HERO ─────────────────────────────────────────────────────────────────────
total_pairs = len(all_rivalries[all_rivalries["rs_games"] >= 5])
most_played_row = all_rivalries.iloc[
    all_rivalries["rs_games"].argmax()
]
closest_row = all_rivalries[all_rivalries["rs_games"] >= 10].copy()
closest_row = closest_row.iloc[closest_row["balance"].argmax()]
most_pl_row = all_rivalries.iloc[all_rivalries["pl_games"].argmax()]
most_lopsided = all_rivalries[all_rivalries["rs_games"] >= 15].copy()
most_lopsided["lopsidedness"] = (most_lopsided["rs_a_pct"] - 0.5).abs()
most_lopsided_row = most_lopsided.iloc[most_lopsided["lopsidedness"].argmax()]

_mp_a = most_played_row["mgr_a"]
_mp_b = most_played_row["mgr_b"]
_cl_a = closest_row["mgr_a"]
_cl_b = closest_row["mgr_b"]
_pl_a = most_pl_row["mgr_a"]
_pl_b = most_pl_row["mgr_b"]
_lo_a = most_lopsided_row["mgr_a"]
_lo_b = most_lopsided_row["mgr_b"]
_lo_wins = int(max(most_lopsided_row["rs_a_wins"], most_lopsided_row["rs_b_wins"]))
_lo_losses = int(min(most_lopsided_row["rs_a_wins"], most_lopsided_row["rs_b_wins"]))
_lo_dom = _lo_a if most_lopsided_row["rs_a_wins"] > most_lopsided_row["rs_b_wins"] else _lo_b
_lo_vic = _lo_b if most_lopsided_row["rs_a_wins"] > most_lopsided_row["rs_b_wins"] else _lo_a

st.markdown(
    f"""
    <div style="text-align:center;padding:3rem 0 2rem;">
        <div class="tl-page-title" style="font-size:clamp(2.5rem,6vw,4rem);">RIVALRIES</div>
        <div style="font-family:'Inter',sans-serif;font-size:clamp(0.85rem,2vw,1.05rem);
            color:#94A3B8;max-width:560px;margin:1rem auto 0;line-height:1.7;">
            Some managers chase championships.<br>
            Others chase each other.
        </div>
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

h1, h2, h3, h4, h5 = st.columns(5)
_stat = lambda v, l: f'<div class="tl-metric"><div class="tl-metric-value">{v}</div><div class="tl-metric-label">{l}</div></div>'
with h1:
    st.markdown(_stat(total_pairs, "Active Rivalries"), unsafe_allow_html=True)
with h2:
    st.markdown(
        _stat(f"{_mp_a} vs {_mp_b}", f"Most Played · {int(most_played_row['rs_games'])} games"),
        unsafe_allow_html=True,
    )
with h3:
    st.markdown(
        _stat(f"{_cl_a} vs {_cl_b}", "Closest Series (RS)"),
        unsafe_allow_html=True,
    )
with h4:
    st.markdown(
        _stat(f"{_pl_a} vs {_pl_b}", f"Most Playoff Meetings · {int(most_pl_row['pl_games'])}"),
        unsafe_allow_html=True,
    )
with h5:
    st.markdown(
        _stat(f"{_lo_dom} {_lo_wins}–{_lo_losses}", f"Most One-Sided vs {_lo_vic}"),
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)


# ── SECTION 1: TOP RIVALRIES ─────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-section-label">THE DEFINITIVE LIST</div>
    <div class="tl-section-title">TOP RIVALRIES IN LEAGUE HISTORY</div>
    <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:1.5rem;">
        Ranked by Rivalry Score — a composite of meetings, playoff intensity,
        close games, recent activity, and competitive balance.
    </div>
    """,
    unsafe_allow_html=True,
)

top_10 = all_rivalries.head(10)
r1, r2, r3 = st.columns(3)
r4, r5, r6 = st.columns(3)
r7, r8, r9 = st.columns(3)
r10_col, _, _ = st.columns(3)
col_map = [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10_col]

for i, (_, row) in enumerate(top_10.iterrows()):
    with col_map[i]:
        st.markdown(_rivalry_card(row, rank=i + 1), unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)


# ── SECTION 2: MANAGER RIVALRIES ─────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-section-label">PERSONAL FILES</div>
    <div class="tl-section-title">MANAGER RIVALRIES</div>
    """,
    unsafe_allow_html=True,
)

active_mgrs = sorted(
    tnh[tnh["season"] >= 2015]["canonical_name"].unique().tolist()
)
default_mgr = "Shawn" if "Shawn" in active_mgrs else active_mgrs[0]
selected_mgr = st.selectbox(
    "Select a manager",
    options=all_mgrs,
    index=all_mgrs.index(default_mgr) if default_mgr in all_mgrs else 0,
    label_visibility="collapsed",
    key="mgr_rivalry_select",
)

mgr_rivals = all_rivalries[
    (all_rivalries["mgr_a"] == selected_mgr) | (all_rivalries["mgr_b"] == selected_mgr)
].copy()

def _from_perspective(row: pd.Series, mgr: str) -> dict:
    if row["mgr_a"] == mgr:
        return {
            "opponent": row["mgr_b"],
            "wins": int(row["rs_a_wins"]), "losses": int(row["rs_b_wins"]),
            "win_pct": float(row["rs_a_pct"]),
            "pl_wins": int(row["pl_a_wins"]), "pl_losses": int(row["pl_b_wins"]),
            "final_wins": int(row["final_a_wins"]), "final_losses": int(row["final_b_wins"]),
            "biggest_win": float(row["a_biggest_win"]),
            "biggest_loss": float(row["b_biggest_win"]),
        }
    else:
        return {
            "opponent": row["mgr_a"],
            "wins": int(row["rs_b_wins"]), "losses": int(row["rs_a_wins"]),
            "win_pct": 1.0 - float(row["rs_a_pct"]),
            "pl_wins": int(row["pl_b_wins"]), "pl_losses": int(row["pl_a_wins"]),
            "final_wins": int(row["final_b_wins"]), "final_losses": int(row["final_a_wins"]),
            "biggest_win": float(row["b_biggest_win"]),
            "biggest_loss": float(row["a_biggest_win"]),
        }

mgr_color = _color(selected_mgr)
mgr_em = _emoji(selected_mgr)

if len(mgr_rivals) == 0:
    st.info("No rivalry data found for this manager.")
else:
    # Build perspective rows
    rows_persp = [_from_perspective(r, selected_mgr) for _, r in mgr_rivals.iterrows()]
    persp_df = pd.DataFrame(rows_persp)
    persp_df["rs_games"] = mgr_rivals["rs_games"].values
    persp_df["pl_games"] = mgr_rivals["pl_games"].values
    persp_df["rivalry_score"] = mgr_rivals["rivalry_score"].values
    persp_df["close_games"] = mgr_rivals["close_games"].values

    # Top rivals, nemesis, victims
    top_rival = persp_df.iloc[persp_df["rivalry_score"].argmax()]
    most_losses = persp_df[persp_df["losses"] >= 5]
    nemesis_row = most_losses.iloc[most_losses["win_pct"].argmin()] if len(most_losses) else persp_df.iloc[persp_df["win_pct"].argmin()]
    most_wins = persp_df[persp_df["wins"] >= 5]
    victim_row = most_wins.iloc[most_wins["win_pct"].argmax()] if len(most_wins) else persp_df.iloc[persp_df["win_pct"].argmax()]

    # Summary cards row
    col_nem, col_riv, col_vic = st.columns(3)

    def _highlight_card(title: str, mgr_name: str, subtitle: str, border_color: str) -> str:
        em = _emoji(mgr_name)
        col = _color(mgr_name)
        return f"""
        <div style="background:#0F1B2D;border:1px solid {border_color}55;border-top:3px solid {border_color};
            border-radius:8px;padding:16px;text-align:center;">
            <div style="font-size:0.55rem;letter-spacing:3px;color:{border_color};
                text-transform:uppercase;margin-bottom:6px;">{title}</div>
            <div style="font-size:1.5rem;">{em}</div>
            <div style="font-family:'Playfair Display',serif;font-size:1rem;
                color:{col};font-weight:700;margin:4px 0;">{mgr_name}</div>
            <div style="font-size:0.72rem;color:#94A3B8;">{subtitle}</div>
        </div>
        """

    _nem_rec = f"{int(nemesis_row['wins'])}–{int(nemesis_row['losses'])} all-time"
    _riv_rec = f"Rivalry Score {int(top_rival['rivalry_score'])}"
    _vic_rec = f"{int(victim_row['wins'])}–{int(victim_row['losses'])} all-time"

    with col_nem:
        st.markdown(
            _highlight_card("NEMESIS", str(nemesis_row["opponent"]), _nem_rec, "#EF4444"),
            unsafe_allow_html=True,
        )
    with col_riv:
        st.markdown(
            _highlight_card("TOP RIVAL", str(top_rival["opponent"]), _riv_rec, "#D4AF37"),
            unsafe_allow_html=True,
        )
    with col_vic:
        st.markdown(
            _highlight_card("MOST DOMINATED", str(victim_row["opponent"]), _vic_rec, "#22C55E"),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin:1.5rem 0 1rem;'></div>", unsafe_allow_html=True)

    # Full H2H table
    table_rows = []
    for _, r in persp_df.sort_values("rivalry_score", ascending=False).iterrows():
        opp = str(r["opponent"])
        wins = int(r["wins"])
        losses = int(r["losses"])
        pct = float(r["win_pct"])
        pl_w = int(r["pl_wins"])
        pl_l = int(r["pl_losses"])
        f_w = int(r["final_wins"])
        f_l = int(r["final_losses"])
        rs_g = int(r["rs_games"])
        rs_score = int(r["rivalry_score"])
        close = int(r["close_games"])
        opp_col = _color(opp)
        opp_em = _emoji(opp)

        winner_str = "YOU LEAD" if wins > losses else ("THEY LEAD" if losses > wins else "EVEN")
        winner_color = mgr_color if wins > losses else (_color(opp) if losses > wins else "#6B7280")
        pl_str = f"{pl_w}–{pl_l}" if (pl_w + pl_l) > 0 else "—"
        final_str = f"{f_w}–{f_l}" if (f_w + f_l) > 0 else "—"
        final_col = "#D4AF37" if (f_w + f_l) > 0 else "#374151"

        table_rows.append(
            f"""<tr>
            <td style="padding:10px 12px;color:{opp_col};font-weight:600;">
                {opp_em} {opp}
            </td>
            <td style="padding:10px 12px;text-align:center;">
                <span style="font-weight:700;color:#E2E8F0;">{wins}–{losses}</span>
                <div style="font-size:0.6rem;color:{winner_color};letter-spacing:1px;">{winner_str}</div>
            </td>
            <td style="padding:10px 12px;text-align:center;color:#94A3B8;">{round(pct*100,1)}%</td>
            <td style="padding:10px 12px;text-align:center;color:#FB923C;">{pl_str}</td>
            <td style="padding:10px 12px;text-align:center;color:{final_col};font-weight:600;">{final_str}</td>
            <td style="padding:10px 12px;text-align:center;color:#6B7280;">{close}</td>
            <td style="padding:10px 12px;text-align:center;">
                <span style="font-size:0.7rem;font-weight:700;color:#D4AF37;">{rs_score}</span>
            </td>
            </tr>"""
        )

    table_html = "".join(table_rows)
    st.markdown(
        f"""
        <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-family:'Inter',sans-serif;font-size:0.82rem;">
        <thead>
            <tr style="border-bottom:2px solid #1E3A5F;">
                <th style="padding:8px 12px;text-align:left;color:#6B7280;font-size:0.6rem;letter-spacing:2px;">OPPONENT</th>
                <th style="padding:8px 12px;text-align:center;color:#6B7280;font-size:0.6rem;letter-spacing:2px;">RECORD</th>
                <th style="padding:8px 12px;text-align:center;color:#6B7280;font-size:0.6rem;letter-spacing:2px;">WIN %</th>
                <th style="padding:8px 12px;text-align:center;color:#FB923C;font-size:0.6rem;letter-spacing:2px;">PLAYOFF</th>
                <th style="padding:8px 12px;text-align:center;color:#D4AF37;font-size:0.6rem;letter-spacing:2px;">FINALS</th>
                <th style="padding:8px 12px;text-align:center;color:#6B7280;font-size:0.6rem;letter-spacing:2px;">CLOSE</th>
                <th style="padding:8px 12px;text-align:center;color:#D4AF37;font-size:0.6rem;letter-spacing:2px;">SCORE</th>
            </tr>
        </thead>
        <tbody style="divide-y:1px solid #1E2A40;">
        {table_html}
        </tbody>
        </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)


# ── SECTION 3: PLAYOFF RIVALRIES ─────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-section-label">WHEN IT MATTERS MOST</div>
    <div class="tl-section-title">PLAYOFF RIVALRIES</div>
    <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:1.5rem;">
        Championship-bracket matchups only. Every game counted. Some ended seasons.
    </div>
    """,
    unsafe_allow_html=True,
)

pc1, pc2 = st.columns(2)

with pc1:
    # Most playoff meetings by pair
    top_pl = all_rivalries[all_rivalries["pl_games"] >= 3].copy().head(8)
    st.markdown(
        '<div style="font-size:0.65rem;letter-spacing:3px;color:#FB923C;'
        'text-transform:uppercase;margin-bottom:0.8rem;">MOST PLAYOFF MEETINGS</div>',
        unsafe_allow_html=True,
    )
    for _, row in top_pl.iterrows():
        ma = row["mgr_a"]
        mb = row["mgr_b"]
        pl_w_a = int(row["pl_a_wins"])
        pl_w_b = int(row["pl_b_wins"])
        pl_g = int(row["pl_games"])
        fin_g = int(row["final_games"])
        ca = _color(ma)
        cb = _color(mb)
        fin_badge = (
            f'<span style="font-size:0.55rem;background:rgba(212,175,55,0.15);color:#D4AF37;'
            f'padding:1px 5px;border-radius:2px;border:1px solid rgba(212,175,55,0.3);">'
            f'{fin_g} TITLE</span>'
        ) if fin_g else ""
        lead_mgr = ma if pl_w_a > pl_w_b else (mb if pl_w_b > pl_w_a else None)
        lead_col = _color(lead_mgr) if lead_mgr else "#6B7280"
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:8px;
                padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="color:{ca};font-weight:600;">{_emoji(ma)} {ma}</span>
                    <span style="color:#6B7280;font-size:0.7rem;margin:0 6px;">vs</span>
                    <span style="color:{cb};font-weight:600;">{_emoji(mb)} {mb}</span>
                    <div style="margin-top:4px;">{fin_badge}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:700;color:{lead_col};">{pl_w_a}–{pl_w_b}</div>
                    <div style="font-size:0.6rem;color:#6B7280;">{pl_g} games</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

with pc2:
    # Executioner table
    st.markdown(
        '<div style="font-size:0.65rem;letter-spacing:3px;color:#EF4444;'
        'text-transform:uppercase;margin-bottom:0.8rem;">MOST PLAYOFF ELIMINATIONS</div>',
        unsafe_allow_html=True,
    )
    total_elim = (
        elim_df.groupby("winner_mgr")["eliminations"]
        .sum()
        .reset_index(name="total")
        .sort_values("total", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    for rank_i, (_, er) in enumerate(total_elim.iterrows()):
        mgr = str(er["winner_mgr"])
        n = int(er["total"])
        col = _color(mgr)
        top_victims = elim_df[elim_df["winner_mgr"] == mgr].nlargest(2, "eliminations")
        victim_str = " · ".join(
            f"{int(r['eliminations'])}× vs {r['loser_mgr']}"
            for _, r in top_victims.iterrows()
        )
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:8px;
                padding:10px 14px;margin-bottom:8px;display:flex;align-items:center;gap:12px;">
                <div style="font-size:0.7rem;font-weight:800;color:#6B7280;width:20px;
                    text-align:center;">#{rank_i+1}</div>
                <div style="flex:1;">
                    <div style="font-weight:600;color:{col};">{_emoji(mgr)} {mgr}</div>
                    <div style="font-size:0.65rem;color:#6B7280;margin-top:2px;">{victim_str}</div>
                </div>
                <div style="font-size:1.4rem;font-weight:800;color:#EF4444;">{n}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Most times eliminated by same manager
    st.markdown(
        '<div style="font-size:0.65rem;letter-spacing:3px;color:#F87171;'
        'text-transform:uppercase;margin:1rem 0 0.6rem;">MOST TIMES ELIMINATED BY ONE PERSON</div>',
        unsafe_allow_html=True,
    )
    top_elim_pair = elim_df.nlargest(5, "eliminations")
    for _, er in top_elim_pair.iterrows():
        killer = str(er["winner_mgr"])
        victim = str(er["loser_mgr"])
        n = int(er["eliminations"])
        k_col = _color(killer)
        v_col = _color(victim)
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E2A40;border-left:3px solid #EF4444;
                border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:6px;font-size:0.78rem;">
                <span style="color:{k_col};font-weight:600;">{_emoji(killer)} {killer}</span>
                <span style="color:#6B7280;"> eliminated </span>
                <span style="color:{v_col};font-weight:600;">{victim}</span>
                <span style="color:#EF4444;font-weight:800;"> {n}×</span>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)


# ── SECTION 4: CHAMPIONSHIP RIVALRIES ────────────────────────────────────────
st.markdown(
    """
    <div class="tl-section-label">THE GRANDEST STAGE</div>
    <div class="tl-section-title">CHAMPIONSHIP RIVALRIES</div>
    """,
    unsafe_allow_html=True,
)

cc1, cc2 = st.columns([3, 2])

with cc1:
    st.markdown(
        '<div style="font-size:0.65rem;letter-spacing:3px;color:#D4AF37;'
        'text-transform:uppercase;margin-bottom:1rem;">TITLE GAME HISTORY</div>',
        unsafe_allow_html=True,
    )
    for _, fin in finals.sort_values("season", ascending=False).iterrows():
        w = str(fin["winner_mgr"])
        l = str(fin["loser_mgr"])
        szn = int(fin["season"])
        ws = float(fin["win_score"])
        ls = float(fin["loss_score"])
        margin = float(fin["margin"])
        wcol = _color(w)
        lcol = _color(l)
        margin_tag = ""
        if margin < 3:
            margin_tag = (
                '<span style="font-size:0.55rem;background:rgba(239,68,68,0.15);color:#EF4444;'
                'padding:1px 5px;border-radius:2px;border:1px solid rgba(239,68,68,0.3);">INSTANT CLASSIC</span>'
            )
        elif margin < 7:
            margin_tag = (
                '<span style="font-size:0.55rem;background:rgba(251,146,60,0.1);color:#FB923C;'
                'padding:1px 5px;border-radius:2px;">CLOSE GAME</span>'
            )
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:8px;
                padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.6rem;color:#6B7280;margin-bottom:3px;">{szn} CHAMPIONSHIP</div>
                    <div style="font-size:0.9rem;">
                        <span style="color:{wcol};font-weight:700;">🏆 {w}</span>
                        <span style="color:#6B7280;font-size:0.7rem;margin:0 6px;">def</span>
                        <span style="color:{lcol};">{l}</span>
                    </div>
                    <div style="margin-top:4px;">{margin_tag}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.85rem;font-weight:700;color:#E2E8F0;">{ws:.1f}–{ls:.1f}</div>
                    <div style="font-size:0.6rem;color:#6B7280;">margin: {margin:.2f}</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

with cc2:
    # Most title game appearances
    title_wins = finals.groupby("winner_mgr").size().reset_index(name="wins").rename(columns={"winner_mgr": "mgr"})
    title_loss = finals.groupby("loser_mgr").size().reset_index(name="losses").rename(columns={"loser_mgr": "mgr"})
    title_rec = title_wins.merge(title_loss, on="mgr", how="outer").fillna(0)
    title_rec["wins"] = title_rec["wins"].astype(int)
    title_rec["losses"] = title_rec["losses"].astype(int)
    title_rec["apps"] = title_rec["wins"] + title_rec["losses"]
    title_rec = title_rec.sort_values(["wins", "apps"], ascending=False).reset_index(drop=True)

    st.markdown(
        '<div style="font-size:0.65rem;letter-spacing:3px;color:#D4AF37;'
        'text-transform:uppercase;margin-bottom:0.8rem;">CHAMPIONSHIP GAME RECORD</div>',
        unsafe_allow_html=True,
    )
    for _, tr in title_rec.head(10).iterrows():
        mgr = str(tr["mgr"])
        w = int(tr["wins"])
        l = int(tr["losses"])
        apps = int(tr["apps"])
        col = _color(mgr)
        fill_w = round(w / apps * 100) if apps else 0
        fill_l = 100 - fill_w
        pct_bar = (
            f'<div style="display:flex;border-radius:3px;overflow:hidden;height:5px;margin:4px 0;">'
            f'<div style="width:{fill_w}%;background:{col};"></div>'
            f'<div style="width:{fill_l}%;background:#1E3A5F;"></div>'
            f'</div>'
        )
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:8px;
                padding:10px 14px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:{col};font-weight:600;font-size:0.85rem;">{_emoji(mgr)} {mgr}</span>
                    <span style="font-weight:700;color:#E2E8F0;">{w}–{l}</span>
                </div>
                {pct_bar}
                <div style="font-size:0.6rem;color:#6B7280;">{apps} title game{"s" if apps != 1 else ""}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)


# ── SECTION 5: HALL OF PAIN ──────────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-section-label">THE EMOTIONAL CENTER</div>
    <div class="tl-section-title">HALL OF PAIN</div>
    <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:1.5rem;">
        The losses that stung. The rivalries that never broke your way. The grudges that never healed.
    </div>
    """,
    unsafe_allow_html=True,
)

hp1, hp2 = st.columns(2)

with hp1:
    # Most RS losses to one opponent
    rs_all = data_raw["weekly_matchups"].copy()
    rs_all["mgr"] = rs_all.apply(lambda r: mgr_lu.get((r["season"], r["team_name"])), axis=1)
    rs_all["opp_mgr"] = rs_all.apply(lambda r: mgr_lu.get((r["season"], r["opponent"])), axis=1)
    rs_only = rs_all[~rs_all["is_bye"].astype(bool) & ~rs_all["is_playoff"].astype(bool)].copy()
    rs_only = rs_only.dropna(subset=["mgr", "opp_mgr"])
    rs_only["pair"] = rs_only.apply(lambda r: tuple(sorted([r["mgr"], r["opp_mgr"]])), axis=1)
    rs_dedup2 = rs_only.drop_duplicates(subset=["season", "week", "pair"])
    rs_dedup2["winner"] = rs_dedup2.apply(
        lambda r: r["mgr"] if r["result"] == "Win" else r["opp_mgr"], axis=1
    )
    rs_dedup2["loser"] = rs_dedup2.apply(
        lambda r: r["opp_mgr"] if r["result"] == "Win" else r["mgr"], axis=1
    )
    loss_ct = (
        rs_dedup2.groupby(["loser", "winner"])
        .size()
        .reset_index(name="losses")
        .sort_values("losses", ascending=False)
    )
    top_losses = loss_ct[loss_ct["losses"] >= 10].head(6)
    st.markdown(
        _pain_entry("😩", "MOST LOSSES TO ONE OPPONENT",
            f"{loss_ct.iloc[0]['loser']} lost {loss_ct.iloc[0]['losses']} times to {loss_ct.iloc[0]['winner']}",
            "The most lopsided long-term regular season record in league history.",
            "#EF4444"),
        unsafe_allow_html=True,
    )
    for _, r in top_losses.iterrows():
        loser = str(r["loser"])
        winner = str(r["winner"])
        losses = int(r["losses"])
        lc = _color(loser)
        wc = _color(winner)
        st.markdown(
            f"""<div style="display:flex;justify-content:space-between;align-items:center;
                background:#0F1B2D;border:1px solid #1E3A5F;border-radius:6px;
                padding:8px 12px;margin-bottom:6px;font-size:0.78rem;">
                <span style="color:{lc};">{_emoji(loser)} {loser}</span>
                <span style="color:#6B7280;font-size:0.65rem;">lost {losses}× to</span>
                <span style="color:{wc};font-weight:600;">{_emoji(winner)} {winner}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # Closest championship loss
    closest_final = finals.nsmallest(3, "margin")
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        _pain_entry("💔", "CLOSEST CHAMPIONSHIP LOSS",
            f"{finals.nsmallest(1,'margin').iloc[0]['loser_mgr']} lost the title by {finals.nsmallest(1,'margin').iloc[0]['margin']:.2f} pts",
            f"The 2024 championship: {finals.nsmallest(1,'margin').iloc[0]['loser_mgr']} vs {finals.nsmallest(1,'margin').iloc[0]['winner_mgr']}. 0.12 points. The cruelest margin in league history.",
            "#F59E0B"),
        unsafe_allow_html=True,
    )
    for _, r in closest_final.iterrows():
        loser = str(r["loser_mgr"])
        winner = str(r["winner_mgr"])
        szn = int(r["season"])
        margin = float(r["margin"])
        lc = _color(loser)
        wc = _color(winner)
        st.markdown(
            f"""<div style="display:flex;justify-content:space-between;align-items:center;
                background:#0F1B2D;border:1px solid #1E3A5F;border-left:3px solid #F59E0B;
                border-radius:0 6px 6px 0;padding:8px 12px;margin-bottom:6px;font-size:0.78rem;">
                <div>
                    <span style="color:#6B7280;">{szn} · </span>
                    <span style="color:{lc};">{loser}</span>
                </div>
                <div style="text-align:right;">
                    <span style="color:#F59E0B;font-weight:700;">lost by {margin:.2f} pts</span>
                    <div style="font-size:0.6rem;color:#6B7280;">to {winner}</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

with hp2:
    # Most championship losses overall
    champ_losers = finals.groupby("loser_mgr").size().reset_index(name="losses").sort_values("losses", ascending=False)
    worst_ru = champ_losers.iloc[0]
    st.markdown(
        _pain_entry("🥈", "MOST CHAMPIONSHIP LOSSES",
            f"{worst_ru['loser_mgr']} has lost {worst_ru['losses']} title games",
            "Close enough to touch the trophy. Never close enough to keep it.",
            "#94A3B8"),
        unsafe_allow_html=True,
    )
    for _, r in champ_losers.head(6).iterrows():
        loser = str(r["loser_mgr"])
        losses = int(r["losses"])
        # Find who they lost to
        against = finals[finals["loser_mgr"] == loser]["winner_mgr"].value_counts()
        against_str = ", ".join([f"{n}× vs {m}" for m, n in against.items()])
        lc = _color(loser)
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:6px;
                padding:8px 12px;margin-bottom:6px;font-size:0.78rem;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:{lc};font-weight:600;">{_emoji(loser)} {loser}</span>
                    <span style="color:#94A3B8;font-weight:700;">{losses} loss{"es" if losses>1 else ""}</span>
                </div>
                <div style="font-size:0.65rem;color:#6B7280;margin-top:2px;">{against_str}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Most playoff eliminations received
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    most_eliminated = (
        elim_df.groupby("loser_mgr")["eliminations"]
        .sum()
        .reset_index(name="times_eliminated")
        .sort_values("times_eliminated", ascending=False)
        .head(6)
    )
    worst_elim = most_eliminated.iloc[0]
    st.markdown(
        _pain_entry("⛔", "MOST PLAYOFF ELIMINATIONS RECEIVED",
            f"{worst_elim['loser_mgr']} eliminated from the bracket {int(worst_elim['times_eliminated'])} times",
            "A fixture of the postseason. Not always in the way you'd want to be remembered.",
            "#8B5CF6"),
        unsafe_allow_html=True,
    )
    for _, r in most_eliminated.iterrows():
        victim = str(r["loser_mgr"])
        n = int(r["times_eliminated"])
        vc = _color(victim)
        top_killer = elim_df[elim_df["loser_mgr"] == victim].nlargest(1, "eliminations")
        killer_str = (
            f"most often by {top_killer.iloc[0]['winner_mgr']} ({int(top_killer.iloc[0]['eliminations'])}×)"
            if len(top_killer) else ""
        )
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:6px;
                padding:8px 12px;margin-bottom:6px;font-size:0.78rem;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:{vc};font-weight:600;">{_emoji(victim)} {victim}</span>
                    <span style="color:#8B5CF6;font-weight:700;">{n}×</span>
                </div>
                <div style="font-size:0.65rem;color:#6B7280;margin-top:2px;">{killer_str}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)


# ── SECTION 6: FRANCHISE RIVALRIES ───────────────────────────────────────────
st.markdown(
    """
    <div class="tl-section-label">INSTITUTIONS IN CONFLICT</div>
    <div class="tl-section-title">FRANCHISE RIVALRIES</div>
    <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:1.5rem;">
        Franchises outlive managers. These rivalries transcend individual stewardships.
    </div>
    """,
    unsafe_allow_html=True,
)

top_fran = fran_rivalries.head(15)
fr_cols = st.columns(3)
for i, (_, r) in enumerate(top_fran.iterrows()):
    fid_a = str(r["fid_a"])
    fid_b = str(r["fid_b"])
    games = int(r["games"])
    a_wins = int(r["a_wins"])
    b_wins = int(r["b_wins"])
    a_pct = float(r["a_pct"])
    leader = fid_a if a_wins > b_wins else (fid_b if b_wins > a_wins else None)
    leader_str = f"{leader} leads" if leader else "Even"
    with fr_cols[i % 3]:
        st.markdown(
            f"""<div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:8px;
                padding:12px;margin-bottom:10px;">
                <div style="font-family:'Playfair Display',serif;font-size:0.9rem;
                    font-weight:700;color:#E2E8F0;margin-bottom:6px;">
                    {fid_a} vs {fid_b}
                </div>
                {_pct_bar(a_pct, "#3B82F6", "#EF4444")}
                <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#94A3B8;">
                    <span><b style="color:#3B82F6;">{a_wins}</b></span>
                    <span style="color:#6B7280;">{games} games · {leader_str}</span>
                    <span><b style="color:#EF4444;">{b_wins}</b></span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)


# ── SECTION 7: RIVALRY EXPLORER ──────────────────────────────────────────────
st.markdown(
    """
    <div class="tl-section-label">FACE-TO-FACE</div>
    <div class="tl-section-title">RIVALRY EXPLORER</div>
    <div style="font-size:0.8rem;color:#94A3B8;margin-bottom:1.5rem;">
        Select any two managers. See everything that happened between them.
    </div>
    """,
    unsafe_allow_html=True,
)

ex_col1, ex_mid, ex_col2 = st.columns([5, 1, 5])
with ex_col1:
    mgr_a_sel = st.selectbox(
        "Manager A",
        options=all_mgrs,
        index=all_mgrs.index("Dominic") if "Dominic" in all_mgrs else 0,
        key="explorer_a",
    )
with ex_mid:
    st.markdown(
        '<div style="text-align:center;padding-top:2rem;font-size:1.2rem;color:#6B7280;">VS</div>',
        unsafe_allow_html=True,
    )
with ex_col2:
    default_b = "Brian Clark" if "Brian Clark" in all_mgrs else all_mgrs[1]
    mgr_b_sel = st.selectbox(
        "Manager B",
        options=all_mgrs,
        index=all_mgrs.index(default_b) if default_b in all_mgrs else 1,
        key="explorer_b",
    )

if mgr_a_sel == mgr_b_sel:
    st.warning("Select two different managers.")
else:
    col_a = _color(mgr_a_sel)
    col_b = _color(mgr_b_sel)

    # Get rivalry row
    mask = (
        ((all_rivalries["mgr_a"] == mgr_a_sel) & (all_rivalries["mgr_b"] == mgr_b_sel)) |
        ((all_rivalries["mgr_a"] == mgr_b_sel) & (all_rivalries["mgr_b"] == mgr_a_sel))
    )
    riv_rows = all_rivalries[mask]
    if len(riv_rows) == 0:
        st.info("No matchup history found between these managers.")
    else:
        riv_row = riv_rows.iloc[0]
        persp = _from_perspective(riv_row, mgr_a_sel)
        a_wins = persp["wins"]
        a_losses = persp["losses"]
        a_pct = persp["win_pct"]
        pl_aw = persp["pl_wins"]
        pl_al = persp["pl_losses"]
        f_aw = persp["final_wins"]
        f_al = persp["final_losses"]
        rs_total = int(riv_row["rs_games"])
        pl_total = int(riv_row["pl_games"])
        close = int(riv_row["close_games"])
        score = int(riv_row["rivalry_score"])
        closest = float(riv_row["closest_game"])
        first_yr = int(riv_row["first_meeting"])
        last_yr = int(riv_row["last_meeting"])

        # Header
        winner_mgr = mgr_a_sel if a_wins > a_losses else (mgr_b_sel if a_losses > a_wins else None)
        lead_str = f"{winner_mgr} leads" if winner_mgr else "All-time series is even"
        lead_col = _color(winner_mgr) if winner_mgr else "#6B7280"

        st.markdown(
            f"""
            <div style="background:#0F1B2D;border:1px solid #1E3A5F;border-radius:12px;
                padding:24px;margin:1.5rem 0;">
                <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:center;">
                    <div style="text-align:center;">
                        <div style="font-size:2rem;">{_emoji(mgr_a_sel)}</div>
                        <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                            color:{col_a};font-weight:700;">{mgr_a_sel}</div>
                        <div style="font-size:2rem;font-weight:800;color:{col_a};margin:4px 0;">{a_wins}</div>
                        <div style="font-size:0.6rem;color:#6B7280;letter-spacing:2px;">WINS</div>
                    </div>
                    <div style="text-align:center;padding:0 8px;">
                        <div style="font-size:0.55rem;letter-spacing:3px;color:#6B7280;margin-bottom:4px;">RIVALRY SCORE</div>
                        <div style="font-size:2rem;font-weight:800;color:#D4AF37;">{score}</div>
                        <div style="font-size:0.6rem;color:#94A3B8;margin-top:2px;">{rs_total} RS · {pl_total} PL</div>
                        <div style="font-size:0.65rem;margin-top:6px;color:{lead_col};">{lead_str}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:2rem;">{_emoji(mgr_b_sel)}</div>
                        <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                            color:{col_b};font-weight:700;">{mgr_b_sel}</div>
                        <div style="font-size:2rem;font-weight:800;color:{col_b};margin:4px 0;">{a_losses}</div>
                        <div style="font-size:0.6rem;color:#6B7280;letter-spacing:2px;">WINS</div>
                    </div>
                </div>
                {_pct_bar(a_pct, col_a, col_b, 10)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Stat breakdown
        sb1, sb2, sb3, sb4, sb5, sb6 = st.columns(6)
        _sb = lambda v, l: f'<div class="tl-metric" style="padding:10px;"><div class="tl-metric-value" style="font-size:1.3rem;">{v}</div><div class="tl-metric-label">{l}</div></div>'
        with sb1:
            st.markdown(_sb(f"{a_wins}–{a_losses}", "RS Record"), unsafe_allow_html=True)
        with sb2:
            st.markdown(_sb(f"{pl_aw}–{pl_al}" if (pl_aw+pl_al) else "—", "Playoff"), unsafe_allow_html=True)
        with sb3:
            st.markdown(_sb(f"{f_aw}–{f_al}" if (f_aw+f_al) else "—", "Finals"), unsafe_allow_html=True)
        with sb4:
            st.markdown(_sb(close, "Close Games"), unsafe_allow_html=True)
        with sb5:
            st.markdown(_sb(f"{closest:.2f}", "Closest Margin"), unsafe_allow_html=True)
        with sb6:
            st.markdown(_sb(f"{first_yr}–{last_yr}", "Span"), unsafe_allow_html=True)

        # Rivalry plaque if it exists
        plaque_text = _plaque(mgr_a_sel, mgr_b_sel)
        if plaque_text:
            st.markdown(
                f"""<div style="background:rgba(212,175,55,0.05);border-left:4px solid #D4AF37;
                    border-radius:0 8px 8px 0;padding:16px 20px;margin:1rem 0;
                    font-style:italic;color:#CBD5E1;line-height:1.7;font-size:0.83rem;">
                    {plaque_text}
                </div>""",
                unsafe_allow_html=True,
            )

        # Game-by-game detail
        h2h = get_h2h_detail(mgr_a_sel, mgr_b_sel)
        rs_games = h2h["rs"]
        pl_games_df = h2h["playoffs"]

        if len(rs_games) > 0:
            with st.expander(f"All {len(rs_games)} Regular Season Games", expanded=False):
                display_rs = rs_games.copy()
                display_rs["Winner"] = display_rs["winner"].apply(
                    lambda w: f"🏆 {mgr_a_sel}" if w == mgr_a_sel else f"🏆 {mgr_b_sel}"
                )
                display_rs[mgr_a_sel] = display_rs["a_score"].round(2)
                display_rs[mgr_b_sel] = display_rs["b_score"].round(2)
                display_rs["Margin"] = display_rs["margin"].round(2)
                st.dataframe(
                    display_rs[["season", "week", mgr_a_sel, mgr_b_sel, "Margin", "Winner"]],
                    use_container_width=True,
                    hide_index=True,
                )

        if len(pl_games_df) > 0:
            with st.expander(f"All {len(pl_games_df)} Playoff Games", expanded=True):
                pl_display = pl_games_df.copy()
                pl_display["Winner"] = pl_display["winner_mgr"].apply(
                    lambda w: f"🏆 {mgr_a_sel}" if w == mgr_a_sel else f"🏆 {mgr_b_sel}"
                )
                pl_display[mgr_a_sel] = pl_display["a_score"].round(2)
                pl_display[mgr_b_sel] = pl_display["b_score"].round(2)
                pl_display["Margin"] = pl_display["margin"].round(2)
                pl_display["Round"] = pl_display["game_type"].str.replace("_", " ").str.title()
                st.dataframe(
                    pl_display[["season", "Round", mgr_a_sel, mgr_b_sel, "Margin", "Winner"]],
                    use_container_width=True,
                    hide_index=True,
                )

# ── CROSS-PAGE CONNECTIONS ────────────────────────────────────────────────────
st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)
st.markdown(
    """
    <div style="margin:2.5rem 0 1.5rem;">
        <div style="font-family:'Playfair Display',Georgia,serif;font-size:0.65rem;
            letter-spacing:4px;color:#A7B0BC;text-transform:uppercase;margin-bottom:1rem;">
            CONTINUE THE STORY
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;">
            <a href="/champions" style="flex:1;min-width:160px;background:#0F1B2D;
                border:1px solid rgba(212,175,55,0.3);border-radius:8px;padding:14px 16px;
                text-decoration:none;display:block;">
                <div style="font-size:1.1rem;margin-bottom:4px;">🏆</div>
                <div style="font-family:'Playfair Display',serif;font-size:0.78rem;
                    color:#D4AF37;font-weight:600;">Trophy Room</div>
                <div style="font-size:0.72rem;color:#A7B0BC;margin-top:3px;">
                    See how rivalries shaped every championship
                </div>
            </a>
            <a href="/manager_profiles" style="flex:1;min-width:160px;background:#0F1B2D;
                border:1px solid rgba(96,165,250,0.3);border-radius:8px;padding:14px 16px;
                text-decoration:none;display:block;">
                <div style="font-size:1.1rem;margin-bottom:4px;">👤</div>
                <div style="font-family:'Playfair Display',serif;font-size:0.78rem;
                    color:#60A5FA;font-weight:600;">Manager Files</div>
                <div style="font-size:0.72rem;color:#A7B0BC;margin-top:3px;">
                    The people behind the rivalries
                </div>
            </a>
            <a href="/franchise_profiles" style="flex:1;min-width:160px;background:#0F1B2D;
                border:1px solid rgba(52,211,153,0.3);border-radius:8px;padding:14px 16px;
                text-decoration:none;display:block;">
                <div style="font-size:1.1rem;margin-bottom:4px;">🏛️</div>
                <div style="font-family:'Playfair Display',serif;font-size:0.78rem;
                    color:#34D399;font-weight:600;">Franchise Files</div>
                <div style="font-size:0.72rem;color:#A7B0BC;margin-top:3px;">
                    Rivalries that outlived the managers
                </div>
            </a>
            <a href="/league_timeline" style="flex:1;min-width:160px;background:#0F1B2D;
                border:1px solid rgba(167,139,250,0.3);border-radius:8px;padding:14px 16px;
                text-decoration:none;display:block;">
                <div style="font-size:1.1rem;margin-bottom:4px;">📜</div>
                <div style="font-family:'Playfair Display',serif;font-size:0.78rem;
                    color:#A78BFA;font-weight:600;">Timeline</div>
                <div style="font-size:0.72rem;color:#A7B0BC;margin-top:3px;">
                    When rivalry moments became league history
                </div>
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_page_footer(
    href="/champions",
    cta="SEE THE CHAMPIONS",
    tagline="EVERY RIVALRY ENDS SOMEWHERE.<br>ONLY ONE PERSON WINS IT ALL.",
)
