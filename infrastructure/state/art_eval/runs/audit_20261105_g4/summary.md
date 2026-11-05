# art_eval run audit_20261105_g4

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Dragonsnake__Dragonsnake_B_n | r3 | creature/swimmer | REALLY_BAD | - | **ESCALATE** | 50.7 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'OWNER_NOTE_IGNORED']; polish ['LEGIB_32']; still failing after 3 regen rounds — one line to the owner |
| RSW_Dragonsnake__Dragonsnake_C_n | r3 | creature/swimmer | REALLY_BAD | - | **ESCALATE** | 44.8 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP']; polish ['LEGIB_32']; still failing after 3 regen rounds — one line to the owner |
| RSW_Dragonsnake__Dragonsnake_D_n | r3 | creature/swimmer | REALLY_BAD | - | **ESCALATE** | 42.1 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish ['LEGIB_32', 'RES_LOW']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RSW_Dragonsnake__Dragonsnake_B_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RSW_Dragonsnake__Dragonsnake_C_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RSW_Dragonsnake__Dragonsnake_D_n: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5 · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
