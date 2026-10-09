# BRIDGE_KILL_HOSTILES_TOOL_1 - Bridge kill-hostiles tool

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
Bridge gaps seen in 2026-10-07 sweeps: (a) no hostile-kill tool, so review/test maps stay contaminated by manhunters and raiders (policy: kill hostiles on review maps); (b) reading the architect menu beyond rimworld/list_architect_designators (designators read as 'RuntimeType' for patches_applied). Neither is filed. Add to JawaBench: jawa/kill_hostiles (map, optional faction/def filter, returns count killed) and make architect designator reads return def names (or add a cheap tool). Use the rimbridge-companion skill; filter by pawn.HostileTo(Faction.OfPlayer) and report killed ids.

## verify
Quicktest map with spawned hostiles; tool-list check that the new tools are present after build.

## criteria
A1: jawa/kill_hostiles kills only hostiles (a colonist and a tamed animal control survive) and returns the count.
A2: architect designator read returns real designator/def names for a given category (patches_applied can read them).
A3: both documented in the rimbridge skill tool list.

NEXT: claim this item and start with criterion A1.

## built 2026-10-08 (FOUNDRY belt, offline; companion not deployed)

- A1: `jawa/kill_hostiles` in `JawaBenchHostileTools.cs` (GenHostility.HostileTo(pawn, player); faction/pawn filters, dryRun, destroyCorpses; returns killed ids, `survivorsNonHostile` control and `hostilesLeft`).
- A2: `jawa/get_defs` now renders a `System.Type` field or list item as its bare class name (the deep path already did), so `DesignationCategoryDef.specialDesignatorClasses` reads e.g. `Designator_Deepfire`, not `RuntimeType`.
- A3 (skill tool list) left for a skill-curation session (skills are edited only there).
- Owed: deploy (`build.py --gm --apply` with the game closed), then the quicktest proof.
