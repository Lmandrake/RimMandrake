# The Designer, Relentless and RimWorld mods: a brief for an outside reader (2026-11-02)

Written for a GPT consult (answer: `mod_description_designs_gpt_2026-11-02.md`). Plain summary of
`src/RimMandrake/rimflow/roles/designer.md`, `concept_agent_design_2026-11-01.md` and
`relentless_agent_design_2026-11-01.md`; where this brief and those files disagree, they win.

Owner, 2026-11-02: *"Please write up the Designer agent now, along with Rimworld mod context and links to Steamworks
for Rimworld, and ask GPT what the elements of a Mod's description SHOULD be to well define it for a Relentless
builder. Give three competing designs with trade-offs. Have it look in actual mod repo's for docs and capabilities."*

## 1. Who we are

One owner (a single human, busy, judges by looking and playing) and a set of AI agents that build RimWorld mods for
him. The mods ship in three name tiers: **RimMandrake** (general), **RimStarWars** (Star Wars content) and
**RimUtinni** (Jawa/salvage flavour), packageId `mandrake.<tier>.<mod>`, def prefixes `RM_`/`RSW_`/`RUT_`. Examples:
Gimme Some Slack (power cables drawn as loose extension cords), FlowWorks (hoses and fluids), biomes, creatures.

## 2. The Designer: what it is and does

An on-demand agent that argues with the owner about ONE mod until both can say what it does and does not do, then writes
that down so a builder and a judge cannot misread it. It writes no code and no art. Its character is Socratic: it leads
by questions he can answer from his own picture of play, names vague words, finds the case he has not pictured, and holds
a position until a reason moves it. Its product is a folder `design/concepts/<Mod>/` holding:

- `sheet.md`, one page he reads: `his words` (verbatim, dated), `does`, `does not`, `waived`, `open`, `delegated`,
  `pruning`, `later`. Each `does`/`does not` line is tagged: a leaf, a floor line, a waiver, or advisory.
- `tree.json`, the acceptance tree: a root (his "north star" experience, his words) and leaves.
- `plan.md`, the implementation plan. `log.md`, every question and verbatim answer (its only memory between runs).

**Stages.** 0 Read (his words, our nearby mods, a vanilla or popular mod doing the same thing, engine feasibility, and
an inventory of what is ALREADY BUILT; never ask him to keep or cut a built capability). 1 Argue the idea (what is it,
whose play changes, smallest version he still wants). 2 Argue the edge (every core line becomes does, does not, waived,
delegated or later). 3 Write (sheet, tree, plan; a lint must pass: Gate A). 4 Exam (below). 5 Lock (an Arbiter signs
coverage; the tree is hash-locked and handed to Relentless).

**A turn with him**: Claim, Attack, Picture (what he would see if each side won), at most three Asks each answerable in a
phrase, and a pre-review by a fresh agent that strikes asks already built or already answered. Five moves: the dumb
version (laziest build that passes the words), a counterexample, the other side (how vanilla or a popular mod does it),
the unsaid sweep (reload, pawn death, 40 colonists), the boundary (usually a `does not`).

**His answers map to records**: yes → does; no → does not (a must-not leaf); "this doesn't matter to me" → waived, in
his words, never raised again; "you decide" → delegated; "show me" → open (an open core line blocks the gate); "not
now" → later (v2); silence → nothing.

**Pruning question** for every would-be leaf: "If everything else worked and only this was false, would you reject the
mod?" No → at most an advisory line. A small mod should fit in eight leaves.

**What a well-defined mod has (owner, 2026-11-02)**, eight elements the Designer must walk:
1. Why reach for it: the player's problem or desire before the mod.
2. Using it: what you do, see and hear, first use, routine use, at 40 colonists (not how it is learned).
3. The result: what changes in the colony's story, decisions and enjoyment.
4. The costs: materials, research, clutter, ticks; what it diminishes or forbids.
5. When it goes wrong: how it fails or is misused, and the readable sign the player gets.
6. Edges: what it deliberately does not do.
7. Neighbours: standing rulings and other systems it meets.
8. Settings: which numbers are the experience, hence toggles and tuning.
Acceptance falls out of the same list: each experience becomes a check with an observer, a situation, what good looks
like, and its proof (mechanical, or a human walk on a staged map or save). A mechanical test alone never accepts an
experience. He checks completeness by reading short stories at key moments (first build, routine use, the failure, the
payoff), not a whole day. A judge agent may rule on enjoyment a priori; the owner confirms.

**The exit test (Gate B, the Cold Reader exam).** Fresh agents who never saw the debate read only the sheet and tree and
predict his verdict (accept / reject / doesn't matter) on 10 frozen scenarios, some written by a Challenger from outside
the sheet. He answers the same 10. Pass: at least 9/10, and zero "predicted accept where he said reject" on a core line.

## 3. Relentless: what it needs from a spec

Relentless is a fire-and-forget builder: *"a fire-and-forget agent you can point at a modest goal and trust it will get
all the way there."* Its promise: a goal accepted at intake reaches a Judge-accepted, checkable done, or stops with a true
statement of why. Its limit: done means the contract was met, not that the contract was complete.

The rule it rests on: **who builds does not set the exam, does not hold all of it, and does not mark it.** So:
- **No tree, no item.** An item without the Designer's tree is refused at intake.
- A **Setter** (a judge-mode agent that never builds this item) binds each leaf to an instrument and writes 1-3 secret
  hold-out checks per leaf. It may not add, drop or reword a criterion.
- A **Marker** (judge mode, behind a filesystem wall from everything the builder wrote) marks the evidence packet.
- Each leaf must carry eight fields: `experience` (what an observer sees; a constraint states number, unit, test
  machine), `scenario` (setup and action), `oracle` (instrument and what it must read), `false_pass` (a named wrong world
  that would read green: the Pit, *"pawn despawns but the player watches someone stand in a box labelled Pit"*), `red`
  (what failure looks like; the check must be seen failing, at base and with a planted guard), `tier` (cheapest test level
  that can settle it; live only with a reason), `budget` (set by a program), `owner_part` (what he must look at; the first
  GREEN of a mod is always his).
- Every mod has one **walk leaf**: the whole scenario on one build, including a reload mid-way, a repeat of the core
  action, and a second order of the main actions.
- Loosening the contract needs his words; tightening is open to the Marker.
- Mechanical constraints are inherited from a shared **floor** (tick cost, stalls, latency, memory, load time, save size,
  log cleanliness, Mod Settings, art, text, naming), numeric lines advisory until calibrated on five mods.

## 4. RimWorld mod context

- **Content is XML Defs** (ThingDef, PawnKindDef, BiomeDef, ...) in `Defs/`, with abstract parents and inheritance.
  Changes to other mods' or vanilla defs go through **PatchOperations** (XPath-based, in `Patches/`). Silent failure modes:
  a patch matching nothing logs nothing; `MayRequire` on a top-level `<Operation>` is ignored.
- **Behaviour is C#** compiled to a DLL in `Assemblies/`, usually with **Harmony** (prefix/postfix/transpiler patches on
  game methods). `Plant` ticks only on the long tick, one of many engine traps.
- **About.xml** names the mod: `packageId`, supported versions, dependencies, `loadBefore`/`loadAfter`. Load order matters;
  the game reads `ModsConfig.xml` for the next load.
- **All DLC are assumed present** (Royalty, Ideology, Biotech, Anomaly, Odyssey): no gating, no degraded mode.
- **Mod Settings rule (owner, 2026-09-12)**: every mod ships on/off per major feature, tuning where a number is the
  experience, defaults = shipped behaviour, all-off degrades gracefully. No exceptions.
- **No worldgen of any kind.** Players receive a savegame holding one hand-made, frozen world. Our biome on 0 tiles is
  expected. Biome mechanics are promised inside our biomes only. No multiplayer support.
- **Flight** of a flying creature is never tested live without the owner; it is verified by a state read.

## 5. What our builders can and cannot test

| Tier | Can | Cannot |
|---|---|---|
| Offline validators | XML well-formed, xpath resolves against a def dump, naming, texture size and alpha, lints | Anything that needs the game to run |
| Def dumps | Every resolved def after patches, from a real load of the same mod set | Runtime state, rendering |
| Live bridge (RimBridge/JawaBench) | Drive a running game: spawn, advance ticks, read state, take screenshots, quicktest colonies; a 13-mod list loads in 22 s | Feel, timing as perceived; the full 25-minute mod list is expensive |
| Northstar walks | A scripted whole-mod walk on a staged map, checked against the owner's north-star lines | Proving taste |
| Human looks | Owner judges art and play on a review sheet or a shipped savegame | Scale: his minutes are the scarcest resource |

The failure we fear most is **the Pit**: every state assertion green, the screen wrong, because nobody pinned what he
meant before the build.

## 6. Links (each checked to resolve, 2026-11-02)

- RimWorld Steam Workshop: https://steamcommunity.com/app/294100/workshop/
- Steamworks Workshop docs: https://partner.steamgames.com/doc/features/workshop
  and implementation: https://partner.steamgames.com/doc/features/workshop/implementation
- RimWorld wiki, Modding Tutorials: https://rimworldwiki.com/wiki/Modding_Tutorials
  (About.xml: https://rimworldwiki.com/wiki/Modding_Tutorials/About.xml ;
  PatchOperations: https://rimworldwiki.com/wiki/Modding_Tutorials/PatchOperations ;
  Harmony: https://rimworldwiki.com/wiki/Modding_Tutorials/Harmony ;
  Mod Settings: https://rimworldwiki.com/wiki/Modding_Tutorials/ModSettings ;
  folder structure: https://rimworldwiki.com/wiki/Modding_Tutorials/Mod_Folder_Structure)
- Harmony: https://github.com/pardeike/Harmony and https://harmony.pardeike.net/articles/intro.html
- Vanilla Expanded on GitHub: https://github.com/Vanilla-Expanded

## 7. Example: Gimme Some Slack, current definition state (sheet DRAFT, sitting 2, 2026-11-02)

Built today: 31 inventory entries, 14 working at level 2+, 4 broken, 13 unverified. Round 1 answered; round 2 open.
No `tree.json` yet.

- His words (selection): *"Everything is a too-long extension cord."* *"Conduit that suddenly ends has a "node" at its
  terminal point that must be reached by a "broken" cord lying on the ground. Sparking if live, dead if not."*
  *"ideally a huge tangle of nasty wires and power strips"* *"it allows GimmeSomeSlack to be entirely about cables and
  conduits and electricity."* *"Yes, I want both poles and floor coords."*
- Does (leaves): no vanilla conduit pipe visible, only cords; cords lie in broad loops and pile against walls; a cord ends
  at the wall face; dense conduit reads as one tangle with power strips; live and dead cut ends look different; overhead
  spans drawn above pawns; a downed span lies on the ground; cutting or building one wire in a large base causes no
  visible stall; walk (reload mid-way, cut and repair, build a second grid). Floor: master switch off restores vanilla.
- Advisory: four art styles, one look per connected run; power theft with goodwill drain; wire-down alert; re-stringing.
- Does not: draw anything for hoses (FlowWorks owns them); pull a cord taut; draw across walls or rock. No multiplayer.
- Waived: *"I don't much care about savegame continuity"* (mod removal).
- Open, core: does a false drawing (cord across a cut, phantom second cable, plug into a pipe slot) reject the mod?
  Open: after a gravship landing, do cords keep their look or get laid fresh?
