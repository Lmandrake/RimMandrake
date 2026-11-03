# UNPROVEN_LIVE_LEGS_TRIAGE_1 - Unproven live legs triage

Filed 2026-10-07 from the GREEN-MIN / L2 sweeps (Transient/*_20261007.md).

## spec
Four items carry UNPROVEN live legs that nobody has triaged. Triage each as: bridge-measurable now, needs a tool, needs a generated map, or owner-eyes. (1) CAULDRON_ENRICHMENT_LIVE_PROOF_1 A4: assay grade string + vexxiss poisoned-water letter legs. (2) FeverWood A3/A4: UI-click legs (bridge click fails silently; use system_click). (3) RUSTCATHEDRAL A5-A9: need a generated Cathedral map (0 tiles until repaint; use a quicktest map generated as the biome if the tool can). (4) FORGE_ENRICHMENT_QUICKTEST_1 A1-A4: keel brace fuel, spunstone reveal, phase voices, dhuvvox clock on a Forge map. Existing item files already hold the criteria; this item adds only the triage verdicts.

## verify
Read each item with rimflow show, attempt the cheapest probe, record verdict per leg on the owning item via note.

## criteria
A1: each of the four items has a rimflow note with a per-leg verdict and NEXT.
A2: legs that are bridge-measurable are run and recorded; the rest are re-filed as needs owner/map/tool.

## live check
New mechanism never seen: the listed legs are mechanisms never once observed running.

NEXT: claim this item and start with criterion A1.

## triage verdicts (2026-11-03; each also a note on its item)
| item | leg | verdict | next |
|---|---|---|---|
| CAULDRON_ENRICHMENT_LIVE_PROOF_1 | A4 assay + letter OFF arms | bridge-measurable now (bars flora.assay_toggle_off, water.water_letter_toggle_off, water.water_poison_toggle_off; PASS in the bench live run 2026-10-19) | live proof A3 here |
| CAULDRON_ENRICHMENT_LIVE_PROOF_1 | A4 nettle-gardens OFF arm | needs a tool (no component) | CAULDRON_NETTLE_OFFARM_BUILD_TWO_OF_THREE |
| FEVERWOOD_BROOD_RANSOM_1 | A3 tally, A4 gift | needs a tool (generic gizmo-invoke [Tool] + tally read + components; system_click is a pixel hunt no proof reads) | BROOD_GIZMO_TOOL_BUILD_CLICKS_GO_NOWHERE |
| FEVERWOOD_BROOD_RANSOM_1 | A6, A7 (outside this spec) | needs the campaign world (Sporefall) | stays owed |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1 | A5-A9 | needs a tool, NOT a map: `live_site.py --biome RM_RustCathedral` makes the map today; no live component exists | CATHEDRAL_BASEFINISH_ROWS_BUILD_MAP_EXISTS |
| FORGE_ENRICHMENT_QUICKTEST_1 | A3, A4 | half bridge-measurable now (voices off / Rain cue; dhuvvox countdown + slowing), rest needs component extensions | live proof A4 here; FORGE_VOICE_ROWS_FINISH_HALF_SUNG |

Proof: `python3 src/RimMandrake/Utils/selftest_unproven_legs_triage.py`; live: `infrastructure/state/live_proofs/UNPROVEN_LIVE_LEGS_TRIAGE_1.txt` (tool `src/RimMandrake/Utils/northstar_bar_proof.py`).
