# BENCH_REBOOT_HANDOFF_202609191902 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609191505`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**The instrument that lies here is the ART PIPELINE'S ROUTING, and only a human eye
catches it.** `cea007c3a` bulk-installed 152 PNGs across ~40 ArtOverride mods. At
least **three are on the wrong creature**: a rusty bipedal droid was binding to the
vorrugath's texPath, and the owner then found grank and greater krayt dragon himself.
🔑 A mis-route passes every automated check there is — the art is valid, gate-passed,
correctly named and correctly sized. It is simply the wrong animal. The remaining
~79 stems are UNVERIFIED and the sheet to clear them is live (below).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- 🔴 **Three mis-routed sprites confirmed so far, ~79 stems unjudged.** His sheet is
  SERVED and mid-review — see the running-process note below. Three verdicts are
  already saved to disk.
- **The Pyrelands is now 100% our own defs** — 14 records, zero donor defNames, read
  from the running game's post-patch dump, not from a patch file. His ruling
  ("use OUR creatures, not the donor references") is live and verified.
- ⚠️ **`AA_Razorjack` still spawns in the WORLD**, added by another mod to `Wetland`,
  `ZBiome_AlpineMeadow` and `ZBiome_Marsh`. Not our content, but it sits against his
  "any donors cut, period". 🔑 Worth measuring whether those `ZBiome_*` biomes carry
  any tiles on the frozen world — `ZBiome_Grasslands` had **ZERO**, which is the
  defect that started this whole thread.
- **Two creatures now fly that could not before** — `RUT_FireHawk` (30s) and
  `RUT_FireWasp` (10s), on his new standing rule. ⛔ There is **no wing-flap**: flight
  animation needs a frame sequence we do not ship, so judge flight as BEHAVIOUR.
  FOUNDRY currently holds the bridge for `FIREHAWK_FLIGHT_BEHAVIOR_1`, which is
  looking for exactly the render that does not exist.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `ROT_SIZE_REJUDGE_APPLY_1` -- proposed, filed this wave. His 11 re-judged sizes are
  frozen in the decisions file and exist in NO def. NEXT: apply the 11 values from the
  item's table; the mycoid colossus is a CREATURE whose live drawSize is **4**, so set
  12 against 4, not against the 15 older notes imply.
- `MYCOID_COLOSSUS_ART_MISROUTE_1` -- proposed. Droid pulled and undeployed; art owed.
  NEXT: regenerate to his brief (huge multi-legged purplish entity, glowing mushrooms
  from its back) once the Codex weekly quota resets **Mon 2026-09-21 09:32**.
- `ROT_FLORA_FAUNA_VERDICTS_1` / `DEEPS_FAUNA_VERDICTS_1` -- both needs-deploy. XML
  rounds are deployed; their **82 art jobs are all in `artpipe/failed/`** on that same
  quota. NEXT: on Monday, re-file the failed jobs — do NOT re-author them.
- The misroute sweep -- ~79 of 82 rows unjudged. NEXT: nothing, until he reviews; the
  sheet is his to work.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it to LESSONS_INBOX.md the moment it is learned, then cite `(filed: LESSONS_INBOX)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- 🔴 **`serve_sheet.py` prints "opened with explorer.exe" and opens a FILE EXPLORER
  WINDOW, not a browser** — the sheet never appears and the tool reports success.
  Launch Chrome explicitly; confirm by the server log's `GET /` + thumbnail 200s
  (filed: LESSONS_INBOX).
- 🔴 **A review-sheet PREFILL must never emit `writeCount`/`savedBy`/`savedAt`** — a
  subagent-built prefill shipped `writeCount: 0`, forging the one tell that proves the
  human touched the file (filed: LESSONS_INBOX).
- 🔴 **A DEPLOY_HOLD directory pattern matches NOTHING** — holds are FILE paths.
  `Droidworks/ArtIncoming/` matched nothing and all three PNGs shipped. The tool DID
  warn; the warning was filtered out of the output and missed (see: `src/DEPLOY_HOLD.txt`).
- 🔴 **`deploy_custom_mods.py` with no `--mod` can be TRUNCATED by a timeout** and stop
  partway through the alphabet. Mine stopped at "Cuisine" and would have reported
  "only Armoury drifts" — the real answer was 5 mods (filed: LESSONS_INBOX).
- ⚠️ **`measure` is not on PATH** — it lives at
  `~/.claude/skills/measuring-large-artifacts/bin/measure`. The blind-scan hook names
  it by bare name, which does not run (filed: LESSONS_INBOX).
- ⚠️ **A "before" log is not a baseline if it came from an aborted load.** Mine was 801
  lines with 1 error; comparing against it would have made 250 errors look catastrophic.
  The real baseline was a completed load at 262 (filed: LESSONS_INBOX).

## Closed since the last handoff (1)

- `GRASSLANDS_CAST_DEAD_BIOME_1` — 558808979a4cfc6986c0bde7f67dfc0b6749063b

## Filed and still open (4) — the next seat's queue

- `EMBERSCYTHE_PYRELANDS_REHOME_1` — Move RUT_Emberscythe out of RotSporeKit into a Pyrelands mod — owner ruled MOVE, not cut (2026-09-19 question card)
- `VANILLA_XENOTYPE_REMOVAL_ASSESSMENT_1` — Assess the 14 non-Star-Wars xenotypes (Baseliner/Dirtmole/Genie/Highmate/Hussar/Impid/Neanderthal/Pigskin/Sanguophage/Starjack/VRESaurids_Saurid/Waste
- `MYCOID_COLOSSUS_ART_MISROUTE_1` — Vorrugath/mycoid colossus rendered as a DROID; our override art was mis-routed by the bulk install
- `ROT_SIZE_REJUDGE_APPLY_1` — Apply the owner's 11 re-judged Rot sizes, measured against the TRUE numbers not the sheet's false ones

## Commits

```
ff445e0ec rimflow: sync ledger — 4 items closed, ROT_SIZE_REJUDGE_APPLY_1 filed
14c8e0d5f ROT_SIZE_REJUDGE_APPLY_1: file the owner's 11 re-judged Rot sizes as owed work
558808979 Live load 2026-09-19: Pyrelands port + flight verified in the running game
0204e4be3 rimflow: sync ledger (GRAFFITI_VARIANT_COUNTS_1 -- 8 parity jobs filed)
66a0cca4e DEPLOY_HOLD: hold the rescued mis-route renders, as FILE paths not a directory
afb08ef4f modlist: recapture FULL.LATEST at 617 (PYRELANDS_DONOR_PORT_4 cleanup)
3785aac81 Flyers fly: standing rule recorded, fire wasp and fire-hawk given real flight
c1b342131 WildAnimals_Pyrelands.xml: fix stale comment (still said "plus vanilla Boomalope")
84c7c6a90 PYRELANDS_DONOR_PORT_4: remove 4 dead ArtOverride mods (621->617 active)
f537c3462 PYRELANDS_DONOR_PORT_4: delete a false hazard claim I wrote into this item
ca636ebfd rimflow: sync ledger (BRIDGE_DOBILL_FORCE_TOOL_1 closed, DEEPS_FAUNA_MECHANICS_1 root-caused live)
0e55faf50 PYRELANDS_DONOR_PORT_4: file the item the port commits already cited
f38b50542 rimflow: sync ledger (crossref fix confirmed 185->38, game UP)
be0cebd18 rimflow: sync ledger (OFFBIOME_SHEET_RERENDERS_1 claimed/started, findings noted) + derived artifacts
280d9affa PYRELANDS_DONOR_PORT_4: repoint art tooling at the moved sprites
d3aa2332b PYRELANDS_DONOR_PORT_4: cast our four, retire the identity patches
ca83da145 PYRELANDS_DONOR_PORT_4: four Pyrelands creatures become our own defs
c4fbc27d3 Rot size re-judge frozen; colossus droid art pulled and rescued
4d85ca601 rimflow: sync ledger (VENTFORGE_KILN_RECIPEWIRING_HELD_1, DEPLOY_HOLD_SAME_BUCKET_BLIND_1 closed) + derived artifacts
2dc1483a0 VENTFORGE_KILN_RECIPEWIRING_HELD_1 + DEPLOY_HOLD_SAME_BUCKET_BLIND_1
... 14 more: git log --oneline 6839a78c4..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     confirm FireHawk wing-flap render tree in-game (FIREHAWK_FLIGHT_BEHAVIOR_1)

Uncommitted (replace each <<< not mine >>> with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/codebase_health.html   <<< health publisher (auto), not mine >>>
 M Transient/codebase_health.json   <<< health publisher (auto), not mine >>>
 M Transient/codebase_health_artifact.html   <<< health publisher (auto), not mine >>>
A  infrastructure/artpipe/daemon_run_20260916_bench_restart.log   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_hawkbat_v1_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kinrath_v1_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/canon_kreetle_v1_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_closed.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/flowworks_sluicegate_stonemetal_open.manifest.json   <<< artpipe daemon, not mine >>>
R  infrastructure/artpipe/pending/nuitae_a_v1.json -> infrastructure/artpipe/done/nuitae_a_v1.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/nuitae_a_v1.manifest.json   <<< artpipe daemon, not mine >>>
R  infrastructure/artpipe/pending/nuitae_b_v1.json -> infrastructure/artpipe/done/nuitae_b_v1.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/nuitae_b_v1.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v3_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_barbslinger_v4_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_boomsnake_v3_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_gizka_dino_v5_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v3_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_mantistanis_v4b_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_north.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/pyrelands_nuna_female_v1_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/rut_agelesscap_v1.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/rut_agelesscap_v1.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/rut_brewingvessel_v1_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/rut_euphoriccrown_v1.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/twistingthornweed_v1_r2.manifest.json   <<< artpipe daemon, not mine >>>
R  infrastructure/artpipe/pending/yumbulbs_a_v1.json -> infrastructure/artpipe/done/yumbulbs_a_v1.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/yumbulbs_a_v1.manifest.json   <<< artpipe daemon, not mine >>>
R  infrastructure/artpipe/pending/yumbulbs_b_v1.json -> infrastructure/artpipe/done/yumbulbs_b_v1.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/done/yumbulbs_b_v1.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/anooba_toyfig_b_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/codexcal_mantrap_r4.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/dragonsnake_toyfig_b_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/nysyllin_v1_r2.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/nysyllin_v1_r2.manifest.json   <<< artpipe daemon, not mine >>>
 M infrastructure/artpipe/failed/orray_v3_south.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/tentacular_toyfig_b_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/terramorph_toyfig_b_east.manifest.json   <<< artpipe daemon, not mine >>>
A  infrastructure/artpipe/failed/wyyyschokk_toyfig_b_east.manifest.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/crystalcap_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/crystaltipbrambles_b_v1.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_drinker_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_drinker_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_drinker_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_gembug_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_gembug_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_gembug_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_glowbulb_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_glowbulb_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_glowbulb_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_grabber_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_grabber_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_grabber_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_megapleura_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_megapleura_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_megapleura_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_mossbeetlelarvae_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_mossbeetlelarvae_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_mossbeetlelarvae_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_shatterjaw_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_shatterjaw_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_shatterjaw_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_soulchime_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_soulchime_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/deeps_soulchime_v2_south.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/dulciscropitem_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/dulcisgrown_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/dulcisharvested_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/dulcisimmature_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/fungusfern_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/fungusfern_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/fungusfern_c_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/fungusfern_d_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/gleamtip_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/gleamtip_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/greyladygrown_c_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/greyladyimmature_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_c_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonechunk_d_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonehuge_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonehuge_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstoneitem_c_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonelarge_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonelarge_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonemedium_c_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonesmall_c_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonesowableimmature_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstoneterrain_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/lanternstonewallicon_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/luminousspout_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/luminousspout_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/mycelium_a_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/mycelium_b_v1.json   <<< artpipe daemon, not mine >>>
D  infrastructure/artpipe/pending/mycelium_c_v1.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_agaricusdomecap_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_agarilux_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_agariluxprime_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_agaripawn_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_agaripawn_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_agaripawn_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_agelesscap_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_arbuscularmycorrhiza_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_arpeau_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_blastpodshroom_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_bleedingtooth_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_brightbell_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_bryolux_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_crimsoncap_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_dewshrooms_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_dribblingcap_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_dulcisplant_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_euphoriccrown_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_falsefruit_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_flakespirefungus_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_fruitingbodies_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_fungalweevil_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_furnacecap_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_giantagarilux_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_glowingagarilux_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_glowstool_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_greylady_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_lilacbeacon_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_mortalmorelplant_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_mycoidcolossus_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_nogtyl_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_nuitae_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_palemoss_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_paletree_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_pusmelon_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_recurvedstropharia_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_regenerantveil_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_rustpuff_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_sagecrust_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_shinecap_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_skulltop_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_slimypholiota_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_swarmling_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_swarmling_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_swarmling_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_violetwimple_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_wildpawn_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_wildpawn_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_wildpawn_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_wildpod_v2_east.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_wildpod_v2_north.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_wildpod_v2_south.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_witchesoyster_v2.json   <<< artpipe daemon, not mine >>>
 D infrastructure/artpipe/pending/rot_wrinklecap_v2.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_falsefruit_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_furnacecap_plant_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_gene_furnaceblood_icon_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_grownfurnace_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_liveingredient_agelesscap_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_liveingredient_euphoriccrown_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_liveingredient_regenerantveil_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_liveprep_toxicinjection_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_livingfurnacecap_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_palemoss_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_paletree_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_regenerantveil_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_symbiont_mycoid_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_symbiont_nightwake_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_symbiont_quickflesh_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_symbiont_sheenblood_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_tea_agereversal_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_tea_bioregeneration_v1.json   <<< artpipe daemon, not mine >>>
AD infrastructure/artpipe/pending/rut_tea_pleasure_v1.json   <<< artpipe daemon, not mine >>>
MM infrastructure/artpipe/registry.jsonl   <<< artpipe daemon, not mine >>>
MM infrastructure/artpipe/throughput.jsonl   <<< artpipe daemon, not mine >>>
 M infrastructure/state/codebase_health_last.json   <<< health publisher (auto), not mine >>>
?? "\\\\wsl.localhost\\Ubuntu\\tmp\\tools_dump.txt"   <<< stray UNC-path scratch file, not mine — safe to delete >>>
?? deployed/config/ModsConfig.before-tier-oracle.xml   <<< not mine >>>
?? deployed/config/ModsConfig.before-tier-stagedlore.xml   <<< not mine >>>
?? deployed/config/ModsConfig.before-tier-warlab.xml   <<< not mine >>>
?? infrastructure/artpipe/failed/deeps_drinker_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_drinker_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_drinker_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_drinker_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_drinker_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_drinker_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_gembug_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_gembug_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_gembug_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_gembug_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_gembug_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_gembug_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_glowbulb_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_grabber_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_grabber_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_grabber_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_grabber_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_grabber_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_grabber_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_megapleura_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_megapleura_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_megapleura_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_megapleura_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_megapleura_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_megapleura_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_mossbeetlelarvae_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_shatterjaw_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_soulchime_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_soulchime_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_soulchime_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_soulchime_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_soulchime_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/deeps_soulchime_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_bolotaur_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_fulgurite_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_fulgurite_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/offbiome_gualaar_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaricusdomecap_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaricusdomecap_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agarilux_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agarilux_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agariluxprime_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agariluxprime_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaripawn_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaripawn_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaripawn_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaripawn_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaripawn_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agaripawn_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agelesscap_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_agelesscap_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_arbuscularmycorrhiza_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_arbuscularmycorrhiza_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_arpeau_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_arpeau_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_blastpodshroom_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_blastpodshroom_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_bleedingtooth_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_bleedingtooth_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_brightbell_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_brightbell_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_bryolux_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_bryolux_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_crimsoncap_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_crimsoncap_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_dewshrooms_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_dewshrooms_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_dribblingcap_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_dribblingcap_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_dulcisplant_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_dulcisplant_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_euphoriccrown_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_euphoriccrown_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_falsefruit_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_falsefruit_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_flakespirefungus_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_flakespirefungus_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fruitingbodies_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fruitingbodies_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_fungalweevil_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_furnacecap_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_furnacecap_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_giantagarilux_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_giantagarilux_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_glowingagarilux_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_glowingagarilux_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_glowstool_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_glowstool_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_greylady_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_greylady_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_lilacbeacon_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_lilacbeacon_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mortalmorelplant_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mortalmorelplant_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_mycoidcolossus_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_nogtyl_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_nogtyl_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_nuitae_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_nuitae_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_palemoss_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_palemoss_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_paletree_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_paletree_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_pusmelon_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_pusmelon_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_recurvedstropharia_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_regenerantveil_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_regenerantveil_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_rustpuff_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_rustpuff_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_sagecrust_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_sagecrust_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_shinecap_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_shinecap_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_skulltop_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_skulltop_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_slimypholiota_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_slimypholiota_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_swarmling_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_swarmling_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_swarmling_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_swarmling_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_swarmling_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_swarmling_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_violetwimple_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_violetwimple_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpawn_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpawn_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpawn_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpawn_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpawn_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpawn_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpod_v2_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpod_v2_east.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpod_v2_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpod_v2_north.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpod_v2_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wildpod_v2_south.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_witchesoyster_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_witchesoyster_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wrinklecap_v2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rot_wrinklecap_v2.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_falsefruit_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_falsefruit_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_furnacecap_plant_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_furnacecap_plant_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_gene_furnaceblood_icon_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_gene_furnaceblood_icon_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_grownfurnace_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_grownfurnace_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveingredient_agelesscap_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveingredient_agelesscap_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveingredient_euphoriccrown_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveingredient_euphoriccrown_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveingredient_regenerantveil_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveingredient_regenerantveil_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveprep_toxicinjection_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_liveprep_toxicinjection_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_livingfurnacecap_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_livingfurnacecap_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_palemoss_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_palemoss_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_paletree_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_paletree_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_regenerantveil_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_regenerantveil_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_mycoid_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_mycoid_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_nightwake_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_nightwake_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_quickflesh_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_quickflesh_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_sheenblood_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_symbiont_sheenblood_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_tea_agereversal_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_tea_agereversal_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_tea_bioregeneration_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_tea_bioregeneration_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_tea_pleasure_v1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/failed/rut_tea_pleasure_v1.manifest.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_scratches_p1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_scratches_p2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_scratches_p3.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_tally_p1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_tally_p2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_tally_p3.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_warn_p1.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/graffiti_warn_p2.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/offbiome_bolotaur_v3_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/offbiome_fulgurite_v3.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_east.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_north.json   <<< artpipe daemon, not mine >>>
?? infrastructure/artpipe/pending/offbiome_gualaar_v3_south.json   <<< artpipe daemon, not mine >>>
?? infrastructure/state/.rimflow_conc_97j8px_9/   <<< not mine >>>
?? infrastructure/state/cherrypicker/CherryPicker.PRESWAP.20260911_234759.xml   <<< not mine >>>
```

