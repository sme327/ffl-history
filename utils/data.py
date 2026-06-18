"""Central data loading and derived metrics for The Long Game."""
import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

LEAGUE_NAME = "The Long Game"
LEAGUE_SUBTITLE = "A Quarter Century of {insert witty name here} Glory"
FOUNDED = 2001
CURRENT_SEASON = 2025

MANAGER_COLORS: dict[str, str] = {
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
        return "🏆 Champion"
    if len(games[(games["game_type"] == "final") & (games["winner"] != team)]):
        return "🥈 Runner-Up"
    if len(games[(games["game_type"] == "3rd_place") & (games["winner"] == team)]):
        return "🥉 3rd Place"
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
_KEEPER_SUSPENSION_YEARS: set[int] = {2005, 2011}


@st.cache_data
def get_draft_picks_with_pos() -> pd.DataFrame:
    """Draft picks joined with position, manager name, and franchise_id.
    Excludes --empty-- placeholder rows and normalises rare non-fantasy positions."""
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
