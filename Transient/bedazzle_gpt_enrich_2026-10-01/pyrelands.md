**Verbs check:** rewire · ride · signal · account · temper — five distinct verbs, none repeated.  
**Systems check:** electrical faults · gravship launch · colony zoning · religion/storyteller · manufacturing — five distinct systems, none repeated.

## 1. Branchglass Reclosers

- **Marks it serves:** 2
- **The player's experience:** Lightning-struck fulgurite can be studied instead of merely collected. Enough samples reveal a research row showing how its branching fractures arrest electrical faults. The player rewires critical grids through Branchglass Reclosers: when a `Zzztt...` occurs, a charged recloser opens, sacrificing its cartridge while keeping the isolated grid section alive. The emotional beat is earned engineering confidence—the Pyrelands teaches survival through planned failure.
- **How it works in RimWorld 1.6:** `ResearchProjectDef`, `ThingDef`, `RecipeDef`, `JobDef`, `SoundDef`, and `CompProperties_RM_Recloser`; a Harmony prefix on `ShortCircuitUtility.DoShortCircuit()` determines which separated `PowerNet` receives the fault. It reads studied fulgurite, connected nets and stored battery energy; it writes breaker state, cartridge consumption and localized discharge. Settings: enable, samples required, cartridge cost, protected-energy percentage and reset time.
- **Readable signs:** The glass visibly blackens, the power overlay shows the opened connection, a sharp descending crack plays, and a letter identifies the isolated branch and lost charge.
- **Drawn from:** *Oxygen Not Included*’s [Power Transformer](https://oxygennotincluded.wiki.gg/wiki/Power_Transformer), which limits flow between circuits, and *Factorio*’s [Power Switch](https://wiki.factorio.com/Power_switch), which partitions a network. Neither turns naturally created lightning glass into a consumable, automatically tripped RimWorld fault boundary.
- **Why it is unique here:** Unlike Rust Cathedral’s watched, living bolts, Branchglass is deterministic engineering learned from dry-lightning scars, with no material awareness.
- **Tier:** free (`RM_`); Branchglass is an invented, setting-independent technology useful on any map.
- **Size:** M

## 2. Ride the Black Column

- **Marks it serves:** 6
- **The player's experience:** A large standing burn raises a marked smoke-column capture zone around a landed gravship. The pilot can choose a Column Launch, beginning a tense countdown during which the qualifying fire must remain large and dangerously close. If maintained, the gravfield couples to the updraft and gains temporary lift capacity for that departure; if the fire collapses, launch aborts rather than silently losing cargo. This is exhilaration: the colony launches because the country is burning, not despite it.
- **How it works in RimWorld 1.6:** `ThingDef` for a grav-engine module, `StatDef`, `ResearchProjectDef`, `SoundDef` and static `FleckDef`; `CompPilotConsole.CompGetGizmosExtra()` adds the mode, while a Harmony postfix on Odyssey’s gravship launch-capacity calculation applies the one-launch mass allowance. It reads the existing burn component’s active-fire cells and vanilla temperature, then writes a temporary launch manifest modifier cleared on takeoff or abort. Settings: enable, required fire area, capture radius, mass percentage, countdown and module cost.
- **Readable signs:** A column-strength meter, projected capture ring, bending ember flecks, escalating hull resonance and an explicit abort letter make every state legible.
- **Drawn from:** Odyssey’s [assembled, flyable gravship](https://rimworldwiki.com/wiki/Gravship), *Surviving Mars* [dust storms](https://survivingmars.paradoxwikis.com/Disasters) that ground rockets, and *Save Our Ship 2*’s [ship heat systems](https://github.com/SonicTHI/SaveOurShip2Experimental). Those systems treat environment or heat as constraint/internal load; this makes a real external wildfire an optional lift medium.
- **Why it is unique here:** Unlike Leaning Scrub, the land does not mistake the ship for fire and summon herds—the player deliberately rides an existing fire column for physical lift.
- **Tier:** free (`RM_`), requiring Odyssey but no campaign IP.
- **Size:** L

## 3. Cinder-Call Posts

- **Marks it serves:** 7
- **The player's experience:** The player places cheap ceramic call-posts on likely approach lines, assigns each a distinct note, and links it to a prepared allowed-area policy. When actual fire reaches a post, it cracks like a signal pistol and switches the chosen colonists or animals into that policy. A sequence of bass, middle and treble reports tells the player which flank the front is consuming without moving the camera. The emotional beat is urgent command: the burning landscape plays the evacuation plan the player composed.
- **How it works in RimWorld 1.6:** `ThingDef`, `SoundDef`, `DesignationDef`, `KeyBindingDef` and `CompProperties_RM_FireCall`; `ThingComp.CompTickRare()` reads adjacent vanilla `Fire` and `GenTemperature`, then a `MapComponent` writes selected pawn-area restrictions. Settings: enable, trip threshold, one-shot/reusable mode, volume, automatic zone switching and eligible pawn categories.
- **Readable signs:** Every post has a colored note-rune, produces sound plus subtitles and a matching screen-edge pulse, leaves shattered ceramic, and records its command in the message log.
- **Drawn from:** *Factorio*’s [Programmable Speaker](https://wiki.factorio.com/Programmable_speaker), which turns circuit signals into alarms, and Project Zomboid’s [emergency broadcast system](https://pzwiki.net/wiki/Automated_Emergency_Broadcast_System), which conveys actionable forecasts through sound. Neither makes expendable spatial notes that are physically struck by a moving hazard and execute prewritten evacuation zoning.
- **Why it is unique here:** Unlike Stillsand’s Listening or Long Shade’s temperature sound bed, these posts detect nothing remotely—they are sacrificial, player-authored command points the fire must physically reach.
- **Tier:** free (`RM_`); no faith or franchise reference is required.
- **Size:** M

## 4. The Ninth Name of Ash

- **Marks it serves:** 9, 2
- **The player's experience:** A fixed, hand-placed Pyrelands inscription opens a research row and then an Ideology ritual performable anywhere. After genuine fire losses, the player selects up to nine recorded names—people, bonded animals, masterworks or rooms—and the colony accounts for what is gone around their surviving ash-marks. The rite provides only shared catharsis and cohesion; it grants no item, power, weather change or divine favour. Separately, subsequent actions—repairing, trading, rebuilding grandly or leaving—subtly alter which Rekko, Mob’Unloo, Ozzik, Ta’Baa or satiated Sh’kaar events the Narrator is likelier to tell.
- **How it works in RimWorld 1.6:** `ThingDef`, `ResearchProjectDef`, `RitualPatternDef`, `PreceptDef`, `RitualBehaviorDef`, `RitualOutcomeEffectDef` and bespoke `IncidentDef`s. A `GameComponent_RUT_SalvationAttention` records fire-destroyed things and later responses; `RitualOutcomeEffectWorker.Apply()` creates cohesion memories only, while a patch at `StorytellerComp_CategoryIndividual.MakeIntervalIncidents()` adjusts event weights without pawn buffs. Settings: enable, qualifying-loss value, memorial window, odds strength, narrator frequency and per-god event toggles.
- **Readable signs:** Losses leave temporary labelled ash silhouettes, the ritual dialog lists exactly what is named, and vivid Narrator lines announce attention without exposing a favour meter.
- **Drawn from:** Ideology’s [configurable rituals and outcomes](https://rimworldwiki.com/wiki/Rituals) and *Frostpunk*’s [Cemetery](https://frostpunk.fandom.com/wiki/Cemetery), where treatment of the dead shapes communal morale. This separates powerless remembrance from a long-lived event ecology responding to what players actually do afterward.
- **Why it is unique here:** Unlike Nightside Ice’s Cold Ledger or Leaning Scrub’s Calling-Pyre, it offers no counter-gift and burns nothing deliberately; involuntary loss is named, while the gods remain hungry witnesses rather than villains.
- **Tier:** campaign (`RUT_`), because it explicitly belongs to the Salvation and its nine gods.
- **Size:** L

## 5. The Walking Kiln

- **Marks it serves:** 2, others—production
- **The player's experience:** Research learned by observing several completed fronts unlocks low, sealable kiln-beds loaded with selectable solid recipes. The player places them in the predicted path and uses firebreaks or firefoam to control how long vanilla fire surrounds them. Correct exposure produces ceramics, glass or durable component casings; underfiring wastes time, while excessive exposure ruins the batch without making it disappear. The emotional beat is anxious craftsmanship—turning an uncontrollable migration of flame into a visiting workshop.
- **How it works in RimWorld 1.6:** `ResearchProjectDef`, `ThingDef`, `RecipeDef`, `StuffDef`, `SoundDef` and `CompProperties_RM_ExposureKiln`; `ThingComp.CompTickRare()` integrates adjacent `Fire` intensity and `GenTemperature.GetTemperatureForCell()`, then writes visible underfired/cured/ruined batch state. It uses only vanilla temperature and fire. Settings: enable, exposure window, overfire tolerance, batch yield, failure loss and individual recipes.
- **Readable signs:** Static glaze-stage graphics, a heat-history bar, pitch-changing ceramic ticks and recoverable cracked spoil show exactly what happened.
- **Drawn from:** *Oxygen Not Included*’s [Kiln](https://oxygennotincluded.wiki.gg/wiki/Kiln), which batch-converts minerals, and *Don’t Starve*’s [Wildfire](https://dontstarve.wiki.gg/wiki/Wildfire), which makes unattended objects smoulder and ignite. Neither lets a geographically moving wildfire supply a player-shaped industrial firing curve.
- **Why it is unique here:** Unlike Cauldron’s fluid conversion or the Tribes’ flame harvest, this is solid-state manufacturing in placed equipment, with no crop, rite, territorial claim or weather cycle.
- **Tier:** free (`RM_`); the technology remains fully usable elsewhere with player-made vanilla fire, while Pyrelands makes it economical and perilous.
- **Size:** M

**Build first:** Cinder-Call Posts—smallest scope, immediately makes sound tactically consequential, and exploits the completed fire-front system.  
**Build second:** The Walking Kiln—it supplies the missing discoverable method and creates a high-skill reason to shape rather than merely suppress the burn.  
**Then:** Branchglass is the best portable reward; Column Launch and the Ninth Name deserve later, DLC-heavy integration passes.