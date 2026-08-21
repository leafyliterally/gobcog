# Changelog since upstream

Everything below was added on top of the source repo after
[`752e2a0`](https://github.com/aikaterna/gobcog/commit/752e2a06e6325b1bc9d22c863fa3e20d2f085177)
("4.1.2 Fix rebirth costs requiring a higher upfront cost"), the last commit inherited from
upstream. Listed oldest to newest.

## `8cbf749` — various adjustment for ojf

- Unified adventure timers to 3 minutes across boss/miniboss/normal (was 2/5 min split); updated
  "Heroes have N minutes" copy to match.
- Fixed Psychic insight's physical/magic/diplomacy roll-threshold mixup; added flavor text for
  very high armour/magic/diplomacy resistance.
- Psychic's "focusing on the monster ahead" line is now randomized across 3 variants.
- Fixed pet-loyalty check wrongly factoring in intelligence/luck.
- `[p]devrebirth` max rebirth level raised 100 → 250.
- `[p]give loot` command: `users` converter narrowed to `discord.Member` only.
- `[p]backpack set` uses proper title-casing (`_title_case`) instead of `.title()`.
- Added new `adventuresync` cog (cross-server adventure-start notifications).
- `.gitignore`: added `.DS_Store`, `__pycache__/`, `.vscode/`.

## `025ce14` — improvement for adv sync

- `adventuresync` reads live `guild.name` instead of a hardcoded name in `LINKED_GUILDS`.
- Cross-server alert embed gained a monster name callout and thumbnail (easy mode only).

## `4a77221` — adjust insight parameter

- Insight's diplomacy-branch `physical_roll`/`magic_roll` tuned 0.6 → 0.7, in both
  `class_abilities.py` and `game_session.py`.

## `c100c1b` — change after adventure to global cooldown

- Adventures are now global: `self._sessions` keyed by a fixed sentinel instead of per-guild, so
  only one adventure runs bot-wide at a time. `GameSession.guild` kept for other cogs/dev tools.
- Post-adventure cooldown moved from per-guild to global config.
- Cooldown timestamp now recorded after loot distribution finishes, not right when the fight ends.
- Merchant-cart spawn check stays guild-scoped (compares session's guild vs. message's guild).
- `[p]adventureset advcooldown` is now owner-only (was admin) and works outside a guild.

## `44d005a` — fix false alarm on finished adv

- Closed a race where a second `[p]adventure` could slip in while the first was still
  mid-loot-distribution and stomp the in-flight session.

## `79d9c61` — fix button order, add participant button, update advcooldown

- Added ephemeral **Participants** button showing who picked fight/magic/talk/pray/run.
- Fixed action button order (Magic before Talk).
- `[p]adventureset advcooldown` min/default lowered 30s/10s (bug) → 5s/5s.

## `18ed356` — safe pagify impl for dealing with ansi code block

- Added `safe_pagify()` in `helpers.py`: keeps `` ``` `` code fences atomic across page breaks,
  fixing long reward messages splitting mid-fence via Red's `pagify()`.
- Swapped into both `_result()` pagify call sites that can contain the ANSI treasure-chest block.

## `e951d76` — fix adventurestats breaking due to global adventure

- `[p]adventurestats` still resolved sessions via `get_guild(server_id)`, which broke once the
  session key became a fixed sentinel instead of a real guild ID.
- Fixed to check the sentinel key directly and read `GameSession.guild.name` instead.

## `51d71e4` — fix insight for global adventure

- Fix `[p]insight` broken after global adventure edits.

## `eaf34c1` — qol: update stats target xp to be max lvl instead of next lvl

- Character sheet's target XP now shows the max-level XP requirement instead of next-level XP.
- Insight's physical/magic/diplomacy roll thresholds retuned again (physical-choice and
  balanced-choice branches).
- `[p]devrebirth` max character level raised 1000 → 2500.

## `a726b5f` — fix insight timestamp cooldown, bug fix with adventure dispatch

- `[p]insight`: cooldown message now shows the correct end time via discord timestamp; removed cooldown for insight.
- Adventure dispatch event now correctly dispatch event in hard mode.
- `_result()`: post-battle messages now show "Transcended" in hard mode whenever one occurs.

## `ad67d81` — bp eset cd reduce and skill reset bug fix

- Cooldown reduction for `[p]backpack eset` to 30s.
- `[p]skill reset` confirmation buttons: fixed `AttributeError` on `view.message` that silently kept the Yes/No buttons stuck on the message.

## `latest`

- Fixed doubled "in" in 5 cooldown messages (Discord timestamp already says "in X").
- `[p]wscoreboard` no longer lists users with a zero weekly score.
- Increases `[p]insight` on transcended modifier
- Change Insight icon when doing insight ability
