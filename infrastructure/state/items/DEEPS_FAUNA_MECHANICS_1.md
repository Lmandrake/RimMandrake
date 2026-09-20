## spec

Owner's own words (verbatim, from the filing, 2026-09-19):

1. **Grabber** (ex-BovineBeetle, bodySize 4): "Give it great strength to
   Hold someone with its pincer and slowly crush them each round" — a
   grapple: target immobilised + recurring crush damage each round until
   freed or killed.
2. **Soulchime** (ex-FacetMothLarvae): "builds armor out of crystal shards
   it collects along the ground. Emits a powerful psychic stun on anyone
   that gets too close and alarms it. Taming one produces a soothing
   effect on those around it." — three parts: (a) crystal-shard
   armor-building behavior, (b) a proximity psychic stun when alarmed, (c)
   a soothing aura once TAMED (owned by a colonist).
3. **Drinker** (ex-BloodropMoth): "sacks that it uses to store drained
   body fluids. Strangely, if it drains any day-side races with normal
   warm iron blood, it becomes poisoned and rapidly dies." — fluid-drain
   storage mechanism + a species-conditional poison-and-death trigger.

Build location: `mandrake.rm.creaturebehaviors` (content-blind comps +
extensions), matching the WoundLink/KinMending/PlantAlarm idiom already in
that assembly. Mod Settings toggle per mechanic. Attach onto the actual
SWBestiary defs. Proof method named in the filing: "quicktest per
spawn-many-for-bridge-tests" (a LIVE bridge criterion) — explicitly NOT
done this pass; build + offline-verify only (compile clean, defs
validate), bridge untouched.

Sibling item `DEEPS_FAUNA_VERDICTS_1` landed the renamed creature defs
these mechanics attach to (`a00f52f10`).

## status log

- 2026-09-19 — read `CreatureBehaviors/Source` in full for the existing
  idiom (`CompProperties_WoundLink`/`RM_CompWoundLink`,
  `CompProperties_KinMending`/`RM_HediffComp_KinMending`,
  `RM_CompPlantAlarm`/`RM_AlarmResponderExtension`) and the Mod Settings
  file (`RM_CreatureBehaviorsMod.cs`) for the toggle pattern. Confirmed via
  RimSage (this session, on the Desktop — RimSage reachable) that
  `DamageDef.additionalHediffs` (`Verse.DamageDefAdditionalHediff`) is a
  pure-vanilla, zero-Harmony way to deliver a hediff to a bite/strike
  victim on a successful hit, and that `Hediff.PostAdd(DamageInfo? dinfo)`
  receives `dinfo.Instigator` — the attacker — letting a hediff identify
  who hit it without any custom `Verb` subclass. Precedent for the whole
  ToolCapacityDef+ManeuverDef+DamageDef delivery trio:
  `UtinniPatches/Defs/ToolCapacityDefs/RUT_FlamefangBite.xml` +
  `DamageDefs/RUT_FlamefangVenomBite.xml`.

- **BUILT — Grabber (hold + crush), fully.**
  - `RM_HediffDef_Grapple` (custom `HediffDef` subclass,
    `Source/RM_HediffDef_Grapple.cs`): tuning
    (`severityGainPerRoundPerBodySize`, `roundIntervalTicks`,
    `escapeChancePerRound`, `releaseRadius`) lives on the hediff def, not a
    `DefModExtension` — this tuning belongs to the HEDIFF, not the race.
  - `RM_Hediff_Grappled` (`Source/RM_Hediff_Grappled.cs`): `PostAdd`
    captures the grappler from `dinfo.Instigator`; `Tick()` releases the
    hold (removes itself) if the grappler dies/downs/despawns/leaves
    `releaseRadius`, or if the mod setting is off; each round, an escape
    roll can free the victim outright, otherwise the hediff's OWN severity
    climbs (scaled by the grappler's `Pawn.BodySize`) toward its
    `<lethalSeverity>1</lethalSeverity>` — vanilla's own
    severity-crosses-lethal kill, so a hold pressed all the way through
    genuinely kills the victim with zero extra code. Deliberately does
    NOT call `Pawn.TakeDamage` from inside its own `Tick()` — that would
    risk re-entering the victim's own HediffSet tick loop mid-iteration,
    the same hazard `RM_CompWoundLink`'s header already flags for a
    sibling mechanism. Three escalating stages (capMods on
    Moving/Manipulation/Breathing/Consciousness) so the hold visibly
    worsens in the health tab.
  - Delivery: `RM_PincerCrush` DamageDef (no Name-attributed vanilla
    "Crush" to `ParentName` off — RimSage-verified — so it stands alone
    with Crush's own fields) + `RM_PincerGrapple` ToolCapacityDef/ManeuverDef
    routing through `Verb_MeleeAttackDamage`.
  - Wired onto `RSW_BovineBeetle` (Grabber) directly in
    `RSW_BiomesTeamPort_Races.xml` (SWBestiary's own content, no patch
    needed — same direct-edit precedent as RotSporeKit's
    `RUT_Emberscythe.xml`): a new "pincer" tool
    (`RM_PincerGrapple`, power 22, chanceFactor 0.5), and the race's
    `<body>` switched from vanilla `BeetleLike` (no claw part at all) to
    vanilla `BeetleLikeWithClaw` (a real `HeadClaw` body part group,
    already the body plan three sibling absorbed creatures in the same
    file use) so the pincer has somewhere to attach.
  - Settings: `grapplerHoldEnabled` (master) + `grapplerCrushMultiplier`
    (rate dial, scales only the per-round severity gain).

- **BUILT — Drinker (fluid sacs + wrong-blood poison), fully.**
  - `RM_CompProperties_FluidSacs` / `RM_CompFluidSacs`
    (`Source/RM_CompProperties_FluidSacs.cs`, `RM_CompFluidSacs.cs`):
    attach to the DRINKER's own race. `Notify_Fed(victim, severity)` is
    called by the marker hediff below; if the victim's
    `RaceProps.FleshType` is in `poisonousFleshTypes` (defaults to
    vanilla `FleshTypeDefOf.Normal` — humans and virtually every vanilla
    mammal/bird — the generic, already-available stand-in for "day-side
    races with normal warm iron blood"), it applies `poisonHediff`
    (`RM_FluidSacPoison`) to itself instead of feeding; otherwise it
    restores `Need_Food.CurLevel` proportional to how much was drained.
  - `RM_Hediff_Drained` (`Source/RM_Hediff_Drained.cs`): a silent marker
    hediff, `PostAdd` reads `dinfo.Instigator` and calls
    `attacker.TryGetComp<RM_CompFluidSacs>()?.Notify_Fed(...)`, then
    clears itself a tick later (`HediffCompProperties_Disappears`, same
    idiom as `RUT_MatGrip`). A harmless no-op for any attacker without the
    comp.
  - `RM_FluidSacPoison` (HediffDef, generic): fast, uncurable
    (`tendable: false`, no Immunizable), `HediffCompProperties_SeverityPerDay`
    pushing it to `lethalSeverity` well under a day — "rapidly dies".
  - Wired: added `RM_CompProperties_FluidSacs` to `RSW_BloodropMoth`
    (Drinker)'s `<comps>`; added a second `<li>` (`RM_Drained`) to the
    ALREADY-SHARED `RSW_BloodSuck` DamageDef in
    `RSW_BiomesTeamPort_Support.xml` (also used by the cut
    `RSW_BloodropLarvae` — harmless no-op there, it has no
    `RM_CompFluidSacs`).
  - Settings: `drinkerFluidSacsEnabled` (master) + `drinkerPoisonMultiplier`
    (0 = a bad bite is simply never fed, same as any other unwanted meal).

- **BUILT — Soulchime (b) proximity psychic stun + alarm, fully; (c)
  tamed soothing aura, fully; (a) shard armor, SIMPLIFIED.**
  - `RM_CompProperties_ProximityPsychicStun` / `RM_CompProximityPsychicStun`:
    scans for pawns within `radius` on a cooldown; applies `stunHediff`
    (wired to vanilla `HediffDefOf.PsychicShock` — a real, ~2-hour,
    Consciousness-capping condition already in the base game, not an
    invented one) to anyone too close whose faction doesn't match the
    carrier's own. A WILD carrier has no faction, so this stuns everyone
    including a wandering colonist, matching "anyone that gets too
    close"; a TAMED carrier's own colonists are exempt (soothed instead,
    see below). On a successful stun, also rings the carrier's own
    `RM_CompPlantAlarm` (reused as-is, un-tagged so it wakes any
    `RM_AlarmResponderExtension` carrier in range) — "alarms it" reuses
    the Rot's existing network-alarm mechanism rather than inventing a
    second one.
  - `RM_CompProperties_TameSootheAura` / `RM_CompTameSootheAura`: only
    acts once `Faction == Faction.OfPlayer`; grants a generic
    `RM_TameSootheThought` memory (`Defs/ThoughtDefs/RM_TameSoothe_Thoughts.xml`,
    +3 mood, stacks 1, decays over a day) to every colonist within
    `radius`. Content-blind and reusable by any future tamed-aura
    creature.
  - `RM_CompProperties_ShardArmor` / `RM_CompShardArmor`: grows an
    `RM_ShardArmor` hediff's severity (plain `HediffWithComps`, ordinary
    `<stages><statOffsets>` for `ArmorRating_Sharp`/`Blunt`, three
    thresholds) on a slow interval, capped, while the carrier is
    unroofed. **This is a SIMPLIFIED stand-in for "collects crystal
    shards ALONG THE GROUND"** — it does not spawn or forage any physical
    shard item; it approximates the player-visible outcome (armor
    visibly thickens over time, capped) without a new ground-clutter
    resource def or a JobGiver to seek it out. **OWED**: a real version
    needs (1) a pickable "crystal shard" Thing scattered on Deeps
    terrain, and (2) a JobGiver making Soulchime path to and collect one,
    consuming it for the severity gain instead of a bare timer. Neither
    exists yet and neither was attempted this pass — flagged as the one
    piece of the three-part Soulchime ask that is a real approximation,
    not the literal mechanism.
  - Wired: all four comps (`ProximityPsychicStun`, `PlantAlarm` reused,
    `ShardArmor`, `TameSootheAura`) added to `RSW_FacetMothLarvae`
    (Soulchime)'s previously-empty `<comps>` block.
  - Settings: `soulchimePsychicStunEnabled` (master); `soulchimeShardArmorEnabled`
    + `soulchimeShardArmorRateMultiplier`; `soulchimeTameSootheEnabled`.

- SWBestiary's `About.xml` `loadAfter` gained
  `mandrake.rm.creaturebehaviors` (same precedent as its existing
  `mandrake.rm.proximityhatch` entry, for the same reason: it now
  references that mod's C# classes by name from XML).

- `dotnet build ... -c Release`: **0 warnings, 0 errors** (two missing
  `using RimWorld;` directives caught and fixed by the first build
  attempt — `FleshTypeDef`, `ThoughtDef`).

- `validate_patch.py` over `CreatureBehaviors/Defs/` +
  `RSW_BiomesTeamPort_Races.xml` + `RSW_BiomesTeamPort_Support.xml`
  against the live 621-mod set (RimWorld install + Mods + Steam Workshop
  content, all three roots needed for the load set to resolve): **0
  errors**, 3 pre-existing warnings (an unrelated `RSW_Yooka` texPath,
  already known-benign). Caught and fixed two real defects first: three
  `<!-- ... -- ... -->` XML comments (illegal double-hyphen inside an XML
  comment, would have broken the WHOLE file) — replaced with em dashes.

- Deployed: all CreatureBehaviors XML/About files (`deploy_custom_mods.py
  --mod CreatureBehaviors --apply`, 8 files, byte-verified). The
  compiled `Assemblies/RimMandrake.CreatureBehaviors.dll` did **NOT**
  deploy — the deploy tool reported it locked (the game process is
  presumably holding the file open), a known limitation ("a companion
  DLL cannot be written while the game runs"). SWBestiary's three edited
  files (`About.xml`, both `RSW_BiomesTeamPort_*.xml`) were copied
  directly rather than via `--apply`, because a `--mod SWBestiary` plan
  also showed drift on several OTHER files not touched this pass
  (`ThingDefs_Onnik.xml`, `SeaBeasts_NurseryJuveniles.xml`,
  `Waterline_Lane1.xml`, `RimMandrakeLivestockRSW.dll`) — another
  window's live/uncommitted state, same situation `DEEPS_FAUNA_VERDICTS_1`
  already hit and handled the same way. All three direct copies
  byte-verified identical to the repo.

- **OWED, explicitly, regardless of how much was built:**
  1. **Live-quicktest proof** (per `spawn-many-for-bridge-tests`) for all
     three mechanics — none of this was checked against a running game
     this pass; the bridge was not touched at all, per the task's own
     instruction.
  2. **Deploy `RimMandrake.CreatureBehaviors.dll`** to the live Mods
     folder — blocked by a file lock this pass; needs a moment when the
     game isn't holding it (or a restart).
  3. **Soulchime's shard-armor foraging loop** — the real "collects
     shards ALONG THE GROUND" mechanism (a ground-clutter shard Thing +
     a JobGiver), not the passive/capped timer built this pass.
  4. Tuning throughout is INVENTED (marked as such in each file's own
     comments) and unverified in play — round intervals, escape chances,
     stun radius/cooldown, hunger-restore/poison rates, soothe mood
     amount. A live pass should re-check all of it against how the
     fights/taming actually feel, not just that it compiles.

## north star

(none filed — this is a mechanics build, not a bar-gated content mod.)

---

## ⚠️ LIVE TEST 2026-09-19 (FOUNDRY, overnight full-621-mod batch) — mechanics did NOT
observably fire live; NOT closing, new finding for whoever owns the next pass

`CreatureBehaviors` deployed clean (assembly + XML in sync, confirmed via
`deploy_custom_mods.py`). Confirmed via `jawa/get_defs` that all four comps ARE
correctly wired on the live defs: `RSW_BovineBeetle` carries
`RM_CompProperties_Grappler`, `RSW_BloodropMoth` carries
`RM_CompProperties_FluidSacs`, `RSW_FacetMothLarvae` carries
`RM_CompProperties_ProximityPsychicStun` + `PlantAlarm` + `ShardArmor` +
`TameSootheAura` — the defs load clean with the comps attached, nothing threw
building or spawning them.

**But the actual mechanics did not visibly trigger in a real live test.** Spawned 3x
each creature (faction `none`) + 6 human test pawns nearby, issued repeated
`jawa/ordered_job AttackMelee` (grabber/drinker → victim) and `Goto` (victim → next to
soulchime), stepped the game **~2000 ticks total** via `rimworld/step_game_ticks`
(explicit paused-mode stepping — the first attempt relied on `waitTicks` on an
ordered job while the quicktest was still paused and silently advanced 0 game ticks;
caught and corrected before drawing any conclusion from it):

- **Grabber**: never landed a single hit on its victim in 8 retries over ~2000 ticks
  (victim's hediff list never changed at all) — `RM_Grappled` never appeared.
- **Drinker**: DID land hits (3 separate `Bruise` wounds accumulated on Arm/Leg/Torso
  across retries), but every hit was generic `Bruise` (Blunt), never a
  `Bite`/`RSW_BloodSuck`-tagged hit — so `RM_Hediff_Drained`/`RM_FluidSacks`/
  `RM_FluidSacPoison` never appeared on victim or attacker. Consistent with the moth's
  own multi-tool RNG simply not drawing the modded tool in this sample, not
  necessarily proof the path is unreachable.
- **Soulchime**: victim was walked onto/adjacent to the soulchime's own cell and left
  there ~2000 ticks (well past any plausible cooldown); no `PsychicShock` ever
  appeared. More concerning than the tool-RNG story covers, since
  `CompProximityPsychicStun` is an automatic proximity scan, not melee-RNG-gated.

**Disposition**: not proven broken — the sample used non-hostile `faction: none` wild
pawns driven by `jawa/ordered_job`; between orders their own AI (`GotoWander` was
observed overriding a queued `AttackMelee` at least once) may interfere with sustained
combat in a way a drafted/hostile pawn would not. But it is also not a live PASS: zero
of the three mechanics fired even once in ~2000 ticks of dedicated attempts. **Leaving
`doing`, not closing.** Owed for whoever picks this up:
1. Retest with an actually-hostile/manhunter creature, or a drafted colonist attacking
   a tamed Grabber, to rule out the ordered-job/non-hostile-AI interference explanation.
2. Read `RM_CompProximityPsychicStun`'s actual default `radius`/`cooldownTicks` (not
   read this pass) — a smaller-than-assumed radius or longer-than-2000-tick cooldown
   alone would explain the soulchime non-result with no code defect.
3. A hostile-pawn retest still showing zero Grabber hits is the strongest signal of a
   real defect — three-tool selection odds should not be that low across 8 attempts.

## correction — 2026-09-20, the OWED list's deploy line is STALE

Item 2 in the "OWED, explicitly" list above ("Deploy
`RimMandrake.CreatureBehaviors.dll`... blocked by a file lock this pass") is
superseded by this file's OWN later "LIVE TEST 2026-09-19" section, which
already confirms the assembly was deployed and loaded live. RE-MEASURED
2026-09-20: the live Mods-folder DLL is still byte-identical (md5
`de8bc66eef4c66c6d50a6e650b306c03`) to the repo copy, `deploy_custom_mods.py
--mod CreatureBehaviors` (plan-only) reports "in sync (14 files)", and the
deploy is traceable to commit `6be013af0` ("Overnight BELT validation: 7
touched assemblies deployed... CreatureBehaviors... 0 typeload/patch_failed/
recovery on a 15-mod minimal-list restart"). The mod is active in the live
617-mod `ModsConfig.xml`. Deploy debt on this item is DISCHARGED; only the
live-behavioral-test debt (items 1 and 3 in the OWED list, and the LIVE TEST
section's own three follow-ups) remains open.
