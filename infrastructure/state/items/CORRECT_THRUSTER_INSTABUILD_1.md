# CORRECT_THRUSTER_INSTABUILD_1 — the thruster mystery is solved; fold this in and close

BENCH proved the answer live on 2026-08-29 while flying the GRAVSHIP_LANDING_DIRECT_PLACE_1
proof. THRUSTER_INSTABUILD_NEVER_ACTIVE_1's own two criteria are both answered below;
apply this to the item (its criteria boxes tick, this text is the resolution) and close it.

## Spec

Append to THRUSTER_INSTABUILD_NEVER_ACTIVE_1 and tick both criteria:

**Persistent, not transient — and not VEF facility-equivalence.** Three stacked causes;
each was cured live on a scratch quicktest until the thruster went ACTIVE (inspect clean,
console "Gravship range: 10", launch_check refusing on fuel/range instead of range 0),
then flew a full launch -> land cycle:

1. **The exclusion zone rotates to the side OPPOSITE the facing.**
   `CompProperties_GravshipThruster.GetExclusionZone`: cells = pos + (i,0,j)·rot +
   offset(0,0,-5)·rot. Rot South puts the 1x5 zone NORTH of pos — across the pad a
   south-edge thruster stands on -> "Blocked by substructure", forever. Correct: rot 0
   (north-facing, exhaust south), zone strip off-pad and cleared of substructure + things.
2. **VGE gates thruster activity on the astrofuel pipe net.**
   `vendor/mod_sources/VanillaGravshipExpanded-main/Source/HarmonyPatches/CompGravshipThruster_CanBeActive_Patch.cs`
   postfixes `CompGravshipThruster.CanBeActive` to false while
   `CompResourceThruster.HasFuel` is false. An unpiped thruster is its own empty
   one-building net, and vanilla's inspect string misreports the state as "Not connected
   to grav engine". ChemfuelTank IS VGE's astrofuel storage (capacity 250,
   `1.6/Patches/VanillaChemfuelTanks.xml`); connect with `VGE_AstrofuelPipe`, fill via
   god-mode "DEBUG: Fill" — exact label prefix, a loose 'fill' match executes "Allow
   manual refill" and fills nothing while returning success.
3. **Substructure writes are silently refused on floor terrain.** AncientConcrete ruins
   left 75/400 pad cells without foundation; parts standing in the hole all read "Not
   connected to grav engine". Verify with `jawa/get_terrain_layers` isSubstructure,
   repaint holes to Soil, re-set substructure.

The earlier "missingComponents cleared" observation stands as FOUNDRY mapped it:
link-existence only, never activity. All three fixes are baked into
`src/RimMandrake/bridgetools/prove_gravship.py` (commit history 2026-08-29).

## Verify

`python.exe src/RimMandrake/bridgetools/prove_gravship.py` on a game-up window passes
end-to-end, or simply: the item text carries the three causes and both criteria are
ticked.

## Criteria

- [ ] THRUSTER_INSTABUILD_NEVER_ACTIVE_1 carries the resolution above, criteria ticked,
      and is closed with a sha.
