# FEVERWOOD_LIMB_LINGER_CAP_1 — the pool breathes

Source: `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md` row FV-1 (owner card 2026-10-08: queue all batches).

## what
Feelers and sentinels never acted and left only when hurt, so a quiet pool filled with limbs and a standing
sentinel muted the crown chorus for good. Built at `b20a31ffc`:
- `RM_CompTentacleLimb.TickLinger`: a limb not driven off sinks back (Vanish, no respite, no cooldown) after its
  linger time. Porters keep their own deposit exit; a limb already withdrawing from damage finishes that ladder.
  A sinking sentinel restores the chorus through the existing `PostDeSpawn` → `Notify_SentinelDown`.
- `RM_MapComponent_TentacleWatch.SpawnEncounterAt`: an ordinary (and oil-boil forced) emergence is trimmed to the
  live-limb cap; the Great Emergence is exempt; a capped roll still deposits pressure.
- Kernel `RM_PoolKernel.LingerExpired / SpawnBudget / LingerTicks`, unit-checked in `SelfTest/FeverWoodFuzz.cs`.
- Mod Settings: "Limbs sink back on their own" toggle, linger hours (1–72), cap (0 = none, up to 20).

**PROVISIONAL numbers** (invented, owe a sitting): linger 12 in-game hours, cap 6.

## criteria
- O1 L0: FeverWood builds; fuzz units cover LingerExpired/SpawnBudget/LingerTicks boundaries
- A1 L1: on a Fever Wood map with the bestiary on, a spawned feeler despawns after the linger time with no pool cooldown recorded
- A2 L1: with the cap at 1 and one limb standing, an ordinary emergence spawns nothing and encounter pressure still rises
- A3 L1: a sentinel sinking on linger restores the biome ambient (ChorusSilenced reads false)
- H1 L4: the owner judges the linger time and cap in a sitting (PROVISIONAL until then)

## verify

Run each criterion at its stated level and record it with `rimflow verify FEVERWOOD_LIMB_LINGER_CAP_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- L0: offline build, selftest/fuzz/lint (already run at implementation).
- L1: one minimal-list load, read Player.log for config/cross-reference errors and the specific line, or one spawn-and-read bridge probe.
- L4: owner judgement in a sitting; not a FOUNDRY acceptance task.
Evidence is the Player.log line or bridge read the criterion names; a screenshot is not evidence of state.

### Exact checks 2026-10-09 (acceptance sitting)
- A1 CHECK: Half readable now. Set `tentacleLimbLingerHours`=1 via `jawa/mod_settings_field typeName="RimMandrake.FeverWood.RM_FeverWoodSettings" action=set field="tentacleLimbLingerHours" value="1"`, spawn a feeler limb (the ThingDef carrying `RM_CompTentacleLimb`; defs in `FeverWood/Defs`) with `jawa/spawn_batch`, advance with `rimworld/step_game_ticks` in chunks and verify with `jawa/time_clock` (ticksGame) that the clock really moved; the tool silently truncates under load, and `jawa/time_set_ticks` does NOT simulate by 2600 ticks (linger checks run every 250 ticks), then `jawa/list_things defName=<feeler def>`; read the clock start with `jawa/comp_read thing=<id> comp="TentacleLimb" members="spawnTick"`. The "no pool cooldown" half needs a debug hook (see A2). PASS: comp_read shows spawnTick set; after 1 h the feeler is gone from list_things (Vanish, not a kill: no corpse or filth). FAIL: the feeler still stands after 2600 ticks at hours=1 (TickLinger never ran), or the setting is rejected.
- A2 CHECK: needs a debug hook. `encounterPressure` and the live-limb count are private to `RM_MapComponent_TentacleWatch` (`FeverWood/Source/RM_MapComponent_TentacleWatch.cs`); `jawa/comp_read` reads ThingComps only. Small item owed: `RM_FeverWoodProof.ProofLimbs(string)` returning `limbs=<N> cap=<N> pressure=<N> chorusSilenced=<B>`, read with `jawa/static_call`; then: set `tentacleLiveLimbCap`=1, stand one limb, trigger an ordinary emergence, read before and after. PASS: with the hook: limbs stays 1 after the emergence while pressure increases by exactly one step. FAIL: limbs becomes 2 (cap ignored) or pressure does not rise (the emergence was swallowed silently).
- A3 CHECK: needs a debug hook: same `RM_FeverWoodProof.ProofLimbs` as A2 (`ChorusSilenced => sentinelCount > 0` is a public property of the map component, unreachable by any current tool). Then spawn a sentinel, read chorusSilenced=True, let linger sink it (as A1), read again. PASS: with the hook: chorusSilenced True while the sentinel stands, False after it sinks. FAIL: still True after the sentinel is gone (ambient never restored).
