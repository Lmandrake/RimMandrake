# art_eval run facingfix_20261026_r1

| subject | cand | template/module | Opus band | GPT | decision | s | reasons |
|---|---|---|---|---|---|---|---|
| RM_Vhorrin | r1 | creature/swimmer | WEAK | regen | **REGEN** | 83.8 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT'] |
| RSW_Starmaw | r1 | creature/swimmer | WEAK | regen | **REGEN** | 75.6 | opus band WEAK (model said good); blocking ['F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_CoolantEel | r1 | creature/swimmer | WEAK | regen | **REGEN** | 64.0 | opus band WEAK (model said really_bad); blocking ['F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1'], own blocking ['F_INCONSISTENT']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_Dovvik | r1 | creature/walker | WEAK | regen | **REGEN** | 95.0 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; polish []; gpt regen: unsettled ['K1', 'K2', 'K3'], own blocking ['DEPARTURE_MISSING', 'DEPARTURE_MISSING', 'F_INCONSISTENT']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_CanopySwinger | r1 | creature/walker | WEAK | regen | **REGEN** | 85.5 | opus band WEAK (model said good); blocking ['SIBLING_MISMATCH', 'DEPARTURE_MISSING']; polish ['LEGIB_32']; gpt regen: unsettled ['K1', 'K2'], own blocking ['SIBLING_MISMATCH', 'DEPARTURE_MISSING']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_Thrummel | r1 | creature/walker | WEAK | regen | **REGEN** | 105.5 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'F_INCONSISTENT', 'STYLE_EARTHLY']; polish []; gpt regen: unsettled ['K1', 'K3'], own blocking ['DEPARTURE_MISSING', 'STYLE_EARTHLY']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RUT_BrineBattery | r1 | creature/walker | REALLY_BAD | - | **REGEN** | 60.1 | opus band REALLY_BAD (model said really_bad); blocking ['STYLE_EARTHLY', 'DEPARTURE_MISSING', 'DESC_MISS', 'F_INCONSISTENT', 'F_SIZE_JUMP', 'STYLE_CARTOON', 'ALPHA_HALO']; polish []; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_FireWasp__dessicated | r1 | creature/flyer | WEAK | regen | **REGEN** | 92.5 | opus band WEAK (model said good); blocking ['DEPARTURE_MISSING', 'STYLE_EARTHLY']; polish ['FLYER_WINGS_GROUNDED']; gpt regen: unsettled ['K1'], own blocking ['DEPARTURE_MISSING']; REPLACES YOUR KEPT ART (owner card 2026-10-23 06:42) — on the next shadow sheet with a revert |
| RM_Muttavaq | r1 | creature/walker | REALLY_BAD | - | **ESCALATE** | 37.2 | opus band REALLY_BAD (model said really_bad); blocking ['DESC_MISS', 'DEPARTURE_MISSING', 'STYLE_EARTHLY', 'F_INCONSISTENT', 'X_WRONG']; polish []; unreadable ['OURS']; still failing after 3 regen rounds — one line to the owner |

## One line each for the owner
- RM_Muttavaq: ESCALATE — still failing after 3 regen rounds — one line to the owner

Models reported: claude-opus-5-5, claude-sonnet-5-5, gpt-6.1-sol · prompt versions: `departures_brief@v2#9cda88+gpt_targeted_second_look@v1#cb6e32+opus_first_pass@v2#85b8f1+preamble@v2#7130aa+regen_prompt_edit@v1#861700+severity@v4#e9bbe1+creature@v3#fdc520`
