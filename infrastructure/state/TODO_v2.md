# TODO_v2.md — the v2 register

_Split out of `TODO.md` 2026-08-13 when the v1 line was drawn
(`D:\Luke\dev\Rimworld\infrastructure\state\V1_SCOPE.md`). Rewritten from 1,172
lines of argument into a register 2026-08-14._

**This is a REGISTER, not a workspace.** One compact entry per open v2 item: what it
is, who would own it, what it depends on, and whether v1 closing unblocks it. The
reasoning that produced an entry lives in the commit; the *spec* that came out of one
lives in `design/`, a skill, or the mod it belongs to — never here.

⚠️ **Do not work these while v1 is open.** If one blocks a v1 row, say so and it
moves back. **v2 starts the day v1's gate passes.**

**Closed items are one line in `infrastructure/state/CLOSED.md`, not a struck-through
block here.** Check there before re-filing anything.

---

## The register

| § | item | owner | blocked by | v1 close unblocks? |
|---|---|---|---|---|
| **0b** | Do enemies actually USE vehicles in raids? Three mods live or die on it | PROJECT | owner must identify "mother (HK Tank)" | no — offline-answerable today |
| **0c** | Alpha Neolithic reskin — the **4 vehicles after the sled** | CREATE | nothing | yes (CREATE is v1-committed) |
| **1** | Everything detonates — energy-density explosion model | unowned | nothing | yes |
| **3a** | Traps entry for the `-main`-branch `supportedVersions` trap | WORLD/OPS | nothing | no — 15 minutes, do it anytime |
| **3b** | W3 — re-scope `outer_rim_cherrypick_list.md` against the 1.6-native module | WORLD | nothing | yes |
| **3c** | W4 — can Royalty noble pawnkinds take varied alien races? | WORLD | nothing | no — offline from the def dump |
| **3d** | Four `INSPIRATION ONLY (1.4/1.5)` bullets the retraction missed | OPS | nothing | no |
| **4a** | W7 — re-cast rebel gear onto the scavenger factions | WORLD | "Junker Scrap-Warrens" has no defName | **no — needs the game up** |
| **4b** | U2 — balance-audit the live JDS droid weapons | WORLD | nothing | yes |
| **4c** | U3 — build the **Free Droid Enclaves** `FactionDef` | CREATE | worldgen (faction #5 in the spec) | yes — and it unblocks C-v3 |
| **4d** | U4 — the rare Homestead Jedi `pawnGroupMaker` | VISION+CREATE | joint Sith/Jedi build (VISION V-new) | yes |
| **5** | V2 Ideology lines — does the Jawaese actually reach Suppress/ReduceWill? | VISION | 🛑 owner STOP WORK | yes — and it needs the game up |

---

## 0b. [PROJECT] Do enemies actually USE vehicles against us?

**Owner's ask, 2026-08-12:** _"The point here is to be able to have enemies use these
against us in raids. If they can't or won't, then these three mods should be
dropped."_ **The test is binary and the owner has pre-committed to the answer.** No
partial credit — the player-facing half is not the justification.

**The three:** `smashphil.vehicleframework` · `gabrieel1482.raidvehicleframework` ·
**"mother (HK Tank)" — ⚠️ NOT IDENTIFIED. Owner: which mod is this?** No `HK`-prefixed
defName in any def type and nothing named "mother"/"HK"/"tank" in the manifest. The
other two can be assessed without it.

**Already found, and not encouraging:** `VRF_SettlementVehicleDef` has **zero defs**
in the live dump — VehicleRaid Framework's own registry of which settlements field
which vehicles, empty. ⚠️ **Do not close on that alone.** Faction Control's whole
capability lived in settings with zero defs; same trap, same day. "The def type is
empty" and "raiders never use vehicles" are different claims.

**Check offline, in order:** (1) `strings` both assemblies for `PawnsArrivalModeDef`,
`RaidStrategyDef`, `IncidentWorker_RaidEnemy`, Harmony targets; (2) look for
`Config/Mod_*_*.xml` settings; (3) does any live `PawnKindDef` or faction
`pawnGroupMaker` reference a vehicle at all — if not, settled; (4) only then put a
named log string in `NEXT_RELOAD.md`.

**Rides the same decision:** `farxmai2.vanilladeconstructablevehicles` (a VVE add-on)
— if VVE survives but the frameworks go, check whether it still has a job.

---

## 0c. [CREATE] Alpha Neolithic reskin — the four vehicles after the sled

`sarg.alphavehiclesneolithic`. **The dog sled shipped** (eopie pair, `ad3e3c7`
`2a9a004`; see `CLOSED.md` C3a). **Four vehicles remain**, each 6 files = **24 PNGs**:
**Chariot** (1 horse) · **War chariot** (2 horses) · **Covered carriage** (2 horses) ·
**Ox cart** (2 oxen).

The other seven have no draught animal — Rickshaw, Palanquin, Wheelbarrow and Hwacha
are human-powered; Balloon is `Air`; Row boat and Outrigger Canoe are `Sea`. Nothing
to reskin.

📏 **The measurement is already done and committed:**
`D:\Luke\dev\Rimworld\src\Jawa\DesertVehicleReskin\Source\GEOMETRY.md` — per-vehicle
animal bounding boxes, hitch bands, the dilate-by-8px mask rule and the 512×512
canvas facts. **Do not re-measure.**

Three numbers that live only here, kept so they are not re-derived:
- **Mask suffix is `AV_DogSled_southm.png` — `m` on the facing, NOT `_south_m.png`.**
  Applies to all 24 remaining files.
- Every facing has a paired `_m` mask for the Vehicle Framework's colour system.
  **Edit the mask in step with the art or the new animal will not tint.**
- Aspect ratios that decided the eopie: dog slot **0.57**, Eopie **0.618**, Massiff
  **0.720**. `bodySize` is a *mass* stat and does not predict sprite proportions —
  that is what made the Massiff argument wrong.

⚠️ **Reference only — do not composite.** The creature art belongs to Star Wars Animal
Collection (Continued), and lives inside a 33 MB Unity AssetBundle (`extract_bundle.py`,
needs the venv; recipe in `design/Jawa/art/graphics_overhaul_protocol.md` §2.2). Draw
from it, never paste it.

**Load `skills/generating-rimworld-sprites/` before making any PNG.**

---

## 1. Everything detonates — explosions scaled by energy density

**Owner's ask 2026-08-12; accepted, not started, no files written.** Explicitly
deferred to v2 by `V1_SCOPE.md` — *"the energy-density explosion model — large,
self-contained, pure v2."*

📄 **The spec now lives at `D:\Luke\dev\Rimworld\design\Jawa\explosion_energy_model.md`**
— the vanilla turret ladder, the shield-belt stat findings, the `PostDestroy` IL read,
the `DestroyMode` table (⚠️ `explodeOnKilled`, **never** `explodeOnDestroyed`), the
`tickerType` ConfigError, the `Turret_FoamTurret` template, the corpse/salvage IL
trace, the three tiers, the `E` curve and its proxy table, and the six pre-decisions.

**The droid half is not in that doc** — it is `design/Jawa/droid_ruling.md` §6.

**State:** the destroy-and-detonate half is **pure XML** and batches into any load.
**Shield-break venting still needs Harmony** and is the only piece that rides a load
alone. Ship the XML first.

---

## 3. The Empire

🔴 **The two-Empire fusion is STRUCK.** Owner ruled one Empire, one Emperor
(`a8768c7`, `78a0967`): vanilla `Empire` (Royalty) reskinned as the Galactic Empire,
Palpatine, the one permanent enemy, ~3 surface seats near the spaceport with the rest
orbital. The *Imperial Desert Directorate*, the *Fallen Dominion*, the
disgraced-local-aristocracy reading and any office called *Sector Director* must not
return in any doc. Canon: `design/Jawa/worldbuilding/faction_world_spec.md` §5.

⚠️ **One consequence still unpriced:** a permanently hostile Empire deletes Royalty's
progression — titles, permits, honour, imperial favour all run through this faction
being talkable-to. Almost certainly correct for a Jawa clan, but it is a whole DLC
subsystem and should be a decision, not a side effect. Owner's call; not a v2 job.

**The Outer Rim module is live and is a GEAR donor, not the faction.**
`Neronix17.OuterRim.GalacticEmpire`, WS `2919248699`, active in the 580 stack, 1.6
verified on disk. It ships the stormtrooper wardrobe (`Imp_StormtrooperCuirass` /
`Helmet` / `Pauldrons` / `Kama`), **`Imp_OfficerUniform_Black`** — the black officer
uniform the owner asked for — ISB, Death/Scout/Range/Snowtroopers, 19 Imperial
`PawnKindDef`s including `OuterRim_ImpStormtrooper_Desert`, and a 10.7 KB Harmony
assembly (solo-load waived by the owner). Full entry: `required_mods.md:604`.

⚠️ **Do NOT also load "Star Wars – Factions (Continued)" (WS 3544900066)** — it ships
its own Galactic Empire and would collide.

### 3a. [WORLD/OPS] File the branch trap — it has caught two independent passes

**The lesson is not written down anywhere.** `skills/rimworld-modding/references/`
has no entry for it, and it cost six days plus a re-derivation by a second census.

> **Never read `supportedVersions` off a GitHub `main` branch or a `*-main` zip.**
> Multi-version RimWorld mods branch per game version and this author keeps `main`
> stale. Check the **Workshop copy on disk**, or the branch matching your version.
> The control case: Outer Rim **Core** reads 1.4/1.5 on GitHub `main` and
> **1.4/1.5/1.6** in the Workshop copy we actually run.

**Generalises to:** a local, complete, file-backed artifact is more convincing than
the truth. All nine `vendor/mod_sources/Outer-Rim-*-main` extracts are stale-branch
pulls — **delete or clearly mark them**, or a third pass reaches the same wrong answer.

### 3b. [WORLD] W3 — re-scope the cherry-pick list

`design/Jawa/mods/outer_rim_cherrypick_list.md` (91 lines) is a hand-port plan whose
stated top priority is *"Empire trooper ladder + blasters + apparel + training hediffs"*.
That plan exists **only because we believed the module was unloadable**. It is
1.6-native and active, so most of §1 is dead work. **Keep §3** — Old Republic Sith as
the Empire's Sith-elite donor; that lift is still wanted.

⭐ **The defNames did not change between 1.5 and 1.6, only the filenames** — so the
SRC-verified defName list in that doc is still accurate. Nothing has gone stale; the
question is only *port vs load*.

### 3c. [WORLD] W4 — the feasibility check the docs already owe

`cherry_picker_killlist.md:82` and `required_mods.md:687` both flag it unanswered: can
Royalty noble pawnkinds be given varied alien races, or do their generation rules block
it? **Answerable offline from the live def dump.** Fallback already written down — let
varied races appear naturally rather than guaranteeing them.

### 3d. [OPS] Four stale `INSPIRATION ONLY (1.4/1.5)` bullets the retraction missed

The 2026-08-12 retraction in `required_mods.md` fixed the table, the Galactic Empire
bullet and (later) Rebel Alliance. **It did not fix `:605`–`:608`** — Galactic
Republic, Separatists, Mandalore and Old Republic all still carry
*"⚠️ INSPIRATION ONLY (1.4/1.5, SRC-AUDITED)"*, which the retraction directly
contradicts. `research/Jawa/sw_ingredients_inventory.md` still carries the old
*"DO NOT LOAD, not 1.6"* framing too. **Verify each by branch before rewriting** — the
verdict may be right for a different reason.

### 3e. Not in scope, deliberately

Player-side anything. Royalty stays non-progression (`forbidden_mods.md:86`), no player
psycasting (`:62`), and Imperial gear that out-classes vanilla rides the §19.5 balance
pass in the same lift — the enemy gets better *coordination*, never a better *curve*.

---

## 4. Ingredient verdicts — the 2026-08-12 subscription batch

**Owner subscribed six mods for evaluation and ratified these verdicts the same day.**
Kept as a register row each; the arguments are in the commits.

| mod | WS | verdict |
|---|---|---|
| Outer Rim – Galactic Empire | `2919248699` | ✅ **ADOPT** — 1.6-native, active. See §3 |
| Outer Rim – Rebel Alliance | `2919249903` | ✅ **ADOPT FOR GEAR, FACTION SUPPRESSED** — done, `5f68a9e` |
| LK Mineable Resources OR | `3565716659` | ✅ **ADOPT** — filed as `desert_world_design.md` §3B(6) |
| Outer Rim – Separatists | `3097604003` | ⚠️ **KEEP DOWNLOADED, NEVER ENABLE** — live JDS TSDA already ships `JDSCIS_CIS_Faction` with 8 `pawnGroupMakers` vs 4 and 16 droid kinds vs 9, and adds zero new droid races. Enabling it puts a second "Confederacy of Independent Systems" on the map |
| Outer Rim – Chiss Ascendancy | `2919962538` | ❌ **REJECTED, unsubscribed** — defines **zero** `GeneDef`s; the xenotype is live three times over (Galactic Diversity's `LoadFolders.xml` stands its copy down only `IfModNotActive` Csilla); 2 of 3 weapons are stat-clones and `OuterRim_CharricRifle` is a §19.5 violation (27 dmg × 2-burst at range 38 on the *rifle* cooldown base) |
| Mines 2.0 | `2503894706` | ❌ **REJECT** — filed as `desert_world_design.md` §3B(6) |
| LK Mines 2.0 compat | `3558833789` | ❌ **REJECT** — falls with Mines 2.0; also unguarded |

⛔ **The Separatist weapon lift is REDUNDANT — do not author it.** All four already
exist live in `[JDS] StarWars - Armory`: `OuterRim_E5Blaster`→`JDSA_E-5_Blaster_Rifle`,
`OuterRim_E5sSniperRifle`→`JDSA_E-5S_Sniper_Rifle`, `OuterRim_RG4DBlaster`→
`JDSA_SE-14_Light_Blaster_Pistol`, `OuterRim_BXVibroblade`→`JDSA_Vibroblade`. The
player would see two E-5 blasters in a stack already carrying 674 weapons. **U2 below
is the work that is actually owed instead, and it is the same effort.**

### 4a. [WORLD] W7 — re-cast the rebel gear onto the scavenger factions

**This is what converts a suppressed faction into a salvage layer.** Without it the
gear exists but nobody wears it. Duplicated at `queue/VISION.md` **V13** `[v2]`.

⚠️ **Three of the four premises in the original filing were wrong. Checked from disk:**
1. **The named tool is NOT installed.** WS `3635005747` (Faction Weapons and Apparel
   Set) was never subscribed — *"already adopted"* meant *chosen on paper* from a
   Workshop page in 2026-08-07.
2. **Not blocked — the documented fallback IS live.** `co.uk.epicguru.factionloadout`
   (Rimsential – Total Control: Continued), active now. `ship_deck_plan.md:201` warns
   plan B is *"more powerful but heavier"*; that trade is now the default.
3. 🔴 **Not offline-authorable through either tool** — both configure through an
   **in-game mod-settings UI**. W7 needs the game *up* and cannot be prepared as a
   patch. `Config/` holds no Total Control file, so nothing has been started.
4. **Half the target does not exist as a def.** `OuterRim_MoistureFarmers` is real.
   **"Junker Scrap-Warrens" has no defName anywhere** — it is a design-doc faction
   (`faction_roster_v2.md` §12) with no implementation vessel. Decide what it maps to
   first; `OuterRim_BinaryStarRaiders` is the only plausible candidate and **nothing
   on file says it is the Junkers**.

⭐ **Prefer the offline XML path for a small change:** `weaponTags` / `apparelTags` on
the PawnKindDef, matched against ThingDef tags and wealth-gated by the engine. Patchable
in `Jawa_Patches` today, no tool and no UI session — appropriate if W7 only ever meant
*"Homestead pawns can carry an A280"*.

### 4b. [WORLD] U2 — balance-audit the live JDS droid weapons

Two smell wrong on sight and need checking against `setting_physics.md`:
`JDSA_E-5S_Sniper_Rifle` fires a **4-round burst** (snipers should not burst) and
`JDSA_E-5_Blaster_Rifle` has **range 20** — shorter than a vanilla assault rifle, which
makes Separatist droids feel limp at exactly the range the fiction wants them dangerous.
Both are one-line `PatchOperationReplace` fixes in a mod we already load, on content the
player will actually meet.

### 4c. [CREATE] U3 — the droid faction we DO want is not in either mod

`faction_world_spec.md` §6 lists **Free Droid Enclaves** as faction 5 —
100% droid chassis, 0% biological — a *territorial* threat holding specific tiles,
hostile to the Empire because the founders were abandoned after the Clone Wars. That is
not "CIS battle droids still fighting a dead war", and **neither Outer Rim module
supplies it**.

Both candidate mods are pure XML with zero C#, and every droid race we need is installed
twice over (Droid Depot + JDS TSDA), so authoring our own `FactionDef` + thin
`PawnKindDef`s is **~200 lines and no assets**. Build it; do not adopt a substitute.

⭐ **This unblocks `queue/CREATE.md` C-v3** — the restraining-bolt spec explicitly lands
with the Free Droid Enclaves *"whose `FactionDef` is unbuilt"*.

### 4d. [VISION+CREATE] U4 — the rare Homestead Jedi

`required_mods.md:596` permits it and `desert_world_design.md` §3B(7) supplies the why.
Unbuilt: the low-weight `pawnGroupMaker` entry on the Moisture-Farmer / Homestead faction
with the curated light + telekinesis VPE loadout. `OuterRim_MoistureFarmers` is live in
Outer Rim Core, so the vessel exists.

**Spec exists:** `design/Jawa/force_users_build_spec.md`. Owner has flagged Jedi-for-
Homestead and Sith-for-Empire as **one joint build** (`queue/VISION.md` V-new), so U4
should not be built alone.

⚠️ `force_users_build_spec.md` cites this item as `TODO_v2.md:1081`. **That line number
is dead as of this rewrite** — the item is §4d/U4. Three citations to repair, at `:8`,
`:1067` and `:1072`. Not my file.

---

## 5. [VISION] V2 Ideology lines — do the Jawaese lines reach Suppress/ReduceWill?

> 🛑 **STOP WORK.** Owner, 2026-08-13: *"Deepening this is a v2 item. Let's get stuff
> working that's a blocker to play first."*

**State: NOT failing — unverified.** SpeakUp is confirmed producing glossed Jawaese on
screen; `Suppress` is confirmed firing twice with Jawa initiators onto slaves. **The
text of a Suppress entry has never been seen** — every hovered line came back
`Chitchat`. The prisoner half cannot fire at all.

**Mechanism half is CLOSED** (`CLOSED.md`, 2026-08-12): 14/14 Ideology defs carry our
rules, `Suppress` sits in `logRulesInitiator` gated `INITIATOR_kind==OuterRim_Jawa` /
`OuterRim_JawaTribal` at `priority=250`, and the `ReduceWill` InteractionDef/
PrisonerInteractionModeDef disambiguation is clean (24 rules vs 0). Source:
`D:\Luke\dev\Rimworld\src\Jawa\JawaVoice\Patches\JawaVoice_Ideology.xml`

### 🔴 The gloss is NOT a discriminator — disproven on screen

Hovering `Keetkeeh tub tub tohti te bataa. (At least the sunlight helps a little.)`
gave the tooltip **"Chitchat"**. The gloss separates JawaVoice from **vanilla**, which
was never in question, and says **nothing** about which InteractionDef sourced it.
V1 insults, V3 Chitchat and V2 Ideology lines all render in the same shape. **Scoring
V2 on the gloss produces a false pass.** RimWorld does not store the rendered line —
`PlayLogEntry_Interaction` holds `intDef` + participants and the text is generated at
*draw* time by the same rule engine for every interaction.

### ✅ The correct test — find the entry first, THEN read its text

| tooltip says | text is | verdict |
|---|---|---|
| `Suppress` / `ReduceWill` / `EnslaveAttempt` / `ConvertIdeoAttempt` | Jawaese + gloss | ✅ PASS for that half |
| same | plain English narration | ❌ real failure — `priority=250` lost its pool |
| `Chitchat` / `ChattedAboutSomeone` / `SpreadRumors` | either | ⬜ NO INFORMATION — do not score |

**Both halves must be seen; they are different interactions.** PRISONER = `ReduceWill`
(6 lines) / `EnslaveAttempt` (4) / `ConvertIdeoAttempt` (3). SLAVE = `Suppress` (4) /
`SparkSlaveRebellion` (4). 14 defs, 49 lines total.

### 🔴 Four preconditions whose absence looks exactly like failure

1. **A prisoner does NOT generate warden interactions by default.** Prisoners default to
   `<interactionMode>MaintainOnly</interactionMode>`, so `ReduceWill` /
   `EnslaveAttempt` / `ConvertIdeoAttempt` **can never fire** and their absence proves
   nothing. Set the mode per prisoner, give a colonist **Warden** work, and check there
   is at least one prisoner bed.
2. **The two halves fail for different reasons** — the slave half is a *text* question,
   the prisoner half a *setup* question. Do not report them together.
3. **The initiator must be a Jawa.** A non-Jawa suppressing a slave **correctly** gives
   a vanilla line — a pass for the gate, not a V2 failure.
4. **The game must be UNPAUSED.** SpeakUp fires on ticks; a paused game produces silence
   indistinguishable from a broken patch.

### ⛔ The save can never answer the text — do not try again

`PlayLogEntry_Interaction` serialises **no `<text>` node** — zero across 56 blocks. It
stores `initiator`, `initiatorFaction`, `initiatorIdeo`, `intDef`, `logID`, `recipient`,
`ticksAbs`. **Jawaese is never in the `.rws`**, so grepping for it returns 0 whether the
patch works or not. A save answers *whether an interaction fired and who initiated it*,
never *what it said*. Only the on-screen social log answers the text.

⚠️ `priority=250` **outbids** Core's pool, it does not replace it — vanilla lines
coexisting is expected and is evidence neither way.
