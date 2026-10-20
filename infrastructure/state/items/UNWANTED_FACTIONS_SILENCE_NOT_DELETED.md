# UNWANTED_FACTIONS_SILENCE_NOT_DELETED

Replaces `COMB_EXCHANGE_FACTIONS_EXCISE_POLITELY`. That item planned `requiredCountAtGameStart 0` plus removing the
factions from the saves. The 1.6 source shows that neither works for the Space Exchange: Odyssey's
`BackCompatibility.FactionManagerPostLoadInit` re-creates `TradersGuild` on every load. Offline removal is the
measured failure in `skills/rimworld-world-editing/references/savegame-editing.md`.

**Owner, 2026-10-20:** *"I notice in factions there are Tallmere Combs and Sacrileg Hunters however. We don't want
those... same with the Space Exchange."* · *"Make sure we can stop that."*

**Design:** `design/RimMandrake/factions_unwanted_and_lingering_2026-10-20.md` (§3 levers, §7 sequence).

## spec

The def side is already committed and is **not deployed**:
- `src/RimMandrake/LeaningScrub/Defs/FactionDefs/RM_CombHolds.xml`, which banishes the faction in its own def.
- `src/RimUtinni/UtinniPatches/Patches/FactionSlate/BannedFactions.xml`, which banishes `TradersGuild` and
  `CASacrilegHunters` and removes `<faction>` from 4 orbital traders.
- `RM_ScrubInjections_GenStep.xml`, whose `farmerFaction` is now `OutlanderCivil`.
- Registry: `src/RimMandrake/Utils/factions/banned_factions.json`.

Steps:

1. **Deploy (on a load round).** Run `deploy_custom_mods.py --mod <Baroque Biomes>` and `--mod <UtinniPatches>`:
   plan first, then `--apply`.
2. **Take a dump on that load.** After it, run
   `python3 src/RimMandrake/Utils/banned_factions.py check-dump <new capture>`. It must PASS.
   - **Baseline today** (capture `2026-10-20T08-31-20Z`): FAIL on 3 defs and 4 traders.
   - **Accepted end state:** `CASacrilegHunters` reads ABSENT, because Caravan Adventures is cut.
3. **Read Player.log for the slate patches.** No red line may come from `BannedFactions.xml`.
4. **Edit each dev save that is kept, through the bridge only.**
   - **Bridge:** run `rimflow bridge take --for "banish unwanted factions in dev saves"` first. Never edit an .rws
     offline. Back up the Saves folder to `D:\ClaudeWork\backups\` first.
   - **Flags:** `jawa/faction_flags_set faction=RM_Faction_CombHolds hidden=true defeated=true`.
   - **The Space Exchange:**
     - set the same flags: `jawa/faction_flags_set faction=TradersGuild hidden=true defeated=true`;
     - remove its orbital `SpaceSettlement` with `jawa/world_objects_get`, then `jawa/world_objects_remove`
       (DEV_START had one).
   - **SHIP / LANDED / FOUNDERS:** they had no `TradersGuild` on disk. They gain it, and `Salvagers`, on their first
     load (per source; record what is MEASURED). Banish it there too.
   - **Do not** set `temporary` on either faction (Odyssey re-creates the Space Exchange), and do not remove the faction.
   - **Save** through the bridge.
5. **Prove the saves.** Run
   `python3 src/RimMandrake/Utils/banned_factions.py check-save <each saved .rws> --dump <new capture>`.
   Each must PASS: ABSENT or BANISHED for all three.
6. **Spot-check the screens (optional, cheap).**
   - **Factions tab:** neither name appears.
   - **Comms console:** neither name appears.
   - **An orbital trader:** fire one with `jawa/` incident tools. Its letter names no faction.
   - **Player.log:** no new `Faction leader for Tallmere Combs is null` line.
7. **For the shipped world, at the re-make.**
   - **Configure Factions:** neither faction is offered (max 0).
   - **Space Exchange:** banish it again after the first load (runbook `06_remake_runbook.md` S7/G15).
   - **VEF:** decide the VEF faction-discovery offers. `ignoredFactions` lives in the world; there are 3 offers on
     the 324 list (design §2/§8).

## verify

- `check-dump` PASS on a post-deploy capture.
- `check-save` PASS on every kept `ASHKARR_DEV_*` save.
- Player.log free of `BannedFactions.xml` errors and of the Tallmere Combs null-leader line.
