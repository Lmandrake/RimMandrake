# Purges (20, by card) and FlowWorks pipe-art drafts — BENCH art helper, 2026-10-22

## 1. Purges (card: "Delete all 20 now")
- status: DONE (MEASURED)
- Fresh `art.py enact … --no-deploy` dry run listed 19 purge CONFLICTS + 1 Veermok install conflict (not a purge). The card's "Frog Dog 1" was already purged 2026-10-22T00:06 (0246ec2415ec, via the sheet) — so 19 remained.
- Ran `art.py purge <sha> --owner-said "BY CARD 2026-10-22 ~07:46 PDT: <card text> → Delete all 20 now" --release-keep` for each of the 19 (not `enact --apply`: that would also retire Insectomorph A N/S and file a Kaadu redraw, neither asked). art.py purge has no --by-card flag; the card text is recorded in `said` with a BY CARD prefix.
- Results: Akk 1, HarvesterBeetle 1, JungleRancor 3, KwazelMaw 2, LothWolf 1, Silooth 3, Snoruuk 3, Taozin 5 = 19 purged, bytes_removed true each; 21 keeps released (KwazelMaw carried 2 keeps). Ledger shard: infrastructure/state/art/events/BENCH.jsonl (+40 lines).
- Re-measure: enact dry run now `purge 0; 166 already purged` (was 147), CONFLICTS 1 (Veermok only). None of the 19 was live in a mod (ledger fold) and none of their sha256s matches any PNG under src/**/Textures for those 9 creatures.
- Left: Veermok south conflict (his C note superseded pick B) — not part of this card.

## 2. Blanks left with no art
- status: DONE — ZERO blanks, so NO item filed
- Instrument: `gametex.py def <48 sheet defs>` (live def dump + game Mods folder): 61 body texPaths, every one IN GAME in SWBestiary with east/north/south; 11 alternateGraphics texPaths (Rancor A–E, TetnissCrab A–C, Tukata A–C) IN GAME with all 3 facings. Repo side: all 61 texPaths have south+east PNGs under src/**/Textures. Dessicated corpse art present for all (naming varies).
- Sanity: the purges removed no live picture (section 1), so no blank could come from them.
- Oddity (not a blank from this card): RSW_Rycrit has NO def in src and no texPath in the live dump; src/RimStarWars/SWBestiary/Textures/swanimals/Rycrit/ is an empty folder. Reported, not filed.

## 3. Pipe-art item + drafts
- status: DONE — 19/19 masters (0 failed), conformed + composed + registered; nothing installed
- item PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS filed --by-card "May we draft replacements for FlowWorks pipe art (...)? → Draft all of it", claimed, doing. Prose infrastructure/state/items/PIPE_FITTINGS_REDRAW_NO_MORE_LADDERS.md.
- existing-art check (artpipe_state.py find pump/tee/cross/endcap/coupling/UniversalPipe/liqjoin): no tee/cross/atlas art anywhere; end caps only RM_MessyConduit_Hose_EndCap (hose, other mod); pumps: liqjoin_pump_<look>_a (10-16, side-view, sheet liquid_connections_2026-10-16 prefill only, never ruled) and RM_LiquidPump_ports_arrow_<look> (10-17, side-view). The LIVE pump is now the top-down 4-port hub (RM_LiquidPump_lj_Scrapper, 05:03 today), so side-view pumps do not match it: new looks drawn as reskins of the live hub.
- atlas layout measured: 704 px = 4x4 tiles of 176 px; tile (tx,ty): U = tx&1, R = tx&2, L = ty in {0,1}, D = ty in {0,2} (vanilla linked atlas).
- 19 artpipe jobs filed 08:32 via fill_queue.py (Transient/pile_2026-10-22/pipefit/make_jobs.py -> jobs.json): pipefitraw_{cross,tee,coupling,endcap}_<look>_v1 (1024, top-down) + pumplook_{industrial,modern,futuristic}_v1 (512, canon_reference = live pump; fill_queue dropped that on no_subject rows, patched into the pending JSONs by hand before claim; lesson filed).
- plan: conform.py scales each piece to the atlas pipe (0.10 cell, 176 px/cell); compose.py builds a DRAFT UniversalPipe_Atlas per look (clean body, one coupling per tile edge = one per joint, Tee/Cross hubs, matched caps, polar-warped elbows); register.py -> art ledger variants + texture manifest -> art_sheet.py --textures.

- compose.py: pieces scaled so each stub = the atlas pipe (18 px at 176 px/cell = 0.10 cell); couplings 0.14-0.15 cell tall, end caps clamped to ~0.12; Tee/Cross padded so the junction is the image centre (first pass had the tee sitting below the pipe line — fixed, re-checked by eye). Draft atlases draft/<Look>/UniversalPipe_Atlas.png: live body with 36-56 band columns painted out, half a coupling at every linked tile edge (= one per joint), Tee/Cross hubs, end caps, polar-warped elbows. Test layouts comp/<Look>_layout.png vs comp/<Look>_live_layout.png. Known: a faint ghost of a painted-out band remains on Scrapper's vertical run.
- pumps: Industrial/Modern/Futuristic reskins of the live hub came out matched (same layout and silhouette, look colours on the flanges); cand/<Look>_Pump.png, re-centred to the live pump's fill box.
- registered (register.py): 16 pieces pipefit_<piece>_<look>_v1 (res Pipe/<Look>/Draft/<Piece>), 4 atlases pipefit_atlas_<look>_v1 (res Pipe/<Look>/UniversalPipe_Atlas), 3 pumps pumplook_<look>_v1c (res Pump/<Look>/RM_LiquidPump); masters + copies in D:\ClaudeWork\rimmandrake\artpipe\_artsrc.

## 4. Review sheet (built + gated, NOT served)
- status: DONE — NOT served, NOT sent
- a SEPARATE sheet from joint_fittings_sheet_2026-10-22 (that one is flange/coupler/saddle, a different item and different art paths; mixing them would muddle two rulings).
- `art_sheet.py --textures Transient/pile_2026-10-22/pipefit/textures_manifest.json --name pipe_fittings_atlas`: 7 rows (4 atlas, 3 pump), gate PASS v1; `scaled_review_gate.py check` PASS; `game_art.py deliver` OK.
- path: \\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\biome_ffar\pipe_fittings_atlas_sheet_2026-10-22.html (decisions …decisions.json, prefill only). Serve later with serve_gated.py.
- after his picks: install the atlas through art.py enact; a pump look needs a style def/C# (like the tanks) — FOUNDRY work.

## 5. Commits
- status: pending
