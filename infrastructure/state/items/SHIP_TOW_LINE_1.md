
## spec

Owner answered 'Queue all' on a question card 2026-10-08 (decision taken by question card) for the remaining work of `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md`. Row X-13 there is the spec:

| X-13 | **A tow line on the ship.** The tether that pulls creatures can hook wrecks, carcasses or a downed beast and drag them home. It pairs with KeelHoist's vertical cargo lift. | CB-9 | M–L | med (save-key migration) | CreatureBehaviors, TheSump, KeelHoist | `IRM_TetherPullHost` has 2 hosts, both pawn-only |
| CB-9 | A salvage winch. The tether line can hook heavy objects as well as creatures (wreck chunks, carcasses, a downed beast) and drag them home to a capstan or the ship. | Generalise RM_CompTetherPull's target from Pawn to Thing, plus a host that only reels objects; research-gated. | M–L | med (save-key migration on `target`) | CreatureBehaviors, TheSump (RM_CapstanTurret), KeelHoist, salvage mods | `IRM_TetherPullHost` has 2 hosts (TractionLance, `TheSump/Source/RM_CapstanTurret.cs`), all with `Pawn target`; no drag/tow mechanic in src (`grep` for drag/tow/winch: only KeelHoist, which is vertical); no item names a tow or salvage winch |

Every invented number is PROVISIONAL. Every feature gets a Mod Settings toggle; names follow the three-tier scheme.

## verify

Record each owed criterion with `rimflow verify SHIP_TOW_LINE_1 --criterion <ID> --result pass|fail|partial --config <list> --evidence <path>`:
- A2 (L1): salvageWinchEnabled wired and gated; RM_SalvageWinch def and research resolve (mechanic_toggles.salvageWinch_w
- A3 (L2): a placed winch drags a wreck chunk home one cell per reel interval (art owed: capstan base placeholder; KeelHo
Evidence is the Player.log line or bridge state read the criterion names.

### Exact checks 2026-10-09 (acceptance sitting)
- A2 CHECK: Same arms as the existing validation chain `CreatureBehaviors/validation.py` `mechanic_toggles` (step `salvageWinch_wired_and_gated`): `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_CompSalvageWinch"`; `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_CompProperties_SalvageWinch"`; `jawa/type_probe typeName="RimMandrake.CreatureBehaviors.RM_SalvageWinchRules"`. Then `jawa/get_defs defs="ThingDef/RM_SalvageWinch;ResearchProjectDef/RM_SalvageWinch" fields="defName" limit=4`. Then `jawa/mod_settings_field typeName="RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings" action=get field="salvageWinchEnabled"`, `action=set field="salvageWinchEnabled" value="False"`, `action=get` again, then restore the old value. PASS: every type_probe resolved=true; get_defs success=true, foundCount=2, notFound empty; get returns true, after set False get returns false, restored value equals the first read. FAIL: any resolved=false (DLL not loaded or not in csproj), foundCount short or notFound non-empty, or the off arm reads true (toggle not wired). A failed get_defs call (success=false) is UNMEASURED, never absent.
