# EMPIRE_RAID_QUICKTEST_1

## spec
Quicktest (~90 s map, bridge) proof of the shipped Empire reskin, against vanilla
`Empire` — successor to V2_DREAMS C2, whose spec drove the raid through the
excluded `OuterRim_GalacticEmpire` (canon.yml `empire.outerrim_faction_excluded`).
No `set_faction_relation` step: vanilla `Empire` is already hostile via the
patched `permanentEnemyToEveryoneExcept` whitelist (player factions deliberately
absent). Fire `jawa/fire_incident incidentDef=RaidEnemy faction=Empire dryRun=true`
first; abort on `canFireNow:false`. PASS `points` EXPLICITLY — `points<=0` takes
the storyteller default, tens of points on a fresh quicktest.

## verify
The live check is owed to mechanisms never once observed running together:
the `permanentEnemy false` + whitelist route to hostility, `fixedLeaderKinds` →
Jawa_Empire_Leader, and `fixedIdeo` Rising Order all BAKE at world creation and
have never been observed on a world generated after the patch landed.

## criteria
- Read the `faction` field in the REPLY, never the one you sent —
  `IncidentWorker_RaidEnemy::TryResolveRaidFaction` silently substitutes a random
  weighted faction and still reports `success:true` when the passed faction fails
  its gates (hostile + !deactivated). Reply faction must be `Empire`.
- Raiders are `Jawa_Empire_Grunt/Heavy/Specialist` wearing OuterRim stormtrooper
  armor (apparelRequired), not cataphracts.
- Faction leader is Jawa_Empire_Leader (Emperor Palpatine), title "Emperor".
- Faction ideo is "The Rising Order"; faction name "Galactic Empire".
- `OuterRim_GalacticEmpire` appears in NO faction list on the world.

## Watch out
- A world generated BEFORE the patch keeps the Stellarch and a generated ideo —
  attribute a miss to world age before blaming the patch.
- The raid groups sit inside `PatchOperationFindMod "Outer Rim - Galactic Empire"`:
  on the minimal modlist without that mod, the whole group patch is a silent no-op
  and vanilla kinds spawn. Run this on a list that includes the OuterRim mod.
