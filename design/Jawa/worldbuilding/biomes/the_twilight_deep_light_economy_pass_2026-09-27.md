# The Twilight Deep — light economy & Compact pass (2026-09-27)

## Ruled 2026-09-27

Owner, typed: **"The Compact does NOT sell light, that's not a mechanic we accepted.
Remove."** Scope, ruled by card the same sitting: the whole paper layer is out — lease
paper (`RM_SkylightRight`), chart paper (`RM_WellChart`), the claim buoy (`RM_ClaimBuoy`),
the poaching-standing code — wells are free ground, the Compact are keepers and neighbours
with no commerce, and the sun-sphere is obtained without buying from anyone (the research
plus a wild seed). Everything ruled as physics — the weekly drift and its stages, the
warning reads, the mobile chained constellation and its ~6/~10 cap, minifiable cages and
lamps, chains, the sun-sphere line — stands unchanged below; code removal is filed as
`TWILIGHT_TENANCY_PAPER_REMOVAL_1`.

_DESIGN pass (Fable subagent, 2026-09-27) on the light-and-Compact layer, consolidating
the TWILIGHTSEA_FLOOR_PASS_1 rulings — week-scale drift, cheap lamp moves, the mobile
constellation — into one coherent spec. Companion to `the_twilight_deep.md`
(frozen sheet), `the_twilight_deep_content_2026-09-26.md` (content drop, "content doc"
below), and `the_twilight_deep_danger_pass_2026-09-27.md` (RULED, "danger pass" below).
Nothing here is an owner quote unless marked; the ruled facts this pass builds on are
recorded on the ledger item and cited by substance. Nothing here is filed work._

**The one sentence this pass serves** (owner's load-bearing insight, typed at the
sitting): the light moves, *"and this explains the movable chained floating fields."*
The whole layer is one arc run three ways: **the sky's light drifts weekly (drift), the
player's fields and lamps are walked to follow it (chase), and the grown light frees them
from both (independence)** — *early game you chase the light, late game you make it and
stop chasing.*

**Ruled facts taken as fixed** (all on `TWILIGHTSEA_FLOOR_PASS_1`, 2026-09-26/27):
skylight drift is ~one week, superseding years-scale, ban 5 intact · cultivated lamps are
chainable and moved as a cheap haul job, minutes · the useful lamp count must stay SMALL
(a handful, not twenty) — a binding balance constraint, not a detail · lid-dark fires
from the gardener's passes, no timer · the suulk grazes lamps including the sun-sphere, slowly and loudly · the vaulisk
counterfeits the gold lamp, one per map, tell readable · light-attraction is CUT for the
Twilight · the pane can kill · the bank works are the immobile counterweight prize · the
held-open skylight is OUT (nothing reaches the waveglass — it is a sky) · plain Plant
defs work on the seabed layer (measured; the earlier "custom sessile thing" claim was
wrong and corrected).

## 1. The skylight clock

The week-cadence is the biome's metronome, and it must be ONE system, not three. The
content doc owed a drift `MapComponent` (§6.3); the danger pass re-parameterised it to a
week (D5) and gave the gardener the firing hand (D9/C7). This section merges them.

### 1.1 One component: the well-ledger

**`RM_MapComponent_WellLedger`** owns every skylight on the map: its position, its
**age**, its **stage**, and the map's target well count (3–6, from map size).
Everything else in this spec — warning stages, gardener hooks, lid-dark's dawn drift —
is a call into this one component. No second timer exists anywhere.

A skylight's life is **5–9 days** (rolled at opening, never shown as a number):

| stage | duration | what the player sees |
|---|---|---|
| **opening** | ~half a day | a new gold column fades in over hours; the rim above is bright pale new growth; no kelp yet, but the pallu arrive first — the Compact's own tell |
| **standing** | days 1 → N−1.5 | full radius, full gold; kelp grows, nets work, the ground is anyone's who stands on it |
| **waning** | the last ~1.5 days | **the sky-read**: the pale rim above thickens and dulls (the lid healing over), the glower's radius steps down ~20% per half-day and its colour cools off gold, the pallu thin out, the breathing pulse slows. Fully legible from the floor, no letter needed to notice |
| **closed** | — | the column is gone; the kelp stand dies over a season; the cells revert to the dark between, which is the loohn's and the vaulisk's ground (danger pass D5) |

The ledger keeps the OPEN count roughly constant: a well closing schedules a well
opening elsewhere within ~a day, on high dry ground, never on a channel bed (the
dressing genstep's siting rules). So the map always has light — just never where it was.

### 1.2 Warning stages — two, both diegetic

1. **The sky-read** (free, always): the waning rim and the stepping radius, above. A
   player who looks up gets ~1.5 days of warning for nothing.
2. **The stake in the ground** (positional): a letter fires ONLY when a waning well
   contains something the player owns — a sown plot, an anchored cage or lamp.
   *"The well over {ground} is closing."* No spam for wells the player never
   touched.

### 1.3 Who fires a drift — the gardener's hand on the ledger's clock

Ruled coherence (C7 + the week ruling): **the ledger is the clock; the gardener is the
hand that moves it.** Three triggers, one code path (`WellLedger.AdvanceWell(...)`):

- **Base aging** — the 5–9 day life above, running always. Drift never *needs* an event;
  a colony that never sees the gardener still lives on a weekly clock.
- **A gardener pass** (`RM_GardenerOverhead`, the five-beat sequence) — on a fraction of
  passes the sequence's beat 2–4 window ADVANCES one well: a waning well closes now, or
  a scheduled opening happens now, in front of the player. Watching the shadow and then
  watching a shaft go dark is the roof being tended (content doc §7.3 Grade A, kept).
- **Lid-dark's dawn** (danger pass D9) — when the lid-dark day ends, the ledger runs one
  forced drift check: *the lid healed differently than it was*. Lid-dark itself fires
  from the pass sequence (a fraction of passes escalate — RULED, no timer), so the whole
  chain is gardener → pass → (sometimes) lid-dark → dawn drift, with the base aging
  underneath. No piece has its own clock.

### 1.4 The engine trap, flagged where it bites

🔴 **Never implement any of this as sun/sky darkness.** The cached plant growth-rate
calculator assumes surface sunlight for the map's tile, so a depth-darkening
`GameCondition` will NOT reflect in cached plant growth — a lid-dark built as a sky
condition would leave kelp growing merrily in the black. The skylights are **glow-grid
light** (`CompGlower` on the `RM_Skylight` thing), and plants gate on `growMinGlow`,
which reads the glow grid live. Lid-dark = every skylight glower driven to ~0 by the
ledger for a day (plus the sky-colour weather for looks); the growth pause then falls
out of `growMinGlow` for free, and the sky colour is only ever cosmetic. The same rule
covers the waning steps: radius steps are real light changes, so kelp at a dying well
slows before it dies — correct, and free.

## 2. The mobile constellation

His insight fuses the cages and the lamps into one picture: **a small constellation of
floating things — two or three cage fields, a handful of lamps — that the colony
re-arranges every few days as the wells walk.** This section makes the move cheap (as
ruled), the picture legible, and the count small (as ruled) by mechanism.

### 2.1 What a move IS — cheap haul, minutes, vanilla verbs

Every mobile piece (sphere cage, cube cage, and every clipped lamp of §3) is a
**`minifiable` building with near-zero uninstall work**. A move is: unclip (an
uninstall job, seconds), carry (a haul), re-anchor (a reinstall, seconds). One colonist,
one trip, minutes — the ruled cost, on shipped verbs, no new movement system. The chain
is drawn from the building to its floor anchor (a link graphic / corner chain in the
cage art, content doc §13.1); a "constellation" is the player's arrangement, not a
system object — there is no group-drag, and none is needed at this piece count.

- **In transit it is dark and dumb.** A minified lamp does not glow and a minified cage
  does not grow. Deliberate: the move has a cost you can see (a dark lamp crossing the
  floor is a lovely beat), and it closes every "carry the lit lamp as a torch"
  degenerate loop — the carryable light is the lamp-bladder item, which rots (§6.4 of
  the content doc), never the clipped lamp.
- **Cages keep their crop.** Vanilla minification would kill a grower's plants, so the
  cage carries a small comp that snapshots its plants (def, growth) on uninstall and
  respawns them on reinstall — the one C# this verb needs (tiny). Growth pauses in
  transit; a long-hauled crop is a slightly later crop.
- **Anchoring rules:** a cage anchors on any floor cell including over the channel bed
  (its vertical payoff, ruled ground); a lamp anchors anywhere standable.

### 2.2 🔴 The cap — why the constellation stays a handful, by mechanism

The ruled constraint: cheap × many = micromanagement tax, so the USEFUL count must stay
small. Three layers, one hard and two ecological — and one deliberate refusal:

1. **The hard cap: the tether-chain.** Nothing is mobile without a **`RM_TetherChain`**
   clipped to it — the Compact's showcase alloy-and-bladder chain (content doc §13.5),
   **uncraftable until the late research, and reaching the colony in ones**: a visiting
   trader stocks one or two, restocking slowly. A chain is recovered whole
   when unclipped, so the colony OWNS N chains and chooses each week what hangs on them
   — the constellation is exactly as big as the chain drawer, and the chain drawer
   grows slowly by trade until the research opens crafting. **Default reachable count ~6** (2–3 cages,
   3–4 lamps); the late-game research raises the ceiling the player can *craft* toward,
   by which point the sun-sphere has already ended the chase (§3). Mod Setting:
   chain availability (scarce / standard / plentiful).
2. **The ecological ceiling: suulk pressure scales with the constellation.** The suulk
   incident's frequency reads the count of player-owned mobile glowers: at a handful,
   the ruled several-day cadence; each lamp past ~6 shortens it. Carpeting the floor in
   lamps is planting a grazing meadow (danger pass D2's fiction, made the tuning knob)
   — the sea itself eats the tax the player tried to pay. One line in the incident
   worker; no new system.
3. **The free physics: glow does not stack.** Overlapping glowers buy nothing — N lamps
   light at most N separate pools, and pawns need only so many lit workplaces. Past the
   handful, marginal utility falls off a cliff on its own; the design only has to not
   fight it (no lamp buffs, no per-lamp auras, nothing that rewards density).
4. ⛔ **The refusal: no feed chores on the small lamps.** A per-lamp hunger clock was
   considered as the cap and rejected — feeding six lamps weekly IS the micromanagement
   tax the ruling forbids, wearing a fiction. The noothelm and hoolimbre clips are
   sealed living things like the aluun pane: they keep. Only the sun-sphere eats
   (§3.1), because it is one building, the colony's centrepiece, and its feed is the
   independence arc's cost — one bill, not six.

### 2.3 What stays put — the counterweight, for contrast

The ruled immobile prize is the **bank works** (river geography, stake-line held
against the current, one breach takes it downstream — scoped with the channel current
as one piece, not this pass's to re-design). This spec touches it once: the bank works
are **light-independent wealth** (silt fertility, not glow), which is exactly why they
anchor the mid-game while the constellation chases the wells — the player always has
one thing the drift cannot tax and one thing the river cannot chase. The two halves
teach each other.

## 3. The living light line

The grown lights are the arc's third act: *late game you make it and stop chasing the
sky.* Three stages, each a real step in cost, mobility and light —
and one mechanism that lets any of them (and anything else that moves) carry its glow.

### 3.1 The progression, staged

| stage | what | light | cost to get | feed | risk | when |
|---|---|---|---|---|---|---|
| **1 — the bladder** | `RM_LampBladder` (hoolimbre harvest) | radius 2–3, rots in ~6 days | pick it, day one | none — it dies instead | none worth naming | landing week: the torch you chase the light with |
| **2 — the clipped lamp** | noothelm bulb / hoolimbre string on a tether-chain (mobile, §2) | radius 3–5, permanent | grow or harvest the plant + **one chain** (trade, or the late-research craft) | none — sealed living clip (§2.2-4) | the **suulk** grazes it; the **vaulisk** counterfeits it; a pane can crush it | the chase economy: lamps walked well to well |
| **3 — the sun-sphere** | `RM_SunSphere` culturing the ollumin | **sun-strength**, radius ~6 — grows crops without any well | the research + a wild seed (a pallu or a bladder — the sea's, free) | **fed**: any raw floor food, days of grace when starved, dims to a seedable husk, never explodes | the suulk grazes it too, *slowly and loudly* (RULED C4) — the dearest lamp needs a guard, not an exemption; starvation if the floor larder fails | independence: farm anywhere, chase nothing |

The stages don't obsolete each other: bladders stay the expedition light, clipped lamps
stay the constellation's working gold, and the sphere is the one sun. Nobody sells
light, and nothing on this line is bought from the Compact — the seed is always the
sea's, which is why the arc reads as learning the biome, not buying it.

**Growth is brightness** (content doc §13.2, kept): the sphere's stages ARE radius
steps — seeded dark → culturing dim → mature sun. You watch your light grow, over days;
the suulk arriving mid-culture is the arc's best bad night.

### 3.2 The moving-glow mechanism — one comp for everything that moves

The content doc measured the gap: `CompGlower` registers its light at the position it
was lit and never re-registers on movement — a walking glower strands its light.
**MEASURED this pass: the fix's API is already verified in our own tree** —
`RM_Comp_WarblingGlow` (`src/RimMandrake/EnvironmentalHazards/Source/RM_Comp_WarblingGlow.cs`,
the Sump gaslight) reads sibling-comp glowers, confirms `GlowRadius`'s setter only
stores the value, and calls `ForceRegister(map)` explicitly on change, per CompGlower's
own public API. The moving version is the same call on a different trigger:

**`RM_CompGlowerMobile`** (new C#, tiny, in `mandrake.rm.terminalbiomes`, shared by
every sea): a `ThingComp` that rare-ticks, compares `parent.Position` to its last
registered cell, and on change de-registers/`ForceRegister`s the sibling glower. That
one comp serves **every mover**: the glowing fish bodies (niim's dot-line shoal,
liiru, kiruun patches), a tame liiru following its handler, the kept waelune rolling
through the yard, the drifting orrilith on a channel, and any future glowing creature
on any floor. Build it before the first glowing creature ships (the content doc's own
bar), and the lamp economy gets it for free where it needs it.

- **The clipped lamps do NOT need it** — they are buildings that are dark in transit
  (§2.1), which is the cheaper and better answer for them.
- **The breathing pulse** (every living lamp breathes; the vaulisk's steady counterfeit
  is the tell — RULED C3) is `RM_Comp_WarblingGlow`'s exact job. Reuse it: either lift
  the comp up to a shared home or ship a sibling with the same verified pattern in
  terminalbiomes; do not write a third glow animator. The vaulisk simply doesn't carry
  it — absence of code as the monster's tell.

## 4. Wells are free ground

There is no tenancy layer. A well belongs to whoever is standing under it: the player
sows, hunts, gathers and anchors in any well at will, pays nobody, and holds nothing
but ground — when the well closes within the week, everyone moves on, and the drift
itself is all the turnover the sea needs. The Compact work wells too: their cast walks
stakes out to the shafts they fish and weeds them daily, and whatever books they keep
about the sky are **their fiction and their hands** — visible daily work and lore, never
a paper, permit, forecast product, sanction or price shown to the player. They are
keepers and neighbours, never landlords and never sellers; their goodwill is plain
vanilla faction goodwill, gating nothing in this layer.

## 5. The gardener's events — one family, one face

Everything the sky does has the same author. The gardener's agency stays exactly what
was ruled acceptable — *keeping skylights open* — and every event below is that work
seen from underneath, in escalating grades of the same pass. Placid throughout: it
never targets, never responds to the player, never descends because of anything below.

| grade | event | cadence | what it is |
|---|---|---|---|
| **0 — passing shadows** | `RM_PassingShadow` (ummarel rafts, far shapes) | frequent, small | the ambient preview: the sky has traffic; a darker patch crosses a shaft. `CompAffectsSky`, no C# (content doc §7.2) |
| **1 — the pass** | `RM_GardenerOverhead`, the five-beat sequence (booming → little light → panic → the rain → overdrive) | one in a few days | the marquee (content doc §13.4, unchanged). The whale-shadow IS the preview beat of everything below it |
| **2 — drift-firing** | a fraction of passes advance the well-ledger (§1.3) | inside grade 1 | the pass *does* something to the map's light: a waning well closes now, or an opening lands now — the roof visibly tended |
| **3 — lid-dark** | a fraction of passes escalate: the sky goes out for ~a day | rare, gardener-fired, **no timer** (RULED C7) | danger pass D9 unchanged; at dawn the ledger runs the forced drift check |
| **the seam** (new, small) | after any grade ≥1 pass, a line of fresh veil-fall flakes lies across the floor along the pass's track, with an orrilith or two in it | inside grades 1–3 | the tending leaves a wake you can walk and glean — the gardener's only "gift", which is just its housekeeping falling off. Ties the pane/rain economy to the pass family with one filth-scatter line in the incident worker |

**Coherence rules:** grade N always contains grades below it (a lid-dark day began as
a pass and had its booming and its rain); the well-ledger is the only state any grade
touches; heavy shed (D1 panes, D8 deck-loading) skews toward pass days and waning
wells, so the whole sky economy reads as one weather system with one animal in it.
Ban 2 served everywhere: no grade exists without the gardener, and killing the last
gardener is already ruled to kill the roof — these events are what that sentence
costs the player who imagines trying.

## 6. The content doc's open questions — dispositions

Checked against the ledger-ruled facts (week drift, cheap moves, small constellation,
lid-dark/C1–C7) before treating any as open:

| Q | subject | disposition |
|---|---|---|
| **Q3** | niim vs noolim — two shoals split by light, or one | **RULED at the 2026-09-26 sitting (§8): TWO, split by light** — niim the lit shoal of the shafts, noolim the dark shoal of the between; the lit shoal is `RM_CompGlowerMobile`'s showcase (§3.2) |
| **Q7** | whale shadow Grade A now, Grade B after a mockup | **already-ruled in substance + designed-here.** The second drop specified the five-beat sequence (supersedes plain Grade A); §5 files the family around it. Grade B's moving-shadow art stays gated on a mockup **with him watching** — that is a joint session, not a card |
| **Q8** | skylight rights: goodwill-only sanction, expiring item | **DEAD — removed by the 2026-09-27 ruling.** The whole paper layer is out; wells are free ground (§4). No rights, no sanctions, no card |
| **Q13** | cage chained down to a floor anchor vs hung from a surface float | **discharged by the mobility ruling.** A cage that is unclipped, walked and re-anchored anywhere (including over the bed) requires the floor anchor; a surface-float hang cannot be walked and reaches through the waveglass fiction besides (the lid is a sky; nothing of ours touches it). Anchor it is |
| **Q14** | walking under a cage | **already-ruled in substance.** His own sentence is the ruling: *"the floating farming doesn't use up surface space because it floats above you."* Passable-beneath ships; the occupy-cells variant stays as the Mod Setting the content doc already proposed. No card |
| **Q15** | living decor neglect | **designed-here, low stakes.** Never dies by default (*"easily"* is his word); the stricter "needs light" behaviour ships as an off-by-default Mod Setting. Reversible in one sitting if he ever cares; not worth a card now |
| **Q16** | sun-sphere fed vs powered | **designed-here** (§3.1): fed, on any raw floor food. Three rulings lean on it — the suulk grazes it *as a living lamp* (C4), the independence arc needs it off the power grid, and the floor-larder-feeds-the-light loop is the biome's economy closing. Powered would break all three. No card |
| **Q19** | techprints: Compact-only sellers, sphere at 2 | **DEAD — overturned by the 2026-09-27 ruling.** The sphere is obtained without buying from anyone: the research plus a wild seed (§3.1). No techprint price, no seller, no card |

(Q2/C1 the sink, Q1 the waveglass, C2–C7 — all already ruled; listed in the header.
The content doc's remaining Qs — Q4 unlimited fishing, Q5/Q6 flora counts, Q10 houses,
Q11 waelune, Q12 settings, Q17/Q18 rain — are outside this pass's territory and
untouched.)

## 7. Engine summary

Searched `src/RimMandrake/` before inventing (this project keeps having already built
things). Found and reused: **`RM_Comp_WarblingGlow` + `RM_CompProperties_WarblingGlow`**
(EnvironmentalHazards — the breathing glow, with the `ForceRegister` API verified
against `Verse/CompGlower.cs`/`GlowGrid.cs` in its own header) · **`Building_GlowTank`**
(LuminousPigment — the culture-in-a-grower pattern the sun-sphere siblings) ·
**`MapComponent_LanternDeepDarkness` / `BiomeGlowPatches` / `GenStep_DeepFloraGate`**
(the glow-gated flora precedents) · vanilla minify/reinstall (the move verb). No
existing chain/tether or moving-glower mechanism exists — those two are genuinely new.

| piece | new C# | size | rides on |
|---|---|---|---|
| `RM_MapComponent_WellLedger` (skylight clock: ages, stages, drift, warning letters, target count, gardener/lid-dark hooks) | **yes** | small–medium | the already-owed drift component (content §6.3) + D5, absorbed into one component |
| skylight waning visuals (rim graphic stage, radius steps, colour cooling) | no | — | `RM_Skylight`'s glower driven by the ledger; `RM_Comp_WarblingGlow` pattern for the pulse |
| lid-dark | no | — | 1 WeatherDef + a ledger call (RULED; danger pass D9). Glow-grid dimming, never a sky GameCondition (§1.4 trap) |
| mobile cages/lamps (unclip–carry–re-anchor) | no | — | vanilla `minifiable` + low-work uninstall/reinstall |
| cage crop snapshot on minify | **yes** | tiny | a comp on the cage growers |
| `RM_TetherChain` economy (the hard cap) | no | — | item + research + trader stock, all XML |
| suulk pressure scaling with constellation size | **yes** | one line | inside the suulk incident worker (`TWILIGHT_DANGER_LIGHTWEB_1`'s scope) |
| `RM_CompGlowerMobile` (glow follows a moving thing) | **yes** | tiny | `ForceRegister` API, already verified by WarblingGlow's header; shared across all seas |
| breathing pulse on lamps + its absence as the vaulisk's tell | no | — | reuse/sibling `RM_Comp_WarblingGlow`; the vaulisk just lacks it |
| sun-sphere (`RM_SunSphere`, fed, growth = brightness) | maybe | tiny | `Building_PlantGrower` + `CompRefuelable` (GlowTank's family); a tiny comp mapping plant growth → glow radius if no shipped hook does it |
| gardener event family incl. the seam | no | — | `RM_GardenerOverhead` (content §13.4) + one filth-scatter line; grades are one worker |

Net-new C# systems this pass adds beyond what the content/danger passes already owe:
**the well-ledger consolidation, `RM_CompGlowerMobile`, the cage snapshot comp** —
everything else is XML or one-line extensions of owed work. 🔴 The one flagged engine trap: cached plant growth rates assume surface
sunlight, so every light effect in this economy must live on the **glow grid**, never
on a sky-darkening GameCondition (§1.4) — this bites lid-dark, the waning steps, and
any future "opacity" weather that hopes to slow the kelp: give it a glower hook or it
does nothing to plants.

**Mod Settings owed by this layer** (per the standing rule): skylight drift on/off +
cadence (week/slow/frozen-for-sandbox) · chain availability scarce/standard/plentiful ·
constellation suulk-pressure scaling on/off · cages passable-beneath on/off · living
decor needs-light off/on · sun-sphere grace period.

## 8. Rulings — 2026-09-26 sitting, both cards answered

Both decisions taken by question card (our wording, clicked, never quoted);
recorded on `TWILIGHTSEA_FLOOR_PASS_1`.

1. **Niim/noolim: TWO, split by light** — niim the lit shoal of the shafts, noolim
   the dark shoal of the between. The overlapping prose in the two live defs gets
   disentangled before the fish-body wave ships, and the lit shoal is
   `RM_CompGlowerMobile`'s showcase (§3.2).
2. **The constellation number: six reachable, ten late-game**, with the sun-sphere
   as the real way past the cap — the design's numbers confirmed as ruled.

Nothing else in this territory needs his word: Q7's Grade-B mockup is a joint session
(not a card), and Q8/Q13/Q14/Q15/Q16/Q19 are dispositioned in §6 under rulings he has
already made.

---

*Nothing above amends the frozen sheet until its sitting; the sheet's ban 5 line
("years scale") is superseded by the ruled week on the ledger and gets its one-line
amendment there, on his word. Vocabulary check: waveglass / the lid / veil-fall
throughout; no mat, no mold; all names invented, `RM_` tier.*
