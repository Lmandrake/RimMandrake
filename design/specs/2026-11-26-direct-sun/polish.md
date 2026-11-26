# Polish: Direct Sun (design/specs/2026-11-26-direct-sun/boundary.md)

- `src/RimMandrake/CreatureBehaviors/Source/RM_CreatureBehaviorsMod.cs`: the Direct Sun master hides its dependents (`if (sunHeatEnabled)`) instead of greying them with the masters kit (SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST), whose contract wants all 125 settings of this screen named. risk: adds a feature (the screen's kit adoption); without it a player who switches Direct Sun off does not see that a tuned zenith, dial or weather switch is still set, and meets it again when the master comes back on.
