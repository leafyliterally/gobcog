# Changelog since upstream

Everything below was added on top of the source repo after
[`752e2a0`](https://github.com/aikaterna/gobcog/commit/752e2a06e6325b1bc9d22c863fa3e20d2f085177)
("4.1.2 Fix rebirth costs requiring a higher upfront cost"), the last commit inherited from
upstream. Listed oldest to newest.

## `8cbf749` — various adjustment for ojf

- Adventure timers are now 3 minutes for every fight (used to be a mix of 2 and 5 minutes).
- Fixed Insight sometimes revealing the wrong kind of weakness; added extra flavor text for very tough monsters.
- Psychic's "focusing" message now has 3 different variations instead of always the same one.
- Fixed pets losing loyalty for the wrong reasons.
- Raised the rebirth cap for the dev rebirth command from 100 to 250.
- The give-loot command can only target real Discord members now.
- Backpack set names are now capitalized correctly.
- Added a new feature that announces when an adventure starts across servers.

## `025ce14` — improvement for adv sync

- Cross-server announcements now show each server's real current name instead of a fixed one.
- The cross-server alert now shows the monster's name and picture (easy mode only).

## `4a77221` — adjust insight parameter

- Tuned how often Insight reveals a magic vs. a diplomacy weakness.

## `c100c1b` — change after adventure to global cooldown

- Adventures are now shared across the whole bot instead of one per server, so only one adventure can happen at a time anywhere.
- The cooldown between adventures is now shared bot-wide too, instead of per server.
- The cooldown timer now starts after rewards are handed out, not the moment the fight ends.
- The owner-only cooldown command now also works outside of a server.

## `44d005a` — fix false alarm on finished adv

- Fixed a bug where starting a new adventure right as the last one finished handing out rewards could break things.

## `79d9c61` — fix button order, add participant button, update advcooldown

- Added a private "Participants" button showing who chose fight, magic, talk, pray, or run.
- Fixed the Magic and Talk buttons being in the wrong order.
- Lowered the minimum and default adventure cooldown, which had been set too high by mistake.

## `18ed356` — safe pagify impl for dealing with ansi code block

- Fixed long reward messages sometimes getting cut off in the middle of a decorated block, which made them look broken.

## `e951d76` — fix adventurestats breaking due to global adventure

- Fixed the adventure stats command crashing after adventures became shared across the whole bot.

## `51d71e4` — fix insight for global adventure

- Fixed Insight breaking after adventures became shared across the whole bot.

## `eaf34c1` — qol: update stats target xp to be max lvl instead of next lvl

- Your character sheet now shows the XP needed to reach the max level, not just the next level.
- Retuned how often Insight reveals each type of weakness.
- Raised the max character level allowed by the dev rebirth command.

## `a726b5f` — fix insight timestamp cooldown, bug fix with adventure dispatch

- Insight's cooldown message now shows the correct time it'll be ready again.
- Fixed adventure announcements not firing correctly in hard mode.
- Battle results now correctly show "Transcended" for tough monsters even outside easy mode.

## `ad67d81` — bp eset cd reduce and skill reset bug fix

- Lowered the cooldown on equipping a full gear set.
- Fixed the skill reset confirmation buttons getting stuck on screen after use.

## `dc17e8f` — wscoreboard fix attempt + cd sentence fix + insight buff

- Fixed cooldown messages awkwardly saying "in in 5 minutes."
- The weekly scoreboard no longer shows players with a zero score for the week.
- Buffed Insight's bonus against tough monsters.
- Changed Insight's icon.

## `2a90a9b` — fix adventure ascended iteration on no adventure

- Fixed a crash that could end an adventure that had no monster in it.

## `657458f` — fix wsc data stuck after 1 year of playing

- Fixed the weekly scoreboard: some players' weekly scores were stuck and never resetting, so they never showed up on the board even though they were active.

## `ce99a96` — buff insight and minor hotfix to ui and calculation

- Insight's team-wide bonus now kicks in on a great roll, not only a perfect one, so it triggers more often.
- Fixed a mix-up where a mage's Insight bonus was boosting the party's melee damage instead of their magic damage.
- Insight now tells you what roll you got when you use it.
- Berserker's bonus damage now shows its own icon instead of a generic one, and no longer shows that icon twice in the battle report.

## `d7442d9` — reduce cd, fix insight cd

- Lowered the minimum cooldown for Insight, Rage, Focus, Music, and Bless to 4 minutes everywhere it's checked, so they're consistent.
- Fixed Psychics getting an overly long cooldown right after switching to that class.
- Insight now also tells you your roll when someone else already beat you to it.
- Fixed Insight's roll messages showing a missing bracket, and sometimes an ugly long decimal instead of a clean number.

## `ad9d19a` — fix ordering of the insight message

- When Insight's bonus helps the party, a message now tells you who to thank and how much it boosted attack, talk, and magic by.

## `b397bdd` — more insight adjustment

- Top Insight rolls now show exact combat effectiveness instead of vague flavor text.
- Insight's team bonus now scales with roll quality (8%-25%) instead of all-or-nothing, and triggers earlier.
- The team bonus message now shows the roll that triggered it instead of an icon.
- Tweak Insight messages.

## `0768a53` — insight word refresh

- Insight's discovery message got a wording refresh.

## `latest`

- Speed up how quickly adventure rewards show up after a fight, by reading and saving each player's character data once instead of several times over.
- Fixed a bug where bonus treasure chests earned by a high-rebirth player could accidentally get added to other party members' chests too, instead of just their own.
- Bless, Insight, Rage, Focus, and Music now respond faster with character data saved in the background.
- Apply fixes to `dev.py` and `negaverse.py` as an impact on adventure optimization
