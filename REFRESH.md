# REFRESH.md — what to do after changing the mod list

_Written 2026-08-11, ahead of adding xenotype packs and ship weaponry._

**Every generated artefact in this project is a snapshot of ONE mod set.** Add a
mod and they do not break — they quietly start describing a game that no longer
exists. Silently stale data is worse than missing data, because it still answers
questions.

## The one command

```bash
python Utils/refresh.py
```

Changes nothing. Prints what is stale, what it costs to fix, and whether you
need to pay for a game load.

```
python Utils/refresh.py --offline    # rebuild everything not needing a load (seconds)
python Utils/refresh.py --patches    # regenerate + validate the armoury patches
python Utils/refresh.py --all        # both, in the right order
```

It fingerprints the active mod list **including load order** — RimWorld resolves
def overrides by order, so the same mods reordered really is a different game —
and compares that against a stamp in `mods/inventory/GENERATED_FROM.json` and
against the live dump's own manifest.

## The dependency order — do not shuffle it

| # | step | cost |
|---|---|---|
| 1 | `ModsConfig.xml` changes | the root of all staleness |
| 2 | offline scan → `mods/inventory/`, contact sheets | **seconds** |
| 3 | **live dump** → `DefDump/` | **a full game load, ~23 min** |
| 4 | generated patches (read the live dump) | seconds, but need a *current* dump |
| 5 | validation (`--live` wants the dump) | seconds |
| 6 | `def_diff.py` (wants both) | seconds |

Only step 3 is expensive, and 4–6 all depend on it. So the useful question is
always *"do I need a game load?"* — and `refresh.py` answers exactly that.

## Taking a fresh live dump

1. Arm it:
   ```
   echo all > "%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\DefDump\dump_request.txt"
   ```
2. Launch and reach the **main menu**. That is all — it writes at startup, before
   any world exists. No colony needed.
3. Watch for `[RimDefDump]` in `Player.log`. Expect ~27 s and ~1.2 GB.
4. `python Utils/refresh.py --all`

The marker is **not** consumed, so it re-dumps on every load until you delete
it. Delete it when you are done, or every debugging load pays 27 seconds and a
gigabyte.

## The trap that makes this necessary

`refresh.py` **refuses** to regenerate the armoury patches against a stale dump,
and that refusal is the point:

> The generator reads CURRENT damage values out of the live dump and retunes
> from them. Run it against a dump of a different mod set and it bakes in
> numbers from a game you no longer have — silently, and the output still
> validates.

## Adding weapon mods specifically (ship weaponry)

The armoury generator is **idempotent under roster change**, deliberately. It
maps each old damage value onto its target band by a *fixed function of the
value*, not by rank among current members.

That distinction is load-bearing. The first implementation ranked whatever was
installed and laid it across the band, so **adding one new blaster shifted the
assigned damage of every existing blaster**. Install a ship-weapons pack, re-run,
and the entire armoury churns — values move for defs nobody touched, and the
diff is unreadable.

With fixed anchors, new defs slot in and existing defs hold still. Verified: two
consecutive runs are byte-identical.

**When you add ship weaponry, expect to:**
1. Take a fresh dump (new weapons are invisible until you do).
2. Check whether the new guns land in an existing rung. `SOURCE_RANGE` in
   `gen_armoury_patch.py` assumes the vanilla-ish input range per rung; a mod
   whose turbolaser already does 500 will be **clamped**, not extrapolated — by
   design, so one outlier cannot drag a rung, but it does mean genuinely
   ship-scale mods may need their own rung.
3. Re-run `compare_ladder.py` to see where everything sits afterwards.

## Adding xenotypes specifically

Xenotypes mostly add `XenotypeDef`, `GeneDef` and pawnkinds rather than weapons,
so the armoury patches are unaffected. What *does* move:

- `mods/inventory/` — if the pack adds animals or races.
- The **live dump**, and therefore `validate_patch.py --live`. A patch you write
  against a new xenotype's defs cannot be validated until the dump includes it.
- `mods/def_override_clusters.md` — new mods mean new contested defNames.

## Debug configurations — do not burn a game load on one

Mods get pulled temporarily to isolate a bug. An artefact rebuilt during that
window is **accurate but unrepresentative**: it describes a configuration nobody
intends to play.

Offline artefacts are cheap and self-correcting — `refresh.py` flags them stale
the moment the mods return — so rebuilding during a debug window costs nothing.
**The live dump is different.** Do not spend 23 minutes capturing a debug stack:

- it is stale the instant the pulled mods come back,
- `validate_patch.py --live` will report the missing mods' defs as *"does not
  exist in the live game"* — a wall of confident false errors,
- and `refresh.py` will (correctly) refuse to regenerate patches from it.

Record the reason when you rebuild during one:

```bash
python Utils/refresh.py --offline --note "VSIE pulled temporarily for debugging"
```

The note is stored in `GENERATED_FROM.json` and printed on every status run. Six
months later the hash only tells you the mod set differed; the note tells you it
was deliberate and temporary.

## What is currently stale

As of writing, the live dump was already out of date within a day: the mod list
gained `vanillaexpanded.helixiengas` and lost two others. `refresh.py` caught it
on its first run, which is the whole argument for having it.
