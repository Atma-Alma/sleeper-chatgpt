# Chris vs Tete Fantasy Battle

This folder tracks a season-long cross-league competition between **Chris / Valaritas** (`cmartin303`, The Sunday Heist in **Do Work**) and **Tete** (`Timboslice796` in **Drone Daddys**).

## Why the battle is normalized

The two Sleeper leagues do not use identical lineup/scoring rules. Chris's league starts QB, 2 RB, 2 WR, TE, FLEX, K and DEF, while Tete's league starts QB, 2 RB, 2 WR, TE and 2 FLEX. There are also small scoring-setting differences.

Because of that, **raw weekly fantasy points are shown but do not decide the cross-league winner by themselves**.

## Weekly battle rule

For every scored NFL fantasy week:

1. Take Chris's score and rank it against every team in the Do Work league that week.
2. Take Tete's score and rank it against every team in the Drone Daddys league that week.
3. Convert each result to a league-relative percentile.
4. The higher percentile wins the Chris-vs-Tete battle for that week and earns **1 battle point**.
5. If the percentiles tie, use league-relative z-score as the first tiebreaker.
6. If still tied, a win in the competitor's own Sleeper matchup beats a tie, which beats a loss.
7. If still tied, the battle week is a draw and each competitor earns **0.5 battle points**.

This answers the fairest cross-league question: **who performed better relative to the competition they actually faced?**

## Files

- `config.json` — competitors, Sleeper identifiers and battle rules.
- `update_battle.py` — pulls both Sleeper leagues and builds the normalized weekly scoreboard.
- `scoreboard.json` — machine-readable season battle standings and weekly detail.
- `.github/workflows/update-competition.yml` — refreshes the battle scoreboard automatically every hour and can also be run manually.

## Current status

The 2026 season is at Week 1 and the battle is awaiting its first scored week. The automated updater will populate weekly results as Sleeper records fantasy points.
