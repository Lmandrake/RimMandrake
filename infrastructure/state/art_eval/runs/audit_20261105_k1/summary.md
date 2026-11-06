# art_eval run audit_20261105_k1

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_PekoPeko__PekoPeko_m_ns | r3 | creature/flyer | WEAK | regen | **REGEN** | 97.5 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert; same picture already REGEN in run audit_auto_20261105_1351 as round 3: round not advanced |
| RM_Ysvaltha | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.1 | canvas not the shipping rule for drawSize [2.5, 2.5]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512 |
| SWPotF_RaceDef_ysalamir__ysalamiri | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.2 | canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256 |
| RM_SparkleechGrub | r1 | creature/walker | WEAK | regen | **REGEN** | 107.5 | opus band WEAK (model said really_bad); blocking ['ALPHA_HALO', 'DESC_MISS', 'DEPARTURE_MISSING', 'F_NORTH_FACE']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['ALPHA_HALO']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |

## One line each for the owner
- RM_Ysvaltha: HOLD_CANVAS — canvas not the shipping rule for drawSize [2.5, 2.5]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512
- SWPotF_RaceDef_ysalamir__ysalamiri: HOLD_CANVAS — canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
