
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row CB-8 there is the spec:

| CB-8 | A decoy shade tarp: a cheap painted awning that predators that hunt from shade read as real shade, though it gives no real cooling. Players use it to lure heat-driven predators into a killbox or pen. A mirrak-hide version is more convincing. | A building carrying a "reads as shade to seekers" extension, built on the creature-only false-shade read; research-gated, with a settings toggle. | M | med (balance: free predator control) | CreatureBehaviors, LongShade (mirrak hide) | `RM_FalseShade.cs` RM_FalseShadeExtension is on race defs only (used by `LongShade/.../RM_LongShade_Mirrak.xml`); `RM_ShadeClothExtension` deepens real shade only; no "decoy" item found in items/ or design/ |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify DECOY_SHADE_TARP_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A1 (L1): decoyShadeEnabled wired and gated (mechanic_toggles.decoyShade_wired_and_gated); tarp def and research resolve
- A2 (L2): a shade-seeking animal paths to a placed decoy tarp and the shade grid reads 0 under it (art owed: tent textur
Evidence is the Player.log line or bridge state read the criterion names.

### Exact checks 2026-10-09 (acceptance sitting)
- A1 CHECK: Same arms as the existing validation chain `CreatureBehaviors/validation.py` `mechanic_toggles` (step `decoyShade_wired_and_gated`): `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_CompDecoyShade"`; `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_FalseShadeExtension"`; `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_MapComponent_FalseShade"`. Then `jawa/get_defs defs="ThingDef/RM_DecoyShadeTarp;ResearchProjectDef/RM_DecoyShadeResearch" fields="defName" limit=4`. Then `jawa/mod_settings_field typeName="RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings" action=get field="decoyShadeEnabled"`, `action=set field="decoyShadeEnabled" value="False"`, `action=get` again, then restore the old value. PASS: every type_probe resolved=true; get_defs success=true, foundCount=2, notFound empty; get returns true, after set False get returns false, restored value equals the first read. FAIL: any resolved=false (DLL not loaded or not in csproj), foundCount short or notFound non-empty, or the off arm reads true (toggle not wired). A failed get_defs call (success=false) is UNMEASURED, never absent.
