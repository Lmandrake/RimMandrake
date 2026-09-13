
## spec
`rimworld/update_mod_settings` reflects INSTANCE fields on the ModSettings
object and refuses `public static` fields ("Could not resolve field ...") —
MEASURED live 2026-09-12 on Pits (MOD_VALIDATION_PIT_PILOT_1). The 2026-09-13
modcheck retrofit wave found the static pattern is OUR HOUSE STYLE, not a
one-off: PitsSettings, RM_NinefoldSettings, RM_InhabitedSettings,
PropertySettings, AntiquitiesSettings, RM_AftermathSettings,
RM_PyrelandsSettings, ShipMemorySettings, RM_GraffitiMod, and
StructureInjections' settings all declare static fields. Consequence: NO
validation.py can flip any toggle live — every toggle component tests
shipped defaults only, and two suites' draft write+read-back components had
to be shelved (see the "NOT a chain" registers in
`src/RimMandrake/Graffiti/validation.py` and
`src/RimMandrake/StructureInjections/validation.py`).

Fix in the JawaBench companion (rimbridge-companion skill): make
update_mod_settings resolve static fields too — try instance first, fall
back to `GetField(name, BindingFlags.Static|Public|NonPublic)` on the
settings type (and on the Mod class itself, since some mods hang values
there). Read-back through the same path.

## verify
On a minimal-list quicktest: flip `trapTriggerEnabled` on Pits via the tool,
read it back changed, and confirm Pits' "armed cover never springs" behavior
flips accordingly (the component Pits' validation.py's "NOT a chain" note
describes). Then restore the shelved components in the two suites above.

## criteria
A toggle-flip component is writable for any of our mods regardless of
instance/static declaration; the two shelved components are restored and
green.
