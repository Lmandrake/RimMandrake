## spec
_not recorded in the source queue_

## verify
_not recorded in the source queue_

## criteria
_not recorded in the source queue_

## notes
🔧 **FIXED ON DISK 2026-08-15 by BUILD — NOT YET CONFIRMED LIVE.** The repo copy had been
correct since `c57f347` (the rename commit); only the game copy under `Xenotypes\` was
stale. So it was never an artifact migration — it was a file that had never been
deployed. Backed up to `MandrakeJawa.xtp.bak-2026-08-15`, copied, md5 equal,
`validate_save_artifact.py` reports 36/36 resolve and zero dangling.
🔴 **THAT IS DISK EVIDENCE, AND DISK EVIDENCE IS WHAT GOT THIS WRONG THE FIRST TIME.**
The superseded claim in LIVE.md was ALSO "36/36 references resolve" from an offline
validator, and the running game contradicted it. The engine is the only witness that
counts here, and the game now running loaded the OLD file at startup, so this session
CANNOT confirm the fix.
⇒ **CLOSING CONDITION, and it costs nothing to collect:** the NEXT load's startup log
carries **zero** `Could not load reference to Verse.GeneDef named Jawa_*` lines. Today's
load carried 12 GeneDef lines, of which 4 were ours. `harvest_log.py --show scribe`
reads them. Until that reads clean, this stays OPEN as *fix deployed, unverified*.
⚠️ **NOT actioned and still live: `softshadow.xtp` carries two dead names** —
`Jawa_Gene_Skittish` and `Jawa_Head_Plain` — and will drop those genes silently at world
creation exactly as `MandrakeJawa.xtp` would have. Not in our repo and not what the owner
named, so BUILD correctly left it. Someone must decide whether it matters before worldgen.
`pokean.xtp` is clean.

**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

blocked — needs a live game. **Fix deployed to the game copy 2026-08-15, never
witnessed.** ⚠️ This item had NO `state:` line for four days, so it was invisible
to the board and to every seat sweeping by state. Added 2026-08-19.
CLOSING CONDITION, and it costs nothing to collect: the next load's startup log
carries **zero** `Could not load reference to Verse.GeneDef named Jawa_*`.
`harvest_log.py --show scribe` reads it. Today's load carried 12 GeneDef lines,
4 of them ours. ⛔ Offline validation cannot close this — an offline validator
already claimed 36/36 resolve and the running engine contradicted it.
✅ The `softshadow.xtp` half is DEAD: the owner had the file deleted 2026-08-15.

**raised:** 2026-08-15 CHECK, from the live startup log of the 575-mod load.

**finding:** `MandrakeJawa.xtp` — the shipping v1 xenotype — **silently drops 4 of our own
          GeneDefs every time it loads.** RimWorld logged 17 Scribe `Could not load
          reference to` lines at startup; 4 are ours:
            `Jawa_Eyes_HugeAmber`  → live def is `RimMandrake_Jawa_Eyes_HugeAmber`
            `Jawa_Eyes_HugeOrange` → live def is `RimMandrake_Jawa_Eyes_HugeOrange`
            `Jawa_Head_Plain`      → live def is `RimMandrake_Jawa_Head_Plain`
            `Jawa_Gene_Skittish`   → live def is `RimMandrake_Jawa_Skittish`
          🔴 The last one is NOT a straight prefix — `Gene_` was dropped as well, so a
          blind "add RimMandrake_ to everything" migration fixes three and breaks the
          fourth differently.
          **Nothing is missing from the game.** All four new names are present in today's
          fresh 575-mod dump. The defs were renamed and the SAVED FILE was never migrated.
          Three further dead genes are `guy762_*` and are EXPECTED — that donor is
          deliberately off for C36. Five more are `RG_*` ThingDefs inside LWM Deep
          Storage's own settings, benign B-BOIL collateral.
why it changes the design, not just the code:
          The .xtp **bakes at world creation**. Whatever it drops is lost in the world the
          owner is about to generate, and the drop is SILENT in play — a Jawa comes out
          without its head type and eye colours and nothing says so.
          ⚠️ `softshadow.xtp` and `pokean.xtp` carry some of the same dead names.
🔴 this invalidates a recorded fact:
          `LIVE.md` said "`MandrakeJawa.xtp` is CLEAN: 36/36 references resolve." That was
          an OFFLINE verdict and the running game contradicts it. Corrected in LIVE.md.
          **An offline validator cannot catch this class at all** — Scribe resolves saved
          names at load time, and a def-dump check answers a different question. C42's
          "the dangling-reference question is CLOSED offline" is falsified for the .xtp.
decision needed:
          Migrate the four names in the saved .xtp before the worldgen run, or accept the
          drops. NOT MINE TO CHOOSE and not mine to author — I am not editing a shipping
          save artifact on my own authority. ⛔ Blocking on the real worldgen run: it bakes.

**evidence:** Player.log 2026-08-15 16:1x, 575 mods, build 1.6.4871 rev591, dump captured
2026-08-15T23:12:54Z — same stack as the running game, so not a stale-dump
artifact. Def loader crossref was CLEAN at baseline 25; this is Scribe only.

---

# ✅ CLOSED — DECIDE, 2026-08-21 13:0x. The closing condition was met, and collected.

**The condition, as this item stated it and unchanged after the fact:** *"the NEXT load's
startup log carries zero `Could not load reference to Verse.GeneDef named Jawa_*` lines."*

**Collected from the run that ended 2026-08-21 12:36:12** (`Player.log`, 21,198 lines,
RimWorld 1.6.4871 rev591, 578 active mods, state `EXITED` — so the log is complete and
nothing is still writing to it), via `harvest_log.py --show scribe`:

| | 2026-08-15 | this run |
|---|---|---|
| `Could not load reference` lines, all types | — | **8** |
| of those, `GeneDef` | 12 | **3** |
| of those, **`Jawa_*`** | **4** | **0** |
| any `Jawa_` in the whole scribe view | — | **0** |

⭐ **The three surviving `GeneDef` lines matter as much as our zero.** They are
`guy762_Furskin_shortfur`, `guy762_BodySizeGene_smaller`, `guy762_Eyes_HugeYellow` — so the
detector is demonstrably still firing on this run. **Our zero is a measured absence, not a
check that quietly stopped running**, which is the failure mode that would otherwise make
this exact evidence worthless.

**Corroborated on disk, deliberately second and not instead of the above** —
`validate_save_artifact.py` against the deployed `MandrakeJawa.xtp`, read against the
**frozen `OFFICIAL-2026-08-21` capture** (67,942 defNames indexed, not the 08-15 def set the
original claim used): **36/36 references resolve, ✅ no dangling names.** 19 of the 585
modIds captured at save time are no longer active, and that is provenance only — no
reference above is missing.

⚠️ **This item was right that disk evidence got it wrong the first time, and that is why the
log is the closer here and the validator is only the corroboration.** Do not reverse that
order if this ever reopens.

## ⚪ the `softshadow.xtp` half is VOID — not passed, not failed

This item's notes said: *"`softshadow.xtp` carries two dead names — `Jawa_Gene_Skittish` and
`Jawa_Head_Plain` — and will drop those genes silently at world creation. Someone must decide
whether it matters before worldgen."*

🔑 **There is no `softshadow.xtp`.** The Xenotypes folder
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Xenotypes`)
holds exactly six files — `Dark Glutton.xtp`, `Dark Troll.xtp`, `MandrakeJawa.xtp`,
`MandrakeJawa.xtp.bak-2026-08-15`, `mimic.xtp`, `pokean.xtp` — and a search of the whole
`LocalLow` tree for `*softshadow*` returns nothing.

⇒ **The decision this item reserved for DECIDE has no subject.** Recording it as void rather
than as answered, because "we decided it was fine" would be a claim about a file nobody can
open. ⚠️ **Scope of the search, stated so it can be re-run rather than trusted:** the user
data tree only. If a `softshadow.xtp` turns up inside a mod folder, this is a new question,
not this one reopened.

✅ **And the two dead names are gone from the file that did exist.** Checked directly:
`MandrakeJawa.xtp` carries **zero** `Jawa_Gene_Skittish` and zero bare `Jawa_Head_Plain`; its
one near-match is `RimMandrake_Jawa_Head_Plain`, the correct prefixed form. The
`.bak-2026-08-15` still carries both bare names, which is what a backup is for.
⚠️ My first grep for `Jawa_Head_Plain` reported a hit on the fixed file and it was a
**substring match inside the prefixed name** — a false positive that would have reopened a
closed item. The validator, not the grep, is the instrument here.
