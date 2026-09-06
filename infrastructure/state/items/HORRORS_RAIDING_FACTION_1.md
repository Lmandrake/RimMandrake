# HORRORS_RAIDING_FACTION_1 — the Horrors as a raiding faction + injected dungeon content

Owner ruling 2026-09-06 (`assailant_weapon_remnants.md` §Rulings 2–3): a RAIDING faction,
not a settlement faction; encountered when players land on the night side; the content
goes into dungeons injected onto nightside tiles.

## spec
- Donor: Horrors (Continued), `Mlie.Horrors`, ws 3535224844 — FactionDef `Horrors`,
  pawnkinds Visceral / Bulwark / Terrorworm / Harvester / Prowler / BroodLord, buildings
  HorrorHive / HorrorDen / HorrorBurrow / SinkHole / MaggotNest / HorrorCrysalis* /
  HorrorFirefoamPod, plant HorrorWeb; own storyteller + map generation + think trees.
- **Faction reshape**: settlementGenerationWeight 0, no bases, no world holdings; raids
  gated to nightside/cold reach (BENCH reading: a threat you walk toward — confirm with
  the owner); permanent-enemy; keep the mod's think trees so the AI behaves.
- **Injections**: nests, burrows, the sinkhole (dungeon door into the cave network),
  dormant crysalises and mite-nest larders as Inhabited objects / dungeon templates on
  nightside tiles — `fall_line.md` injection precedent; KCSG or the dungeon items'
  method (`VAULT_DUNGEON_BUILD_1` pattern).
- **Reskin toward the starved-cold weapon**: cold-adapted forms, crysalis = cold dormancy,
  the BroodLord's live-capture as "sample collection" for a dead master.
- Naming per the tier grammar (`RSW_`); no Anomaly dependency unless
  `ANOMALY_EXCEPTION_ACCESS_1` opens it.
- Check the mod's storyteller/map-gen hooks don't fire outside our injections.

## verify
Faction has 0 settlements on the frozen world; a nightside quicktest map shows injected
nest objects; a raid arrives from the Horrors faction under the reach rule; no Horror
raid on a dayside test map.
