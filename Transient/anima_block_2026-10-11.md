# anima block 2026-10-11

## routes

## fix

## status
routes: Base_Player genSteps li AnimaTrees; Storyteller BaseStoryteller OnOffCycle AnimaTreeSpawn; Glowforest preventGenSteps(already). No wildPlants route.
status: patch AnimaTree_NoRandomSpawn.xml in MandrakePatches; selftest added; selftests 330/410 only art_checks FAIL.
live check: new quicktest map -> count Plant_TreeAnima == 0; Base_Player genSteps lacks AnimaTrees; no AnimaTreeSpawn storyteller comp.
