# Owner walk: Gimme Some Slack + FlowWorks: scenes to stage (2026-10-11)

Owner, 2026-10-11: *"The priority then is to build the human-review sheets for me to walk through them and provide
feedback."* and *"I'd really like both of these mods to be as close to 100% deployed as possible with my assistance."*

This is the **staging run-sheet** for the bridge session that prepares his walk. He records rulings on the decisions
sheet; the scenes below are what the sheet's rows point at (`where:` = `GSS map N`, `FW map N / block V`, `walk scene Wn`,
`Mod Settings > …`). Per CLAUDE.md, *"Save user review options as save games."*: every scene ends as a **keeper
savegame**. Keepers stay until he says delete.

| what | path |
|---|---|
| decisions sheet (non-art, 93 rows: GSS 29, FlowWorks 64) | `Transient/owner_walk_gss_flowworks_2026-10-11/gss_flowworks_owner_walk_2026-10-11.html` (generator `make_sheet.py` beside it) |
| GSS art at true size (4 rows) | `Transient/biome_ffar/gss_owner_walk_art_sheet_2026-10-11.html` |
| FlowWorks art at true size (47 rows) | `Transient/biome_ffar/flowworks_owner_walk_art_sheet_2026-10-11.html` |
| GSS station key | `src/RimMandrake/GimmeSomeSlack/review/KEYSHEET.md` (33 stations) |
| FlowWorks station key | `src/RimMandrake/FlowWorks/northstar/review/map/KEYSHEET.md` (block V + 52 stations) |

## Before you start

1. **Wait for both builders**: the rigid universal pipe art (4 looks through the wire-style interface, owner rulings #1/#8)
   and the hose-off drain (ruling #2). Until they land, W3 and W4 cannot be staged. Stage everything else first; the
   sheet's PLACEHOLDER rows wait.
2. `rimflow bridge who`. Another subagent was validating on it 2026-10-11. Take it only when it is free:
   `rimflow bridge take --for "owner walk staging GSS+FlowWorks"`. Release it the moment you stop.
3. Deploy what the builders changed (`deploy_custom_mods.py --mod FlowWorks`, then `--mod GimmeSomeSlack`, plan then
   `--apply`). A DLL cannot be written while the game runs, so close the game first. Then check that the deployed DLLs
   equal the repo blobs (`git hash-object`).
4. Tier: `fw_gss_sitting` (17 mods, all 5 DLCs: `modset_builder.py --tier fw_gss_sitting --apply`). It is what
   FOUNDRY left active; restore afterwards with `modset_builder.py --restore`. Launch through Steam and wait for
   `[RimBridge] Bridge token:` (about 90 s).
5. Mod Settings at **shipped defaults** for every keeper except the deliberate variant in W1b. Back up
   `Config/Mod_*GimmeSomeSlack*` and `Config/Mod_*FlowWorks*` first.

All bridge scripts run under `python.exe` from the repo root and print CRLF, so pipe them through `tr -d '\r'`. 🔴 Look at
every keeper's screenshot yourself before he does (rimworld-live-review §9 checklist).

## Scenes, in walk order

**W1. GSS review map** (sheet groups GSS 1-4, FlowWorks 4 hoses):
`python.exe src/RimMandrake/GimmeSomeSlack/human_review.py --build --fresh-map`, then
`python.exe src/RimMandrake/GimmeSomeSlack/save_review_map.py --name RM_gss_review_owner_walk`.
It builds 33 labelled stations (style gallery 1-12, floor and overhead 13-20, hoses 16-17 and 21-33), a free build area
and the art-slot board, calm and paused, with god mode on. After the hose port the hose stations are cross-mod: check
that 11, 16, 17 and 29-33 built (no placeholder pads) before saving.

**W1b. Drip-loops variant** (row `gss_drip_loops`): on the same map, set the setting
`jawa/mod_settings_field typeName=RimMandrake.GimmeSomeSlack.Aerial.AerialSettings` field `dripLoops` = true, then
`human_review.py --goto 6` and save as `RM_gss_review_owner_walk_driploops`. Set it back to false afterwards.

**W2. FlowWorks review map** (sheet groups FlowWorks 1-3, 6, 7):
`python.exe src/RimMandrake/FlowWorks/review_map.py --build --fresh-map`, then
`python.exe src/RimMandrake/FlowWorks/review_map.py --save --name RM_fw_review_owner_walk`.
Block V is the pit look grid (D1-D4 × dirt/stone × dry/water/tar/scorched, plus oil, slime and the new liquids), and
stations 1-52 are the features. 🔴 Call `jawa/map_commit` before you judge any frame (a generated map renders stale).
Look for: tar opaque dark grey (not blue), scorch blast marks, depth labels ("chest-deep water"), bubbles on acid,
slime and boiling liquid, and propane pale grey. Those are the 2026-10-06 notes he will rule on.

**W3. Rigid universal pipe** (FlowWorks 5; after the pipe builder lands): on a clear soil patch of the W2 map or a fresh
map, build four short `RM_UniversalPipe` runs, one per look (Scrapper, Industrial, Modern, Futuristic), each run being
pump → pipe → tank, with a hose reel on one run. Also build one tank touched by two separate runs: they must stay two
lines (`never_tank_bridges_pipe_runs`). Label each run with `jawa/review_label`. Leave the style picker usable on one
unstyled run so he can try "Choose style" himself. Save as `RM_fw_pipe_owner_walk`. Interop with Dubs/VE pipes needs
those mods loaded, and this tier lacks them. Say so on the sheet note rather than staging a fake.

**W4. Hose switched off drains** (row `fw_hose_off_drains`; after the drain builder lands): charge a tank, couple a reel,
lay a hose to open ground with its end open, and let liquid flow (pump powered). Save **before** the flick as
`RM_fw_hose_drain_owner_walk`, so he flicks it off himself and watches it drain out of the open end. Take a state read
of the hose units before and after one test flick, then reload the save.

**W5. Pumps, storage, tank→hose** (rows `fw_intake_pump`, `fw_tank_feeds_hose`): one tank with a hose screwed in and
no pump, its far end on a second tank. The far tank fills (ruling #9). Beside it, a tank beside a pond with no pump
stays empty, and the same with a powered pump fills (ruling #3). Pouring out of storage needs no pump. Save as
`RM_fw_storage_owner_walk`.

**W6. Mod Settings screens** (GSS 5, FlowWorks 8): open Options → Mod Settings → Gimme Some Slack (both tabs) and
FlowWorks (scroll each of the 20 sections) and capture each with
`python.exe src/RimMandrake/Utils/system_screenshot.py Transient/owner_walk_gss_flowworks_2026-10-11/settings/<name>.bmp`.
He will still open the screens live; the captures are for the note column.

**W7. River steam on Pyrelands** (row `fw_river_steam`, optional): a Pyrelands-biome quicktest with a river (owed-audit
step B2). Steam puffs near river cells. Save as `RM_fw_pyre_steam_owner_walk`. If the biome cannot be reached on
this tier, mark the row "Not seen yet" in the note and move on.

**W8. Joint flight scenes, owner present ONLY** (rows `gss_gravship`, `fw_flyer_river`): prepare the saves and **do
not step time**. 🔴 *"For the third time, do not do live testing of flyers without a human present."* One save has a
flyer beside a river (`RM_fw_flyer_owner_walk`). The other has a small gravship with two masts linked by a span on its
deck (`RM_gss_gravship_owner_walk`). He runs them.

## After he walks

- Prove the sheet wrote before using it: `serve_sheet.py --decisions <json> --status` must show `touchedBySheet: true`
  (review-sheets §8). Read the overrides as a group (`--overrides`).
- The art sheets go through `art.py enact` (dry run, then `--apply`). The decisions sheet's Change notes become items
  (`rimflow file`), and the Approve rows close the matching L4 criteria (`rimflow verify … --level L4 --owner-said`).
- Restore the mod list and Mod Settings backups, and release the bridge.
