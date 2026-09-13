# GIDDYUP_KEEP_OR_CUT_1 — analysis, 2026-09-12

Item: `GIDDYUP_KEEP_OR_CUT_1`. Question: keep Giddy-Up (and Run-and-Gun) for Star Wars
mount gameplay, or cut them as bug confounders. Owner framing: worth keeping only if the
content earns its complexity AND the mod is now better written than the Roolo-era code
that "easily broke."

Note: the ledger shows two other analyses of this item already exist
(`Transient/giddyup_keep_or_cut_2026-09-12.md`, `Transient/GIDDYUP_KEEP_OR_CUT_analysis_2026-09-13.md`).
This report was produced blind to both, from disk and repo evidence only.

## 1. What is actually active

From the live `ModsConfig.xml`
(`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml`):

- **`memegoddess.giddyup`** — ACTIVE
- **`memegoddess.runandgun`** — ACTIVE
- Also active and relevant: `memegoddess.buildfrominventory`, `memegoddess.replacestuff`
  (same maintainer, unrelated function). No Roolo or Owlchemist Giddy-Up ids active.
- NOT active: `com.yayo.yayoAni.continued` (Yayo's Animation), `dylan.animalgear` — the two
  mods GU2's own `loadBefore` worries about. That compat edge is moot on this list.

## 2. Lineage (disk evidence)

Folder: `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3674332861`
(WSL: `/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3674332861`).

- About.xml: **"Giddy-Up 2 - Continued"**, author chain **"Roolo, Owlchemist, dav9670, Meme Goddess"**,
  modVersion **2.2.5**, source URL `https://github.com/MemeGoddess/GiddyUp2`, supports 1.4/1.5/1.6.
- It declares itself `incompatibleWith` **all four** old Roolo modules (`roolo.giddyupcore`,
  `rideandroll`, `caravan`, `battlemounts`) AND `Owlchemist.GiddyUp` — it is the successor, not a repack.
- The shipped patch file is literally named `Patches/patch.owlchemist.giddyup.xml` and the DLL is
  `GiddyUpCore.dll` built from shipped full source (`Source/GiddyUpCore.csproj`) with the Owlchemist
  architecture: modules folded into ONE assembly (`Core/`, `RideAndRoll/`, `BattleMounts/`, `Caravan/`,
  `SaddleUp/`), internally toggled by mod settings — not four separate mods sharing a fragile core.
- **Verdict: this is the memegoddess continuation of the Owlchemist rewrite.** The Roolo-era
  reputation ("easily break") attaches to a codebase that is two full rewrites behind what's installed.
  (Web-memory context, labeled as such: Owlchemist rewrote Giddy-Up ~1.4 for performance, using
  cached `HashSet<ushort>` def-hash lookups; memegoddess picked it up after Owlchemist left modding.
  Disk agrees: `MountableCache`/`DrawRulesCache` as `HashSet<ushort>` are in the shipped source.)

RunAndGun: folder `3562365100`, "RunAndGun - Continued", author MemeGoddess, full source shipped
(`Source/RunAndGun/RunAndGun.csproj`), same continuation family (original by Roolo — web memory).

## 3. Patch surface (from shipped source, both mods)

**Giddy-Up 2** (~35 Harmony patches, enumerated from `Source/**`):
- **Rendering/draw**: `PawnRenderer.DynamicDrawPhaseAt`, `PawnRenderer.ParallelGetPreRenderResults`,
  `Pawn_DrawTracker.DrawPos`, `PawnRenderNodeWorker.AltitudeFor`, `PawnUIOverlay.DrawPawnGUIOverlay`,
  `Thing.Rotation`. This is the riskiest cluster — it's exactly where mounted-pawn offset bugs live,
  and it touches the 1.6 parallel render path.
- **Jobs/AI**: `Pawn_JobTracker` (StartJob, DetermineNextJob, TryTakeOrderedJob,
  Notify_MasterDraftedOrUndrafted), `JobDriver` internals, `WorkGiver_Train`/`WorkGiver_TakeToPen`,
  pen/rope logic (`AnimalPenUtility.NeedsToBeManagedByRope`, `CompAnimalPenMarker.AcceptsToPen`).
- **Pathing**: `PathUtility.GetAllowedArea`, `Area.Set` — area/allowed-area shaping, not the pathfinder core.
- **Caravans**: `CaravanEnterMapUtility.Enter`, `TransferableUtility.TransferAsOne`,
  `TransferableOneWayWidget.DoRow` (mount+rider enter/leave maps together, caravan UI rows).
- **Raids/visitors**: `IncidentWorker_Raid.TryGenerateRaidInfo` + `PostProcessSpawnedPawns`,
  `IncidentWorker_VisitorGroup`, `IncidentWorker_Ambush`, `LordToil_KidnapCover` (NPC mount spawning).
- **Combat math**: `VerbProperties.AdjustedAccuracy`, `ArmorUtility.ApplyArmor` (mounted penalties).
- Shipped compat shims: `Source/Compatibility/` for AnimalApparel, WalkTheWorld (active:
  `addvans.walktheworld`), WhatTheHack; `Temporary/YayosAnimation-YesItsMe.cs` (that mod is inactive here).

**RunAndGun** (7 patches — small surface): `Verb.TryCastNextBurstShot`, `Verb.TryStartCastOn`,
`VerbProperties.AdjustedAccuracy`, `Pawn.TicksPerMove`, `JobDriver.SetupToils`,
`MentalStateHandler.TryStartMentalState`, `Pawn.GetGizmos`. Verb-pipeline patches, which is
also where CAI-5000, Yayo's Combat 3 and Melee Animation live (see §5).

Both mods ship full C# source next to the DLLs, so nothing here is UNMEASURED.

## 4. Evidence from OUR game (repo only)

- `infrastructure/state/ledger/events.jsonl`: 40 giddy-mentioning events. The substantive ones:
  - `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` — root cause independently re-verified by FOUNDRY as
    **vanilla** `BiomeDef.CommonalityOfAnimal` lazy-dictionary behavior colliding with OUR cast
    data, not Giddy-Up logic.
  - `GIDDYUP_NULLKEY_COLD_READING_1` / `COLD_LOAD_RUN_SHEET_4` ENTRY 7 — the ArgumentNullException
    at `BiomeDef.CommonalityOfAnimal` reached via `[Giddy-Up] BuildAnimalBiomeCache` traces to a
    missing `GR_Mantistanis` PawnKindDef (our data), with a next-cold-load expectation of zero
    occurrences after our fix.
- Player logs (e.g. `Transient/Player_log_before_giddyup_verify_restart_20260912.log`): the only
  Giddy-Up error line is its own **caught** handler — `"[Giddy-Up] An error occured calling
  AllWildAnimals... Skipping..."` — and reading `Source/Core/MountUtility.cs:44-60` confirms the
  eager biome sweep is wrapped in try/catch per biome and degrades by skipping. The 2026-09-12
  crashes were OUR cast-data defects that this eager all-biome cache **surfaced first. Canary, not
  culprit** — and a canary that iterates every BiomeDef at load is mildly useful to us.
- Positive live-compat lines in the same log: `[LargePawns] Giddy-Up mounted patch applied` (×3)
  and `[FacLoadout] Registered module: 'GiddyUp Mounts'` — two active mods explicitly integrate
  WITH it.
- No repo evidence of any crash, save corruption, or misbehavior attributed to Giddy-Up itself.
  RunAndGun: zero mentions in the ledger at all — but also zero evidence anyone uses it.

## 5. Compat risk vs our heavy hitters

| Mod (active id) | Overlap | Evidence | Risk read |
|---|---|---|---|
| Vehicle Framework (`smashphil.vehicleframework`) | None structural — VF pawns aren't animals; GU2 mount logic keys off animal PawnKinds/tradeTags | No cross-references in either source tree (disk) | Low |
| CAI-5000 (`krkr.rule56`) | GU2: raid/lord patches (NPC mounts) vs CAI's combat AI; RunAndGun: verb pipeline overlaps CAI's fire decisions | No cross-references on disk; web memory: no known hard conflict, both widely co-run | Medium-low for GU2, **medium for RunAndGun** (three mods stacking on Verb/accuracy) |
| Facial Animation (`nals.facialanimation` + compat project) | Head rendering vs GU2's DrawPos/render-phase offsets | `danzinagri.facialanimationcompatabilityproject` active; no GU2 reference on disk | Medium-low; symptom would be cosmetic (face offset while mounted), not a crash |
| Large Pawns (`neku.largepawns`) | Mount scaling | **Explicitly patches GU2 by name, 3 patches applied at load (Player.log)** | Handled |
| Melee Animation (`co.uk.epicguru.meleeanimation`) | Pawn draw + verb hooks | No cross-references on disk; web memory: its known conflicts are grapple/duel vs mounted pawns — cosmetic | Medium-low |
| Yayo's Combat 3 (`mlie.yayoscombat3`) | `AdjustedAccuracy` patched by GU2, RunAndGun AND Yayo | No disk cross-reference; all three are additive prefix/postfix on the same stat pipeline | Stacking penalties possible; wrong numbers, not crashes |

The genuinely scary edge (Yayo's **Animation** reordering the render tree under a mounted pawn) is
absent from this mod list.

## 6. What the content buys us (the scenario side)

This is a Jawa scavenger clan on a hand-authored desert planet where **caravan travel is core
gameplay**, and the bestiary was chosen for riding: banthas, dewbacks, rontos, eopies
(`mlie.starwarsanimalcollection` active, plus our per-animal art-override mods). GU2 is the only
mod in the stack that makes those animals mountable — on-map riding, mounted caravans (speed from
mounts via `giveCaravanSpeed`), and mounted raiders/visitors (a Tusken-raider-on-bantha moment is
free flavor from `enemyMountChance`). Cutting it turns the signature fauna into pack mules.
Everything is settings-gated per module (RideAndRoll / BattleMounts / Caravan / mount chances /
body-size filter), which fits the MOD_OPTIONS_RETROFIT_1 doctrine: keep the mod, trim the dials.

RunAndGun buys much less here: move-and-shoot for colonists/raiders. Star Wars flavored, but no
animal/caravan tie-in, and it triples the crowd on the verb pipeline that CAI-5000 already owns.

## 7. The cards

---
**CARD A — KEEP BOTH, AS-IS**
Everything on: riding, battle mounts, mounted NPCs, run-and-gun.
*Trade: maximum flavor for maximum patch surface — ~42 Harmony patches across rendering, jobs,
raids and verbs stay live, and every future oddity in those areas has two more suspects.*

**CARD B — KEEP GIDDY-UP, TRIM THE DIALS; CUT RUN-AND-GUN**
Keep GU2 for riding + mounted caravans + mounted NPC raiders. In its settings: leave Caravan and
RideAndRoll on, review BattleMounts and visitor/enemy mount chances with the owner, set the
body-size filter so only the big four ride. Deactivate `memegoddess.runandgun`.
*Trade: we keep the content the scenario was built around and drop the one mod with no desert-planet
payoff; cost is one settings session and losing move-and-shoot in fights.*

**CARD C — CUT BOTH**
Deactivate both. Banthas and dewbacks remain as pack/farm animals only.
*Trade: smallest possible bug surface; cost is the scenario's signature gameplay — nobody ever
rides a bantha on the planet we hand-built for riding banthas.*
---

## 8. Recommendation

**CARD B.** The owner's fear was calibrated on Roolo-era code; what's installed is two rewrites
newer (Owlchemist architecture, memegoddess-maintained, v2.2.5, full source, active on 1.6, shipped
compat shims, and two of OUR active mods integrate with it by name). Our own ledger shows zero
defects caused by it — the 2026-09-12 crashes were our cast data, with Giddy-Up as the canary that
found them, inside a try/catch that degrades instead of dying. The content is not generic garnish
here: riding IS the point of this bestiary on this planet. RunAndGun is the opposite case — small
mod, but its whole surface sits on the verb pipeline CAI-5000 and Yayo's Combat already contest,
for a feature nobody has cited in any log or ledger entry. Keep the one that carries the scenario,
cut the one that only carries risk.
