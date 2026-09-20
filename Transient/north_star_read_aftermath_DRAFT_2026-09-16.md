# `must read` candidates — Aftermath + AftermathRites (DRAFT, binds nothing)

Written 2026-09-16T18:15-0700 on the **Mac laptop** — no game, no bridge, RimSage has
never connected here. Every count below is MEASURED from a file on disk or marked
UNMEASURED. Working spec: `design/RimMandrake/north_star_validation_spec.md` §10 +
§11 (the read axis) and §6a (axis-scoped hashing). Reference examples read in full:
`design/validation_walks/RimMandrake/Oracle.md` (read axis) and `Graffiti.md`
(validated visual axis).

⚠️ **DRAFT — BINDS NOTHING.** Per spec §3 and §10.1 a DRAFT checklist cannot fail a
mod and cannot green one. Every line here is an agent's distillation. Only the owner
promotes a line to a bar.

⛔ **Nothing here may be written into either walk yet.** Spec §6a: the section hash is
whole-section today, and §7's owed items 8 (axis-scoped hashing) and 9 (`reads=`,
`capture_text`, `uncovered_reads`) do not exist. Neither `Aftermath.md` nor
`AftermathRites.md` currently has a `## north star` section at all, so appending one
breaks no existing validation — but the read machinery still cannot enforce it.

Provenance tag per line: 🗣 his verbatim recorded words or a ruling of his ·
📐 a def or a source file measured this pass · 🤔 my inference, weakest, cut freely.

---

## 1. The measured inventory — what a player can read today

### 1a. Aftermath (`src/RimMandrake/Aftermath`, `mandrake.rm.aftermath`)

**MEASURED**: 27 files, 0 PNG, exactly one XML (`About/About.xml`). Exactly **one**
player-facing text call in the whole source tree — `Find.LetterStack.ReceiveLetter`
at `AftermathRuleRunner.cs:337`. Zero `Messages.Message`, zero `Alert`, zero
`InspectString`, zero `.Translate()`. Seven `Log.*` calls, all console-only and
excluded from every count below (two of them `Prefs.DevMode`-gated).

| group | authored strings | reachable | note |
|---|---|---|---|
| letter channel | **1** | 0 in practice | the telegraph-text fallback `"{0} is stirring."` (`AftermathRuleRunner.cs:336`). Reachable in code; unreached by shipped data, because all 8 rules author a `telegraphText`. |
| Mod Settings | **7** | 7 | `RM_AftermathMod.cs:57-71` + `SettingsCategory()` = "Battle Aftermath" |
| About.xml | **2** | 2 | `<name>` + `<description>` |
| **total** | **10** | **9** | MEASURED |

🔑 **The engine authors almost nothing the player reads.** Every word of the
aftermath *experience* is data in AftermathRites; Aftermath owns the CHANNEL. Its
read lines therefore have to be about the channel's integrity (does the authored
string arrive intact, with the right substitutions, on a card that fits) plus its own
non-letter prose (settings, mod-list description). That is a different shape from
Oracle and it is worth saying out loud before the lines are read.

### 1b. AftermathRites (`src/RimUtinni/AftermathRites`, `mandrake.rut.aftermath`)

Defs-only, no C#. **MEASURED**: 4 files total — `About/About.xml`, `LICENSE`, and two
def files (`Defs/RM_AftermathRuleDefs.xml`, `Defs/RM_AlliancePairDefs.xml`). No PNG,
no assembly, no `validation.py`.

| group | authored strings | messages | reachable messages |
|---|---|---|---|
| telegraph (`telegraphLabel` + `telegraphText`) | 16 | **8** | **5** |
| payload letter (`letterLabel` + `letterText`) | 16 | **8** | **0** |
| **letter/telegraph total** | **32** | **16** | **5** |
| About.xml | 2 | — | 2 |
| rule `<label>` ×8 | 8 | — | 0 today (surfaces only as the letter-title fallback, never reached) |
| `RM_AlliancePairDefs.xml` (6 defs) | **0** | — | — |

🔴 **5 of 16 — MEASURED independently this pass, and it matches the earlier pass's
number by a different route.** The two reasons, both read from source rather than
from the def file's own header:

1. **8 dead payload letters.** `letterLabel` / `letterText` are declared at
   `RM_AftermathRuleDef.cs:56-57` and a grep of all of `src/` finds **no read of
   either field anywhere** — the only other hits are unrelated vanilla `IncidentDef`
   `letterLabel` fields in other mods. `AFTERMATH_DEAD_LETTERS_1`.
2. **3 unwired trigger kinds.** `AftermathRuleEligibility` gates on `triggerKind`
   in all three predicates (`:16`, `:30`, `:42`), and `AftermathRuleRunner` calls
   only those three. So `BattleOutcome` (rules 1-3), `PrisonerHeldDuration` (rule 4)
   and `MentalBreakNearBattle` (rule 6) reach `SendTelegraph`; `GodBandCrossed`
   (rule 5), `RootedClockQuadrum` (rule 7) and `TakingEventWitnessed` (rule 8) are
   evaluated by nothing. `AftermathTriggerKind.cs:19,21,22` says the same, but it is
   corroboration, not the source.

⚠️ Rule 2 is *conditionally* reachable, counted as reachable: it needs an
`RM_AlliancePairDef` whose `a` matches the defeated faction AND an ally hostile to
the player (`AftermathRuleRunner.cs:296-307`). Six pairs ship, so the condition is
satisfiable.

### 1c. Two evidence channels, and which lines can be judged offline

Per spec §10.3, def-sourced text proves the words EXIST and channel-captured text
proves they ARRIVED. Of the 14 candidate lines below:

- **11 are judgeable from disk today** — all 6 `enumerated` lines (the authored set
  *is* the distribution), the 2 `fixed` lines over the fallback string and the About
  description, and 3 of the 4 `absolute` lines. No game, no bridge, laptop-runnable.
- **3 need a live channel capture** (`rimworld/list_letters`, per Oracle's walk):
  `telegraph_substitution_is_right`,
  `payload_arrival_names_its_cause`,
  `never_generic_raid_letter_for_an_authored_rule`.

---

## 2. Class distribution — and why this pair is the easy case

| class | count | which |
|---|---|---|
| `fixed` | **4** | all Aftermath: the fallback, the substitution, the payload arrival, the About description |
| `enumerated` | **6** | 1 Aftermath (the settings block, N=7) + 5 AftermathRites (N=8 / N=8 / N=8 / N=3 / N=34) |
| `open` | **0** | — |
| `absolute` | **4** | 2 per mod |
| **total** | **14** | 10 `must read` + 4 `cannot read` |

🔑 **Zero `open` lines, and that is the whole difference from Oracle.** Neither mod
contains a generator. Every string a player can read from either one is authored by
a human and sits in a def or a `.cs` literal. Consequences, each one removing work
that Oracle's checklist could not avoid:

- §10.2's distribution problem does not arise. No line needs an N the owner has to
  invent, and no line needs a k/N bar.
- §5's consequence — *"a mod whose validated checklist carries an open-generator read
  line cannot go GREEN unattended"* — does not bind either mod. Both can go GREEN
  unattended once the machinery exists.
- The judge's narrowed powers (§10.4) never come into play: on `fixed`, `enumerated`
  and `absolute` lines a model may pass, exactly as on the visual axis, because the
  artifact is stable and hash-pinned.
- 11 of 14 lines can be judged **today, on this laptop, with no game.** That makes
  this pair the cheapest read-axis work available and the right second sitting.

✅ Answering the brief's check directly: the expectation that these two mods would be
almost entirely `fixed`/`enumerated` **held**. I found no generator, no runtime
string assembly beyond one `string.Format`, and no LLM consumer in either mod.

---

## 3. The owner's own words — what I found, and what I did not

An earlier pass found **zero** owner quotes about Aftermath's *appearance*. That
holds for its *text* too, in the narrow sense: **no recorded utterance of his is
about these letters.** MEASURED: 8,609 ledger events, 23 mention "aftermath", exactly
1 carries an `ownerSaid` — *"Summarize and rule please."* (2026-09-05,
`PLOT_MECHANISM_MODS_WAVE_1`). Worthless as vision prose.

But the search was not empty. Three recorded rulings of his do bear on this text,
and two of them name Aftermath directly:

**🗣 R5 and R6, owner rulings 2026-09-08** (`MOD_NAMING_CONSOLIDATION_AUDIT_1.md:134-139`):

> R5. **Aftermath → RimChronicle (RM)**: a game-event evidence engine other mods
> hook … AftermathRites = its RUT data pack, renamed grammar-compliant.
>
> R6. **Engine + data-pack pattern RATIFIED as doctrine**: RM engine holds machinery
> + generic vanilla-style default content; scenario packs patch in from RUT.

**🗣 R9, owner ruling 2026-09-08**, same sitting, applied to Pyrelands but stated as
the doctrine's text half (`PYRELANDS_GENERIC_TEXT_1.md:4-7`):

> **de-campaign all text — labels/descriptions must read vanilla-generic**,
> uniquely-Ashkarr residue moves to UtinniPatches per the map.

🔑 Read together these are a ruling **about the text of exactly this pair**: the
engine's own strings must read generic, the campaign's words live in the data pack.
Two lines below (`prose_is_tier_neutral`,
`campaign_vocabulary_lives_here`) are that ruling and nothing else.

**🗣 His own voice on prescripted text**, verbatim, from the frozen decision sheet
`design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json`, row
`llm:inhabited-rumor-dialogue` (his sitting of 2026-09-02):

> *"I like it for now. Can start prescripted but if the LLM is available, it gets
> enriched. That's the general metric I'm thinking about: baseline prescripted stuff
> with LLM enrichment when available."*

⚠️ Honest about its reach: that row is about Inhabited's rumor dialogue, not about
Aftermath. What makes it admissible is that he calls it *"the general metric I'm
thinking about"* — and Aftermath's letters are the purest instance of "baseline
prescripted stuff" in the repo. It is his standard for this class of text, not his
statement about this mod.

**🗣 One nearby quote, offered and not used as an anchor** (2026-09-12,
`FASCINATING_WORLD_JUNK_1`): *"re-graphic and re-text them to make the world come
alive by... being dead, in the right flavor."* His voice on flavour text mattering,
about map junk. Cited so the search is auditable; no line rests on it.

**No `### the experience` block is drafted here.** Spec §1: *"This is the only part
an agent never writes."* The closest thing that exists is `plot_mechanisms_wave.md`
§2.2, which is **agent prose in a DRAFT proposal** written AFK on his brief, and
must not be laundered into his voice. Its two sentences are worth putting in front of
him as a *candidate* for him to adopt, reject or rewrite:

> *"Every aftermath telegraphs 0.5–2 days ahead through a surface that already
> exists … Nothing arrives out of nowhere twice; the player is being taught to read
> the sky."*

---

## 4. Aftermath — candidate lines

Proposed placement: a new `## north star` section in
`design/validation_walks/RimMandrake/Aftermath.md`, `read-state: DRAFT`.

### must read

**The telegraph channel — the mod's one letter call**

- [ ] `telegraph_fallback_reads_as_a_warning` (fixed) 📐 — the engine's own
      prescribed telegraph text, the string that ships when a data pack authors none,
      reads as an in-world warning naming a faction and a coming thing. 🔴 **Fails
      today for QUALITY**: the whole string is `"{0} is stirring."`
      (`AftermathRuleRunner.cs:336`) — three words and a period, no observation, no
      cause, no lead time. It is the read-axis analogue of a tile with "Pit" written
      on it. Per spec §10.2 *"the fallback is the floor, and the floor is fixed"*; the
      floor here is a stub. ⚠️ It is unreached by the shipped data (all 8 rules carry
      text), so this line binds a floor rather than a live defect — it earns its place
      because R6 makes Aftermath a pluggable RM engine whose next data pack may omit
      the field.
- [ ] `telegraph_substitution_is_right` (fixed) 📐 — every `{0}` a telegraph
      renders is filled with the faction the sentence actually means. 🔴 **Fails today
      for QUALITY, on rule 2, and it is a REACHABLE letter, not a dead one.** NEW
      FINDING this pass, from source: `SendTelegraph(def, targetFaction)` formats with
      `targetFaction.Name` (`:336-337`), and for `payloadFactionMode=AllyOfTrigger`
      `ResolveTargetFaction` returns **the ally** (`:293-307`). So rule 2's authored
      *"News of the fight has reached {0}'s allies. Livery not your enemy's own has
      been sighted on the roads."* renders as **the ally's** allies having heard —
      when the ally is the one coming, and "not your enemy's own" then contradicts
      the name in the same sentence. A judge saying NO can quote the span.
      ⚠️ Needs a channel capture of a rule-2 telegraph; the defect itself was derived
      offline from the two code paths.
- [ ] `payload_arrival_names_its_cause` (fixed) 📐 — when the queued payload
      lands, the text the player reads names the thing that caused it: the battle he
      won, the prisoner he is holding, the break in his colony. 🔴 **Fails today for
      ABSENCE** — `letterLabel`/`letterText` are read nowhere
      (`RM_AftermathRuleDef.cs:56-57`, `AFTERMATH_DEAD_LETTERS_1`), so the payload
      arrives as a vanilla `RaidEnemy` with vanilla's stock raid letter and the causal
      link is stated **nowhere at the moment it matters**. This is the mod's founding
      promise — *"hostilities born of what just happened"* — and the one line whose
      failure is pure absence.

**The mod's own non-letter prose**

- [ ] `settings_read_as_player_options` (enumerated, **N=7** — every string
      in `RM_AftermathSettings.DoWindowContents` plus `SettingsCategory()`) 📐🗣 — each
      settings string says what the *player* gets, in the player's words. Anchored in
      his 2026-09-12 ruling that every mod ships a real settings screen. ⚠️ **Passes
      today with one wobble**: *"Max queued follow-ups for the same faction at once"*
      is the engine's noun for what the player experiences as a returning raid. His
      call whether that clears the bar; this is the weakest line in the set and the
      first I would cut.
- [ ] `prose_is_tier_neutral` (enumerated, **N=10** — all 10 authored
      strings from §1a) 🗣 — nothing the player reads from this RM engine names the
      campaign. Directly R6 + R9: *"labels/descriptions must read vanilla-generic."*
      🔴 **Fails today on one string**: `About.xml`'s description cites
      *"design/Jawa/proposals/plot_mechanisms_wave.md Part 2"* — a campaign word and a
      repo path in a generic-tier mod's player-facing description. The other nine
      pass.
- [ ] `about_description_reads_for_a_player` (fixed) 📐 — the mod-list
      description tells a player what the mod does. 🔴 **Fails today for QUALITY,
      comprehensively.** It opens *"PLOT_MECHANISM_MODS_WAVE_1 — the
      aftermath-hostilities engine from design/Jawa/proposals/plot_mechanisms_wave.md
      Part 2, ruled in scope 2026-09-05"* and goes on, **all inside the
      `<description>` element itself**, to name `IncidentWorker_Raid.TryGenerateRaidInfo`,
      `Patch_BattleResolved.cs`, `RM_AftermathRuleDef`,
      `Find.Storyteller.incidentQueue.Add(def, fireTick, parms)`,
      `parms.forced = true`, *"doc §2.2"*, and `design/CHRONICLE_EVENT_SPINE.md`. It is
      an engineering note in the player's channel. ⚠️ **UNMEASURED on this machine**: that `<description>` is the text
      RimWorld shows in the Mods list. That is standard modding knowledge and no repo
      doc asserts it; it is settled in one glance at the Mods panel on the game
      machine and should be before this line is validated.

### cannot read

Absolute, per §10.2: one occurrence fails the mod, no N and no k needed.

- [ ] `never_engineering_marker_in_player_text` (absolute, shared) 📐 — cites
      `design/validation_walks/_read_line_registry.md`'s founding entry
      (`READ_LINE_REGISTRY_SHARED_1`); prose copied verbatim: a bracketed
      marker, a defName, a placeholder or a project codename in text the
      player reads — this draft additionally reads it as covering a repo
      path, an internal item id, a C# symbol or a `§` reference, all of
      which this mod's own evidence needs. 🔴 **Ships today** in `About.xml`
      (at least eight distinct instances inside `<description>`, named
      above), and one path is **latent in code**:
      `SendTelegraph`'s label chain is `def.telegraphLabel ?? def.label ?? def.defName`
      (`:335`), so a rule missing both fields puts `RM_AftermathRule_…` in the letter
      stack's title. No shipped rule triggers it; the line binds it so none ever does.
- [ ] `never_advertises_text_it_does_not_send` (absolute) 📐 — no
      player-read string promises the player words the engine never delivers. 🔴
      **Fails today**: `About.xml` says *"Ships a deterministic templated-letter
      baseline per rule — literal English, faction- and reason-named, no LLM
      required."* The letters are dead. This is the sharpest single line in the draft,
      because it fails **for absence of the advertised thing** while the offending
      string itself is present and reachable — the two failure modes in one line.

### deliberately NOT a line here

- **`{0}` or `{1}` visible on screen.** A regex on a captured letter settles it, so
  per §10.6 it is a lint rule, not a read line. Recommend it as a lint over
  `capture_text` output when the machinery lands.
- **Whether the telegraph precedes the payload.** That is a tick-order state
  assertion and belongs in `## must be true`, not on either axis.
- **Which letter CARD an omen arrives on.** `LetterDefOf.ThreatBig` is hardcoded
  (`:337`) with no def field selecting another, so rule 6's chartreuse flicker and
  rule 1's returning warband must arrive identically. That is presentation → the
  **show** axis, the same shape as Oracle's `god_letter_is_not_neutral_noise`. Out
  of this pass's scope; recommend one show line for it.

---

## 5. AftermathRites — candidate lines

Proposed placement: a new `## north star` section in
`design/validation_walks/RimUtinni/AftermathRites.md`, `read-state: DRAFT`.

### must read

**The telegraph — the 8 authored omens**

- [ ] `telegraph_is_an_observation_not_a_notification` (enumerated, **N=8**) 📐 —
      each telegraph reads as something a colonist *noticed* on Ash'karr, never as a
      rules notification about a queued event. **Passes today on all 8 by inspection**
      — *"A lone scout was seen at the edge of your land, studying your defenses
      before slipping away"* · *"Desert scavengers circle the field where the bodies
      still lie unburied"* · *"A chartreuse flicker runs through the ship's old
      lights, three quick pulses, gone before anyone else sees it."* Evidence is the
      def file; no game needed.
- [ ] `telegraph_gives_the_player_lead_time` (enumerated, **N=8**) 🤔 — each
      telegraph lets the player understand that *something is coming*, not only that
      something odd happened. ⚠️ **Marginal today on 2 of 8, and this is the line he
      is most likely to rewrite or reject.** Rule 6 (*"three quick pulses, gone before
      anyone else sees it"*) and rule 7 (*"the hull coughs once, deep in its bones, as
      if remembering it used to move"*) are the best-written strings in the file and
      neither says anything is coming. Per §2.2's own discipline (*"the player is
      being taught to read the sky"*) that may be exactly right — the omen is
      illegible on first contact and legible on the fifth. If he agrees, this line
      should be **cut**, not softened.
- [ ] `campaign_vocabulary_lives_here` (enumerated, **N=34** — the 32
      letter/telegraph strings plus 2 About strings) 🗣 — the campaign's words (Sh'kaar,
      Zizzik, Ta'Baa, the Junkers, the Hutt Cartel, Ash'karr) live in **this** RUT data
      pack and not in the RM engine. The mirror of `prose_is_tier_neutral`,
      same ruling (R6 + R9). **Passes today on all 34.** Kept as a pair because
      together they are the only enforcement R6's text half will ever have.

**The payload letter — the 8 authored letters, judgeable from disk and dead in play**

- [ ] `payload_letter_names_the_cause` (enumerated, **N=8**) 📐 — each payload
      letter names what the player did that brought this on. **Passes today on the
      WORDS** — rule 1: *"{0} did not forget what happened last time. This is the same
      enemy, returned to try you again."* rule 3: *"The Junkers were never going to let
      good salvage rot. They come for what {0} left behind."* 🔴 **And is
      UNJUDGEABLE in play, for ABSENCE**: none of the eight arrives. This is the
      cleanest illustration in the repo of §10.3's def-vs-channel split — the enumerated
      evidence passes from disk today and the channel evidence cannot be captured at
      all until `AFTERMATH_DEAD_LETTERS_1` is fixed.
- [ ] `god_is_named_as_a_presence_not_a_stat` (enumerated, **N=3** — the three
      letters that name a god) 📐 — where a god is named, the letter speaks of them as a
      presence in the world, never reporting a band, a delta or a number. **Passes
      today on the words**: *"Sh'kaar has noticed you"* (rule 5), *"Zizzik was already
      close when it happened"* (rule 6), *"Ta'Baa marks another quadrum you did not
      fly"* (rule 7); no `godDelta` value appears in any of the 32 strings. All three
      are dead letters, so the line is judgeable only from disk today.
      ⚠️ Deliberately NOT anchored on R-W6: that ruling governs a god *speaking* in
      his own voice, and these are narration *about* gods. Claiming R-W6 here would be
      laundering a law into a place he did not put it.

### cannot read

- [ ] `never_generic_raid_letter_for_an_authored_rule` (absolute) 📐 — an
      aftermath payload arriving with vanilla's stock raid letter while this mod ships
      a written one for that rule. 🔴 **This is the shipped behaviour, for ABSENCE.**
      Needs a channel capture; the cause is already measured offline.
- [ ] `never_names_a_mechanism` (absolute) 📐 — a defName, a trigger-kind name, a
      god enum name, a tick count, a delta or a points number in any of the 32
      strings. **Passes today on all 32 by inspection.** ⚠️ Per §10.6 the
      substring-shaped part of this (`RM_`, `BattleOutcome`, digits) belongs in a lint
      and should be written as one; the line's real content is the case a substring
      cannot reach — a sentence that describes the machinery in plain words
      (*"a follow-up raid has been queued against this faction"*). Written here so a
      later agent cannot weaken the lint, exactly as spec §10.6 licenses.

### deliberately NOT a read line here

- 🔴 **`every_shipped_rule_can_be_read` — the biggest fact about this mod, and it is
  not a read line.** "11 of 16 authored messages cannot reach the screen" is a
  reachability question: a state assertion answers it, and §10.5's `uncovered_reads`
  floor enforces it. Per §10.3 a walk needs **both** — a state assertion that the
  string reached the stack, and a read verdict on the string that did. Recommend it
  as a `## must be true` line on this walk plus the two open items, and keep the read
  lines judging the words. Writing it as a read line would be spending his attention
  on a bug already filed.
- **The 8 rule `<label>`s.** Not player-facing today (they surface only through the
  never-reached letter-title fallback). If `AFTERMATH_DEAD_LETTERS_1` is fixed with
  `{1} = this rule's label` (as `RM_AftermathRuleDef.cs:55` anticipates), they become
  player text and want a line then.

---

## 6. Which lines the code fails TODAY — absence vs quality

The distinction the brief asks for, stated per line. **7 of 14 fail.**

| line | fails? | absence or quality |
|---|---|---|
| `telegraph_fallback_reads_as_a_warning` | 🔴 FAILS | **quality** — the string exists, is reachable in code, and is a stub |
| `telegraph_substitution_is_right` | 🔴 FAILS | **quality** — a live, reachable letter renders the wrong faction's name (rule 2) |
| `payload_arrival_names_its_cause` | 🔴 FAILS | **absence** — no code reads the field |
| `settings_read_as_player_options` | passes (marginal) | — |
| `prose_is_tier_neutral` | 🔴 FAILS | **quality** — 1 of 10 strings names the campaign |
| `about_description_reads_for_a_player` | 🔴 FAILS | **quality** — a reachable string written for an agent |
| `never_engineering_marker_in_player_text` | 🔴 FAILS | **quality** (About.xml, shipping) + latent (defName label fallback) |
| `never_advertises_text_it_does_not_send` | 🔴 FAILS | **absence of the advertised thing**, via a present string |
| `telegraph_is_an_observation_not_a_notification` | passes | — |
| `telegraph_gives_the_player_lead_time` | marginal on 2 of 8 | **quality** — and probably the line is wrong, not the prose |
| `campaign_vocabulary_lives_here` | passes | — |
| `payload_letter_names_the_cause` | passes on words / unjudgeable in play | **absence** of the channel, not of the words |
| `god_is_named_as_a_presence_not_a_stat` | passes on words / unjudgeable in play | **absence** of the channel |
| `never_generic_raid_letter_for_an_authored_rule` | 🔴 FAILS | **absence** |

🔑 **Four quality failures and three absence failures, and they are not the same
bug.** `AFTERMATH_DEAD_LETTERS_1` closing would clear the three absence rows and
leave every quality row standing. That is the test of whether this checklist is
useful rather than a restatement of the filed bug: **fixing the bug fixes 3 of 7
lines.** The other four — a stub fallback, a wrong `{0}` substitution, an
agent-written mod description, and engineering markers in the player's channel — are
independent defects that no reachability fix touches, and three of the four were
found only by reading the strings as a player would.

🔴 **And the falsification signature to expect** (spec §11's shape, applied here): if
this checklist is validated and Aftermath comes back GREEN on its first run, the bar
was written to be passed. The known answer is that `never_advertises_text_it_does_not
_send` and `payload_arrival_names_its_cause` must both be RED.

---

## 7. Things I could not measure, and things the owner may disagree with

**UNMEASURED / UNMEASURABLE on this machine**

1. That `About.xml`'s `<description>` is the string RimWorld renders in the Mods
   list. Standard modding knowledge; asserted by no repo doc I could find; one glance
   at the Mods panel settles it. Two lines depend on it.
2. Any engine internal — RimSage has never connected here. I asserted none.
3. Whether a rendered rule-2 telegraph reads as badly as the two code paths say it
   must. Derived offline from `:336-337` and `:293-307`; not seen on screen.
4. What a captured payload-arrival letter looks like today. It cannot be captured;
   the field is read by nothing.
5. Whether `rimworld/list_letters` returns the telegraph body for THIS mod's letters.
   Oracle's walk records it returning semantic letter content and a marker string
   matched byte-for-byte, so it should; not re-verified for a `ThreatBig` letter.

**Flags — where I expect disagreement or a correction**

- ✅ **Id namespace collision — RESOLVED 2026-09-16, `READ_LINE_REGISTRY_SHARED_1`
  (owner ruling).** Spec §10.1 said *"one id namespace across both axes, and an id
  belongs to exactly one"* but did not say whether the namespace is per-mod or
  global; it is now **global**, with a shared registry
  (`design/validation_walks/_read_line_registry.md`) for recurring demands and every
  mod-specific line drawing its id from the same flat namespace. Every id below has
  been de-prefixed accordingly (no more `aftermath_`/`rites_`), and
  `never_engineering_marker_in_player_text` — this draft's Aftermath instance of it —
  now **cites** the registry's founding entry (tagged `(absolute, shared)` below)
  rather than defining its own copy, since Oracle's DRAFT already held the exact same
  demand under that exact id.
- ⚠️ **`telegraph_gives_the_player_lead_time` is the line I would bet he
  rejects.** It puts a legibility demand on the two best-written strings in the file.
  If he says the omen is *supposed* to be unreadable until you have seen it once, cut
  it outright rather than softening it — a softened version would be unfalsifiable.
- ⚠️ **`settings_read_as_player_options` may be beneath the axis.** It is
  the one line here that a careful proofread also catches, and §10.6 exists to keep
  such things out.
- ⚠️ **`prose_is_tier_neutral` / `campaign_vocabulary_lives_here` are
  a pair by design.** Validating one without the other leaves R6's text half
  half-enforced. If he wants only one, keep the RM-side one.
- ⚠️ **Both mods are slated to be RENAMED** (R5: Aftermath → RimChronicle;
  AftermathRites renamed grammar-compliant under NAMING_SCHEME_EXECUTION_1). Line ids
  here name mechanics, not mod names, so they survive the rename — but the walk
  filenames and `packageId`s in them will not.

**Two incidental doc defects measured this pass** (not mine to fix; flagged for BENCH)

- 🔴 `Aftermath.md` says twice that the rule defs ship in *"the not-yet-built
  `mandrake.rut.aftermath`"* (`status-hint` and walk step 5) and that step 5 should
  see zero `RM_AftermathRuleDef` loaded. **`src/RimUtinni/AftermathRites` exists and
  ships 8 of them.** The walk is stale, and step 5 would now be asserting a false
  expectation on the `minimal+mandrake.rm.aftermath` list if AftermathRites is active.
- 🔴 `AftermathRites.md`'s `## must be true` (line 13) and steps 5-6 name the faction
  defNames **without** the `RUT_` prefix — `Jawa_GeonosianFoundryHive`,
  `Jawa_FreeDroidEnclaves`, `Jawa_Junkers`, `Jawa_HuttCartel`, `Jawa_AscendantHelix`.
  The shipped XML carries `RUT_Jawa_…` on all five
  (`Defs/RM_AlliancePairDefs.xml`). Every def read-back in those steps would fail as
  written.
