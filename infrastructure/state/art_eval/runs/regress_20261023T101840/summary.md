# art_eval run regress_20261023T101840 (TEST — nothing installed, no rounds counted)

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Shadefern | B | plant/bush | GOOD | - | **ACCEPT** | 21.1 | opus band GOOD (model said good); blocking []; polish ['STYLE_EARTHLY', 'WANTS_VARIANTS'] |
| RM_Huldu | C | creature/swimmer | REALLY_BAD | - | **REGEN** | 49.7 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'F_TOPDOWN', 'STYLE_CARTOON']; polish ['LEGIB_32'] |
| RM_Ssurr | B | creature/walker | REALLY_BAD | - | **REGEN** | 55.9 | opus band REALLY_BAD (model said really_bad); blocking ['F_INCONSISTENT', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'STYLE_CARTOON', 'DEPARTURE_MISSING', 'DEPARTURE_MISSING']; polish [] |
| RM_Vellak | B | creature/pack | - | - | **HOLD_ERROR** | 6.8 | opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles) |

## One line each for the owner
- RM_Vellak: HOLD_ERROR — opus: You've hit your session limit · resets 1:10pm (America/Los_Angeles)

Models reported: claude-opus-5-5, claude-sonnet-5-5 · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v3#950903+plant@v3#bf05d6`
