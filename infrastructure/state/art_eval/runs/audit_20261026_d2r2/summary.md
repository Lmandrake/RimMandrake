# art_eval run audit_20261026_d2r2

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Illisk_s | r2 | creature/swimmer | GOOD | - | **ACCEPT** | 32.0 | opus band GOOD (model said good); blocking []; polish ['RES_LOW', 'SCALE_WRONG'] |
| RM_Krannock_n | r2 | creature/flyer | WEAK | strong_accept | **ACCEPT** | 49.6 | opus band WEAK (model said good); blocking ['STYLE_OFF']; polish []; gpt strong_accept: unsettled [], own blocking [] |
| RM_Saluksis_n | r2 | creature/walker | WEAK | regen | **REGEN** | 81.0 | opus band WEAK (model said good); blocking ['F_SIZE_JUMP']; polish ['SCALE_WRONG']; gpt regen: unsettled ['K1'], own blocking ['F_SIZE_JUMP']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_Fuzzviper_n | r2 | creature/walker | WEAK | regen | **REGEN** | 113.1 | opus band WEAK (model said weak); blocking ['F_SIZE_JUMP', 'F_SIZE_JUMP', 'DEPARTURE_MISSING']; polish []; gpt regen: unsettled ['K1', 'K3'], own blocking ['F_SIZE_JUMP']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
