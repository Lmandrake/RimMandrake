# 5. Fable independent review of the judge "flaws not polish" proposal

Status: COMPLETE. Reviewer: Fable builder, 2026-11-17. Nothing but this file was changed; nothing was committed. Section 2 was written before files 2, 3 and 4 were read and is unedited.

## 1. Verdict in ten lines or fewer

- Adopt a smaller set, not the nine: four rules (A name the broken build, B one search and one repair look, C numbers are examples, D hints are not bars) plus two bug fixes. Section 5.
- GPT's diagnosis is sound and I reached most of it alone (section 2). Its nine rulings merge to four; its ten edits are an expert system with no knobs. Build four now in cut-down form, the rest later or never.
- Most findings were real flaws. A flaws-only judge still sends Pyrelands back at looks 1 to 3. The saving is in looks 4, 7 and 8.
- The wind finding was a real flaw. The owner is wrong there. He is right about "under half" and "almost nothing burns".
- The sort into "flaw" and "more proof" does not hold steady on the contested cases (GPT changed four of its own). So the levers must be structural: scope, look count, who confirms.
- Two code faults are plain bugs and should be fixed whatever is decided: a `polish` gap can block; a repaired gap stays refused for want of a claim form.
- Biggest risk: `covered` is read as "works" while the live reads are UNRUN. Pyrelands' wind and flood tests have never run once. With one search, what the first look misses ships unless play catches it.
- Pyrelands: leave it covered, do the pending restamp and one-entry look, run the live reads. Section 8.

## 2. My own diagnosis and rules, written before reading the proposals (unedited first draft)

Written after reading file 1 and the dossier (01, 03 lines 1-247, round1_prompt.txt) and the live prompt and code. Files 2, 3 and 4 were unread when this was written. Short names: "01" is `/mnt/d/ClaudeWork/rimmandrake/conductor/judge_rethink_20261117/01_pyrelands_experience.md`.

### 2.1 What I think happened

1. The owner's bars are loose. The strictness is made below him. His burn-line bar says "moving like a natural grass fire, with a visibly scorched trail behind it" [measured: 01 lines 5-82]. No bar of his says "under half" or "almost nothing".
2. The judge is not asked to judge his bars. It is asked to cover "every in-scope capability in record.json's inventory and every leaf in tree.json" [measured: `src/RimMandrake/rimflow/coverage_judge.py` prompt, lines ~967-1021]. Pyrelands has about 21 owner bars but 24 leaves, 30 scenes and 21 inventory rows [measured: script over the mod's tree.json, scenes.json, record.json]. Most of looks 1 to 4 are "shipped code has no scene": furnace-beast heat immunity, the hide bank, a table for all 43 saved settings, the plant allowlist, the scanner payload [measured: 01 lines 280-470]. The code moved under the concept (a 74-commit landing) and the judge chased it.
3. The Designer prompt orders the pedantry. Each leaf must say "what it reads as and what it must not read as", and name a `false_pass`, "the worker's cheapest way to fake this leaf" [measured: `roles/designer_write.md` lines 37-38]. 21 of 24 leaves carry a must-not clause [measured: same script]. The judge prompt then makes each clause a "part" that needs its own scene with a control. So one loose bar becomes three or four blocking demands. The "flood" must-not on the burn line is the Designer's clause, not the owner's bar.
4. The control demand itself is the owner's. His own words 2026-11-03: "the ladder is installed in a pit that he can climb without the ladder, so that's not a good test." [measured: `roles/designer_scene_contract.md`]. So "this test cannot fail" is a real flaw class and he asked for it. It is not peevishness.
5. The numbers come from the refusal format. A refusal must carry a `would_pass` that a script can check. That forces the judge to invent a concrete threshold ("below one half", "about 0", days 1, 2, 3) [measured: 01 look 7]. The fixer then copies the example as if it were the bar. One judge example became a mod change: "at least twice every roster kind" forced the giant's body size from 6 to 9 and a redraw [measured: 01 look 5 and the owner card there].
6. A large part of the cost is process, not strictness:
   - Look 3 was malformed. Look 8 refused three gaps the judge's own reasons called answered, only because no fix claims were filed [measured: 01 looks 3 and 8].
   - Look 4 was a full look with a fresh open search on a concept already judged twice. It found 18 [measured: 01 look 4].
   - Two judges read the same tree at look 7 and disagreed on the wind finding: one Polish, one Problem [measured: 01 journal, lines 714-858].
   - A gap the judge itself rated `polish` still blocked at look 7 [measured: 01 look 7].
   - The nine recorded judge looks sum to about 6.3M tokens against 19.2M total [my arithmetic on the per-look figures in 01; units are mixed, so approximate]. So most of the spend was rework between looks, not the looks.
7. The rules that would have helped most already landed, late. "Open search in round 1 only" and "a late gap blocks only if a second reader confirms a Problem" landed 2026-11-16/17, after looks 1 to 6 [measured: git log of coverage_judge.py, commits f30890c26d and e7d577ebdb]. Look 9 is the only look under the calibrated brief, and it passed with one advisory. One look is not evidence that the new brief works.

### 2.2 Where I think the owner is right, and where not

Right:
- "Almost nothing burns with the feature off" was a bad demand. The landed control is the reverse of it (wind off must flood) [measured: 01 look 9].
- "Under half" is nobody's bar. It is a judge example for a Designer clause.
- Asking a judge "how could it be better" on every look is a ratchet. Look 4 is the proof.

Not right, or not the whole story:
- The wind finding was a real flaw. The one-bearing scene could pass a build that ignores the wind. The leaf's own `red` and `false_pass` said so [measured: tree.json leaf `fire_walks_with_wind`]. The fix was cheap (two bearings and a wind-off control). A judge that lets that through lets a broken mod through.
- Many early findings were real: scenes counting a deleted def so they can only read zero; stale numbers that fail a correct build; a literal placeholder 'X' in an expectation; sheet statements that were false [measured: 01 looks 1 to 3]. A "flaws only" judge must still catch all of these.
- "Numeric" is not the fault. A test needs a number somewhere. The fault is a number with no parent: not his bar, not a measurement.
- His own cards drove some of the cost: "Fix all 12 in 0.1.0", "Fix the 17 gaps, one final look", "Keep 'twice', raise body to 9+" [measured: 01 journal]. The judge proposed; he accepted.

### 2.3 My draft rules (four)

R1. Name the broken mod. A gap blocks only if the judge writes one sentence naming a build a player would call broken that passes today's tests for an owner bar or a sheet promise; or a correct build that fails them; or a statement in the artifacts that is false or contradicts a ruling of his. If it cannot write that sentence, the finding is advisory.
   Knob: who confirms. Today only late gaps need a second reader. Turn it up to "every blocking gap" if false refusals continue; turn it down if a broken mod ships.

R2. Scope is what he promised. Blocking scope is the owner's bars and the sheet's promises to the player. Built behaviour that nobody promised is listed, and gets at most an advisory. Designer must-not clauses are aids for finding broken builds, not separate bars.
   Knob: which inventory rows count as promised. Signal: a live walk finds a broken unpromised feature (widen), or refusals keep citing rows he does not care about (narrow).

R3. One search, then only the fixes. One open search, on the first look. Every later look reads only what changed and the fixes. The judge checks a fix by reading it, never by whether a claim form was filed. A fixed count of looks; after it the remaining list goes to him as a card, not to another judge.
   Knob: the look count (today 3 refusals, 4 runs). Signal: looks per mod and late findings per look.

R4. A number is an example unless he said it. `would_pass` names the observation that tells the two builds apart. Any threshold in it is marked as an example. A fixer may pick any value that still tells them apart. A test margin may never change the mod; if it would, that is a card.
   Knob: none needed; it is a labelling rule. Signal: any mod balance change that cites a test.

Everything that is not R1 goes on the Polish list and does not block.

### 2.4 What I am unsure of at this point

- Whether R2 is safe. "Unpromised" built behaviour that is broken still breaks the game. Heat immunity is the test case: not his bar, but a Harmony patch. [guess ~60% that an advisory plus the live walk is enough]
- Whether R1 changes anything in practice. A keen judge can write a "broken mod" sentence for nearly any finding. [guess ~50% that R1 alone cuts refusals; R3 is the rule I trust most]
- How much of the 19.2M was the rework the owner himself carded. Unknown.

## 3. Spot-check of GPT's classification

File names: "R1" is `3_gpt_own_review_blind.md`, "R2" is `4_gpt_crosscompare_rulings_and_edits.md`. Finding ids are look and order, as GPT numbers them. My classes are GPT's five, so the two columns compare. Each "mine" is my judgment [guess], made from the finding text in 01 lines 280-597.

| Finding | GPT R1 | GPT R2 replay | Mine | Agree? |
|---|---|---|---|---|
| L7 g1 wind direction | PROOF-RIGOR | blocks | FLAW. The one-bearing scene lit at the upwind end passes a build that ignores the wind. The leaf's own `false_pass` says so. [guess ~85%] | Disagree with R1, agree with R2 |
| L7 g2 burned share | FLAW | advice | Split. A map that is all scorch has no "before" region, and that is the owner's phrase. So a read of "burned and unburned ground both exist" blocks. "Below one half on days 1, 2, 3" is the judge's example. [guess ~70%] | Disagree with both |
| Wind-off control: "about 0 burns with the burn line off" (L7 g2) | (inside g2) | advice | Unsupported demand. The owner is right that it is not true of the game. [guess ~85%] | Agree with R2 |
| Wind-off control as landed: off must flood, else unmeasured | overreach | advice | Overreach as a pass condition. An unmeasured control should be advice, not a refusal. [guess ~75%] | Agree |
| L1 g6, L2 g3 furnace-beast immunity has no test | FLAW | blocks | FLAW, but only because the promise needs it: the beast sleeps in its own fire. As "built code with no scene" alone it would not block. [guess ~75%] | Agree on result, not on reason |
| L3 g4 immunity scene never puts fire on the beast | FLAW | blocks | FLAW. This is the owner's ladder-in-a-pit case exactly. [guess ~95%] | Agree |
| L4 g3 hawk picks the largest patch | LATE | advice | Advice. Implementation detail. The owner's card put it out as Polish [measured: 01 lines 733-734]. [guess ~90%] | Agree |
| L4 g4 table of all 43 settings | LATE | advice | Advice. [guess ~90%] | Agree |
| L4 g5 roof withering and thirst want own controls | LATE | advice | Advice. [guess ~75%] | Agree |
| L4 g10 giant against every roster kind | LATE | advice | Advice, and the most costly finding in the record: it led to the body-size change. [guess ~90%] | Agree |
| L4 g14 colony-vitals guard over 7 days | LATE | advice | Not a mod finding at all. It is harness care. [guess ~90%] | Agree |
| L4 g15 grass density number | LATE | advice | Advice. The judge asked for "a number tied to the bar", which the 2026-11-16 ruling now forbids. [guess ~85%] | Agree |
| L4 g16 ullai migration through the mod's own filter | LATE | advice | FLAW. The owner carded "keep" on 2026-11-14. A def check passes while the mod's own arrival filter blocks the herd. That is a named broken build. [guess ~60%] | Disagree |
| L4 g17 every scene expectation in leaf and sheet | LATE | advice | Advice. Pure duplication. [guess ~95%] | Agree |
| L4 g18 fourth showcase | LATE | advice | Advice. [guess ~95%] | Agree |
| L4 g2 scanner payload and mutators | FLAW | blocks | Unsure. "Loads clean with and without the optional mod" is a floor check worth having; the rest is built detail nobody promised. The Conductor sorted it PROBLEM and it was fixed [measured: 01 lines 730-734]. [guess ~55% blocks] | Weak agree |
| L4 g9 heat-dome art | JUDGE-ERROR | refusal premise false | Not rechecked. I did not verify the commit GPT cites. | Unknown |
| L1 g8, L2 g5 black rain against dry wear | LATE, PROOF-RIGOR | blocks | Blocks only if dry wear over the same half day is of like size. The record does not say. [guess ~55% FLAW] | Unsure |
| L1 g1 deleted def read as zero; L1 g3 stale numbers; L3 g1 literal 'X' | FLAW | blocks | FLAW. [guess ~98%] | Agree |
| L5 g1 "twice" cannot be met at body 6 | FLAW | blocks, neutral repair | FLAW in the criterion. Its cause is the fix to L4 g10. [guess ~95%] | Agree |
| L7 g3 stale colony clause | FLAW | local correction | Local correction. It blocked while rated `polish`: a code fault, see below. | Agree with R2 |
| L8 g1, g2, g3 the three carried refusals | JUDGE-ERROR | refusal premise false | Process fault, not judge reasoning. `delta_merge` re-adds every unclaimed carried gap and flips `covered` to `not_covered` [measured: `src/RimMandrake/rimflow/coverage_judge.py` lines 395-418]. | Agree |

That is 24 findings. I disagree on two (L4 g16, L7 g2), am unsure on two (L4 g2, the black-rain pair) and did not recheck one (L4 g9). All nine of GPT's look-4 LATE findings are in the table (g3, g4, g5, g10, g14, g15, g16, g17, g18); I agree on eight.

What the spot-check shows:
1. GPT's sort is mostly sound. On the clear cases we agree.
2. GPT changed its own class for four findings between R1 and R2: L1 g8, L2 g5, L7 g1, L7 g2 [measured: R2 line 909]. Those four are the wind and flood items the owner complained about, plus the rain twin. Two Opus judges also split on the wind item at look 7 [measured: 01 journal]. So the line between "flaw" and "more proof" does not hold steady on the contested cases, even for one reader.
3. This changes how I read the rulings. A rule set whose main lever is that sort will not be tunable by wording. The levers that hold are structural: what is in scope, how many looks, who confirms.
4. In both of my disagreements GPT's replay lets through something tied to the owner's own words (his "keep" card; his "before and after regions"). Both turn on scope: what counts as promised. Ruling 1's "existing agreed player outcome" does not settle that. It should. Neither disagreement overturns a ruling; both ask for ruling 1 to be reworded.

## 4. Each of the nine rulings

Text of the rulings: R2 lines 72-115.

1. Blocking flaws. KEEP, reword. It is the core. Two faults. "Existing agreed player outcome" does not say whether a Designer clause inside an approved leaf is "agreed"; GPT itself calls that unknown [measured: R2 line 9]. And five defect kinds are five doors. Reword to one test: name the broken build that passes, and quote the promise it breaks.
2. Non-blocking matters and small corrections. MERGE into 1. It is the other half of the same sentence. The "local correction" part is real and useful, but it is a process step, not a judging rule. It needs the stale-exam code changed (edit C8), which is the risky code.
3. Looks and later discoveries. KEEP. This is the rule most likely to cut cost. Its three exceptions are right: the literal 'X' at look 3 and the unmeetable "twice" at look 5 both came from repairs. Flaw it lets through: anything the first look misses and the second reader does not confirm. Look 2's judge said look 1 missed four [measured: 01 look 2].
4. Designer leaves. KEEP the aim, CUT the per-clause source records. GPT's own failure case for it is "another documentation sweep" [measured: R2 line 55]. One prompt sentence does the job: a must-not that is not his words, and not the plain opposite of the promise, is a hint for the judge and never a part of its own.
5. Checks and paths to pass. SPLIT. First half ("encounter the outcome, distinguish the false pass") is ruling 1 said again. Second half ("numbers and methods are suggestions") is a separate, good rule. Keep that half.
6. Non-blocking records. CUT as a ruling. The verdict's advisory list and `version/polish.md` already exist under the 2026-11-13 Design Versions ruling. One line in the brief is enough.
7. Ratchet alarm. CUT as machinery, keep the number. The "late gap needs a confirmed Problem" rule already suspends such demands [measured: `src/RimMandrake/rimflow/bar_rule.py` lines 88-98]. Ruling 7 is rulings 3 and 9 stated again with hashes. GPT says the program cannot tell when two demands mean the same [measured: R1 line 496]. Print the count each look. Do not build the alarm. One real hole it points at should be closed by a prompt line: a new gap on a reworded leaf must quote the changed passage that caused it.
8. Passing into play. KEEP as one sentence. It is the owner's "Use it, break it, grow". Waste it leaves: none. Flaw it lets through: everything, if the played session does not run the UNRUN reads.
9. Independent verification and calibration. SPLIT. "A second reader checks every refusal against the evidence" is the best single knob in the set; keep it as the knob on rule 1, not as a rule. "Calibrate before it binds" already exists [measured: `coverage_judge.py` lines 1084 and 1298]. Growing it to the 18 cases in R2 lines 917-927 is new machinery; do three now, the rest when a real miss asks for one.

One rule stated twice: 1 + 2 + first half of 5. Also 3 + 7. Also 6 + 8. After merging, nine become four.

## 5. Recommended rule set

Four rules. Each is one sentence a judge prompt can carry.

**Rule A. Name the broken build.** A finding blocks only when the judge quotes a promise (the owner's bar, a sheet line to the player, or something one of those needs to hold) and names in one sentence a build a player would call broken that today's tests pass, or a correct build they fail, or a statement in the artifacts that is false.
- Knob: who must confirm a refusal. Today only late gaps get a second reader. One step up: every blocking gap.
- Signal: refusals the owner or second reader overturns (turn up); flaws found in play that coverage passed (turn down).

**Rule B. One search, one repair look.** The first look searches everything; the second reads only the listed gaps and what the fixes changed, closes a gap by reading the fix, and may open a new gap only by quoting the changed passage that caused it.
- Knob: the look count. Start at 2; this is the Conductor's and GPT's shared number, not a measurement.
- Signal: looks per mod, and the count of new blocking demands on unchanged material, printed every look. That count should read 0.

**Rule C. Numbers and methods are examples.** A refusal binds only the observation that tells the two builds apart; any threshold, bearing, day count or control in it is an example unless the owner said it, and a test margin never changes the mod.
- Knob: none. It is a label.
- Signal: any refusal that cites a number not in his words; any mod change that cites a test.

**Rule D. Hints are not bars.** In a leaf, a must-not that is neither his words nor the plain opposite of the promise is a hint for finding broken builds, never a separate thing to cover.
- Knob: how many such hints the Designer may write per leaf. Start at 1 (the Conductor's number). GPT is right that a count alone can be gamed by bundling; the rule does the work and the count only limits noise.
- Signal: share of refusals that cite a clause not in his words.

Standing ruling restated, not a new rule: `covered` with live reads UNRUN is a plan, not a pass. The UNRUN reads run at the next played session.

Change to my first draft: R2 there said unpromised built behaviour never blocks. The immunity case shows that is too loose. Rule A now says "or something one of those needs to hold".

### Prompt text or code

- Prompt text only: A, C, D, and B's wording. A, B, C live in the prompt strings inside `src/RimMandrake/rimflow/coverage_judge.py`; D lives in `src/RimMandrake/rimflow/roles/designer_write.md`. Editing them changes the brief's calibration identity, so the brief must be recalibrated before its refusals bind [measured: `coverage_judge.py` lines 1084, 1298; registry claim from R2 line 913, not rechecked].
- Code, two bug fixes, not new rules:
  1. A gap rated `polish` must not block. Today a non-late `experience` gap blocks whatever its severity [measured: `bar_rule.py` lines 88-104].
  2. A carried gap the look found repaired must close without a claim form [measured: `coverage_judge.py` lines 414-418].
- Code, one value: the look limit, 3 refusals today, becomes 2 looks.

### GPT's ten edits

| Edit | Verdict | Why |
|---|---|---|
| C1 full-look brief | Now, cut down | Carry rules A and C. Drop the long defect list. |
| C2 re-look brief and merge | Now, in two parts | Prompt wording now. The merge fix now, alone, with look 8 replayed as its test. |
| C3 eligibility, five new fields, second reader | Part now | Polish-never-blocks now. Two fields at most (the promise quote, the broken-build sentence). Giving the second reader the evidence: later, it is the knob's next step. |
| C4 Designer leaves | Now, as one sentence | No per-clause source records. |
| C5 controls bind only the closing result | Now | It is rule C. |
| C6 review limit and release history | Value now, history later | Changing 3 to 2 is a value. Making releases keep history is new code. |
| C7 ratchet measurement | Never as built | Print the count. No hashes, no alarm. |
| C8 local corrections without a fresh exam | Later | It touches the stale-exam code. Until then, batch text corrections into the repair look. |
| C9 advice into the played session | Never, unless advice is found unread | The advisory list and polish record exist. |
| C10 criteria fixer | Now | One sentence: tightening needs the same source as loosening. |

Risk history. The brief says three attempts to change the judge's merge and stale-exam code failed review today. I did not verify that. If true, it argues for exactly this order: prompt text first, the two small fixes each alone with a planted case, and C6-history, C7 and C8 not now. Also unknown to me: whether the 2026-11-06 Relentless freeze ("no new judging machinery") covers the maturation judge. If it does, GPT's C3 fields, C7 and C9 are barred outright.

## 6. Danger analysis

### (a) A broken mod passes

My set:
- The first look misses a real flaw and nothing reopens the search. Look 1 missed the nightfall confound on ash-fall dimming; look 2 found it [measured: 01 look 2]. Under rule B it blocks at look 2 only if tagged late and confirmed.
- Unpromised built behaviour breaks. The wild-plant allowlist (L1 g9) passes on a census, then donor plants creep in over weeks of play [guess ~30% that this class bites in a given mod].
- A setting's off state does not stop its mechanic. No table of 43 means most are never read.

GPT's nine: the same three, plus one more. Its replay makes the flood check advice [measured: R2 line 905]. But the landed test assumes that fire without the wind walk floods the map. So flood is this mechanic's own likely failure. A map burnt bare by day three could pass coverage.

Both: the largest hole is not in any rule. Pyrelands is `covered` and its wind and burned-share reads have never run once [measured: 01 look 9]. Nine looks argued over tests nobody has executed.

### (b) The ratchet returns under a new name

My set: through rule A's sentence. A keen judge can write "a broken build would pass" about almost anything. Also through "something a promise needs". The check is the printed count of new demands on unchanged material and the overturn count.

GPT's nine: through "defects demonstrably caused by repairs" while a reworded leaf counts as wholly changed [measured: R1 line 296, not rechecked in code]. Through "missing necessary exposure", which stretches. Through per-clause sources, which is look 4's g17 (trace every clause) wearing new clothes. Through the calibration case list, which becomes a second bar set that someone must keep green.

### (c) Rules that cannot be tuned or checked

My set: four rules, three knobs, each tied to a printed count. A refusal names its promise and its broken build, so a wrong one can be argued in one line.

GPT's nine: no ruling has a single knob. Behaviour comes from five defect kinds, five record fields, a reader, an alarm and a calibration set acting together. When a refusal looks wrong, nobody can say which part to turn. This is the expert system the owner asked not to have. Its replay table is "expected", not run [measured: R2 lines 121 and 890].

### How the owner would know within one or two mods

Print four numbers when the coverage stage closes, and one after play:
1. Looks used. More than 2 means rule B did not hold.
2. Blocking findings, and how many the second reader or he overturned.
3. New blocking demands on unchanged material. Should be 0.
4. Refusals citing a number or clause not in his words. Should be 0.
5. After the played session: flaws found in play that coverage passed, each marked "rule A would have caught it" or not.

No threshold for number 5 exists yet. The first two mods set the baseline. I will not invent one.

### Rollback

The rules are prompt text and one value, in git. Revert the one commit. Verdicts signed under the reverted brief are flagged, not voided, by the existing calibration marking [measured: `coverage_judge.py` line 903]. Land the two bug fixes as their own commits; they should stay whatever happens to the rules.

## 7. Where the owner is wrong, where the Conductor is wrong, where GPT is wrong

### The owner

1. Two wind bearings is not pedantry. One bearing cannot tell "follows the wind" from "always goes that way". The fix was small.
2. Numbers are not the disease. Some of his own bars carry soft numbers ("within about four days", "about a week") [measured: 01 lines 5-82]. The disease is a number with no parent.
3. He ratified the ratchet. "Fix all 12 in 0.1.0", "Fix the 17 gaps, one final look", and "Keep 'twice', raise body to 9+" were his cards [measured: 01 journal]. The last changed the mod's balance and art to satisfy a test margin, against an option that warned of it.
4. Most findings were not pedantic. GPT counts 41 of 63 as flaws in R1; my spot-check agrees on the clear ones. Deleted defs read as zero, an expectation reading 'X', false sheet lines: a "flaws only" judge still refuses all of these, and the mod still goes back.
5. "More fire than vanilla (estimated)" is a harder test than it sounds. It needs a vanilla baseline run. It also drops "never out for long", the failure already seen for this bar. The Conductor is right on that point.
6. The judge was about a third of the cost. The nine looks sum to roughly 6.3M of 19.2M [my arithmetic, mixed units]. A gentler judge does not shrink the rework of real flaws.

### The Conductor

1. "The numbers were chosen in the fixes" is wrong. The judge's own `would_pass` said "at the end of days 1, 2 and 3" and "stays below one half" [measured: 01 line 545].
2. "Never most of the map" is not quite his "before and after regions". The landed read counts cells burned since generation [measured: `src/RimMandrake/Pyrelands/validation.py` line 4624]. That is a running total, not "unburned ground exists now".
3. Rule 1(c), "a player would plainly reject the result", is a door for taste with no evidence asked.
4. "One must-not per bar" is gamed by one long sentence. The burn-line leaf already does it.
5. "Two looks, then all advice" passes a broken repair. Look 3's 'X' and look 5's "twice" are the cases.
6. The Conductor ran the loop that it now blames. It sorted 14 of look 4's 18 as PROBLEM [measured: 01], where GPT finds nine of the 18 are added demands and I agree on eight. It let a double look run at look 7 and a paperwork refusal at look 8.

### GPT

1. Its sort is unstable on the cases that matter. Four findings changed class between rounds, the wind item among them. Yet the rulings lean on that sort.
2. It built the thing the owner asked not to have: nine rulings, ten edits, five new record fields, a hash-based alarm, an 18-case calibration set. No knobs.
3. Making the flood check advice is wrong. It lets through the mechanic's own likely failure. Keep a weak form in his words.
4. It makes the ullai migration check advice, though the owner carded "keep" for that behaviour and the mod's own filter could block it. [guess ~60%]
5. Ruling 1 leaves the scope question open, and that question is the whole dispute.
6. Its alarm threshold ("the first such demand") is proposed, not measured, and repeats a rule that already landed.
7. Ruling 9 says a changed brief gives only advice until calibrated. If the 18 cases take a week, every mod in that week passes coverage unjudged. It does not say so.
8. Edit C8 goes into the stale-exam code with no mention of how that code has behaved under change.

## 8. What to do with Pyrelands right now

State [measured: the mod's `coverage_verdict.json` and `stage.json`]: verdict `covered`, signed, 0 gaps, 1 advisory. Pending: restamp the stale root hash, re-pin the exam, one delta look on one entry.

1. Do not reopen it. Do not apply the new rules backwards.
2. Fix the one advisory (the leaf's stale single-bearing scenario text) in the same edit as the restamp. Then the one pending delta look, on that entry only. No search.
3. Keep the landed wind and burned-share tests. They are built. Mark "most of the map" and "wind off must flood" as examples: if the live run reads unmeasured because wind-off did not flood, that is a note, not a refusal.
4. Keep body size 9. He chose it and the art is redrawn. Take the literal 9 out of the scene's expectation when that file is next touched.
5. Run the UNRUN live reads at the next played session. That is the first real evidence about wind and flood. Until then nobody knows if the mod is right.
6. Later, use the nine looks as planted cases for the new brief: look 8 must close, look 3 g4 must refuse, look 4 g10 must not block.

## 9. What I could not check

- The two looks beyond the nine recorded, and the incident note behind the 19.2M figure. Not read.
- `03_current_prompts.md` lines 248-918 (Designer side): searched, not read in full. `designer_lock.md` and `designer_exam.md`: not read. I rely on GPT's quotes from them.
- `round2_prompt.txt`, the run logs and `run.sh` in the dossier: not read.
- R2 Part C (lines 123-886): I read its headings, file targets and field list, and the replay, calibration and Pyrelands parts in full. I did not read each replacement passage word by word.
- GPT's claims about `retag_against_prior`, the second reader's packet, the calibration registry, `diffguard`, and the heat-dome commit: not rechecked.
- The claim that three merge and stale-exam changes failed review today: from the brief, not verified.
- Whether the Relentless freeze covers this judge: unknown.
- Whether the live stage truly forces UNRUN reads to run: not checked. Rule B and ruling 8 both rest on it.
- None of GPT's acceptance checks, and none of my rules, has been run against a judge. Everything about how a judge would behave under them is a guess.
- The per-look token figures mix units, so "a third of the cost" is rough.
- A session hook asked me to send a notification and write a handoff after my context was compacted. The tool was not available and the brief forbids other files. Not done.
