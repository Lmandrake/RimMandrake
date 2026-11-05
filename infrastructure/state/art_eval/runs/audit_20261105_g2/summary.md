# art_eval run audit_20261105_g2

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_CrimsonOpee_ns | r3 | creature/swimmer | WEAK | regen | **REGEN** | 106.0 | opus band WEAK (model said weak); blocking ['F_TOPDOWN', 'F_INCONSISTENT', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['F_TOPDOWN', 'F_INCONSISTENT', 'DEPARTURE_MISSING']; same picture already REGEN in run audit_auto_20261028_1301 as round 3: round not advanced |
| RSW_Blarth__Blarth_Swimming_n | r3 | creature/swimmer | WEAK | regen | **ESCALATE** | 120.0 | opus band WEAK (model said good); blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'DESC_MISS']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['F_INCONSISTENT', 'F_SIZE_JUMP', 'F_TOPDOWN']; still failing after 3 regen rounds — one line to the owner |
| RSW_Blixus | r2 | creature/swimmer | WEAK | regen | **REGEN** | 98.2 | opus band WEAK (model said good); blocking ['ALPHA_HALO', 'CANON_MISS', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K2'], own blocking ['ALPHA_HALO']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert; same picture already REGEN in run audit_auto_20261028_1301 as round 2: round not advanced |

## One line each for the owner
- RSW_Blarth__Blarth_Swimming_n: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v3#4e4c26+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v3#2337d2+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
