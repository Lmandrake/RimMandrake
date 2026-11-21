## spec
found-by: FlowWorks in-game visit 3, game a, flowworks tier, calm site, 2026-11-21 5:53 AM PST.
sc_moat_raid row MOAT_two_held_and_captured UNMEASURED (evidence/sc_moat_raid_20261121T055350.json): the raiders swam and tired,
the moat drained, but only ONE raider (Human21193) was held in the drained moat; that one was captured (VERDICT AlreadyPrisoner,
warden able after); five free raiders were driven off. The row needs two held, so it could not ask. Every other row PASS
(swim, drain, chemfuel pumped, moat burns, bridge-down control).
Class SITE, presumed [guess ~60%]: how many raiders are in the water when the drain ends is the raid's chance in this staging.
Unrepaired in the sitting. See also RIMMANDRAKE_PROBE_FLOWWORKS_WARDEN_DOWNED_BESIDE_HELD_RAIDER (a different cause: a warden downed).

## verify
- sc_moat_raid live: at least two raiders held when the drain ends, on every run (or the row reads the count it got and the bar text changes, the Designer's call).

Acceptance test: `python.exe src\RimMandrake\FlowWorks\northstar\concept_scenes.py --scene scene_moat_raid --out <json>` exits 0 (every row PASS); UNMEASURED now (1 held).

## refs
file: src/RimMandrake/FlowWorks/northstar/concept_scenes.py
