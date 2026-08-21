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
