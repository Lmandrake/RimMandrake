# faction_authoring_mechanism.md — How we make rich, differentiated factions

_The coherent method for the "Per-Faction Definition to the Samuel Streamer level" deliverable. This file owns the **mechanism** (source-grounded evidence, the FactionDef field map, the build layers, the dossier template). The **filled roster** lives in `faction_roster_v2.md`; the **status / dependencies / next-steps** live in `Custom_World.md` under the "🅿️⭐ PARKED — Per-Faction Definition" heading (the parked-work board) — not duplicated here._

---

## 0. The core insight (evidence-grounded, not asserted)

**[Evidence]** I read Outer Rim Core's own 1.6 FactionDefs — `Faction_MoistureFarmers.xml` (peaceful Outlander) and `Faction_BinaryStarRaiders.xml` (permanent-enemy pirate). The two factions ship an **identical** `maxPawnCostPerTotalPointsCurve` — the curve that translates raid points into pawn budget is byte-for-byte the same. Every bit of felt difference between "farmers who hire mercs to defend a claim" and "hit-and-run marauders who strike fear into spacefaring communities" is carried by four things:

1. **`pawnGroupMakers`** — *which* archetypes spawn and at what weights. Raiders get six distinct combat compositions (mixed, melee-only, ranged-only, explosives, snipers-only, lone-drifter); Farmers get settlers + guards + hired mercenaries + a Miners group. Same points budget, completely different battle.
2. **Ideology fields** — Raiders `requiredMemes` Supremacist + Raider, `allowedMemes` PainIsVirtue + FleshPurity, culture Kriminul. Farmers are theist, `disallowedMemes` Nudism/Blindsight/Animist, culture Rustican.
3. **`raidLootMaker`** — a `ThingSetMakerDef` with a fixed filter. Raiders drop Silver, bacta, Tibanna, Durasteel — a recognizable plunder signature.
4. **Flavor** — `label`, `description`, `pawnSingular`, `leaderTitle` (boss vs. councilman), `colorSpectrum`, `factionNameMaker` (Pirate vs. Outlander namer).

**The conclusion that drives everything below:** *distinctiveness comes from composition and curation, never from stat inflation.* This is the anti-exponential pillar (§19.5) proven in the base mod's own data. Our whole mechanism therefore edits **which pieces** a faction is made of and **what we delete** — and leaves the danger-scaling curves alone. A faction is dangerous because of *what it fields and how it fights*, not because its numbers are bigger.

---

## 1. The mechanism in one picture

```
   PER-FACTION DOSSIER (markdown, one file section per faction — the single source of truth)
                    │  (Claude authors this; you approve/steer)
                    ▼
   ┌────────────────┼───────────────────────────────┐
   ▼                ▼                                 ▼
 (A) CURATION     (B) GENERATION                    (C) INSTANCE / PLACEMENT
 layer            layer                             layer
 ─ Sensible       ─ FactionDef override patch        ─ starting-save .rws edits
   Factions         (label/desc/memes/               ─ the placed faction's custom
   allow-list       pawnGroupMakers/loot/flavor)       <name>, its leader pawn,
 ─ Cherry Picker  ─ PawnKind + apparel/weapon          goodwill/relations
   delete-list      tag distribution (arsenal)      ─ any faction-specific map edits
 ─ Backstory
   Constructor
   (leader persona)
```

One dossier compiles into three kinds of concrete artifact. **(A)** and **(B)** are *rules* (reproducible config that regenerates any world). **(C)** is *authored state* (the specific instance in our specific save — the thing you can't get from rules alone, and the thing Streamer's starting saves teach us to build). This split is already our decided model (save-based authoring, Custom_World status board).

---

## 2. The five differentiation axes → concrete FactionDef fields

Every faction is deliberately differentiated on each axis. The right-hand column is the *actual* XML lever (verified against Outer Rim's 1.6 source), so "author a faction" has a precise meaning, not a vibe.

| Axis | What it controls | Concrete lever (FactionDef unless noted) |
|---|---|---|
| **Identity / face** | How you'd describe them to a friend | `label`, `description`, `pawnSingular`/`pawnsPlural`, `leaderTitle`, `colorSpectrum`, `factionIconPath`, `factionNameMaker`, `settlementNameMaker` |
| **Disposition / doctrine** | Friend, foe, or fickle; how they pressure you | `permanentEnemy`, `canSiege`, `canStageAttacks`, `categoryTag`, + **Faction Territories & Vassalage** (in-turf ambush), **Faction Raid Cooldown** (coherent pressure), **CAI-5000** (how they fight) |
| **Arsenal / capability** | What they field — the §19.5 axis | `pawnGroupMakers` archetype mix + weights; the referenced `PawnKindDef`s' `weaponTags`/`apparelTags`; VWE-Makeshift junk tier vs. Outer Rim charge tier distributed *across* factions |
| **Belief / culture** | Why they act as they do | `allowedCultures`, `requiredMemes`, `allowedMemes`, `disallowedMemes`, `structureMemeWeights`, `backstoryFilters` |
| **Economy / interaction** | What they trade; can you ally/vassalize | `caravanTraderKinds`, `visitorTraderKinds`, `baseTraderKinds`, `raidLootMaker` (ThingSetMaker filter), vassal stance via Faction T&V |

**Leave alone (pillar guard):** `maxPawnCostPerTotalPointsCurve` and any raw stat multipliers. Escalation across the 3-act arc is authored by *changing the pawnGroupMaker composition a faction fields* (e.g., the Empire's late-game groups add charge-tier elites and armor), **not** by steepening the points curve. If a proposed faction edit touches the curve, it fails §19.5 — reroute it to composition.

---

## 3. How each layer is actually built

### (A) Curation layer — subtractive identity
- **Sensible Factions / Faction Filter (WS 3531306011):** allow-list only the cast. A faction reads as intentional partly because the soup around it is gone.
- **Cherry Picker (WS 3521312241):** for each faction, delete the off-theme xenotypes / sub-factions / things its source mod drags in, so the roster reads clean. Each dossier's *"What Cherry Picker deletes from their source"* field becomes a line in `cherry_picker_killlist.md`. (defNames confirmed in-game — that step is still open.)

### (B) Generation layer — Claude-authored override patches
This is the "your own authoring power" the user asked about, made concrete. For each faction we write a **PatchOperation** file (or a standalone override FactionDef loaded after Outer Rim) that overrides only the fields the dossier changes — most often `description`, the meme lists, the `pawnGroupMakers` weights, and the `raidLootMaker` filter. We do **not** fork the whole mod; we patch the specific nodes. Arsenal differentiation is done here by editing which PawnKindDefs a group draws and (where needed) their `weaponTags`/`apparelTags`, so scavenger clans field scrap+Makeshift while the Empire fields charge-tier — *without* changing any weapon's stats.

### (C) Instance / placement layer — starting-save authoring
The generation layer makes a faction *type*; the save makes *this world's instance* of it. In the `.rws` (plain-text XML, already dissected in our Gravtasm anatomy work) each faction is a node in the world-level faction list with a `<def>` plus an editable custom `<name>`. Here we set the specific faction name, place its leader pawn (persona authored via **Backstory Constructor**, WS 2907131508), and set starting `goodwill`/relations. **Handle with care:** rosters and relations are ID-linked — flavor/name edits are safe, structural relation edits need the ID map kept consistent (also established in the anatomy work).

---

## 4. The per-faction dossier template (the format)

One of these per faction, all in one file so they can be diffed against each other. Fields map 1:1 to §2's axes, with the target XML lever named so authoring is mechanical.

```
### <Faction working name>
- Premise (one line):            → label + description
- Emotional register:            → tone of description + colorSpectrum + namer choice
- Disposition:                   → permanentEnemy / canSiege / canStageAttacks / categoryTag
- Tech tier:                     → techLevel + which PawnKindDefs the groups draw
- Signature arsenal/apparel:     → pawnGroupMakers options + PawnKind weaponTags/apparelTags
  §19.5 note:                    → assert danger is compositional; curves untouched
- Raid & movement doctrine:      → pawnGroupMaker mix + Faction T&V / Raid Cooldown / CAI-5000
- Belief/culture:                → allowedCultures + required/allowed/disallowedMemes
- Economy / trade goods:         → *TraderKinds + raidLootMaker filter
- Alliance / vassal stance:      → goodwill start + Faction T&V vassalage eligibility
- Named leader persona:          → Backstory Constructor entry (lore + skillGains + workDisables)
- What Cherry Picker deletes:    → line(s) for cherry_picker_killlist.md
- Distinct-from line:            → how this contrasts with the faction nearest it
```

**The forcing function:** after all dossiers are filled, **diff them**. If two factions' *Signature arsenal*, *Doctrine*, and *Distinct-from* lines could be swapped without noticing, one faction isn't pulling its weight — merge or re-differentiate. This is the step that turns "several Star Wars factions installed" into "a cast of distinct powers."

---

## 5. What examining the save games buys us (the user's hunch, assessed)

**[Evidence — confirmed against the Gravtasm save on disk, 2026-08-05]** the instance layer lives at `<factionManager><allFactions>`, where each `<li>` is one placed faction instance with exactly the shape the mechanism predicted:
```
<li>
  <leader>Thing_Human760</leader>      ← points to a specific pawn Thing ID (the authored leader)
  <def>PatreonCivil</def>              ← the faction TYPE from the (B) generation layer
  <name>Holy Council of the Liplickers</name>  ← the editable custom instance name
  <randomKey>269983972</randomKey>
  <colorFromSpectrum>0.626971781</colorFromSpectrum>
</li>
```
The save carries 300+ such faction entries (many are per-trader-company sub-factions of the Merchant's Cartel). This confirms the three instance-layer edits are real, located nodes: set `<name>`, point `<leader>` at an authored pawn, and the `<def>` binds back to the generation-layer type. `<name>` is free-text and safe to edit; `<leader>` and any relations are ID-linked (edit with the ID map kept consistent).

**[Status update]** We already hold **Gravtasm's** starting save (dissected above), so the core instance-layer node shape is now *evidence*, not inference. The remaining gain is **Bounty Hunter's** starting save — it uses our exact Outer Rim + nomad stack (the #24 reference), so it would show how *combat/pursuer* factions (not just trade companies) get their leader pawns, starting goodwill, and any faction-specific map edits wired in. **Recommendation:** pull Bounty Hunter's save before executing the instance layer for the Empire/Bounty-Hunter pursuers — highest-value remaining input, but not a blocker.

**Workaround if the saves don't come:** we can still author the instance layer from our own Gravtasm dissection — we know the node shape. The saves would make it faster and lower-risk, not unblock it.

---

## 6. Dependencies, risks, next steps

→ **See `Custom_World.md`, the "🅿️⭐ PARKED — Per-Faction Definition" heading** (the parked-work status board). It owns the live status: what gates execution (the Sensible Factions casting decision), the "fill the ~4 already-decided factions now" workaround, dependencies, principal risk (shallow pass → "lots of SW mods installed"), and the ordered next steps. Kept there, not here, so there is one place to update.

Two linkages specific to *this* mechanism, so they're recorded at their source: the §19.5 arsenal audits feed each dossier's *Signature arsenal* + *Doctrine* fields, and the in-game Cherry Picker defName confirmation feeds the *What Cherry Picker deletes* field. The diff step (§4) is the guard against a shallow pass.

---

## 7. Worked micro-example (proof the format produces contrast)

Two factions from the decided set, filled just enough to show the mechanism forces difference. Not final content — illustrative.

**Jawa scavenger clans** — Premise: *"Scrap-hoarding desert nomads who strip anything that stops moving."* Register: comedic, skittish, greedy. Disposition: not permanentEnemy (raidable + tradeable + potentially placatable). Tech: Industrial floor. Arsenal: VWE-Makeshift junk + salvaged low-tier Outer Rim cast-offs; groups are many-but-weak (swarm of Scavenger/Drifter archetypes, no elites). §19.5: threat is *numbers + unpredictability*, not gear. Doctrine: hit-and-grab, retreat when hurt (CAI-5000 flavor), ambush in their own dune turf (Faction T&V). Economy: trade scrap/components, want anything shiny. Leader: a clan chief persona, high Social/Crafting, disabled Intellectual. Cherry Picker: strip any off-theme xenotypes their source drags in. **Distinct-from Empire:** disposable swarm vs. disciplined elite.

**Outer Rim Empire (pursuer)** — Premise: *"A disciplined military power that wants the gravship back."* Register: cold, inexorable. Disposition: escalating enemy, sieges, staged attacks. Tech: Ultra (charge-tier). Arsenal: elite mercenaries + heavies + snipers, charge weapons, armor; §19.5: danger is *quality and coordination*, groups stay small — curve untouched. Doctrine: sieges + coordinated assaults, presses hardest in Act III. Economy: does not trade with you; loot is charge-tier gear. Leader: an Imperial officer persona, Shooting/Melee capable, high, disabled nothing menial-relevant. Cherry Picker: delete non-Imperial sub-factions the source bundles. **Distinct-from Jawa:** few, elite, relentless vs. many, ragged, opportunistic.

Diffed: arsenal, doctrine, disposition, economy, and register all invert. The format is doing its job.
