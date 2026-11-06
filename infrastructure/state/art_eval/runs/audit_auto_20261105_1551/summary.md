# art_eval run audit_auto_20261105_1551

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| SWPotF_RaceDef_ysalamir__ysalamiri | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.2 | canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256 |
| RM_Krissek | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 71.1 | opus band WEAK (model said good); blocking ['STYLE_OFF']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking []; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_OcularJelly__RM_OcularJelly_Bell | r1 | creature/walker | WEAK | strong_accept | **ACCEPT** | 47.0 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt strong_accept: unsettled [], own blocking [] |
| RM_TheUnfinished__RM_TheUnfinished_RM_TheUnfinished | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 54.3 | opus band REALLY_BAD (model said really_bad); blocking ['DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'STYLE_EARTHLY']; polish []; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |

## One line each for the owner
- SWPotF_RaceDef_ysalamir__ysalamiri: HOLD_CANVAS — canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
