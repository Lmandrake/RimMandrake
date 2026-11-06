# art_eval run audit_20261105_m6

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Maguana | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.2 | canvas not the shipping rule for drawSize [2.5, 2.5]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512 |
| RSW_Maligoat__MaligoatMale | r2 | creature/walker | WEAK | regen | **REGEN** | 78.7 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RSW_Manka | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.2 | canvas not the shipping rule for drawSize [3.0, 3.0]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512 |

## One line each for the owner
- RSW_Maguana: HOLD_CANVAS — canvas not the shipping rule for drawSize [2.5, 2.5]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512
- RSW_Manka: HOLD_CANVAS — canvas not the shipping rule for drawSize [3.0, 3.0]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
