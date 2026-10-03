# RimMandrake: The Bazaar — validation walk
subject: src/RimMandrake/TheBazaar  (packageId `mandrake.rm.bazaar`)
deps: Core only (no DLC); the broker tab is designed to auto-hide without FlowWorks (`mandrake.rm.flowworks`)
list: any tier that loads the mod; no map content needed
status-hint: THE_BAZAAR_FIRST_SCRIPT_1 / BAZAAR_WINDOW_GRID_1 — only slice 1 ships (four plugin def classes, an inert Dialog_Trade subclass, an empty settings screen); the intercept, grid, price engine, whole-deal haggle duel, banter and broker tab are designed and NOT built

Sources: `src/RimMandrake/TheBazaar/About/About.xml` description, `Source/*.cs`, `Source/Defs/*.cs`, `design/RimMandrake/bazaar_trade_window_design.md` (sections 2-7, rulings log: whole-deal haggle, owner 2026-09-13). Script: `src/RimMandrake/TheBazaar/validation.py`.

## must be true
- The mod ships no XML defs, only four plugin def classes (`RM_BazaarColumnDef`, `RM_BazaarBadgeDef`, `RM_BazaarTabDef`, `RM_BazaarIntelLayerDef`); a probe for an absent def reads notFound. → defs_and_types.no_xml_defs_shipped
- Every shipped C# type (the four def classes, `RM_BazaarSession`, `RM_Window_Bazaar`, `RM_BazaarSettings`, `RM_BazaarMod`) resolves in the running game from the loaded assembly; a bogus type reads unresolved. → defs_and_types.types_resolve
- The log carries no Bazaar error. → defs_and_types.no_bazaar_log_errors
- The settings screen declares every `public static` field as a Mod Settings toggle; at slice 1 it declares none (`RM_BazaarSettings` has no field), and the screen says so. → settings_roundtrip.settings_probe_finds_fields, settings_roundtrip.<field>_round_trips (generated per field when fields land)
- Slice-1 truth: nothing replaces vanilla's trade window; no Harmony patch of this mod sits on `WindowStack.Add`. → intercept_state.window_stack_add_not_patched (goes red the day the intercept lands, as a prompt to extend this script)
- The trade window is a searchable, sortable, column-configurable grid. → UNCOVERED: not built (design section 2; slice 2+)
- Intel layers are gated by Social skill and found artifacts. → UNCOVERED: not built (design section 4)
- The price engine reads the trader's economy side only and never rewrites vanilla trade execution. → UNCOVERED: not built (design section 3)
- The haggle duel is over the WHOLE deal at confirm time with one patience meter per trader session (owner ruling 2026-09-13), not per item. → UNCOVERED: not built (design section 5); needs a trade session driven through the bridge
- The broker tab appears only with FlowWorks. → UNCOVERED: not built (design section 2/7)
- Banter is the fourth Oracle consumer and degrades to nothing without the CLI. → UNCOVERED: not built (design section 6)
- With every Bazaar setting off, the trade window is a plain good trade grid. → UNCOVERED: no settings exist yet

## the walk
1. [D] `jawa/get_defs` for an absent def (control) and `jawa/type_probe` for each shipped type plus a bogus type   # defs_and_types
2. [D] `jawa/mod_settings_field` round trip over every `public static` settings field (none today)   # settings_roundtrip
3. [D] `jawa/harmony_patches WindowStack.Add`: no postfix/prefix owned by `mandrake.rm.bazaar`   # intercept_state
4. [B] trade sessions: grid, haggle duel, broker tab   # unshipped (UNMEASURED)

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the mod already replaces the trade window" — `RM_Window_Bazaar.cs` says NOT WIRED IN and no Harmony patch exists in `Source/`; `intercept_state` reads it live.
RULED OUT: "the missing settings toggles are a defect" — `RM_BazaarSettings.cs` records the rule that a toggle is added in the slice that adds its mechanic, never ahead.
