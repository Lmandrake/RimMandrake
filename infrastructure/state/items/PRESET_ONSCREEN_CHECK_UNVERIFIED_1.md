## spec
🔴 **I closed `worldbuilder-preset-is-wiped-at-every-launch-not-just-on-steam-updates-6b1e4d`
tonight against the wrong half of its own criteria.** That item asked for two things:

1. *"on the world-creation page, Configure Planet reads **Scale 7** and **Coverage 100%**.
   🔴 If Scale reads 10, the preset lost its parameters — ABORT, do not generate."*
2. *"after the next launch: the LocalLow file is still intact and unchanged."*

I verified (2) — the file is 3,895 bytes, dated 2026-08-20 00:59, still carrying
`myLittlePlanetSubcount 7`, `planetCoverage 1`, `saveGenerationParameters True`, and it is
STILL intact right now after the whole session. I closed the item on that.

**(1) is the half that matters, and it failed.** The owner, remaking the world later in the
session: *"it had lost the scale 7 coverage 100% settings I need."*

⇒ **The file being intact does not mean the game read it.** Those are two different claims
and I treated the cheap one as evidence for the expensive one.

WHAT IS KNOWN, measured:
- LocalLow preset: intact, unchanged, correct values. ✅
- The **workshop stub was regenerated at 01:18**, during this session's launch — 683 bytes,
  parameterless. AWF's `[StaticConstructorOnStartup] Refresh()` does this every launch and
  that part is expected.
- `TryLoadPreset` is documented as first-wins with LocalLow scanned before mod folders,
  which is why the LocalLow copy was supposed to outrank the stub.
- ⚠️ The owner's world-creation page nevertheless came up without the parameters.

So either the scan order is not what we believe, or the game will not re-read the preset for
a SECOND world created inside one session, or the broken session state
(`PAINT_UNDER_MAP_DESTROYS_GAME_1`) took the preset loader with it. **All three are
untested.** ⛔ Do not write any of them down as the cause.

## verify
On the next launch, BEFORE generating anything: reach the world-creation page and read
Scale and Coverage off the screen. Then, without leaving the session, generate a second
world and read them again — that isolates "first world only" from "never".

## criteria
- Configure Planet reads **Scale 7 / Coverage 100%** on the FIRST world of a session
- and again on a SECOND world created in the same session
- if either reads 10, the preset route is not reliable and the parameters must be set some
  other way before the one-shot run — this is the click that decides 21,872 tiles

## notes
Filed by CHECK, 2026-08-21, correcting my own close from earlier the same session. The
closed item stays closed — a run is immutable and a later failure does not reopen it — but
its evidence covered the file and not the screen, and this item is the descendant that
covers the screen. ⚠️ The lesson generalises: **a file being correct on disk is never
evidence that the program read it.**

## PARTLY SETTLED OFFLINE — CHECK, 2026-08-23 11:4x, game DOWN

🔴 **THE OPERATIONAL FINDING, and it is the thing to act on.** The preset does not apply
itself. Worldbuilder's `UI/Page_SelectWorld.cs:46` sets `WorldPresetName = null` **every time
that page opens**, and it is set only by clicking a preset (`:472`). Its
`HarmonyPatches/Page_CreateWorldParams_Reset_Patch.cs:32-34` then forces `subdivisions = 10`
and `TrySetMLPSubcount(10)` **unconditionally**, and returns early at `:41` if no preset is
currently selected — only past that point do `:58` (coverage) and `:75-76` (subcount 7) run.

⇒ **Any world created without clicking *tidally locked world* on the Select World page comes
out at coverage 0.3 / subcount 10** — including a dev quicktest and a bridge-made world —
no matter how correct the preset file is. That is what produced the world in
`LIVE_WORLD_IS_WRONG_PRESET_1`.

### Ruled out offline — two of the three named suspects are dead

- ⛔ **Scan order is NOT the problem; the doctrine hypothesis is disproven.**
  `…/3522102833/1.6/Source/WorldPresetManager.cs:144` adds
  `GenFilePaths.FolderUnderSaveData("Worldbuilder")` (LocalLow) **before** mod folders
  (`:147-157`), and `TryLoadPreset:189-197` is **first-wins**. The AWF stub cannot shadow the
  LocalLow copy.
- ⛔ **AWF never wipes LocalLow.** `…/3626210061/Source/WorldbuilderCompat.cs:33` deletes only
  `AlienWorldsFramework.root/Worldbuilder`. "Wiped at every launch" only ever applied to the
  MOD copy — 🔑 this corrects
  `worldbuilder-preset-is-wiped-at-every-launch-not-just-on-steam-updates-6b1e4d`. It also
  nulls `presetsCache` at startup (`:74`), so a stale cache is not the failure either.

### The file is intact — confirmed, not assumed

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Worldbuilder\TidallyLocked\Preset.xml`
— 3895 bytes, mtime **2026-08-20 00:59**, `<myLittlePlanetSubcount>7</myLittlePlanetSubcount>` (:36),
`<saveGenerationParameters>True</saveGenerationParameters>` (:37), `<planetCoverage>1</planetCoverage>` (:69),
15 `Jawa_*` faction lines. `diff` against `design/Jawa/worldbuilding/TidallyLocked_Preset.xml`
differs only by the repo master's comment block.
(The AWF stub regenerated again at 2026-08-23 00:10, 683 bytes, no subcount, no coverage — harmless per the above.)

### What still genuinely needs the game — ONE observation

With ***tidally locked world* selected** on the Select World page, does Configure Planet read
**Scale 7 / Coverage 100%** on screen — and again for a **second** world created in the same
session? Nothing on disk can answer that; everything else in this item now can.
