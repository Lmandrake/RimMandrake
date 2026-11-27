# WreckedMachines Designer log

The verbatim record of each turn with him: what was sent, what he answered. `record.json` is the working record.

## 2026-11-26 turn 1 (run rm-role-designer-1795752087), sent 8:15 PM PST

Text: `design/concepts/WreckedMachines/turn_01.md`. It opens with the offer of a look at the running mod, then the case
for and against a generic version, then the root paragraph (`record.json` `root_draft`), its Attack and its Picture.

### Asks sent (three)

1. **a_root:** Is the paragraph under Claim Wrecked Machines? Say "yes", or change any word. The word I doubt is "any"
   in "any RimWorld game": strike it if the factory mod is simply required. The Attack says why.
2. **a_how_found:** Picture a stranger's colony in an ordinary game, a year in. When does this mod first show itself?
   (a) Only in the rooms of an ancient ruin, on a tile that the colony settles on or visits. The bench's note of your
   card of 2026-10-03 reads "relics are found at ancient ruin sites". (b) Also now and then on an ordinary map: one
   wreck, half-buried, there on arrival. Every colony meets one early, and the ruins hold the good ones. (c) Something
   else that you picture. I recommend (b), judged on one test: does a colony that never leaves home ever see the mod?
   What (b) costs: a wreck is less rare.
3. **a_riders:** Three finished rules sit in this mod's folder and are not about a wreck that is found and repaired:
   the alloy forge that comes early with its plasteel recipe late; the one rule for what smelting and cremation give
   back; and the water distillation machine. A stranger who installs Wrecked Machines gets the first two, and the third
   when FlowWorks is also loaded. What does 0.1.0 say about them? (a) They are outside this mod's promise. The bars of
   0.1.0 do not judge them. They go on working as they do today, and each moves to the mod it belongs to in a later
   version. (b) They are part of what this mod is, a factory-floor mod, and each gets bars of its own in 0.1.0. (c) A
   different answer for each; say which. I recommend (a), judged on one test: the paragraph has one promise, and a
   tester's time goes to that promise.

### Review

Reviewed by rm-judge a467e768ff82de4be (fresh Opus, not the author): all three pass.

- a_root narrowed to the word "any". The first draft also doubted "No colony can make one" and offered a second
  reading (the build menu as the late road). The judge: his ruling of 2026-09-16, "remove the VFE factory, not the
  manual one.", came the day after the stand-alone ruling and settles the phrase; the second reading would undo a built
  capability. The Designer agreed and took the second reading out of the page.
- a_how_found: option (a) had put "rare, an expedition, as your card said" on his card. The card's note has neither
  word. Reworded.
- a_riders: "gets all three" was false; the distillation machine loads only with FlowWorks. Corrected. His first-version
  card (OWNER:1794896960342841440) is now cited with its date.
- Page: the generic case quotes both halves of his sentence, names the cost of two designs, and no longer says that he
  asked for the case in writing. Two claims nobody could confirm were taken out.

### Not sent this turn

- a_quick_look: struck as an ask. The look is this turn's `quick_look` offer in the result and the first section of
  the page.
- a_how_study_feels: held until after the look; two notes for stage 2 are on the ask.
- a_component_source: new draft for stage 2.

### New in the record this run

- `root_draft`: the paragraph and its judged-first line. It is not the root. Stage 1 ends only on his approval.
- `c_factory_mod_required` (core): the mod does not load without the factory mod, and the paragraph says "any
  RimWorld game". His answer to a_root settles the word.

## 2026-11-26 turn 1, his answers (recorded by the Conductor 9:00 to 9:01 PM PST; taken in by run rm-role-designer-1795756411)

He answered all three asks on the Conductor's cards of 8:29 PM PST. He did not answer the offer of a look.

### a_root: he typed his own statement (OWNER:1795755622961436106)

> Add this (you may rephrase for efficiency or clarity) "The mod changes specified furniture-installable machines such
> as Vanilla Factory Enhanced into advanced, ancient machines that can no longer simply be researched and built like
> normal. Instead, they must be found and retrieved to a safe location, studied to enable research, and then slowly
> repaired through several levels of functionality: wrecked (nonfunctional), Kludged (minimal), Refurbished (full
> functionality but slower than original), Original (no longer attainable through research or repair, used only for
> comparison). Each repair requires machine study, research bench time, and considerable resources. The final
> refurbishment requires a rare ancient component. While the concept may be applied to any game tree, the mod's initial
> version will only support Vanilla Factory Enhanced in this fashion." This is the original intention of this mod and
> remains true. Please revise with the current version's detail while maintaining the truth of this statement.
> remember: we must first prioritize Utinni service, and VFE plus some versions of vanilla expanded items like
> archotech power supplies and psychic emitters will be the only supported options.

What became of it: his statement is the root (`record.json` `root`; `words` holds the statement word for word, `text`
its rephrasing, `agent_words` each wording that is not his). A fresh Opus reader (a90c3d35ce434f40d, not the
author) compared the two; six wordings in the record that said more than his words were corrected on its findings. The paragraph of turn 1 is not the mod and is gone from
`record.json`; `turn_01.md` keeps it as sent.

### a_how_found: by card (OWNER:1795755647483442186)

> Ruins, plus a rare wreck (Recommended)

### a_riders: he typed an answer and picked no option (OWNER:1795755673273656447)

> This is confounded. Giving the "smelter first" is an Utinni-tier decision independent of this mod about machine
> availability. Each machine Certainly Will need specific recipies blessed per repair tier, production rates, etc...
> that will be the normal onboarding process for any device into the Wrecked Machines mod. We may be able to
> semi-automate this to support other machines, but not in 0.1.0. Water Distillation is definitely a FlowWorks machine
> that would then be onboarded into this mod to become Wrecked if we so desired (and without this, it would remain a
> fully functional machine in FlowWorks).

The ask was a defect of this role: it put three unlike things under one choice and did not ask first whose decision
each was. A lesson is filed.

### Where his statement differs from the built mod and from his earlier words (the Designer's reading, not his words)

| His statement | Built today, or said earlier | Taken as |
|---|---|---|
| "found and retrieved to a safe location" | The smelter's Wrecked and Kludged grades cannot be picked up. 2026-09-15: "repairing big machines in place, and that's excellent." | Both hold: carry the wreck to safety, then repair it where it stands (`d_reading_retrieve_then_repair`). Open for stage 2: `c_wreck_cannot_be_carried`. |
| "wrecked (nonfunctional)" | The power-cell wreck gives a faint current. 2026-09-15: "Their batteries just slowly lose capacity over millenia yet still work." | A Wrecked machine gives nothing; the sagging battery is the Kludged and Refurbished levels. Open for stage 2: `c_wreck_gives_a_trickle`. |
| "Refurbished (full functionality but slower than original)" | The refurbished smelter runs five of six recipes. | His words settle it; a build item (`c_kludged_and_refurbished_levels`). |
| "Each repair requires machine study, research bench time, and considerable resources" | Kludged needs no study and no research. | His words settle it, and they give `c_study_fights_build_over` its direction: study comes before every repair. |
| "Original (no longer attainable through research or repair, used only for comparison)" | A Mod Setting, off as shipped, brings the original-grade smelter back. | Shipped behaviour matches; one line at stage 3 (`c_full_restoration_switch`). |
| "the mod's initial version will only support Vanilla Factory Enhanced" | One factory machine, the smelter, is onboarded. | A question for him at stage 2: how many of the factory's machines (`a_which_factory_machines`, draft). |

### Decisions taken in this run (each can be undone by him)

- `d_root_is_his_statement`: no second approval is asked for the rephrasing.
- `d_riders_fate`: 0.1.0 has no bar for the forge's steps, the distillation machine or the salvage rule. He did not
  speak of the salvage rule; that part is the Designer's call.
- `d_reading_retrieve_then_repair`: a position for stage 2, not yet a line.

## 2026-11-26 turn 2 (run rm-role-designer-1795757288), sent 9:43 PM PST

Text: `design/concepts/WreckedMachines/turn_02.md`. It repeats the offer of a look, says what was taken from his three
answers, shows eight readings that the Designer took itself, and sends two asks.

### Asks sent (two)

1. **a_which_factory_machines:** A stranger installs Wrecked Machines beside the factory mod and opens the build menu. The factory mod has 18 production machines. Which picture is 0.1.0? (a) One ancient machine: the automated smelter must be found and repaired; the other 17 are researched and built as before. (b) An ancient factory: all 18 must be found and repaired. (c) A proven handful: the smelter and two more, taken in the order in which the campaign repairs them; the other 15 are built as before until a later version onboards them. I recommend (c), judged on one test: can a second machine go through onboarding by the written steps alone?
2. **a_component_source:** The last repair, to Refurbished, costs an Ancient Component, and nothing gives one today. Where does a colony get one? (a) Out of another wreck: colonists take a wrecked machine apart, the wreck is gone for good, and one Ancient Component is left. Each wreck found is a choice between a machine and a part. (b) Only as a rare find in the rooms of ancient ruins. (c) Both: (a), and now and then one lies in a ruin. I recommend (c), judged on one test: does the component make the player choose?

### Review

Reviewed by rm-judge a15c1525ac03b2c3f (fresh Opus, not the author): both asks pass with no rewording. It measured the
factory mod's machines again: 18 production machines, all with a minified form (17 without Vanilla Cooking Expanded).
Three sentences of the page said more than the sources and were corrected:

- Reading 1 said that his two sentences "both hold". The mod he praised on 2026-09-15 had a smelter wreck that cannot
  be picked up, so they conflict; the newer statement decides, and "where the machine stands" is the Designer's gloss.
- Reading 6 put the forge's move on his words. He spoke of "smelter first"; the forge's steps are a reading.
- Reading 7 put the wealth rule's deferral on his first-version card. The card says what happens to an extra; calling
  it an extra is the Designer's call.

### Calls taken in this run (each can be undone by him; shown to him as readings on the page)

- `d_wreck_is_carried`: a wreck of any size is carried home; each repair is made where the machine stands.
- `d_wrecked_gives_nothing`: a Wrecked machine has no function; a faint light is a look.
- `d_study_before_each_repair`: two research projects for each machine, each opened by study of the machine at its
  present level; Research Reinvented's study stays on top when that mod is loaded.
- `d_found_is_wrecked`: a found machine is always Wrecked; which wrecks lie where is data a layer above can change.
- `d_three_looks`: Wrecked, Kludged and whole are told apart by eye; Refurbished may share the Original's picture.
- `d_riders_move_no_interim`: the three rules outside the promise work as today until each move lands.
- `d_wealth_next_version`: a relic's value outside colony wealth waits for the next version.

### Resolved in this run

`c_wreck_cannot_be_carried`, `c_wreck_gives_a_trickle`, `c_study_fights_build_over`, `c_grades_share_one_picture`,
`c_riders_in_the_folder`. Still open and core, each waiting for one of the two asks: `c_half_ancient_factory`
(a_which_factory_machines), `c_no_way_in` (a_component_source).

### Struck, not sent

- a_how_study_feels: his statement settled it; the part about Research Reinvented is taken in
  `d_study_before_each_repair`.

## 2026-11-26 his reply to turn 2 (OWNER:1795760440829904733, 10:20 PM PST), and turn 3 (run rm-role-designer-1795761299), sent 10:47 PM PST

His reply, word for word: "Yes I will look at the existing wrecked machines. By the way they CAN be moved with special
hauler droids or machines you can ride in through droidworks but notified or built." The last four words are kept as
typed; the Conductor asked him what they mean, and nothing is read from them. He has not answered the two asks of
turn 2; both stay sent.

Text of turn 3: `design/concepts/WreckedMachines/turn_03.md`. The look: `design/concepts/WreckedMachines/look_01.md`,
staging filed as `RIMMANDRAKE_STAGE_WRECKED_MACHINES_LOOK_HE_SAID_YES`.

### Ask sent (one)

3. **a_who_moves_a_wreck:** A stranger's game has Wrecked Machines and the factory mod, and no Droidworks. Three colonists stand in an ancient ruin in front of a wrecked smelter of 3 by 4 cells. How does it get home? (a) By hand: colonists uninstall it and carry it, as they carry any machine of the factory mod. Who may lift a wreck is data that a layer above can narrow, so the campaign gives the lift to hauler droids and ride-in machines only. (b) Only by a heavy hauler, in every game, and this mod brings a plain hauler of its own for a game without Droidworks. (c) Only by a heavy hauler, in every game, and this mod brings none: without one, a colony repairs a wreck only where it lies. I recommend (a), judged on one test: can a stranger with this mod and the factory mod alone do what your statement says, 'found and retrieved to a safe location'?

### Review

Reviewed by rm-judge a44e086c95b4295e7 (fresh Opus, not the author): the ask passes, and it reads nothing into the four
words. Three sentences of the page said more than their sources and were corrected (a guess that the four words might
be this same question; "all say" in the Attack; the lift list "says what your reply says"). The picture of answer (c)
was made to match the answer's words.

### Changed in the record by this run

- `s_look_yes_and_haulers`: his reply. `d_look_accepted`: the look is accepted and filed.
- `d_feasible_wreck_lift`: what is built for lifting a wreck (the Property mod's hauler job, five marked Droidworks
  chassis, the lift list of 2026-11-01 with its pass not built, the built smelter wreck with no carried form).
- `d_wreck_is_carried` is reopened in one part: who lifts a wreck. It had missed the lift list and the hauler design.
- `c_who_lifts_a_wreck`: new, core, open, waiting for a_who_moves_a_wreck.

## 2026-11-26 his three card answers (10:38, 10:39 and 10:57 PM PST), and turn 4 (run rm-role-designer-1795763300), sent 11:25 PM PST

His answers, word for word, from the ledger:

- a_which_factory_machines (OWNER:1795761534460592124, by card): "How many of the factory's machines are ancient in
  0.1.0 → All 18 machines". The option's description on the card (our text): "Why: the mod at full strength; every
  factory machine is out in the world to be found. Cost: 136 new pictures and 17 more onboardings by hand, and a
  stranger who already has a factory loses the most." The options he did not take: "A proven handful (Recommended)",
  "Only the smelter".
- a_component_source (OWNER:1795761550785045693, typed on the card, no option picked): "Only found in ruins or via
  plot".
- a_who_moves_a_wreck (OWNER:1795762605668672773, by card): "How does that wreck get home in a game without Droidworks
  → Colonists carry it (Recommended)". The options he did not take: "The mod brings a hauler", "No hauler: repair in
  place".

Text of turn 4: `design/concepts/WreckedMachines/turn_04.md`.

### Ask sent (one)

4. **a_plasteel_on_the_forge:** A colony has found a wrecked alloy forge, studied it and made it Kludged. It makes its first alloys. Which picture gives it plasteel? (a) Research: a late research project opens the plasteel recipe on any working forge, the Kludged one included. This is your sentence of 2026-10-09, and no Ancient Component is spent. (b) The Refurbished forge: plasteel is the recipe that the last repair brings. It takes the second study, the second research project and one Ancient Component, from a ruin or "via plot" (your words). (c) Both locks: the Refurbished forge, and the late research project too. I recommend (b), judged on one test: is there a reason to spend a rare Ancient Component on the forge?

### Review

Reviewed by rm-judge a5105ca4acff55348 (fresh Opus, not the author), three reads. The first read struck the page: it
had decided where plasteel sits as a reading, and the judge found that his words of 2026-10-09 put that unlock on
research; the reading became this ask. It also found a false cost line (durasteel is re-melted from slag on the
smelter), his "machine availability" words put on the forge (he said them of "smelter first"), and a rule on Kludged
machines made from one def. The second read struck the ask for saying that plasteel comes only from the forge. The
third read passed the ask and the page.

### Changed in the record by this run

- `s_all_eighteen`, `s_component_ruins_or_plot`, `s_colonists_carry`: his three answers. The three asks are answered.
- `d_all_eighteen_shape`: the 18 machines measured, and what "all 18" means (the build menu, an old factory, a switch
  for each machine, two research projects each, the build order, the onboarding rule).
- `d_forge_is_onboarded`: the alloy forge is one of the 18, so its research step that opens it for building ends with
  its onboarding. `d_riders_fate` and `d_riders_move_no_interim` are corrected for the forge.
- `d_component_from_ruins`: components lie in ruins; "via plot" is read as the campaign's story (a reading).
- `d_lift_is_data`: colonists carry; who may lift is data that a layer above narrows.
- Resolved: `c_no_way_in`, `c_half_ancient_factory`, `c_who_lifts_a_wreck`.
- `c_plasteel_behind_a_component`: new, core, open, waiting for a_plasteel_on_the_forge.
- `inv_more_factory_machines` and `inv_ancient_component_source` are in scope by his answers.

