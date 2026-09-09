#!/usr/bin/env python3
"""Build a fair Chris-vs-Tete scoreboard across different Sleeper leagues."""

import json
import math
import os
import statistics
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://api.sleeper.app/v1"
ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
SCOREBOARD_PATH = ROOT / "scoreboard.json"
README_PATH = ROOT / "README.md"


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Sleeper-ChatGPT-Cross-League-Battle/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def percentile(score, scores):
    """Midrank percentile: ties share the midpoint of their tied positions."""
    if not scores:
        return None
    lower = sum(1 for x in scores if x < score)
    equal = sum(1 for x in scores if x == score)
    return 100.0 * (lower + 0.5 * equal) / len(scores)


def z_score(score, scores):
    if len(scores) < 2:
        return 0.0
    mean = statistics.mean(scores)
    std = statistics.pstdev(scores)
    if std == 0:
        return 0.0
    return (score - mean) / std


def result_value(result):
    return {"W": 1.0, "T": 0.5, "L": 0.0}.get(result, 0.0)


def matchup_result(my_row, all_rows):
    matchup_id = my_row.get("matchup_id")
    if matchup_id is None:
        return None, None
    opponents = [
        row for row in all_rows
        if row.get("matchup_id") == matchup_id and row.get("roster_id") != my_row.get("roster_id")
    ]
    if not opponents:
        return None, None
    opponent = opponents[0]
    mine = float(my_row.get("points") or 0)
    theirs = float(opponent.get("points") or 0)
    if mine > theirs:
        return "W", theirs
    if mine < theirs:
        return "L", theirs
    return "T", theirs


def roster_for_owner(league_id, owner_id):
    rosters = get_json(f"{BASE}/league/{league_id}/rosters")
    for roster in rosters:
        if str(roster.get("owner_id")) == str(owner_id):
            return roster
    raise RuntimeError(f"Owner {owner_id} not found in league {league_id}")


def weekly_snapshot(competitor, week, roster_id):
    rows = get_json(f"{BASE}/league/{competitor['league_id']}/matchups/{week}")
    my_row = next((r for r in rows if int(r.get("roster_id")) == int(roster_id)), None)
    if my_row is None:
        return None

    scores = [float(r.get("points") or 0) for r in rows]
    my_score = float(my_row.get("points") or 0)
    result, opponent_score = matchup_result(my_row, rows)

    # A whole league at zero means Sleeper has not produced a meaningful weekly result yet.
    complete_enough = any(abs(score) > 0.0001 for score in scores)

    return {
        "week": week,
        "status": "scored" if complete_enough else "pending",
        "score": round(my_score, 2),
        "league_size": len(scores),
        "league_score_percentile": round(percentile(my_score, scores), 3) if complete_enough else None,
        "league_score_z_score": round(z_score(my_score, scores), 4) if complete_enough else None,
        "league_week_rank": (
            1 + sum(1 for score in scores if score > my_score)
            if complete_enough else None
        ),
        "matchup_result": result if complete_enough else None,
        "opponent_score": round(opponent_score, 2) if complete_enough and opponent_score is not None else None,
    }


def choose_battle_winner(a, b):
    if a["status"] != "scored" or b["status"] != "scored":
        return None, "pending"

    # Primary: league-relative scoring percentile.
    ap = a["league_score_percentile"]
    bp = b["league_score_percentile"]
    if not math.isclose(ap, bp, abs_tol=0.0005):
        return ("chris" if ap > bp else "tete"), "league_score_percentile"

    # Tiebreak 1: how many standard deviations above/below that league's weekly mean.
    az = a["league_score_z_score"]
    bz = b["league_score_z_score"]
    if not math.isclose(az, bz, abs_tol=0.00005):
        return ("chris" if az > bz else "tete"), "league_score_z_score"

    # Tiebreak 2: actual result in each person's own league.
    ar = result_value(a.get("matchup_result"))
    br = result_value(b.get("matchup_result"))
    if not math.isclose(ar, br):
        return ("chris" if ar > br else "tete"), "matchup_result"

    return "tie", "tie"


def markdown(scoreboard):
    competitors = scoreboard["competitors"]
    standings = scoreboard["standings"]
    rows = []
    for week in scoreboard["weeks"]:
        c = week["competitors"]["chris"]
        t = week["competitors"]["tete"]
        winner = week["battle_winner"] or "Pending"
        winner_label = (
            competitors.get(winner, {}).get("display_name", winner)
            if winner not in (None, "tie") else ("Tie" if winner == "tie" else "Pending")
        )
        c_pct = "—" if c["league_score_percentile"] is None else f"{c['league_score_percentile']:.1f}%"
        t_pct = "—" if t["league_score_percentile"] is None else f"{t['league_score_percentile']:.1f}%"
        rows.append(
            f"| {week['week']} | {c['score']:.2f} | {c_pct} | {t['score']:.2f} | {t_pct} | {winner_label} |"
        )

    return f"""# {scoreboard['competition_name']}

Cross-league fantasy battle between **{competitors['chris']['display_name']}** and **{competitors['tete']['display_name']}**.

## Battle standings

| Competitor | Battle points | Weekly wins | Weekly losses | Weekly ties |
|---|---:|---:|---:|---:|
| {competitors['chris']['display_name']} | {standings['chris']['battle_points']:.1f} | {standings['chris']['battle_wins']} | {standings['chris']['battle_losses']} | {standings['chris']['battle_ties']} |
| {competitors['tete']['display_name']} | {standings['tete']['battle_points']:.1f} | {standings['tete']['battle_wins']} | {standings['tete']['battle_losses']} | {standings['tete']['battle_ties']} |

## Weekly head-to-head

The primary metric is **weekly score percentile within each competitor's own league**. This makes different lineup and scoring settings much less important than simply asking: *how badly did you beat (or get beaten by) your own league that week?*

| Week | Chris score | Chris league percentile | Tete score | Tete league percentile | Battle winner |
|---:|---:|---:|---:|---:|---|
{os.linesep.join(rows) if rows else '| — | — | — | — | — | Season not scored yet |'}

### Tiebreakers

1. League-relative z-score.
2. Actual matchup result in each competitor's league (win > tie > loss).
3. If still equal, the battle week is a tie and each gets 0.5 battle points.

Generated automatically from Sleeper data at `{scoreboard['generated_at']}`.
"""


def main():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    nfl_state = get_json(f"{BASE}/state/nfl")
    current_week = int(nfl_state.get("week") or 1)

    competitors = {item["key"]: item for item in config["competitors"]}
    resolved = {}
    for key, competitor in competitors.items():
        roster = roster_for_owner(competitor["league_id"], competitor["owner_id"])
        resolved[key] = {
            **competitor,
            "roster_id": int(roster["roster_id"]),
            "season_wins": int((roster.get("settings") or {}).get("wins") or 0),
            "season_losses": int((roster.get("settings") or {}).get("losses") or 0),
            "season_ties": int((roster.get("settings") or {}).get("ties") or 0),
        }

    weeks = []
    standings = {
        "chris": {"battle_points": 0.0, "battle_wins": 0, "battle_losses": 0, "battle_ties": 0},
        "tete": {"battle_points": 0.0, "battle_wins": 0, "battle_losses": 0, "battle_ties": 0},
    }

    for week in range(1, current_week + 1):
        c = weekly_snapshot(resolved["chris"], week, resolved["chris"]["roster_id"])
        t = weekly_snapshot(resolved["tete"], week, resolved["tete"]["roster_id"])
        if c is None or t is None:
            continue

        winner, decided_by = choose_battle_winner(c, t)
        if winner == "chris":
            standings["chris"]["battle_points"] += 1.0
            standings["chris"]["battle_wins"] += 1
            standings["tete"]["battle_losses"] += 1
        elif winner == "tete":
            standings["tete"]["battle_points"] += 1.0
            standings["tete"]["battle_wins"] += 1
            standings["chris"]["battle_losses"] += 1
        elif winner == "tie":
            standings["chris"]["battle_points"] += 0.5
            standings["tete"]["battle_points"] += 0.5
            standings["chris"]["battle_ties"] += 1
            standings["tete"]["battle_ties"] += 1

        weeks.append({
            "week": week,
            "battle_winner": winner,
            "decided_by": decided_by,
            "competitors": {"chris": c, "tete": t},
        })

    scoreboard = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "competition_name": config["competition_name"],
        "season": config["season"],
        "nfl_week": current_week,
        "rules": config["rules"],
        "competitors": resolved,
        "standings": standings,
        "weeks": weeks,
    }

    save_json(SCOREBOARD_PATH, scoreboard)
    README_PATH.write_text(markdown(scoreboard), encoding="utf-8")
    print(f"Wrote {SCOREBOARD_PATH}")
    print(f"Wrote {README_PATH}")


if __name__ == "__main__":
    main()
