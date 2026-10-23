## spec
Child 7 of `FLOWWORKS_BRIDGES_DESIGN_SPAN_ANYTHING`. The suspension bridge textures, in the four styles (Scrapper,
Industrial, Modern, Futuristic; `liquid_containers_four_styles_2026-10-16.md`), list in `design/RimMandrake/suspension_bridge_construction_design_2026-10-18.md` §5: deck solid (linked),
deck grated (linked, real alpha), railing edge set (linked, open edges only), anchor (`Graphic_Multi`), tower,
collapse debris, jetty; rope tier Scrapper-only; sunken-deck ledge shadow overlay. About 28 textures.
- **Search first:** `artpipe_state.py find` and existing sheets' `.decisions.json` for deck, catwalk, grate or
  rope-bridge art. Trap covers keep their own look (Q8).
- Review sheet via `art_sheet.py` at true scale beside a vanilla human; grated tiles shown **over live liquid**; one
  shot of a pawn passing under a deck. Cosmetic: his permission before anything ships; install through `art install`.
- `ThingStyleDef` per building per style, picked by `Machinery/PipeLook.cs` (the `RM_BankWeir_*` pattern).
Dependencies: the sheet any time; install after `SUSPENSION_BRIDGE_BUILD_POSTS_AT_BOTH_ENDS` (defs exist).
ESTIMATE 1 to 2 agent-days + his look.

## verify
- L1: every texture passes the sprite validator (canvas, real alpha, facings).
- L4: his rulings on the sheet recorded in its `.decisions.json`; `art.py enact` run.
- L2: each style's deck, railing and anchor resolve in game (no pink texture; graphic path read per def).
