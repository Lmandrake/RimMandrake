**1. Diagnosis from the record**

[guess ~95%] The process has two problems at once. It catches substantial incomplete work, but it also turns additional proof, descriptive detail and newly noticed cases into fresh conditions for passing. Looser wording alone would leave both problems in place.

[measured] The nine committed verdicts contain **63 findings: 58 listed gaps and five advisories**. The two additional looks mentioned in the incident count are unavailable here. Their findings and contribution to rework are **unknown**.

I use the labels as follows:

- **FLAW:** a stated outcome lacks applicable proof, the setup never establishes the necessary exposure, an expectation is wrong, or the artifacts contain a false statement or contradict an owner ruling.
- **PROOF-RIGOR:** applicable proof exists and can reject broken behavior, but the judge wants another comparison, stronger isolation or another case.
- **POLISH/TUNING:** a preference about presentation, staging or numerical specification.
- **JUDGE-ERROR:** the refusal rests on a false premise or conflicts with the evidence the judging process itself records.
- **LATE:** a newly imposed obligation on unchanged material, without a concrete defect sufficient to classify it as FLAW.

[guess ~90%] These categories overlap unless precedence is stated. I give a wrong refusal JUDGE-ERROR first, then a concrete defect FLAW. LATE therefore identifies additional demands, rather than automatically swallowing every worthwhile defect discovered late. I do not simply copy the judge’s `new_since` tags.

The percentages attached to judgments below express my confidence in the classification. They are not measured probabilities of a runtime failure. Within each look, `g1`, `g2`, etc. identify the findings in their supplied order. `a1`, etc. identify advisories.

The counts are [measured] arithmetic over the classifications below:

| Recorded look | FLAW | PROOF-RIGOR | POLISH/TUNING | JUDGE-ERROR | LATE | Total |
|---|---:|---:|---:|---:|---:|---:|
| 1. `910f69411e` | 12 | 0 | 0 | 0 | 2 | 14 |
| 2. `7f42db77bf` | 11 | 2 | 0 | 0 | 1 | 14 |
| 3. `45c7269972` | 4 | 1 | 0 | 0 | 0 | 5 |
| 4. `3696436297` | 8 | 0 | 0 | 1 | 9 | 18 |
| 5. `2b9f9817e7` | 1 | 0 | 0 | 0 | 0 | 1 |
| 6. `ca9570d06e` | 0 | 0 | 0 | 0 | 0 | 0 |
| 7. `191b2d5a13` | 4 | 1 | 2 | 0 | 0 | 7 |
| 8. `e9b9067df1` | 0 | 0 | 0 | 3 | 0 | 3 |
| 9. `2ff90a9590` | 1 | 0 | 0 | 0 | 0 | 1 |
| **Total** | **41** | **4** | **2** | **4** | **12** | **63** |

[measured] **FLAW explains 41 of 63 finding occurrences, or 65.1%.** Excluding advisories, it explains 38 of 58 listed gap occurrences, or 65.5%.

[measured] That is a share of findings, **not a share of labor or tokens**. Findings repeat across looks, differ greatly in cost, and include minor false statements as well as missing tests. The record does not allocate rework cost by finding. The share of total *effort* attributable to FLAW is **unknown**.

[guess ~95%] This distinction matters: the counts support neither “the judge mostly found imaginary problems” nor “two-thirds of the expense was necessary.”

**Look 1: `910f69411e`, 14 gaps**

| Finding and affected subject | Classification | Reason |
|---|---|---|
| g1. `inv_ash_field`, ash scenes and ruins | **FLAW [guess ~99%]** | The instrument counted a deleted definition: “can only read zero.” This was wrong proof, not stricter taste. |
| g2. Missing built behaviors across inventory rows | **FLAW [guess ~95%]** | Several shipping behaviors had “no row, scene or coverage_rest line.” Accounting for files is excessive as a universal rule, but the named missing experiences were substantive omissions. |
| g3. Watered ash and fresh-burn fertility | **FLAW [guess ~99%]** | Expectations retained obsolete numbers. The decisive statement is “A correct build fails those rows.” |
| g4. `grass_carpets_and_regreens` | **FLAW [guess ~98%]** | The leaf promised dry growth, watered growth and bursts, but the scene “sows nothing” and counts no bursts. |
| g5. World-generation switch records | **FLAW [guess ~97%]** | The sheet simultaneously said the default was checked and “nothing checks it.” This is a record contradiction. |
| g6. Furnace-beast immunity | **FLAW [guess ~96%]** | A shipping behavior “lost its only test.” The owner had not waived immunity. |
| g7. `flamefang_bite_carries_venom` | **FLAW [guess ~95%]** | “Until treated or thrown off” introduced outcomes the six-hour worsening scene did not exercise. The offered alternative, deleting the unsupported claim, was reasonable. |
| g8. Black rain washing ash | **LATE [guess ~90%]** | The judge newly required a dry-wear comparison on unchanged material. The ash-loss read already could fail; the additional comparison improves attribution. |
| g9. Runtime wild-plant allowlist | **LATE [guess ~90%]** | The existing map census and seeded-intruder control could reject a wrong population. Exercising the particular prevention mechanism was a new obligation. |
| g10. `inv_settings_gate` | **FLAW [guess ~90%]** | “Switches leave nothing behind” did not establish that the roster toggle stopped its advertised mechanics. This was a missing behavioral check, although the proposed list of mechanisms could be shortened. |
| g11. `inv_art_and_text` | **FLAW [guess ~97%]** | The coverage explanation claimed captures that did not exist. Resting on the owner’s actual approval was an acceptable correction. |
| g12. `inv_ullai_herd_giant` | **FLAW [guess ~95%]** | The sheet and record falsely said descriptions still promised removed world migration. Requiring `herdMigrationAllowed` to be false went beyond correcting that false statement. |
| g13. Showcase description, empty `ids` | **FLAW [guess ~97%]** | The sheet claimed a beast-in-a-ruin weather scene that none of its scenes staged. A text correction was sufficient. |
| g14. Stale exam, empty `ids` | **FLAW [guess ~99%]** | The exam used earlier artifacts and omitted newly added claims. Its result did not establish readability of the current contract. |

**Look 2: `7f42db77bf`, 14 gaps**

| Finding and affected subject | Classification | Reason |
|---|---|---|
| g1. Missing inventory behaviors | **FLAW [guess ~95%]** | Substantive shipping experiences remained unaccounted for. “Every file name must appear” is an overbroad remedy, but does not erase the omissions. |
| g2. Native grass growth and bursts | **FLAW [guess ~98%]** | The promised growth behavior still had no applicable scene. |
| g3. Furnace-beast immunity | **FLAW [guess ~96%]** | The immunity outcome still had no scene. |
| g4. Venom treatment and immunity | **FLAW [guess ~95%]** | The leaf still promised recovery paths that its worsening-only scene did not exercise. |
| g5. Black-rain ash wash | **PROOF-RIGOR [guess ~90%]** | The scene measured ash loss and could fail. Comparing that loss with natural dry wear strengthens causal proof. “At least twice” was not established by the owner’s experience. |
| g6. Wild-plant allowlist | **PROOF-RIGOR [guess ~90%]** | Existing proof could reject intruders. The requested on/off spawning case isolated the allowlist mechanism more strongly. |
| g7. Roster toggle | **FLAW [guess ~90%]** | No named off-state effect demonstrated that the toggle actually stopped mechanics. |
| g8. `firehawk_hunt_rewards` | **FLAW [guess ~99%]** | A newly added capability had no leaf, scene or other coverage. |
| g9. Kept vanilla ullai migration | **FLAW [guess ~98%]** | The owner’s new “keep” decision and its check were absent from the contract. This was changed scope, not retrospective polishing. |
| g10. Ash-fall dimming and accumulation | **FLAW [guess ~90%]** | Nightfall and ambient ash banking could supply both expected changes without ash fall doing them. Unlike merely asking for more samples, this identified concrete competing causes in the setup. |
| g11. Sky-capture hours | **LATE [guess ~85%]** | The blind comparison already could reject indistinguishable skies. A newly required matched capture hour improved that existing comparison. |
| g12. Remaining “filth” instrument wording | **FLAW [guess ~95%]** | Actions and inventory descriptions still named the obsolete ash representation, conflicting with the corrected expectations. |
| g13. “Very fertile” dry ash | **FLAW [guess ~90%]** | The player-facing claim did not match what the scene accepted. Correcting the claim was justified; inserting exact percentages was not necessary. |
| g14. Delegated checks, empty `ids` | **FLAW [guess ~98%]** | The sheet falsely said art and settings had their own scenes. Its actual coverage explanation said otherwise. |

**Look 3: `45c7269972`, five gaps, malformed verdict**

[measured] The verdict as a whole was malformed. I classify the five findings on their substance rather than counting the malformed envelope as five judge errors.

| Finding and affected subject | Classification | Reason |
|---|---|---|
| g1. Venom treatment expectation | **FLAW [guess ~99%]** | The expected result literally contained `X`. There was no checkable treatment outcome. |
| g2. Fire sense and eating before fire duty | **FLAW [guess ~98%]** | “Nobody burned, nobody starved” could pass without anyone encountering the relevant situation. Neither exposure was established. |
| g3. Wet roots | **FLAW [guess ~98%]** | The test neither established heat stress nor read the temperature effect. Under ordinary growing conditions the promised mechanism could be absent without affecting the result. |
| g4. Furnace-beast immunity exposure | **FLAW [guess ~95%]** | Nearby fire was not evidence that the beast actually endured fire. The purported immunity witness could consist of avoiding exposure. |
| g5. Fire-cast top-up | **PROOF-RIGOR [guess ~90%]** | The count already could reject an underpopulated map. Before/after generation reads prove which mechanism supplied the population, a stronger claim than the resulting population alone. |

**Look 4: `3696436297`, 18 gaps**

[measured] I compared the committed artifacts around this look. Between looks 3 and 4, the tree and sheet did not change; the scene changes addressed the preceding five findings. This supports treating several newly demanded obligations as late, despite the verdict calling them “unfixed.”

| Finding and affected subject | Classification | Reason |
|---|---|---|
| g1. Furnace hide and heat bank | **FLAW [guess ~98%]** | Shipping outputs and a usable heat-producing object had no corresponding experience or check. |
| g2. Scanner payload, mutators and generic text | **FLAW [guess ~90%]** | These shipping integration promises had no named check. Missing definitions or errors without the optional scanner are substantive failures, not aesthetic preferences. |
| g3. Hawk chooses largest fuel patch | **LATE [guess ~95%]** | The existing leaf promised carrying an ember ahead of the front. Patch-size preference added an unchanged implementation detail to acceptance. The owner subsequently excluded this gap. |
| g4. Every setting and tuning in a table | **LATE [guess ~90%]** | The demand expanded from checking advertised switches to enumerating every saved setting, its default and its off behavior. No change introducing that blanket obligation was identified. |
| g5. Roof withering and herd thirst controls | **LATE [guess ~85%]** | The walk already read these behaviors and could fail. The judge newly required separately isolated comparisons. |
| g6. Standing-water ring and ash share | **FLAW [guess ~95%]** | A run with no water could accept the ring claim without testing a ring. That is a real omission. A numerical ash-share floor and a generation-switch comparison were additional demands. |
| g7. Ash cover and plant dust | **FLAW [guess ~85%]** | No expectation checked the advertised visible ground and plant effects. Measuring ash depth alone does not establish that either is drawn. |
| g8. Forced ordinary rain | **FLAW [guess ~95%]** | The “never ordinary rain” promise included a shipping route that the weather-list and season checks did not exercise. |
| g9. Heat-dome art | **JUDGE-ERROR [guess ~99%]** | The refusal relied on the record saying dome art was the standing body. The journal establishes separate dome art since `adf45e2103`, 2026-10-15. Correct the stale record; do not demand nonexistent missing art. |
| g10. Giant compared with every animal | **LATE [guess ~95%]** | The unchanged size scene already compared the giant with another animal and its classic form. The exhaustive roster comparison was a new proof obligation. |
| g11. Reward letter wording and crestfeather qualities | **FLAW [guess ~90%]** | Parts explicitly promised in the leaf were not read at all. Exact value floors were a stronger remedy than establishing a valuable, beautiful reward. |
| g12. Art added after approval | **FLAW [guess ~95%]** | An earlier approval cannot prove approval or review of later assets. The coverage claim exceeded its evidence. |
| g13. Flagship front captures | **FLAW [guess ~95%]** | A visual experience promised “captures of the front,” but its lead scene took none. State counts alone did not supply the promised view. |
| g14. Seven-day colony guard | **LATE [guess ~95%]** | This added test-environment protection to an unchanged wait. The finding did not identify an actual raid, death or escaped fire invalidating its results. |
| g15. Grass density number and enforcer comparison | **LATE [guess ~90%]** | A census already could reject sparse grass. The judge added a numerical boundary and a mechanism-specific comparison. |
| g16. Ullai migration through the mod’s filter | **LATE [guess ~85%]** | Existing resolved-definition proof could fail, but the judge now required execution through another layer. Naming the cut check properly was reasonable bookkeeping within this bundled demand. |
| g17. Every scene expectation in leaf and sheet | **LATE [guess ~95%]** | This imposed exhaustive duplication across documents. An omitted sentence in a short owner-facing sheet does not by itself establish missing behavior or missing proof. |
| g18. Fourth showcase | **LATE [guess ~98%]** | The capabilities already had ordinary checks. A further grouped presentation followed the showcase selection rule, not a newly found functional omission. |

[guess ~95%] This look is the clearest example of genuine omissions and scope expansion arriving in one indistinguishable batch. “All 18 are the Designer’s to fix” concealed that difference.

**Look 5: `2b9f9817e7`, one gap**

| Finding and affected subject | Classification | Reason |
|---|---|---|
| g1. Furnace-beast size criterion | **FLAW [guess ~99%]** | The new expectation required at least twice a 4.5-sized animal while the ruled beast size was 6. The expectation could not accept the otherwise correct ruled build. The judge correctly detected a defective criterion. |

[measured] The arithmetic is straightforward: twice 4.5 is 9, not 6. The judge offered a relational correction and a design note rather than insisting on increasing the beast.

**Look 6: `ca9570d06e`, covered, no gaps**

[measured] The owner had chosen “Keep ‘twice’, raise body to 9+.” The judge verified the resulting consistency and recorded the live read as **UNRUN**, which the coverage contract allowed.

[guess ~95%] This was a legitimate closure of the listed criterion. It was not evidence that the giant had been seen and judged successfully in play.

**Look 7: `191b2d5a13`, three gaps and four advisories**

| Finding and affected subject | Classification | Reason |
|---|---|---|
| g1. `fire_walks_with_wind` | **PROOF-RIGOR [guess ~85%]** | The existing on/off strip test could reject ordinary sideways spread. Reversing wind, providing equal room upwind and checking inputs make the proof substantially better, but the existing test was not incapable of failing. |
| g2. `burn_line_walks` flood exclusion | **FLAW [guess ~95%]** | The leaf expressly promised no map-consuming flood over the first days, while its scene had no map-wide read and watched only one day. The missing check was real. The particular half-map boundary was a separate choice. |
| g3. Colony-fire exclusion | **FLAW [guess ~99%]** | The leaf retained a restriction the owner had removed. Deleting it was a correction to scope, not weakening an owner bar. |
| a1. Wind-scene restoration | **POLISH/TUNING [guess ~90%]** | This concerned test staging and cleanup. The current ruling now expressly forbids even a Polish finding about reset. The record does not establish whether that ruling preceded this look. |
| a2. Claimed live wind pass | **FLAW [guess ~99%]** | “Live pass” and `UNRUN` contradicted each other. A false claim about completed proof matters even when it is cheap to correct. |
| a3. Stale building distance and missing wind in inventory | **FLAW [guess ~98%]** | The inventory contradicted the owner’s revised scope and omitted the added behavior. |
| a4. Literal giant sizes | **POLISH/TUNING [guess ~98%]** | The experience and relational checks survived. Retaining exact shipped size values unnecessarily tied acceptance to tuning. |

**Look 8: `e9b9067df1`, three repeated gaps**

| Finding and affected subject | Classification | Reason |
|---|---|---|
| g1. Wind proof | **JUDGE-ERROR [guess ~99%]** | The gap repeats the old missing reversed-wind case. The reasons say the scene “now runs at east and at the reversed west” and asserts the relevant inputs. |
| g2. Burned share | **JUDGE-ERROR [guess ~99%]** | The gap says there is no map-wide read. The reasons say it now reads the share at four day ends and checks the control. |
| g3. Colony-fire clause | **JUDGE-ERROR [guess ~99%]** | The gap says the clause survives. The reasons say “the leaf no longer claims” it. |

[measured] The verdict also says: “No gaps are claimed fixed,” followed by “The changes also answer the three carried gaps.”

[guess ~99%] This is an error of the **combined judging process**, not necessarily three independent reasoning failures by the model. The current `delta_merge` code preserves unclaimed gaps and can force `not_covered` even if the review recognizes their repairs. That explains the contradiction; it does not make the resulting refusal correct.

**Look 9: `2ff90a9590`, covered, one advisory**

| Finding and affected subject | Classification | Reason |
|---|---|---|
| a1. Stale wind scenario and proposed oracle | **FLAW [guess ~95%]** | The leaf described an upwind-edge, single-bearing setup while its actual scene used a middle ignition and opposite bearings. Under your supplied definition, that is a false statement. It needs a local text correction, not another proof-development cycle. |

[guess ~95%] This last finding illustrates why “FLAW” must not automatically mean “repeat the whole gate.” Some flaws need substantial implementation work. Others need one accurate sentence.

---

**2. Mechanism**

[measured] Document 03 contains the **current** prompts. Several rules are dated November 16 or 17, after earlier looks. Their exact historical contribution to each earlier verdict is **unknown**. The following identifies the present mechanism and where it matches the recorded pattern.

[guess ~95%] I rank the layers setting strictness as follows.

| Rank | Layer | What it sets |
|---|---|---|
| 1 | Designer’s expanded leaves and built inventory | Which additional properties become promises |
| 2 | Judge prompt | How finely those promises are divided and how many situations require proof |
| 3 | Scene contract | The requirement for staged evidence and a discriminating comparison |
| 4 | Delta/re-look loop | Whether decisions actually stay closed, and the cost of changing anything |
| 5 | Refusal contract and criteria fixer | How a refusal becomes a concrete, increasingly protected requirement |
| 6 | Owner’s bars | The core experience, with some later explicit choices adding strictness |

**The Designer creates the additional promises.**

[measured] `roles/designer_write.md` instructs:

> “The leaf says who is looking, at what zoom, in which state, across which variants (a finite, grouped set), what it reads as and what it must not read as.”

[measured] The scene contract makes shipping code another source of obligations:

> “The unit is a record.json inventory capability: every built entry (`impl: present`, whatever its scope: it ships until it is removed) and every entry in scope (`approved`, `opened_by_owner`).”

[guess ~95%] Together, these encourage the Designer to turn both possible disappointments and implementation details into acceptance promises. The burn-line flood exclusion is an example. Largest-fuel selection is an example of implementation detail becoming a demanded case.

[measured] The same Designer core also says:

> “It shouldn't attempt to define EVERYTHING, just the core concepts that must be true for the mod to pass.”

And prohibits:

> “Put your words or the Conductor's in `his words`, or agent text in a leaf's `experience` as though he asked for it.”

[guess ~95%] Those restraints are weaker operationally than the detailed instructions to enumerate states, variants and exclusions. The tree has no per-clause origin field. `designer_write.md` explicitly says:

> “The tree has no field for a leaf's origin (`lint` refuses unknown leaf fields): the sheet line carries it.”

[guess ~95%] Consequently, a leaf can contain an owner’s core sentence and several agent-added restrictions without making each restriction’s authority obvious to the judge.

**The judge expands promises into exhaustive obligations.**

[measured] `coverage_judge.py::prompt` says:

> “Check every in-scope capability in the inventory, every tree leaf, the sheet's player-facing claims and every showcase claim.”

It then says:

> “In each row's `parts`, name every separate thing a player would notice that capability or leaf ships or tests (one effect among several, a creature that must appear, a control that must fail), each with the id of the scene that tests it ('' if none) and `ok`”

And:

> “Assess coverage of every stated experience.”

[guess ~98%] This is the sentence chain that turns every “must not” into something requiring acceptance evidence. The judge is largely doing what it was asked to do when it refuses an untested Designer-added exclusion.

[measured] The same function directs:

> “For a capability claiming behaviour across a range, identify the relevant inputs and situations from its words.”

And:

> “Hunt parameter regimes and regions, not examples.”

[guess ~95%] That instruction specifically encourages stronger wind-direction coverage, forced-weather cases, exhaustive animal comparisons and additional operating conditions. It has no sufficiently concrete boundary between an essential untested behavior and an optional stronger demonstration.

[measured] It also says:

> “This one pass must list EVERY gap: each round of gaps costs a full rewrite, exam and judge, so a gap held back for later is the failure this checklist exists to stop.”

[guess ~95%] That creates pressure to include every defensible concern now. It does not tell the judge to stop when one adequate demonstration and one useful rejection have been established.

**The scene contract makes stronger causal proof the default.**

[measured] `roles/designer_scene_contract.md` says:

> “Control: passes when the expected rejection or absence occurs, and it must distinguish the intended mechanism from a plausible alternative explanation (`rules_out`).”

And:

> “Removing the object is not automatically a useful control: the positive case needs evidence it used the mechanism.”

[guess ~95%] These are sound instructions for avoiding the owner’s ladder-that-was-never-needed problem. The overreach comes when “a plausible alternative explanation” becomes an expanding list of alternatives, with no stopping condition.

**The refusal contract can turn one possible test into the specification.**

[measured] `coverage_judge.py::RECORD_TEXT` requires `would_pass` to be:

> “the concrete result that would pass, checkable by a script or a fresh judge”

[guess ~95%] Concrete repair instructions are useful. But “add a map-wide observation sufficient to distinguish a front from a flood” and “below one half at the end of days 1, 2 and 3” are different commitments. The second should not acquire authority merely by appearing under `would_pass`.

[measured] Document 02 says the numbers were chosen in the fixes. That is only partly correct. Look 7’s judge already demanded:

> “at the end of days 1, 2 and 3”

and:

> “stays below one half”

[measured] The fixes chose four days and the implementation details. The judge itself supplied the original three-day, half-map boundary.

[measured] `roles/criteria_fixer.md` permits tightening directly:

> “tighten it: add a control, move a threshold toward stricter, name an object”

But says:

> “You may not loosen it (remove it, drop a control, move a threshold toward permissive) unless you can show that no owner bar or spec line asks for the property”

[guess ~95%] This is asymmetric. Added strictness is easier to introduce than to remove. It protects genuine owner requirements, but also protects agent-created methods unless their relationship to the owner’s requirement is examined carefully.

**The loop does not reliably preserve closure.**

[measured] `coverage_judge.py::delta_prompt` begins from:

> “A previous judge listed every gap”

and ends with:

> “Answer `covered` only when every claimed gap is fixed and no change opened one.”

[measured] `roles/designer_lock.md` adds:

> “A gap you do not claim stays open”

[measured] The implementation confirms that behavior: [`delta_merge`](/home/mandrake/rm/bench/src/RimMandrake/rimflow/coverage_judge.py:395) appends carried gaps and changes a returned `covered` to `not_covered` when carried gaps remain.

[guess ~99%] That is the immediate explanation for look 8’s contradictory result. A bookkeeping omission was allowed to overrule the review’s recognition that the defects were repaired.

[measured] Current [`retag_against_prior`](/home/mandrake/rm/bench/src/RimMandrake/rimflow/coverage_judge.py:616) also treats a late finding on a changed inventory or leaf entry as `changed`. It does not establish that the particular demand was caused by the particular edit.

[guess ~95%] Rewording a large leaf can therefore expose unchanged parts of it to new blocking demands while appearing to obey the “changed material only” rule.

**Two present safeguards are incomplete.**

[measured] In [`bar_rule.blocks`](/home/mandrake/rm/bench/src/RimMandrake/rimflow/bar_rule.py), severity is consulted for late findings. A non-late finding labeled `experience` can still block with `severity: polish`.

[measured] Look 7 g3 has exactly that combination: an experience finding labeled polish, yet listed among blocking gaps.

[guess ~99%] “Polish does not block” is therefore not fully implemented by merely adding a severity field.

[measured] `coverage_judge.py::reader_prompt` tells the second reader:

> “Read no file and edit nothing.”

The packet construction supplies portions of criterion text and the proposed demand, rather than independently checked source evidence.

[guess ~95%] The second reader can assess whether the demand sounds fair. It cannot reliably discover that dome art already exists, or that the judge’s description of the scene is false, without seeing the deciding evidence.

---

**3. Where the owner is wrong or overreaching**

**Two wind directions are not inherently pedantic.**

[measured] The original scene set one bearing and lit at the upwind end. The judge identified a particular false pass: a mod that “simply stops sideways spread whatever the wind’s direction.”

[guess ~95%] Reversing the wind is a small, relevant experiment for the sentence “The fire walks with the wind.” It checks response to wind rather than merely a fire’s shape. Bearings 90 and 270 are test inputs, not tuning requirements imposed on the game.

[guess ~90%] I would keep that test. I would challenge treating that exact test design as the only attainable path to passing. Another clear demonstration of changing wind changing spread could establish the same experience.

[measured] The final wind live read remained **UNRUN**. The record does not establish that the shipping mod actually ignored wind before these proof changes.

**A bounded burned share addresses a real omitted promise, but the chosen bound is not established.**

[measured] The Designer’s leaf promised:

> “It must not read as a flood that takes the whole map and its grass”

Its proposed oracle added:

> “never most of the map inside a few days”

[guess ~95%] Once those statements were in the accepted leaf, the judge was right to identify missing coverage. The owner cannot retain them as passing promises while treating every observation of map-wide burning as irrelevant.

[guess ~98%] But neither “natural grass fire” nor “clear before and after regions” establishes a universal half-map limit over three or four days. That boundary was a choice, not a discovered meaning of the owner’s words.

[measured] The final implementation’s [`_r6_burned_share`](/home/mandrake/rm/bench/src/RimMandrake/Pyrelands/validation.py:4624) describes its measure as:

> “Cells burned since generation outside the fire pads”

[guess ~95%] Cumulative area burned is not the same experience as the whole map being consumed at once. A fire can move naturally, leave fruit beds, permit regrowth and eventually visit much of the map. The selected measure can reject that behavior without showing the rejected experience.

**The off-switch objection was based on stale information, but the final control also overreaches.**

[measured] The owner objected that “almost nothing burns with the feature switched off” would not be true. Document 02 acknowledges that this summary was stale. The final control requires the opposite: wind off must produce a flood.

[guess ~99%] His physical objection to “nothing burns” was reasonable. It was not an accurate objection to the landed test.

[measured] [`burned_share_verdict`](/home/mandrake/rm/bench/src/RimMandrake/Pyrelands/validation.py:4589) returns unmeasured when the wind-off run does not cross the majority boundary.

[guess ~95%] That requirement is also too strong as a general acceptance condition. Correct wind handling does not imply that ordinary fire must burn most of every selected map. Fuel, weather and layout can prevent that.

[guess ~95%] Turning the feature off is useful evidence. Requiring the off state to exhibit one particular disaster makes the proof depend on a second outcome that the product need not guarantee.

**His proposed looser bars are useful experiences, but insufficient replacements for the full contract.**

| Proposed phrase | What it usefully asks for | What it leaves unresolved |
|---|---|---|
| “Significantly more abundant fire than vanilla (estimated)” | A visibly fire-rich biome | Whether fire moves, relights, preserves an ecological cycle or behaves sensibly around pawns |
| “Driven by the wind clearly” | Observable response to wind | The evidence still needs to distinguish wind response from a fixed preferred direction |
| “Clear before and after regions” | A readable front and scar suitable for fruit | Whether fruit actually emerges, can be harvested and feeds a pawn; whether other promised systems work |

[guess ~95%] “Estimated” should permit an inexpensive visual comparison. It should not mean that no comparison is needed. A rough impression still needs a named observation, otherwise two reviewers can apply different private standards.

[guess ~95%] If these phrases replace only the fire bars, they do **not** authorize dropping the plant, animal, weather, food or save/reload bars. Judged against the actual omissions, these phrases alone would not reject:

- [guess ~98%] The fire-sense proof in look 3 g2, where nobody had to encounter fire or become urgently hungry at fire duty.
- [guess ~98%] The immunity proof in look 3 g4, where the beast did not have to endure fire.
- [guess ~98%] The missing hide-bank experience in look 4 g1.
- [guess ~98%] The missing forced-rain case in look 4 g8.
- [guess ~99%] The false claim of a completed live wind pass in look 7 a2.

[measured] These were demonstrated **coverage or record defects**. The record does not establish that the corresponding shipping behavior was broken in every case.

[guess ~95%] His looser fire bars would also stop rejecting some things that should be allowed: cumulative burning above half a map, ordinary fire continuing with wind carry disabled, and relights inside a colony after he expressly removed that exclusion. Those are not losses of genuine protection.

**The owner also helped ratify some escalation.**

[measured] He authorized “Fix the 17 gaps, one final look.” He later explicitly selected:

> “Keep ‘twice’, raise body to 9+”

The offered option warned that this changed health, meat and combat balance and could break again if a larger animal were patched in.

[guess ~99%] The giant episode cannot fairly be blamed entirely on a peevish judge. The Designer introduced a stronger criterion, the judge correctly found it inconsistent with the ruled size, and the owner then chose the more expensive specification.

[guess ~95%] Finally, “no tuning numbers in bars” cannot mean “retuning never requires relevant validation.” If retuning makes the giant look ordinary or makes watered crops indistinguishable from dry crops, it has changed the promised experience. Removing numerals from the sentence does not remove that obligation.

---

**4. Recommendations**

**Define a FLAW by a closed set of reasons and required evidence.**

[guess ~90%] Permit a blocking finding only when it supplies all of the following:

1. **The exact existing requirement.** Quote it and identify its authority. An owner bar, an approved experience or a standing rule qualifies. A new interpretation invented in the refusal does not.
2. **One recognized defect.** Missing applicable check; missing necessary exposure; wrong instrument or expectation; contradiction; false claim of completed work; or an observed failure.
3. **The deciding evidence.** Cite the current artifact and the relevant passage or result.
4. **Why existing proof does not establish that requirement.** Identify the missing outcome or the concrete way the current setup can accept without encountering it.
5. **The minimum result needed to close it.** State the outcome, without prescribing an unnecessarily specific implementation.

[guess ~95%] A refusal that supplies only “another case could fail,” “this mechanism deserves its own control,” or “a stronger experiment would be possible” is not sufficient. Otherwise every repaired proof creates material for another hypothetical objection.

[guess ~95%] Use these mechanical questions:

| Question | Treatment |
|---|---|
| No scene or other check addresses an existing promised outcome? | FLAW |
| The scene can accept without the relevant fire, bite, heat, water or action occurring? | FLAW |
| The instrument reads the wrong thing, or the expected result rejects the correct ruled build? | FLAW |
| A record claims a run, approval or restriction that is contradicted by its source? | FLAW |
| A working check could be strengthened with another direction, seed, comparison or internal read? | PROOF-RIGOR, unless a concrete existing requirement remains entirely untested |
| The judge introduces a new threshold, operating condition or implementation preference? | Nonblocking proposal |
| The finding concerns reset housekeeping? | Do not emit a mod finding |

[guess ~95%] Distinguish **correcting a flaw** from **reopening acceptance**. False descriptive text should be corrected. That does not automatically justify a new exam and full judge run. A local check that the false statement is gone can close it.

[guess ~90%] Replace broad `would_pass` prescriptions with two fields in the judging record: the necessary closing result, and an optional suggested method. Only the result binds. For the flood finding, the result would be evidence of the agreed non-flood experience; “three days below half” would remain a proposed method until justified.

**Stop after one full look and one repair look for the frozen release.**

[guess ~85%] My proposed limit is:

- One full coverage review establishes the complete list.
- One repair review examines those findings and actual consequences of the fixes.
- No third open-ended coverage review starts.

[guess ~95%] If a genuine listed flaw remains, the work stays incomplete. It goes back for that specific repair and verification against the already recorded closing result. The limit stops further exploratory judging; it does not confer a pass.

[guess ~90%] A newly discovered issue after that point can block only with concrete evidence of a real flaw: an observed failure, a demonstrably wrong expectation, an unexercised existing outcome or a contradiction. A second reader checks the deciding evidence. Merely imagining a stronger proof is insufficient.

[guess ~95%] Rewording a leaf, repairing a record, re-pinning artifacts or granting “one more look” must not reset that release’s review history. A genuinely new owner-requested behavior earns review of that behavior and its affected interactions, not a fresh search across everything.

[guess ~95%] Keep coverage and execution separate. “Covered, live read UNRUN” means the proof plan is adequate. It must not become “the mod passed live validation.” The later live gate must enforce that distinction.

**Constrain what the Designer can put in a leaf.**

[guess ~95%] The Designer may write:

- A player-visible outcome supported by an owner statement, an existing approved capability or a standing rule.
- A plain example of success and a concrete example of failure.
- Conditions necessary to encounter the outcome.
- A proposed inexpensive way to observe it.

[guess ~95%] The Designer may not silently add:

- A new prohibition because it would improve the design.
- Every internal mechanism found in source code.
- Guarantees across all maps, animals, settings or circumstances when the approved experience does not require them.
- An exact numerical boundary merely because a script can evaluate it.
- An additional showcase as a substitute for finding missing functional coverage.

[guess ~95%] A “must not” should either negate the promised outcome or preserve an explicit ruling or observed rejection. “Moves with the wind” can reject “does not respond to wind.” It does not automatically authorize “must never burn most of any map within four days.”

[guess ~90%] Give each independently enforceable clause its own source reference. This can be maintained alongside the tree if changing its schema is undesirable. A whole-leaf source citation is insufficient when one leaf combines owner words, retained shipping behavior and agent interpretation.

[guess ~95%] Preserve the built-capability inventory, but stop equating one source file, saved setting or helper mechanism with one player-facing promise. The current allowance to classify something as `not_a_capability` should be used with an explanation.

**Handle non-FLAW findings without another acceptance cycle.**

[guess ~90%] Keep them in the verdict’s advisory records and, where useful, the existing `version/polish.md`. Record each once, with its evidence, likely benefit and the event that would make it worth revisiting.

| Kind | Who reads it | When it is reconsidered |
|---|---|---|
| PROOF-RIGOR | Person maintaining the proof and the Conductor | When that feature is next changed, or when a real failure exposes the weakness |
| POLISH/TUNING | Designer and Conductor | During a planned tuning or presentation pass |
| LATE | Conductor | Once, to distinguish a real missed defect from an added obligation |
| JUDGE-ERROR | Maintainer of the judging process | Prompt or program repair and calibration, without charging the mod another rewrite |

[guess ~95%] Do not automatically create implementation tickets, owner questions or exam reruns from those entries. The owner should see a short selection of consequential choices, not every possible improvement.

[guess ~95%] Let the repair review explicitly resolve a carried gap when it has inspected evidence establishing the recorded closing result. Missing `coverage_fixes.json` bookkeeping can be repaired locally. It should not preserve a refusal whose factual basis the judge has already found obsolete.

**Measure ratcheting using new mandatory demands on unchanged material.**

[guess ~85%] Require every mandatory demand to name a stable requirement and check identifier. Store the relevant requirement, test and implementation hashes from the first look.

For every later look, compute:

> **R = new mandatory demands on unchanged relevant material ÷ all mandatory demands in later looks**

[guess ~85%] Set the initial alarm threshold at **one such demand**, meaning `R > 0`. This is a proposed operating threshold, not a measured optimum.

[guess ~95%] When it fires, suspend that new demand’s blocking effect and ask for the concrete-flaw evidence described above. A genuine late defect can then be confirmed. An additional proof preference remains advisory.

[guess ~90%] This can be cheap: compare identifiers and stored hashes, and require the judge to identify the changed passage that supposedly caused a changed or regression finding. Use the smallest independently checked clause, rather than the entire leaf. Otherwise an unrelated wording edit makes old material look newly eligible.

[guess ~95%] Automatic comparison cannot determine whether two differently worded demands mean the same thing. That limitation is **unknown without calibration**. Stable identifiers and required evidence make the signal useful without pretending the program understands the whole design.

[guess ~99%] Add one separate consistency check: a gap cannot remain open at the same evidence version when its structured repair assessment says the closing result is satisfied. That would have caught look 8 without another coverage search.

---

**5. Risks of these recommendations**

[guess ~95%] These recommendations deliberately accept less predictive coverage. Some defects will get through the coverage stage. The protection is an actual played look, targeted live execution and regression checks built from failures, rather than more hypothetical coverage rounds.

| What could get through | How it should be caught later |
|---|---|
| A wind implementation that works at the tested opposite bearings but fails at another angle | A live run with changing wind; preserve any failing bearing as a regression case |
| A fire ecology that looks reasonable on the chosen map but floods a different layout | A played colony look; retain the failing map and settings as a repeatable regression |
| Fire that moves correctly in short tests but creates a disappointing ecological cycle | Play through burning, fruit emergence and regrowth together |
| A rarely used setting that fails to disable an effect | A targeted live off/on test when that setting changes or a failure is reported |
| An internal mechanism that is broken while the visible outcome happens another way | Investigate when that mechanism matters to a real interaction or observed failure |
| A visual experience that technically satisfies the written examples but feels wrong | The owner’s played look, followed by a specific correction or next-version choice |
| A proof plan that is excellent on paper but cannot run against the game | The live gate must require the actual run and retain UNRUN or unmeasured results honestly |

[guess ~95%] The largest risk is mistaking “we stopped asking for stronger proof” for “we proved the behavior.” Those are different statements. The coverage judge should establish that the agreed work has an adequate, usable path to verification. Live validation must establish that it actually works.

[guess ~95%] I would retain the reversed-wind test, replace the unsupported universal flood boundary with an agreed observable experience, remove the requirement that the off run must flood, and preserve the substantive missing-behavior checks. The main repair is to stop letting new interpretations and bookkeeping failures repeatedly redefine what completion means.