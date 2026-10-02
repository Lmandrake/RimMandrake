You are a senior game designer consulting on a RimWorld 1.6 mod campaign. This is a SECOND ROUND. In round one you gave five further offerings for a tar rite in THE SUMP (a planet's tar basin). The owner's verdict on all five, verbatim:

"These are all really poignant, but they're just not hitting. But so close! Try again, and try to make it something a player on THIS map would care about. Really close though."

Your round-one answer, for reference (do not repeat any of these):
---
**Offerings check:** a blooded weapon; a clean-room door; a dead colonist’s last possession; a filled incident recorder; a working derrick head.  
**Consequence-kinds check:** faction command behaviour; map architecture; the remembered dead; the ship’s Narrator; a tar-beast world event.

## 1. The Weapon That Lost the Argument

- **What is put in the tar:** Alongside the fixed sacrifice and effigy, a valuable weapon that has wounded or killed, deliberately bent or disabled before immersion.
- **What it does:** The effigy’s next armed detachment arrives at normal strength but halts while its commanders quarrel over contradictory orders. After a visible standoff, it either fractures into mutually hostile groups or reconciles into an immediate, unusually coordinated attack. Neither outcome changes goodwill, Imperial Heat, equipment or loot. The tar has preserved the weapon’s failure of authority, not applied the existing tarred condition.
- **Which god it speaks to, and why** (never as an enemy): **Mob’Unloo**—a grievance is collected and presented back as an unsettled account.
- **How it works in RimWorld 1.6:** A `ThingComp` records qualifying weapon use. `RitualOutcomeEffectDef` stores the faction in a `WorldComponent`; the main C# hook intercepts that faction’s next armed `Lord` creation and substitutes a two-command `LordJob`. Mod Settings expose the split/reconciliation odds.
- **Readable signs:** Two command standards, argument motes, a countdown letter and distinct rally sounds; nobody silently disappears.
- **Drawn from:** Deliberately deposited Bronze/Iron Age weapons and named targets on the [Bath curse tablets](https://www.romanbaths.co.uk/roman-curse-tablets), plus the uncertainty and counterplay of [CK3 hostile schemes](https://ck3.paradoxwikis.com/Schemes). Those sources curse a person or resolve a scheme; this makes a sacrificed weapon infect military decision-making without weakening the force numerically.
- **Why it is unique here:** Unlike the faction effigy’s tarred sign, this changes a detachment’s command logic and may make the encounter worse.
- **Size:** M.

## 2. The Threshold the Tar Keeps

- **What is put in the tar:** One complete installed door, removed from the colony’s cleanest enclosed room during the rite and sunk with its hinges.
- **What it does:** Several hours later, the tar outlines every threshold of another highly clean, controlled room. The black seals jam its doors until cut apart or dissolved with acid; dissolution produces the already-established green gas. Contents remain intact, so the event is an architectural emergency rather than theft. Dirty, improvised rooms are poor targets.
- **Which god it speaks to, and why** (never as an enemy): **Ishko**—a prepared refuge may also become a prepared trap.
- **How it works in RimWorld 1.6:** An `IncidentDef` starts `MapConditionDef RM_RememberedThreshold`; its worker scores `Room` objects using cleanliness, impressiveness and regularity, then places static `ThingDef` seals. Door interaction is handled by a `CompUseEffect`; settings control delay, room-weighting and seal duration.
- **Readable signs:** Hairline black rectangles appear first, doors begin sticking, and the Narrator names the chosen room before it closes.
- **Drawn from:** [Dwarf Fortress engravings](https://dwarffortresswiki.org/index.php/Engraving), which make rooms repositories of value and history, and [Darkest Dungeon curios](https://darkestdungeon.wiki.gg/wiki/Curio), whose consequences depend on the supplied object. Neither makes excessive architectural control itself select the target.
- **Why it is unique here:** This is not a tar belch or mire: it attacks thresholds according to tidiness, directly expressing the Sump’s dislike of immaculate colonies.
- **Size:** S.

## 3. The Last Tool Has Standing

- **What is put in the tar:** A dead colonist’s last equipped weapon, tool or worn personal relic—not their corpse, organs or effigy.
- **What it does:** The tar later produces a no-reward quest concerning that specific dead pawn’s unfinished social history. A living friend, rival or creditor arrives to demand testimony, challenge the colony’s account, or hold a witnessed remembrance; if none exists, the Narrator reconstructs one genuine stored tale instead. The visitors cannot join or trade, and resolution grants neither items nor goodwill. The corpse remains visibly buried, burned or lost exactly where play left it.
- **Which god it speaks to, and why** (never as an enemy): **Ozzik**—ambition becomes grief, and grief insists that the dead retain a voice.
- **How it works in RimWorld 1.6:** `CompAssociatedDeadPawn` binds the item to a pawn record. The outcome launches `QuestScriptDef RM_LastToolClaim`, populated through `Slate` from `Pawn_RelationsTracker` and `TaleManager`; a fallback `IncidentDef` handles pawns with no valid relation. Settings control delay and how confrontational claims may become.
- **Readable signs:** The quest names the dead, cites an actual relationship or tale, and visitors carry matching name strips.
- **Drawn from:** The extraordinary preservation embodied by the [Tollund Man](https://www.museumsilkeborg.dk/tollundmanden), Dwarf Fortress memorial practice, and death’s continuing social consequences in [Pathologic 2](https://store.steampowered.com/app/505230/Pathologic_2/). This creates neither resurrection nor grave goods: preservation returns an argument about memory.
- **Why it is unique here:** Unlike the Cold Ledger, it settles no debt and seals no counter-gift; it opens testimony about a known dead person.
- **Size:** M.

## 4. A Black Box for Yesterday

- **What is put in the tar:** A costly recorder filled with the colony’s last three major incident records, after the player verifies its contents.
- **What it does:** Days later, the ship’s Narrator chooses one record and stages a dangerous “rhyme”: the same dramatic structure through a different cause or delivery. A drop assault might rhyme as ground troops encircling conduits; an inspection might rhyme as an armed customs cordon. Only threat and pressure templates are eligible, with no recruits, tradable visitors or reward block. The player knows which memory was chosen, but not how it will rhyme.
- **Which god it speaks to, and why** (never as an enemy): **Rekko**—a discarded event is salvaged, repaired incorrectly, and made to work again.
- **How it works in RimWorld 1.6:** A `MapComponent` records eligible `IncidentDef` contexts. `RitualOutcomeEffectDef` consumes the recorder and queues `IncidentDef RM_TarRhyme`; template-specific `QuestScriptDef`s rebuild the event. `RUT_` sends the event key to the campaign Narrator bridge, while standalone `RM_` uses an ordinary narrator letter; settings expose delay and threat-point scaling.
- **Readable signs:** The Narrator quotes the recorded date, a tar-sealed letter announces the rhyme, and normal arrival warnings remain intact.
- **Drawn from:** RimWorld’s [Ideology rituals](https://rimworldgame.com/ideology/), Frostpunk’s consequence-bearing laws, Cult of the Lamb’s costly rituals, and [Sunless Sea](https://www.failbettergames.com/games/sunless-sea)’s recurring storylets. Unlike those systems—and the permanent powers common in ritual mods—the player sacrifices campaign history so the storyteller can recombine it once.
- **Why it is unique here:** No other biome preserves an incident itself and hands its structure back to the Narrator.
- **Size:** L.

## 5. Give the Pump Its Answer

- **What is put in the tar:** The complete working head of a productive derrick, packed with a fixed quantity of its own output and still ticking as it sinks.
- **What it does:** A tar beast begins travelling toward one known Sump pumping site, chosen from the ritual map and Junker stations by an openly displayed weighted lottery. Its journey takes several days and may erase an NPC station or cross the player’s map as an evacuation-scale environmental front. It cannot be attacked, harvested or redirected, and leaves no loot. Pawns struck are displaced, tarred or killed with a corpse and continuous wake-trail—never silently removed.
- **Which god it speaks to, and why** (never as an enemy): **Ohm**—the offered machine has spoken rhythmically into something immense and living.
- **How it works in RimWorld 1.6:** `WorldObjectDef RM_TarBeastTrack` advances between fixed hand-made sites; arrival triggers an `IncidentDef` and `MapComponent_TarBeastTraverse`. Static bulge meshes, decals, sound and cell-by-cell destruction replace an animated or fightable pawn; the existing `HediffDef RM_Tarred` marks survivors. Settings control travel time, site weights and structural damage.
- **Readable signs:** Bending mouse-lines, stalled pumps, sequential surface bulges, a world-map track and escalating Narrator reports provide ample evacuation warning.
- **Drawn from:** The risk-forward ritual logic of [RimWorld: Anomaly](https://rimworldgame.com/anomaly/), costly votive objects such as the [Gundestrup cauldron](https://en.natmus.dk/historical-knowledge/denmark/prehistoric-period-until-1050-ad/the-early-iron-age/the-gundestrup-cauldron/), and Kenshi-style persistent settlement consequences. Unlike summoning rituals, this spawns nothing: it gives an already-existing catastrophe a destination lottery.
- **Why it is unique here:** It extends the established tar beast into a readable world-state gamble, without turning it into a raid, boss or weapon.
- **Size:** L.

**Build first:** *The Threshold the Tar Keeps*—cheap, unmistakably Sump, and it immediately validates the messy-colony rule.  
**Build second:** *The Last Tool Has Standing*—it demonstrates “the trap that remembers” through existing pawn history rather than new spectacle.  
**Order rationale:** Together they test the map-selection and narrative-record systems needed by the three larger variants.
---

# Diagnosis to act on

Round one reached outward: a faction's command quarrel, a visitor arguing a dead colonist's life story, the Narrator re-staging old incidents, a beast walking to a distant Junker station. The owner wants offerings and consequences that land HERE, on the map the player is standing on, among things the player already loves, fears or depends on: their own colonists (their skills, traits, bonds, grudges, mood), their buildings and rooms, their tamed and bonded animals, the tar beast and its bulge on this map, the pumps and derricks, the tar ponds, the wick-gardens, the dig shafts, the moat, the map's own resources and terrain. The player should feel the consequence within a day or two, on screen, in their own colony.

# The two rites as now ruled (fixed; your ideas are FURTHER OFFERINGS within these, not new rites)

- Rite A, the single offering: the colony throws one thing of value into the tar. It lowers Imperial Heat (the Empire's attention), lowers raid frequency, and erases ownership claims on an item (a stolen thing's provenance is wiped, so its old owner can no longer recognise it as theirs).
- Rite B, for Mob'Unloo (debt, exchange, grudges): one good thing as the price plus an effigy of something hated; unfortunate consequences fall on someone else, paid for by you. An Empire effigy holds the Empire off this map for five times the normal time; a faction effigy makes the whole next group of that faction arrive covered in tar.

# What to give

EXACTLY FIVE further offerings. Each is (a) a specific thing from THIS colony or THIS map that goes into the tar, and (b) a consequence the player SEES ON THIS MAP soon. Each must belong clearly to Rite A or Rite B (say which), differ from the other four in what is offered and in what system the consequence touches, and differ from round one. Start with two check lines: the five offerings; the five systems touched.

# Laws (violating one disqualifies the idea)

- A rite creates cohesion, never a material reward or a power for the colony. Nothing comes back out of the tar as loot.
- God favour shows only through events, world state and subtle odds, told by the ship's Narrator; never a buff, hediff, trait or stat on the colony's own pawns.
- A dramatic, risky world event is welcome; the owner loves rites whose effect is a gamble.
- Nothing living is thrown in: no pawn, prisoner, corpse or animal (no human or animal sacrifice). A living thing may be AFFECTED, but nothing vanishes without a readable sign.
- No god is evil; never make a god an enemy.
- Never gate on darkness.
- Avoid new animation work.
# Binding project rules (violating one disqualifies the idea)

- RimWorld 1.6 with ALL five DLCs present (Royalty, Ideology, Biotech, Anomaly, Odyssey); depend on them freely.
- One fixed, hand-made, tidally locked planet: a dayside, a terminator, a nightside. NO worldgen features of any kind, no procedural planets, no variants. Content lives on maps, incidents, pawns, buildings.
- ONE kind of heat planet-wide: vanilla temperature, heatstroke, hypothermia. Never invent a new "kind" of heat or cold or a new heat hediff.
- No animal or pawn ever vanishes without a readable sign (a mark, a letter, a trail, a tell).
- If it flies in the fiction, it flies in the game (real 1.6 flight).
- The free tier (RM_, franchise-free) uses only INVENTED exotic names; genuine Star Wars IP (canon creatures, Jedi/Sith, named canon planets) belongs only in the separate campaign layer (RUT_). The free tier must stand alone, not be a thin fallback.
- One animal, one biome, unless there is an in-game reason (migration, a life stage that moves).
- Every mod ships real Mod Settings: feature toggles, tuning sliders.
- The religion of the campaign (the Jawa "Salvation", nine small jealous gods) is in the campaign layer; a biome can TEACH a rite (found inscription → research row → ritual performable anywhere).
- NO GOD IS EVIL. Sh'kaar (the searing sun) and Zizzik (malfunction, the wrong spark) are "the hungry gods", dangerous, never villains.
- A god's favour shows ONLY through events, world state and subtle odds (and the ship's Narrator speaking of the gods vividly). NEVER a hediff, a stat blessing, a buff or a curse status.
- A rite may not grant a power. "Rituals create cohesion, not material rewards."
- Powerful tech is good; balance it by cost or gating, never by narrowing what it does.
- Avoid anything that needs new multi-frame animation work; the owner warns against "endless animation development". Static art, sound, terrain, map conditions, AI behaviour and UI are cheap; new animated rigs are not.
- The Sump is NOT extreme heat (temperature ~ -4 to +15 C). Its cold is vanilla cold. Fire is vanilla fire.



# The biome: THE SUMP ("the trap that remembers")

Owner-ratified sheet, frozen. Do NOT contradict it and do NOT re-propose what is ruled or built (listed below): build on it.

- Image: "black glass under a sun that never rises, holding a million years of the unlucky, perfectly." The planet's oil sump: the lowest basin on the planet (1 m elevation), just past the terminator on the night side, sun ~10 degrees below the horizon forever (permanent deep dusk). Flat black tar pools and cooled glassy sheet-tar ("glass reaches"), ringed with low waxy chemotroph plants that feed on the tar's energy, not the sun. No rain, no surface water: the only liquid is tar.
- Origin: the Pyrelands' endless ash, churned by ancient floods and compressed over eons, drained downhill and nightward; the cold is the lid, nothing evaporates back. The hydrocarbon ladder runs on nightward: Blue Desert chemistry, then the Propane Lakes.
- The tar PRESERVES (anoxic, cold, patient): everything that ever blundered in is still in there. Digging is a lottery across deep time: bones and hides of unnamed ages, sunken machines, sealed casings, and armed booby traps in perfect working order. Every dig is treasure or a click. Owner ruling: dig wakes are ancient machines or ancient assailants ONLY; no normal life survives the tar.
- The tar DEFENDS: nothing crosses it willingly, and it can be lit into a terrible smoky wall nothing can cross. The export is "being left alone": moat-tar for hermits, droid enclaves, paranoid rich.
- The Junker stations: nodding pumping derricks in the dusk, gangs in tar-stiff coats, holding ponds, barrel yards, the reek; the biome's only industry, law and light. The play-style law (owner): the Sump REWARDS dirty, messy, idiosyncratic colonies and FRUSTRATES neat, tidy, controlled ones.
- The TAR BEASTS: slow, huge things IN the tar, oozing and accreting it, digesting the unfortunate. Dormant set-pieces woken by deep digs, explosions or greedy pumping; a woken one is a slow, unstoppable, station-eating catastrophe you EVACUATE AHEAD OF, never fight. Hard ban: never a fightable spawn or raid entry.
- Hard bans: no whole ancient assailant ever in the tar (partial remains only; booby traps more likely than either); no sun-driven flora; no rain or surface water; no warm-climate flavour; no Earth flora or fauna.

Already BUILT or RULED (do not re-pitch; you may build ON these):
- Poured tar moats with fuse posts that light them on command into a smoke-and-flame wall; network fire along connected tar with gate firebreaks (ruled).
- The dig shaft and the dig-strata lottery (traps weighted first).
- The tar belch: a pit randomly belches tar over the local terrain; tar coats any terrain and any pawn ("tarred": slow, stinking, mood); solvents (an acid) clean it, and the cleaning reaction releases a green gas.
- GASLIGHT: tar + acid makes a green gas; gas lamps with a dancing, warbling, colour-shifting light; flame statuary (art statues with flames issuing from them, quality scales the show); natural seep flames on the map whose first sighting TEACHES the gaslight chemistry (ruled, unbuilt).
- The tar vault: anything sealed in tar never rots, but taking it out needs acid per item, or it comes out ruined.
- Walkways: cheap plank duckboards that foul with tar; poured-bitumen "glasswalk" that never fouls but is slippery (speed cap, rare harmless pratfalls).
- Ship gifts (ruled): glasswalk ship flooring; gas lamps and flame statues aboard.
- Mouse-lines: sump-mice run the tar in lines; where the lines bend, the crust is thin or something is under it.
- Fauna: sump-mouse (the instrument), gulveth (sofa-sized tar grazer that wades the black), the thrummel family (warm furred burrowing hive under the tar lid, aggressive at its mounds; chitin and seepwax; a broodmother), brommet (wool grazer of the margin), dredgel (dig-site sifter), skarrid (still hunter that mimics a tar beast's bulge), skellarn (stilt-legged flier that lands and walks the tar). Flora: wick-plants (slow-burning stems, candles), dorvel (slow crop), skelver (forage), korveth (bitumen accumulator), brindeth (woody margin), soffeth (rings where gas rises), tolleth (grave-bloom marker), velloch (tar-surface film), mirrelin (glass-reach graze), pallick (a pale false-floor crust that lies).
- The permanent dusk lock (weather).
- Campaign: an arrival letter in which the ship's memory warns about thin tar; a precept making the flame statues a holy act for Sh'kaar.


# Output format (Markdown)

The two check lines, then for each idea:

## <n>. <evocative title> (Rite A or Rite B)
- **What goes in the tar (from this colony):**
- **What the player sees on this map, and when:** 3-5 sentences.
- **Why a player on this map cares:** one sentence.
- **How it works in RimWorld 1.6:** def types and the main C# hook.
- **Readable signs:**
- **Drawn from:** one or two cited games/mods and what this does that they don't.
- **Size:** S / M / L.

End with a 3-line ranking of the two to build first. Under 1,800 words.
