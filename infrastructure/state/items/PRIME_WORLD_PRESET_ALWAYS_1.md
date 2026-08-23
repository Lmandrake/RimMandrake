## spec

🔴 **OWNER, 2026-08-23:** *"So how can we always prime the game to have span=7, coverage=100%
so we don't have to remember to do that?"*

**MEASURED FIRST, and the answer is that there is nowhere to write it.**

| where a setting could persist | what is actually there |
|---|---|
| `Config/Prefs.xml` | 63 keys, and **not one** mentions planet, coverage, subcount or seed. Only `zoomSwitchWorldLayer` |
| a My Little Planet mod config | **none exists.** `oblitus.mylittleplanet` is active and writes no `Config/Mod_*.xml` at all |
| any other config | `grep -li subcount` across all 92 config files returns **nothing** |

⇒ **RimWorld persists nothing about the planet preset.** Both values are re-chosen on
`Page_CreateWorldParams` every single time and fall back to the vanilla defaults —
**coverage 0.3 and subcount 10**. That is not a hypothetical: the world running on
2026-08-23 07:28 read `planetCoverage 0.3` / `tilesCount 119904`
(`LIVE_WORLD_IS_WRONG_PRESET_1`). **The default is the wrong preset and nothing remembers.**

## 🔑 Two different problems, and only one of them needs code

1. ✅ **Players never see this page.** They receive a savegame holding the frozen world —
   there is no worldgen feature in any version. For the shipped product this is a non-issue.
2. 🔴 **WE re-create test worlds**, and that is where it bites every time.

⇒ This is a **development ergonomics** fix, not a v1 content item. Size it accordingly.

## what to build

**A tiny Harmony postfix on `Page_CreateWorldParams`** that sets the two values when the page
opens, in the idiom this project already uses six times over (`mandrake.blastdoorframeasyncfix`,
`mandrake.msedroidfix`, `mandrake.sauridfrillfix`, `mandrake.gravshipastronautfix`, …).

- `planetCoverage = 1.0f`
- the My Little Planet subcount = **7**

⚠️ **Read MLP's own field before writing it.** The subcount is MLP's, not vanilla's; do not
guess the field name or the type. `oblitus.mylittleplanet` is active — read its assembly or
its page patch and name what you found in the commit.
⚠️ **Postfix the page's constructor or `PreOpen`, not `DoWindowContents`** — writing every
frame fights the owner if he ever wants to change it deliberately.
✅ **It must remain overridable.** This primes a default; it does not lock the screen. If he
drags the slider it stays dragged.

⛔ **Do NOT reach for `--despite-map` or any bypass in `w9_run.py` as an alternative.** The
guard is the safety net and it is correct.

## the guard already exists — do not rebuild it

`src/RimMandrake/Utils/w9_run.py:67` holds `EXPECT_TILES = 21872`, refuses at line 243 when
`jawa/world_info_get` disagrees, and passes `expectTiles` into every import call. **Priming
and guarding are different jobs**: the mod stops the mistake being made, the guard stops it
being acted on. Keep both.

## verify

Open a new game to the world-creation page and read it off the bridge, not off the screen:

    python.exe src/RimMandrake/Utils/w9_run.py        # dry run: prints coverage and tilesCount

**PASS = `planetCoverage 1` and `tilesCount 21872` without anyone having touched a slider.**
⚠️ Bridge calls at that screen take **over 25 s** against a 30 s default timeout — use
`timeout=150` and a fresh connection per call, or a late response is read as the next call's
answer and you get an id-mismatch cascade that looks like four different failures.

## criteria

- [ ] A fresh world-creation page opens at coverage 1.0 and subcount 7 with no human action.
- [ ] The values are still draggable — this is a default, not a lock.
- [ ] The MLP field name is read from the mod, not guessed, and named in the commit.
- [ ] `w9_run.py`'s `EXPECT_TILES` guard left exactly as it is.

## watch out

- ⚠️ **An assembly cannot be written while the game is running** — the OS locks it. This
  deploys in the shutdown window like every other companion DLL.
- 🔑 **A wrong subcount shifts every tile ID.** `world/ASHKARR_WORLDMAP_tiles.csv` addresses
  0…21871; against a 119,904-tile grid every one of those points at different ground and a
  paint reports success while writing a scrambled planet. That is what this prevents.
