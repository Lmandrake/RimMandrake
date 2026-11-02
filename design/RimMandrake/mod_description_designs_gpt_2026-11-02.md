# Mod description designs: GPT consult with web research (2026-11-02)

Owner, 2026-11-02: *"ask GPT what the elements of a Mod's description SHOULD be to well define it for a Relentless
builder. Give three competing designs with trade-offs. Have it look in actual mod repo's for docs and capabilities."*
Brief sent: `designer_brief_for_gpt_2026-11-02.md` (inlined). Transport: `src/RimMandrake/Utils/gpt_consult.py`,
default model, high effort, web search on. Raw answer, prompt and fetched sources:
`D:\ClaudeWork\rimmandrake\designer_gpt_2026-11-02\` (`gpt_answer.md`, `ask.md`, `cites\`). GPT is guidance, not
authority: nothing below is decided until the Conductor or the owner rules.

## Conductor-ready summary

GPT read six real mods (Vanilla Furniture Expanded Power, Vanilla Expanded Framework, Dubs Bad Hygiene, Mlie's Cleaning
Priority, Performance Fish, Fluffy's Work Tab) plus the wiki and Steamworks, and found what public mod docs carry
(features, dependencies, load order, named incompatibilities, save add/remove notes) and what they almost never carry
(acceptance criteria with observers, false passes, non-goals, a reproducible test environment, settings timing). It then
offers three formats. **A, player promise first**: a short numbered description is authoritative and the tree expands
it; cheapest for the owner to read, but polished prose hides several obligations per sentence and the prose and tree
drift. **B, acceptance contract first**: the typed tree is authoritative and the sheet is a generated digest; least
ambiguity and best traceability, but the owner reviews in the agents' language and proxies can replace intent. **C,
scenes and transitions first**: four to six scene cards (starting state, action, what the player perceives, reject
example, acceptable variation) plus invariants that hold beyond the scenes, with the tree as their binding projection;
matches how the owner judges (short moments of play, his "key-moment stories") and attacks the Pit directly, at the cost
of maintained fixtures and the risk that showcase scenes hide general defects, which the invariant layer is there to
catch. **GPT picks C**, and names two first changes: replace the flat does-list in `sheet.md` with scene cards plus a
decision panel (keeping the eight elements as the Designer's checklist behind them), and make `tree.json` require a
traceable observation contract per leaf (source scene or invariant, disposition, observation scope, fixture and floor
revision, defined semantics kept apart from Setter-owned instruments).

## Verification notes (BENCH helper, 2026-11-02)

**Citations: 18 of 18 URLs resolve to the named subject.** 13 fetched directly (HTTP 200). The five Workshop pages
were rate-limited (HTTP 429) to curl, so they were resolved through the Steam Web API
(`ISteamRemoteStorage/GetPublishedFileDetails`): each returned result 1, app 294100, and the expected title.

**Claims spot-checked against the fetched text: 13 checked, 13 confirmed.**
1. Cleaning Priority README: "soft incompatibility with Dubs Bad Hygiene: pawns clean outside of the designated zone.
   Turning off "prefer indoor cleaning" in DBH options solves the problem." Confirmed.
2. Cleaning Priority Workshop: new filth is not cleaned until "600 ticks after the filth has last thickened". Confirmed.
3. VFE Power Workshop contradicts itself: "move the mod further up the mod queue" and, in its FAQ, "Move the mod further
   down the mod load order" for the same symptom. Confirmed.
4. VEF `About.xml` names one incompatibility (`<incompatibleWith><li>hatena.RangeAnimalFramework</li>`). Confirmed.
5. VEF Workshop FAQ: "it is compatible with every other mod". Confirmed.
6. Performance Fish README lists compatible and incompatible mods and gives no benchmark, fps or ms figure (0 hits).
   Confirmed.
7. Dubs Bad Hygiene README: "Works with existing saves! Cannot be removed from saves easily". Confirmed.
8. DBH Workshop: Lite mode "needs a restart to remove the defs". Confirmed.
9. Work Tab 1.3 README: "there will never be an 'autolabour' mode" and the deadlock warning. Confirmed.
10. Wiki About.xml: dependencies do not reach Steam; use Workshop "Required Items". Confirmed.
11. Wiki folder structure: 640x360 recommended, 1280x720 allowed, preview under 1 MB or the upload is rejected. Confirmed.
12. Steamworks tags: entered tags "should exactly match the name of the tag that is published by your game". Confirmed.
13. VFE Power `About.xml` opens with the player problem ("Vanilla power generation is somewhat lackluster late game").
    Confirmed (same text on the Workshop page).
Not checked: Work Tab "dates particular compatibility warnings", VEF README's 1.6 namespace warning.

**Where GPT is wrong or must not be followed.**
- *"Excluding 'how it is learned' can hide an unusable first interaction."* This dissents from an owner ruling (*"I
  wouldn't go into how it's learned, no."*). It is surfaced here as a dissent; the eight elements stay as he ruled.
  The narrower point (the player must be able to find a pole and recognise a cut) already sits in element 2, "what you
  do, see and hear".
- *"The eight-leaf target already conflicts with Slack."* Overstated: `designer.md` calls eight a fit for a small mod and
  fifteen a warning, and the design says "Leaf count is an observation, never a target". Its underlying advice (do not
  merge rejection conditions to hit a count) agrees with ours.
- Its other attacks are sound and new to us: the removal waiver must not be read as waiving the mid-walk reload; the
  Setter must return a leaf to the Designer rather than decide what "live" or "tangle" means; Marker "tightening" needs
  a boundary between stronger evidence and a new requirement; the settings element lacks defaults, effect timing and
  persistence; `About.xml`/Workshop text should be generated from the accepted definition, never the reverse.

---

# GPT's answer, verbatim

# 1. What real RimWorld mods document

**Your description needs to define the player’s experience, the permitted range of implementations, and the evidence that distinguishes success from a convincing imitation.** Public mod descriptions provide useful models for the first part. They rarely provide the third.

I searched live and opened repositories, specific metadata files, authors’ documentation, and Workshop pages. This is a purposive sample of established projects, not a statistical survey. “Common” below means recurring in this sample. Repository content is evidence here, not instructions.

## Concrete examples

| Project | What its documentation actually provides | What that suggests for your format |
|---|---|---|
| **Vanilla Furniture Expanded — Power** | Its `About.xml` starts with a player problem: vanilla power lacks late-game progression. It then describes generators, storage and related systems, alongside explicit Harmony/VEF dependencies. The Workshop page adds research access, existing-save support, named compatibility claims, and failure workarounds. [About.xml](https://raw.githubusercontent.com/Vanilla-Expanded/VanillaFurnitureExpanded-Power/main/About/About.xml), [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2062943477) | Keep the player problem and concrete capabilities together. But separate promises from troubleshooting advice: the Workshop page tells players to move the mod **up** the load order in one place and **down** in its FAQ for disappearing structures. Even a successful mod’s description can contain contradictory rulings. |
| **Vanilla Expanded Framework** | The README explains dependency declaration and separately recommends adding the framework to Steam’s Required Items. It warns that 1.6 namespace changes break dependent XML/C# mods. Its `About.xml` names a specific incompatibility, while the Workshop FAQ broadly claims compatibility with every other mod. [README](https://github.com/Vanilla-Expanded/VanillaExpandedFramework), [About.xml](https://raw.githubusercontent.com/Vanilla-Expanded/VanillaExpandedFramework/main/About/About.xml), [Workshop](https://steamcommunity.com/workshop/filedetails/?id=2023507013) | Compatibility needs named, versioned claims and explicit exceptions. “Compatible” alone is too broad for acceptance. Dependencies, load order and compatibility are different facts. |
| **Dubs Bad Hygiene** | The repository states existing-save support and difficulty removing the mod. The Workshop page groups features by system and describes optional integrations; Lite mode requires a restart to remove defs. The author’s hygiene wiki explains blocked drains, the inspect-tab sign, contamination alerts and corrective actions. [Repository](https://github.com/Dubwise56/Dubs-Bad-Hygiene), [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=836308268), [Hygiene wiki](https://github.com/Dubwise56/Dubs-Bad-Hygiene/wiki/Hygiene) | Document settings as changes of behaviour, including **when they take effect**. Model a failure as cause → player-visible sign → recovery. This is much more useful than “handles errors gracefully.” |
| **Mlie’s Cleaning Priority (Continued)** | README and Workshop describe a concrete conflict: with Dubs Bad Hygiene, pawns can clean outside the designated zone; disabling DBH’s “prefer indoor cleaning” resolves it. The Workshop page also explains default behaviour and a 600-tick delay before newly thickened filth is cleaned. [Repository](https://github.com/emipa606/CleaningPriority), [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2018316486) | A compatibility record should include the symptom, relevant configuration and workaround. Apparent failure can also be an intentional delay; the description must distinguish them. |
| **Performance Fish** | The README promises improved frame/tick performance while preserving functionality, explains immediate per-patch disabling and save-removal behaviour, and lists compatible/incompatible mods. `About.xml` encodes dependencies, order and incompatibilities with comments explaining several reasons. The README supplies no fixed benchmark workload, machine or numerical performance guarantee. [README](https://raw.githubusercontent.com/bbradson/Performance-Fish/main/README.md), [About.xml](https://raw.githubusercontent.com/bbradson/Performance-Fish/main/About/About.xml) | “Improves performance” is a public-facing claim, not a measurable acceptance condition. Your workload, measurement method and reference environment must be additional contract material. |
| **Fluffy’s Work Tab** | Its historical 1.3 README explains exact gestures, configurable priority levels, interactions with other mods, deadlock risks, and an explicit refusal to provide automatic labour assignment. It dates particular compatibility warnings. The Workshop page also explains the interception of vanilla priority behaviour. [1.3 README](https://raw.githubusercontent.com/fluffy-mods/WorkTab/1.3/Readme.md), [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=725219116) | Explicit non-goals are valuable and do exist. Date and version them: this is a historical documentation example, not evidence that those old compatibility warnings still apply. |

The strongest examples describe **a consequence the player can recognise**: cleaning outside a zone, a blocked drain, priorities resetting, a structure disappearing. Those make good starting points for acceptance checks.

## What is common, rare, and almost absent

**Common in this sample:**

- Feature lists and the player-facing purpose.
- Installation requirements, versions, dependencies or load-order advice.
- Named compatibility claims and known issues.
- Settings mentioned as ways to tune or disable behaviour.
- Some statement about adding to or removing from saves.

**Less consistent:**

- Exact setting defaults, ranges, persistence and application timing.
- A compatibility claim bounded by game version, mod version and configuration.
- Failure signs explained alongside their causes and recovery.
- Explicit non-goals.
- Performance claims accompanied by reproducible measurements.
- Agreement between README, metadata and Workshop text.

**Almost never documented in the public material examined:**

- Acceptance/rejection criteria with named observers and evidence.
- Known false passes: implementations that satisfy an assertion while betraying the experience.
- A complete release-specific acceptance environment.
- Proof that a check detects a deliberately introduced defect.
- Authority for unresolved choices, waivers and scope changes.

Failure signs and non-goals are **uncommon, not absent**; Dubs, Mlie and Fluffy provide counterexamples. Independent acceptance contracts are the conspicuous missing layer. That finding concerns the documentation inspected, not private development practices.

## What Steamworks and the RimWorld wiki require or recommend

These sources describe packaging and publication, not how to define a satisfactory mod.

- **`About.xml`:** the RimWorld wiki identifies required metadata including package ID, name, author, description and supported versions. It recommends listing versions actually tested. The description seeds the initial Workshop description, but Workshop text can subsequently change independently; the wiki recommends keeping the metadata description relatively short. Dependencies in XML do **not** automatically populate Steam Required Items. [About.xml guide](https://rimworldwiki.com/wiki/Modding_Tutorials/About.xml)
- **Preview:** the folder guide lists `About/Preview.png` as required, recommends 640×360, allows higher-resolution artwork, and specifies keeping it below 1 MB for Workshop upload. [Folder structure guide](https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_Folder_Structure)
- **Workshop fields:** Steamworks exposes title, description, visibility, tags, content and preview as separate update fields. These are publication mechanisms, not an acceptance rubric. [Implementation guide](https://partner.steamgames.com/doc/features/workshop/implementation)
- **Tags:** Steamworks explains that tags are submitted by the game/upload tool and must exactly match configured names to function as filters. Your release record should therefore identify applicable tags rather than treating them as free-form prose. [Workshop tags](https://partner.steamgames.com/doc/features/workshop/tags)

**Implication:** generate the short `About.xml` description and longer Workshop description from the accepted definition. Neither should be the only place where the definition lives.

# 2. Attack on your current eight elements

Your eight elements are a strong **interview agenda**. They are not yet a sufficient builder handoff schema.

| Current element | Keep or change | Builder-specific weakness |
|---|---|---|
| **Why reach for it** | Keep, concise. | Motivation does not settle behaviour. “Too-long extension cords” still permits several incompatible visual interpretations. |
| **Using it** | Keep; include recognition and discovery when necessary. | Excluding “how it is learned” can hide an unusable first interaction. The builder needs to know how the player finds a pole, recognises a cut, or discovers a setting. |
| **The result** | Keep as the north star; avoid repeating feature claims. | “Enjoyment” cannot become a second, unspecified rejection contract after all leaves pass. |
| **The costs** | Split player costs from engineering constraints. | Materials/research and frame stalls need different observers and evidence. “40 colonists” alone does not define a cable-rendering workload. |
| **When it goes wrong** | Expand. | Distinguish intended in-world failure, player misuse, incompatibility and software defect. Each has different acceptance consequences. |
| **Edges** | Keep, but type the records. | A non-goal, a must-not, a waiver and deferred work are not interchangeable. |
| **Neighbours** | Replace the catch-all with explicit interfaces and environment assumptions. | FlowWorks ownership, all-DLC assumptions, electrical connectivity and a particular Harmony conflict are different relationships. |
| **Settings** | Keep as a behaviour contract. | A list of sliders omits defaults, scope, persistence, effect timing, combinations and all-off behaviour. |

## What is missing

### A bounded environment

Acceptance needs an exact game build, DLC set, dependency versions, load order, settings profile, floor revision and test fixture.

“All DLC present” is useful. It does not identify a reproducible load. A version tag in metadata is also not evidence of compatibility.

### State and transition semantics

For Slack, “live and dead cut ends look different” leaves several questions:

- What makes an endpoint live?
- What drawing changes when one cable is cut?
- What remains after repair, reload, toggling or landing?
- Does the appearance depend on the order in which the player built the network?

These are part of the mod’s behaviour, even when its main purpose is visual.

### A visual observation contract

“Broad loops,” “pile against walls” and “one tangle” need reference cases, viewing conditions and rejection examples.

A screenshot at one zoom can conceal a wall crossing. A still image cannot establish sparking behaviour or absence of a stall. The evidence format must fit the promise.

### Traceability and decision authority

Every binding claim needs an ID, disposition and provenance. An implementation choice delegated to an agent needs a recorded outcome and limits.

Owner quotations should remain verbatim. Designer interpretations should be visibly separate.

### Delivery and change rules

Define what constitutes the accepted artifact: runnable mod, review save, settings behaviour, metadata, preview, installation instructions and evidence.

Also define when acceptance expires: a new game build, dependency change, changed fixture or changed rendering system can invalidate particular evidence.

## Problems in the current acceptance machinery

**The eight-leaf target already conflicts with Slack.** The draft names nine positive leaves including the walk, before negative requirements and floors. Do not hide independent rejection conditions inside giant leaves to preserve a count. Budget owner decisions and review time; allow the evidence structure to reflect the real obligations.

**The removal waiver is narrower than “save support.”** “I don't much care about savegame continuity” is explicitly identified in the brief as concerning mod removal. It does not waive the required mid-walk reload.

**The false-drawing question is foundational.** If a cut can remain visibly connected, green electrical assertions can coexist with a false screen. Whether that rejects the mod belongs in the definition before lock.

**The Setter must not complete the design secretly.** If the Setter cannot construct an oracle without deciding what “live” or “tangle” means, the item returns to Designer. Hold-outs may vary the case; they must not introduce new expectations.

**“Tightening is open to the Marker” needs a boundary.** Strengthening evidence against an existing promise is reasonable. Narrowing the permitted behaviour adds a requirement and needs a contract revision.

**The Cold Reader exam measures shared interpretation, not correctness.** Ten scenarios can reveal ambiguity. They cannot establish coverage, feasibility or enjoyment. In addition to the pass score, retain the disagreement reasons and identify which text must change.

# 3. What all three competing formats need

The formats below differ in **what is authoritative and how the owner defines the mod**. All need a small common envelope:

| Record | Contents |
|---|---|
| **Release envelope** | Identity, exact supported environment, dependency/order assumptions, applicable floor revision, artifact being accepted. |
| **Decision ledger** | Binding promises and prohibitions; advisory, delegated, waived, open and later records; sources and scope. |
| **Settings contract** | Major-feature switches, defaults, tuning, persistence, application timing and all-off result. |
| **Evidence bindings** | Promise → scenario → observer/oracle → false pass → evidence → owner involvement. |
| **Change record** | What changed, affected promises, evidence invalidated and any owner decision required. |

Do not ask the owner to supply technical fields that agents can discover. Ask him only where different answers change the experience.

For the worked examples:

- **Given** means supplied in the brief.
- **Proposal** means my suggested interpretation, fixture or format—not an owner quotation or an approved decision.
- All examples remain **drafts**. Slack has no tree yet and has unresolved core decisions.
- All retain the given advisory features, removal waiver and open landing question. They do not authorise deleting built capabilities.

# 4. Design A — Player promise first

**Authoritative object:** a short, numbered player-facing description. The tree is its reviewed, mechanically traceable expansion.

This design asks: **“What exactly are we promising someone who installs this?”**

## Elements

| Section | What it holds |
|---|---|
| **The reason to install** | Player desire and north-star quotation. |
| **What you get** | Numbered, concrete promises describing actions and observations. |
| **What changes when…** | Cuts, repairs, reloads, disabling, scale and other important transitions. |
| **Costs and controls** | Gameplay costs, major settings, defaults and consequences. |
| **Boundaries and neighbours** | Explicit prohibitions, exclusions and interface rulings. |
| **Release conditions** | Supported environment and deliverables. |
| **Decision appendix** | Advisory, waiver, delegated, open and later records. |
| **Promise index** | Each numbered promise’s tree IDs and observation references. |

## Worked example: Gimme Some Slack

> **North star — given owner words:** “Everything is a too-long extension cord.”

**Proposed presentation of the given promises:**

| ID | Description text |
|---|---|
| P1 | In the supported cable views, cords replace the vanilla conduit pipe drawing. |
| P2 | Floor cords form broad slack loops and collect against walls. They end at the wall face and do not draw through walls or rock. |
| P3 | Dense cable layouts read as a combined tangle containing power strips. |
| P4 | Cut endpoints have distinguishable live and dead appearances; the live appearance includes sparking. |
| P5 | Overhead spans draw above pawns. A downed span lies on the ground. |
| P6 | Building or cutting one wire in the agreed large-base fixture causes no visible stall. |
| P7 | The whole experience works through a mid-walk reload, repeated cut/repair, a second grid and a changed action order. |

**Controls — given:** master off restores vanilla; the standing policy requires switches for major features and tuning where numbers determine the experience.

**Controls — proposal:** an accompanying settings table identifies the major features and specifies whether each switch takes effect immediately or after reload/restart. Those details are presently missing.

**Boundaries — given:** no hose drawing, no taut cords, no drawing across walls/rock, no multiplayer and no worldgen.

**Advisory — given:** four styles, one look per connected run, theft/goodwill effects, wire-down alert and re-stringing. These are not silently promoted to acceptance requirements.

**Open — given:** false drawings and landing appearance.

**Additional interpretation to settle — proposal:** specify the supported conduit types and views. “No vanilla pipe visible” must not silently acquire or exclude hidden conduits, construction previews or overlays.

Notice that this wording exposes unresolved scope instead of making a publishable claim that the builder must guess how to implement.

## How Relentless consumes it

Before lock, an agent expands P1–P7 into tree obligations. Designer reviews that expansion against the prose. Each tree obligation cites a promise ID; any prose without a disposition is a lint error.

Relentless builds against the locked expansion, using the description for intent. It may not treat promotional adjectives as additional hidden requirements.

The main danger is the **translation step**: a pleasant sentence can conceal three separate obligations.

## How acceptance is derived

Designer defines the promise and observation boundary. Setter writes the instruments and hold-outs.

For P2, a **proposed** check would stage straight walls, corners and rock boundaries:

- **Observer:** owner reviews fixed-camera views; an independent geometry/state read supports them.
- **Oracle:** slack cords end at the visible wall face without crossing the barrier.
- **False pass:** an endpoint coordinate is correct, but its thick rendered stroke clips through the wall.
- **Red evidence:** deliberately render a crossing cord and establish that the review catches it.
- **Marker:** checks the evidence against P2; the owner judges the visual interpretation.

A screenshot alone cannot establish P6. That promise needs a recording and event-aligned frame-time evidence on the agreed fixture.

## Trade-offs

- **Owner burden:** lowest initial reading burden; familiar language.
- **Ambiguity:** highest risk of broad words carrying unexamined meaning.
- **Testability:** good only after careful expansion into the tree.
- **Drift:** prose and tree can diverge; one-way generation and promise IDs are essential.
- **Cold Reader cost:** cheap to read, relatively expensive to repair. Readers can agree on prose while imagining different screens.

**Choose this when:** the mod has a simple player proposition and publication clarity is the dominant concern.

# 5. Design B — Acceptance contract first

**Authoritative object:** the typed acceptance tree. `sheet.md` is a generated owner-readable digest.

This design asks: **“What facts must be established before we can say done?”**

## Elements

| Field or section | What it holds |
|---|---|
| **Root intent** | Owner’s north star and interpretation references. |
| **Environment** | Exact acceptance load, fixture, settings and floor revision. |
| **Obligations** | Stable IDs, positive/negative type, source and disposition. |
| **Observation contract** | What is observed, where, under what conditions, with what permitted variation. |
| **Scenario domain** | Valid setups/actions and relevant state combinations. |
| **Evidence binding** | Your eight leaf fields, with explicit ownership of who completes them. |
| **Composition rules** | Which obligations must all pass; handling of absent evidence. |
| **Change dependencies** | Changes that invalidate an obligation’s evidence. |

Here, “a small mod fits eight leaves” becomes an editorial preference, not a schema restriction.

## Worked example: Gimme Some Slack

**Proposed tree structure, preserving the supplied scope:**

| Obligation | Required outcome |
|---|---|
| G1 | Vanilla conduit pipe drawing is replaced in the agreed scope. |
| G2 | Floor cords have the agreed slack-loop appearance. |
| G3 | Wall/rock boundaries are respected and wall-face termination is correct. |
| G4 | Dense layouts produce the agreed tangle and power-strip appearance. |
| G5 | Live/dead cut-end appearance is distinguishable, including live sparking. |
| G6 | Standing overhead spans draw above pawns. |
| G7 | Downed spans draw on the ground. |
| G8 | Single-wire changes meet the visible-stall promise on the agreed fixture. |
| GW | Whole-mod walk passes through reload, repetition, second grid and alternate action order. |
| F-settings | Applicable standing settings floor, including master-off vanilla restoration. |
| N-boundaries | No hose rendering, taut cords, barrier crossings, multiplayer or worldgen. |

The negative obligations would be separate typed records or inherited clauses, not one vague “boundaries pass” checkbox.

An illustrative leaf:

```yaml
id: G5
status: draft
source: "Brief: live/dead cut ends; owner terminal-node quotation"

experience:
  "Live and dead cut endpoints are visually distinguishable;
   a live cut endpoint sparks."

scenario:
  "Cut the staged cable with its source active.
   Repeat with the source inactive."

oracle:
  designer:
    "Visible distinction, not merely an internal flag."
  setter:
    "Bind independent endpoint-state observation to timed visual capture.
     Exact electrical meaning of live must be resolved before lock."

false_pass:
  "Both endpoints use the same drawing, while live/dead state reads correctly."

red:
  "Show failure on the applicable baseline and with the same-rendering
   defect deliberately introduced."

tier:
  "Live visual observation: offline state cannot settle sparking."

budget:
  "Program assigns execution cost before intake acceptance."

owner_part:
  "Approve the distinction and sparking appearance on the first GREEN."
```

This is a **proposed record**, not a completed leaf. Missing semantics cannot be disguised as “Setter will decide.”

**Proposed new obligation, pending the given open decision:** drawing must faithfully represent the current connection state. If the owner rejects that proposal, record the narrower permission explicitly.

## How Relentless consumes it

Relentless gets a closed list of obligations and their permitted implementation freedom. It maps implementation tasks to obligation IDs and plans evidence collection alongside implementation.

Intake refuses unresolved binding fields. An advisory numeric floor remains advisory; the builder cannot invent a convenient threshold and claim it was approved.

The tree also carries the verified inventory references. An existing feature starts with its evidence status, not an assumption that “built” means “accepted.”

## How acceptance is derived

Designer owns criteria. Setter owns instruments and secret variations. Marker judges trusted observations of the candidate artifact. Builder-authored explanations are not proof.

For G5, Setter can vary the topology and source state without changing the criterion. A charged isolated battery, for example, is a legitimate hold-out only after the contract establishes how it affects “live.”

**False-pass defence:** identify the wrong world first, then select evidence that distinguishes it. A state flag and a screenshot from unrelated runs do not establish correspondence.

The walk is a composition check over G1–G8 and floors. It does not create an unlimited extra taste criterion.

## Trade-offs

- **Owner burden:** highest semantic review burden, even with a digest.
- **Ambiguity:** lowest once complete; incompleteness becomes visible as missing fields.
- **Testability:** strongest direct traceability.
- **Drift:** precise impact analysis, but instrumentation and fixtures require maintenance.
- **Cold Reader cost:** higher reading effort; lower ambiguity in cases the contract explicitly models. There is a risk that owner and agents spend time translating schemas instead of discussing play.

**Choose this when:** the main uncertainty is technical correctness, the owner’s desired appearance is already stable, or the mod has many interacting rules.

# 6. Design C — Scenes and transitions first

**Authoritative object:** a small set of owner-readable scenes, plus invariants that apply beyond those scenes. The tree is the acceptance projection of that material.

This design asks: **“At the moments that matter, what happens, what does the player perceive, and what would make him reject it?”**

This is more than writing stories. Each scene has a reproducible starting state, action, observable result and links to general rules.

## Elements

| Section | What it holds |
|---|---|
| **North star** | Owner words and the experience they anchor. |
| **Scene cards** | First use, ordinary use, failure/recovery, scale/payoff. |
| **Starting state** | Fixture, settings, relevant geometry and system state. |
| **Action and transition** | What the player does and how the situation changes. |
| **What the player perceives** | Screen, sound, feedback and timing. |
| **Reject this / acceptable variation** | Concrete bad outcomes and allowed differences. |
| **Invariants** | Rules that hold across layouts, scenes and action orders. |
| **Decision ledger** | Open, waived, advisory, delegated and later records. |
| **Coverage map** | Scenes/invariants → acceptance leaves and evidence. |

## Worked example: Gimme Some Slack

The scene staging below is **proposed**. The required outcomes come from the supplied draft unless identified otherwise.

| Scene | Starting state and action | Required experience | Reject examples or unresolved boundary |
|---|---|---|---|
| **S1: First floor run** | Build an L-shaped floor route beside a wall, terminating at its face. | Cords replace conduit pipe, form broad loops and collect against the wall. | Straight taut line; cord through rock; endpoint visibly inside the wall. Exact viewing references remain to be approved. |
| **S2: A lived-in base** | View several adjacent runs in a dense working area. | The area reads as a combined tangle containing power strips. | Separate neat parallel lines with no tangle. **Proposal:** review both ordinary play zoom and a close view so detail cannot substitute for overall appearance. |
| **S3: Something breaks** | Cut a live route; repeat on a dead route; repair. | Terminal treatment follows the supplied description; live and dead ends differ, with live sparking. | Identical live/dead appearance. Whether any apparently continuous cable across the cut rejects remains **open**. |
| **S4: Overhead route falls** | Observe a standing span with a pawn beneath it, then a downed span. | Standing span is above the pawn; downed span lies on the ground. | Ground-level standing span or floating downed span. Exact downing/re-stringing mechanics must be taken from inventory or resolved; advisory re-stringing is not automatically mandatory. |
| **S5: Change a large base** | Build and cut one wire on an agreed dense-base fixture with 40 colonists. | No visible stall. | Perceptible hitch attributable to the action. **Proposal:** capture frame times around the event; fixture cable count, camera and machine must be recorded. |
| **S6: Return and repeat** | Reload midway, repeat cut/repair, build a second grid and perform the main actions in another order. | All applicable promises remain true on the same candidate build. | Passing only before reload or only in one construction order. Whether the exact cable look persists after landing remains **open**. |

**Invariants — given:**

- No taut cords.
- No drawing across walls or rock.
- No hose rendering.
- Master off restores vanilla; standing feature-toggle policy applies.
- No worldgen or multiplayer support.

**Proposed additional invariant, requiring resolution of the existing open question:**

> Visible connections and endpoints correspond to the represented electrical layout; the renderer must not invent a connection.

That sentence is more general than S3. It prevents the builder from correcting the showcase cut while leaving phantom connections elsewhere.

**Decision panel — given:**

- Four styles, connected-run style consistency, theft/goodwill, alert and re-stringing remain advisory.
- Mod-removal continuity remains waived within its recorded scope.
- False drawings and gravship landing remain unresolved.

**Proposed settings panel:** for each major feature, record default, disabled appearance, application timing and reload persistence. The scene set includes default play and relevant disabled states; it need not exhaust every slider combination.

## How Relentless consumes it

Relentless receives a coverage map:

- S1 supports cord appearance and barrier obligations.
- S2 supports density/tangle.
- S3 supports cut-end states.
- S4 supports overhead/downed rendering.
- S5 supports the performance experience.
- S6 supplies the required walk.
- Invariants apply across all relevant scenes and unseen layouts.

The builder may choose internal representations and rendering algorithms. It cannot redefine the perceived outcome.

Fixtures are agent work. Designer must confirm fixture feasibility before lock, so the contract does not depend on an imaginary bridge capability or a missing save.

## How acceptance is derived

Designer writes scene outcomes and invariants with the owner. Setter constructs runnable fixtures, instruments and hold-outs.

For S3:

- **State observer:** independently records the actual topology and endpoint energisation under the agreed rule.
- **Visual observer:** reviews timed captures of those same endpoints on the same build/run.
- **Oracle:** the observed appearance matches the approved state distinction.
- **False pass:** a pre-recorded spark animation plays at a fixed location regardless of which cable was cut.
- **Guard:** move the cut and change source state; confirm the defect is detected.
- **Owner part:** approve whether the appearance communicates the intended broken, live/dead cord.

Setter varies layouts, positions and action order within the defined domain. Secret checks cannot require a new artistic style, unpromised persistence or an advisory alert.

**The key defence against overfitting is the invariant layer.** Scenes make meaning inspectable; invariants make it general.

## Trade-offs

- **Owner burden:** moderate drafting effort, lowest likely burden for meaningful review.
- **Ambiguity:** lower for appearance and sequences; generalisation must be explicit.
- **Testability:** excellent for integration and visual correspondence; isolated algorithmic properties need supporting checks.
- **Drift:** scenes remain understandable, but saves, camera setups and captures must be maintained.
- **Cold Reader cost:** more fixture preparation; likely less owner interpretation effort because he already judges short moments of play. That is a prediction to measure, not an established result.

**Choose this when:** the largest risk is a technically plausible implementation that looks or behaves unlike the owner’s picture.

# 7. Direct comparison

| Dimension | A: Player promise first | B: Acceptance contract first | C: Scenes and transitions first |
|---|---|---|---|
| Authoritative material | Numbered description | Typed tree | Scenes plus invariants |
| Owner’s main work | Approve wording | Approve conditions | Judge pictured situations |
| Main strength | Clear product proposition | Explicit, auditable obligations | Connects state to perceived play |
| Characteristic failure | Polished but ambiguous prose | Passing proxies replace intent | Showcase scenes conceal general defects |
| Necessary defence | Reviewed prose-to-tree expansion | Visual evidence and semantic review | Invariants and varied hold-outs |
| Maintenance hotspot | Duplicate prose/tree claims | Schema and instruments | Fixtures and captures |
| Cold Reader hotspot | Interpretive disagreement | Reading/translation effort | Scenario preparation and boundary cases |

For every design, freeze the exam scenarios before either side answers. Have Cold Readers explain their predicted verdicts and cite the controlling passage. Otherwise 9/10 can conceal lucky agreement.

An off-script Challenger case should test a consequence of a stated promise or expose a missing decision. It should not become a retrospective requirement.

# 8. My choice and the first two changes

I would choose **Design C: scenes and transitions first**, with `tree.json` as its binding acceptance projection.

Your owner thinks in short moments of play, and your feared failure is a mismatch between valid state and the screen. Scene cards expose that mismatch directly. A contract-first format is stronger for formal bookkeeping, but it asks your scarcest participant to review the mod in the agents’ language.

The choice is consequential: **Designer should organise the debate around scenes and invariants; the tree should preserve those decisions, not become a second place where agents invent meaning.**

I would make these two changes first.

## Change 1 — Replace the flat promise list in `sheet.md` with scene cards and an explicit decision panel

For Slack, begin with:

1. First floor run and wall endpoint.
2. Dense tangle.
3. Live/dead cut and repair.
4. Standing/downed overhead span.
5. Large-base edit.
6. Reload, repeat and alternate order.

Each card gets **starting state, action, perceived result, reject example, acceptable variation and linked IDs**. Use the eight current elements as the Designer’s completeness checklist behind these cards.

Keep owner words and dispositions visible. Put false drawings and landing behaviour in the blocking/open panel. Do not turn either into an assumed answer. Preserve the existing inventory and its evidence levels.

This immediately makes “show me the dumb version that passes” concrete.

## Change 2 — Make `tree.json` require traceable observation contracts before lock

Add these alongside the existing eight leaf fields:

- Stable obligation ID and source scene/invariant.
- Source and disposition: quotation, interpretation, proposal, delegation or inherited floor.
- Observation scope: relevant objects, states, views, timing and permitted variation.
- Environment/fixture references and floor revision.
- Explicit distinction between **defined semantics** and **Setter-owned instrumentation**.

For Slack, make the first completed binding a cut-end contract connecting actual electrical state to the observed drawing. Retain its unresolved status until the false-drawing ruling and “live” semantics are settled.

Require the evidence packet to identify the exact candidate build, environment and run. Missing or invalid observation is **unproven**, never green.

These two changes preserve your independent Setter/Marker arrangement while addressing its most serious upstream risk: an exam whose checks are precise but whose meaning was never agreed.

# Sources

All links below were opened during the research.

1. [Vanilla Furniture Expanded — Power: About.xml](https://raw.githubusercontent.com/Vanilla-Expanded/VanillaFurnitureExpanded-Power/main/About/About.xml)
2. [Vanilla Furniture Expanded — Power: Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2062943477)
3. [Vanilla Expanded Framework: repository README](https://github.com/Vanilla-Expanded/VanillaExpandedFramework)
4. [Vanilla Expanded Framework: About.xml](https://raw.githubusercontent.com/Vanilla-Expanded/VanillaExpandedFramework/main/About/About.xml)
5. [Vanilla Expanded Framework: Steam Workshop](https://steamcommunity.com/workshop/filedetails/?id=2023507013)
6. [Dubs Bad Hygiene: repository README](https://github.com/Dubwise56/Dubs-Bad-Hygiene)
7. [Dubs Bad Hygiene: Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=836308268)
8. [Dubs Bad Hygiene: author’s Hygiene wiki](https://github.com/Dubwise56/Dubs-Bad-Hygiene/wiki/Hygiene)
9. [Cleaning Priority (Continued): repository README](https://github.com/emipa606/CleaningPriority)
10. [Cleaning Priority (Continued): Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2018316486)
11. [Performance Fish: README](https://raw.githubusercontent.com/bbradson/Performance-Fish/main/README.md)
12. [Performance Fish: About.xml](https://raw.githubusercontent.com/bbradson/Performance-Fish/main/About/About.xml)
13. [Work Tab: historical 1.3 README](https://raw.githubusercontent.com/fluffy-mods/WorkTab/1.3/Readme.md)
14. [Work Tab: Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=725219116)
15. [RimWorld wiki: About.xml](https://rimworldwiki.com/wiki/Modding_Tutorials/About.xml)
16. [RimWorld wiki: Mod Folder Structure](https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_Folder_Structure)
17. [Steamworks: Workshop Implementation Guide](https://partner.steamgames.com/doc/features/workshop/implementation)
18. [Steamworks: Workshop Item Tags](https://partner.steamgames.com/doc/features/workshop/tags)