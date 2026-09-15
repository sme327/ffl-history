"""The Recap's awards engine — pure functions, no I/O, no league knowledge.

One identical copy lives in each museum that publishes a weekly Recap
(Dynasty 22: scripts/recap_engine.py; {insert witty name here}:
scripts/recap_engine.py). Fix a bug in one, copy the file to the other —
the two leagues must never compute "Best Managed" two different ways.

Input is one week, already normalized by the league's own builder:

    teams = [{
        "key": "M01",                 # stable id the builder understands
        "players": [{
            "name": "Josh Allen",
            "positions": ["QB"],      # every position he's eligible at
            "slot": "QB",             # the slot he sat in: a starter slot label,
                                      # "BN" for bench, or an inactive slot
            "points": 39.66,
            "projected": 21.49,       # pregame projection, None when unknown
        }, ...],
    }, ...]
    games = [("M01", "M05"), ...]
    config = {
        "slots": [("QB", ["QB"]), ("RB", ["RB"]), ..., ("FLEX", ["RB", "WR", "TE"])],
        "inactive": ["IR", "TAXI"],   # never startable, never "bench"
        "award_positions": ["QB", "RB", "WR", "TE"],
        "bench_positions": ["QB", "RB", "WR", "TE"],
    }

Every award is a computed fact. Nothing here writes prose; the builder's
brief and the hand-approved copy file do that.
"""

from __future__ import annotations

EMPTY = {"name": None, "positions": [], "points": 0.0, "projected": 0.0}


def r2(x: float | None) -> float | None:
    return None if x is None else round(x + 0.0, 2)


def _hungarian(cost: list[list[float]]) -> list[int]:
    """Min-cost assignment of n rows to distinct columns (n <= m)."""
    n, m = len(cost), len(cost[0])
    inf = float("inf")
    u, v = [0.0] * (n + 1), [0.0] * (m + 1)
    p, way = [0] * (m + 1), [0] * (m + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [inf] * (m + 1), [False] * (m + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], inf, 0
            for j in range(1, m + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    out = [0] * n
    for j in range(1, m + 1):
        if p[j]:
            out[p[j] - 1] = j - 1
    return out


def optimal_lineup(players: list[dict], config: dict) -> tuple[float, list[dict]]:
    """The best legal lineup in hindsight from every active player (starters
    plus bench; inactive slots excluded). Exact, including multi-position
    eligibility. A slot may be left empty (0) rather than start a negative."""
    inactive = set(config["inactive"])
    pool = [p for p in players if p["slot"] not in inactive and p.get("name")]
    slots = config["slots"]
    cols = pool + [EMPTY] * len(slots)
    big = 1e6
    cost = [
        [
            -(c["points"] or 0.0) if (c is EMPTY or set(c["positions"]) & set(elig)) else big
            for c in cols
        ]
        for _, elig in slots
    ]
    pick = _hungarian(cost)
    lineup = [{"slot": slots[i][0], "player": cols[j] if cols[j] is not EMPTY else None} for i, j in enumerate(pick)]
    total = sum((x["player"]["points"] or 0.0) for x in lineup if x["player"])
    return r2(total), lineup


def best_single_swap(players: list[dict], config: dict) -> dict | None:
    """The one bench-for-starter move (same slot, player eligible for it) that
    would have gained the most points. None if no swap gains anything."""
    elig = dict(config["slots"])
    starter_slots = set(elig)
    starters = [p for p in players if p["slot"] in starter_slots]
    bench = [p for p in players if p["slot"] == "BN" and p.get("name")]
    best = None
    for b in bench:
        for s in starters:
            if not set(b["positions"]) & set(elig[s["slot"]]):
                continue
            gain = (b["points"] or 0.0) - ((s["points"] or 0.0) if s.get("name") else 0.0)
            if gain > 0 and (best is None or gain > best["gain"]):
                best = {"bench": b["name"], "bench_points": r2(b["points"]),
                        "starter": s.get("name"), "starter_points": r2(s["points"] if s.get("name") else 0.0),
                        "slot": s["slot"], "gain": r2(gain)}
    return best


def _top(rows: list[dict], key, reverse=True) -> list[dict]:
    """Every row tied for the top value — awards are shared, never coin-flipped."""
    if not rows:
        return []
    ordered = sorted(rows, key=key, reverse=reverse)
    best = key(ordered[0])
    return [r for r in ordered if key(r) == best]


def week_awards(teams: list[dict], games: list[tuple[str, str]], config: dict) -> dict:
    starter_slots = {s for s, _ in config["slots"]}
    by_key = {}
    for t in teams:
        starters = [p for p in t["players"] if p["slot"] in starter_slots]
        actual = r2(sum((p["points"] or 0.0) for p in starters if p.get("name")))
        projs = [p["projected"] for p in starters if p.get("name")]
        projected = r2(sum(x or 0.0 for x in projs)) if any(x is not None for x in projs) else None
        optimal, lineup = optimal_lineup(t["players"], config)
        optimal = max(optimal, actual)  # a legal lineup can't beat the optimum
        by_key[t["key"]] = {
            "key": t["key"],
            "actual": actual,
            "projected": projected,
            "vs_projection": r2(actual - projected) if projected is not None else None,
            "optimal": optimal,
            "optimal_lineup": [{"slot": x["slot"], "name": x["player"]["name"] if x["player"] else None,
                                "points": r2(x["player"]["points"]) if x["player"] else 0.0} for x in lineup],
            "efficiency": r2(100.0 * actual / optimal) if optimal else None,
            "left_on_bench": r2(optimal - actual),
            "best_swap": best_single_swap(t["players"], config),
        }

    # All-play: this week's score against every other team's
    for k, row in by_key.items():
        others = [o["actual"] for kk, o in by_key.items() if kk != k]
        row["all_play"] = {
            "wins": sum(row["actual"] > x for x in others),
            "losses": sum(row["actual"] < x for x in others),
            "ties": sum(row["actual"] == x for x in others),
        }
    ranked = sorted(by_key.values(), key=lambda r: -r["actual"])
    for i, row in enumerate(ranked):
        row["score_rank"] = 1 + sum(o["actual"] > row["actual"] for o in ranked)

    results = []
    for a, b in games:
        ta, tb = by_key[a], by_key[b]
        winner = a if ta["actual"] > tb["actual"] else b if tb["actual"] > ta["actual"] else None
        loser = None if winner is None else (b if winner == a else a)
        margin = r2(abs(ta["actual"] - tb["actual"]))
        game = {"a": a, "b": b, "score_a": ta["actual"], "score_b": tb["actual"],
                "winner": winner, "loser": loser, "margin": margin,
                "coulda_won": None, "swap_flip": None}
        for side, opp in ((a, b), (b, a)):
            by_key[side]["opponent"] = opp
            by_key[side]["result"] = "tie" if winner is None else ("win" if side == winner else "loss")
            by_key[side]["margin"] = margin if side == winner else -margin
        if loser:
            tl, tw = by_key[loser], by_key[winner]
            if tl["optimal"] > tw["actual"]:
                game["coulda_won"] = {"team": loser, "optimal": tl["optimal"], "needed": tw["actual"]}
            swap = tl["best_swap"]
            if swap and swap["gain"] > margin:
                game["swap_flip"] = {"team": loser, **swap}
        results.append(game)

    decided = [g for g in results if g["winner"]]
    active = list(by_key.values())

    def team_award(rows, value_key):
        return [{"team": r["key"], "value": r[value_key]} for r in rows]

    awards = {
        "highest_score": team_award(_top(active, lambda r: r["actual"]), "actual"),
        "lowest_score": team_award(_top(active, lambda r: r["actual"], reverse=False), "actual"),
        "biggest_blowout": [{"winner": g["winner"], "loser": g["loser"], "value": g["margin"]}
                            for g in _top(decided, lambda g: g["margin"])],
        "narrowest_win": [{"winner": g["winner"], "loser": g["loser"], "value": g["margin"]}
                          for g in _top(decided, lambda g: g["margin"], reverse=False)],
        "best_managed": team_award(_top([r for r in active if r["efficiency"] is not None],
                                        lambda r: (r["efficiency"], r["actual"])), "efficiency"),
        "worst_managed": team_award(_top([r for r in active if r["efficiency"] is not None],
                                         lambda r: (r["efficiency"], r["actual"]), reverse=False), "efficiency"),
        "most_left_on_bench": team_award(_top(active, lambda r: r["left_on_bench"]), "left_on_bench"),
        "overachiever": team_award(_top([r for r in active if r["vs_projection"] is not None],
                                        lambda r: r["vs_projection"]), "vs_projection"),
        "below_expectation": team_award(_top([r for r in active if r["vs_projection"] is not None],
                                             lambda r: r["vs_projection"], reverse=False), "vs_projection"),
    }
    # Luck: the loser who'd have beaten the most of the league, and the
    # winner who'd have beaten the fewest.
    losers = [by_key[g["loser"]] for g in decided]
    winners = [by_key[g["winner"]] for g in decided]
    awards["unluckiest_loss"] = team_award(_top(losers, lambda r: r["all_play"]["wins"]), "actual") if losers else []
    awards["luckiest_win"] = team_award(_top(winners, lambda r: r["all_play"]["wins"], reverse=False), "actual") if winners else []

    # Players of the week (starters) and best benchwarmers, by primary position
    def primary(p):
        return p["positions"][0] if p["positions"] else None

    def player_row(t, p):
        return {"team": t["key"], "name": p["name"], "position": primary(p), "points": r2(p["points"]),
                "projected": r2(p["projected"])}

    started = [(t, p) for t in teams for p in t["players"] if p["slot"] in starter_slots and p.get("name")]
    benched = [(t, p) for t in teams for p in t["players"] if p["slot"] == "BN" and p.get("name")]
    players_of_week = {}
    for pos in config["award_positions"]:
        rows = [player_row(t, p) for t, p in started if primary(p) == pos]
        players_of_week[pos] = _top(rows, lambda r: r["points"] or 0.0)
    bench_best = {}
    for pos in config["bench_positions"]:
        rows = [player_row(t, p) for t, p in benched if primary(p) == pos]
        bench_best[pos] = _top(rows, lambda r: r["points"] or 0.0)
    duds = [player_row(t, p) for t, p in started if p["projected"] is not None]
    for d in duds:
        d["shortfall"] = r2((d["projected"] or 0.0) - (d["points"] or 0.0))
    dud = _top(duds, lambda r: r["shortfall"]) if duds else []

    return {
        "teams": by_key,
        "games": results,
        "awards": awards,
        "players_of_week": players_of_week,
        "bench_best": bench_best,
        "dud": dud,
        "coulda_won": [g["coulda_won"] | {"opponent": g["winner"], "margin": g["margin"]} for g in results if g["coulda_won"]],
        "swap_flips": [g["swap_flip"] | {"opponent": g["winner"], "margin": g["margin"]} for g in results if g["swap_flip"]],
    }


def series_update(prior: list[dict], a: str, b: str, winner: str | None) -> dict:
    """What this week's result did to a lifetime series.

    prior: chronological games between a and b that count toward the series,
    each {"season", "week", "winner"} (winner a key or None for a tie)."""
    def tally(games):
        return {a: sum(g["winner"] == a for g in games), b: sum(g["winner"] == b for g in games),
                "ties": sum(g["winner"] is None for g in games)}

    def streak(games):
        holder, n = None, 0
        for g in reversed(games):
            if g["winner"] is None:
                break
            if holder is None:
                holder, n = g["winner"], 1
            elif g["winner"] == holder:
                n += 1
            else:
                break
        return {"team": holder, "length": n} if holder else None

    before = tally(prior)
    after_games = prior + [{"season": None, "week": None, "winner": winner}]
    after = tally(after_games)
    s_before, s_after = streak(prior), streak(after_games)

    def leader(t):
        return a if t[a] > t[b] else b if t[b] > t[a] else None

    notes = []
    if not prior:
        notes.append({"kind": "first_meeting"})
    if winner:
        loser = b if winner == a else a
        if s_before and s_before["team"] == loser and s_before["length"] >= 2:
            notes.append({"kind": "snapped", "team": winner, "length": s_before["length"]})
        if s_after and s_after["team"] == winner and s_after["length"] >= 2:
            notes.append({"kind": "streak", "team": winner, "length": s_after["length"]})
        lb, la = leader(before), leader(after)
        if lb != la:
            notes.append({"kind": "took_lead" if la == winner else "evened", "team": winner})
        last_win = next((g for g in reversed(prior) if g["winner"] == winner), None)
        if prior and last_win is None:
            notes.append({"kind": "first_win", "team": winner, "games": len(prior)})
        elif last_win and last_win["season"] is not None:
            gap = sum(1 for g in prior if (g["season"], g["week"]) > (last_win["season"], last_win["week"]))
            if gap >= 3:
                notes.append({"kind": "first_win_since", "team": winner, "season": last_win["season"],
                              "week": last_win["week"], "games_between": gap})
    return {"before": before, "after": after, "games_after": len(after_games),
            "streak_after": s_after, "notes": notes}
