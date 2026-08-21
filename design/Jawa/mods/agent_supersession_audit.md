<!-- status: live -->
# agent_supersession_audit.md — "does a mod already do this?"

_A single source-level audit (Fetcher 2026-08-08) answering, for each enrichment agent in
`design/Jawa/worldbuilding/enrichment_agents.md`, whether an existing mod already does the job. Kept as its own
file because the **ADJUSTER vs DEFINED-EFFECT** distinction below is the reusable part — it is the
test that decides whether adopting a mod deletes work or only moves it — and because burying a
13-row verdict table inside `required_mods.md`'s date-ordered log would lose it._

**Adoption verdicts still live in `required_mods.md`.** This file says *what a mod can do for us*;
that file says *what we run*. The 1.6 `<supportedVersions>` pins from the same pass are also there
(§"About.xml 1.6-verify pass"), not here.

_Salvaged from `RimMaster.md` when that spec was retired; the audit never depended on it._

---

## The distinction that reversed several verdicts

Motivation (user): *"the less I have to write, the faster I get to play."* A first 20-search Fetcher
batch (`Delivery/2026-08-08_agent_normalization_mods/`) gave optimistic first-pass verdicts; a
follow-up **25-item source-level deep-dive** (`Delivery/2026-08-08_mod_deepdive_claims/`, filed
because the user rightly warned *"a lot of animal frequency things are just 'adjusters' without
normalized effects clearly spelled out — useless"*) then read the actual GitHub READMEs/source and
**materially reversed several verdicts.**

- **ADJUSTER** — the mod exposes a knob (a slider / an editable stat field) but encodes **no notion of
  what a *coherent* value is**. Customize Animals says it outright: *"This mod does not change anything
  on its own… there are basically no limitations in regards to balance, you decide on what fits."*
  Animal Commonality Tweaker: *"It's a tool for tweaking the wild animal commonality value."* An
  adjuster is a **write surface with no brain** — adopting it deletes *zero* real work (deciding every
  value + the §19.5 balance judgment); it only saves writing an XML-poker.
- **DEFINED-EFFECT** — the mod ships spelled-out semantics/targets (per-def rules, event cadences, a
  balance model). *Dynamic Diplomacy* is the clean example: hostility flips ≈every 20 days, conquest
  ≈15 days, new settlements ≈40 days, alliance thresholds, rebellions — a real simulation, not a knob.
  These can genuinely **supersede** a build.

**Verdict legend:** ⛔ **SUPERSEDED** (a defined-effect mod does the whole job — build nothing, just
configure) · 🧰 **ADJUSTER-ONLY** (a knob with no defined coherent state — we still decide **every**
value and carry the balance judgment) · 🟡 **MECHANISM-ONLY** (a *structured* write surface, e.g.
per-pawnkind/per-faction schema — the work shrinks to "decide values + drive the mod") · 🔨 **BUILD**
(no off-the-shelf coverage).

⚠️ **Every Workshop ID below is a search/deep-dive hit.** 1.6 `<supportedVersions>` pins are in
`required_mods.md`; items the deep-dive source-tagged 1.6 are noted `[1.6 src✓]`.

---

## Verdict table

| Agent (phase) | Verdict | Off-the-shelf mod(s) — the leverage | Residual we still author |
|---|---|---|---|
| Weapon/armor normalization (B) | 🔨 **BUILD** (confirmed) | **RWWB / RimWeapon Balance** (932311074) — self-described *"a series of mod patches… balanced according to the averages between them, not vanilla"* = a **curated patch-set for a specific mod list**, not a general normalizer; **Vanilla Expanded Rebalance – Weapons** (3619272479) — *"comprehensive rebalance patch for the VWE series"*, **scoped to VWE only**; **Combat System Rebalanced** — a *combat-math* mod (changes how armor/damage/deflection interact), **not** a per-weapon normalizer; RIMMSQOL/[Kas] Combat Tweaks = adjusters | Confirmed by re-fetch (`2026-08-08_mod_deepdive_refetch` searches 002/004/005): no mod does a *holistic cross-author* pass over OUR exact stack. The §19.5 judgment + coherent target values stay ours. **BUILD stands.** |
| Animal normalization (B) | 🧰 **ADJUSTER-ONLY** (was 🟡→⛔ — **downgraded**) | **Customize Animals** (2587157544; GitHub ChrisF-127 `1.6/` folder `[1.6 src✓]`) — rich per-animal stat surface but **self-described "changes nothing on its own, you decide what fits"**; **Choose Wild Animal Spawns** (2564042934 `[1.6 src✓]`) per-biome-per-animal slider + density + copy/reverse; **Animal Commonality Tweaker** (2591446825) — *"a tool for tweaking the commonality value"*, and explicitly **only wild spawns — not manhunter, not trader, not enemy-attached animals**; **Livestock Traders** (2960610215 `[1.6 src✓]`) adds generic livestock traders but does **not** map which-faction-sells-what | **Almost everything.** These are knobs, not normalizers — every commonality/density/stat value plus the anti-exponential balance model is still ours. Choose Wild Animal Spawns has the best granularity (per-biome-per-animal) so it's the preferred write surface *if* we drive it. |
| Faction repair/enrichment (B) | **split** | **Dynamic NPC-NPC layer → ⛔ SUPERSEDED: Dynamic Diplomacy – Continued** (`[1.6 src✓]`) is a genuine **defined-effect** sim — hostility flips ≈20d, conquest/razing ≈15d, new settlements ≈40d, ideology adoption, alliances (>10 settlements / 40–60% planet), rebellions, save-safe "History Generation" option. **Static per-faction identity layer → 🟡 MECHANISM-ONLY:** **yc's Faction Editor** (**1.6-only** `[1.6 src✓]`, deepest — per-pawnkind gear/forced-gear/material/quality/biocode/xenotype-prob/traits/genes/appearance/trade inventory + faction create/modify) and **TotalControl** (feldoh, *already in stack*, `[1.6 src✓]` — role names/apparel/hair/weapon types/colors/caravan animals per pawnkind per faction); **Xenotype Spawn Control** (bbradson `[1.6 src✓]`) racial mixes; **Faction Customizer** (3336572602 `[1.6 src✓]`) rename/ideology/relations/colour/add | For the **dynamic** layer: only choosing to enable it + initial relations. For the **static** layer: the editors are structured write surfaces but carry **no idea of our roster** — the reconciliation *to* `design/Jawa/worldbuilding/faction_roster_v2.md` is still ours. |
| Trader-inventory coherence (B) | 🧰/🟡 | **TraderGen** (3525848981) per-trader specializations = closest to *defined-effect* (ships opinionated trader archetypes) — re-verify; **Trading Options** (2876541977) freq/stock/silver = knobs; **Livestock Traders** (`[1.6 src✓]`, generic, no faction mapping) | The faction-identity → stock *mapping* itself — no mod knows our roster. |
| Research-tree / techprint gate guard (B) | 🔨 | **NONE** — Research Tree (Continued)/ResearchPal/Organized Research Tab are *visualizers/queues*, not gate-requirement editors. Notable negative result. | The entire three-gate integrity check stays a patch job. |
| Name-pool localization (B) | 🧰 ADJUSTER-ONLY (**confirmed**) | **Cool Names** (3726665156) — **verified**: *"overhauls name generation… custom name pools for different technological and thematic groups, no auto-nicknames, prioritizes first names"* = a **loader for authored pools**; **Pawn Name Variety** (emipa606), **NamesGalore** (AaronCRobinson), TotalControl (names per faction) | **No SW name-pack exists** — we author every bank; the mod is the loader. Correct by nature: a name pool is *content*, not a normalizable effect. |
| Map hand-crafting (C) | 🟡 (set-pieces) / 🔨 (holistic) | **New Blueprint** (3534166729 — **verified**: *"using the new Prefab system introduced in RimWorld 1.6 to create shareable blueprints that capture both terrain and buildings"* = native-1.6-prefab write-primitive for stamping authored set-pieces), **Alpha Prefabs** (3070780021 `[1.6 src✓]`, 200+ prefabs), **Real Ruins** (1552146295), **Vanilla Landmarks Expanded** (3656316229); Map Designer (owned) | The *holistic "make a generated tile feel hand-crafted"* judgment — the hard, high-V&V core — stays a build. Prefabs are set-piece *content*, not a normalizer. |
| NPC hand-crafting per map (C) | 🟡 | **Pawn Editor** (ISOR3X), **Character Editor** (owned), **Backstory Constructor** (2907131508, *already PRIMARY* in the personas doc), **RimTalk Persona Director** (3619548407) | The authored per-NPC content + context-tuning; mods are the write surface. |
| Emergent ship-sentience voice + **demands** (D) | ⛔ candidate → **BAKE-OFF RESOLVED 2026-08-08** | **RimTalk Expand: AI Storyteller** (3715752189) — *"storyteller becomes a character… four dims: benevolence, malice, calmness, morality… tyrant drops raids when annoyed, guardian sneaks gifts, chat directly."* **RimAgent:Orca** (`RedstonePanda.Orca`, `[1.6 src✓]`, graceful offline-XML fallback). vs the already-adopted **RimAI Core** (buildable talkable Server/Terminal = the Cradle-Mind). | **✅ RESOLVED — RimAI WINS the ship-voice; the "RimTalk-Expand retires the bespoke build" hypothesis was WRONG (false substitute).** See the verdict block below. |
| "State of affairs" / social-log summarizer (D) | ⛔ substrate → **later reversed** | **RimLog** (ubergarm, GitHub `RimWorld-RimLog`) — *"logs periodic time-series data for events, tales, quests, chat and battle logs in CSV format… handy for crafting Local-LLM AI-generated story prompts using your actual player data."* Timestamped-tick CSV schema (`type,defName,text`) = exactly our blackboard feed | ⛔ **RULED OUT — RimLog is 1.5-only** (About.xml pass; no 1.6 branch/tag/release). The clean no-LLM feed does not exist on 1.6. This is the origin of the event-feed gap, `design/Jawa/worldbuilding/enrichment_agents.md` §7.3. |
| Social-drama chronicler (D) | ⛔ (**confirmed**) | **RimLegend** (3697076313, Rifex, **Mod 1.6 + Harmony**, 200-fetch verified) — *"captures every event… sends them to an AI of your choice (Ollama/OpenAI/Groq/**Anthropic**/any OpenAI-compatible). Two-layer: Main Colony Chronicle (Event.md) + per-colonist bios. 5 styles or define your own. Author directives to steer. Hierarchical summarization keeps tokens predictable after 100+ hrs."*; alts **EchoTales**, **RimSaga** | Chronicler agent **collapses entirely** into RimLegend — style + author-directives cover our steering need. LLM-endpoint dependency; comments report connection flakiness (test before relying). |
| Difficulty-drift monitor (D, read-only) | 🟡 | **Visible Wealth** (3461137081, breakdown + pie), **Wealth Display (Continued)** (3298960397), **Wealth Tweaks** (Nexus 694, cap scaling = manual actuator). NB: raid points hard-cap ~10,000. | The *automatic pillar-drift flag* (vs a static readout) isn't off-the-shelf; monitoring + manual cap are. |

---

## Decision translation (revised after the source deep-dive — the earlier optimism was wrong)

The user's warning held: *most of the "collapse into config" verdicts were overstated because the mods
are adjusters, not normalizers.* The honest breakdown:

- **Genuine build-deletes (defined-effect mods that really do the job):** **one** in the normalization
  space — **Dynamic Diplomacy – Continued** (real event sim, spelled-out cadences). On the Phase-D side,
  **RimLegend** (two-layer AI chronicler, 5 styles, author-directive steering, hierarchical
  summarization, Anthropic-API support) collapses the drama-chronicler build entirely.
- **Adjuster-only (🧰) — NOT a build-shrink:** the animal layer (Customize Animals, Choose Wild Animal
  Spawns, Animal Commonality Tweaker, Livestock Traders) and the name-pool layer are **knobs with no
  defined coherent state**. Adopting them saves only writing an XML-poker; every value and the entire
  anti-exponential/§19.5 balance model is still ours. This is the bulk of the work and it does **not**
  go away. *"The less I have to write" barely moves here — what I have to* decide *is unchanged.*
- **Mechanism-only (🟡) — structured write surface, brain still ours:** the static faction-identity
  layer via **yc's Faction Editor** / **TotalControl** / **Xenotype Spawn Control** — none know our
  `design/Jawa/worldbuilding/faction_roster_v2.md`, so the reconciliation is still authored.
- **Still-real builds:** research-gate integrity guard (no mod exists), holistic map hand-crafter (only
  set-piece *stamping* is covered), cross-author weapon/armor balancing brain.

*Principal risk:* the AI-chronicler/voice mods (RimTalk family, RimLegend, Orca) need an external/local
LLM endpoint and mutate live — they inherit the save/reload-survival unknown
(`design/Jawa/worldbuilding/enrichment_agents.md` §7.1) plus a model-quality dependency.

---

## Ship-voice bake-off — RESOLVED 2026-08-08 (RimTalk-Expand vs RimAI vs RimAgent:Orca)

_Decided from source-read evidence already in hand (`design/Jawa/worldbuilding/ship_distinctive_features.md` Q1-bis
Fetcher `2026-08-07_llm_speaking_mods_deep` + `2026-08-07_rimai_rimdialogue_source`)._

**The framing was wrong on one point, and correcting it IS the verdict:** the three mods were listed as
candidates that might "retire the bespoke ship-voice build." That treated them as substitutes for one
voice. They are **not** — they voice **three different surfaces**, so it is not winner-take-all:

- **RimAI Core** (`kilokio.rimai.core`, 1.6-only; + Framework `kilokio.rimai.framework`, 1.5/1.6) — voices
  a **buildable, in-world talkable Server/Terminal object** with an authored Persona module. The **only**
  mod in the whole search space where the voice is natively *a machine you build and address* — a
  near-perfect vehicle for the **engine-is-god / Cradle-Mind** (Ohm the All-Current speaking through the
  grav-controller). **Already ADOPTED** (user, 2026-08-07). **→ WINS the ship-voice role.**
- **RimTalk-Expand: AI Storyteller** (3715752189) — voices the **storyteller-as-character** (four fixed
  personality axes; drops raids when annoyed, sends gifts, chattable). A **different role**. **→ NOT the
  ship voice.** Verdict: **PARK** — a second LLM director is duplicate machinery alongside the
  storyteller/GM layer we author ourselves.
- **RimAgent:Orca** (`RedstonePanda.Orca`, 1.6✓) — an **LLM storyteller/companion** with the best offline
  story of the field (ships XML storyteller comps; with no LLM configured it degrades gracefully to the
  vanilla XML storyteller). Same *role* as RimTalk-Expand. **→ NOT the ship voice.** Verdict: **PARK as
  the graceful-degradation reference** — its offline-XML fallback is the pattern to imitate if we ever
  want our GM layer to survive an LLM outage. Not adopted as a mod.

**Bottom line:** the ship voice was already solved (RimAI Core, adopted) and this bake-off *confirms* it
rather than replacing it. RimTalk-Expand and Orca lose **not on quality but on role**. **No new adoption
results from the bake-off; RimAI stays the Cradle-Mind.** Remaining RimAI watch-items are unchanged (use
VOICE-ONLY, keep its actuator tools disabled per the anti-exponential pillar; non-LLM fallback = SpeakUp
+ CQF DialogTree + a single quested vanilla persona core — see `required_mods.md` §(8)).
