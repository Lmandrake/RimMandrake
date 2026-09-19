# TECH_TREE_WEAPON_GROUPS_1 — the research tree, examined with the owner

Owner, 2026-08-29 (verbatim): "the technology tree of the game must be examined
(bringing ship systems online, grouping technologies together for the weapons
by the kind of tech it is e.g. ion, laser, blaster, sonic, etc.)."

Two threads, one sitting:
1. **Ship-systems-online arc** — research that brings the Utinni's systems up
   over the campaign (ties to the disconnected anticraft caster showpiece,
   [[STARTING_SHIP_ANTICRAFT_1]] — part of the initial v1 challenge).
2. **Weapon tech grouped by KIND** — research projects reorganized along the
   forms-of-harm vocabulary (ion / laser / blaster / sonic / kinetic /
   gravitic...; `setting_physics.md` is the constitution, the turret canon's
   family analysis in `turret_register.json` is the worked example).

Census first (ResearchProjectDef across the 585 capture: what exists, what the
donor mods scatter), then the grouping design with the owner. Expect overlap
with turret normalization — the turrets' techs should hang off the same tree.

## Inherited from the turret pass (2026-08-29, BENCH)
CORRECTED 2026-08-30 (research prep, MEASURED): Mortars unlocks 21 things, only 2 cut — it is NOT an orphan; it still unlocks three non-roster turrets and five live shell recipes. The earlier 'unlocks nothing' claim was wrong. Original (wrong) note kept context: Vanilla ResearchProjectDef `Mortars` was believed to unlock nothing:
`Turret_Mortar` and `FT_Turret_Mortar` are Cherry-Picker cut at the turret
roster normalization (proton mortars are OuterRim tech, auto-mortars are mech
cluster pieces). At this sitting: cut the research row too, or repoint it at
something worth researching. Same look owed at `GunTurrets` (still unlocks
uranium slug — alive) and any mod research rows naming only cut turrets.
