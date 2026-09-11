<!-- status: design brief — nothing here is built -->
# The slimification system — SLIME_TRANSFORMATION_SYSTEM_1

_Design brief, 2026-09-10, Fable pass (backgrounded from BENCH per
`infrastructure/agents/Agent_Policy.md`). This doc **specifies**: no XML, no C#, no
art. Format precedent: `creatures/RUT_hydrocarbon_ecology_commission.md`. Every rule
INVENTED here rather than derived from a ruling, sheet law, or measurement is flagged
**[INVENTED]**._

**The ruling this executes (owner card, 2026-09-10):** the Slime — flagship biome,
cast of 6 — gets its ambient density from a **transformation system, not new
species**: *"visitors get transformation states: the biome slowly slimifies what
enters, and ambient density comes from half-absorbed versions of other biomes'
creatures."*

**Frozen-sheet posture:** `biomes/the_slime.md` is FROZEN
(`BIOME_FREEZE_FABLE_REVIEW_1`) — amendments add detail, never change a ruling. This
brief changes nothing: the §3 slimification ruling ("unprotected organic life in
contact converts in **~1 week**"), ban 5 (every resident resistant-or-transforming),
ban 1 (no sentience), ban 7 (the disarmed war-legacy split), and the Rot-injection
cure are all already ruled. This brief is the detail layer those rulings owe — it is
the design half of the sheet's Owed "engine feasibility pass: slimification hediff +
~1-week clock."

---

## 0. The system at a glance

| piece | what it is | engine shape |
|---|---|---|
| `RUT_Slimification` | one hediff, four stages, severity 0→1 over the ruled ~7 days | HediffDef, stages in XML |
| the driver | slime-biome maps apply and advance it on every unprotected organic pawn | C# — SPIKE A (§6) |
| the look | one shared green-tint + drip overlay, reused across every species | hediff render-node graphics — SPIKE B |
| ambient density | other biomes' creatures on the Slime's wildAnimals list, spawning pre-staged | roster edit + SPIKE C |
| the exit | stage 4 dissolution: no corpse, a smear, the genome enters circulation | SPIKE D |
| the cure | the ruled Rot-derived toxic injection, any stage before completion | item + hediff removal, XML-mostly |
| the demonstrator | GR_Chickenrabbit, renamed, living at stage 2 permanently | §5 |

**What this is NOT (the Contagion distinction, named):** the Contagion's Red Goo
**generates** — it buds the Unfinished from its own tissue, grows eyes on what it
takes, and its ocular takeover converts ground and trees into more watching weapon
(`biomes/the_contagion.md` §4: the goo "buds new forms every Bloom," the jellies are
"the Contagion's sensory organ"). The Slime **archives** — it buds nothing onto you,
grows no eyes, converts nothing to its cause. A slimifying creature keeps its own
shape, its own temperament, its own species-read to the end; it is being *copied
out*, not *recruited*. Contagion: the weapon still making forms. Slime: the library
filing them. The visual grammar enforces it: slimification art is **film, tint, and
drip — never eyes, never buds, never new limbs** (new-limb chimerism is the
Contagion's register and the Slime's own trace-tail experiments', not the visitor
ladder's). And slimified creatures **never gain hostility** — using what it reads as
a weapon would re-arm the disarmed weapon (ban 7) and grant it intent (ban 1).

---

## 1. The mechanic — the stage ladder

One hediff, `RUT_Slimification`, severity 0→1.0 across the ruled ~7 days on-biome.
Stage names are the player-facing vocabulary. **[Stage count, boundaries, and all
numbers INVENTED; the 7-day total is ruled.]**

### Stage 1 — TOUCHED (severity 0–0.2, ~0 to 1.5 days)

- **What it is:** a wet film. The Slime has noticed you.
- **Stats:** moving −5%. Nothing else. **[INVENTED]**
- **Visual:** the shared overlay at low alpha — a sheen, readable on inspection,
  invisible at zoom.
- **Behavior:** unchanged.
- **Reversibility:** fully self-reversing — severity decays off slime terrain
  (leave the biome, or even camp on the ruins' hard floors **[INVENTED: the
  hard-floor refuge; flagged, it gives bases a reason to exist here]**).
- **Player read:** a health-tab entry with the clock visible. The alert fires here
  for player-owned pawns.

### Stage 2 — SLICKED (severity 0.2–0.5, ~1.5 to 3.5 days)

- **What it is:** the film has soaked in. Green shows through the skin; the reading
  has reached tissue.
- **Stats:** moving −15%, manipulation −10%, sight −10% (the ruled slime-in-eyes
  register, made chronic). **[INVENTED values]**
- **Visual:** full green tint + light drip overlay — the TeratogenicOriginator
  "tint green" ruling's grammar, applied as the whole ladder's art language.
- **Behavior:** unchanged — a slicked predator still hunts, a slicked herd still
  grazes. The biome stays alive-looking; that is the ambient-density point.
- **Reversibility:** no longer self-reversing off-biome (severity holds, does not
  decay); the **Rot injection** (ruled, sheet §3) clears it. **[INVENTED: the
  holds-off-biome line — it makes the injection matter and caravan passage risky]**
- **Player read:** a tamed animal reaching stage 2 is the "spend the injection or
  write it off" decision.

### Stage 3 — HALF-ABSORBED (severity 0.5–0.9, ~3.5 to 6.5 days)

- **What it is:** the owner's phrase, literally. Translucent in patches; the
  creature is partly an entry already.
- **Stats:** moving −40%, consciousness −20%, **pain ×0** — the Slime damps what it
  reads; the creature stops suffering, which is worse to watch. **[INVENTED]**
- **Behavior:** **placid.** It stops fleeing, stops hunting, drifts. NOT manhunter,
  NOT hostile, ever — see §0's ban-7 line. The uncanny stillness is the fear, not
  an attack. (Mental-state suppression at a stage may need a flag — build
  verification, §6.)
- **Butchery:** yields raw slime in place of most meat fraction — the flesh is
  already goo. **[INVENTED]**
- **Reversibility:** injection only, and it leaves scars — permanent small stat
  debuff, "read-marks." **[INVENTED, flagged: pure design choice, cut freely]**
- **Player read:** this stage IS the ambient density. Half-absorbed versions of
  other biomes' creatures standing in the fields — the biome's signature image.

### Stage 4 — RETURNED-TO-FLOW (severity 1.0, day ~7)

- **What it is:** dissolution. The pawn dies with **no corpse**: a smear of liquid
  slime terrain and a few stacks of raw slime where it stood. The genome enters
  circulation.
- **The library hook [INVENTED, flagged as owner option]:** a species that has
  returned-to-flow on the player's map becomes *availability lore* for the gene
  machine's curated target list — the machine's flavor text can name what the
  player watched dissolve. Zero mechanics required; one line of registry flavor per
  dissolution event sells the whole biome ("Entry recorded: dromedary").

**Resistance gate (ruled):** pawns carrying the mycoid-symbiote hediff or the
Slime-resistant gene (sheet §3) never receive the hediff. Residents split into the
**resistant band** (Green Goo by identity; the acanthamoebas as immune-system
champions; OvergrownColossus and TeratogenicOriginator get their resistance lines
written per ban 5 — one sentence each, owed at the sheet) and the **transforming
band** (§5's demonstrator).

**What the player fears, summarized:** not an attack — a clock. The biome never
raises a hand; it just starts counting the moment anything organic steps on it, the
count is visible in the health tab, and the only clean exits are early departure or
a deliberately toxic injection. The eating-slime cure (ruled) starts the same clock
— the wondrous and the fatal are one mechanism.

---

## 2. Honest engine scoping — what exists, what needs the spike

Nothing below is promised free. Closest real mechanisms, cited:

| need | closest existing mechanism | verdict |
|---|---|---|
| hediff with stages, stat mods, painFactor, capacity mods | vanilla HediffDef stages | FREE (XML) |
| apply + advance a hediff on every exposed pawn, map-conditioned | **toxic fallout** (GameCondition advancing ToxicBuildup on exposed pawns) and **Biotech pollution** (polluted-terrain toxicity); Anomaly's progressive hidden infections (metalhorror) are the stage-gated-reveal precedent; VFE gas hediffs are the apply-on-contact precedent | **C# — SPIKE A.** No vanilla route ties a permanent condition to a *biome* with a terrain + resistance gate |
| creature-visible transformation art | **1.5 PawnRenderTree**: hediffs can attach render nodes with graphics (Anomaly's flesh/tentacle parts) | **C#-adjacent — SPIKE B**: the mechanism exists; severity-staged overlay graphics on ANIMAL bodies, scaled per body, is the part to prove |
| wild spawns arriving pre-staged | none — PawnKindDef carries no starting hediffs | **C# — SPIKE C** (small Harmony postfix) |
| death-without-corpse + smear | boomalope's custom deathAction worker; Anomaly dissolution effects | **C# — SPIKE D** (small) |
| the injection item | vanilla drug/serum administration (Anomaly serums) | XML-mostly; administration route verified at build |
| other biomes' creatures spawning here | wildAnimals lists take any PawnKindDef | FREE (roster edit) |

🔴 House rule carried: never guess a field — every class and field name above is a
direction, and the build seat verifies the exact def shapes against RimSage before
XML. The donor's own slime-in-eyes terrain attack (sheet, taken in) is prior art
that this biome's terrain already acts on pawns.

---

## 3. Which species — the visitor set

The density carrier is band (a); the ladder applies to all four bands.

- **(a) Wild-spawn visitors** — other biomes' creatures added to the Slime's
  `wildAnimals` at visitor commonality, spawning pre-staged (SPIKE C) so the fields
  read half-absorbed from the player's first minute. Source biomes, in adjacency
  order: **wasteland first** (CONFIRMED neighbor — Glass Reach and Chalk Marches
  are wasteland basin regions, sheet §0) — its post-churn cast of 12 is the natural
  donor pool, and its "wretched-many" register (sick, cornered, scavenging bodies)
  is tonally perfect arriving here to be read; then desert-edge strays and
  terminator-strip neighbors **[adjacency beyond wasteland UNVERIFIED against the
  canon map — verify at the sitting]**. Target: **8–12 visitor species**, exact
  picks at `BIOME_FAUNA_ASSIGNMENT_SITTING_1` (the sheet's Owed roster
  reconciliation — this brief deliberately names the mechanism, not the picks).
  Key property of this design: **with the shared overlay (§4), adding a visitor
  species costs zero art**, so the sitting can size the list freely.
- **(b) Caravan and trade animals** passing through — the ladder applies; a trade
  caravan that lingers leaves lighter than it came. Scope question flagged (§7 Q5).
- **(c) The player's own animals** — full ladder, the stage-2 injection decision.
- **(d) Colonists and humanlike visitors** — 🔴 **THE SCOPE GATE. Flagged as an
  owner call, not decided here — §7 Q1.** Note only that the frozen sheet's text
  ("unprotected **organic life** … converts in ~1 week") already includes humans on
  its face; the open question is presentation and endpoint, not whether.
- **NOT visitors:** the trace-tail experiments (sheet §4) are the database's own
  *outputs* walking around — the opposite register. They never carry the visitor
  ladder; conflating the two would blur the Contagion distinction (§0).

---

## 4. Art strategy — one overlay, every species

**Recommended: the cheap route.** One shared slimification overlay set — green tint
plus a drip/film graphic — attached by the hediff's render node, reused across every
affected species, scaled to the wearer. Precedent is the owner's own ruling grammar:
TeratogenicOriginator entered this cast as "tint green" — tint-level art already
satisfies the register here.

**Sprite cost, counted against the realistic visitor list (8–12 species, §3):**

| route | sprites | scaling behavior |
|---|---|---|
| **shared overlay (recommended)** | 2 overlay states (slicked, half-absorbed; touched = slicked at low alpha) × 3 size buckets (small ≤0.5 bs / medium ≤1.5 / large) × 3 rotations = **18 sprites, flat** — plus the Chickenrabbit bespoke pass (§5, ruled anyway, ~3–6) ≈ **21–24 total, forever** | flat: species #13 costs nothing |
| bespoke per-species | ~10 species × 3 rotations × 2 stages = **60+**, before the list grows | linear: every added visitor is 6 more sprites |

The bespoke route also fights the system's own point — the ladder exists so the
biome does NOT commission per-species content. Bespoke slimified art is reserved for
exactly one creature: the demonstrator (§5), where it doubles as the calibration
target the overlay's tint values and drip shapes are matched against.

**Overlay design notes:** amorphous film and drips, deliberately loose-fitting
(reads on any silhouette in a bucket); palette inside the sheet's §9 language —
translucent greens and ambers, specular ("the one biome that shines by day"); stage
3 adds translucency patches. Never eyes, never buds (§0). ⚠️ SPIKE B decides
whether full-body green tint comes free from render-node color or needs the tint
baked into the overlay texture — the 18-count survives either answer.

---

## 5. GR_Chickenrabbit — the first native demonstrator

Both round-2 rulings on it fold in here rather than running as a stray art task:

- **The rename (ruled — "chicken+rabbit fails recognizability"):** label-level
  rename with this system's art pass; defName/packageId migration rides
  `NAMING_SCHEME_EXECUTION_1` per standing rule (no renames ahead of it).
  Candidates **[INVENTED — owner picks one, or coins his own]**: **ollop** /
  **murrel** / **glib**. Soft-bodied vowel-led register per `Alien_Bestiary.md` §1;
  collision-sweep owed at build.
- **The slimified art pass (ruled):** executed as this system's ONE bespoke piece
  (§4) — the demonstrator wears the transformation natively and its art calibrates
  the shared overlay.
- **The role:** the cast's **transforming band** of one (ban 5 satisfied by
  transformation, not resistance): a small fast breeder living in permanent rolling
  conversion — it multiplies faster than the Slime finishes reading it, so its
  population stands at equilibrium around stage 2, every generation partly slicked,
  the oldest individuals half-absorbed. The one resident that demonstrates the whole
  ladder to a player before any visitor does. Its trace-tail lore keeps: a
  recombinator's chimera IS the living database's idiom — the database's favorite
  entry, checked out again and again. **[INVENTED: the equilibrium framing; its
  residency and both rulings are prior.]**

---

## 6. The spike list — exactly what C# is needed, sized

Sizing per the twinkle-spike precedent (`TWINKLE_FLORA_SPIKE_1`): prove the pattern
on ONE def, measure tick cost, report — timeboxed, no production wiring.

| spike | proves | size |
|---|---|---|
| **A — SLIME_LADDER_SPIKE** | biome-conditional driver: MapComponent (or biome-bound GameCondition) applies `RUT_Slimification` to unprotected organic pawns on slime maps, advances at 1.0/7 days, resistance gate, off-map halt/decay per stage (§1). Rate-limited scan — measure tick cost on a 96-tile-biome map's pawn count | **M** (1–2 sessions). The core; B–D ride it |
| **B — SLIME_OVERLAY_SPIKE** | hediff render-node overlay on an ANIMAL body: one overlay graphic, severity-staged swap, drawSize-scaled, tint question answered (§4) | **S** |
| **C — SLIME_SPAWNSTAGE_SPIKE** | wild spawns arrive pre-staged: Harmony postfix on wild-animal spawn rolling stage 1–3 for listed visitor kinds | **S** |
| **D — SLIME_DISSOLVE_SPIKE** | stage-4 deathAction: no corpse, slime smear + raw-slime yield, one registry-flavor message | **S** |
| **E — flow-drift (OPTIONAL, cut-able)** | stage-3 placid wander biased toward the flow — only if playtest says stillness needs motion | S, deliberately unscheduled |

Non-spike build work: hediff XML (stages/stats), injection item + administration
route verification, wildAnimals roster edits, ban-5 resistance lines for the two
arrivals still owing them, the overlay sprite set (18), the Chickenrabbit bespoke
pass.

---

## 7. Open questions — the owner's, not ours

1. 🔴 **COLONIST TRANSFORMATION — the scope gate.** The frozen sheet already says
   unprotected organic life converts; the call is the endpoint for humanlikes.
   **Option 1, full ladder:** colonists ride all four stages to dissolution.
   Strongest horror, mechanically honest, makes the resistance economy (symbiotes /
   the gene) genuinely mandatory — but an ambient permadeath clock on colonists is
   the harshest mechanic on the planet, overlay-on-apparel art is messy, and a
   missed alert costs a colonist to weather. **Option 2, capped at stage 3:**
   colonists bottom out half-absorbed and DOWNED — a rescue-and-inject window,
   never ambient death; dissolution stays animal-only. Gentler, still frightening,
   cheaper (no humanlike stage-4 art/edge-cases) — but the sheet's "converts" is
   then softened for exactly one taxon, and the gene machine's coma flow already
   proves the owner will put colonists in the Slime's hands. **Not decided here.**
2. **Chickenrabbit's new name** — ollop / murrel / glib, or the owner's own coin
   (§5).
3. **The library hook** (§1 stage 4): dissolved species named in gene-machine
   flavor — keep or cut? [INVENTED]
4. **Manhunter: recommended NEVER** (ban 1 + ban 7 reasoning, §0) — confirm, since
   "no hostile transformation ever" is a strong standing rule to hand FOUNDRY.
5. **Trade-caravan animals** (§3b): full ladder while visiting (funny, cruel,
   faction-goodwill implications), or exempt NPC-owned animals?
6. **Stage-3 injection scars** ("read-marks", §1) — keep or cut? [INVENTED]

---

## 8. Sources read for this brief

- `biomes/the_slime.md` (FROZEN sheet — §3 slimification + cure rulings, ban 1/5/7,
  §4 cast bands, §9 art language, Owed feasibility line)
- `biomes/the_contagion.md` (§4 Red Goo / the Unfinished — the distinction in §0)
- `review/round2/biome_findings.md` (the_slime: cast 9→6, the two findings and the
  density opportunity this executes; wasteland: post-churn cast 12, wretched-many)
- `review/round2/move_mapping_v2.md` (departure/arrival provenance)
- `biomes/rosters/the_slime.json` (pre-churn roster; bands; Chickenrabbit lore line)
- `creatures/RUT_hydrocarbon_ecology_commission.md` (format precedent; the
  never-guess-a-field house rule; spike-sizing convention)
- `Alien_Bestiary.md` §1 via precedent citations (naming grammar),
  `design/NAMING_SCHEME_PLAN.md` (tier grammar, migration rule)
