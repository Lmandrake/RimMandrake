## spec
Found by the Graffiti 0.1.0 blind challenge, cycle 2 (RIMMANDRAKE_JUDGE_GRAFFITI_BLIND_CYCLE_TWO_TESTS_FIRST), 2026-11-17. Class: **Problem**, bar `ugliness_visible`.

**Criterion:** tree.json ugliness_visible: when the same hand painted both, the scrawl inspects as uglier (false pass: 'the scrawl is uglier only in its def, while the same hand's scrawl and tally inspect alike'); T_UGLINESS_OFFLINE, a decider, claims 'the Beauty stat and both inspect lines read NetBeauty' and that NetBeauty takes MarkBeauty of the mark's form

**Evidence:**
- planted fault PF_C_NETBEAUTY_SCRAWL_AS_TAG (Filth_Mark.NetBeauty passes `ext.form == GraffitiForm.Scrawl ? GraffitiForm.Tag : ext.form`: an awful hand's scrawl inspects -6, the same as its tally) left T_UGLINESS_OFFLINE green: lane2/planted_results.jsonl first row for it
- planted fault PF_C_STATPART_KEEPS_DEF (StatPart_GraffitiCraft sets `val = m.NetBeauty * 0f + val`: the Beauty stat is the def's -15/-3, the false pass the bar names) left it green
- cause: the source read accepted any first argument containing the word `form` and any statement starting `val = m.NetBeauty`
- red: python3 design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/catch_check.py --fault PF_C_NETBEAUTY_SCRAWL_AS_TAG --test T_UGLINESS_OFFLINE rc 1 (MISSED) on the parent of dad3e902ac; lane2/fixes.jsonl

**Smallest fix:** tighten the read: MarkBeauty's first argument is a bare <ext>.form with <ext> = def.GetModExtension<ModExtension_Graffiti>(); the StatPart and the two inspect lines take NetBeauty whole (`= NetBeauty;`); both faults added as source mutants so the read is shown able to refuse every run

Record: `design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/faults.json`.

## criteria
T_UGLINESS_OFFLINE red on both planted faults and green on the shipped source

## verify
Acceptance test: `python3 design/concepts/Graffiti/version/blind_challenge/cycle_2/lane2/catch_check.py --fault PF_C_NETBEAUTY_SCRAWL_AS_TAG --test T_UGLINESS_OFFLINE` and `--fault PF_C_STATPART_KEEPS_DEF` each rc 0 (CAUGHT), and `python3 src/RimMandrake/Utils/selftest_graffiti_ugliness.py` rc 0. Watched fail on the base (rc 1, MISSED) and pass at dad3e902ac: `lane2/fixes.jsonl`. FIXED dad3e902ac9d2e7c9a85e0a6d088e2047144ad4d.
