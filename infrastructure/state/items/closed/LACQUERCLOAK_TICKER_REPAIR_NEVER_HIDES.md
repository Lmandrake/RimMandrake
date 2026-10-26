# LACQUERCLOAK_TICKER_REPAIR_NEVER_HIDES

Found in code-review wave (DIRTY_CODE_REVIEW_STANDING_LOOP_1), reviewing src/RimMandrake/Scarlands/Source/RM_Chotrix.cs.

RM_Apparel_LacquerCloak (Scarlands/Defs/ThingDefs_Items/RM_CloakLacquer.xml, ParentName ApparelMakeableBase) carries
CompLacquerCloak, which does all its work in CompTick. Vanilla 1.6 Core Apparel_Various.xml ApparelBase/ApparelMakeableBase
set no tickerType, so ThingDef.tickerType is the default Never. A worn apparel is ticked through the pawn's holder
children (Thing.DoTick -> ThingOwner.DoTick -> Thing.DoTick), but each thing calls Tick() only when its own
def.tickerType == Normal (decompiled Verse/Thing.cs DoTick). So the cloak never hid its wearer.

Fix: `<tickerType>Normal</tickerType>` on the def (vanilla belts and packs do the same).
lint_ticker_compat now resolves vanilla ApparelBase/ApparelMakeableBase to Never; mutation-checked: with the fix
reverted the lint reports NEVER_TICKER on this def, and it is the only apparel finding in the repo.

Owed: a live look (cloak worn, standing still, unseen -> invisibility hediff) when a load round is next spent; not deployed.
