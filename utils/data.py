"""Central data loading and derived metrics for The Long Game."""
from __future__ import annotations
import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

LEAGUE_NAME = "The Long Game"
LEAGUE_SUBTITLE = "A Quarter Century of {insert witty name here} Glory"
FOUNDED = 2001
CURRENT_SEASON = 2025

MANAGER_COLORS = {
    "Shawn":         "#D4AF37",
    "Brian Clark":   "#3B82F6",
    "Dominic":       "#EF4444",
    "Kevin O'Boyle": "#10B981",
    "Kevin Swanson": "#F59E0B",
    "Thomas":        "#8B5CF6",
    "Evan":          "#EC4899",
    "Steve Swanson": "#14B8A6",
    "Fadi":          "#F97316",
    "Douglas":       "#6366F1",
    "Jeff":          "#84CC16",
    "Eric":          "#06B6D4",
    "Jamie":         "#A78BFA",
    "Nick Blaettler":"#FB923C",
    "Adam":          "#F43F5E",
    "Rob":           "#94A3B8",
    "Byron":         "#C084FC",
    "Dan":           "#4ADE80",
    "Dale":          "#FCD34D",
    "Bryan Kearney": "#60A5FA",
    "Joe Tyszko":    "#34D399",
    "Mike":          "#FCA5A5",
    "Robby":         "#93C5FD",
    "BV":            "#6B7280",
}

MANAGER_EMOJI = {
    "Shawn": "🐝",
    "Fadi": "👑",
    "Brian Clark": "🍺",
    "Kevin O'Boyle": "🍺",
    "Kevin Swanson": "🧔",
    "Thomas": "🐻",
    "Evan": "🎉",
    "Steve Swanson": "🐻",
    "Dominic": "🏈",
    "Douglas": "⚙️",
    "Jeff": "⚽",
    "Eric": "⛳",
    "Jamie": "😇",
    "Mike": "🍻",
    "Joe Tyszko": "🌽",
    "Robby": "🎸",
    "Rob": "⚔️",
    "Byron": "🏛️",
    "Dan": "📖",
    "Dale": "🌪️",
    "Bryan Kearney": "💪",
    "BV": "❓",
    "Adam": "🎯",
    "Nick Blaettler": "🐱",
}


@st.cache_data
def load_all() -> dict:
    _cache_bust = 2  # increment to force re-read when CSV data changes
    files = {
        "standings": "season_standings.csv",
        "playoff_games": "playoff_games.csv",
        "weekly_matchups": "weekly_matchups.csv",
        "managers": "managers.csv",
        "season_managers": "season_managers.csv",
        "team_name_history": "team_name_history.csv",
        "franchise_history": "franchise_history.csv",
        "draft_picks": "draft_picks.csv",
        "player_positions": "player_positions.csv",
        "season_trades": "season_trades.csv",
        "league_settings": "league_settings.csv",
        "manager_lookup": "manager_lookup.csv",
    }
    return {key: pd.read_csv(DATA_DIR / fname) for key, fname in files.items()}


@st.cache_data
def get_champions() -> pd.DataFrame:
    _cache_bust = 1
    data = load_all()
    pg = data["playoff_games"]
    tnh = data["team_name_history"]

    tnh_map = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

    finals = pg[
        (pg["game_type"] == "final") & (pg["bracket"] == "championship")
    ].copy()

    def resolve(season, team):
        return tnh_map.get((int(season), team), team)

    finals["champion_team"] = finals["winner"]
    finals["champion_manager"] = finals.apply(
        lambda r: resolve(r["season"], r["winner"]), axis=1
    )
    finals["champion_score"] = finals.apply(
        lambda r: float(r["score_1"]) if r["winner"] == r["team_1"] else float(r["score_2"]),
        axis=1,
    )
    finals["runner_up_team"] = finals.apply(
        lambda r: r["team_2"] if r["winner"] == r["team_1"] else r["team_1"], axis=1
    )
    finals["runner_up_manager"] = finals.apply(
        lambda r: resolve(r["season"], r["team_2"] if r["winner"] == r["team_1"] else r["team_1"]),
        axis=1,
    )
    finals["runner_up_score"] = finals.apply(
        lambda r: float(r["score_2"]) if r["winner"] == r["team_1"] else float(r["score_1"]),
        axis=1,
    )

    return finals[[
        "season", "champion_team", "champion_manager", "champion_score",
        "runner_up_team", "runner_up_manager", "runner_up_score",
    ]].sort_values("season").reset_index(drop=True)


@st.cache_data
def get_manager_stats() -> pd.DataFrame:
    _cache_bust = 1
    data = load_all()
    wm = data["weekly_matchups"]
    tnh = data["team_name_history"]
    managers_df = data["managers"]
    pg = data["playoff_games"]

    champions = get_champions()

    # Regular season record via vectorised merge
    rs = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
    rs_merged = tnh.merge(rs, on=["season", "team_name"], how="inner")
    record = (
        rs_merged.groupby("canonical_name")
        .apply(lambda g: pd.Series({
            "wins": int((g["result"] == "Win").sum()),
            "losses": int((g["result"] == "Loss").sum()),
            "ties": int((g["result"] == "Tie").sum()),
            "points_for": round(g["team_score"].sum(), 2),
        }))
        .reset_index()
    )

    # Playoff appearances (championship bracket, distinct seasons)
    champ_pg = pg[pg["bracket"] == "championship"].copy()
    team_playoff = pd.concat([
        champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
        champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
    ]).drop_duplicates()
    playoff_merged = tnh.merge(team_playoff, on=["season", "team_name"], how="inner")
    playoff_apps = (
        playoff_merged.groupby("canonical_name")["season"]
        .nunique()
        .reset_index(name="playoff_apps")
    )

    # Championships and runner-ups
    champ_counts = (
        champions.groupby("champion_manager").size()
        .reset_index(name="championships")
        .rename(columns={"champion_manager": "canonical_name"})
    )
    ru_counts = (
        champions.groupby("runner_up_manager").size()
        .reset_index(name="runner_ups")
        .rename(columns={"runner_up_manager": "canonical_name"})
    )

    stats = managers_df[[
        "canonical_name", "display_name", "first_season", "last_season", "seasons_played"
    ]].copy()
    stats = stats.merge(record, on="canonical_name", how="left")
    stats = stats.merge(playoff_apps, on="canonical_name", how="left")
    stats = stats.merge(champ_counts, on="canonical_name", how="left")
    stats = stats.merge(ru_counts, on="canonical_name", how="left")

    for col in ["wins", "losses", "ties", "playoff_apps", "championships", "runner_ups"]:
        stats[col] = stats[col].fillna(0).astype(int)
    stats["points_for"] = stats["points_for"].fillna(0.0)

    total = stats["wins"] + stats["losses"] + stats["ties"]
    stats["win_pct"] = (stats["wins"] / total.replace(0, pd.NA)).round(3)
    stats["active"] = stats["last_season"] == CURRENT_SEASON

    return stats.sort_values(
        ["championships", "playoff_apps", "wins"], ascending=False
    ).reset_index(drop=True)


@st.cache_data
def get_manager_season_history(canonical_name: str) -> pd.DataFrame:
    data = load_all()
    tnh = data["team_name_history"]
    wm = data["weekly_matchups"]
    standings = data["standings"]
    pg = data["playoff_games"]
    champions = get_champions()

    mgr_seasons = tnh[tnh["canonical_name"] == canonical_name].copy()
    results = []

    for _, row in mgr_seasons.iterrows():
        season = int(row["season"])
        team = row["team_name"]

        # Regular season record
        rs = wm[
            (wm["season"] == season)
            & (wm["team_name"] == team)
            & (~wm["is_bye"])
            & (~wm["is_playoff"])
        ]
        wins = int((rs["result"] == "Win").sum())
        losses = int((rs["result"] == "Loss").sum())
        ties = int((rs["result"] == "Tie").sum())
        pf = round(float(rs["team_score"].dropna().sum()), 2)
        pa = round(float(rs["opponent_score"].dropna().sum()), 2)

        # Standing
        std = standings[(standings["season"] == season) & (standings["team_name"] == team)]
        rank = int(std.iloc[0]["rank"]) if len(std) > 0 else None

        # Playoff result
        playoff_result = _playoff_result(season, team, pg)

        results.append({
            "Season": season,
            "Team Name": team,
            "W": wins,
            "L": losses,
            "T": ties,
            "PF": pf,
            "PA": pa,
            "Rank": rank,
            "Result": playoff_result,
        })

    return pd.DataFrame(results).sort_values("Season", ascending=False).reset_index(drop=True)


@st.cache_data
def get_franchise_steward_periods() -> pd.DataFrame:
    data = load_all()
    fh = data["franchise_history"].sort_values(["franchise_id", "season"])

    periods = []
    for fid, group in fh.groupby("franchise_id"):
        current_mgr = None
        start = None
        prev_season = None

        for _, row in group.iterrows():
            mgr = row["manager_name"]
            season = int(row["season"])
            if mgr != current_mgr:
                if current_mgr is not None:
                    periods.append({
                        "franchise_id": fid,
                        "manager_name": current_mgr,
                        "start_season": start,
                        "end_season": prev_season,
                        "years": prev_season - start + 1,
                    })
                current_mgr = mgr
                start = season
            prev_season = season

        if current_mgr:
            periods.append({
                "franchise_id": fid,
                "manager_name": current_mgr,
                "start_season": start,
                "end_season": prev_season,
                "years": prev_season - start + 1,
            })

    return pd.DataFrame(periods)


@st.cache_data
def get_franchise_stats() -> pd.DataFrame:
    data = load_all()
    fh = data["franchise_history"]
    tnh = data["team_name_history"]
    wm = data["weekly_matchups"]
    pg = data["playoff_games"]
    champions = get_champions()

    # Map franchise seasons to team names
    fh_tnh = fh.merge(
        tnh.rename(columns={"canonical_name": "manager_name"}),
        on=["season", "manager_name"],
        how="left",
    )

    # Regular season record per franchise
    rs = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
    rs_merged = fh_tnh.merge(rs, on=["season", "team_name"], how="inner")
    record = (
        rs_merged.groupby("franchise_id")
        .apply(lambda g: pd.Series({
            "wins": int((g["result"] == "Win").sum()),
            "losses": int((g["result"] == "Loss").sum()),
            "ties": int((g["result"] == "Tie").sum()),
        }))
        .reset_index()
    )

    # Championships per franchise
    champ_teams = champions[["season", "champion_team"]].rename(
        columns={"champion_team": "team_name"}
    )
    fh_champs = fh_tnh.merge(champ_teams, on=["season", "team_name"], how="inner")
    champ_count = (
        fh_champs.groupby("franchise_id").size().reset_index(name="championships")
    )

    # Playoff appearances per franchise (distinct seasons in championship bracket)
    champ_pg = pg[pg["bracket"] == "championship"].copy()
    team_playoff = pd.concat([
        champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
        champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
    ]).drop_duplicates()
    playoff_merged = fh_tnh.merge(team_playoff, on=["season", "team_name"], how="inner")
    playoff_apps = (
        playoff_merged.groupby("franchise_id")["season"]
        .nunique()
        .reset_index(name="playoff_apps")
    )

    # Established year and current manager (2025)
    established = (
        fh.groupby("franchise_id")["season"].min().reset_index(name="established")
    )
    current_mgr = fh[fh["season"] == CURRENT_SEASON][
        ["franchise_id", "manager_name"]
    ].rename(columns={"manager_name": "current_manager"})

    stats = established.merge(current_mgr, on="franchise_id", how="left")
    stats = stats.merge(record, on="franchise_id", how="left")
    stats = stats.merge(champ_count, on="franchise_id", how="left")
    stats = stats.merge(playoff_apps, on="franchise_id", how="left")

    for col in ["wins", "losses", "ties", "championships", "playoff_apps"]:
        stats[col] = stats[col].fillna(0).astype(int)

    total = stats["wins"] + stats["losses"] + stats["ties"]
    stats["win_pct"] = (stats["wins"] / total.replace(0, pd.NA)).round(3)
    stats["seasons"] = stats.apply(
        lambda r: CURRENT_SEASON - int(r["established"]) + 1, axis=1
    )

    return stats.sort_values("franchise_id").reset_index(drop=True)


@st.cache_data
def get_all_time_manager_stats() -> pd.DataFrame:
    data = load_all()
    wm = data["weekly_matchups"]
    tnh = data["team_name_history"]
    standings = data["standings"]
    pg = data["playoff_games"]
    managers_df = data["managers"]
    champions = get_champions()

    rs = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
    rs_merged = tnh.merge(rs, on=["season", "team_name"], how="inner")
    rs_stats = (
        rs_merged.groupby("canonical_name")
        .apply(lambda g: pd.Series({
            "rs_wins": int((g["result"] == "Win").sum()),
            "rs_losses": int((g["result"] == "Loss").sum()),
            "rs_pf": round(g["team_score"].sum(), 1),
            "rs_pa": round(g["opponent_score"].sum(), 1),
        }))
        .reset_index()
    )

    champ_pg = pg[pg["bracket"] == "championship"].copy()

    pl_games = pd.concat([
        champ_pg[["season", "team_1", "score_1", "score_2", "winner"]].rename(
            columns={"team_1": "team_name", "score_1": "team_score", "score_2": "opp_score"}
        ),
        champ_pg[["season", "team_2", "score_2", "score_1", "winner"]].rename(
            columns={"team_2": "team_name", "score_2": "team_score", "score_1": "opp_score"}
        ),
    ])
    pl_games["result"] = pl_games.apply(
        lambda r: "Win" if r["winner"] == r["team_name"] else "Loss", axis=1
    )
    pl_merged = tnh.merge(pl_games, on=["season", "team_name"], how="inner")
    pl_stats = (
        pl_merged.groupby("canonical_name")
        .apply(lambda g: pd.Series({
            "pl_wins": int((g["result"] == "Win").sum()),
            "pl_losses": int((g["result"] == "Loss").sum()),
        }))
        .reset_index()
    )

    all_pl_teams = pd.concat([
        champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
        champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
    ]).drop_duplicates()
    pl_apps = (
        tnh.merge(all_pl_teams, on=["season", "team_name"], how="inner")
        .groupby("canonical_name")["season"].nunique()
        .reset_index(name="playoff_apps")
    )

    finals = champ_pg[champ_pg["game_type"] == "final"]
    finals_teams = pd.concat([
        finals[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
        finals[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
    ])
    finals_apps = (
        tnh.merge(finals_teams, on=["season", "team_name"], how="inner")
        .groupby("canonical_name")["season"].nunique()
        .reset_index(name="finals_apps")
    )

    champ_counts = (
        champions.groupby("champion_manager").size()
        .reset_index(name="championships")
        .rename(columns={"champion_manager": "canonical_name"})
    )

    std_merged = tnh.merge(standings[["season", "team_name", "rank"]], on=["season", "team_name"], how="inner")
    best_worst = (
        std_merged.groupby("canonical_name")["rank"]
        .agg(best_finish="min", worst_finish="max")
        .reset_index()
    )

    seasons_played = tnh.groupby("canonical_name")["season"].nunique().reset_index(name="seasons")

    stats = managers_df[["canonical_name", "display_name"]].copy()
    for df in [seasons_played, rs_stats, pl_stats, pl_apps, finals_apps, champ_counts, best_worst]:
        stats = stats.merge(df, on="canonical_name", how="left")

    for col in ["rs_wins", "rs_losses", "pl_wins", "pl_losses", "playoff_apps", "finals_apps", "championships", "seasons"]:
        stats[col] = stats[col].fillna(0).astype(int)
    for col in ["rs_pf", "rs_pa"]:
        stats[col] = stats[col].fillna(0.0)

    stats = stats[stats["seasons"] > 0].copy()
    return stats.sort_values(
        ["championships", "finals_apps", "playoff_apps", "rs_wins"], ascending=False
    ).reset_index(drop=True)


@st.cache_data
def get_manager_h2h(canonical_name: str) -> pd.DataFrame:
    data = load_all()
    wm = data["weekly_matchups"]
    tnh = data["team_name_history"]

    rs = wm[~wm["is_bye"] & ~wm["is_playoff"]].copy()
    mgr_teams = tnh[tnh["canonical_name"] == canonical_name][["season", "team_name"]]
    mgr_games = mgr_teams.merge(rs, on=["season", "team_name"], how="inner")

    opp_lookup = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    mgr_games = mgr_games.copy()
    mgr_games["opp_manager"] = mgr_games.apply(
        lambda r: opp_lookup.get((int(r["season"]), r["opponent"]), None), axis=1
    )
    mgr_games = mgr_games.dropna(subset=["opp_manager"])
    mgr_games = mgr_games[mgr_games["opp_manager"] != canonical_name]
    mgr_games["margin"] = mgr_games["team_score"] - mgr_games["opponent_score"]

    def summarize(g):
        wins = g[g["result"] == "Win"]
        losses = g[g["result"] == "Loss"]
        return pd.Series({
            "games": len(g),
            "wins": int((g["result"] == "Win").sum()),
            "losses": int((g["result"] == "Loss").sum()),
            "ties": int((g["result"] == "Tie").sum()),
            "pf": round(g["team_score"].sum(), 1),
            "pa": round(g["opponent_score"].sum(), 1),
            "biggest_win": round(wins["margin"].max(), 1) if len(wins) > 0 else 0.0,
            "biggest_loss": round(losses["margin"].min(), 1) if len(losses) > 0 else 0.0,
        })

    h2h = mgr_games.groupby("opp_manager").apply(summarize).reset_index()
    h2h["win_pct"] = (h2h["wins"] / h2h["games"]).round(3)
    return h2h.sort_values("games", ascending=False).reset_index(drop=True)


def _playoff_result(season: int, team: str, pg: pd.DataFrame) -> str:
    """Shared logic for resolving a team's final playoff placement."""
    games = pg[
        (pg["season"] == season)
        & (pg["bracket"] == "championship")
        & ((pg["team_1"] == team) | (pg["team_2"] == team))
    ]
    if len(games) == 0:
        return "—"
    if len(games[(games["game_type"] == "final") & (games["winner"] == team)]):
        return "Champion"
    if len(games[(games["game_type"] == "final") & (games["winner"] != team)]):
        return "Runner-Up"
    if len(games[(games["game_type"] == "3rd_place") & (games["winner"] == team)]):
        return "3rd Place"
    if len(games[(games["game_type"] == "3rd_place") & (games["winner"] != team)]):
        return "4th Place"
    if len(games[games["game_type"] == "semifinal"]):
        return "Semifinals"
    return "Playoffs"


def get_playoff_result_for_team(season: int, team: str, pg: pd.DataFrame) -> str:
    return _playoff_result(season, team, pg)


@st.cache_data
def get_timeline_events() -> pd.DataFrame:
    """Merge computed timeline events with manual editorial events into one sorted DataFrame."""
    data = load_all()
    champions_df = get_champions()
    fh = data["franchise_history"]
    tnh = data["team_name_history"]
    pg = data["playoff_games"]
    dp = data["draft_picks"]

    tnh_fwd = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    tnh_rev = tnh.set_index(["season", "canonical_name"])["team_name"].to_dict()
    fh_lookup = {(int(r["season"]), r["manager_name"]): r["franchise_id"] for _, r in fh.iterrows()}

    events: list[dict] = []

    def _ev(season, event_type, title, description, manager="", franchise_id="",
            team_name="", player_name="", importance="medium",
            show_home=False, show_franchise=None, show_manager=None):
        events.append({
            "season": int(season),
            "event_type": event_type,
            "title": title,
            "description": description,
            "manager": manager,
            "franchise_id": franchise_id,
            "team_name": team_name,
            "player_name": player_name,
            "importance": importance,
            "source": "computed",
            "show_on_homepage": show_home,
            "show_on_league_timeline": True,
            "show_on_franchise_page": bool(franchise_id) if show_franchise is None else show_franchise,
            "show_on_manager_page": bool(manager) if show_manager is None else show_manager,
        })

    # ── LEAGUE FOUNDING ──────────────────────────────────────────────────────
    _ev(FOUNDED, "milestone", "The Long Game begins",
        f"The inaugural season opens. {len(fh[fh['season']==FOUNDED]['franchise_id'].unique())} "
        f"franchises enter the league. The first champion is yet to be crowned.",
        importance="high", show_home=True, show_franchise=False, show_manager=False)

    # ── CHAMPIONSHIP EVENTS ───────────────────────────────────────────────────
    sorted_champs = champions_df.sort_values("season").reset_index(drop=True)
    consec_track: dict[str, int] = {}
    mgr_total: dict[str, int] = {}
    all_margins: list[float] = []
    all_win_scores: list[float] = []

    for i, row in sorted_champs.iterrows():
        szn = int(row["season"])
        mgr = row["champion_manager"]
        ru_mgr = row["runner_up_manager"]
        champ_team = row["champion_team"]
        ru_team = row["runner_up_team"]
        cs = float(row["champion_score"])
        rs = float(row["runner_up_score"])
        margin = cs - rs
        fid = fh_lookup.get((szn, mgr), "")
        ru_fid = fh_lookup.get((szn, ru_mgr), "")

        prev_mgr = sorted_champs.iloc[i-1]["champion_manager"] if i > 0 else None
        prev_szn = int(sorted_champs.iloc[i-1]["season"]) if i > 0 else szn - 1
        if prev_mgr == mgr and prev_szn == szn - 1:
            consec_track[mgr] = consec_track.get(mgr, 1) + 1
        else:
            consec_track[mgr] = 1
        mgr_total[mgr] = mgr_total.get(mgr, 0) + 1

        n_c = consec_track[mgr]
        n_t = mgr_total[mgr]
        ordinals = {1:"first",2:"second",3:"third",4:"fourth",5:"fifth",6:"sixth"}

        # Championship title wording
        if i == 0:
            chtitle = f"{mgr} wins the inaugural championship"
        elif n_c == 2:
            chtitle = f"{mgr} repeats as champion"
        elif n_c == 3:
            chtitle = f"{mgr} completes a three-peat"
        elif n_c >= 4:
            chtitle = f"{mgr} extends the dynasty to {n_c} straight"
        elif n_t > 1:
            chtitle = f"{mgr} claims their {ordinals.get(n_t, str(n_t)+'th')} title"
        else:
            chtitle = f"{mgr} wins the {szn} championship"

        chdesc = (f"{champ_team} defeats {ru_team}, {cs:.1f}–{rs:.1f} "
                  f"(margin: {margin:.2f} pts)")
        _ev(szn, "championship", chtitle, chdesc, mgr, fid, champ_team,
            importance="high", show_home=True)

        # Runner-up
        _ev(szn, "runner_up", f"{ru_mgr} finishes as runner-up",
            f"{ru_team} falls in the championship game, {rs:.1f}–{cs:.1f}",
            ru_mgr, ru_fid, ru_team, importance="medium")

        # Dynasty milestones (separate card for notable streaks)
        if n_c == 2:
            _ev(szn, "dynasty", f"{mgr} claims back-to-back titles",
                f"Consecutive championships in {szn-1} and {szn}. Rare in any league.",
                mgr, fid, importance="high")
        elif n_c == 3:
            _ev(szn, "dynasty", f"{mgr} three-peat complete",
                f"Three straight championships, {szn-2}–{szn}. Historically elite.",
                mgr, fid, importance="high")
        elif n_c >= 4:
            _ev(szn, "dynasty", f"{mgr}: {n_c}-year championship run",
                f"From {szn-n_c+1} to {szn}, {mgr} wins every year. "
                f"One of the great dynasties in league history.",
                mgr, fid, importance="high", show_home=True)

        # As-of records (compare against previous seasons only)
        if all_margins:
            if margin > max(all_margins):
                _ev(szn, "record", "New record: largest championship margin",
                    f"{champ_team} wins by {margin:.2f} pts — the widest margin in a title game.",
                    mgr, fid, importance="medium")
            if margin < min(all_margins):
                _ev(szn, "record", "Closest championship in league history",
                    f"Just {margin:.2f} pts separated the champion and runner-up. The tightest title game ever.",
                    mgr, fid, importance="medium")
            if cs > max(all_win_scores):
                _ev(szn, "record", "Record championship winning score",
                    f"{champ_team} scores {cs:.1f} pts in the title game — a new high-water mark.",
                    mgr, fid, importance="low")

        all_margins.append(margin)
        all_win_scores.append(cs)

    # ── STEWARD CHANGES ───────────────────────────────────────────────────────
    sp = get_franchise_steward_periods()
    for fid_val in fh["franchise_id"].unique():
        fid_periods = sp[sp["franchise_id"] == fid_val].sort_values("start_season")
        for idx, (_, p) in enumerate(fid_periods.iterrows()):
            mgr = p["manager_name"]
            start = int(p["start_season"])
            if idx == 0:
                continue  # founding handled by league event
            prev_mgr = fid_periods.iloc[idx - 1]["manager_name"]
            fran_founded = int(fh[fh["franchise_id"] == fid_val]["season"].min())
            _ev(start, "steward_change",
                f"{mgr} takes the helm of {fid_val}",
                f"{fid_val} changes hands from {prev_mgr} to {mgr}. "
                f"Franchise established {fran_founded}.",
                mgr, fid_val, importance="medium")

    # ── FIRST PLAYOFF APPEARANCE PER MANAGER ─────────────────────────────────
    champ_pg = pg[pg["bracket"] == "championship"]
    pl_teams = pd.concat([
        champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
        champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
    ]).drop_duplicates()
    pl_teams["manager"] = pl_teams.apply(
        lambda r: tnh_fwd.get((int(r["season"]), r["team_name"]), None), axis=1
    )
    pl_teams = pl_teams.dropna(subset=["manager"])
    first_pl = pl_teams.sort_values("season").groupby("manager")["season"].first().reset_index()

    champ_set = set(zip(sorted_champs["champion_manager"], sorted_champs["season"].astype(int)))
    for _, r in first_pl.iterrows():
        mgr = r["manager"]
        szn = int(r["season"])
        if (mgr, szn) in champ_set:
            continue  # championship event already covers it
        fid = fh_lookup.get((szn, mgr), "")
        _ev(szn, "milestone", f"{mgr}'s first playoff appearance",
            f"{mgr} qualifies for the postseason for the first time.",
            mgr, fid, importance="low")

    # ── DRAFT & KEEPER EVENTS ─────────────────────────────────────────────────
    if len(dp) > 0:
        dp_named = dp.copy()
        dp_named["manager"] = dp_named.apply(
            lambda r: tnh_fwd.get((int(r["season"]), r["team_name"]), r["team_name"]), axis=1
        )

        # First keeper season
        keeper_seasons = sorted(dp_named[dp_named["is_keeper"]]["season"].unique())
        if keeper_seasons:
            fks = int(keeper_seasons[0])
            k_count = int(dp_named[dp_named["season"] == fks]["is_keeper"].sum())
            _ev(fks, "rule_change", f"Keeper format introduced — {k_count} players retained",
                f"For the first time, managers may carry players forward from the previous season. "
                f"The league is no longer purely a draft-and-reset format.",
                importance="high", show_franchise=False, show_manager=False)

        # Keeper summary per season (subsequent seasons, low importance)
        for szn in sorted(dp_named["season"].unique()):
            szn_keepers = dp_named[(dp_named["season"] == szn) & (dp_named["is_keeper"])]
            if len(szn_keepers) == 0 or szn == (keeper_seasons[0] if keeper_seasons else -1):
                continue
            n_k = len(szn_keepers)
            r1_kept = szn_keepers[szn_keepers["round"] == 1]["player_name"].tolist()
            r1_str = (", ".join(r1_kept[:4]) + ("…" if len(r1_kept) > 4 else "")) if r1_kept else "none"
            _ev(int(szn), "keeper", f"{n_k} players kept — {szn} draft",
                f"Round-1 keepers: {r1_str}" if r1_kept else f"{n_k} players retained before the {szn} draft.",
                importance="low", show_franchise=False, show_manager=False)

        # First overall pick each season (non-keeper preferred)
        for szn_val in sorted(dp_named["season"].unique()):
            szn_dp = dp_named[dp_named["season"] == szn_val].sort_values("overall_pick")
            fo = szn_dp.iloc[0]
            keeper_flag = " (kept)" if fo["is_keeper"] else ""
            mgr_fo = fo["manager"]
            fid_fo = fh_lookup.get((int(szn_val), mgr_fo), "")
            _ev(int(szn_val), "draft",
                f"Draft: {fo['player_name']} goes first overall{keeper_flag}",
                f"{mgr_fo} ({fo['team_name']}) holds the top pick in {szn_val}.",
                mgr_fo, fid_fo, fo["team_name"], fo["player_name"], importance="low")

    # ── MERGE MANUAL EVENTS ───────────────────────────────────────────────────
    manual_path = DATA_DIR / "manual_timeline_events.csv"
    computed_df = pd.DataFrame(events)

    if manual_path.exists():
        manual_df = pd.read_csv(manual_path, dtype=str).fillna("")
        manual_df["season"] = manual_df["season"].apply(lambda x: int(x) if x.strip() else 0)
        for col in ["show_on_homepage", "show_on_league_timeline",
                    "show_on_franchise_page", "show_on_manager_page"]:
            if col in manual_df.columns:
                manual_df[col] = manual_df[col].str.strip().str.lower().isin(["true", "1", "yes"])
        manual_df["source"] = "editorial"
        all_events = pd.concat([computed_df, manual_df], ignore_index=True, sort=False)
    else:
        all_events = computed_df

    # Sort: season desc → importance rank → computed before editorial
    _imp = {"high": 0, "medium": 1, "low": 2}
    _src = {"computed": 0, "editorial": 1}
    all_events["_imp"] = all_events["importance"].map(_imp).fillna(1)
    all_events["_src"] = all_events["source"].map(_src).fillna(1)
    all_events = (
        all_events
        .sort_values(["season", "_imp", "_src", "event_type"])
        .drop(columns=["_imp", "_src"])
        .reset_index(drop=True)
    )

    # Ensure consistent dtypes
    for col in ["manager", "franchise_id", "team_name", "player_name",
                "title", "description", "event_type", "importance", "source"]:
        all_events[col] = all_events[col].fillna("").astype(str)
    for col in ["show_on_homepage", "show_on_league_timeline",
                "show_on_franchise_page", "show_on_manager_page"]:
        all_events[col] = all_events[col].fillna(False).astype(bool)

    return all_events


# ── DRAFT & KEEPER ANALYSIS ───────────────────────────────────────────────────

_FANTASY_POS = ["QB", "RB", "WR", "TE", "DEF", "K"]
_POS_NORM = {"FB": "RB"}          # rare fullbacks count as RBs in fantasy
_POS_COLORS = {
    "RB":  "#22C55E",
    "WR":  "#3B82F6",
    "QB":  "#EF4444",
    "TE":  "#F59E0B",
    "DEF": "#8B5CF6",
    "K":   "#6B7280",
    "Other": "#374151",
}
# Seasons where the keeper format was suspended — treat as gaps in streak math
_KEEPER_SUSPENSION_YEARS: set[int] = set()   # 2005 and 2011 data now complete


@st.cache_data
def get_draft_picks_with_pos() -> pd.DataFrame:
    """Draft picks joined with position, manager name, and franchise_id.
    Excludes --empty-- placeholder rows and normalises rare non-fantasy positions.
    Cache version: 3 (2005 and 2011 data complete)."""
    _cache_bust = 4  # increment this to force cache invalidation when data files change
    data = load_all()
    dp = data["draft_picks"].copy()
    pp = data["player_positions"]
    fh = data["franchise_history"]
    tnh = data["team_name_history"]

    dpw = dp.merge(pp[["player_name", "position"]], on="player_name", how="left")
    dpw["position"] = dpw["position"].map(lambda p: _POS_NORM.get(p, p) if pd.notna(p) else p)

    dpw = dpw.merge(
        tnh[["season", "team_name", "canonical_name"]],
        on=["season", "team_name"], how="left",
    ).rename(columns={"canonical_name": "manager"})

    dpw = dpw.merge(
        fh[["season", "manager_name", "franchise_id"]],
        left_on=["season", "manager"], right_on=["season", "manager_name"], how="left",
    ).drop(columns=["manager_name"])

    return dpw[dpw["player_name"] != "--empty--"].reset_index(drop=True)


@st.cache_data
def get_position_trends_data() -> pd.DataFrame:
    """Round-1 position share by season. Excludes keeper picks and years with <5 real R1 picks."""
    _cache_bust = 1
    dpw = get_draft_picks_with_pos()
    r1 = dpw[(dpw["round"] == 1) & (~dpw["is_keeper"]) & dpw["position"].isin(_FANTASY_POS)].copy()
    r1["pos_group"] = r1["position"]

    trend = (
        r1.groupby(["season", "pos_group"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    # Keep only seasons with enough real round-1 picks
    pos_cols = [c for c in trend.columns if c != "season"]
    trend["total"] = trend[pos_cols].sum(axis=1)
    trend = trend[trend["total"] >= 5].copy()
    for col in pos_cols:
        trend[col] = (trend[col] / trend["total"] * 100).round(1)
    return trend.drop(columns=["total"])


@st.cache_data
def get_draft_records() -> dict:
    """Various draft superlatives as a dict of labelled facts."""
    _cache_bust = 1
    dpw = get_draft_picks_with_pos()
    real = dpw[~dpw["is_keeper"]].copy()
    keepers = dpw[dpw["is_keeper"]].copy()

    # Most drafted individual players (exclude DEF)
    indiv = real[real["position"] != "DEF"]
    most_drafted = indiv.groupby("player_name").size().sort_values(ascending=False)

    # Most drafted DEF
    defs = real[real["position"] == "DEF"]
    most_drafted_def = defs.groupby("player_name").size().sort_values(ascending=False)

    # Most managers to draft the same player
    mgr_per_player = indiv.groupby("player_name")["manager"].nunique().sort_values(ascending=False)

    # Most frequently kept player
    most_kept = keepers.groupby("player_name").size().sort_values(ascending=False)

    # Earliest QB taken (lowest overall_pick, non-keeper, from rounds 1+)
    qb_picks = real[real["position"] == "QB"].sort_values("overall_pick")
    te_picks = real[real["position"] == "TE"].sort_values("overall_pick")
    k_picks  = real[real["position"] == "K"].sort_values("overall_pick")
    def_picks = real[real["position"] == "DEF"].sort_values("overall_pick")

    def _top(df, n=1):
        if len(df) == 0:
            return []
        return df.head(n)[["season", "overall_pick", "round", "pick_in_round", "manager", "player_name"]].to_dict("records")

    # Keeper position breakdown
    k_pos = keepers[keepers["position"].notna()]["position"].value_counts()

    return {
        "most_drafted_players": most_drafted.head(10).reset_index().values.tolist(),
        "most_drafted_def": most_drafted_def.head(5).reset_index().values.tolist(),
        "most_mgrs_one_player": mgr_per_player.head(5).reset_index().values.tolist(),
        "most_kept_players": most_kept.head(10).reset_index().values.tolist(),
        "earliest_qb": _top(qb_picks, 5),
        "earliest_te": _top(te_picks, 5),
        "earliest_k": _top(k_picks, 3),
        "earliest_def_r1": _top(def_picks[def_picks["round"] == 1], 3),
        "keeper_pos_breakdown": k_pos.to_dict(),
        "total_picks": len(real),
        "total_keepers": len(keepers),
        "total_unique_players": indiv["player_name"].nunique(),
        "keeper_seasons": sorted(keepers["season"].unique().tolist()),
    }


@st.cache_data
def get_keeper_chains() -> pd.DataFrame:
    """Per-player keeper streak analysis. One row per (player, manager, streak)."""
    _cache_bust = 1
    dpw = get_draft_picks_with_pos()
    keepers = dpw[dpw["is_keeper"]].copy()

    rows = []
    for player, grp in keepers.groupby("player_name"):
        all_rows = grp.sort_values("season")[["season", "manager", "franchise_id"]].values.tolist()
        if not all_rows:
            continue

        def _flush(streak):
            mgrs = list(dict.fromkeys([r[1] for r in streak]))  # ordered unique managers
            rows.append({
                "player_name": player,
                "primary_manager": streak[0][1],
                "all_managers": mgrs,
                "franchise_id": streak[0][2],
                "seasons": [int(r[0]) for r in streak],
                "streak_len": len(streak),
                "first_season": int(streak[0][0]),
                "last_season": int(streak[-1][0]),
                "multi_manager": len(mgrs) > 1,
            })

        streak_start = 0
        for i in range(1, len(all_rows)):
            prev_szn, prev_mgr, prev_fid = all_rows[i - 1]
            curr_szn, curr_mgr, curr_fid = all_rows[i]
            gap_years = set(range(int(prev_szn) + 1, int(curr_szn)))
            is_suspension_gap = gap_years.issubset(_KEEPER_SUSPENSION_YEARS)
            # Break streak on non-suspension year gap OR franchise change
            if not is_suspension_gap or curr_fid != prev_fid:
                _flush(all_rows[streak_start:i])
                streak_start = i

        _flush(all_rows[streak_start:])

    df = pd.DataFrame(rows)
    return df.sort_values("streak_len", ascending=False).reset_index(drop=True)


@st.cache_data
def get_player_ownership() -> pd.DataFrame:
    """Per (player, manager) summary: draft count, keeper count, seasons list."""
    _cache_bust = 1
    dpw = get_draft_picks_with_pos()
    rows = []
    for (player, mgr), grp in dpw.groupby(["player_name", "manager"]):
        k_grp = grp[grp["is_keeper"]]
        rows.append({
            "player_name": player,
            "manager": mgr,
            "franchise_id": grp["franchise_id"].iloc[0] if grp["franchise_id"].notna().any() else None,
            "position": grp["position"].iloc[0],
            "draft_count": int((~grp["is_keeper"]).sum()),
            "keeper_count": int(grp["is_keeper"].sum()),
            "total_seasons": len(grp),
            "seasons": sorted(grp["season"].astype(int).tolist()),
            "first_season": int(grp["season"].min()),
            "last_season": int(grp["season"].max()),
        })
    return pd.DataFrame(rows).sort_values("total_seasons", ascending=False).reset_index(drop=True)


@st.cache_data
def get_keeper_enriched() -> pd.DataFrame:
    """Keeper picks enriched with championship flags, manager season W-L, and playoff appearances."""
    _cache_bust = 1
    dpw = get_draft_picks_with_pos()
    keepers = dpw[dpw["is_keeper"]].copy()
    champions = get_champions()
    data_all = load_all()
    std = data_all["standings"]
    tnh = data_all["team_name_history"]
    pg = data_all["playoff_games"]

    # Championship flag
    champ_lookup = champions[["season", "champion_manager"]].rename(
        columns={"champion_manager": "_champ_mgr"}
    )
    keepers = keepers.merge(champ_lookup, on="season", how="left")
    keepers["won_title"] = keepers["manager"] == keepers["_champ_mgr"]
    keepers = keepers.drop(columns=["_champ_mgr"])

    # Manager W-L record that season
    tnh_mgr = tnh[["season", "team_name", "canonical_name"]].rename(
        columns={"canonical_name": "manager"}
    )
    std_with_mgr = std.merge(tnh_mgr, on=["season", "team_name"], how="left")
    std_lookup = (
        std_with_mgr[["season", "manager", "wins", "losses", "rank"]]
        .drop_duplicates(subset=["season", "manager"])
    )
    keepers = keepers.merge(std_lookup, on=["season", "manager"], how="left")
    keepers = keepers.rename(columns={"rank": "finish"})
    keepers["wins"] = keepers["wins"].fillna(0).astype(int)
    keepers["losses"] = keepers["losses"].fillna(0).astype(int)

    # Playoff flag (appeared in championship bracket)
    champ_pg = pg[pg["bracket"] == "championship"]
    pl_teams = pd.concat([
        champ_pg[["season", "team_1"]].rename(columns={"team_1": "team_name"}),
        champ_pg[["season", "team_2"]].rename(columns={"team_2": "team_name"}),
    ]).drop_duplicates()
    pl_with_mgr = (
        pl_teams.merge(tnh_mgr, on=["season", "team_name"], how="left")
        .drop_duplicates(subset=["season", "manager"])
    )
    pl_with_mgr["made_playoffs"] = True
    keepers = keepers.merge(
        pl_with_mgr[["season", "manager", "made_playoffs"]],
        on=["season", "manager"], how="left",
    )
    keepers["made_playoffs"] = keepers["made_playoffs"].fillna(False)
    keepers["keeper_cost_round"] = keepers["round"].astype(int)

    return keepers.reset_index(drop=True)


@st.cache_data
def get_franchise_legends(franchise_id: str) -> list[dict]:
    """Top players for a franchise by weighted (draft + keeper) frequency."""
    po = get_player_ownership()
    fpo = po[po["franchise_id"] == franchise_id].copy()
    if len(fpo) == 0:
        return []
    fpo["legend_score"] = fpo["draft_count"] * 1 + fpo["keeper_count"] * 3
    fpo = fpo[fpo["position"] != "DEF"]  # exclude team defenses
    top = fpo.nlargest(8, "legend_score")
    return top[["player_name", "position", "draft_count", "keeper_count", "legend_score", "seasons"]].to_dict("records")


# ── RIVALRY DATA ──────────────────────────────────────────────────────────────

@st.cache_data
def get_all_rivalries() -> pd.DataFrame:
    """Rivalry scores and head-to-head records for every manager pair."""
    data = load_all()
    wm = data["weekly_matchups"]
    tnh = data["team_name_history"]
    pg = data["playoff_games"]

    mgr_lu = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

    # Regular-season games — one row per game (deduplicate from two-perspective data)
    rs = wm[~wm["is_bye"].astype(bool) & ~wm["is_playoff"].astype(bool)].copy()
    rs["mgr"] = rs.apply(lambda r: mgr_lu.get((r["season"], r["team_name"])), axis=1)
    rs["opp_mgr"] = rs.apply(lambda r: mgr_lu.get((r["season"], r["opponent"])), axis=1)
    rs = rs.dropna(subset=["mgr", "opp_mgr"])
    rs = rs[rs["mgr"] != rs["opp_mgr"]]
    rs["pair"] = rs.apply(lambda r: tuple(sorted([r["mgr"], r["opp_mgr"]])), axis=1)
    rs["margin"] = (rs["team_score"] - rs["opponent_score"]).abs()
    rs["winner"] = rs.apply(
        lambda r: r["mgr"] if r["result"] == "Win" else r["opp_mgr"], axis=1
    )
    rs_dedup = rs.drop_duplicates(subset=["season", "week", "pair"]).copy()

    # Championship-bracket playoff games
    champ = pg[pg["bracket"] == "championship"].copy()
    champ["mgr1"] = champ.apply(lambda r: mgr_lu.get((r["season"], r["team_1"])), axis=1)
    champ["mgr2"] = champ.apply(lambda r: mgr_lu.get((r["season"], r["team_2"])), axis=1)
    champ["winner_mgr"] = champ.apply(lambda r: mgr_lu.get((r["season"], r["winner"])), axis=1)
    champ = champ.dropna(subset=["mgr1", "mgr2"])
    champ["pair"] = champ.apply(
        lambda r: tuple(sorted([r["mgr1"], r["mgr2"]])), axis=1
    )
    champ["margin"] = (champ["score_1"] - champ["score_2"]).abs()

    RECENT_CUTOFF = CURRENT_SEASON - 4
    # sorted() is load-bearing: iterating a set of name tuples follows Python's
    # randomized string hashing, so row order changed on every app restart.
    all_pairs = sorted(set(rs_dedup["pair"].unique()) | set(champ["pair"].unique()))

    rows = []
    raw_scores = []

    for pair in all_pairs:
        mgr_a, mgr_b = pair
        rs_grp = rs_dedup[rs_dedup["pair"] == pair]
        pl_grp = champ[champ["pair"] == pair]
        final_grp = pl_grp[pl_grp["game_type"] == "final"]

        total_rs = len(rs_grp)
        a_wins = int((rs_grp["winner"] == mgr_a).sum())
        b_wins = int((rs_grp["winner"] == mgr_b).sum())
        close = int((rs_grp["margin"] < 5).sum())
        recent = int((rs_grp["season"] >= RECENT_CUTOFF).sum())
        a_pct = a_wins / total_rs if total_rs > 0 else 0.5
        balance = 1.0 - abs(a_pct - 0.5) * 2.0

        pl_total = len(pl_grp)
        pl_a = int((pl_grp["winner_mgr"] == mgr_a).sum()) if pl_total else 0
        pl_b = int((pl_grp["winner_mgr"] == mgr_b).sum()) if pl_total else 0
        final_total = len(final_grp)
        final_a = int((final_grp["winner_mgr"] == mgr_a).sum()) if final_total else 0
        final_b = int((final_grp["winner_mgr"] == mgr_b).sum()) if final_total else 0

        raw = (
            total_rs * 1.5
            + pl_total * 8.0
            + final_total * 15.0
            + close * 2.0
            + recent * 1.5
            + balance * 25.0
        )
        raw_scores.append(raw)

        # Season range
        seasons_played = sorted(rs_grp["season"].unique().tolist()) if total_rs else []
        first_meeting = int(min(seasons_played)) if seasons_played else 0
        last_meeting = int(max(seasons_played)) if seasons_played else 0

        # Biggest win margins
        a_wins_df = rs_grp[rs_grp["winner"] == mgr_a]
        b_wins_df = rs_grp[rs_grp["winner"] == mgr_b]
        a_biggest = float(a_wins_df["margin"].max()) if len(a_wins_df) else 0.0
        b_biggest = float(b_wins_df["margin"].max()) if len(b_wins_df) else 0.0
        closest_game = float(rs_grp["margin"].min()) if total_rs else 0.0

        rows.append({
            "mgr_a": mgr_a, "mgr_b": mgr_b,
            "rs_games": total_rs, "rs_a_wins": a_wins, "rs_b_wins": b_wins,
            "rs_a_pct": round(a_pct, 3), "balance": round(balance, 3),
            "close_games": close, "recent_games": recent,
            "pl_games": pl_total, "pl_a_wins": pl_a, "pl_b_wins": pl_b,
            "final_games": final_total, "final_a_wins": final_a, "final_b_wins": final_b,
            "rivalry_raw": raw,
            "a_biggest_win": round(a_biggest, 1),
            "b_biggest_win": round(b_biggest, 1),
            "closest_game": round(closest_game, 2),
            "first_meeting": first_meeting,
            "last_meeting": last_meeting,
        })

    df = pd.DataFrame(rows)
    mx = df["rivalry_raw"].max()
    df["rivalry_score"] = (df["rivalry_raw"] / mx * 100).round(0).astype(int)
    # rivalry_score is rounded to an integer, so ties are common and the default
    # quicksort is not stable. Break ties on the raw score, then on names, so the
    # Top 10 on the rivalries page is the same list every time it renders.
    return (
        df.sort_values(
            ["rivalry_score", "rivalry_raw", "mgr_a", "mgr_b"],
            ascending=[False, False, True, True],
            kind="mergesort",
        )
        .reset_index(drop=True)
    )


@st.cache_data
def get_h2h_detail(mgr_a: str, mgr_b: str) -> dict:
    """All games between two managers — RS + playoff — with per-game detail."""
    data = load_all()
    wm = data["weekly_matchups"]
    tnh = data["team_name_history"]
    pg = data["playoff_games"]

    mgr_lu = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    pair = tuple(sorted([mgr_a, mgr_b]))

    # RS games
    rs = wm[~wm["is_bye"].astype(bool) & ~wm["is_playoff"].astype(bool)].copy()
    rs["mgr"] = rs.apply(lambda r: mgr_lu.get((r["season"], r["team_name"])), axis=1)
    rs["opp_mgr"] = rs.apply(lambda r: mgr_lu.get((r["season"], r["opponent"])), axis=1)
    rs = rs.dropna(subset=["mgr", "opp_mgr"])
    rs["pair"] = rs.apply(lambda r: tuple(sorted([r["mgr"], r["opp_mgr"]])), axis=1)
    rs = rs[rs["pair"] == pair].drop_duplicates(subset=["season", "week", "pair"])
    rs["winner"] = rs.apply(lambda r: r["mgr"] if r["result"] == "Win" else r["opp_mgr"], axis=1)
    rs["a_score"] = rs.apply(
        lambda r: r["team_score"] if r["mgr"] == mgr_a else r["opponent_score"], axis=1
    )
    rs["b_score"] = rs.apply(
        lambda r: r["opponent_score"] if r["mgr"] == mgr_a else r["team_score"], axis=1
    )
    rs["margin"] = (rs["team_score"] - rs["opponent_score"]).abs()

    # Playoff games
    champ = pg[pg["bracket"] == "championship"].copy()
    champ["mgr1"] = champ.apply(lambda r: mgr_lu.get((r["season"], r["team_1"])), axis=1)
    champ["mgr2"] = champ.apply(lambda r: mgr_lu.get((r["season"], r["team_2"])), axis=1)
    champ["winner_mgr"] = champ.apply(lambda r: mgr_lu.get((r["season"], r["winner"])), axis=1)
    champ["pair"] = champ.apply(lambda r: tuple(sorted([r["mgr1"], r["mgr2"]])), axis=1)
    champ = champ[champ["pair"] == pair]
    champ["a_score"] = champ.apply(
        lambda r: float(r["score_1"]) if r["mgr1"] == mgr_a else float(r["score_2"]), axis=1
    )
    champ["b_score"] = champ.apply(
        lambda r: float(r["score_2"]) if r["mgr1"] == mgr_a else float(r["score_1"]), axis=1
    )
    champ["margin"] = (champ["score_1"] - champ["score_2"]).abs()

    return {
        "rs": rs[["season", "week", "winner", "a_score", "b_score", "margin"]].sort_values(["season", "week"]),
        "playoffs": champ[["season", "game_type", "winner_mgr", "a_score", "b_score", "margin"]].sort_values("season"),
    }


@st.cache_data
def get_franchise_rivalries() -> pd.DataFrame:
    """Franchise-vs-franchise head-to-head records."""
    data = load_all()
    wm = data["weekly_matchups"]
    tnh = data["team_name_history"]
    fh = data["franchise_history"]

    # Team → franchise lookup
    fh_lu = fh.set_index(["season", "manager_name"])["franchise_id"].to_dict()
    tnh_lu = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

    def fid_from_team(season, team):
        mgr = tnh_lu.get((season, team))
        if mgr is None:
            return None
        return fh_lu.get((season, mgr))

    rs = wm[~wm["is_bye"].astype(bool) & ~wm["is_playoff"].astype(bool)].copy()
    rs["fid"] = rs.apply(lambda r: fid_from_team(r["season"], r["team_name"]), axis=1)
    rs["opp_fid"] = rs.apply(lambda r: fid_from_team(r["season"], r["opponent"]), axis=1)
    rs = rs.dropna(subset=["fid", "opp_fid"])
    rs = rs[rs["fid"] != rs["opp_fid"]]
    rs["pair"] = rs.apply(lambda r: tuple(sorted([r["fid"], r["opp_fid"]])), axis=1)
    rs["winner_fid"] = rs.apply(
        lambda r: r["fid"] if r["result"] == "Win" else r["opp_fid"], axis=1
    )
    rs_dedup = rs.drop_duplicates(subset=["season", "week", "pair"])

    rows = []
    for pair, grp in rs_dedup.groupby("pair"):
        fid_a, fid_b = pair
        a_wins = int((grp["winner_fid"] == fid_a).sum())
        b_wins = int((grp["winner_fid"] == fid_b).sum())
        total = len(grp)
        rows.append({
            "fid_a": fid_a, "fid_b": fid_b,
            "games": total, "a_wins": a_wins, "b_wins": b_wins,
            "a_pct": round(a_wins / total, 3) if total else 0.5,
        })

    df = pd.DataFrame(rows)
    return df.sort_values("games", ascending=False).reset_index(drop=True)


@st.cache_data
def get_playoff_eliminations() -> pd.DataFrame:
    """Who has eliminated whom in the championship bracket."""
    data = load_all()
    pg = data["playoff_games"]
    tnh = data["team_name_history"]

    mgr_lu = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    champ = pg[
        (pg["bracket"] == "championship")
        & (pg["game_type"].isin(["quarterfinal", "semifinal", "final"]))
    ].copy()
    champ["winner_mgr"] = champ.apply(lambda r: mgr_lu.get((r["season"], r["winner"])), axis=1)
    champ["loser_team"] = champ.apply(
        lambda r: r["team_2"] if r["winner"] == r["team_1"] else r["team_1"], axis=1
    )
    champ["loser_mgr"] = champ.apply(
        lambda r: mgr_lu.get((r["season"], r["loser_team"])), axis=1
    )
    champ = champ.dropna(subset=["winner_mgr", "loser_mgr"])

    pair_counts = (
        champ.groupby(["winner_mgr", "loser_mgr"])
        .size()
        .reset_index(name="eliminations")
        .sort_values("eliminations", ascending=False)
        .reset_index(drop=True)
    )
    return pair_counts


# ── SEASON DETAIL ─────────────────────────────────────────────────────────────
# Lifted out of pages/season_archive.py so the page and the static build share
# one implementation, and so the logic is covered by tests/.

# Postseason finish ranks above regular-season rank when ordering the table:
# a champion who limped in as the 6th seed still belongs at the top.
_PLAYOFF_RESULT_ORDER = {
    "Champion": 1, "Runner-Up": 2, "3rd Place": 3, "4th Place": 4,
    "Semifinals": 5, "Playoffs": 6,
}

_BRACKET_ROUNDS = [
    ("quarterfinal", "Quarterfinals"),
    ("semifinal", "Semifinals"),
    ("final", "Championship"),
]


def _seed(value) -> int | None:
    if value is None or pd.isna(value) or str(value) == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _game(row: pd.Series) -> dict:
    return {
        "game_type": row["game_type"],
        "round": int(row["round"]) if not pd.isna(row["round"]) else None,
        "seed_1": _seed(row.get("seed_1")),
        "team_1": row["team_1"],
        "score_1": round(float(row["score_1"]), 2),
        "seed_2": _seed(row.get("seed_2")),
        "team_2": row["team_2"],
        "score_2": round(float(row["score_2"]), 2),
        "winner": row["winner"],
    }


@st.cache_data
def get_nfl_league_links(season: int) -> list[dict]:
    """Players named in a season's NFL context who were on a league roster.

    Derived rather than hand-written, so the connection can never drift from
    the draft record. This is the museum's own test applied to the NFL bullets:
    the league story is the point, the NFL is the backdrop.
    """
    from utils import narratives

    lines = narratives.NFL_CONTEXT.get(int(season), [])
    if not lines:
        return []

    picks = get_draft_picks_with_pos()
    season_picks = picks[picks["season"] == int(season)]
    text = " ".join(lines)

    links = []
    for player in sorted(set(season_picks["player_name"].dropna())):
        # Guard against short names matching mid-sentence.
        if len(player) <= 6 or player not in text:
            continue
        rows = season_picks[season_picks["player_name"] == player]
        owners = sorted(
            {(r["manager"], bool(r["is_keeper"])) for _, r in rows.iterrows() if r["manager"]},
            key=lambda o: o[0],
        )
        if owners:
            links.append({
                "player": player,
                "managers": [{"manager": m, "kept": k, "emoji": MANAGER_EMOJI.get(m, "")} for m, k in owners],
            })
    return links


@st.cache_data
def get_season_detail(season: int) -> dict:
    """Everything the season archive shows for one year.

    Facts and generated copy, no markup — so both the Streamlit page and the
    static build render the same season from the same source.
    """
    from utils import narratives  # local import: narratives is pure content

    season = int(season)
    data = load_all()
    standings = data["standings"]
    playoff_games = data["playoff_games"]
    weekly = data["weekly_matchups"]
    tnh = data["team_name_history"]

    champions = get_champions()
    manager_by_team = (
        tnh[tnh["season"] == season].set_index("team_name")["canonical_name"].to_dict()
    )

    # ── Champion and the copy generated from it ──────────────────────────────
    champ_rows = champions[champions["season"] == season]
    champion = title = narrative = hook = None
    if len(champ_rows):
        c = champ_rows.iloc[0]
        prior = champions[champions["season"] < season]
        prev_rows = champions[champions["season"] == season - 1]
        previous_champion = prev_rows.iloc[0]["champion_manager"] if len(prev_rows) else None
        prior_titles = int((prior["champion_manager"] == c["champion_manager"]).sum())
        margin = float(c["champion_score"]) - float(c["runner_up_score"])

        champion = {
            "manager": c["champion_manager"],
            "team": c["champion_team"],
            "score": round(float(c["champion_score"]), 2),
            "runner_up_manager": c["runner_up_manager"],
            "runner_up_team": c["runner_up_team"],
            "runner_up_score": round(float(c["runner_up_score"]), 2),
            "margin": round(margin, 2),
            "prior_titles": prior_titles,
            "is_repeat": previous_champion == c["champion_manager"],
            "emoji": MANAGER_EMOJI.get(c["champion_manager"], "🏆"),
        }
        title = narratives.season_title(
            season,
            margin=margin,
            is_repeat=champion["is_repeat"],
            prior_titles=prior_titles,
        )
        narrative = narratives.season_narrative(
            champion_manager=c["champion_manager"],
            champion_team=c["champion_team"],
            runner_up_manager=c["runner_up_manager"],
            runner_up_team=c["runner_up_team"],
            champion_score=float(c["champion_score"]),
            runner_up_score=float(c["runner_up_score"]),
            is_first_title=prior_titles == 0,
            previous_champion_manager=previous_champion,
        )
        hook = narratives.SEASON_HOOKS.get(season, "")

    # ── Final standings, ordered by how the season actually ended ────────────
    table = []
    for _, row in standings[standings["season"] == season].sort_values("rank").iterrows():
        manager = manager_by_team.get(row["team_name"], "—")
        result = get_playoff_result_for_team(season, row["team_name"], playoff_games)
        rs_rank = int(row["rank"])
        table.append({
            "result": result,
            "team": row["team_name"],
            "manager": manager,
            "emoji": MANAGER_EMOJI.get(manager, ""),
            "wins": int(row["wins"]),
            "losses": int(row["losses"]),
            "ties": int(row["ties"]),
            "points_for": round(float(row["points_for"]), 2),
            "points_against": round(float(row["points_against"]), 2),
            "rs_rank": rs_rank,
            "_order": _PLAYOFF_RESULT_ORDER.get(result, 100 + rs_rank),
        })
    table.sort(key=lambda r: r["_order"])
    for entry in table:
        del entry["_order"]

    # ── Championship bracket ─────────────────────────────────────────────────
    bracket_games = playoff_games[
        (playoff_games["season"] == season) & (playoff_games["bracket"] == "championship")
    ].sort_values(["round", "game_type"])

    rounds = []
    for game_type, label in _BRACKET_ROUNDS:
        games = bracket_games[bracket_games["game_type"] == game_type]
        if len(games):
            rounds.append({
                "type": game_type,
                "label": label,
                "games": [_game(g) for _, g in games.iterrows()],
            })
    third = bracket_games[bracket_games["game_type"] == "3rd_place"]

    # ── Regular-season scoring leaders ───────────────────────────────────────
    regular = weekly[
        (weekly["season"] == season)
        & (~weekly["is_bye"].astype(bool))
        & (~weekly["is_playoff"].astype(bool))
    ]
    totals = (
        regular.groupby("team_name")["team_score"].sum()
        .reset_index(name="points_for")
        .sort_values(["points_for", "team_name"], ascending=[False, True])
        .reset_index(drop=True)
    )
    top_scorers = [
        {
            "rank": i + 1,
            "team": row["team_name"],
            "manager": manager_by_team.get(row["team_name"], "—"),
            "emoji": MANAGER_EMOJI.get(manager_by_team.get(row["team_name"], "—"), ""),
            "points_for": round(float(row["points_for"]), 2),
        }
        for i, (_, row) in enumerate(totals.iterrows())
    ]

    return {
        "season": season,
        "champion": champion,
        "title": title,
        "hook": hook,
        "narrative": narrative,
        "nfl_context": list(narratives.NFL_CONTEXT.get(season, [])),
        "nfl_league_links": get_nfl_league_links(season),
        "standings": table,
        "bracket": {
            "rounds": rounds,
            "third_place": _game(third.iloc[0]) if len(third) else None,
        },
        "top_scorers": top_scorers,
    }


@st.cache_data
def get_all_seasons() -> list[int]:
    """Every season with recorded standings, newest first."""
    return sorted((int(s) for s in load_all()["standings"]["season"].unique()), reverse=True)


# ── TIMELINE VIEW ─────────────────────────────────────────────────────────────
# Lifted out of pages/league_timeline.py. The page's three controls are filters
# rather than entity pickers, so this exposes fully enriched events plus a
# grouping helper: the page filters then groups, and the static site will do the
# same work client-side from the same payload.

@st.cache_data
def get_era_by_season() -> dict[int, dict]:
    """season -> {name, color}, expanded from the era definitions."""
    from utils import narratives

    mapping: dict[int, dict] = {}
    for era in narratives.LEAGUE_ERAS:
        for year in range(era["start"], min(era["end"], CURRENT_SEASON) + 1):
            mapping[year] = {"name": era["short"], "color": era["color"]}
    return mapping


def _clean(value) -> str:
    """Timeline columns arrive from CSV with literal 'nan' for blanks."""
    text = "" if value is None else str(value)
    return "" if text in ("nan", "NaT", "None") else text


@st.cache_data
def get_timeline_view() -> dict:
    """Every timeline event, enriched with its display taxonomy, plus totals."""
    from utils import narratives

    events_df = get_timeline_events()
    eras = get_era_by_season()

    events = []
    for _, row in events_df.iterrows():
        event_type = _clean(row.get("event_type")) or "note"
        icon, color, label = narratives.TIMELINE_EVENT_META.get(
            event_type, ("📝", "#6B7280", event_type.replace("_", " ").title())
        )
        importance = _clean(row.get("importance")) or "medium"
        manager = _clean(row.get("manager"))
        season = int(row["season"])

        events.append({
            "season": season,
            "event_type": event_type,
            "icon": icon,
            "color": color,
            "label": label,
            "importance": importance,
            "importance_label": narratives.IMPORTANCE_LABELS.get(importance, "MINOR"),
            "importance_rank": narratives.IMPORTANCE_ORDER.get(importance, 1),
            "title": _clean(row.get("title")),
            "description": _clean(row.get("description")),
            "manager": manager,
            "manager_emoji": MANAGER_EMOJI.get(manager, "") if manager else "",
            "franchise_id": _clean(row.get("franchise_id")),
            "source": _clean(row.get("source")) or "computed",
            "is_editorial": _clean(row.get("source")) == "editorial",
            "era": eras.get(season, {"name": "", "color": "#6B7280"}),
            "show_on_league_timeline": bool(row.get("show_on_league_timeline")),
            "show_on_homepage": bool(row.get("show_on_homepage")),
        })

    editorial = sum(1 for e in events if e["is_editorial"])
    return {
        "events": events,
        "stats": {
            "total_events": len(events),
            "total_seasons": len({e["season"] for e in events}),
            "computed_events": len(events) - editorial,
            "editorial_events": editorial,
        },
        "filter_groups": narratives.TIMELINE_FILTER_GROUPS,
        "all_types": narratives.TIMELINE_ALL_TYPES,
    }


def group_timeline_by_season(events: list[dict], newest_first: bool = True) -> list[dict]:
    """Group enriched events into the per-season blocks the timeline renders.

    Pure function over the output of get_timeline_view() so the page and the
    static site lay the timeline out the same way after filtering.
    """
    by_season: dict[int, list[dict]] = {}
    for event in events:
        by_season.setdefault(event["season"], []).append(event)

    blocks = []
    for season in sorted(by_season, reverse=newest_first):
        # Stable within equal importance, so the CSV's own order is preserved.
        season_events = sorted(by_season[season], key=lambda e: e["importance_rank"])
        editorial = sum(1 for e in season_events if e["is_editorial"])
        count_label = f"{len(season_events)} event{'s' if len(season_events) != 1 else ''}"
        if editorial:
            count_label += f" · {editorial} editorial"

        blocks.append({
            "season": season,
            "era": season_events[0]["era"],
            "count_label": count_label,
            "event_count": len(season_events),
            "editorial_count": editorial,
            "high": [e for e in season_events if e["importance"] == "high"],
            "other": [e for e in season_events if e["importance"] != "high"],
        })
    return blocks


# ── HOME VIEW ─────────────────────────────────────────────────────────────────
# Lifted out of app.py. Every ranking here carries an explicit tie-break: the
# originals used the default non-stable quicksort, so a tie could reorder the
# league legends or change which manager was named between restarts.

@st.cache_data
def get_home_view() -> dict:
    from utils import narratives

    data = load_all()
    champions = get_champions()
    manager_stats = get_manager_stats()
    standings = data["standings"]
    weekly = data["weekly_matchups"]
    manager_by_team = (
        data["team_name_history"].set_index(["season", "team_name"])["canonical_name"].to_dict()
    )

    # ── Headline counts ──────────────────────────────────────────────────────
    stats = {
        "seasons": int(CURRENT_SEASON - FOUNDED + 1),
        "active_managers": int((manager_stats["last_season"] == CURRENT_SEASON).sum()),
        "unique_champions": int(champions["champion_manager"].nunique()),
        "total_games": int(len(weekly[~weekly["is_bye"].astype(bool)]) // 2),
    }

    def _champion_entry(row) -> dict:
        manager = row["champion_manager"]
        return {
            "season": int(row["season"]),
            "manager": manager,
            "team": row["champion_team"],
            "emoji": MANAGER_EMOJI.get(manager, "🏆"),
            "score": round(float(row["champion_score"]), 2),
            "runner_up_team": row["runner_up_team"],
            "runner_up_score": round(float(row["runner_up_score"]), 2),
            "titles_to_date": int(
                ((champions["champion_manager"] == manager)
                 & (champions["season"] <= row["season"])).sum()
            ),
            "titles_all_time": int((champions["champion_manager"] == manager).sum()),
        }

    current_rows = champions[champions["season"] == CURRENT_SEASON]
    current_champion = _champion_entry(current_rows.iloc[0]) if len(current_rows) else None

    recent = champions[champions["season"] < CURRENT_SEASON].tail(5).iloc[::-1]
    recent_champions = [_champion_entry(r) for _, r in recent.iterrows()]

    # ── League legends ───────────────────────────────────────────────────────
    grouped = (
        champions.groupby("champion_manager")
        .agg(titles=("season", "count"),
             years=("season", lambda s: ", ".join(str(y) for y in sorted(s))))
        .reset_index()
        .sort_values(["titles", "champion_manager"], ascending=[False, True], kind="mergesort")
    )
    legends = [
        {
            "manager": r["champion_manager"],
            "titles": int(r["titles"]),
            "years": r["years"],
            "emoji": MANAGER_EMOJI.get(r["champion_manager"], "👤"),
        }
        for _, r in grouped.iterrows()
    ]

    # ── Best regular season ever ─────────────────────────────────────────────
    played = standings.copy()
    played["games"] = played["wins"] + played["losses"] + played["ties"]
    played["win_pct"] = played["wins"] / played["games"].replace(0, float("nan"))
    best = played[played["win_pct"] == played["win_pct"].max()].sort_values(
        ["season", "team_name"], kind="mergesort"
    )
    champion_by_season = dict(zip(champions["season"], champions["champion_manager"]))
    best_entries = [
        {
            "manager": manager_by_team.get((int(r["season"]), r["team_name"]), r["team_name"]),
            "season": int(r["season"]),
            "won_title": champion_by_season.get(int(r["season"]))
                         == manager_by_team.get((int(r["season"]), r["team_name"])),
        }
        for _, r in best.iterrows()
    ]
    best_record = (
        f"{int(best.iloc[0]['wins'])}-{int(best.iloc[0]['losses'])}" if len(best) else ""
    )

    # ── Storylines ───────────────────────────────────────────────────────────
    droughts = manager_stats[
        (manager_stats["championships"] == 0) & (manager_stats["active"])
    ].sort_values(["playoff_apps", "canonical_name"], ascending=[False, True], kind="mergesort")
    drought = None
    if len(droughts) and int(droughts.iloc[0]["playoff_apps"]) >= 3:
        row = droughts.iloc[0]
        drought = {
            "manager": row["canonical_name"],
            "playoff_apps": int(row["playoff_apps"]),
            "emoji": MANAGER_EMOJI.get(row["canonical_name"], "👤"),
        }

    scorer = manager_stats.sort_values(
        ["points_for", "canonical_name"], ascending=[False, True], kind="mergesort"
    ).iloc[0]

    return {
        "stats": stats,
        "current_champion": current_champion,
        "recent_champions": recent_champions,
        "legends": legends,
        "drought": drought,
        "storylines": {
            "most_championships": {
                "manager": legends[0]["manager"],
                "titles": legends[0]["titles"],
                "years": legends[0]["years"],
            } if legends else None,
            "best_season": {
                "record": best_record,
                "seasons": [e["season"] for e in best_entries],
                "managers": [e["manager"] for e in best_entries],
                "summary": narratives.best_season_summary(best_entries, best_record),
            },
            "top_scorer": {
                "manager": scorer["canonical_name"],
                "points_for": round(float(scorer["points_for"]), 2),
            },
        },
    }


# ── LEAGUE HISTORY VIEW ───────────────────────────────────────────────────────
# Lifted out of pages/league_history.py.
#
# Two defects fixed on the way out:
#   * The scoring chart shaded eras from a hardcoded ERA_SHADES list that
#     duplicated LEAGUE_ERAS — and had already drifted, labelling the third era
#     "Keeper Rev." where the era cards on the same page said "Keepers". Era
#     bands are now derived from LEAGUE_ERAS, so there is one definition.
#   * Championship counts are full of ties (two managers on 4, four on 2, four
#     on 1) and were ranked with the default non-stable sort, so the bar chart
#     reordered between restarts.

def _rgba(hex_color: str, alpha: float) -> str:
    """#RRGGBB -> rgba(r,g,b,alpha)."""
    value = hex_color.lstrip("#")
    r, g, b = (int(value[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


@st.cache_data
def get_season_scoring() -> pd.DataFrame:
    """Average, high and low points-for per season."""
    return (
        load_all()["standings"]
        .groupby("season")["points_for"]
        .agg(avg="mean", high="max", low="min")
        .reset_index()
        .sort_values("season")
    )


@st.cache_data
def get_league_history_view() -> dict:
    from utils import narratives

    data = load_all()
    champions = get_champions()
    standings = data["standings"]
    weekly = data["weekly_matchups"]
    playoff_games = data["playoff_games"]
    manager_by_team = (
        data["team_name_history"].set_index(["season", "team_name"])["canonical_name"].to_dict()
    )

    def manager_of(season, team):
        return manager_by_team.get((int(season), team), team)

    scoring = get_season_scoring()
    regular = weekly[~weekly["is_bye"].astype(bool) & ~weekly["is_playoff"].astype(bool)].copy()

    # ── Eras ─────────────────────────────────────────────────────────────────
    eras = []
    for era in narratives.LEAGUE_ERAS:
        start, end = era["start"], min(era["end"], CURRENT_SEASON)
        era_champs = champions[champions["season"].between(start, end)].sort_values("season")
        era_scoring = scoring[scoring["season"].between(start, end)]
        eras.append({
            "name": era["name"],
            "short": era["short"],
            "years": era["years"],
            "color": era["color"],
            "icon": era["icon"],
            "headline": era["headline"],
            "body": era["body"],
            "start": start,
            "end": end,
            "titles_awarded": len(era_champs),
            "unique_champions": int(era_champs["champion_manager"].nunique()),
            "avg_score": round(float(era_scoring["avg"].mean()), 2) if len(era_scoring) else 0.0,
            "champions": [
                {
                    "season": int(r["season"]),
                    "manager": r["champion_manager"],
                    "emoji": MANAGER_EMOJI.get(r["champion_manager"], "🏆"),
                }
                for _, r in era_champs.iterrows()
            ],
        })

    # ── Scoring evolution ────────────────────────────────────────────────────
    champion_pf = []
    for _, ch in champions.iterrows():
        row = standings[
            (standings["season"] == ch["season"]) & (standings["team_name"] == ch["champion_team"])
        ]
        if len(row):
            champion_pf.append({
                "season": int(ch["season"]),
                "points_for": round(float(row.iloc[0]["points_for"]), 2),
            })

    peak = scoring.loc[scoring["avg"].idxmax()]
    lean = scoring.loc[scoring["avg"].idxmin()]

    # ── Competitive balance ──────────────────────────────────────────────────
    championship_bracket = playoff_games[playoff_games["bracket"] == "championship"]
    playoff_managers: dict[int, list[str]] = {}
    for season in sorted(champions["season"].unique()):
        games = championship_bracket[championship_bracket["season"] == season]
        teams = set(games["team_1"].tolist() + games["team_2"].tolist())
        playoff_managers[int(season)] = sorted({manager_of(season, t) for t in teams})

    appearances: dict[str, int] = {}
    for managers in playoff_managers.values():
        for manager in managers:
            appearances[manager] = appearances.get(manager, 0) + 1
    # Explicit tie-break: value_counts() ordered ties by set-iteration order.
    ranked_playoff = sorted(appearances.items(), key=lambda kv: (-kv[1], kv[0]))

    title_counts = sorted(
        champions.groupby("champion_manager").size().items(),
        key=lambda kv: (-kv[1], kv[0]),
    )
    total_titles = len(champions)
    total_seasons = CURRENT_SEASON - FOUNDED + 1
    unique_champions = int(champions["champion_manager"].nunique())

    # ── Records ──────────────────────────────────────────────────────────────
    wins = regular[regular["result"] == "Win"].copy()
    wins["margin"] = wins["team_score"] - wins["opponent_score"]
    week_high = regular.loc[regular["team_score"].idxmax()]
    blowout = wins.loc[wins["margin"].idxmax()]
    closest = wins.loc[wins["margin"].idxmin()]

    played = standings.copy()
    played["games"] = played["wins"] + played["losses"] + played["ties"]
    played["win_pct"] = played["wins"] / played["games"].replace(0, float("nan"))
    best_record = played.loc[played["win_pct"].idxmax()]
    best_points = standings.loc[standings["points_for"].idxmax()]

    def _record(row, extra=None) -> dict:
        base = {
            "season": int(row["season"]),
            "team": row["team_name"],
            "manager": manager_of(row["season"], row["team_name"]),
        }
        return {**base, **(extra or {})}

    return {
        "eras": eras,
        "era_bands": [
            {
                "start": e["start"],
                "end": e["end"],
                "label": e["short"],
                "color": e["color"],
                # Pre-mixed for the chart: Plotly rejects 8-digit hex, and the
                # page shouldn't be doing colour maths.
                "fill": _rgba(e["color"], 0.06),
            }
            for e in eras
        ],
        "scoring": {
            "by_season": [
                {
                    "season": int(r["season"]),
                    "avg": round(float(r["avg"]), 1),
                    "high": round(float(r["high"]), 1),
                    "low": round(float(r["low"]), 1),
                }
                for _, r in scoring.iterrows()
            ],
            "champion_points": champion_pf,
            "peak": {"season": int(peak["season"]), "avg": round(float(peak["avg"]), 1)},
            "lean": {"season": int(lean["season"]), "avg": round(float(lean["avg"]), 1)},
            "rise": round(float(peak["avg"]) - float(lean["avg"]), 1),
        },
        "balance": {
            "unique_champions": unique_champions,
            "total_seasons": int(total_seasons),
            "diversity_rate": round(unique_champions / total_seasons, 4),
            "playoff_managers_ever": len(appearances),
            "most_consistent": (
                {
                    "manager": ranked_playoff[0][0],
                    "appearances": ranked_playoff[0][1],
                    "emoji": MANAGER_EMOJI.get(ranked_playoff[0][0], ""),
                }
                if ranked_playoff else None
            ),
            "title_counts": [{"manager": m, "titles": int(n)} for m, n in title_counts],
            "top1_pct": int(title_counts[0][1] / total_titles * 100) if title_counts else 0,
            "top3_pct": int(sum(n for _, n in title_counts[:3]) / total_titles * 100) if title_counts else 0,
        },
        "records": {
            "week_high": _record(week_high, {
                "week": int(week_high["week"]), "points": round(float(week_high["team_score"]), 2),
            }),
            "blowout": _record(blowout, {
                "week": int(blowout["week"]), "margin": round(float(blowout["margin"]), 2),
            }),
            "closest": _record(closest, {
                "week": int(closest["week"]), "margin": round(float(closest["margin"]), 2),
                "loser": manager_of(closest["season"], closest["opponent"]),
            }),
            "best_record": _record(best_record, {
                "wins": int(best_record["wins"]), "losses": int(best_record["losses"]),
            }),
            "best_points": _record(best_points, {
                "points_for": round(float(best_points["points_for"]), 1),
            }),
        },
    }


# ── CHAMPIONS VIEW ────────────────────────────────────────────────────────────
# Lifted out of pages/champions.py, which had seven rankings resolved by the
# default non-stable sort — runner-up counts, third-place counts, finals
# appearances, active-no-title, best-regular-season-no-title, and the per-season
# best record — all of which have real ties in this data. It also assigned
# columns onto the cached champions frame; everything here works on copies.

@st.cache_data
def get_champions_view() -> dict:
    data = load_all()
    champions = get_champions().copy()
    manager_stats = get_manager_stats()
    standings = data["standings"]
    playoff_games = data["playoff_games"]
    tnh = data["team_name_history"]
    franchise_history = data["franchise_history"]

    manager_by_team = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()
    emoji = lambda name: MANAGER_EMOJI.get(name, "👤")  # noqa: E731

    champions["margin"] = champions["champion_score"] - champions["runner_up_score"]
    champions["combined"] = champions["champion_score"] + champions["runner_up_score"]

    # ── Finals records ───────────────────────────────────────────────────────
    titles = champions.groupby("champion_manager").size()
    runner_ups = champions.groupby("runner_up_manager").size()
    finals: dict[str, dict] = {}
    for name in sorted(set(titles.index) | set(runner_ups.index)):
        won, lost = int(titles.get(name, 0)), int(runner_ups.get(name, 0))
        finals[name] = {
            "titles": won,
            "runner_ups": lost,
            "finals_apps": won + lost,
            "win_pct": round(won / (won + lost), 2) if won + lost else 0.0,
        }

    # ── Manager leaders ──────────────────────────────────────────────────────
    grouped = (
        champions.groupby("champion_manager")
        .agg(championships=("season", "count"),
             first=("season", "min"), last=("season", "max"),
             year_list=("season", lambda s: sorted(int(y) for y in s)))
        .reset_index()
        .sort_values(["championships", "last", "champion_manager"],
                     ascending=[False, False, True], kind="mergesort")
    )
    manager_leaders = [
        {
            "manager": r["champion_manager"],
            "emoji": emoji(r["champion_manager"]),
            "championships": int(r["championships"]),
            "years": ", ".join(str(y) for y in r["year_list"]),
            "year_list": r["year_list"],
            "first": int(r["first"]),
            "last": int(r["last"]),
            **finals.get(r["champion_manager"], {}),
        }
        for _, r in grouped.iterrows()
    ]

    # ── Franchise leaders ────────────────────────────────────────────────────
    fh_named = franchise_history.merge(
        tnh.rename(columns={"canonical_name": "manager_name"}),
        on=["season", "manager_name"], how="left",
    )
    champ_teams = champions[["season", "champion_team"]].rename(columns={"champion_team": "team_name"})
    fran_wins = fh_named.merge(champ_teams, on=["season", "team_name"], how="inner")
    current_managers = dict(
        franchise_history[franchise_history["season"] == CURRENT_SEASON]
        [["franchise_id", "manager_name"]].values
    )
    fran_grouped = (
        fran_wins.groupby("franchise_id")
        .agg(championships=("season", "count"), last=("season", "max"),
             year_list=("season", lambda s: sorted(int(y) for y in s)))
        .reset_index()
        .sort_values(["championships", "last", "franchise_id"],
                     ascending=[False, False, True], kind="mergesort")
    )
    franchise_leaders = [
        {
            "franchise_id": r["franchise_id"],
            "current_manager": current_managers.get(r["franchise_id"], "—"),
            "emoji": emoji(current_managers.get(r["franchise_id"], "")) if current_managers.get(r["franchise_id"]) else "🏟️",
            "championships": int(r["championships"]),
            "years": ", ".join(str(y) for y in r["year_list"]),
            "last": int(r["last"]),
        }
        for _, r in fran_grouped.iterrows()
    ]

    # ── Dynasties ────────────────────────────────────────────────────────────
    dynasties = []
    for leader in manager_leaders:
        if leader["championships"] < 2:
            continue
        years = leader["year_list"]
        consecutive = all(years[i + 1] == years[i] + 1 for i in range(len(years) - 1))
        span = leader["last"] - leader["first"] + 1
        dynasties.append({
            **leader,
            "consecutive": consecutive,
            "span": span,
            "era_desc": (
                f'{leader["championships"]} consecutive championships' if consecutive
                else f'{leader["championships"]} titles across {span} seasons '
                     f'({leader["first"]}–{leader["last"]})'
            ),
        })

    # ── Ranked helpers with explicit tie-breaks ──────────────────────────────
    def _ranked(counts: dict) -> list[tuple[str, int]]:
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    ru_ranked = _ranked({k: int(v) for k, v in runner_ups.items()})

    third_place = playoff_games[
        (playoff_games["bracket"] == "championship") & (playoff_games["game_type"] == "3rd_place")
    ]
    third_counts: dict[str, list[int]] = {}
    for _, g in third_place.iterrows():
        team = g["team_1"] if g["winner"] == g["team_1"] else g["team_2"]
        manager = manager_by_team.get((int(g["season"]), team), team)
        third_counts.setdefault(manager, []).append(int(g["season"]))
    third_ranked = sorted(
        ((m, len(y), sorted(y)) for m, y in third_counts.items()),
        key=lambda t: (-t[1], t[0]),
    )

    finals_ranked = sorted(
        finals.items(), key=lambda kv: (-kv[1]["finals_apps"], kv[0])
    )

    # ── Best regular season that didn't win it all ───────────────────────────
    best_rs_no_title = []
    for _, champ in champions.iterrows():
        season = int(champ["season"])
        table = standings[standings["season"] == season].copy()
        table["manager"] = table.apply(
            lambda r: manager_by_team.get((season, r["team_name"])), axis=1
        )
        table = table.dropna(subset=["manager"])
        table["games"] = table["wins"] + table["losses"] + table["ties"]
        table["win_pct"] = table["wins"] / table["games"].replace(0, float("nan"))
        table = table.sort_values(["win_pct", "points_for", "manager"],
                                  ascending=[False, False, True], kind="mergesort")
        if not len(table):
            continue
        best = table.iloc[0]
        if best["manager"] != champ["champion_manager"]:
            best_rs_no_title.append({
                "season": season,
                "manager": best["manager"],
                "emoji": emoji(best["manager"]),
                "wins": int(best["wins"]),
                "losses": int(best["losses"]),
                "win_pct": round(float(best["win_pct"] or 0), 4),
            })
    best_rs_no_title.sort(key=lambda r: (-r["win_pct"], r["season"]))

    still_waiting = manager_stats[
        (manager_stats["championships"] == 0) & (manager_stats["playoff_apps"] >= 3)
    ].sort_values(["playoff_apps", "canonical_name"], ascending=[False, True], kind="mergesort")

    # ── Back-to-back (most recent successful defence) ────────────────────────
    ordered = champions.sort_values("season").reset_index(drop=True)
    back_to_back = None
    for i in range(1, len(ordered)):
        if (ordered.iloc[i]["champion_manager"] == ordered.iloc[i - 1]["champion_manager"]
                and ordered.iloc[i]["season"] == ordered.iloc[i - 1]["season"] + 1):
            back_to_back = {
                "manager": ordered.iloc[i]["champion_manager"],
                "season": int(ordered.iloc[i]["season"]),
                "team": ordered.iloc[i]["champion_team"],
            }

    def _final(row) -> dict:
        return {
            "season": int(row["season"]),
            "champion_manager": row["champion_manager"],
            "champion_team": row["champion_team"],
            "champion_score": round(float(row["champion_score"]), 2),
            "runner_up_manager": row["runner_up_manager"],
            "runner_up_team": row["runner_up_team"],
            "runner_up_score": round(float(row["runner_up_score"]), 2),
            "margin": round(float(row["margin"]), 2),
            "combined": round(float(row["combined"]), 2),
            "emoji": MANAGER_EMOJI.get(row["champion_manager"], "🏆"),
        }

    current_rows = champions[champions["season"] == CURRENT_SEASON]

    return {
        "totals": {
            "seasons": int(CURRENT_SEASON - FOUNDED + 1),
            "titles_awarded": len(champions),
            "unique_managers": int(champions["champion_manager"].nunique()),
        },
        "top_manager": manager_leaders[0] if manager_leaders else None,
        "current_champion": _final(current_rows.iloc[0]) if len(current_rows) else None,
        "manager_leaders": manager_leaders,
        "franchise_leaders": franchise_leaders,
        "chronological": sorted(manager_leaders, key=lambda m: (m["first"], m["manager"])),
        "dynasties": dynasties,
        "trivia": {
            "biggest_blowout": _final(champions.loc[champions["margin"].idxmax()]),
            "closest_final": _final(champions.loc[champions["margin"].idxmin()]),
            "most_runner_up": {
                "manager": ru_ranked[0][0], "count": ru_ranked[0][1],
                "emoji": emoji(ru_ranked[0][0]),
            } if ru_ranked else None,
            "highest_scoring_final": _final(champions.loc[champions["combined"].idxmax()]),
            "lowest_scoring_final": _final(champions.loc[champions["combined"].idxmin()]),
            "most_finals": {
                "manager": finals_ranked[0][0], **finals_ranked[0][1],
            } if finals_ranked else None,
            "back_to_back": back_to_back,
            "highest_winning_score": _final(champions.loc[champions["champion_score"].idxmax()]),
            "first_champion": _final(ordered.iloc[0]),
        },
        "pain": {
            "most_runner_up": {
                "manager": ru_ranked[0][0],
                "count": ru_ranked[0][1],
                "emoji": emoji(ru_ranked[0][0]),
                "years": sorted(
                    int(s) for s in champions[champions["runner_up_manager"] == ru_ranked[0][0]]["season"]
                ),
            } if ru_ranked else None,
            "most_third": {
                "manager": third_ranked[0][0], "count": third_ranked[0][1],
                "years": third_ranked[0][2], "emoji": emoji(third_ranked[0][0]),
            } if third_ranked else None,
            "still_waiting": {
                "manager": still_waiting.iloc[0]["canonical_name"],
                "playoff_apps": int(still_waiting.iloc[0]["playoff_apps"]),
                "emoji": emoji(still_waiting.iloc[0]["canonical_name"]),
            } if len(still_waiting) else None,
            "closest_loss": _final(champions.loc[champions["margin"].idxmin()]),
            "biggest_loss": _final(champions.loc[champions["margin"].idxmax()]),
            "best_rs_no_title": best_rs_no_title[0] if best_rs_no_title else None,
        },
        "finals": [_final(r) for _, r in champions.sort_values("season", ascending=False).iterrows()],
    }


# ── MANAGER PROFILES ──────────────────────────────────────────────────────────
# Lifted out of pages/manager_profiles.py. The head-to-head highlights are a
# pure helper rather than baked in, because the page scopes them to current
# members or all-time — the same shape the static site will need.

_DRAFT_SKILL_POSITIONS = ["QB", "RB", "WR", "TE"]


def _finals_records() -> dict[str, dict]:
    champions = get_champions()
    titles = champions.groupby("champion_manager").size()
    runner_ups = champions.groupby("runner_up_manager").size()
    return {
        name: {
            "titles": int(titles.get(name, 0)),
            "runner_ups": int(runner_ups.get(name, 0)),
            "finals_apps": int(titles.get(name, 0)) + int(runner_ups.get(name, 0)),
        }
        for name in sorted(set(titles.index) | set(runner_ups.index))
    }


def manager_h2h_highlights(rows: list[dict], min_games: int = 5) -> dict:
    """Most-played, favourite victim and toughest opponent for a set of H2H rows.

    Pure function so the page can scope it to current members or all-time and
    the static site can do the same client-side. The victim/nemesis sorts carry
    an explicit tie-break; the originals used the default non-stable sort.
    """
    if not rows:
        return {"most_played": None, "victim": None, "nemesis": None}

    eligible = [r for r in rows if r["games"] >= min_games]
    by_win_pct = sorted(eligible, key=lambda r: (-r["win_pct"], r["opp_manager"]))
    return {
        "most_played": rows[0],
        "victim": by_win_pct[0] if by_win_pct else None,
        "nemesis": sorted(eligible, key=lambda r: (r["win_pct"], r["opp_manager"]))[0] if eligible else None,
    }


def _season_result_category(result: str) -> str:
    result = str(result)
    if "Champion" in result:
        return "Champion"
    if "Runner-Up" in result:
        return "Runner-Up"
    if "3rd" in result or "4th" in result:
        return "3rd / 4th"
    return "Playoffs" if result != "—" else "Missed"


@st.cache_data
def get_manager_directory() -> dict:
    """Active and former managers, in the order the selector shows them."""
    stats = get_manager_stats()
    return {
        "active": stats[stats["active"]]["canonical_name"].tolist(),
        "former": stats[~stats["active"]]["canonical_name"].tolist(),
    }


@st.cache_data
def get_manager_profile(name: str) -> dict:
    from utils import narratives

    stats = get_manager_stats()
    row = stats[stats["canonical_name"] == name].iloc[0]
    champions = get_champions()
    finals = _finals_records().get(name, {"titles": 0, "runner_ups": 0, "finals_apps": 0})

    championships = int(row["championships"])
    runner_ups = int(row["runner_ups"])
    playoff_apps = int(row["playoff_apps"])
    seasons_played = int(row["seasons_played"])
    wins, losses, ties = int(row["wins"]), int(row["losses"]), int(row["ties"])
    is_active = bool(row["active"])
    champ_years = sorted(int(s) for s in champions[champions["champion_manager"] == name]["season"])

    # ── Season history, chart-ready ──────────────────────────────────────────
    history = get_manager_season_history(name).copy()
    seasons = []
    for _, h in history.iterrows():
        played = int(h["W"]) + int(h["L"]) + int(h["T"])
        seasons.append({
            "season": int(h["Season"]),
            "team_name": h["Team Name"],
            "wins": int(h["W"]), "losses": int(h["L"]), "ties": int(h["T"]),
            "points_for": round(float(h["PF"]), 2),
            "points_against": round(float(h["PA"]), 2) if "PA" in history.columns else None,
            "rank": int(h["Rank"]) if h["Rank"] else None,
            "result": str(h["Result"]),
            "category": _season_result_category(h["Result"]),
            "win_pct": round(int(h["W"]) / played, 3) if played else None,
        })

    # ── Head to head ─────────────────────────────────────────────────────────
    active_managers = set(stats[stats["active"]]["canonical_name"])
    h2h = [
        {
            "opp_manager": r["opp_manager"],
            "opp_emoji": MANAGER_EMOJI.get(r["opp_manager"], "👤"),
            "opp_active": r["opp_manager"] in active_managers,
            "games": int(r["games"]), "wins": int(r["wins"]), "losses": int(r["losses"]),
            "win_pct": round(float(r["win_pct"]), 4),
            "pf": round(float(r["pf"]), 1), "pa": round(float(r["pa"]), 1),
        }
        for _, r in get_manager_h2h(name).iterrows()
    ]

    # ── Draft identity ───────────────────────────────────────────────────────
    picks = get_draft_picks_with_pos()
    mine = picks[picks["manager"] == name]
    drafted = mine[~mine["is_keeper"]]
    kept = mine[mine["is_keeper"]]
    draft = None
    if len(drafted):
        # Each season's first live pick — a keeper consumes the round-1 slot in
        # several eras, so literal round 1 undercounts (see get_draft_center_view).
        first_picks = drafted.loc[drafted.groupby("season")["overall_pick"].idxmin()]
        round_one = first_picks[
            first_picks["position"].isin(_DRAFT_SKILL_POSITIONS + ["DEF", "K"])
        ]
        counts = {p: int(n) for p, n in round_one["position"].value_counts().items()}
        total = len(round_one)
        keeper_rate = len(kept) / len(mine) if len(mine) else 0.0

        def _share(position: str) -> float:
            return counts.get(position, 0) / total if total else 0.0

        if total == 0:
            style, style_color = "UNKNOWN", "#6B7280"
        elif _share("RB") >= 0.55:
            style, style_color = "RB HOARDER", "#22C55E"
        elif _share("WR") >= 0.45:
            style, style_color = "WR COLLECTOR", "#3B82F6"
        elif _share("QB") >= 0.35:
            style, style_color = "QB LOYALIST", "#EF4444"
        elif _share("TE") >= 0.15:
            style, style_color = "TE FIRST BELIEVER", "#F59E0B"
        elif keeper_rate >= 0.08:
            style, style_color = "KEEPER MAXIMIZER", "#A78BFA"
        else:
            style, style_color = "BALANCED DRAFTER", "#A7B0BC"

        def _top_player(frame) -> tuple[str, int]:
            named = frame[frame["position"] != "DEF"]
            if not len(named):
                return "—", 0
            # Explicit tie-break; value_counts() ordered ties arbitrarily.
            tally = sorted(
                named["player_name"].value_counts().items(), key=lambda kv: (-kv[1], kv[0])
            )
            return tally[0][0], int(tally[0][1])

        most_drafted, most_drafted_n = _top_player(drafted)
        most_kept, most_kept_n = _top_player(kept)

        draft = {
            "round_one_counts": counts,
            "round_one_total": total,
            "style": style,
            "style_color": style_color,
            "keeper_rate": round(keeper_rate, 4),
            "most_drafted": {"player": most_drafted, "count": most_drafted_n},
            "most_kept": {"player": most_kept, "count": most_kept_n},
        }

    # ── Team name history, consecutive runs collapsed ────────────────────────
    tnh = load_all()["team_name_history"]
    mine_names = tnh[tnh["canonical_name"] == name].sort_values("season")
    runs: list[dict] = []
    for _, r in mine_names.iterrows():
        season, team = int(r["season"]), r["team_name"]
        if runs and runs[-1]["team_name"] == team:
            runs[-1]["end"] = season
        else:
            runs.append({"team_name": team, "start": season, "end": season})
    for run in runs:
        run["years"] = str(run["start"]) if run["start"] == run["end"] else f'{run["start"]}–{run["end"]}'

    return {
        "name": name,
        "display_name": row["display_name"],
        "emoji": MANAGER_EMOJI.get(name, "👤"),
        "color": MANAGER_COLORS.get(name, "#D4AF37"),
        "active": is_active,
        "first_season": int(row["first_season"]),
        "last_season": int(row["last_season"]),
        "status_label": (
            f'Active · {int(row["first_season"])}–Present' if is_active
            else f'{int(row["first_season"])}–{int(row["last_season"])}'
        ),
        "metrics": {
            "championships": championships,
            "runner_ups": runner_ups,
            "playoff_apps": playoff_apps,
            "seasons_played": seasons_played,
            "playoff_rate": round(playoff_apps / seasons_played, 4) if seasons_played else 0.0,
            "record": f"{wins}-{losses}" + (f"-{ties}" if ties else ""),
            "win_pct": round(float(row["win_pct"]), 3) if (wins + losses + ties) else 0.0,
            **finals,
        },
        "championship_years": champ_years,
        "plaque": narratives.manager_plaque(
            championships=championships,
            runner_ups=runner_ups,
            playoff_apps=playoff_apps,
            seasons_played=seasons_played,
            championship_years=champ_years,
            is_active=is_active,
        ),
        "identity": narratives.MANAGER_IDENTITY.get(name, ""),
        "seasons": seasons,
        "head_to_head": h2h,
        "draft": draft,
        "team_names": runs,
    }


# ── DRAFT CENTER ──────────────────────────────────────────────────────────────
# Lifted out of pages/draft_center.py. Four more arbitrary tie-breaks fixed:
# the most-loyal-owner pick, the best round-one find, the player legend ranking,
# and the round-one player counts.

DRAFT_SKILL_POSITIONS = ["QB", "RB", "WR", "TE"]
DRAFT_POSITION_ORDER = ["RB", "WR", "QB", "TE", "DEF", "K", "Other"]


@st.cache_data
def get_draft_center_view() -> dict:
    from utils import narratives

    picks = get_draft_picks_with_pos()
    ownership = get_player_ownership()
    stats = get_manager_stats().set_index("canonical_name")

    drafted = picks[~picks["is_keeper"]]
    kept = picks[picks["is_keeper"]]
    round_one = drafted[drafted["round"] == 1]

    # ── Player legends: who the league could not stop drafting ───────────────
    skill = ownership[ownership["position"].isin(DRAFT_SKILL_POSITIONS)]
    seasons_drafted = picks.groupby("player_name")["season"].nunique()
    league_seasons = ownership.groupby("player_name")["total_seasons"].sum().to_dict()

    # Most devoted owner: most seasons with the player. Ties resolved by name —
    # the original kept whichever row sorted first, which was arbitrary.
    most_loyal: dict[str, str] = {}
    for player, group in skill.groupby("player_name"):
        ranked = sorted(
            ((r["manager"], int(r["total_seasons"])) for _, r in group.iterrows()),
            key=lambda kv: (-kv[1], kv[0]),
        )
        most_loyal[player] = ranked[0][0] if ranked else None

    legends_frame = (
        skill.groupby("player_name")
        .agg(total_drafts=("draft_count", "sum"),
             unique_managers=("manager", "nunique"),
             first_season=("first_season", "min"),
             last_season=("last_season", "max"),
             position=("position", "first"))
        .reset_index()
    )
    legends = []
    for _, r in legends_frame.iterrows():
        player = r["player_name"]
        span = int(seasons_drafted.get(player, 0))
        drafters = ownership[(ownership["player_name"] == player) & (ownership["draft_count"] > 0)]
        legends.append({
            "player_name": player,
            "position": str(r["position"]) if r["position"] else "?",
            "total_drafts": int(r["total_drafts"]),
            "unique_managers": int(r["unique_managers"]),
            "first_season": int(r["first_season"]),
            "last_season": int(r["last_season"]),
            "career_span": span,
            "most_loyal": most_loyal.get(player),
            "story": narratives.player_obsession_story(
                drafts=int(r["total_drafts"]), managers=int(r["unique_managers"]),
                career_span=span, first_season=int(r["first_season"]),
                last_season=int(r["last_season"]), most_loyal=most_loyal.get(player),
                position=str(r["position"]) if r["position"] else "?",
            ),
            "drafters": sorted(
                ({"manager": d["manager"], "count": int(d["draft_count"]),
                  "emoji": MANAGER_EMOJI.get(d["manager"], "👤"),
                  "color": MANAGER_COLORS.get(d["manager"], "#6B7280")}
                 for _, d in drafters.iterrows()),
                key=lambda d: (-d["count"], d["manager"]),
            ),
        })
    # Five players tie at 13 drafts for the last two slots of the top-8 panel,
    # so this ranking is load-bearing. Ties break on breadth of obsession
    # (managers, then career span) before falling back to name.
    legends.sort(key=lambda p: (
        -p["total_drafts"], -p["unique_managers"], -p["career_span"], p["player_name"],
    ))

    # ── Manager draft DNA ────────────────────────────────────────────────────
    # A keeper consumes a draft slot, so a manager's first *live* pick is their
    # first real choice of that draft — which is not always round 1.
    #
    # In 2003, 2011 and 2013 every team kept a player at round-1 cost, so live
    # drafting began in round 2; reading literal round 1 lost those seasons
    # entirely. From 2014 the same thing happens to individual managers whose
    # keeper costs round 1. Taking each manager's earliest non-keeper pick
    # covers all 25 seasons and treats every era the same way.
    r1_named = drafted[drafted["position"].notna()].copy()
    r1_named = r1_named.loc[
        r1_named.groupby(["season", "manager"])["overall_pick"].idxmin()
    ]
    r1_named["pos_group"] = r1_named["position"].apply(
        lambda p: p if p in DRAFT_SKILL_POSITIONS + ["DEF", "K"] else "Other"
    )
    grid = r1_named.groupby(["manager", "pos_group"]).size().unstack(fill_value=0)
    keeper_rates = (kept.groupby("manager").size() / picks.groupby("manager").size()).fillna(0)

    # Best first-pick find: the manager's first-pick skill selection with the
    # most league-wide ownership. Ties resolved by player name.
    best_find: dict[str, str] = {}
    r1_skill = r1_named[r1_named["position"].isin(DRAFT_SKILL_POSITIONS)]
    for manager, group in r1_skill.groupby("manager"):
        players = sorted(set(group["player_name"]))
        if players:
            best_find[manager] = max(players, key=lambda p: (league_seasons.get(p, 0), p))

    dna = []
    for manager in grid.index:
        counts = {pos: int(grid.loc[manager].get(pos, 0)) for pos in DRAFT_POSITION_ORDER}
        total = sum(counts.values())
        if total < 4:  # not enough evidence to read a pattern
            continue
        shares = {pos: counts[pos] / total for pos in counts}
        shares["total"] = total
        keeper_rate = float(keeper_rates.get(manager, 0.0))
        championships = int(stats.loc[manager, "championships"]) if manager in stats.index else 0
        seasons_played = int(stats.loc[manager, "seasons_played"]) if manager in stats.index else 1
        playoff_apps = int(stats.loc[manager, "playoff_apps"]) if manager in stats.index else 0
        label, color, blurb = narratives.draft_archetype(
            shares, keeper_rate=keeper_rate, championships=championships
        )
        # max() returns the first maximal element, so the fixed position order
        # already decides ties deterministically — matching the original.
        top_position = max(["RB", "WR", "QB", "TE", "DEF", "K"], key=lambda p: counts.get(p, 0))
        dna.append({
            "manager": manager,
            "emoji": MANAGER_EMOJI.get(manager, "👤"),
            "color": MANAGER_COLORS.get(manager, "#6B7280"),
            "counts": counts,
            "shares": {p: round(shares[p], 4) for p in DRAFT_POSITION_ORDER},
            "total": total,
            "keeper_rate": round(keeper_rate, 4),
            "championships": championships,
            "playoff_rate": round(playoff_apps / max(seasons_played, 1), 4),
            "archetype": label,
            "archetype_color": color,
            "archetype_blurb": blurb,
            "top_position": top_position,
            "top_position_pct": int(counts.get(top_position, 0) / total * 100),
            "best_round_one_find": best_find.get(manager, "—"),
            "seasons_sampled": total,
        })
    dna.sort(key=lambda d: (-d["total"], d["manager"]))

    # ── Round one history ────────────────────────────────────────────────────
    r1_counts = sorted(
        (
            {"player_name": p, "position": pos, "count": int(n)}
            for (p, pos), n in r1_named[
                r1_named["position"].isin(DRAFT_SKILL_POSITIONS)
            ].groupby(["player_name", "position"]).size().items()
        ),
        key=lambda r: (-r["count"], r["player_name"]),
    )
    # The first live pick of each draft — again not always overall pick 1, since
    # keepers occupy the earliest slots in several eras.
    opening_picks = drafted.loc[drafted.groupby("season")["overall_pick"].idxmin()]
    first_overall = sorted(
        (
            {"player_name": p, "count": int(n)}
            for p, n in opening_picks.groupby("player_name").size().items()
        ),
        key=lambda r: (-r["count"], r["player_name"]),
    )

    return {
        "legends": legends,
        "manager_dna": dna,
        "round_one": {"most_taken": r1_counts, "first_overall": first_overall},
        "totals": {
            "picks": len(picks),
            "real_drafts": len(drafted),
            "keepers": len(kept),
            "unique_players": int(picks["player_name"].nunique()),
        },
    }


@st.cache_data
def get_draft_loyalty_board(position_filter: str = "All Players", limit: int = 25) -> list[dict]:
    """Most-owned players for one of the page's position filters.

    Kept separate from the main view because it is a user control: the page
    picks a filter, and the static site will do the same client-side.
    """
    ownership = get_player_ownership()

    if position_filter == "All Players":
        subset = ownership[ownership["position"] != "DEF"]
    elif position_filter == "Keepers Only":
        subset = ownership[(ownership["keeper_count"] > 0) & (ownership["position"] != "DEF")]
    else:
        subset = ownership[ownership["position"] == position_filter]

    grouped = (
        subset.groupby("player_name")
        .agg(total=("total_seasons", "sum"), position=("position", "first"),
             first=("first_season", "min"), last=("last_season", "max"))
        .reset_index()
    )
    rows = sorted(
        (
            {
                "player_name": r["player_name"],
                "position": str(r["position"]) if r["position"] else "?",
                "total_seasons": int(r["total"]),
                "first_season": int(r["first"]),
                "last_season": int(r["last"]),
            }
            for _, r in grouped.iterrows()
        ),
        key=lambda r: (-r["total_seasons"], r["player_name"]),
    )
    return rows[:limit]


# ── FRANCHISE PROFILES ────────────────────────────────────────────────────────
# Lifted out of pages/franchise_profiles.py, which computed ~175 lines of
# per-franchise history inline. The rivalry table was ranked by games with the
# default non-stable sort; it now breaks ties explicitly.

@st.cache_data
def get_franchise_profile(franchise_id: str) -> dict:
    from utils import narratives

    data = load_all()
    history = data["franchise_history"]
    tnh = data["team_name_history"]
    weekly = data["weekly_matchups"]
    playoff_games = data["playoff_games"]
    champions = get_champions()

    stats_row = get_franchise_stats().set_index("franchise_id").loc[franchise_id]
    periods = get_franchise_steward_periods()
    periods = periods[periods["franchise_id"] == franchise_id].sort_values("start_season")

    mine = history[history["franchise_id"] == franchise_id].sort_values("season")
    all_seasons = sorted(int(s) for s in mine["season"].unique())
    established = int(stats_row["established"])
    first_manager = periods.iloc[0]["manager_name"]
    current_manager = (
        str(stats_row["current_manager"]) if pd.notna(stats_row.get("current_manager"))
        else periods.iloc[-1]["manager_name"]
    )
    opponent_manager = tnh.set_index(["season", "team_name"])["canonical_name"].to_dict()

    # ── The franchise's team in each season ──────────────────────────────────
    team_seasons = []
    for _, row in mine.iterrows():
        season, manager = int(row["season"]), row["manager_name"]
        named = tnh[(tnh["canonical_name"] == manager) & (tnh["season"] == season)]
        if len(named):
            team_seasons.append({
                "season": season, "manager": manager, "team_name": named.iloc[0]["team_name"],
            })
    team_by_season = {t["season"]: t for t in team_seasons}
    owns = {(t["season"], t["team_name"]) for t in team_seasons}

    regular = weekly[
        ~weekly["is_bye"].astype(bool) & ~weekly["is_playoff"].astype(bool)
    ].copy()
    regular = regular[[(int(s), t) in owns for s, t in zip(regular["season"], regular["team_name"])]]

    # ── Postseason ───────────────────────────────────────────────────────────
    bracket = playoff_games[playoff_games["bracket"] == "championship"]
    appearances, finals, third_places, playoff_games_played = set(), set(), set(), []
    for _, g in bracket.iterrows():
        season = int(g["season"])
        team = team_by_season.get(season, {}).get("team_name")
        if team is None:
            continue
        for side, other in (("team_1", "team_2"), ("team_2", "team_1")):
            if g[side] != team:
                continue
            appearances.add(season)
            if g["game_type"] == "final":
                finals.add(season)
            if g["game_type"] == "3rd_place" and g["winner"] == team:
                third_places.add(season)
            playoff_games_played.append({
                "opponent": opponent_manager.get((season, g[other]), g[other]),
                "won": g["winner"] == team,
            })

    champion_seasons = sorted(
        int(r["season"]) for _, r in champions.iterrows()
        if team_by_season.get(int(r["season"]), {}).get("team_name") == r["champion_team"]
    )
    runner_up_seasons = sorted(
        int(r["season"]) for _, r in champions.iterrows()
        if team_by_season.get(int(r["season"]), {}).get("team_name") == r["runner_up_team"]
    )

    longest_streak = streak = 0
    for season in all_seasons:
        streak = streak + 1 if season in appearances else 0
        longest_streak = max(longest_streak, streak)

    # ── Per-season records ───────────────────────────────────────────────────
    season_records = []
    for season in all_seasons:
        games = regular[regular["season"] == season]
        if not len(games):
            continue
        season_records.append({
            "season": season,
            "manager": team_by_season.get(season, {}).get("manager"),
            "team_name": team_by_season.get(season, {}).get("team_name"),
            "wins": int((games["result"] == "Win").sum()),
            "losses": int((games["result"] == "Loss").sum()),
            "points_for": round(float(games["team_score"].sum()), 2),
        })

    def _peak(key):
        if not season_records:
            return None
        return max(season_records, key=lambda r: (r[key], -r["season"]))

    best_week = None
    if len(regular):
        row = regular.loc[regular["team_score"].idxmax()]
        best_week = {
            "season": int(row["season"]), "week": int(row["week"]),
            "points": round(float(row["team_score"]), 2),
            "manager": team_by_season.get(int(row["season"]), {}).get("manager"),
        }

    # ── Stewards ─────────────────────────────────────────────────────────────
    titles_by_manager: dict[str, list[int]] = {}
    for season in champion_seasons:
        titles_by_manager.setdefault(team_by_season[season]["manager"], []).append(season)

    stewards = []
    for _, p in periods.iterrows():
        manager = p["manager_name"]
        their_seasons = {int(s) for s in mine[mine["manager_name"] == manager]["season"]}
        their_games = regular[regular["season"].isin(their_seasons)]
        stewards.append({
            "manager": manager,
            "emoji": MANAGER_EMOJI.get(manager, "👤"),
            "color": MANAGER_COLORS.get(manager, "#6B7280"),
            "start_season": int(p["start_season"]),
            "end_season": int(p["end_season"]),
            "seasons": int(p["years"]),
            "wins": int((their_games["result"] == "Win").sum()),
            "losses": int((their_games["result"] == "Loss").sum()),
            "playoff_apps": len(appearances & their_seasons),
            "championships": len(titles_by_manager.get(manager, [])),
            "championship_years": sorted(titles_by_manager.get(manager, [])),
        })

    best_steward = max(
        stewards,
        key=lambda s: (s["championships"], s["playoff_apps"], s["wins"], s["manager"]),
    )["manager"] if stewards else None

    # ── Rivalries ────────────────────────────────────────────────────────────
    rivals: dict[str, dict] = {}
    for _, g in regular.iterrows():
        opponent = opponent_manager.get((int(g["season"]), g["opponent"]), g["opponent"])
        entry = rivals.setdefault(opponent, {
            "opponent": opponent, "emoji": MANAGER_EMOJI.get(opponent, "👤"),
            "games": 0, "wins": 0, "losses": 0, "playoff_games": 0, "playoff_wins": 0,
        })
        entry["games"] += 1
        entry["wins" if g["result"] == "Win" else "losses"] += 1
    for game in playoff_games_played:
        entry = rivals.setdefault(game["opponent"], {
            "opponent": game["opponent"], "emoji": MANAGER_EMOJI.get(game["opponent"], "👤"),
            "games": 0, "wins": 0, "losses": 0, "playoff_games": 0, "playoff_wins": 0,
        })
        entry["playoff_games"] += 1
        entry["playoff_wins"] += int(game["won"])
    top_rivals = sorted(rivals.values(), key=lambda r: (-r["games"], r["opponent"]))[:6]

    return {
        "franchise_id": franchise_id,
        "established": established,
        "first_manager": first_manager,
        "current_manager": current_manager,
        "seasons": all_seasons,
        "totals": {
            "seasons": len(all_seasons),
            "championships": len(champion_seasons),
            "runner_ups": len(runner_up_seasons),
            "playoff_apps": len(appearances),
            "finals_apps": len(finals),
            "third_places": len(third_places),
            "longest_playoff_streak": longest_streak,
            "winning_seasons": sum(1 for r in season_records if r["wins"] > r["losses"]),
        },
        "championship_seasons": champion_seasons,
        "runner_up_seasons": runner_up_seasons,
        "playoff_seasons": sorted(appearances),
        "third_place_seasons": sorted(third_places),
        "stewards": stewards,
        "best_steward": best_steward,
        "season_records": season_records,
        "peaks": {
            "best_record": _peak("wins"),
            "most_points": _peak("points_for"),
            "best_week": best_week,
        },
        "rivals": top_rivals,
        "legends": get_franchise_legends(franchise_id),
        "story": narratives.franchise_story(
            established=established,
            first_manager=first_manager,
            current_manager=current_manager,
            stewards=stewards,
            championship_seasons=champion_seasons,
            total_seasons=len(all_seasons),
            total_championships=len(champion_seasons),
        ),
    }


# ── KEEPER HALL ───────────────────────────────────────────────────────────────
# Lifted out of pages/keeper_hall.py. Five more rankings gained explicit
# tie-breaks: the immortal chains, championship keepers, per-manager DNA order,
# favourite keeper, and the most-kept player board.

KEEPER_DNA_BLURBS = {
    "BELL COW HUNTER": "Staked the franchise on elite RBs. Kept the workhorse, season after season.",
    "RECEIVER KINGDOM": "Built through the pass-catchers. Wide receivers were the currency.",
    "SIGNAL CALLER": "Bet on quarterbacks at a position most managers left to the draft.",
    "TIGHT END LOYALIST": "Found the value others ignored. Elite TEs don't hit free agency.",
    "SKILL POSITION SNIPER": "No positional bias. Any skill player, any round, any season.",
    "BALANCED CURATOR": "A methodical approach. Position was secondary to player quality.",
}

_KEEPER_POSITIONS = ["RB", "WR", "QB", "TE", "DEF", "K"]


def _keeper_dna_label(position_counts: dict) -> str:
    total = sum(position_counts.values())
    if total == 0:
        return "BALANCED CURATOR"
    rb = position_counts.get("RB", 0) / total
    wr = position_counts.get("WR", 0) / total
    qb = position_counts.get("QB", 0) / total
    te = position_counts.get("TE", 0) / total
    if rb >= 0.55:
        return "BELL COW HUNTER"
    if wr >= 0.50:
        return "RECEIVER KINGDOM"
    if qb >= 0.25:
        return "SIGNAL CALLER"
    if te >= 0.20:
        return "TIGHT END LOYALIST"
    if rb + wr >= 0.80:
        return "SKILL POSITION SNIPER"
    return "BALANCED CURATOR"


@st.cache_data
def get_keeper_hall_view() -> dict:
    picks = get_draft_picks_with_pos()
    chains = get_keeper_chains()
    enriched = get_keeper_enriched()
    keepers = picks[picks["is_keeper"]]

    positions_by_player = (
        enriched.dropna(subset=["position"]).groupby("player_name")["position"].first().to_dict()
    )

    # ── Immortal chains: streak x2 + titles x5 + playoffs x0.5 ───────────────
    immortals = []
    for _, chain in chains.iterrows():
        player = chain["player_name"]
        run = enriched[
            (enriched["player_name"] == player) & (enriched["season"].isin(chain["seasons"]))
        ]
        titles = int(run["won_title"].sum())
        playoffs = int(run["made_playoffs"].sum())
        immortals.append({
            "player_name": player,
            "position": str(positions_by_player.get(player, "?")),
            "primary_manager": chain["primary_manager"],
            "all_managers": list(chain["all_managers"]),
            "franchise_id": chain["franchise_id"],
            "seasons": [int(s) for s in chain["seasons"]],
            "streak_len": int(chain["streak_len"]),
            "titles": titles,
            "playoffs": playoffs,
            "score": round(int(chain["streak_len"]) * 2 + titles * 5 + playoffs * 0.5, 2),
            "multi_manager": bool(chain["multi_manager"]),
        })
    immortals.sort(key=lambda c: (-c["streak_len"], -c["score"], c["player_name"]))

    # ── Keeper volume by season ──────────────────────────────────────────────
    by_season = [
        {"season": int(s), "count": int(n)}
        for s, n in keepers.groupby("season").size().items()
    ]

    # ── Players kept on championship rosters ─────────────────────────────────
    title_keepers = enriched[enriched["won_title"]]
    champions_kept = sorted(
        (
            {
                "player_name": player,
                "position": str(positions_by_player.get(player, "?")),
                "title_count": len(group),
                "seasons": sorted(int(s) for s in group["season"]),
                "managers": sorted(set(group["manager"])),
            }
            for player, group in title_keepers.groupby("player_name")
        ),
        key=lambda p: (-p["title_count"], p["player_name"]),
    )

    # ── Per-manager keeper DNA ───────────────────────────────────────────────
    dna = []
    for manager, group in keepers.groupby("manager"):
        total_picks = len(picks[picks["manager"] == manager])
        if not len(group):
            continue
        named = group[group["position"] != "DEF"]
        favourite, favourite_count = "—", 0
        if len(named):
            tally = sorted(named["player_name"].value_counts().items(), key=lambda kv: (-kv[1], kv[0]))
            favourite, favourite_count = tally[0][0], int(tally[0][1])

        theirs = chains[chains["all_managers"].apply(lambda m: manager in m)]
        longest, longest_player = 1, "—"
        if len(theirs):
            ranked = sorted(
                ((int(r["streak_len"]), r["player_name"]) for _, r in theirs.iterrows()),
                key=lambda kv: (-kv[0], kv[1]),
            )
            longest, longest_player = ranked[0]

        counts = {
            p: int(n) for p, n in
            group[group["position"].isin(_KEEPER_POSITIONS)]["position"].value_counts().items()
        }
        label = _keeper_dna_label(counts)
        dna.append({
            "manager": manager,
            "emoji": MANAGER_EMOJI.get(manager, "👤"),
            "color": MANAGER_COLORS.get(manager, "#6B7280"),
            "keeper_count": len(group),
            "keeper_rate": round(len(group) / total_picks, 4) if total_picks else 0.0,
            "favourite": {"player": favourite, "count": favourite_count},
            "longest_streak": longest,
            "longest_streak_player": longest_player,
            "titles": int(enriched[enriched["manager"] == manager]["won_title"].sum()),
            "dna": label,
            "dna_blurb": KEEPER_DNA_BLURBS[label],
            "position_counts": counts,
            "last_season": int(picks[picks["manager"] == manager]["season"].max()),
        })
    dna.sort(key=lambda d: (-d["keeper_count"], d["manager"]))

    # ── Most-kept players ────────────────────────────────────────────────────
    most_kept = sorted(
        (
            {"player_name": p, "position": str(positions_by_player.get(p, "?")), "count": int(n)}
            for p, n in keepers[keepers["position"] != "DEF"].groupby("player_name").size().items()
        ),
        key=lambda p: (-p["count"], p["player_name"]),
    )

    # Hand-written lore, attached to the players it is about. This is the most
    # human content in the project and belongs on the page, not in a dict.
    from utils import narratives
    keep_counts = {p: int(n) for p, n in keepers.groupby("player_name").size().items()}
    lore = sorted(
        (
            {
                "player_name": player,
                "position": str(positions_by_player.get(player, "?")),
                "times_kept": keep_counts.get(player, 0),
                "lore": text,
            }
            for player, text in narratives.KEEPER_LORE.items()
        ),
        key=lambda entry: (-entry["times_kept"], entry["player_name"]),
    )

    return {
        "lore": lore,
        "immortals": immortals,
        "notable_chains": [c for c in immortals if c["streak_len"] >= 3],
        "by_season": by_season,
        "champions_kept": champions_kept,
        "manager_dna": dna,
        "active_dna": [d for d in dna if d["last_season"] >= CURRENT_SEASON],
        "alumni_dna": [d for d in dna if d["last_season"] < CURRENT_SEASON],
        "most_kept": most_kept,
        "keeper_seasons": sorted({int(s) for s in keepers["season"]}),
        "totals": {
            "keepers": len(keepers),
            "unique_players": int(keepers["player_name"].nunique()),
            "chains": len(chains),
            "managers": len(dna),
        },
    }


# ── RIVALRIES ─────────────────────────────────────────────────────────────────
# Lifted out of pages/rivalries.py — the page this whole effort started with,
# where the first test run caught get_all_rivalries() reordering itself between
# restarts. The page also rebuilt the regular-season head-to-head dedup that
# get_all_rivalries() already does internally; that logic now lives in one place.

def rivalry_from_perspective(row: dict, manager: str) -> dict:
    """Flip a rivalry row so it reads from one manager's point of view."""
    is_a = row["mgr_a"] == manager
    return {
        "manager": manager,
        "opponent": row["mgr_b"] if is_a else row["mgr_a"],
        "wins": int(row["rs_a_wins"] if is_a else row["rs_b_wins"]),
        "losses": int(row["rs_b_wins"] if is_a else row["rs_a_wins"]),
        "win_pct": round(float(row["rs_a_pct"]) if is_a else 1.0 - float(row["rs_a_pct"]), 4),
        "pl_wins": int(row["pl_a_wins"] if is_a else row["pl_b_wins"]),
        "pl_losses": int(row["pl_b_wins"] if is_a else row["pl_a_wins"]),
        "final_wins": int(row["final_a_wins"] if is_a else row["final_b_wins"]),
        "final_losses": int(row["final_b_wins"] if is_a else row["final_a_wins"]),
        "biggest_win": round(float(row["a_biggest_win"] if is_a else row["b_biggest_win"]), 2),
        "biggest_loss": round(float(row["b_biggest_win"] if is_a else row["a_biggest_win"]), 2),
        "rs_games": int(row["rs_games"]),
        "pl_games": int(row["pl_games"]),
        "close_games": int(row["close_games"]),
        "rivalry_score": int(row["rivalry_score"]),
    }


@st.cache_data
def get_head_to_head_losses() -> list[dict]:
    """Regular-season losses by (loser, winner) across league history.

    One row per game — the two-perspective source data is deduplicated on
    (season, week, pair), the same way get_all_rivalries() does it.
    """
    data = load_all()
    weekly = data["weekly_matchups"]
    manager_of = data["team_name_history"].set_index(["season", "team_name"])["canonical_name"].to_dict()

    games = weekly[~weekly["is_bye"].astype(bool) & ~weekly["is_playoff"].astype(bool)].copy()
    games["mgr"] = [manager_of.get((int(s), t)) for s, t in zip(games["season"], games["team_name"])]
    games["opp_mgr"] = [manager_of.get((int(s), t)) for s, t in zip(games["season"], games["opponent"])]
    games = games.dropna(subset=["mgr", "opp_mgr"])
    games["pair"] = [tuple(sorted([a, b])) for a, b in zip(games["mgr"], games["opp_mgr"])]
    games = games.drop_duplicates(subset=["season", "week", "pair"])

    tally: dict[tuple[str, str], int] = {}
    for _, g in games.iterrows():
        winner = g["mgr"] if g["result"] == "Win" else g["opp_mgr"]
        loser = g["opp_mgr"] if g["result"] == "Win" else g["mgr"]
        tally[(loser, winner)] = tally.get((loser, winner), 0) + 1

    return sorted(
        ({"loser": l, "winner": w, "losses": n} for (l, w), n in tally.items()),
        key=lambda r: (-r["losses"], r["loser"], r["winner"]),
    )


@st.cache_data
def get_rivalries_view() -> dict:
    data = load_all()
    playoff_games = data["playoff_games"]
    manager_of = data["team_name_history"].set_index(["season", "team_name"])["canonical_name"].to_dict()

    rivalries = get_all_rivalries()
    eliminations = get_playoff_eliminations()

    # ── Championship finals ──────────────────────────────────────────────────
    bracket = playoff_games[
        (playoff_games["bracket"] == "championship") & (playoff_games["game_type"] == "final")
    ]
    finals = []
    for _, g in bracket.iterrows():
        season = int(g["season"])
        winner_team = g["winner"]
        loser_team = g["team_2"] if winner_team == g["team_1"] else g["team_1"]
        win_score = float(g["score_1"] if winner_team == g["team_1"] else g["score_2"])
        loss_score = float(g["score_2"] if winner_team == g["team_1"] else g["score_1"])
        finals.append({
            "season": season,
            "winner_manager": manager_of.get((season, winner_team)),
            "winner_team": winner_team,
            "winner_score": round(win_score, 2),
            "loser_manager": manager_of.get((season, loser_team)),
            "loser_team": loser_team,
            "loser_score": round(loss_score, 2),
            "margin": round(abs(float(g["score_1"]) - float(g["score_2"])), 2),
        })
    finals.sort(key=lambda f: -f["season"])

    # ── Title-game records ───────────────────────────────────────────────────
    title_records: dict[str, dict] = {}
    for final in finals:
        for manager, key in ((final["winner_manager"], "wins"), (final["loser_manager"], "losses")):
            entry = title_records.setdefault(manager, {
                "manager": manager, "emoji": MANAGER_EMOJI.get(manager, "👤"),
                "wins": 0, "losses": 0,
            })
            entry[key] += 1
    for entry in title_records.values():
        entry["apps"] = entry["wins"] + entry["losses"]
    ranked_titles = sorted(
        title_records.values(), key=lambda r: (-r["wins"], -r["apps"], r["manager"])
    )

    # ── Playoff eliminations ─────────────────────────────────────────────────
    elim_rows = [
        {"winner": r["winner_mgr"], "loser": r["loser_mgr"], "eliminations": int(r["eliminations"])}
        for _, r in eliminations.iterrows()
    ]
    by_executioner: dict[str, int] = {}
    by_victim: dict[str, int] = {}
    for r in elim_rows:
        by_executioner[r["winner"]] = by_executioner.get(r["winner"], 0) + r["eliminations"]
        by_victim[r["loser"]] = by_victim.get(r["loser"], 0) + r["eliminations"]

    def _rank(counts: dict, label: str) -> list[dict]:
        return sorted(
            ({label: m, "total": n, "emoji": MANAGER_EMOJI.get(m, "👤")} for m, n in counts.items()),
            key=lambda r: (-r["total"], r[label]),
        )

    top_pairs = sorted(elim_rows, key=lambda r: (-r["eliminations"], r["winner"], r["loser"]))

    # ── Hall of pain ─────────────────────────────────────────────────────────
    losses = get_head_to_head_losses()
    finals_losses: dict[str, int] = {}
    for final in finals:
        finals_losses[final["loser_manager"]] = finals_losses.get(final["loser_manager"], 0) + 1

    return {
        "managers": sorted(set(rivalries["mgr_a"]) | set(rivalries["mgr_b"])),
        "finals": finals,
        "title_records": ranked_titles,
        "eliminations": {
            "pairs": top_pairs,
            "by_executioner": _rank(by_executioner, "manager"),
            "by_victim": _rank(by_victim, "manager"),
        },
        "hall_of_pain": {
            "worst_matchups": [r for r in losses if r["losses"] >= 10],
            "finals_losses": sorted(
                ({"manager": m, "losses": n, "emoji": MANAGER_EMOJI.get(m, "👤")}
                 for m, n in finals_losses.items()),
                key=lambda r: (-r["losses"], r["manager"]),
            ),
            "closest_final": min(finals, key=lambda f: (f["margin"], -f["season"])) if finals else None,
        },
        "totals": {
            "pairs": len(rivalries),
            "managers": int(len(set(rivalries["mgr_a"]) | set(rivalries["mgr_b"]))),
            "finals": len(finals),
            "playoff_eliminations": sum(r["eliminations"] for r in elim_rows),
        },
    }
