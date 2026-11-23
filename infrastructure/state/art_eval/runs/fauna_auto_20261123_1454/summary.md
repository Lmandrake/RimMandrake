# art_eval run fauna_auto_20261123_1454

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Dustveil | r3 | creature/flyer | - | - | **ESCALATE** | 162.9 | facing truth FLAG (facing_scale_lint gate, plan insect): south d_south 1.643 (band 0.69..1.20); north d_north 1.722 (band 0.74..1.36); south feet 0.1289 (band -0.03..0.03); north feet 0.1426 (band -0.03..0.03) |
| RM_Harrok | r3 | creature/walker | WEAK | regen | **ESCALATE** | 89.1 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'ALPHA_HALO']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K3'], own blocking ['F_INCONSISTENT', 'ALPHA_HALO']; still failing after 3 regen rounds — one line to the owner |
| RM_Mirrak | r3 | creature/walker | - | - | **ESCALATE** | 8.5 | facing truth FLAG (facing_scale_lint gate, plan quadruped): south d_south 0.332 (band 0.63..1.33); north d_north 0.448 (band 0.64..1.23) |
| RM_Pirrik | r3 | creature/flyer | WEAK | regen | **ESCALATE** | 92.9 | opus band WEAK (model said weak); blocking ['F_INCONSISTENT', 'ALPHA_HALO']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT', 'ALPHA_HALO']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Dustveil: ESCALATE — facing truth FLAG (facing_scale_lint gate, plan insect): south d_south 1.643 (band 0.69..1.20); north d_north 1.722 (band 0.74..1.36); south feet 0.1289 (band -0.03..0.03); north feet 0.1426 (band -0.03..0.03)
- RM_Harrok: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RM_Mirrak: ESCALATE — facing truth FLAG (facing_scale_lint gate, plan quadruped): south d_south 0.332 (band 0.63..1.33); north d_north 0.448 (band 0.64..1.23)
- RM_Pirrik: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: UNMEASURED, claude-opus-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#3e1892+creature@v3#8de395`
