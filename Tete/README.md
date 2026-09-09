# Tete Sleeper / ChatGPT Setup

This folder is the dedicated Sleeper data feed for **Tete**.

- Sleeper league ID: `1370052597343326208`
- Team identifier: `Timboslice796`
- GitHub repo: `Atma-Alma/sleeper-chatgpt`
- Dedicated folder: `Tete/`
- Automatic refresh schedule: hourly at minute 37

## Main data files

- `Tete/sleeper-chatgpt.json` — complete league feed
- `Tete/my-team.json` — Tete's roster, matchup and opponent
- `Tete/waivers.json` — available players and waiver context
- `Tete/rosters.json` — all league rosters
- `Tete/matchups.json` — current-week matchups
- `Tete/transactions.json` — league transactions

Raw feed URL:

`https://raw.githubusercontent.com/Atma-Alma/sleeper-chatgpt/main/Tete/sleeper-chatgpt.json`

## Recommended ChatGPT setup for Tete

1. Sign into Tete's own ChatGPT account.
2. In ChatGPT, connect GitHub from Settings > Plugins (or the GitHub connection shown in ChatGPT).
3. If Chris has added Tete's GitHub account as a read-only collaborator, authorize the `Atma-Alma/sleeper-chatgpt` repository when prompted. Because the repository is public, the raw data URL can also be used without write access.
4. Start a dedicated chat named something like `Tete Fantasy Football Advisor`.
5. Paste the setup prompt below into that chat.

### Setup prompt

Use the GitHub repository `Atma-Alma/sleeper-chatgpt` as the source of truth for my Sleeper fantasy football team. My dedicated data is only under the `Tete/` folder. Do not use the root-level Valaritas files for my team.

My Sleeper league ID is `1370052597343326208` and my team identifier is `Timboslice796`.

Use these files when advising me:
- `Tete/my-team.json` for my roster, starters, matchup and opponent.
- `Tete/waivers.json` for available players, waiver position/budget and trending adds/drops.
- `Tete/rosters.json` for all teams and league-wide roster comparisons.
- `Tete/matchups.json` for current matchups.
- `Tete/transactions.json` for recent league activity.
- `Tete/sleeper-chatgpt.json` when you need the complete league data set.

Act as my fantasy football advisor. Help me maximize sustainable wins throughout the season. When I ask for an update, check the latest Tete data before answering. Evaluate lineup choices, injuries, free agents, waiver claims, waiver priority or FAAB value, trades, roster construction, opponent strengths, league transactions, and upcoming matchup risk. Tell me when no move is better than making a move. Preserve valuable waiver priority or FAAB when the expected gain is small. Be proactive about identifying players who could become valuable before the rest of the league reacts.

When recommending a transaction, always tell me:
1. Who to add.
2. Who to drop, if anyone.
3. Whether to use a waiver claim/FAAB or wait for free agency.
4. Why the move improves my team.
5. The downside or opportunity cost.

Keep Tete's league completely separate from Chris/Valaritas.

## Read-only access

Tete does not need write access for ChatGPT analysis. Read access is sufficient. The GitHub Actions workflow in Chris's repository performs the data refreshes and commits updated JSON files.

If Tete is only using the public raw feed, no GitHub write permission is required at all.
