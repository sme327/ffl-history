"""Keeper Hall — museum of players nobody could let go."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.data import (
    get_draft_picks_with_pos, get_keeper_chains, get_player_ownership,
    get_draft_records, get_keeper_enriched,
    MANAGER_EMOJI, MANAGER_COLORS, CURRENT_SEASON, FOUNDED,
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

def _mgr_color(mgr):
    return MANAGER_COLORS.get(mgr, "#6B7280")

def _mgr_emoji(mgr):
    return MANAGER_EMOJI.get(mgr, "👤")

def _pos_badge(pos):
    c = POS_COLORS.get(pos or "?", "#6B7280")
    return (
        f'<span style="background:{c};color:#000;font-weight:700;font-size:0.58rem;'
        f'padding:2px 5px;border-radius:3px;letter-spacing:1px;">{pos or "?"}</span>'
    )

def _yr_pill(szn, color):
    return (
        f'<span style="background:{color}22;border:1px solid {color};border-radius:4px;'
        f'padding:1px 6px;font-size:0.62rem;font-family:\'Inter\',sans-serif;color:#F5F5F5;'
        f'margin:1px;">{szn}</span>'
    )

def _trophy(n):
    return ("🏆 " * n).strip() if n > 0 else ""

# ── LOAD ──────────────────────────────────────────────────────────────────────
dpw = get_draft_picks_with_pos()
chains = get_keeper_chains()
ke = get_keeper_enriched()
po = get_player_ownership()
rec = get_draft_records()
keepers = dpw[dpw["is_keeper"]].copy()

# Suspension-year aware active keeper seasons
active_keeper_szns = sorted(keepers["season"].unique().astype(int).tolist())

# Immortal scoring: streak × 2 + titles × 5 + playoffs × 0.5
immortal_rows = []
for _, ch in chains.iterrows():
    player = ch["player_name"]
    seasons_in_run = ch["seasons"]
    chain_ke = ke[(ke["player_name"] == player) & (ke["season"].isin(seasons_in_run))]
    titles = int(chain_ke["won_title"].sum())
    playoffs = int(chain_ke["made_playoffs"].sum())
    score = ch["streak_len"] * 2 + titles * 5 + playoffs * 0.5
    pos_vals = ke[ke["player_name"] == player]["position"].dropna()
    pos = str(pos_vals.iloc[0]) if len(pos_vals) > 0 else "?"
    immortal_rows.append({
        "player_name": player,
        "primary_manager": ch["primary_manager"],
        "all_managers": ch["all_managers"],
        "franchise_id": ch["franchise_id"],
        "seasons": seasons_in_run,
        "streak_len": int(ch["streak_len"]),
        "titles": titles,
        "playoffs": playoffs,
        "score": score,
        "multi_manager": ch["multi_manager"],
        "position": pos,
    })

immortal_df = (
    pd.DataFrame(immortal_rows)
    .sort_values("score", ascending=False)
    .reset_index(drop=True)
)
top_chains_scored = immortal_df[immortal_df["streak_len"] >= 3]

# ── PAGE HEADER ───────────────────────────────────────────────────────────────
total_keepers = len(keepers)
total_keeper_seasons = keepers["season"].nunique()
longest_streak = int(chains["streak_len"].max()) if len(chains) else 0
most_kept_player = keepers.groupby("player_name").size().idxmax() if len(keepers) else "—"
most_kept_count = int(keepers.groupby("player_name").size().max()) if len(keepers) else 0

st.markdown(
    f"""
    <div class="tl-page-title">Keeper Hall</div>
    <div class="tl-page-subtitle">
        {total_keepers} keeper seasons &nbsp;·&nbsp;
        {keepers["player_name"].nunique()} unique players &nbsp;·&nbsp;
        {longest_streak}-season longest streak &nbsp;·&nbsp;
        a museum of the players nobody could quit
    </div>
    <hr class="tl-divider">
    """,
    unsafe_allow_html=True,
)

s1, s2, s3, s4 = st.columns(4)
for col, val, lbl in [
    (s1, total_keepers, "Total Keeper Seasons"),
    (s2, keepers["player_name"].nunique(), "Unique Kept Players"),
    (s3, longest_streak, "Longest Keeper Streak"),
    (s4, most_kept_count, f"{most_kept_player} — Most Times Kept"),
]:
    col.markdown(
        f'<div class="tl-metric"><div class="tl-metric-value">{val}</div>'
        f'<div class="tl-metric-label">{lbl}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 1 — THE IMMORTALS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE IMMORTALS", "Greatest Keeper Runs in League History"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.75rem;">'
    'Scored by streak length, championships won during the run, and playoff appearances. '
    'The definitive list of keepers that defined franchises.</p>',
    unsafe_allow_html=True,
)

top4 = top_chains_scored.head(4)

if len(top4) > 0:
    # Hero card — #1 Immortal
    hero = top4.iloc[0]
    hero_color = _mgr_color(hero["primary_manager"])
    hero_pos = _pos_badge(hero["position"])
    hero_mgrs = hero["all_managers"]
    hero_mgr_str = (
        f'{hero["franchise_id"]} ({" → ".join(hero_mgrs)})'
        if hero["multi_manager"] else
        f'{_mgr_emoji(hero["primary_manager"])} {hero["primary_manager"]}'
    )
    hero_yr_pills = "".join(_yr_pill(s, hero_color) for s in hero["seasons"])
    hero_titles_str = _trophy(hero["titles"])
    hero_desc = []
    if hero["titles"] > 0:
        hero_desc.append(f'{"🏆" * hero["titles"]} Championship{"s" if hero["titles"] > 1 else ""} won during this run')
    if hero["playoffs"] > 0:
        hero_desc.append(f'{hero["playoffs"]} playoff appearance{"s" if hero["playoffs"] > 1 else ""} in {hero["streak_len"]} seasons')
    hero_desc_html = "".join(
        f'<div style="font-size:0.7rem;color:#A7B0BC;margin:2px 0;">{d}</div>' for d in hero_desc
    )

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0F1B2D 0%,#0a1520 100%);'
        f'border:1px solid {hero_color}44;border-left:6px solid {hero_color};'
        f'border-radius:8px;padding:24px 28px;margin-bottom:16px;'
        f'box-shadow:0 4px 24px {hero_color}22;">'
        f'<div style="display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap;">'
        f'<div style="flex:0 0 auto;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:4.5rem;color:{hero_color};'
        f'line-height:1;margin-bottom:-4px;">{hero["streak_len"]}</div>'
        f'<div style="font-family:\'Inter\',sans-serif;font-size:0.6rem;color:#A7B0BC;'
        f'letter-spacing:2px;text-transform:uppercase;">seasons</div>'
        f'</div>'
        f'<div style="flex:1;min-width:200px;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.2rem;color:#F5F5F5;'
        f'letter-spacing:3px;line-height:1;">{hero["player_name"]}</div>'
        f'{hero_pos}'
        f'</div>'
        f'<div style="font-size:0.72rem;color:#A7B0BC;margin-bottom:10px;">{hero_mgr_str}</div>'
        f'{hero_desc_html}'
        f'<div style="display:flex;flex-wrap:wrap;gap:3px;margin-top:12px;">{hero_yr_pills}</div>'
        f'</div>'
        f'<div style="flex:0 0 auto;text-align:right;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.65rem;color:#A7B0BC;'
        f'letter-spacing:3px;margin-bottom:4px;">IMMORTAL SCORE</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:3rem;color:#D4AF37;'
        f'line-height:1;">{hero["score"]:.1f}</div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Cards 2-4 in a row
    row2 = top4.iloc[1:]
    if len(row2) > 0:
        cols = st.columns(len(row2))
        for col, (_, im) in zip(cols, row2.iterrows()):
            c = _mgr_color(im["primary_manager"])
            pb = _pos_badge(im["position"])
            mgr_str = (
                f'{im["franchise_id"]} ({" → ".join(im["all_managers"])})'
                if im["multi_manager"] else
                f'{_mgr_emoji(im["primary_manager"])} {im["primary_manager"]}'
            )
            yr_pills = "".join(_yr_pill(s, c) for s in im["seasons"])
            extra = []
            if im["titles"] > 0:
                extra.append(f'{"🏆" * im["titles"]}')
            if im["playoffs"] > 0:
                extra.append(f'{im["playoffs"]}× playoffs')
            extra_html = "&nbsp;·&nbsp;".join(extra) if extra else "&nbsp;"
            col.markdown(
                f'<div style="background:#0F1B2D;border:1px solid {c}44;border-left:4px solid {c};'
                f'border-radius:6px;padding:16px;margin-bottom:10px;height:100%;">'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:2.8rem;color:{c};'
                f'line-height:1;margin-bottom:4px;">{im["streak_len"]}</div>'
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:#F5F5F5;'
                f'letter-spacing:2px;">{im["player_name"]}</div>{pb}</div>'
                f'<div style="font-size:0.63rem;color:#A7B0BC;margin-bottom:8px;">{mgr_str}</div>'
                f'<div style="font-size:0.62rem;color:#D4AF37;margin-bottom:8px;">{extra_html}</div>'
                f'<div style="display:flex;flex-wrap:wrap;gap:2px;">{yr_pills}</div>'
                f'<div style="text-align:right;margin-top:8px;">'
                f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.3rem;color:#D4AF37;">'
                f'{im["score"]:.1f}</span>'
                f'<span style="font-size:0.55rem;color:#4B5563;margin-left:3px;">SCORE</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Show #5-6 if they exist
    if len(top_chains_scored) > 4:
        st.markdown(
            '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.7rem;color:#A7B0BC;'
            'letter-spacing:3px;margin:1rem 0 0.5rem;">ALSO LEGENDARY</div>',
            unsafe_allow_html=True,
        )
        extra_cols = st.columns(min(len(top_chains_scored) - 4, 3))
        for col, (_, im) in zip(extra_cols, top_chains_scored.iloc[4:7].iterrows()):
            c = _mgr_color(im["primary_manager"])
            mgr_str = (
                f'{im["franchise_id"]} ({" → ".join(im["all_managers"])})'
                if im["multi_manager"] else
                f'{_mgr_emoji(im["primary_manager"])} {im["primary_manager"]}'
            )
            yr_pills = "".join(_yr_pill(s, c) for s in im["seasons"])
            col.markdown(
                f'<div style="background:#081120;border:1px solid #1E2D40;border-left:3px solid {c};'
                f'border-radius:5px;padding:10px 12px;margin-bottom:8px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:baseline;">'
                f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F5F5;">'
                f'{im["player_name"]}</span>'
                f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:{c};">'
                f'{im["streak_len"]}</span></div>'
                f'<div style="font-size:0.6rem;color:#A7B0BC;margin:2px 0;">{mgr_str}</div>'
                f'<div style="display:flex;flex-wrap:wrap;gap:2px;margin-top:5px;">{yr_pills}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 2 — KEEPERS THAT WON TITLES
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("CHAMPIONS KEPT THEIR BEST", "Players on Championship Rosters"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Every player kept on a championship-winning roster. The common thread in title runs.</p>',
    unsafe_allow_html=True,
)

champ_keepers = ke[ke["won_title"] == True].copy()

if len(champ_keepers) > 0:
    # Players kept on multiple championship rosters
    player_champ_agg = (
        champ_keepers.groupby("player_name")
        .agg(
            title_count=("won_title", "sum"),
            champ_seasons=("season", list),
            champ_managers=("manager", list),
            position=("position", "first"),
        )
        .sort_values("title_count", ascending=False)
        .reset_index()
    )

    # Multi-title keepers (appeared on 2+ championship rosters)
    multi = player_champ_agg[player_champ_agg["title_count"] >= 2]
    single = player_champ_agg[player_champ_agg["title_count"] == 1]

    if len(multi) > 0:
        st.markdown(
            '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:#D4AF37;'
            'letter-spacing:3px;margin-bottom:0.75rem;">MULTI-CHAMPIONSHIP KEEPERS</div>',
            unsafe_allow_html=True,
        )
        multi_html = '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:1.5rem;">'
        for _, row in multi.iterrows():
            pb = _pos_badge(str(row["position"]) if row["position"] else "?")
            mgrs = row["champ_managers"]
            szns = row["champ_seasons"]
            mgr_str = " / ".join(sorted(set(mgrs)))
            seasons_str = " · ".join(str(s) for s in sorted(set(szns)))
            multi_html += (
                f'<div style="background:#0F1B2D;border:1px solid #D4AF3744;border-top:3px solid #D4AF37;'
                f'border-radius:6px;padding:12px 16px;min-width:180px;flex:1;">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                f'{"🏆" * int(row["title_count"])}'
                f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:#F5F5F5;'
                f'letter-spacing:2px;">{row["player_name"]}</span>'
                f'{pb}</div>'
                f'<div style="font-size:0.62rem;color:#A7B0BC;">{mgr_str}</div>'
                f'<div style="font-size:0.62rem;color:#D4AF37;margin-top:3px;">{seasons_str}</div>'
                f'</div>'
            )
        multi_html += '</div>'
        st.markdown(multi_html, unsafe_allow_html=True)

    # Championship timeline — each title year and what was kept
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
        'letter-spacing:3px;margin-bottom:0.75rem;">CHAMPIONSHIP KEEPER BREAKDOWN BY YEAR</div>',
        unsafe_allow_html=True,
    )

    champ_by_year = champ_keepers.sort_values("season", ascending=False)
    years_shown = sorted(champ_by_year["season"].unique(), reverse=True)
    yr_cols = st.columns(min(4, len(years_shown)))

    for i, szn in enumerate(years_shown):
        col_idx = i % len(yr_cols)
        yr_data = champ_by_year[champ_by_year["season"] == szn].sort_values("round")
        mgr = yr_data["manager"].iloc[0]
        c = _mgr_color(mgr)
        em = _mgr_emoji(mgr)
        players_html = "".join(
            f'<div style="font-size:0.65rem;color:#F5F5F5;padding:2px 0;">'
            f'{_pos_badge(str(row["position"]) if row["position"] else "?")} {row["player_name"]}'
            f'<span style="color:#4B5563;font-size:0.55rem;"> (Rd {row["round"]})</span>'
            f'</div>'
            for _, row in yr_data.iterrows()
        )
        yr_cols[col_idx].markdown(
            f'<div style="background:#081120;border:1px solid {c}33;border-top:2px solid {c};'
            f'border-radius:5px;padding:10px 12px;margin-bottom:8px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.2rem;color:#D4AF37;">🏆 {szn}</div>'
            f'<div style="font-size:0.65rem;color:#A7B0BC;margin-bottom:6px;">{em} {mgr}</div>'
            f'{players_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("No championship keeper data found.")

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 3 — KEEPER DNA
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("KEEPER DNA", "Manager Keeper Identities"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Every manager has a keeper philosophy. Some hoard running backs. Some found elite TEs early. '
    'Some kept whoever just won them the title.</p>',
    unsafe_allow_html=True,
)

_DNA_LABELS = {
    "BELL COW HUNTER": "Staked the franchise on elite RBs. Kept the workhorse, season after season.",
    "RECEIVER KINGDOM": "Built through the pass-catchers. Wide receivers were the currency.",
    "SIGNAL CALLER": "Bet on quarterbacks at a position most managers left to the draft.",
    "TIGHT END LOYALIST": "Found the value others ignored. Elite TEs don't hit free agency.",
    "SKILL POSITION SNIPER": "No positional bias. Any skill player, any round, any season.",
    "BALANCED CURATOR": "A methodical approach. Position was secondary to player quality.",
}

def _dna_label(mgr_keepers):
    pos_c = mgr_keepers[mgr_keepers["position"].isin(POS_COLORS.keys())]["position"].value_counts()
    total = pos_c.sum()
    if total == 0:
        return "BALANCED CURATOR"
    rb_p = pos_c.get("RB", 0) / total
    wr_p = pos_c.get("WR", 0) / total
    qb_p = pos_c.get("QB", 0) / total
    te_p = pos_c.get("TE", 0) / total
    if rb_p >= 0.55:
        return "BELL COW HUNTER"
    if wr_p >= 0.50:
        return "RECEIVER KINGDOM"
    if qb_p >= 0.25:
        return "SIGNAL CALLER"
    if te_p >= 0.20:
        return "TIGHT END LOYALIST"
    if rb_p + wr_p >= 0.80:
        return "SKILL POSITION SNIPER"
    return "BALANCED CURATOR"

# Per-manager keeper stats for DNA cards
dna_stats = []
for mgr, kgrp in keepers.groupby("manager"):
    total_picks = len(dpw[dpw["manager"] == mgr])
    k_count = len(kgrp)
    if k_count == 0:
        continue
    k_rate = k_count / total_picks if total_picks > 0 else 0
    indiv = kgrp[kgrp["position"] != "DEF"]
    fav_k = indiv["player_name"].value_counts().index[0] if len(indiv) > 0 else "—"
    fav_k_n = int(indiv["player_name"].value_counts().iloc[0]) if len(indiv) > 0 else 0
    # Longest streak for this manager
    mgr_chains = chains[chains["all_managers"].apply(lambda m: mgr in m)]
    longest = int(mgr_chains["streak_len"].max()) if len(mgr_chains) > 0 else 1
    longest_player = mgr_chains.loc[mgr_chains["streak_len"].idxmax(), "player_name"] if len(mgr_chains) > 0 else "—"
    # Championship seasons
    mgr_ke = ke[ke["manager"] == mgr]
    titles = int(mgr_ke["won_title"].sum())
    dna = _dna_label(kgrp)
    dna_stats.append({
        "manager": mgr, "k_count": k_count, "k_rate": k_rate,
        "fav_k": fav_k, "fav_k_n": fav_k_n,
        "longest": longest, "longest_player": longest_player,
        "titles": titles, "dna": dna,
    })

dna_stats = sorted(dna_stats, key=lambda x: -x["k_count"])

# Baseball card style grid
dna_html = '<div style="display:flex;flex-wrap:wrap;gap:12px;margin-top:0.5rem;">'
for stat in dna_stats:
    mgr = stat["manager"]
    color = _mgr_color(mgr)
    em = _mgr_emoji(mgr)
    label = stat["dna"]
    desc = _DNA_LABELS.get(label, "")
    title_str = f'{"🏆" * stat["titles"]}' if stat["titles"] > 0 else ""
    dna_html += (
        f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-top:3px solid {color};'
        f'border-radius:6px;padding:12px 14px;min-width:180px;flex:1;max-width:260px;">'
        f'<div style="font-size:1.8rem;margin-bottom:4px;">{em}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1rem;color:#F5F5F5;'
        f'letter-spacing:2px;margin-bottom:2px;">{mgr} {title_str}</div>'
        f'<div style="background:{color}22;border-radius:3px;padding:2px 6px;display:inline-block;'
        f'font-family:\'Bebas Neue\',sans-serif;font-size:0.65rem;color:{color};'
        f'letter-spacing:2px;margin-bottom:6px;">{label}</div>'
        f'<div style="font-size:0.6rem;color:#6B7280;margin-bottom:8px;line-height:1.4;">{desc}</div>'
        f'<div style="border-top:1px solid #1E2D40;padding-top:6px;">'
        f'<div style="font-size:0.62rem;color:#A7B0BC;">'
        f'{stat["k_count"]} keepers &nbsp;·&nbsp; {stat["k_rate"]*100:.0f}% rate</div>'
        f'<div style="font-size:0.62rem;color:#A7B0BC;margin-top:2px;">'
        f'Longest run: <span style="color:#F5F5F5;">{stat["longest_player"]} ({stat["longest"]}yr)</span></div>'
        f'<div style="font-size:0.62rem;color:#A7B0BC;margin-top:2px;">'
        f'Most kept: <span style="color:#F5F5F5;">{stat["fav_k"]}'
        f'{(" ×" + str(stat["fav_k_n"])) if stat["fav_k_n"] > 1 else ""}</span></div>'
        f'</div></div>'
    )
dna_html += '</div>'
st.markdown(dna_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 4 — THE MOST COVETED
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE MOST COVETED", "Player Keeper Timelines"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Top kept players across all seasons. Expand any player to see who owned them best.</p>',
    unsafe_allow_html=True,
)

top_kept = (
    keepers[keepers["position"] != "DEF"]
    .groupby("player_name").size()
    .sort_values(ascending=False)
    .head(20)
)

keeper_map = {}
for _, row in keepers.iterrows():
    keeper_map[(row["player_name"], int(row["season"]))] = (row["manager"], row["franchise_id"])

tl_html = (
    '<div style="overflow-x:auto;">'
    '<table style="border-collapse:collapse;font-family:\'Inter\',sans-serif;font-size:0.65rem;width:100%;">'
    '<thead><tr>'
    '<th style="text-align:left;padding:4px 8px;color:#A7B0BC;min-width:160px;border-bottom:1px solid #1E2D40;">PLAYER</th>'
    '<th style="padding:4px 4px;color:#A7B0BC;border-bottom:1px solid #1E2D40;">POS</th>'
)
for szn in active_keeper_szns:
    susp = szn in _KEEPER_SUSPENSION_YEARS
    clr = "#4B5563" if susp else "#A7B0BC"
    lbl = "—" if susp else f"'{str(szn)[-2:]}"
    tl_html += (
        f'<th style="padding:2px 3px;color:{clr};border-bottom:1px solid #1E2D40;'
        f'text-align:center;min-width:26px;" title="{"Keepers suspended" if susp else szn}">'
        f'{lbl}</th>'
    )
tl_html += '<th style="padding:4px 6px;color:#A7B0BC;border-bottom:1px solid #1E2D40;">TOTAL</th></tr></thead><tbody>'

for i, (player, count) in enumerate(top_kept.items()):
    bg = "rgba(255,255,255,0.02)" if i % 2 == 0 else "transparent"
    pos_val = keepers[keepers["player_name"] == player]["position"].iloc[0] if len(keepers[keepers["player_name"] == player]) > 0 else "?"
    pb = _pos_badge(str(pos_val) if pos_val else "?")
    tl_html += (
        f'<tr style="background:{bg};">'
        f'<td style="padding:5px 8px;color:#F5F5F5;font-weight:600;white-space:nowrap;">{player}</td>'
        f'<td style="padding:5px 4px;text-align:center;">{pb}</td>'
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
    tl_html += f'<td style="padding:5px 6px;text-align:center;font-weight:700;color:#D4AF37;">{int(count)}</td></tr>'

tl_html += '</tbody></table></div>'

shown_mgrs = sorted(keepers[keepers["player_name"].isin(top_kept.index)]["manager"].unique())
legend_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;margin:1rem 0 1.5rem;">'
for mgr in shown_mgrs:
    c = _mgr_color(mgr)
    em = _mgr_emoji(mgr)
    legend_html += (
        f'<span style="background:{c}22;border:1px solid {c};border-radius:4px;'
        f'padding:2px 8px;font-size:0.62rem;font-family:\'Inter\',sans-serif;color:#F5F5F5;">'
        f'{em} {mgr}</span>'
    )
legend_html += '</div><p style="font-size:0.62rem;color:#4B5563;font-family:\'Inter\',sans-serif;">— = Keeper format suspended (2005, 2011)</p>'

st.markdown(legend_html + tl_html, unsafe_allow_html=True)

# Per-player expanders — "Who Owned Him Best?"
st.markdown(
    '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.75rem;color:#A7B0BC;'
    'letter-spacing:3px;margin:1.5rem 0 0.75rem;">WHO OWNED THEM BEST? — EXPAND ANY PLAYER</div>',
    unsafe_allow_html=True,
)

top12 = list(top_kept.index[:12])
expand_cols = st.columns(3)
for idx, player in enumerate(top12):
    col = expand_cols[idx % 3]
    with col:
        player_ke = ke[ke["player_name"] == player].copy()
        pos_val = str(player_ke["position"].iloc[0]) if len(player_ke) > 0 and player_ke["position"].notna().any() else "?"
        total_keeper_szns = len(player_ke)
        pb_inline = _pos_badge(pos_val)

        with st.expander(f"{player} ({total_keeper_szns}× kept)"):
            mgr_breakdown = []
            for mgr, mgr_grp in player_ke.groupby("manager"):
                seasons = sorted(mgr_grp["season"].astype(int).tolist())
                w = int(mgr_grp["wins"].sum())
                lg = int(mgr_grp["losses"].sum())
                titles = int(mgr_grp["won_title"].sum())
                mgr_breakdown.append({
                    "manager": mgr, "seasons": seasons, "count": len(seasons),
                    "wins": w, "losses": lg, "titles": titles,
                })
            mgr_breakdown.sort(key=lambda x: -x["count"])

            for mb in mgr_breakdown:
                c = _mgr_color(mb["manager"])
                em = _mgr_emoji(mb["manager"])
                szn_pills = "".join(_yr_pill(s, c) for s in mb["seasons"])
                record_str = f'{mb["wins"]}-{mb["losses"]}' if mb["wins"] + mb["losses"] > 0 else "—"
                title_str = f' · {"🏆" * mb["titles"]}' if mb["titles"] > 0 else ""
                st.markdown(
                    f'<div style="background:#081120;border-left:3px solid {c};'
                    f'border-radius:4px;padding:8px 10px;margin-bottom:6px;">'
                    f'<div style="font-size:0.7rem;color:#F5F5F5;font-weight:600;">'
                    f'{em} {mb["manager"]} — {mb["count"]}× kept</div>'
                    f'<div style="font-size:0.62rem;color:#A7B0BC;">'
                    f'Record during keeper run: {record_str}{title_str}</div>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:2px;margin-top:5px;">{szn_pills}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 5 — POSITION ERA ANALYSIS
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE SHIFTING TIDE", "Keeper Position Evolution"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'How keeper strategy evolved over 25 years. The RB-dominated early era gave way '
    'to a more diverse approach as the game changed.</p>',
    unsafe_allow_html=True,
)

_ERA_POSITIONS = ["RB", "WR", "QB", "TE"]
ke_pos = ke[ke["position"].isin(_ERA_POSITIONS)].copy()
era_raw = (
    ke_pos.groupby(["season", "position"]).size()
    .unstack(fill_value=0)
    .reset_index()
)
for p in _ERA_POSITIONS:
    if p not in era_raw.columns:
        era_raw[p] = 0

era_raw["total"] = era_raw[[p for p in _ERA_POSITIONS]].sum(axis=1)
era_pct = era_raw.copy()
for p in _ERA_POSITIONS:
    era_pct[p] = (era_raw[p] / era_raw["total"].replace(0, 1) * 100).round(1)

fig_era = go.Figure()
era_traces = [
    ("TE", "tozeroy"),
    ("QB", "tonexty"),
    ("WR", "tonexty"),
    ("RB", "tonexty"),
]
for p, fill in era_traces:
    if p not in era_pct.columns:
        continue
    fig_era.add_trace(go.Scatter(
        x=era_pct["season"].tolist(),
        y=era_pct[p].tolist(),
        name=p,
        mode="lines",
        fill=fill,
        line=dict(width=1.5, color=POS_COLORS[p]),
        fillcolor="rgba({},{},{},0.33)".format(
            int(POS_COLORS[p][1:3], 16),
            int(POS_COLORS[p][3:5], 16),
            int(POS_COLORS[p][5:7], 16),
        ),
        hovertemplate=f"<b>%{{x}}</b><br>{p}: %{{y:.1f}}%<extra></extra>",
        stackgroup="one",
    ))

fig_era.add_vrect(x0=2002.5, x1=2008.5, fillcolor="#D4AF37", opacity=0.04,
                  line_width=0, annotation_text="RB ERA", annotation_position="top left",
                  annotation=dict(font_size=9, font_color="#D4AF37"))
fig_era.add_vrect(x0=2008.5, x1=2015.5, fillcolor="#3B82F6", opacity=0.04,
                  line_width=0, annotation_text="TRANSITION", annotation_position="top left",
                  annotation=dict(font_size=9, font_color="#3B82F6"))
fig_era.add_vrect(x0=2015.5, x1=2025.5, fillcolor="#22C55E", opacity=0.04,
                  line_width=0, annotation_text="MODERN ERA", annotation_position="top left",
                  annotation=dict(font_size=9, font_color="#22C55E"))

fig_era.update_layout(
    plot_bgcolor="#081120", paper_bgcolor="#081120",
    font=dict(family="Inter", color="#F5F5F5", size=10),
    xaxis=dict(title="Season", gridcolor="#1E2D40", dtick=2),
    yaxis=dict(title="Share of Keepers (%)", gridcolor="#1E2D40", range=[0, 100]),
    legend=dict(orientation="h", y=1.08, x=0, font=dict(size=10)),
    margin=dict(l=50, r=20, t=40, b=40),
    height=340,
    hovermode="x unified",
)
st.plotly_chart(fig_era, use_container_width=True, config={"displayModeBar": False})

# Era summary callouts
era_a = era_pct[era_pct["season"].between(2003, 2008)]
era_b = era_pct[era_pct["season"].between(2009, 2015)]
era_c = era_pct[era_pct["season"].between(2016, 2025)]

era_col_a, era_col_b, era_col_c = st.columns(3)
for col, era_data, era_name, era_years, era_color in [
    (era_col_a, era_a, "The RB Era", "2003–2008", "#D4AF37"),
    (era_col_b, era_b, "The Transition", "2009–2015", "#3B82F6"),
    (era_col_c, era_c, "The Modern Era", "2016–2025", "#22C55E"),
]:
    if len(era_data) == 0:
        continue
    rb_avg = era_data["RB"].mean()
    wr_avg = era_data["WR"].mean()
    top_pos = "RB" if rb_avg > wr_avg else "WR"
    col.markdown(
        f'<div style="background:#081120;border-left:3px solid {era_color};'
        f'border-radius:5px;padding:10px 14px;margin-bottom:8px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.9rem;color:{era_color};">'
        f'{era_name}</div>'
        f'<div style="font-size:0.62rem;color:#A7B0BC;">{era_years}</div>'
        f'<div style="margin-top:6px;">'
        f'<div style="font-size:0.65rem;color:#F5F5F5;">RB avg: {rb_avg:.0f}%</div>'
        f'<div style="font-size:0.65rem;color:#F5F5F5;">WR avg: {wr_avg:.0f}%</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 6 — THE ONES THAT GOT AWAY
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE ONES THAT GOT AWAY", "When Great Keeper Runs Ended"), unsafe_allow_html=True)
st.markdown(
    '<p style="font-family:\'Inter\',sans-serif;color:#A7B0BC;font-size:0.78rem;margin:-0.5rem 0 1.5rem;">'
    'Keeper dynasties that ended. Every great run has a last season. '
    'These are the players a franchise finally let go.</p>',
    unsafe_allow_html=True,
)

# Chains with streak ≥ 2 that ended before current season
ended = (
    chains[(chains["streak_len"] >= 2) & (chains["last_season"] < CURRENT_SEASON)]
    .sort_values(["streak_len", "last_season"], ascending=[False, False])
    .head(12)
)

if len(ended) > 0:
    ended_cols = st.columns(2)
    for i, (_, ch) in enumerate(ended.iterrows()):
        col = ended_cols[i % 2]
        player = ch["player_name"]
        mgrs = ch["all_managers"]
        primary = ch["primary_manager"]
        c = _mgr_color(primary)
        pos_val = ke[ke["player_name"] == player]["position"].dropna()
        pos = str(pos_val.iloc[0]) if len(pos_val) > 0 else "?"
        pb = _pos_badge(pos)
        seasons = ch["seasons"]
        last = ch["last_season"]
        streak = ch["streak_len"]

        mgr_str = (
            f'{ch["franchise_id"]} ({" → ".join(mgrs)})'
            if ch["multi_manager"] else
            f'{_mgr_emoji(primary)} {primary}'
        )

        # Check if same player was kept again later by anyone (different chain)
        later_chains = chains[
            (chains["player_name"] == player) &
            (chains["first_season"] > last)
        ]
        comeback_str = ""
        if len(later_chains) > 0:
            lc = later_chains.iloc[0]
            comeback_str = (
                f'<div style="font-size:0.62rem;color:#22C55E;margin-top:4px;">'
                f'↩ Kept again by {lc["primary_manager"]} starting {lc["first_season"]}</div>'
            )

        yr_pills = "".join(_yr_pill(s, c) for s in seasons)
        col.markdown(
            f'<div style="background:#0F1B2D;border:1px solid #1E2D40;border-left:4px solid {c};'
            f'border-radius:6px;padding:12px 14px;margin-bottom:10px;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;color:#F5F5F5;">'
            f'{player}</div>{pb}</div>'
            f'<div style="font-size:0.63rem;color:#A7B0BC;">{mgr_str}</div>'
            f'<div style="font-size:0.62rem;color:#6B7280;margin:3px 0;">'
            f'Kept {streak} consecutive seasons · last seen {last}</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:2px;margin-top:6px;">{yr_pills}</div>'
            f'{comeback_str}'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 7 — KEEPER RECORD BOOK
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("THE RECORD BOOK", "Keeper Records & Superlatives"), unsafe_allow_html=True)

# Compute records
mgr_keeper_totals = keepers.groupby("manager").size().sort_values(ascending=False)
most_keepers_mgr = mgr_keeper_totals.index[0]
most_keepers_n = int(mgr_keeper_totals.iloc[0])

# Most keepers in a single season
mgr_szn_k = keepers.groupby(["season", "manager"]).size().reset_index(name="k_count")
mgr_szn_k_max = mgr_szn_k.loc[mgr_szn_k["k_count"].idxmax()]
single_szn_mgr = str(mgr_szn_k_max["manager"])
single_szn_n = int(mgr_szn_k_max["k_count"])
single_szn_yr = int(mgr_szn_k_max["season"])

# Most expensive keeper (lowest round, excluding suspension era rounds 15)
modern_keepers = ke[ke["keeper_cost_round"] < 15].copy()
if len(modern_keepers) > 0:
    cheapest_round = modern_keepers["keeper_cost_round"].max()
    cheapest_row = modern_keepers[modern_keepers["keeper_cost_round"] == cheapest_round].iloc[0]
    most_expensive_round = modern_keepers["keeper_cost_round"].min()
    most_expensive_row = modern_keepers[modern_keepers["keeper_cost_round"] == most_expensive_round].iloc[0]

# First player ever kept
if len(keepers) > 0:
    first_ever = keepers.sort_values("season").iloc[0]
    first_ever_player = str(first_ever["player_name"])
    first_ever_mgr = str(first_ever["manager"])
    first_ever_szn = int(first_ever["season"])

# Most unique keepers by manager (never repeated)
mgr_unique_k = keepers.groupby("manager")["player_name"].nunique().sort_values(ascending=False)
most_diverse_mgr = str(mgr_unique_k.index[0])
most_diverse_n = int(mgr_unique_k.iloc[0])

# Keeper who changed franchises most (appeared in most different franchise IDs)
player_fids = keepers.groupby("player_name")["franchise_id"].nunique().sort_values(ascending=False)
most_franchises_player = str(player_fids.index[0])
most_franchises_n = int(player_fids.iloc[0])

records = [
    ("Most Keepers (Career)", f"{most_keepers_mgr}", f"{most_keepers_n} keeper seasons"),
    ("Most Keepers (Single Season)", f"{single_szn_mgr}, {single_szn_yr}", f"{single_szn_n} keepers in one draft"),
    ("Most Times Kept (Player)", most_kept_player, f"Kept {most_kept_count}× total"),
    ("Longest Single Streak", immortal_df.iloc[0]["player_name"] if len(immortal_df) > 0 else "—",
     f'{longest_streak} consecutive seasons'),
    ("Most Diverse Keeper Portfolio", most_diverse_mgr, f"{most_diverse_n} different players kept"),
    ("Most Franchises (Player)", most_franchises_player, f"Kept by {most_franchises_n} different franchises"),
    ("First Keeper Ever", f"{first_ever_player} ({first_ever_mgr})" if len(keepers) > 0 else "—",
     f"Season {first_ever_szn}" if len(keepers) > 0 else ""),
    ("Most Valuable Keeper Run", immortal_df.iloc[0]["player_name"] if len(immortal_df) > 0 else "—",
     f'Score {immortal_df.iloc[0]["score"]:.1f}' if len(immortal_df) > 0 else ""),
]
if len(modern_keepers) > 0:
    records.insert(5, ("Cheapest Keeper (Highest Rd)", f'{cheapest_row["player_name"]} ({cheapest_row["manager"]})',
                       f'Round {cheapest_round} in {int(cheapest_row["season"])}'))
    records.insert(5, ("Most Expensive Keeper (Lowest Rd)", f'{most_expensive_row["player_name"]} ({most_expensive_row["manager"]})',
                       f'Round {most_expensive_round} in {int(most_expensive_row["season"])}'))

rb_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px;">'
for rec_label, rec_val, rec_sub in records:
    rb_html += (
        f'<div style="background:#081120;border:1px solid #1E2D40;border-radius:5px;padding:12px 14px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.65rem;color:#A7B0BC;'
        f'letter-spacing:2px;margin-bottom:4px;">{rec_label}</div>'
        f'<div style="font-size:0.85rem;color:#F5F5F5;font-weight:600;">{rec_val}</div>'
        f'<div style="font-size:0.62rem;color:#D4AF37;margin-top:2px;">{rec_sub}</div>'
        f'</div>'
    )
rb_html += '</div>'
st.markdown(rb_html, unsafe_allow_html=True)

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# SECTION 8 — KEEPER POSITION ANALYSIS (league-wide + per manager)
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(section_header("WHAT THEY HOARDED", "Keeper Position Analysis"), unsafe_allow_html=True)

pos_col, mgr_col = st.columns([1, 2])

with pos_col:
    st.markdown(
        '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.8rem;color:#A7B0BC;'
        'letter-spacing:3px;margin-bottom:0.75rem;">LEAGUE-WIDE</div>',
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
        'letter-spacing:3px;margin-bottom:0.75rem;">BY MANAGER</div>',
        unsafe_allow_html=True,
    )
    mgr_keeper_pos = (
        keepers[keepers["position"].isin(POS_COLORS.keys())]
        .groupby(["manager", "position"]).size()
        .unstack(fill_value=0)
    )
    mgr_keeper_pos["total"] = mgr_keeper_pos.sum(axis=1)
    mgr_keeper_pos = mgr_keeper_pos[mgr_keeper_pos["total"] >= 3]

    fig_kp = go.Figure()
    kp_sorted = mgr_keeper_pos.sort_values("RB" if "RB" in mgr_keeper_pos.columns else "total", ascending=True)
    for pos in ["K", "DEF", "TE", "QB", "WR", "RB"]:
        if pos not in kp_sorted.columns:
            continue
        pcts = (kp_sorted[pos] / kp_sorted["total"] * 100).round(1)
        fig_kp.add_trace(go.Bar(
            name=pos, y=kp_sorted.index.tolist(), x=pcts.tolist(),
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
        height=max(260, len(kp_sorted) * 26 + 70),
    )
    st.plotly_chart(fig_kp, use_container_width=True, config={"displayModeBar": False})

st.markdown('<hr class="tl-divider-full">', unsafe_allow_html=True)

render_page_footer(
    href="/draft_center",
    cta="BACK TO THE DRAFT CENTER",
    tagline="THE KEEPERS WERE COVETED.<br>THE DRAFT IS WHERE IT ALL STARTED.",
)
