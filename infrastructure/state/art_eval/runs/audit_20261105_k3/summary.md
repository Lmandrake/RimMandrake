# art_eval run audit_20261105_k3

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Gembug__Green_Jewelbug | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.6 | canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256 |
| RM_Gembug__Red_Jewelbug | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.5 | canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256 |
| RM_Gembug__Yellow_Jewelbug | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.4 | canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256 |
| RM_Dakkra | r1 | creature/walker | WEAK | regen | **REGEN** | 113.1 | opus band WEAK (model said good); blocking ['DESC_MISS', 'STYLE_EARTHLY', 'F_INCONSISTENT']; polish ['LEGIB_32']; gpt regen: unsettled ['K2', 'K3'], own blocking ['STYLE_EARTHLY', 'F_INCONSISTENT', 'F_INCONSISTENT']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |

## One line each for the owner
- RM_Gembug__Green_Jewelbug: HOLD_CANVAS — canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256
- RM_Gembug__Red_Jewelbug: HOLD_CANVAS — canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256
- RM_Gembug__Yellow_Jewelbug: HOLD_CANVAS — canvas not the shipping rule for drawSize [1.5, 1.5]: east 512x512 != 256x256; north 512x512 != 256x256; south 512x512 != 256x256

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
