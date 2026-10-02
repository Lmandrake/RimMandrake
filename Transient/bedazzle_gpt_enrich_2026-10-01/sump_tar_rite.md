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