# GPTREDO_JUDGE_UNJUDGED_ROWS — run the art-eval pipeline on GPT-redo rows it has never judged

Source: the six *_ART_AUDIT_GPT_UNKEPT_REDO_LIST findings (GPT second-look says redo; no owner keep). Triage evidence:
`/home/mandrake/.seat-tmp/FOUNDRY/` (st_*.txt art.py status, cls_out.txt regen_eligibility Gate, outcomes.json).

All their live art is REFUSED_REGEN (a render of ours), so no direct regen. Documented intake = art-eval candidate:
`fauna_spec.py build DEF... --out <dir>` then `runner.py run --spec ... --run-id gptredo_<n> --record` (Opus first, GPT only on WEAK).
Never judged by any art_eval run (no decisions.jsonl row), not owner-kept:
- creatures: RSW_Mynock, RSW_Gizka, RSW_Clodhopper, RM_Harrok, RM_Mirrak, RM_Pirrik, RM_Dustveil, RM_Hwelgrue, RM_ThozzikColonyQueen
- plants (flora spec path): RM_AgariluxPrime, RM_Ruskara
Dustveil/Hwelgrue/ThozzikColonyQueen/Gizka/Clodhopper have PROTECTED live slots: check keep status (`art.py status`) before any
REGEN is filed; a protected pick needs its revert record (pipeline HOLD_KEPT).
Not here: RSW_LongtailGorg, RSW_Worrt (ruled owner keeps exist), RM_AmbrosyxFungus (ROT_CARTOON_VARIANT_REPAINT_1).
Judge budget: one Opus helper at a time; coordinate with whoever is judging fauna.

## Outcomes (2026-10-24, FOUNDRY Opus judge, delegated: art-eval)

| def | run | verdict | route |
|---|---|---|---|
| RM_Harrok | gptredo_00 | REGEN | WEAK -> GPT -> regen (filed) |
| RM_Mirrak | gptredo_00 | REGEN | WEAK -> GPT -> regen (filed) |
| RM_Pirrik | gptredo_00 | REGEN | REALLY_BAD: glowing four-winged insect, not a bird (filed) |
| RSW_Gizka (kept) | gptredo_01 | REGEN | WEAK -> GPT STYLE_CARTOON; redraw with revert (filed) |
| RSW_Clodhopper (kept) | gptredo_01 | REGEN | REALLY_BAD, cartoon north (filed) |
| RSW_Mynock | gptredo_01b | REGEN | REALLY_BAD on the Graphic_Single picture (filed). The gptredo_01 Mynock row is VOID: judged undrawn facings |
| RM_Dustveil (kept) | gptredo_02 | REGEN | REALLY_BAD (filed) |
| RM_Hwelgrue (kept) | gptredo_02 | ACCEPT | WEAK -> GPT strong_accept |
| RM_ThozzikColonyQueen (kept) | gptredo_02 | REGEN | WEAK -> GPT F_TOPDOWN (filed) |
| RM_AgariluxPrime (TheRot copy) | gptredo_03 | ACCEPT | |
| RM_AgariluxPrime (UtinniPatches copy) | gptredo_03 | REGEN, NOT filed | shadowed copy -> AGARILUX_PRIME_COPIES_RECONCILE_SPLIT |
| RM_Ruskara a-d | gptredo_04 | ACCEPT | all four variants |

The regen prompts for gptredo_00 and gptredo_01 were refused by the fill_queue gate. They were filed from reworded copies instead; see ART_EVAL_REGEN_FIX_FILING_GATE_REFUSES.
Owed:
- the owner's shadow sheets for gptredo_01, 03 and 04 (ART_EVAL_SHADOW_FIX_PLANT_KEPT_ROWS);
- the kept redraws must be shown with a REVERT once drawn;
- the Mynock install needs a graphicClass decision (MYNOCK_REGEN_INSTALL_NEEDS_GRAPHIC_MULTI).
Evidence: D:\ClaudeWork\rimmandrake\art_eval\gptredo\
