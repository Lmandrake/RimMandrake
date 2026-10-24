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
