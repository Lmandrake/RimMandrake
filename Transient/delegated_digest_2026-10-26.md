# Delegated calls digest, 2026-10-26

Calls agents took for you today (ledger why "delegated:", plus art judge decisions). Say "overturn <item>" in any words and the seat undoes it and adds the reason to the judge brief. Silence is not approval. Verdict files: D:\Luke\dev\RimMandrake\infrastructure\state\delegated\2026-10-26\

## Art (judge agents)

- INSTALLED over your kept art, you said "Yes, but show me after" (card 2026-10-23): RM_CoolantEel north. Judge: Opus scored it weak (size jump flagged), then GPT strong-accepted. Why: old north was half the size of the south. Look: D:\Luke\dev\RimMandrake\Transient\biome_ffar\art_eval_shadow_facingfix_20261026_r2_sheet_2026-10-26.html. Reverse: line 2 of D:\ClaudeWork\rimmandrake\facing_backlog_20261026\redraw\revert\REVERT_ARGV.txt (old bytes in the revert folder beside it).
- INSTALLED: RM_Vhorrin north (WeepingStones). Judge: Opus alone rated it good (no GPT second look needed). Why: old north was a top-down view of the fish, not a rear view. Same sheet. Reverse: line 1 of the same REVERT_ARGV.txt.
- NOT INSTALLED, 7 sets failed 3 regen rounds and are escalated: Dovvik, CanopySwinger, Thrummel, BrineBattery, FireWasp-dessicated, Starmaw, Muttavaq. Item FACING_SETS_REDRAW_WHOLE_SET_ESCALATED (needs you or a whole-set redraw). Candidates on the live, r1, r2 sheets in D:\Luke\dev\RimMandrake\Transient\biome_ffar\ (art_eval_shadow_facingfix_20261026_*_sheet_2026-10-26.html). Nothing to reverse.
- Facing audit of 29 regenerated creature sets (Opus-based judge): 20 pass, 9 fail; table D:\ClaudeWork\rimmandrake\facing_backlog_20261026\judge.md. Filed under ARTPIPE_FACING_COHERENCE_1; no art changed by this.
- Foreign-copy audit (FOUNDRY, judge eyeball plus art-eval): 4 renders that were copies were thrown out and re-judged: Runyip east REGEN, Muttavaq south a/b REGEN, Venomvine ACCEPT but not installed (raw, unfinalized). Item ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS. Nothing installed, nothing to reverse.
- RM_Grellik size (FOUNDRY, 146f2dfc9c): adult drawSize 4 to 1.75, judged on true-scale panels beside a colonist (D:\ClaudeWork\rimmandrake\grellik_judge\). Reverse: set drawSize back to 4 in the Grellik def.
- Leather picks (FOUNDRY, 3123bbb1ff and later): RM_Baseopsis, Holcorobeus, Protosolpuga, Termitotron get RM_MediumChitin; two pupae take their adult's chitin. A second judge upheld 6 of 6 (verdict RACES_JUDGE_LEATHER_PICKS_DELEGATED.json). Then 29 more races given leather by class (bird, monkey, pinniped, quadruped; published d04fe6e1a5, 61dcfdcc32, 295c4ef0dd, 475b434c91, 1a03259941); about 9 quadrupeds left alone as uncertain. Reverse: revert those commits.

## Design calls (agents, with reasons)

- Unpowered shield bubble blocks nothing (SHIELDGEN_DECIDE_INTERCEPT_UNPOWERED, c7f5b6a928). Why: your "power is the fuel" line. Judge: UPHOLD.
- Striking a Cathedral machine voids that pawn's own pass (CATHEDRALPASS_DECIDE_RETALIATION, c7f5b6a928). Why: arc spec section 3. Judge: mechanic UPHELD, message text REVISE (follow-up CATHEDRALPASS_FIX_REVOKE_MESSAGE_REGISTER). Verdict: DESIGNJUDGE_VERIFY_SHIELD_AND_PASS.json.
- Chill seabed fire ban extended: fuelled cooking and fuelled power stop without pumped air (345da77cf4); attached fire and meltdown flame also banned (d6530b895c). Why: your 2026-09-27 "total ban". Reverse: revert those shas.
- Sith inquisitor aid only for hostile factions (dc446ffc7b); Tetchik gate also admits at the map edge with 10 or more Glowers (2eebba6e5486); dune-track erase widened to weather sand (4867d0b64e); pooler counts vanilla heaters (cafb80cbc5).
- Tooling designs (BENCH): known-good skip and daily WASTE metrics (24b90ea28b, e10b2468f8).
- Sequencing (RIM-2, "B" picks logged 18:04 yesterday): flora step 3 may run before your grades; lore arbitration by canon references plus an agent proposal you spot-check; desiccated families start only where biome art is final.

## Needs you (not delegable)

- 7 escalated facing sets above (whole-set redraw or your call).
- DIG_SPOIL_DECIDE_FOUR_DEFAULTS_HELD: 4 dig-spoil defaults BENCH took, awaiting your check.
- Judge not yet run on the AaroxisDendoria and RoyalRhino pupa picks was later covered (6 of 6 upheld); the unsure quadruped exemptions are listed in the lint STRICT_EXEMPT list.

Not surfaced in RimPulse: its "since you left" digest (src/RimMandrake/Utils/pulse/pulse.py) is a different digest and does not read this file.
