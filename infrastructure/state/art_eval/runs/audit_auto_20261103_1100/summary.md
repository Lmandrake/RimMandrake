# art_eval run audit_auto_20261103_1100

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RSW_Dragonsnake__Dragonsnake_A_n | r3 | creature/swimmer | REALLY_BAD | - | **ESCALATE** | 44.2 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_TOPDOWN', 'F_INCONSISTENT', 'CANON_MISS', 'OWNER_NOTE_IGNORED', 'DEPARTURE_MISSING']; polish []; still failing after 3 regen rounds — one line to the owner |
| RSW_Dragonsnake__Dragonsnake_B_n | r3 | creature/swimmer | REALLY_BAD | - | **ESCALATE** | 40.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT', 'OWNER_NOTE_IGNORED', 'DEPARTURE_MISSING']; polish []; still failing after 3 regen rounds — one line to the owner |
| RSW_Dragonsnake__Dragonsnake_C_n | r3 | creature/swimmer | WEAK | regen | **ESCALATE** | 83.6 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP']; still failing after 3 regen rounds — one line to the owner |
| RSW_Dragonsnake__Dragonsnake_D_n | r3 | creature/swimmer | REALLY_BAD | - | **ESCALATE** | 45.2 | opus band REALLY_BAD (model said weak); blocking ['F_SIZE_JUMP', 'F_INCONSISTENT']; polish ['LEGIB_32']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RSW_Dragonsnake__Dragonsnake_A_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RSW_Dragonsnake__Dragonsnake_B_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RSW_Dragonsnake__Dragonsnake_C_n: ESCALATE — still failing after 3 regen rounds — one line to the owner
- RSW_Dragonsnake__Dragonsnake_D_n: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
