# MACBENCH_REBOOT_HANDOFF_202609240211 — READ FIRST on wake

Follows `MACBENCH_REBOOT_HANDOFF_202609240027`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

🔑 **Reading the source before designing was the highest-yield action of this session FOUR separate
times — and once it converted an owner ruling from "build a system" into "refine one method".**

The tally, all one sitting: the warden mother's anchor/defend/wander AI was already built
(`RM_CompTerritorialAnchor` + `RM_AnchorGuard`); the stranding pools were already built; the surge
and gradient axis were already built; and when he ruled that a canal must let her swim *"as long as
it connects to the sea"*, **that predicate had been shipping since 2026-09-14** —
`RM_MapComponent_StrandingPools` flood-fills the map's water cells into connected components (4-way),
keeps the largest as the main network, and exposes `IsReconnected()`. **Swim-eligibility IS that
predicate.** A session that designed first would have built a second connectivity system beside a
working one.

⇒ Reading it also **unified two halves of the design I had been treating separately**: a stranded
young is simply *a young in water that lost its connection*. Same test, both directions. That came
from the code, not from the conversation.

🔴 **And the inverse of the same rule cost a retraction this session.** I wrote that
`RUT_WardenMother` ships. **It does not exist** — the name lives only as an **XML example inside a C#
comment**, so every grep hit was documentation. That claim reached two committed documents before it
was caught. The trap is one `CLAUDE.md` already names: **an existence test is not an identity
test.** ⇒ When a name resolves, check *what kind of thing* resolved.

## What the owner should see

1. 🔴 **A real defect in shipped code, found by his own wording.** `RM_MapComponent_StrandingPools`
   tests open water as *"reaches the map edge"* — and its own header is honest that this is a proxy.
   But on a Miasma map **the fresh end touches the map edge too, because the rivers do.** So a canal
   dug to a river mouth reads as "connected to the sea", and a brine-broken **sea** elder could swim
   inland up fresh water. He said *the sea*; the code says *any edge*. ✅ Fix needs no new machinery
   — `RM_GradientAxisExtension` already knows which direction is brine, so it becomes *"reaches the
   **seaward** edge."* Owed in `WARDEN_MOTHER_BEFRIENDING_1`.
2. 🔴 **One gate could make the whole canal section fiction: do FlowWorks' canal cells register as
   water-band cells in that flood-fill?** If not, canals are invisible to every mechanism designed
   around them. UNMEASURABLE on the Mac — Desktop, and it should be measured *before* any of §6b is
   built.
3. ⚠️ **He named "the Earth Flow mod" and no such mod is in the active list** — checked the newest
   snapshot (2026-09-19, **621** active mods); the only canal engine there is ours,
   `mandrake.rm.flowworks`. He then confirmed *"FlowWorks"*, so this is settled — but ⚠️ the **live**
   list is a Windows path unreachable from the Mac, so a laptop claim about it stays UNMEASURABLE.
4. ⚠️ **I corrected the frozen sheet twice and a campaign doc once, on his rulings** — worth his eye
   because the edits are mine: `the_miasma.md` §4's *"stationary"* and *"never random spawns"* are
   superseded, and *"the reason ships sink"* became *"why nobody goes out onto the open water"* since
   the world has no nautical ships. `CAMPAIGN_ARC_GATHER.md` G34 carried the stale phrasing and also
   stops being a campaign `GAP`.
5. ⚠️ **Still open from the previous handoff and NOT re-raised with him:** the attar is given a plant
   rather than the terrain its sheet implies; `RM_Brathek`'s digging rate is unset and is the most
   consequential missing number; `RM_Ismerrow` is only worth building if it can be colour-randomised;
   `RSW_Porg` probably fails his own "not parrots" brief. All five are in that handoff's §2.
6. 🔴 **98 live biome rows still name the bare donor for 73 creatures we already ported**
   (`MLIE_ABSORPTION_BIOME_WIRING_1`), so the campaign still hard-depends on that mod and 73 ported
   creatures spawn nowhere. Deliberately not swept — he stopped sweeping roster changes 2026-09-22.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `WARDEN_MOTHER_BEFRIENDING_1` — **fully designed across five owner rounds this sitting, ZERO built.** The biome's centrepiece; roster §6/§6a/§6b is the authority; NEXT: on the **Desktop**, measure the three gating engine questions before writing any code — (a) do FlowWorks canal cells count as water-band cells in `RM_MapComponent_StrandingPools`' flood-fill, (b) can a pawn's pathing be constrained to a terrain set at all, (c) does the `mindState.duty` seam behave on a non-insect ThinkTree.
- ⚠️ **The `mindState.duty` trap is the one that will silently eat this feature** — `RM_AnchorGuard.xml`'s own comment records that vanilla's plain Animal ThinkTreeDef does **not** consult duty, only insect-shaped trees do; NEXT: **decide her ThinkTreeDef before her ThingDef** — a warden mother on a plain Animal tree wanders off, defends nothing, and reads as correctly configured.
- **Seaward-edge refinement of `IsReconnected()`** — specified, not written; NEXT: change the open-water test from *any* map edge to the **seaward** edge using `RM_GradientAxisExtension`, and ⛔ do not write a second connectivity system to do it.
- `MIASMA_FLORA_ROSTER_1` — 19 plants authored, art search discharged, **zero defs, zero art**; NEXT: author the four mangal `ThingDef`s first (§3) — they replace the donor canopy, which is what `mandrake.rm.miasma` needs to stand alone at all.
- `MIASMA_FAUNA_FLOOR_ROSTER_1` — 5 creatures + the stranded mechanism specified, nothing built; NEXT: **read `RM_CompVerminBreeder` + `RM_MapComponent_VerminPopulation` before writing any C#** — a scuttler population drawn down by five plants, a harvest and every predator is what a vermin-population component already is.
- `SEA_BEASTS_TIER_RULING_1` — **RULED, reassigned to FOUNDRY, needs=offline, nothing built**; NEXT: on the **Desktop**, rename the 11 invented sea beasts **and their juveniles** from `RSW_` to `RM_` and repoint every leather/meat/egg/sound/`wildBiomes`/biome-cast reference — ⛔ a retier MOVES creatures and removes none, and the final-concept mockups are not re-rolled.
- `FEVERWOOD_SAP_SUCKER_GUILD_1` — cast named in `fever_wood_fauna_roster_2026-09-23.md`, no defs; NEXT: build the nectar contract on `RM_CompGatherableCalmGated`, which already compiles — ⛔ not `CompProperties_HasGatherableBodyResource`, which has zero precedent here.
- `FEVERWOOD_ALIEN_BIRD_CHORUS_1` — four birds named with one role each, nothing built; NEXT: give `RM_MapComponent_SilenceCue` a public "hush now" entry point, the exact gap the sitting recorded.
- **The Miasma's §7 economy defs are still unauthored and no item owns them** — attar refinement, delta loam, arthropod harvest, flotsam tables; NEXT: **file one item for the four §7 trade goods**, citing `miasma_flora_roster_2026-09-23.md` §6 for which plant feeds which.
- ⚠️ `MIASMA_MECHANICS_1` — M1–M6 built; its only open boxes are **in-game verification**; NEXT: on a Desktop cold load, quicktest a **scratch** world tiled to the Miasma and confirm forced miasma weather with no rain, then tick the boxes or record what failed.
- ⚠️ `KORRUM_ART_REGEN_1` / `STONEBACK_BOKKA_ART_STANDARD_1` / `ROSTER_DEAD_BMT_NAMES_SWEEP_1` — **still deliberately not carried.** All three are Desktop-gated and their own item text says carrying them as pending decisions is wrong behaviour; NEXT: **leave them until a Desktop session** — ⛔ do not re-inherit them into a Mac handoff a seventh time.

## Traps learned

1. 🔴 `block_forged_owner_said.py` **refused a quote he genuinely typed this session** — his sentence contained an apostrophe and parenthesised text and the transcript check did not match it. Took the guard's prescribed exit: dropped the flag, filed under BENCH, recorded the attribution in the item prose instead (filed: LESSONS).
2. 🔴 A name that resolves is not a thing that exists — `RUT_WardenMother` is an **XML example inside a C# comment**, and two documents asserted it ships (see: `CLAUDE.md > Instruments that return a confident wrong number`, the existence-vs-identity entry).
3. ⚠️ A frozen sheet can hold an image that is **false for this world** rather than merely stale — *"the reason ships sink"* in a world with no nautical ships. ⇒ Check a metaphor against the setting, not just against other docs (filed: LESSONS).
4. 🔴 The ledger rebase conflict recurred **twice more** this sitting and the git-plumbing method handled both, keeping a concurrent BENCH window's events intact each time (see: `CLAUDE.md > Git`).
5. ⚠️ zsh not word-splitting an unquoted variable, and the sanity-probe rule that catches it — already recorded and it held up (see: `CLAUDE.md > Instruments that return a confident wrong number`).

## Commits

```
497b0efed Connection to the sea is the gate, and that predicate shipped nine days ago
fa4e3358a No ships to sink, no time to grow up, and canals make her reach the player's
8e666ea10 She dies of age, and the young she could not reach inherit her
e3fb906aa chore: health publisher artifacts regenerated
435553401 The warden mother cannot reach her own young, and that is the whole mechanism
c29c8cec9 Bridge release: batch live-verify pass complete (items 1-8 + 11 real work, item 10 partial, item 9 untouched -- needs a multi-restart bisection out of scope for this session).
5c1aa709d MOD_OPTIONS_RETROFIT_1: live spot-check of 8 mods' Mod Settings (all 3 tiers) via jawa/mod_settings_field -- all 8 resolve cleanly, 5 round-trip toggle-verified. Real evidence the retrofit's settings layer is sound; not a full 46-mod census.
6e8f79dcd BARBSLINGER_SCORPION_REDESIGN_1: attempted live combat test, inconclusive (defenseless test colonist fled before engagement). Discovered and recorded a real bridge-tooling gap: jawa/pawn_use_verb cannot see/fire CompTurretGun-owned verbs at all (separate verb tracker from pawn.VerbTracker), relevant to any future turret-gun creature testing.
40d54e0b2 SEA_FLOOR_AND_CATCH_PASS_1: record that (a)-(c) shipped as mandrake.rm.seashores (fb352d7c6)
fb352d7c6 SEA_FLOOR_AND_CATCH_PASS_1: mandrake.rm.seashores — our seas become real coasts (mutator, IsCoastal, sea-keyed catch)
caa1f043d WYYYSCHOKK_FANG_PENDANT_1: three different attempts to produce a live trader on the campaign map to test the fang pendant's sale, all failed for different reasons (fire_incident silently doesn't fire; debug action produces no pawns; forcing the wrong pawn NREs inside a third-party trade mod). Trade-sell claim remains unconfirmed; documented why for the next pass.
1e7c1a305 Ledger sync: DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave note (9 files clean, 1 fix)
f83ed91c5 CODE_REVIEW_STATUS sync: 9 files marked CLEAN (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave)
f34c32a99 vivify_world.py: drop dead if-False ternary in diff()'s sort key
28b1fe9a8 WAR_LAB_CRATER_HOOK_1: first live proof of the ignition->crater mechanism on the real Ash'karr world (owner-authorized 2026-09-13). 57/57 propane lake tiles flipped correctly, 0 unexpected, confirmed persisting across a real save/load cycle on a separate test save. Idempotency and map-not-loaded edge cases remain untested.
a93a2b800 Remove closed item's old-path prose (moved to items/closed/ by rimflow close)
6ae07b0ce Ledger sync: close DUPLICATE_CANON_DEFNAME_PAIRS_1, file STARWARS_DONOR_PORT_LABEL_COLLISIONS_1
7562e534e DUPLICATE_CANON_DEFNAME_PAIRS_1: merge gizka/kreetle/nuna/worrt onto their RSW_ ports
1e43270da DIRTY_CODE_REVIEW_STANDING_LOOP_1: ledger sync, resume-wave note
28be4e7c0 DIRTY_CODE_REVIEW_STANDING_LOOP_1: mark CLEAN RM_MirrorPoolBiomeExtension.cs + RM_GenStep_ScatterPools.cs
... 21 more: git log --oneline e8fa2f86f..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M Transient/codebase_health.html            MACBENCH — generated by the health publisher; superseded, see below
 M Transient/codebase_health.json            MACBENCH — generated; superseded
 M Transient/codebase_health_artifact.html   MACBENCH — generated; superseded
 M infrastructure/dashboards/hub/data/health.json   MACBENCH — generated; superseded
 M infrastructure/state/codebase_health_last.json  MACBENCH — generated; superseded
```

⚠️ **The five lines above are the tree as it stood when the skeleton was written, not at wrap.**
All five are the health publisher's own output — `code_review_status.py` spawns it on every
`prune`/`list`, and rimflow calls trip it — so they are generated, never hand-edited.

**What actually became of them, recorded because it is the honest account:** I committed them, then
a concurrent BENCH window pushed a *newer* regeneration of the same five files. The rebase conflicted
on all five, and since generated output contains no authored work my commit was **redundant — so it
was skipped** (`git rebase --skip`) rather than overwriting either side. ⇒ The versions on `main` are
that window's, which are at least as new. ⛔ An earlier draft of this section cited my skipped
commit's sha; that object is unreachable from `main` and a fresh clone cannot resolve it, so the
reference is removed rather than left to rot.

🔑 **Worth carrying:** when a rebase conflicts *only* on generated artifacts, `--skip` is the right
resolution — it is the one option that discards nobody's work, because there was none to discard.

**At wrap, the only uncommitted files were MACBENCH's own and both are in this handoff's commit:**
`infrastructure/state/LESSONS_INBOX.md` (two lessons appended this session) and this handoff file
itself. Nothing of another agent's was touched, and nothing is left on disk only.

