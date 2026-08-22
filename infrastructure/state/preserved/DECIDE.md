<!-- status: live -->
# Prose rescued from `infrastructure/state/queue/DECIDE.md`

> ✅ **THE MAP IS ADOPTED, AND AUTHORING IS OPEN AGAIN — owner, 2026-08-22.** Verbatim, after
> looking at the four-globe sheet: *"That world, upon examination, really isn't very bad at all…
> we're thinking of trying to adopt it."* ⇒ **Ash'karr as it stands IS the v1 planet**, and work
> on it continues: continuity repairs, landmarks, named places, settlements, terrain detail.
>
> ⛔ **This REPLACES the 2026-08-21 freeze banner**, which said the opposite and is struck. The
> freeze lasted one evening and did its job — it stopped a redraft nobody wanted.
> ⚠️ **What did NOT come back:** re-running `ashkarr_paint.py` to regenerate the bundle, the
> reference-match harness (`refmatch.py` stays cancelled), and worldgen, which is out of every
> version and always was. **The map is edited DIRECTLY, one map, in place** — that is the whole
> method, per `the_one_map.md`.
> 🔮 `design/V2_DREAMS.md > PLANET_METHOD_RETHINK_1` stands as history, not as a plan.
> Ruling: `WORLD_ADOPTED_AUTHORING_OPEN_1` · supersedes `WORLD_FROZEN_RETHINK_PLANET_1`.


🔴 **HAND-WRITTEN. NOT GENERATED. Nothing regenerates this file.**

These 2 sections carried no fields, so the ledger has nowhere to put them —
an event holds scalars and an item file holds spec/verify/criteria, and a briefing
is neither. They were moved here verbatim when `queue/DECIDE.md` became a generated
view, on 2026-08-20. ⚠️ Some are still unanswered.

---

## 📌 SESSION HANDOFF — 2026-08-20 EVENING. Newest first; the morning handoff follows below.

**Shutdown state: clean.** Everything committed and pushed, game DOWN, dump marker consumed,
LIVE mod list = FULL = **578** (`modlist_swap.py --status` reads `matches: FULL`).

### 🔴 Four things this seat did that are NOT in its lane, and why

The owner directed each one personally while working alongside this window. Recorded so a
later reader does not conclude DECIDE has quietly widened her remit.
1. **Authored the planet** — edited `src/RimMandrake/Utils/ashkarr_paint.py` and re-rendered.
   CLAUDE.md's *"iterate by LOOKING"* makes this the world-authoring loop, and he was watching
   the render with me.
2. **Generated sprites** and committed them to `DesertVehicleReskin`.
3. ⛔ **Did NOT deploy any of it.** `deploy_custom_mods.py --mod DesertVehicleReskin` reports
   **6 files of drift** — the regenerated sled art is committed and NOT in the game folder.
   That is BUILD's, deliberately, after the owner's 2026-08-20 correction on the Worldbuilder
   preset: *"a seat boundary is worth most exactly when something feels too urgent to hand over."*
4. **Ruled cast size and the beast ladder** — those two ARE this seat's, and they unblocked
   two BUILD items that would otherwise have bounced.

### ⭐ The single most useful thing learned today, and it cost this session its accuracy twice

🔑 **Four seats share ONE working tree, so a measurement taken while a peer is committing
describes a repo that has stopped existing.** It happened twice in an hour:
- The pre-load brief was written at 07:35 reading 577 mods and *"no assembly rides this load"*.
  Both were false within twenty minutes — BUILD had built and deployed `Inhabited`, and the
  owner enabled it. Corrected in `NEXT_RELOAD.md` §0 with the dead readings struck.
- `modlist_swap --status` then read **UNRECOGNISED**, which looks like someone corrupting the
  owner's list. Diffed before raising it: **0 of 578 positions differ** — formatting only.
⇒ **Re-measure immediately before acting, never at the top of the session**, and diff before
you escalate.

### ✅ What landed

| | |
|---|---|
| **The planet** | 712 river edges → **238** (owner: *"1/3"*). Scald shoreline **70/79 → 1**, its outflow notch. Systems touching two seas **3 → 0**. Mycotic jungle moved onto the terminator |
| **`Inhabited`** | reversed to v1 by the owner, 8 items filed, BUILD built all of it overnight, and it **loaded clean on its first run**: `[Inhabited] ready: 2 patches, 269 characters, 0 places, 0 casts` |
| **The sled** | all three facings regenerated, 0 REJECT from `validate_sprite.py`, committed, ⛔ **undeployed** |
| **The beasts** | bantha, ronto and dewback drawn south-facing and committed; **12 composites not done** |
| **Vehicle fuel** | specced. 🔴 No XML route — `CompProperties_FueledTravel` has no filter field |

### 🔴 The root-cause find worth not re-deriving

`ashkarr_paint.py` called `flow()` twice. The erosion cycles passed `evap`; **the final call —
the one whose accumulation decides where a river IS — did not.** So no branch ever dried out,
the Scald's trunk crossed the planet, and the owner's 2026-08-19 ruling that rivers must not
connect the basins sat in the comment directly above that line for a day, doing nothing.
⇒ **A ruling written as a comment beside the code it governs is not enforcement.**

### ⏳ What this seat still owes

- `INHABITED_OPEN_QUESTIONS_1` — the four missing character fields (⭐ BUILD's improvement on
  my plan: pre-fill the review sheet **by RACE, not per person** — two dozen calls, not 269),
  the twelfth faction's cast, and three answers held until the roster soak reports.
- 🔴 **The nightside is still noise.** ~12% of the planet, and the only region that reads as
  generated rather than authored. The owner has seen it and not yet ruled.
- **Glowforest and HorrorWastes are still 0 tiles** — both authored at `ashkarr_paint.py:590`
  and `:594`, both behind noise gates that never coincide. Diagnosed, not fixed.
- The green terminator ring thinned with the rivers (`AB_FeraliskInfestedJungle` 7.1% → 2.4%).
  ⚠️ **If he wants it back, widen the riparian bands — do NOT restore the rivers**, or the
  three requirements he gave this morning come undone.

---

## 📌 SESSION HANDOFF — 2026-08-20. Read this before working the items below.

**State:** 7 live items, 1,456 lines of archive. The queue opened this session at **40 items /
1,529 lines** and every item that did not need a live game or an owner decision is closed.

### 🔴 The three things a fresh DECIDE must not re-derive

1. **The map reaches the game over the LIVE BRIDGE** (owner, 2026-08-19). Vanilla worldgen runs
   untouched, then the companion stamps all 21,872 authored tiles before any map exists.
   ⛔ Savegame writing is dead; `worldmap.py` refuses to write. `ASHKARR_WORLD_DEFINITION.md` §12.
   ⇒ **This killed the biome mix as a worldgen gate** and re-premised two design items. If
   something reads as worldgen tuning, check whether we now simply paint it.
2. **`permanentEnemy` short-circuits before the exception list** (`FactionDef.cs:463`). Ruled
   2026-08-20: the Empire's enmity becomes a whitelist, filed as
   `empire-permanent-enemy-becomes-a-whitelist-7c31d9`. ⚠️ It is a whitelist of who is NOT an
   enemy — anything absent is hostile, silently.
3. **The Rakata are the VICTIMS.** Terraformers and mega-builders, nearly wiped out by an
   assailant whose technology **rots** — which is why nobody can name them and why everything
   scavengeable on this planet is Rakatan. `the_forgotten_war.md` R-W6. ⛔ DECIDE asserted the
   opposite on 2026-08-20 and propagated it into four files before the owner corrected it; the
   wrong version is the intuitive one and is struck in place, not deleted.

### ⏱️ What is on the worldgen clock, and what is not

**ON:** B40–B54 (factions + ideos are read ONCE at world creation) · the Empire whitelist ·
`seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8` · the Worldbuilder preset
(CHECK's) · Imperial **name makers** still generate Sophian names into the shipped save.
**OFF, ruled 2026-08-20:** `pawnGroupMakers` are read at raid time, not world creation — so the
16 orphaned roster kinds can be fixed after the world is frozen. The biome mix, likewise, gates
nothing.

### 📄 `Inhabited` — the mod designed this session

`design/Jawa/bridge/INHABITED_DESIGN.md` (526 ln) · `_SPECIES_TEXTURE.md` (248 ln) · **eleven
cast files, ~300 characters, all twelve factions.** Owner's scope: **v1 for the DESIGN, v2 for
the code** — the world is built as though the people will arrive; ⛔ do not file BUILD items for
the code. The remaining DECIDE work is the placement pass onto the gazetteer.

### ❓ Open, and waiting on the owner
- `8d4c07` — the `Rule_Disallow*` set for the ScenarioDef. His principle is recorded (*a Jawa may
  not personally sow or dig; machines may do both*); the per-building judgements are not.
- `D-V2-RAIN` — spec written and measured; needs a BUILD item filing.
- Whether the Sith rumour ever hardens. **Current ruling: it never does.**


📁 **Settled items live in `infrastructure/state/queue/DECIDE_ARCHIVE.md`** — 31 of them,
moved 2026-08-19 verbatim on the owner's instruction so this file holds only live work.
Read them as records, not instructions: several carry premises the live-bridge ruling
killed.
