
## spec
First live wave (MODCHECK_MATURE_WAVE_1, 2026-09-13, min16 environment):
2 GREEN (Pits 3/3, FluidCanals 3/3), 12 RED, 2 aborted. Evidence per mod:
`Transient/modcheck/<Mod>_20260913T*.html` + `<Mod>_summary.json` (raw
read-backs per component), run log
`Transient/modcheck_wave_bridge_20260913.log`. Most REDs are SUITE
assumption bugs of exactly the class each file's own "Still not proven"
register predicted — correct the suite against the captured evidence, and
file a real mod-defect finding ONLY where the evidence shows the MOD wrong
(read-the-mechanism-first). Known starting points:
- Inhabited 0/10: its `_debug()` non-ToolMap path analogy
  (`Actions\T: <label>`) likely wrong wholesale — its docstring predicted
  this exact all-fail signature and the fix locus.
- RimProperty: aborted in chain setup — `jawa/set_thing_props(faction=
  "Pirate")` read back faction=None on a spawned Turret_MiniTurret (its
  registered unproven #1). Check the tool's actual param shape.
- Graffiti: bridge desync "unexpected response id" — the poisoned-socket
  trap; needs the reconnect-with-post-condition-polling pattern in the
  LIBRARY (runner spec §2 names it as owed), then a re-run.
- Ninefold 3/6, Pyrelands 3/6, Droidworks 11/21, PawnFlavor 6/14,
  JawaIonWeapons 2/10, StarWarsRaces 1/4, Antiquities 1/2, ShipMemory 2/3,
  ResearchRetag 1/2, StructureInjections 1/2, Aftermath 0/3: read each
  sheet's expected-vs-observed before touching anything.
- Ninefold data point: the min16 quicktest opener did NOT crash with
  Ninefold loaded — supports NINEFOLD_DEBUG_GAME_READY_CRASH_1's
  full-stack-log-volume/OOM theory, note it there.

## verify
Each corrected suite re-run on the min16 list; verify events recorded;
every remaining RED component is either a filed mod-defect finding or an
explicitly registered environment gap.

## criteria
No RED that is merely a wrong suite assumption; GREEN set grows honestly.
