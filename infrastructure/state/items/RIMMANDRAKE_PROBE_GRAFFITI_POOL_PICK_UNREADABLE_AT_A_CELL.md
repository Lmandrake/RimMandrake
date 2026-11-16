## the gap
Three controls in `src/RimMandrake/Graffiti/validation.py` need GraffitiPool's own answer and no probe gives it (`GraffitiPool.WeightedPick`
is private; `PickForSpree` needs a live painter's job):
- `wall_closeup` / `control_edge_on_cell_gets_no_mark`: "the pool returns none" at a cell whose only wall is east or west (sc_wall_closeup);
- `wall_closeup` / `control_south_only_cell_holds_no_mark`: the same at the south-only cell after FarSideSetup (sc_wall_closeup);
- `spree_variety` / `control_pool_gated_to_one_def`: "the pool gated to one def gives one def only" (sc_spree_variety).
Each raises `MISSING TOOL ... filed as POOL_PICK_ITEM` today.

## spec
Add `public static string PoolPick(string args)` to `Source/RM_GraffitiStage.cs` (test probe, jawa/static_call): args
`painter/x,z[/onlyDef][/n]` -> `POOL x,z | picks n | none k | <def>:<count> ...`, calling the same pick the spree's brush calls at that cell
`n` times (default 20), with `onlyDef` restricting the eligible set to that one def (a test-only filter, never a setting). Build with
`winbuild.py Graffiti`, commit the DLL with its `.srchash`, then replace the three MISSING TOOL raises with reads of it (edge-on and
south-only: `picks 0`; gated: one def in the histogram).

## acceptance test
Watched failing on the base 2026-11-15 (`probe False missing_tool_rows 3`); expected `PASS`:

    python3 -c "
    import re;s=open('src/RimMandrake/Graffiti/Source/RM_GraffitiStage.cs').read()+open('src/RimMandrake/Graffiti/Source/RM_GraffitiSocialProof.cs').read()
    v=open('src/RimMandrake/Graffiti/validation.py').read()
    probe=bool(re.search(r'public static string PoolPick\(string args\)',s));left=len(re.findall(r'MISSING TOOL[^\n]*\n?[^\n]*POOL_PICK_ITEM',v))
    print('probe',probe,'missing_tool_rows',left);assert probe and left==0;print('PASS')"

Live (UNRUN, owner 2026-11-13 rule): `python.exe src/RimMandrake/Utils/modcheck/cli.py run Graffiti` chains `wall_closeup` and `spree_variety`.
