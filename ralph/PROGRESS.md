# GSS Ralph: where the last pass got to

**Game: `ralph/GAME` says `b` (bridge 5175, data `/mnt/d/ClaudeWork/rimmandrake/instances/b`), lent by the Conductor while Graffiti is paused. A deploy needs game A free (`ralph/fw_holds.py a` exit 1). B has the GSS tier; B's Graffiti list is backed up at `$RM_GAME_USERDATA/Config/ModsConfig.graffiti-before-gss-20261107.xml`, and I moved my clone's stale swap marker aside on Steve (`deployed/config/ModsConfig.swap-active.stale-20261107.json`) so `tier` would run.**

Pass 12. Deployed DLL: commit 9c8c26b7cf (fallen lay, Scrapper strand, relink, path cost). Not deployed yet: the cut-half relink fix in `CompAerialAnchor` (below).

## Fixed this pass (all seen in the game on B unless said)
- **Fallen wires stopped at a shed's wall as rods** (`AerialMath.LayFallen`). Played: a mortar on the lamp mast with a shed under the span; the far mast's three wires ran straight to the shed wall and ended in three sparks. Now a wire tries its full slack turned up to 50 degrees off its line (own side first) before less slack; with a wall across every way it piles its spare cable in coils in front of the wall. Self-test row: 0/40 seeds lay whole beside a shed before, 36+ now. Seen: `p12q3_Modern_line.png` (before: `p12n3_Industrial_line.png`, `p12m3_Futuristic_line.png`).
- **Scrapper cords were Industrial's black rubber.** New `Strand_ScrapTaped.png` (1024x32, built from `Strand_Jawa`'s pixels by `ralph/art/scrap_strand.py`, installed through the art ledger): rust-red and olive salvage spliced in, duct and electrical tape. Ribbon repeat now follows the texture's aspect (`CordMaterials.Aspect`), so it repeats every 2.56 cells. Overhead/fallen Scrapper wires keep `Strand_Jawa`. Seen: `ba_new_Scrapper_t01.png`, `p12p_Industrial_pair.png` (Industrial heap beside a Scrapper run).
- **A rebuilt mast took back one span, not both** (`RM_MapComponent_Aerial.ProcessAutoLinks`): now every neighbour whose wires fell toward its cell. Seen: `p12q5_Modern_line.png` (orphanRelinks 1, both spans up).
- **Colonists walked into live fallen wires** (3 of 6 down at once, `p12n`): `RM_LiveWirePathCost`, +600 perceived path cost on live contact cells (vanilla fire +1000), only while shocks are on. Seen: priced cells follow liveness (41/21/41 as the hut battery went full/empty/full).
- **Not deployed:** a span cut mid-way whose far pole then dies left wires the rebuilt pole never takes back (played + reloaded, `p12r`, `gss_p12_mid*_Modern` saves on B). Cause: the cut half kept the cut cell as `toward`. Fixed in `CompAerialAnchor` despawn: it keeps its lay but belongs to the dead pole's cell. Build, deploy, rerun `p12_reno.py TAG Modern reload` to see it.

## The six owed items (Conductor's apply_now list): none still real
COLOUR_SEED_SPLIT fixed (`Core/RebuildTail.cs:57-59`), NO_LAMP_GEOMETRY false by design (lamps keep the centroid look he asked for), AUDIT_REJECTS_WALL_PLUGS fixed (`Core/CordAudit.cs:206`), FRESH_BUILD_TAP_CLAMPS fixed (`GimmeSomeSlackProbe.cs:353`), FUZZ_ONLY_UNKNOWN fixed (`GssFuzz.cs:630`), RESTRING_STYLES fixed (`ConduitStylePicker.cs:484`, now with an offline guard row in `StyleStage2Checks.BridgeWiring`). Side note from that check: `GssFuzz.cs:163` makes half the fuzz's consumers lamps, a kind the game never produces.

## Played this pass (GPT broaden, pass 12, `gpt_help_pass011.md`)
Asked: what a real player would do that my one scripted layout can't show. Acted on #4, #5, #8 (`ralph/live/p12_reno.py`): renovating through cords (wall built across kitchen cords: they re-lay round it; a bedroom wall over conduit made a door: the cord passes through it), liveness following a battery (correct), save/reload mid-rebuild (found the cut-half bug above). Not yet: #1 growing a colony one appliance at a time, #3 a live span across a rescue route, #6 joining two runs of different looks, #7 clutter/night/snow. Pass 10's leads 4 and 6 done (`p12m`/`p12n`/`p12q`: mast failure over a shed, rebuild, colonists).

## Blind judge on the colony at play zoom (old DLL; `D:\ClaudeWork\rimmandrake\ralph_gss\judge_p12\`)
Worst: straight 3-5 cell cords down the 3-cell corridor between house and workshop (Modern/Futuristic/Industrial; the lamp at (22,2) is wired by vanilla through the wall to conduit outside, so its cord runs out, down the corridor, and in at the south door), hairpins with straight legs (Futuristic workshop), a W of straight legs (Industrial kitchen), Modern's dense heap a net of straight strokes, a taut drop cord from the lamp mast to a lamp, fallen-wire legs from crossarms. Being fixed offline by a builder subagent when this was written (lab: `Transient/lab/ba/worlds/ba_*.json`, the four played colonies dumped by `ralph/live/dump_worlds.py`).

## Do next
1. Take the builder's straight-run fix if it holds (look at its renders), build, deploy, re-shoot tiles (`p12_look.py TAG --frames "" --tiles`), re-judge.
2. Consider routing a cord THROUGH a wall (into one face, out of the other) when the walkable detour is far longer than the wall's thickness: the corridor cord is a 12-cell detour for a lamp 4 cells from its conduit, and that is also an eighth way extra cables show at a doorway.
3. The cut-half relink: deploy and replay `reload`.
4. Modern dense heap (net of straight strokes, few strips), lamp-mast drop cord taut arc.
5. Full proof once (`proof_all.py --live`), not recorded.

## Steve
Fault window F20261107T174953Z open the whole pass (status showed `bad_cpus=[13]`): all shots are in-window. No surprise needed a restart; no dead game, no dropped ssh, no reboot. Game B restarted 4 times for deploys and the old-DLL before/after; the bridge came up in 22 s each time.

## North star, judged hard
- conduit_reads_invisible: true
- cord_lies_slack_in_loops: true
- cord_meets_wall_at_its_face: true
- dense_grid_reads_as_tangle: true for Scrapper, Industrial, Futuristic; Modern reads as a net of straight strokes (judge) — false until fixed
- break_live_and_dead_ends_differ: true (judge: easy in all four looks)
- overhead_span_above_everything: true (span over the shed's wall, `p12q5_Modern_line.png`; pawns `p12m0_Futuristic_shed.png`)
- downed_span_lies_on_ground: true on this DLL beside a shed (`p12q3`); crossarm drop legs still read straight-ish
- four_styles_distinguishable: true on this DLL (`p12p_*_pair.png`)
- one_run_one_style: true (`p12p_*_pair.png`, four looks, each beside a run in another look)
- never_taut_straight_cord: false (corridor, hairpins, kitchen W)
- never_cord_across_impassable: true (judge: none; a wall built through cords re-lays them round it)
