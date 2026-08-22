## spec
**`infrastructure/state/NEXT_RELOAD.md` is the run sheet CHECK spends a ~25-minute
cold load against, and it is describing a load that already happened.**

Assembled by DECIDE **2026-08-20 07:35**. Since then the **2026-08-22 08:40** load ran
(578 mods, rev591), was harvested, and `NEXT_LOAD_LOG_HARVEST_1` closed on it. The owner
said 2026-08-22 10:25 that we are *"building towards a fresh cold start"*, so this sheet
is about to be used.

A staleness banner naming the four specific breaks is already at the top of the file —
that is a warning, not a fix. **Only DECIDE reassembles the sheet**, because it is built
from every seat's queue and CHECK cannot see what BUILD and REP intend to ride along.

**What is known to be wrong, each measured this session:**
- ⛔ **§9 INHABITED's premise.** It is written as a *first run* and says a positive
  sighting settles the architecture gate. `Inhabited` has now run: `[Inhabited] ready:
  2 patches, 193 characters, 0 places, 0 casts` — **193 of 294**, because all 101
  CharacterDefs carrying a `<skills>` block are discarded at def load
  (`CAST_ROSTER_SKILLS_DISCARDED_1`). A baseline taken now is taken against a cast
  missing 34% of its people.
- ✅ **§0's two pending deploys are done** (2026-08-22 10:30 game-down window):
  `Inhabited` in sync at 18 files; `bridgetools --gm --apply` moved the game copy
  `7df3c51b` → `e3e8a89c`. Listing them as pending sends someone to redo them.
- ⚠️ **`harvest_log.py` changed underneath it.** It was counting the load-time
  patch-file manifest as evidence: `303 / 5252 / 2224` RED against baseline 0 for
  MegafaunaYield, `Jawa_Patches`, `JawaVoice`. Now `0 / 0 / 2`. Any figure in the sheet
  taken from the old tool is suspect.
- 🔑 **`269` is dead.** The cast roster is **294** on disk.

## verify
DECIDE rebuilds `NEXT_RELOAD.md` from the current queues, and the rebuilt sheet:
1. carries a fresh `assembled` datestamp later than 2026-08-22,
2. does not list either of the two completed deploys as pending,
3. does not describe `Inhabited` as a first run, and
4. states which items ride the 578 list and which ride minimal.
Then the staleness banner is REMOVED — a banner left on a corrected file trains
everyone to ignore banners.

## criteria
A run sheet whose §0 brief describes the load about to happen. Closed by DECIDE, not
by CHECK.

## Watch out
- 🔑 **CHECK cannot do this one.** The sheet is assembled from all four seats' queues.
  CHECK can say what is wrong with it; only DECIDE can say what the next load is FOR.
- ⚠️ **Do not simply delete §9.** `Inhabited`'s first-run sequence is still the right
  test — it is the *ordering* that broke. It has to run after the cast fix, not before,
  or the architecture gate is measured against a short roster and passes falsely.
- ⛔ **Two loads, not one.** `ROSTER_SURVIVES_OFFMAP_PROOF_1` needs save → quit → reload.
  The old sheet already knew this (§9) and it is the kind of thing a rebuild drops.
- **A rebuild that only adds is not a rebuild.** The failure mode here is a sheet that
  grows a new section for today while keeping yesterday's completed work listed as
  pending — which is exactly how it got into this state.
