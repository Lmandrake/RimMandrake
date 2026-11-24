# art_eval run fauna_auto_20261123_2053

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_ThozzikColonyQueen | r3 | creature/flyer | - | - | **ESCALATE** | 5.8 | facing truth FLAG (facing_scale_lint gate, plan insect): south d_south 1.214 (band 0.69..1.20); south feet 0.0879 (band -0.03..0.03); north feet 0.0684 (band -0.03..0.03) |
| RSW_Clodhopper | r3 | creature/walker | - | - | **ESCALATE** | 0.2 | facing truth FLAG (facing_scale_lint gate, plan quadruped): south d_south 1.538 (band 0.64..1.35); north d_north 1.362 (band 0.63..1.20); south feet 0.125 (band -0.03..0.03); north feet 0.0703 (band -0.03..0.03) |
| RSW_Gizka | r3 | creature/walker | WEAK | regen | **ESCALATE** | 109.3 | opus band WEAK (model said weak); blocking ['CANON_MISS', 'CANON_MISS', 'F_SIZE_JUMP', 'CANON_MISS', 'F_INCONSISTENT', 'STYLE_CARTOON']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K5'], own blocking ['CANON_MISS', 'CANON_MISS']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_ThozzikColonyQueen: ESCALATE — facing truth FLAG (facing_scale_lint gate, plan insect): south d_south 1.214 (band 0.69..1.20); south feet 0.0879 (band -0.03..0.03); north feet 0.0684 (band -0.03..0.03)
- RSW_Clodhopper: ESCALATE — facing truth FLAG (facing_scale_lint gate, plan quadruped): south d_south 1.538 (band 0.64..1.35); north d_north 1.362 (band 0.63..1.20); south feet 0.125 (band -0.03..0.03); north feet 0.0703 (band -0.03..0.03)
- RSW_Gizka: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: UNMEASURED, claude-opus-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#3e1892+creature@v3#8de395`
