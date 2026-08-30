<!-- status: LIVE — the buildable engineering spec for DROID_SYSTEM_BUILD_1.
     Reopened by the owner 2026-08-29 ("We've fallen in love with the full droid
     item... fully work it out into a buildable spec... we will not build on any
     one of the packs... borrow from them and make our own... port all the
     droids in the game to that one platform").
     Design intent lives in droid_system_spec.md (unparked, still authoritative
     for WHAT); this doc is HOW. Verb decisions: droid_verbs_decisions.json
     (FROZEN). Engine evidence: droid_ruling.md. Census: droid_census_2026-08-29.md. -->

# The Droid Platform — buildable spec (v1 of the build)

## 0. The question the owner asked: build our own vs wrangle a pack

Verdict first: **build our own mechanics layer; demote all three packs to
content-and-art libraries.** "Our own mod" does not mean from-nothing — it means
the behavior DLL is ours and nothing of theirs executes, while their races,
bodies, textures and def-identities are borrowed in place wherever that is free.

### Why not wrangle each pack

| pack | what wrangling means | why it loses |
|---|---|---|
| **ABF/Synstructs** (richest; KotOR rides it) | Harmony-patch a living third-party DLL into the five-state model; amputate battery-food, top-off surgeries, its charging fictions; bolt on detonation, spikes, bolts, drift | We would still author ~60% of the C# — but as patches against someone else's moving internals. Every upstream update is a re-audit. Its states are CLOSE to ours, which is the trap: near-miss semantics (its inert states don't map 1:1 onto our 3/4/5 split) surface as subtle bugs, not crashes. |
| **Asimov/Droid Depot** | Add a power metabolism it entirely lacks; keep its bolt/wipe/reprogram | No energy need at all is not a gap, it is a different philosophy. Retrofitting the platform's core need into foreign C# is harder than owning the need. Its bolt/wipe are the parts worth stealing as *design*, and they are small. |
| **JDS (mechanoid reskins)** | Un-mechanoid a mechanoid | Not a platform. `IsMechanoid` force-kill on down is one line of vanilla IL we cannot patch away per-race without owning the flesh type anyway (droid_ruling.md §2). Conversion IS a rewrite; there is nothing to wrangle. |

### Why build wins

- **The verbs the campaign actually needs exist in no pack**: battery-proportional
  detonation, faction-keyed data spikes, bolt resentment/consequence layer,
  wipe-randomizes-and-drift, embodied-software head identity, the shop lifecycle.
  Every pack would need them added. Once you are writing that DLL, owning the
  whole state machine costs little more and removes every seam.
- **We have the toolchain**: user-local .NET build, 1-minute edit-build-deploy-test
  on the minimal modlist, JawaBench bridge verification, and our own working C#
  precedents (JawaIonWeapons DamageWorker, StrandedQuest, WreckedMachines).
- **The engine mechanics are already verified in this repo** (droid_ruling.md):
  down-vs-die is `FleshTypeDef` + `IsMechanoid`, `explodeOnKilled` fires on death
  not down, ion buildup is OUR worker with a one-line guard, the spike/bolt
  patterns are one-liners we can re-author cleanly.
- **The port cost is identical either way.** All ~80 kinds must be re-authored
  per-kind whether the platform is ours or ABF's. The platform choice only moves
  the C# line.

### The cost, honestly

ABF spent years hardening death-rewiring edge cases (caravans, transport pods,
surgery on a thing that is legally an object, storyteller targeting of pawns
with no food need). Phase 0 exists to hit those edges on a quicktest map before
any port. And the owner's earlier play-all-three-raw ruling is not wasted: the
v1 raw period is requirements capture — every annoyance logged is a spec line.

## 1. Architecture

One new mod, **`Jawa_Droidworks`** (working name; owner names it — candidates:
Droidworks, Droidbrain per the dream shortlist §28). Contents: one DLL + defs +
patches. Substrate decisions:

- **Flesh type**: our own `DW_FleshType_Droid`, `isOrganic: false` from birth.
  Supersedes the `DroidsAreMachines.xml` retro-patch for every ported race (the
  patch stays for anything not yet ported).
- **Race substrate: HAR humanlike races** (Humanoid Alien Races stays as a
  library dependency — KotOR's races already are HAR; HAR is load-bearing for
  many active mods regardless; blast radius in §6). Humanlike is what buys the
  whole sapient layer for free: traits, backstories, social, apparel slots.
  NOT Biotech mechanoid (force-kill, mechanitor, no inner life), NOT xenotype
  genes (organic machinery, wrong body/art pipeline).
- **One race per chassis family**, model variation inside the race (HAR body
  variants + per-kind art), new races only where art demands: astromech ·
  protocol · battle · utility/labour · probe/scout · heavy platform · gonk/power.
  A ported model keeps its existing race def where that race is already HAR
  (KotOR line) — see the port waves.
- **Modules are apparel** in droid-only body groups (KotOR's six-slot scheme
  embraced: hardware/software/sensor/gadget/weapon/shield), extended by a comp
  that lets a module carry personality (§3).

## 2. The five states as engine objects

| state (droid_system_spec.md §1) | mechanism |
|---|---|
| 1 Functional | normal pawn |
| 2 Transient stun | ion: our `DamageWorker_IonBuildup` with the `!IsFlesh` guard narrowed to `IsMechanoid` only (the known one-liner) + short stun stage; works *extremely well* by design |
| 3 Downed/off | buildup ≥ threshold or manual shutdown → `DW_PoweredDown` hediff: Consciousness `setMax 0.10`, **no decay** (floor stage) — stays an object until externally rebooted (doctor tend or crafter bench job). Capturable here. |
| 4 Damaged/unbootable | death by conventional damage → corpse persists; `Recipe_ShopRebuild` (bench, not field) restores from corpse if the HEAD part survives, quality scaled by `partsLeft` — the Option-B fiction at the shop, Option-A reliability in the field |
| 5 Catastrophic → detonation | `CompDroidDetonation`: on `KillFinalize`, explosion scaled by **current stored charge** (reads `Need_Power.CurLevel` × chassis energy density), never def-time capacity — "POWER DENSITY explodes, not the fact it's a machine" (owner, 2026-08-12). `chanceNeverExplodeFromDamage: 1` always (the mid-fight PostPreApplyDamage bypass destroys the corpse with no warning). Deliberate deny-your-parts modules and Gonk/KX-12 nature raise density; everyone else detonates only at genuine catastrophe |

Parts always survive tiers 4 and (partially) 5. The Forgotten Arsenal wall
stands: mechanoids are ancient self-replicating tech, no part compatibility,
not ported, not touched.

## 3. The DLL — work breakdown

Each row is a buildable unit with its own quicktest proof. Owner-facing verbs
cite the frozen decision sheet.

| # | unit | shape | borrow from | est. |
|---|---|---|---|---|
| 1 | `Need_Power` + charge cadence per chassis (combat ~daily, protocol ~monthly) | Need subclass + race comp | ABF design (room nimbus / dock / socket three-tier, sparks and glow) — reauthored | M |
| 2 | Charging buildings ×3 | ThingComps + gizmos | ABF design | S |
| 3 | Ion integration: guard narrowed, no-decay floor stage, EMP side-damage for shields, BodySize scaling | edits to OUR JawaIonWeapons + hediff XML | ourselves (droid_ruling.md §5A) | S |
| 4 | `DW_PoweredDown` state machine + reboot verbs (tend-reboot, bench-reboot) | hediff + JobDrivers | ABF inert-state design | M |
| 5 | Death rewiring for `DW_FleshType_Droid`: conventional kill → corpse w/ parts; catastrophic threshold → §2 state 5 | Harmony on `Pawn_HealthTracker` paths | ABF proves feasibility; OUR edge-case matrix in §5 | **L — the risk center** |
| 6 | `CompDroidDetonation` | ThingComp | vanilla `explodeOnKilled` + charge read | S |
| 7 | Restraining bolt: hediff (mute, ×0.75 manip, no breaks, mood aura, ALL idiosyncrasy benefits off) + **resentment accumulator that survives removal** + un-bolt-each-other rebellion jobs + shear-on-damage | hediff + comps + Harmony on `BreakCanOccur` | Asimov bolt design + `worldbuilding/restraining_bolt_technical.md` (goodwill layer, written) | M |
| 8 | Data spikes, faction-keyed: consumable, made by destructively consuming a damaged droid HEAD of that faction; touch job on downed/prisoner droid → `SetFaction` | item + `CompTargetable` + recipes | Droid Depot's one-line spike verb, re-authored with the faction key | M |
| 9 | Memory wipe: RANDOMIZES traits (not clears), clears relations/social/idiosyncrasies, faction → player; sapient deformat = murder thought/goodwill per faction ethics (§8 of design spec) | Recipe + worker | Asimov `Recipe_WipeDroid` design | S |
| 10 | Format tiers mindless/programmable/sapient/blank: one `Hediff_FormatTier`, stages gate capacities; workTags via Harmony postfix on `WorkTagIsDisabled`; needs switch (mindless: no rest/rec/morale) | hediff + 2 Harmony | ABF formatting design | M |
| 11 | Personality drift: `CompServiceRecord` — time-since-wipe accretes idiosyncrasy traits from chassis-weighted pools; long-unwiped droids are PEOPLE | comp + trait pools | exists nowhere; ours | M |
| 12 | Module personality: apparel comp granting trait-equivalent hediffs while worn (the spider-arm changes who you are) | ThingComp | KotOR slots + ours | S |
| 13 | Shop benches: repair bench (part-item bills), reassembly harness (pawn-from-parts bill; head item carries scribed identity — backstory/traits snapshot comp), overclock as a bench job (reversible, ~+15% for power/heat/mood — venue change only) | buildings + `Recipe_` workers + `CompHeadIdentity` | ABF Cradle proves pawn-from-bill; overclock numbers source-verified | **L** |
| 14 | Wild-droid faction + seek-a-master behavior; reprogram-as-recruit w/ resistance | FactionDef + pawnState-like comp | ABF `Reprogrammable` design | M |

XML content besides: races, kinds (ports), chassis part items, head items,
trait pools, research tab, faction-ethics precept/goodwill wiring.

Rough honest total: **~3–4k LOC C#, ~15 patch files, one port generator** —
phases 0–1 carry most of it.

## 4. Porting every droid in the game

Port manifest: **§7 (MEASURED census, pending fill from the sweep now running —
counts below are the 2026-08-29 census's until then: ~44 KotOR kinds, ~19 Droid
Depot, ~15 JDS, plus strays).**

The port pipeline is a **generator** (pattern: gen_turret_doctrine.py):
per source kind, emit (a) patches re-pointing race → our flesh type/comps,
(b) our kind def or a patch of theirs, (c) module loadout from its equipment,
(d) Cherry Picker keys for the amputated originals. Waves:

1. **KotOR wave (cheapest, first)** — races are already HAR. Patch race defs in
   place: fleshType → `DW_FleshType_Droid`, strip ABF comps, add ours.
   **defNames preserved → save-compatible by construction.** Backstories (19
   childhood models + 13 service adulthoods) map straight onto Assembly ×
   Service-Record.
2. **Asimov wave** — same in-place strategy: strip Asimov comps/needs, add ours.
   defNames preserved.
3. **JDS wave (only true conversion)** — mechanoid ThingDefs cannot become
   humanlike by patch; author NEW races/kinds on our platform reusing their
   art via texPath, Cherry-Picker cut the originals, re-point the Separatist
   faction kind lists. Under one frame they detonate via shield-collapse or
   deliberate module; no mechanitor control; Droideka shield becomes a
   high-power module with collapse-detonation risk.
4. **Strays** — per the census (gonk building-variant, KX-12, mouse droids, …),
   case by case on the same pattern.

**Save-compat check, done 2026-08-29**: the frozen world save scribes **no droid
pawns** (kindDef census over `world/WORLDMAP_V1_original.rws`: colonists,
animals, faction leaders only), so even the JDS new-defName wave costs nothing
in save surgery. One oddity flagged: 82 `Asimov_EnergyNeed` strings in the save
— source UNCERTAIN, check before the JDS wave. The campaign colony save at port
time will hold live droids — port waves land at a save boundary the owner picks.

The packs stay in the mod list as **asset libraries**: their art, sounds, and
(waves 1–2) their def identities. Their DLLs stay loaded but idle on ported
pawns — nothing references their comps any more. Their redundant content
(factories, kits, disks, generators) is already CUT on the frozen decision
sheet and goes to Cherry Picker.

## 5. Phase plan, each phase with its own proof

- **Phase 0 — skeleton + pilot.** Flesh type, `Need_Power`, charging, five
  states, ion integration, ONE pilot chassis (gonk: smallest and it detonates —
  exercises the whole loop). Proof on quicktest: spawn → ion-down → capture →
  bolt → wipe → kill → rebuild → catastrophic detonation scales with charge.
  **The edge-case matrix rides here**: caravan with a powered-down droid,
  transport pod, surgery-on-object, storyteller raid targeting, hungry-with-no-
  food-need, drafted at 0 power.
- **Phase 1 — verbs + shop.** Spike, bolt+resentment, wipe, format tiers,
  benches, head identity.
- **Phase 2 — port waves 1–3 + strays**, generator-assisted, one wave per
  cold-load round.
- **Phase 3 — the soul.** Drift, module personality, wild-droid faction,
  faction ethics, Free Droid Enclave goodwill layer (spec already written).
- **Phase 4 — economy/balance + residual cuts**, and the shop CUSTOMER layer
  decision (§11.3 of the design spec: own-mod vs quest pack on top).

## 6. Dependencies and blast radius

- HAR: stays (library). Synstructs/ABF: stays through wave 1 as KotOR's declared
  dependency — after wave 1 its runtime role is nil; whether to eventually cut
  it depends on the census's dependency sweep (§7).
- Licensing: we borrow **design and def-identities, never code or shipped art
  files** — art is referenced by texPath from installed mods, exactly like the
  turret pass. Nothing is redistributed.
- `DroidsAreMachines.xml` retires per-wave; JawaIonWeapons keeps its role as the
  ion authority (ion doctrine: personal ion is Jawa identity — canon.yml).

## 7. Port manifest (MEASURED — census sweep 2026-08-29, dump capture
2026-08-29T20-07-29Z at 585 mods, fingerprint-matched to live ModsConfig)

| wave | mod (packageId) | kinds | races | notes |
|---|---|---|---|---|
| 1 | Star Wars KotOR Droids (`guy762.kotordroids`) | **44** | 22 | 24 colonist/hero + 14 enemy + 6 neutral. **Pure XML, no DLL at all** — rides ABF/Synstructs entirely, so wave 1 is pure def patching |
| 2 | Outer Rim - Droid Depot (`neronix17.outerrim.droiddepot`) | **20** | 19 | 19 player-buildable + 1 escaped-battle-droid rogue. Ships `Source/` on disk |
| 2 | Outer Rim - Galactic Empire | **1** | 0 new | `OuterRim_ImperialKXSecurityDroid` reuses the Droid Depot KX race — cross-mod race reuse, port rides wave 2 |
| 2 | **our** `mandrake.jawa.patches` | **4** | 0 new | `Jawa_Droid_{Grunt,Heavy,Specialist,Leader}` on Droid Depot races, Free Droid Enclaves faction — an existing partial unified platform; ports trivially with wave 2 |
| 3 | [JDS] Separatist Droid Army | **16** | 16 | true vanilla-mechanoid pipeline (confirmed `mechWeightClass` on B1) — the conversion wave |
| | **total** | **85** | ~57 | |

**No strays exist**: gonk (`OuterRim_GNKDroid`), mouse (`OuterRim_MSEDroid`) and
the KX-12 probe (KotOR) all live inside the packs above; a full-corpus scan of
all 1,737 PawnKindDefs found no droid kind outside these five packageIds. The
"strays" wave dissolves.

**C# source availability**: ABF/SynCore — Assemblies only on disk, ABF has a
GitHub (`RWDevathon/Artificial-Beings-Framework`); Asimov — Assemblies only;
HAR — Assemblies, GitHub wiki; Droid Depot + Outer Rim Core — `Source/` shipped
on disk. Design-borrowing is unaffected either way (§6: we take design, not code).

**Dependency blast radius (active mods declaring deps)**: ABF/SynCore ← the 3
KotOR mods + our Jawa Doctrine Patches (+ FSF Complex Jobs on ABF). Asimov ←
Droid Depot, FSF Complex Jobs, Jawa Doctrine Patches. HAR ← 13 mostly
non-droid mods (shared race infrastructure — confirms HAR stays regardless).
Conclusion: **all framework packs stay installed** (as §4 planned); nothing is
ever uninstalled, only behaviorally amputated. ⚠️ Their packageIds are
capitalized (`Killathon.ArtificialBeings`) — any future dependency grep must
match case-insensitively or it reads 0.

## 8. Open for the owner

1. **Name** the platform mod (Droidworks / Droidbrain / …).
2. **Chassis race granularity** — per family (recommended) or per model.
3. **JDS Separatist identity post-port**: stay a faction of battle droids on our
   platform (recommended: they finally become capturable, which the 2026-08-13
   "never taken alive" ruling traded away for lack of a platform — reopen?) or
   keep force-kill flavor via high energy-density detonation instead.
4. **When the v1 play-raw period ends** — build starts at phase 0 regardless
   (it touches no shipped pack), port waves need the call.
