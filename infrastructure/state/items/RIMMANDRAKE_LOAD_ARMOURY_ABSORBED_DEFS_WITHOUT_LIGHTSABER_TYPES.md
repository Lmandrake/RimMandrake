## spec

Armoury (mandrake.rsw.armoury) ships absorbed copies of donor defs. Some nodes in those copies name classes that only a
donor's DLL provides: `Lightsaber.*` (lee.theforce.lightsaber), `BigAndSmall.*` (redmattis.betterprerequisites),
`XmlExtensions.*` (imranfish.xmlextensions) and `WHands.*` (mlie.showmeyourhands). None of these mods is a hard
dependency of Armoury. On a list without the donor, each unguarded node fails the load of its def, and the game logs
"Could not find type named ..." or "Type ... is not a Def type". The failed Kyber and crystal-formation defs then
also cause "Could not resolve cross-reference" lines. Measured: the 26-mod tier `explosiveknockback_visit`, ArchBig,
Player.log of 2026-11-26 03:16 PST (the same lines are in Player-prev.log).

Fix: guard each such node with `MayRequire="<donor packageId>"` on the node itself or on an ancestor. Then the def
loads without the donor's comp, and the donor's def type or patch is skipped. On a list with the donor, nothing
changes.

## verify

Offline: `python3 src/RimMandrake/Utils/selftest_armoury_donor_class_guard.py`. The lint reads every Armoury XML
file and fails on a donor-namespace class that has no MayRequire for its donor. It is red on the parent and green on
the fix.

Live: a cold load of the tier `explosiveknockback_visit` logs no "Could not find type named Lightsaber.", "BigAndSmall.",
"XmlExtensions." or "WHands." line, and no "is not a Def type" line for those namespaces, from an Armoury file.

## criteria

- The offline lint is red on the parent and green on the fix.
- A cold load of the tier `explosiveknockback_visit` logs no donor-class error from an Armoury file.

## refs
file: src/RimStarWars/Armoury/Defs/Absorbed_TheForceLightsaber/ThingDefs_Misc/Absorbed_TheForceLightsaber_Kyber.xml
file: src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/ThingDefs_WeaponsArmorsGadgets/Absorbed_KotorCore_Apparel_SWGenericHeadgear.xml
def: ThingDef/Force_KyberCrystal
tier: explosiveknockback_visit
