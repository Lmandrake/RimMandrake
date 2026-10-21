# CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT

**Owner, by question card 2026-10-20:** "Celestial Rogues is another faction you may not want. Ban it too?" ->
"Ban Celestial Rogues".

Design: `design/RimMandrake/factions_unwanted_and_lingering_2026-10-20.md` §5 Celestial Rogues, §7, §8 decision 4.

## spec

Def side committed, NOT deployed: `src/RimUtinni/UtinniPatches/Patches/FactionSlate/BannedFactions.xml` banishes
`Salvagers` (Odyssey; adds raidsForbidden, start/max/required 0/0/0; hidden and canGenerateQuestSites false were
already Odyssey's). Registry entry in `src/RimMandrake/Utils/factions/banned_factions.json`.

Same recipe as the Combs and the Space Exchange (`UNWANTED_FACTIONS_SILENCE_NOT_DELETED`); do them in one sitting.

1. Deploy UtinniPatches (`deploy_custom_mods.py --mod UtinniPatches`, plan then `--apply`) on a load round.
2. After the load, `python3 src/RimMandrake/Utils/banned_factions.py check-dump <new capture>` must PASS.
   Baseline (capture `2026-10-21T01-39-11Z`): FAIL on Salvagers raidsForbidden / maxConfigurable / requiredCount.
3. Bridge (`rimflow bridge take --for "banish Celestial Rogues in dev saves"`), back up Saves to
   `D:\ClaudeWork\backups\` first. In each kept dev save:
   `jawa/faction_flags_set faction=Salvagers hidden=true defeated=true`; then save through the bridge.
   Do NOT remove the faction or set temporary: BackCompatibility re-creates it on every load.
   - START / `_FACTIONS` / `_PARITY_QUIET`: loadID 24 'The Celestial Rogues', 0 settlements, 0 world objects
     (measured offline 2026-10-20), so there is nothing to remove with `jawa/world_objects_remove`; re-check with
     `jawa/world_objects_get` anyway.
   - SHIP / FOUNDERS: absent on disk; Odyssey adds it on their first load. Banish it there too.
4. `check-save <each saved .rws> --dump <new capture>` must PASS (ABSENT or BANISHED for every registry entry).

## verify

- `check-dump` PASS on a post-deploy capture; `check-save` PASS on every kept `ASHKARR_DEV_*` save.

## NEXT

`CELESTIAL_ROGUES_SILENCE_GROUNDED_IN_ORBIT` — def banish committed, not deployed; NEXT: on the next load round deploy UtinniPatches, run check-dump, then via the bridge set Salvagers hidden+defeated in each kept dev save and run check-save.
