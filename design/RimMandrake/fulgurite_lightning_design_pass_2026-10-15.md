# Fulgurite and the lightning breaker: a design pass (2026-10-15)

Read-only design pass, BENCH, one Opus 5.5 agent. Nothing in the game or the bridge was touched.

The owner asked, verbatim: *"I also would like an evaluation of the fulgurite -> lightning breaker aspect. It
seems quite tacked on, and it's inexplicable why it's here and nowhere else in the biomes... Do a design pass
with a single Opus 5.5 evaluating the game design nature of this mechanic and whether we should add it
anywhere there's sand and lightning, or just drop it entirely, in terms of how enchanting it will be to the
player."*

## 1. What is actually built

There are two mechanics, and **the code does not connect them.** The only link between them is a sentence of
flavour text.

### Fulgurite (`RM_FE_Fulgurite`)

- **Trigger:** a Harmony postfix on `WeatherEvent_LightningStrike.DoStrike`
  (`src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs`, `Patch_LightningStrike_Fulgurite`). A strike on
  sand-family ground (`RM_FE_Ground_Sand`, `Sand`, `SoftSand`, `RM_DeepSand`) rolls 35% (`fulguriteChance`)
  to drop one fulgurite item next to the impact.
- **Not limited to the Pyrelands.** Since `STILLSAND_GLASS_LENS_CHAIN_1` §10, a strike on any sand anywhere
  rolls, and only the `fulguriteEnabled` toggle governs it. The Pyrelands master switch governs only the
  Pyrelands' own ground. So fulgurite **already appears in every biome that has sand and lightning.**
- **The item:** `src/RimMandrake/Pyrelands/Defs/ThingDefs_Fulgurite/Fulgurite.xml`. A ground resource with
  market value 3, beauty 2 and mass 0.4. Its description reads *"Worthless to sell, satisfying to find."*
- **What uses it:** (a) `RM_MeltFulgurite` at the Stillsand sun furnace, 1 fulgurite → 4 sun glass
  (`src/RimMandrake/Stillsand/Patches/RM_GlassChain.xml`); (b) the Struck Glass rite, which needs a ring of
  fulgurite and is still unbuilt (`PYRELANDS_STRUCK_GLASS_RITE_BUILD_1`, open). **The breaker does not use
  it.**

### The lightning breaker (`RM_LightningBreaker`)

- **Research:** `RM_LightningBreakers` costs 700 and needs Electricity. A `CanStartNow` postfix stops it from
  being *begun* unless the player holds a home map in the Pyrelands (`breakerPyrelandsOnly`, on by default).
  Once begun, it finishes anywhere. **There is no fulgurite step in it.**
- **Recipe:** 30 steel and 20 `RM_GlassSand` (the Stillsand's shovelled sand, not fulgurite) at either smithy
  make a breaker core. The core plus 15 steel builds the breaker, a 1×1 conduit on the Power tab.
- **Behaviour:** a prefix on `ShortCircuitUtility.DoShortCircuit` walks the faulted section of the grid. An
  armed breaker on its boundary trips: it stops carrying power, spends glass sand from a 30-unit hopper, plays
  `Thunder_OnMap`, and sends a "Breaker tripped" letter. Only the faulted side's batteries discharge. The
  player re-arms it with a gizmo.
- **What sets it off:** RimSage, 1.6. The only caller of `DoShortCircuit` is `IncidentWorker_ShortCircuit`,
  the random "Zzztt..." incident. Lightning never calls it. `TryShortCircuitInRain` is a separate path that
  sets off a 1.9-cell flame burst on the device itself and never drains the grid, so the breaker cannot act
  on it. **The "lightning breaker" never meets lightning.**
- **Test footprint:** north-star rows `lightning_breaker.*` (static, ProofGate, ProofTrip), review-save
  KEYSHEET stations 20, 21, 22 and 24, COVERAGE rows 80 to 84, and 58 mentions in the Pyrelands
  validation and northstar scripts. Art still owed: the `_Off` frame and the core's own icon.

### Where it came from

- `design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md` §5. A GPT consult proposed
  **"Branchglass Reclosers"**. In that version you studied enough fulgurite to reveal the research, and
  fulgurite's branching fractures *were* the fuse, so the chain from fulgurite to breaker was real.
- The owner took it and revised it, typed: *"The Lightning breakers is a neat idea. They should be made of
  metal and sand in a recipe in the forge. Only learnable here because of the frequent lightning and sandy
  soil. Desert sand works just fine too once you know how"*.
- The spec carried a hint: *"studying fulgurite where it fell is the natural trigger."* The build
  (`PYRELANDS_LIGHTNING_BREAKER_BUILD_1`, closed) took the cheaper gate instead: owning a home map in the
  biome. That step cut the fulgurite out of the chain.
- **Why it is here and nowhere else:** every biome is scored against the bedazzle marks. Mark 2 is a
  "discoverable technology": learned in one biome, used everywhere. Other biomes have their own: the Forge's
  spunstone, the Greentide's stellock lace, the Abyss's fold-lamp. The breaker is the Pyrelands' mark 2.
  Being unique to one biome is the rule working as designed, not an accident. Its weakness is that the
  biome's fiction never reaches the player.

### Overlaps elsewhere in the project

| what | where | relation |
|---|---|---|
| fulgurite spawn | every sand biome (Stillsand, Long Shade, Leaning Scrub, Flooded Canyon, Weeping Stones, vanilla sand) | already general |
| dry lightning | Pyrelands `DryThunderstorm` **20** in a weather table summing to 88 (~23%). Long Shade 4, Rust Cathedral 4, Flooded Canyon 2, most others 0 to 1 | the Pyrelands really is the lightning biome, by a factor of 5 to 20 |
| glass from sand | Stillsand glass chain (`RM_GlassSand` → sun glass, lenses), moving to transparisteel (`GLASS_TO_TRANSPARISTEEL_1`) | the breaker eats Stillsand's sand. Fulgurite is kept as a natural glass |
| living bolts | Rust Cathedral (`RUT_LivingBolt`, watched bolts) | the only other lightning fiction. GPT said explicitly that its idea was distinct from this |
| Struck Glass rite | Pyrelands, campaign tier, unbuilt | the only planned use of fulgurite that is about lightning |
| found-tech study | `src/RimMandrake/EnvironmentalHazards/Source/RM_FoundTechStudy.cs` (shared; the Forge and the Greentide use it) | the built, tested way to make "study the thing where it fell" real |
| unity rule | CLAUDE.md "One kind of heat": a new mechanic attaches to the vanilla channel, never a parallel one | the breaker does this correctly: it hooks the vanilla short circuit |

## 2. Evaluation as a game designer

**Discoverability: poor.** A player in the Pyrelands sees fulgurite drop after storms, finds it nearly
worthless, and has no reason to think of electricity. The research is one more node in the tab. Off the
Pyrelands it simply cannot be started, and the reason sits only in the description. Nothing ever says
"your colonists noticed something." The only route to the breaker is reading the research tree.

**Readable cause and effect: broken in the middle.** The fiction promises: lightning fuses sand → we learn
from the glass → we build a fuse → it protects us from lightning. The game delivers: own a home map → do the
research → shovel sand from a *different* biome's chain → a breaker that answers a random indoor electrical
fault. **Two of the four links are missing, and the name promises a third thing that never happens.** That
gap is why it reads as tacked on. The owner's instinct is correct.

**Agency and meaningful choice: modest but real.** Zzztt is one of vanilla's most resented incidents. A
breaker that saves half your batteries is a genuine planning tool: where you place breakers is a layout
decision, and keeping the hopper stocked is upkeep. But vanilla already offers most of it: a power switch,
or batteries on a separate net. The breaker automates a trick, so it is a quality-of-life part, not a new
verb.

**Fantasy fit: strong in the material, absent in play.** "Desert people make fuses from lightning glass" is
a lovely, plausible piece of world texture, and it suits the Jawa as scavenger-engineers. Real fulgurites
are drawn from the photographs in `design/Jawa/worldbuilding/biomes/references/fulgurite/`. But the
fantasy lives only in two description strings.

**First time versus the hundredth.** First time: a letter, a crack of thunder, and "the east battery bank
survived." That is a nice beat, *if* the player remembers why they built it. Hundredth time: invisible, a
conduit that occasionally needs sand. Fulgurite is the opposite: the first find is a small pleasure, and by
the twentieth it is clutter worth 3 silver. Neither one grows.

**Frequency.** Short circuits are random colony incidents and happen in every biome. In the Pyrelands
specifically they are not more common, so the place that teaches the breaker does not *need* it more than
anywhere else. Fulgurite in the Pyrelands is frequent: about 23% storm weather times 35% a strike. How
often a strike lands on sand there is UNMEASURED, because Pyrelands ground is mostly ash.

**Interaction with other systems.** It is good on the engine side, since it hooks the vanilla short circuit
with no parallel system. It is thin on the design side: it does not touch storms, fire, ash or the burn
line, which are everything else the Pyrelands is about.

**Cost to keep.** The code is built and its proofs are green. The ongoing cost is a Harmony prefix on a
vanilla method, a research gate patched onto `CanStartNow`, two items, one building, owed art, and about 6
review and north-star rows that must be re-run on every Pyrelands trial. That is moderate for a part most
players will meet once.

**Enchanting to the player? Honest verdict: not as built.** It is a competent quality-of-life part wearing
a story it never tells. The *idea* has real enchantment potential, because "the storm hurts you and the
storm's own glass teaches you to survive it" is exactly the shape that makes a biome memorable. But that
potential depends on the two missing links: lightning that actually threatens the grid, and fulgurite that
actually teaches.

## 3. Three options

### Option A: drop the breaker; keep fulgurite as a found curiosity

Remove `RM_LightningBreakers`, the core, the breaker, both patches, the four Mod Settings and the
breaker's north-star and KEYSHEET rows. Fulgurite stays as it is: everywhere there is sand, melted at the
sun furnace, and later the Struck Glass rite ring.

- **Pros:** the least that can go wrong; removes a mechanic that tells a false story; frees a Harmony
  prefix and some test rows; fulgurite keeps its two honest uses.
- **Cons:** the Pyrelands loses its only mark-2 technology and drops back to MISS on a sheet the owner
  already ruled. It drops an idea he called *"a neat idea"*. A save migration is needed for any save holding
  a breaker; at minimum the review save does (station 20).
- **Build cost:** S, about half a day. Deletions, a settings cleanup, a save check, and a re-run of the
  Pyrelands static rows.

### Option B: keep it in the Pyrelands, and make the chain real *(recommended)*

Restore the two missing links. Every part reuses machinery that is already built.

1. **Lightning threatens the grid, in the Pyrelands.** On a Pyrelands dry-lightning strike within N cells
   of a powered conduit or battery, roll a short circuit through the vanilla `DoShortCircuit`. This uses one
   kind of short circuit, never a new one, and goes on the existing `DoStrike` postfix. Now the breaker's
   name is true, the biome creates the problem, and storms there become a real reason to fear for your
   batteries. Mod Settings: on/off and a chance per strike. A readable sign: the letter says "lightning
   struck near the line".
2. **Fulgurite teaches.** Give `RM_FE_Fulgurite` the shared `RM_CompFoundTechStudy`
   (`src/RimMandrake/EnvironmentalHazards/Source/RM_FoundTechStudy.cs`). Studying N pieces reveals
   `RM_LightningBreakers` with a breakthrough letter naming who studied it. This replaces the "own a home
   map" gate and honours *"Only learnable here because of the frequent lightning and sandy soil"* in play,
   not in prose: the Pyrelands is where fulgurite is plentiful enough to study.
3. **Fulgurite is the fuse, optionally.** The core takes 2 fulgurite plus steel *or* 20 glass sand plus
   steel (*"Desert sand works just fine too once you know how"*), so the glass the player picked up has a
   job.
4. Owed art (`_Off` frame), and the KEYSHEET stations rewritten to show strike → trip → letter.

- **Pros:** cause and effect becomes a story the player *lives*: a storm sparks a fault, half the grid
  survives, and the glass on the sand explains why. Fulgurite stops being clutter. The biome's identity
  (storms, fire) reaches its technology. It stays within the owner's ruling and the mark-2 rule. Every part
  reuses something built (the `DoStrike` postfix, `DoShortCircuit`, `RM_FoundTechStudy`).
- **Cons:** it adds a hazard: Pyrelands storms now threaten power, which is harsher. That is deliberate, but
  it needs tuning. It needs a live proof of strike-induced faults (a forced strike next to a conduit,
  through the bridge; not a flyer, so no owner-present rule applies). The research gate changes shape, so the
  `research_only_in_the_pyrelands` row is rewritten.
- **Build cost:** M, about 1 to 1.5 FOUNDRY days. Roughly 60 lines of C# on existing hooks, one comp line in
  XML, a recipe variant, settings, re-written north-star rows and KEYSHEET stations 20 to 22, and one art job.

### Option C: generalise to every biome with sand and lightning

B's machinery, but switched on wherever fulgurite falls. Any colony that studies fulgurite can learn the
breaker, and lightning near conduits can short them on any map with dry storms.

- **Pros:** consistent ("same physics everywhere", in the spirit of the one-kind-of-heat rule); Stillsand,
  Long Shade and Flooded Canyon players meet it too; fulgurite spawns there already, so the extra code is
  almost nothing.
- **Cons:** it **contradicts the owner's typed ruling** (*"Only learnable here"*) and takes away the
  Pyrelands' mark-2 identity, so it needs his explicit word. Lightning is 0 to 4 in those biomes against 20,
  so most players there would wait seasons for enough fulgurite: a discovery that never fires is worse than
  none. A strike-induced fault on every map is a planet-wide difficulty change, and the owner has ruled that
  biome mechanics are promised only inside our biomes. It also adds test surface in several biomes.
- **Build cost:** M+, about B plus half a day. Biome-scoped settings, one proof per biome family, and a
  balance pass on study thresholds against low strike rates.

## 4. Recommendation

**Option B.** The idea is good; what is wrong is the build, which cut out the one link (study the glass,
fear the storm) that made it enchanting, and B puts that link back with machinery we already own.

If B's new storm hazard is unwanted, fall back to A rather than C. A breaker with no lightning and no
fulgurite in its loop is a power switch with a story it does not tell, and that is the "tacked on" feeling
he is reacting to.
