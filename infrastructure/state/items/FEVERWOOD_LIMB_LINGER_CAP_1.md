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
