# FLOWWORKS_SETTINGS_WIRE_AFTER_TANKS

Filed by BENCH 2026-10-14 from SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST (kit built at e21f179c3c, GSS and Pyrelands wired).
FlowWorks C# was being edited by another agent, so its wiring was written down instead of done.

## spec

Follow `infrastructure/state/items/SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST.md` section "FlowWorks wiring owed" (steps 1-5:
csproj links, Masters/Get/Set/Dependent helpers, Reset all, candidate masters to confirm at their read sites).

## criteria

- A1 L0: settings_audit.py shows FlowWorks masters "declared"; selftest_settings_screens.py all ok; FlowWorks DLL stamp MATCH.
- A2 L1: in the FlowWorks settings window a master off shades its dependents and keeps their values; Reset all asks first.
