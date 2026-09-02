# BENCH/FOUNDRY reboot handoff — 2026-09-02 (superseded in place, see below)

Owner went AFK to bed, then called the reboot. Everything below is committed and
pushed; nothing lives only in scratch.

⚠️ UPDATED BY FOUNDRY, 2026-09-02T10:2x UTC — the "Machine state" and "Standing
/ waiting" sections below were written before most of tonight's FOUNDRY work
landed and are stale on several points (game state, ATMOSPHERE_CONFIG_RESTORE_1,
the two Droidworks items). Corrected in place, not left to mislead the next
reader.

## Machine state
- Game is **DOWN**, not up. FOUNDRY killed it after a fresh restart reproduced
  COLD_LOAD_STATIC_CTOR_STALL_1's identical stall a 4th time (19+ min silent at
  "Finished transpiling 1409 methods", same CPU-climbing-but-stuck signature,
  bridge alive answering status:no_game the whole time). **This needs the
  owner** — see COLD_LOAD_STALL_INTERMITTENT_1, filed fresh; a bridge/log seat
  cannot diagnose further (disk space checked clean, 3.2TB free; 7
  steamwebhelper processes observed at kill-time, circumstantial only).
- Disk ModsConfig = the confirmed-good FULL 592, untouched. Atmosphere config
  (glorious rings+thick-atmo) WAS copied into place during this session's
  game-down gap — ATMOSPHERE_CONFIG_RESTORE_1 is done, not still pending.
  Bridge FREE (FOUNDRY released it).
- Fresh def dump captured 2026-09-02T08-39-17Z against the live 592; defDump
  marker DELETED (re-arm only on purpose).
- Sweep tooling promoted to repo: `src/RimMandrake/Utils/loadsweep/`
  (gen_config.py + sweep_load.sh; ~60s per minimal-list load cycle; poll
  "Bridge token:", the JawaBench ready line is lazy).

## Done this session (all scored in the ledger / run sheet)
- LOAD-HEALTH SWEEP 25/25 self-contained mods: zero resets, sentinels resolve.
  WreckedMachines needs VEF + vfecore + vfefactory. HelixTellurox still OUT.
- PawnFlavor `{0}`-label config error fixed + PROVEN absent on the full list.
- Utinni scenario live proof PASS (1 Ikee bonded+Obedience, 6 MandrakeJawa).
- Salvagers fold PASS; Salvation/VME_Nomad check RE-SCOPED to campaign creation
  (WORLDMAP_V1's ideo is generated "Astropolitan", the .rid was never in play).
- Gravship exporter round trip PROVEN on the current ship (export → raze →
  print_gravship --offset 82,58 → 2865/2865); corrosion-halo walls applied
  (587 verified); MEASURED: paint does NOT survive export — wall-colour scripts
  are NOT superseded. Export snapshot: `world/_ship/exports/`.
- Owner rulings landed: cast-only biomes (WILD_ANIMALS_PADDED_LISTS_1 →
  FOUNDRY, ready) · drop the 10 entity cast entries · corrosion-plan re-emit
  dismissed.

## Done this session, FOUNDRY (after BENCH's snapshot above)
- BIOME_CAST_REFS_BREAK_MAPGEN_1 closed: gen_cast_patch.py now gates every
  donor mod's cast entries behind their own MayRequire instead of one
  unconditional Replace mixing ~40 donors — root cause was
  BiomeDef.CommonalityOfAnimal's null-key Dictionary.Add crashing mapgen on
  any absent donor (see LESSONS_INBOX).
- WILD_ANIMALS_PADDED_LISTS_1: mlie.rimmsqol confirmed as the padder
  (biome_probe 1024→187 on Desert once retired). Owner's cast-only-exclusivity
  ruling implemented (1138 stray wildBiomes pairs removed, 10 Anomaly-entity
  cast entries dropped) and deployed. **Post-load census still owed** — was
  about to verify live when the cold-load stall hit; needs a load that
  actually reaches Playing.
- JAWA_SPAWN_KINDS_NO_RACE_1 closed: fixed a real forcedMissRadius config
  error on RSW_Gun_Sonic_HiveEmitter and an out-of-order/dead HediffDef stage
  on RSW_JawaIon_Stun. The "3 raceless pawnkinds" half did NOT reproduce
  against the live dump — noted, not chased further.
- ARMOURY_ABSORBED_FRAMEWORK_DEPS_1 closed: declared 5 real hard
  modDependencies (kotorcore, VEF, AdaptiveStorage, EBSG, Outer Rim Core) —
  found a 5th (Outer Rim Core, via RSW_EWebShot's damageDef) beyond the 3 the
  item named.
- DROIDWORKS_HEALTHSCALE_SENTINELS_1 dropped (stale, already resolved
  2026-08-30) — so **not** offline work remaining, correcting BENCH's note
  below.
- DROIDWORKS_DETONATION_ROLLOUT_1 + DROIDWORKS_GENERATOR_NAMING_DRIFT_1
  closed: CompDroidDetonation rolled to 20 more races (verified count myself:
  20, not the filed 17). Found and fixed 4 separate staleness bugs in
  gen_droidworks_defs.py left by the naming-scheme migration (dead path, 2
  bare-namespace Class= strings, a stripped RSW_ defName prefix) — proved by
  getting a byte-identical regen against committed HEAD.
- HELIX_TELLUROX_SHELL_LOAD_CRASH_1 blocked: full source-verified field audit
  found no defect, and mandrake.rsw.helixtellurox isn't even active right
  now, so it can't be reproduced offline.

## Standing / waiting
- **COLD_LOAD_STALL_INTERMITTENT_1 — needs the owner, see Machine state
  above.** This is the live blocker on everything else that needs a
  restart, including WILD_ANIMALS_PADDED_LISTS_1's own post-load census.
- Donor sunset: Wave 1 = themedsounds + swlights + TSDA, ready for a game-down
  gap with decision strings (see STARWARS_DONOR_SUNSET_1 notes). btd shippack
  re-measured KEEP, excluded. Trap for all waves: absorbed XML naming a donor
  DLL class is eaten silently when the donor leaves — sweep + minimal-list
  proof load per wave.
- Droids: critical path chokes on ONE Droidworks-enabled minimal quicktest
  session (Phase 0 proof + POWEREDDOWN wiring + wave-1 recipes — batch them).
  The two items BENCH's snapshot listed as "offline meanwhile" are now BOTH
  done (see above) — nothing offline currently queued for Droidworks.
- Next owner sitting: lee.theforce.lightsaber reconfirmation · droid
  Humanlike-needs card (BENCH rec: suppress) · run-sheet §5 look-ats · why
  the cold load is now intermittently stalling on the known-good list.
