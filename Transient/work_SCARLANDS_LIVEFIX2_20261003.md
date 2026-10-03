# Scarlands live fix 2

Started.
- refit: rewrote live check to get_defs deep=True, asserts ComponentSpacer 3 + RM_Etchant 10 by name (real def has 3 rows incl. Steel 200). If rows still bare type names -> UNMEASURED.
- tracking: live evidence shows ordered_job success=false, curJob '(none)', nowRunningRequested false (pawn never walked; also spawned on turret cell). Comp reads fine (CompTick needs a Moving pather; patch sets tickerType Normal). Not provably a mod bug; harness issue. Chain now reports UNMEASURED when Goto is not confirmed running. No C# change; no rebuild. Unproven live whether comp is attached.
