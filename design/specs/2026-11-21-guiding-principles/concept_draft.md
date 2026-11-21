# Guiding principles: concept draft (not a ruling yet)

Item `RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES`. Draft by the Conductor, 2026-11-21, for the
owner's review, a GPT review and two censuses. Nothing here binds until he rules.

## His words (2026-11-21)

"Biome mechanics in general do NOT stay confined to the biome of origin: they are universal, but that biome depends on
them, showcases them, or has the materials or sources to make them or make them shine. For example, the Stillshade has
nothing 'special' about its long shadows and intense sun exposure effects: those should be planet-wide. But the
Stillshade showcases them with a unique biome adaptation to them. ... The Rot features a living floor covering that
heats rooms and keeps life alive in the cold through food consumption. It works anywhere, but it's native to the Rot and
must be tended and carried elsewhere. We should also make it die in direct Sun exposure to explain why the Rot hasn't
spread over the whole surface." And: "the meaningless pale region around steam geysers I definitely did [mind]."
"Form first, Specifics later."

## Part 1: the game principles, proposed form

1. **A mechanic is physics; a biome is a place.** A mechanic (sun, shadow, heat, water, fire, rot, a living floor, a
   creature's behaviour) works the same on every tile of the planet. The code of a mechanic never asks "which biome is
   this?". It asks for the physical conditions: sun angle, temperature, water, fire near, ground kind, roof.
2. **A biome earns a mechanic in one of three ways, and says which.** It DEPENDS on the mechanic (life there needs
   it), it SHOWCASES the mechanic (its conditions make the mechanic extreme, and its natives are adapted to it), or it is
   the SOURCE (the material, creature or plant that makes the mechanic is native there and must be carried elsewhere).
3. **A limit in the world, never a limit in the code.** When something from a biome must not take over the planet, the
   reason is a physical one that the player can find out and use (the Rot's floor dies in Direct Sun; it eats food; it
   must be tended). A biome check is not a reason.
4. **What a biome owns is its data, not its laws.** Which plants, animals, terrain, weather odds and map features a
   biome has is biome data, and stays per biome. How those things behave once they exist is a mechanic, and is universal.
5. **Every visible effect means something the player can read and act on.** An effect with no meaning (the pale region
   around a steam geyser) is removed. It is not kept and confined.

## Part 2: questions that the form leaves open (for cards)

- **Universal by design, or also validated everywhere?** His ruling of 2026-10-15 released the requirement that biome
  mechanics WORK in other biomes: "That's too much of a lift. ... We can't guarantee they will work in other biomes
  beyond our framework. They should... but we're not going to validate that at this time." Today's ruling says the
  mechanics ARE universal. These fit together only if "universal" is a rule about how the code is written (no biome
  check) and the validation promise stays where a mod's bars put it. Or the 2026-10-15 ruling is reversed and each
  mechanic also gets a check on a foreign biome. The cost differs a lot.
- **Vanilla and third-party biomes.** Universal on our planet (one hand-made world, our biomes only) is cheap. Universal
  on any biome of any mod is not testable.
- **Mod Settings.** The existing cross-biome switches are "default off, labelled Unsupported". Under principle 1 the
  switch has nothing to switch: a mechanic is on everywhere. What does a player switch off, then: the mechanic itself.
- **Mechanics that are dangerous everywhere.** A planet-wide mechanic changes every colony, also one that never visits
  the biome (fire ecology, venom, heat). Is each universal mechanic on by default?
- **The 1.0 scope.** The world is painted once at the end; six biome mods are held. Universal mechanics couple the
  mods: a mechanic may have to move out of its biome mod into a shared mod, or the biome mod must load for every colony.

## Part 3: GUIDING_PRINCIPLES.md, proposed form

- One file at the project root, beside `LEXICON.md`. LEXICON says what words mean; GUIDING_PRINCIPLES says what is
  always true of the product, above any one mod, biome or feature.
- A principle is a sentence that (a) decides real design questions, (b) can be broken by a concrete design, and (c)
  comes with one example that honours it and one that breaks it. A sentence that no design could break is a slogan and
  does not go in.
- Each principle carries: the sentence; his words and the date (or a pointer to them); one honouring example; one
  breaking example; the check, if a program can make one (principle 1 can be a lint: mechanic code that reads the
  BiomeDef).
- Few. A ceiling of about a dozen. A new one enters only by his ruling; an agent may propose.
- It is a product document (what the game is), not a process document (how agents work): process stays in CLAUDE.md
  and the CHARTER. Rulings that are cases of a principle point at it.
- Lodestar: every tracked project gets the file at birth (the birth-certificate step), seeded by a short interview;
  existing projects get one derived from their rulings and confirmed with the owner, one project per sitting; the file
  is re-read at each Design Version change, because a MAJOR version is by definition a change of vision.

## Known tension inside tonight's work (examples for the censuses)

- TheForge's geyser haze was confined to The Forge biome at `d07e03a938f7`, citing "biome mechanics stay inside our own
  biomes". Under principles 1 and 5 the haze is removed or given a meaning; it is not confined.
- Pyrelands: the fresh reader of the ashwallow dive fix made the dive apply only on a Pyrelands map, so that a tamed
  ashwallow does not dive on another biome's map (`675ab57651`). Under principle 1 an ashwallow dives from fire anywhere.
- Pyrelands: `pyrelandsEnabled` gates and the burn line apply per map; the Tribes fire rite makes burned wild animals
  roll revenge.
- Direct Sun is already written as "a pure function of geometry", with one exception (the Scald's steam clock).
