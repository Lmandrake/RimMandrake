# art_eval run audit_20261105_k7

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Falumpaset__FalumpasetE | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.2 | canvas not the shipping rule for drawSize [4.0, 4.0]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512 |
| RSW_Fambaa | r1 | creature/swimmer | - | - | **HOLD_CANVAS** | 0.3 | canvas not the shipping rule for drawSize [8.0, 8.0]: east 512x512 != 1024x1024; north 512x512 != 1024x1024; south 512x512 != 1024x1024 |
| RSW_Fanback__FanbackV_C | r1 | creature/swimmer | WEAK | regen | **REGEN** | 85.9 | opus band WEAK (model said really_bad); blocking ['F_INCONSISTENT', 'CANON_MISS', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT', 'CANON_MISS']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RSW_FeralGrazer | r1 | creature/walker | - | - | **HOLD_CANVAS** | 0.2 | canvas not the shipping rule for drawSize [3.0, 3.0]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512 |

## One line each for the owner
- RSW_Falumpaset__FalumpasetE: HOLD_CANVAS — canvas not the shipping rule for drawSize [4.0, 4.0]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512
- RSW_Fambaa: HOLD_CANVAS — canvas not the shipping rule for drawSize [8.0, 8.0]: east 512x512 != 1024x1024; north 512x512 != 1024x1024; south 512x512 != 1024x1024
- RSW_FeralGrazer: HOLD_CANVAS — canvas not the shipping rule for drawSize [3.0, 3.0]: east 256x256 != 512x512; north 256x256 != 512x512; south 256x256 != 512x512

Models reported: UNMEASURED, claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
