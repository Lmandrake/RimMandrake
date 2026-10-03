SUBJECT: Utinni discovery achievements

**I would build a “Scavenger’s Atlas”: a catalogue organized around the biomes’ nine marks, with staged hints and separate recognition for encountering content and trying its capabilities.** Use a small `RM_` discovery framework with `RUT_` content and presentation. Keep rewards off by default.

One correction to the design doc: **VAE now publishes 1.6 support.** Its repository contains a 1.6 assembly, defs, and source; its Workshop listing also advertises 1.6. That establishes published support, **not verified compatibility with Utinni’s campaign or a guarantee of continued maintenance**. The missing achievements folder in the inspected VWE directory does not establish VAE’s status. [VAE 1.6 package](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/tree/main/1.6), [Workshop listing](https://steamcommunity.com/sharedfiles/filedetails/?id=2288125657)

This is design-only. Your inlined document is the authority for existing Utinni machinery. Names beginning `RM_Discovery…` below are proposals, not existing APIs.

**Research: what these systems actually teach**

The failure assessments below are my design judgments, unless attributed explicitly. They describe limitations relevant to Utinni, rather than claims that the games’ systems are broken.

**Vanilla Achievements Expanded — good tracking architecture, a different product emphasis.**

VAE separates authored definitions from runtime progress:

- `AchievementDef` declares the label, description, icon, points, optional achievement tab, and a tracker with tracker-specific fields.
- `AchievementTabDef` supplies grouping.
- Trackers distinguish actions from conditions: `BuildingTracker` counts completed construction, whereas `ItemTracker` checks possession periodically. Research, crafting, abilities, incidents, quests, containment, and other activities have their own trackers. [Authoring documentation](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/wiki), [tracker catalogue](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/wiki/Available-Trackers)
- `AchievementPointManager : GameComponent` owns runtime cards and point balances, rebuilds lookup structures when starting/loading, queues notifications, and scribes cards with `LookMode.Deep`. [Manager source](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/blob/main/1.6/Source/AchievementsExpanded/AchievementsExpanded/AchievementManager/AchievementPointManager.cs)
- Harmony dispatches gameplay events to relevant trackers. Periodic conditions are checked every 2,000 ticks or daily; the 1.6 source includes gravship landing and launch-content callbacks. [Detection source](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/blob/main/1.6/Source/AchievementsExpanded/AchievementsExpanded/AchievementManager/AchievementHarmony.cs)
- Rewards are separate purchasable defs with costs and execution logic. Examples include caravans, cargo pods, raids, and random quest items. They are a points shop, not automatically a small gift tied to one discovery. [Reward definitions](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/blob/main/1.6/Defs/Rewards/Rewards.xml), [reward base class](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/blob/main/1.6/Source/AchievementsExpanded/AchievementsExpanded/Rewards/AchievementReward.cs)

**What works:** visible goals make unfamiliar actions legible; the def/tracker split lets content mods register achievements.

**What fails for this brief:** a card saying “craft this named technology” can spoil the discovery; counters and points encourage optimization rather than curiosity. The documented model does not establish the rumor/evidence/LoreStages behavior Utinni needs.

There is also a significant uncertainty: the wiki says supported custom C# trackers were removed in 1.5, while current source still discovers `TrackerBase` subclasses and uses tracker-supplied hook metadata. **Custom integration may remain technically possible, but I would not assume it is a supported extension contract.** [Maintainer’s custom-tracker notice](https://github.com/Vanilla-Expanded/VanillaAchievementsExpanded/wiki/Custom-Trackers)

| System | How it reveals content while preserving discovery | Limitation and lesson for Utinni |
|---|---|---|
| **RimWorld Anomaly entity codex** | Undiscovered slots communicate that more entities exist; discovered entries give a durable reference. Encountering and studying entities connect knowledge to play. Your document identifies `EntityCodexEntryDef` as the relevant vanilla precedent. [Entity overview](https://rimworldwiki.com/wiki/Entities) | Silhouettes can reveal creature shapes, and an entry can explain too much immediately. Entity coverage also cannot represent every campaign capability. Borrow persistent entries and staged knowledge; do not force canals, graffiti, weather, and gods into an entity schema. |
| **Anomalies Expected’s Entity Database** | The author describes a larger codex, grouping, dynamic labels/descriptions, and retained unlocked study notes. This makes learning accessible after the entity is gone. [Author’s description](https://steamcommunity.com/sharedfiles/filedetails/?id=3240752689), [author’s UI explanation](https://www.reddit.com/r/RimWorld/comments/1ikeybq) | Better organization helps remembered discoveries; it does not by itself supply leads toward unseen content. Borrow retained evidence and readable grouping. **Unsure:** its present 1.6 integration suitability. |
| **Dwarf Fortress Legends mode** | Historical figures, sites, artifacts, and events become interconnected records. The “Reveal All Historical Events” setting distinguishes omniscient history browsing from history uncovered through adventuring. [Legends documentation](https://new.dwarffortresswiki.org/index.php/Legends) | With full revelation, mystery is sacrificed; without it, missing history is not necessarily an actionable lead. Dense history can bury possibilities. Borrow provenance—who, where, when—and links between discoveries, not omniscience. |
| **Caves of Qud journal/lore** | Locations can enter the journal through exploration **or information from another source**. Gossip, sultan histories, chronology, and personal notes preserve different kinds of knowledge. World-map notes turn information into destinations. Secrets also circulate socially. [Developer announcement](https://store.steampowered.com/news/posts/?appids=333640&enddate=1497056841), [secret system](https://wiki.cavesofqud.com/wiki/Secret) | A remembered rumor does not guarantee that its subject remains available or that the player understands how to investigate it. Excellent for inscriptions, urns, and Jawa hearsay, provided every important rumor supplies a usable next step and a source. |
| **Outer Wilds ship log** | Rumor mode distinguishes a place heard about from one explored. Connections preserve why it matters; question marks invite investigation without supplying the answer. “More to explore” signals incomplete knowledge. The modding schema explicitly distinguishes `RumorFact` and `ExploreFact`. [Ship-log description](https://outerwilds.fandom.com/wiki/Computer), [New Horizons authoring schema](https://nh.outerwildsmods.com/guides/ship-log/) | “More to explore” can become frustrating when one small fact remains. Visible graph structure can itself reveal relationships. Borrow rumor-versus-evidence and an actionable unfinished lead; do not equate every missing flavor detail with unfinished gameplay. |
| **Subnautica PDA/scanner** | The scanner creates an explicit investigative action: approach an organism or technology fragment, scan it, and retain useful findings in the PDA. Encounter precedes explanation. [Developer’s scanner introduction](https://unknownworlds.com/en/news/h2-o-update-released) | A scan can deliver a large explanation immediately; unseen scan targets remain difficult to anticipate. Fragment counts can become a search chore. Borrow “study this interesting thing” for inscriptions and organisms, but do not add a scanner tax to every Utinni mechanic. |
| **Noita progress and unlocks** | Progress records perks tried, spells actually cast, and enemies killed. This distinguishes using something from merely finding it. Spell availability unlocks are a separate form of progression; secret culture is reinforced even through redacted developer notes. [Progress documentation](https://noita.wiki.gg/wiki/Progress), [developer release notes](https://www.noitagame.com/release_notes/) | Deep concealment supports community investigation but gives a solo player little direction. “Unlocked,” “found,” and “used” can also be confused. Borrow first-use recognition; reserve Noita-level obscurity for genuinely optional secrets. |
| **Hades codex** | Entries deepen through encounters, conversations, gathering, and slaying. Achilles’ authored perspective makes incomplete knowledge feel natural. Supergiant explicitly added backfilling for earlier discoveries and deferred codex alerts until after combat. [Codex description](https://hades.fandom.com/wiki/Codex), [developer patch notes](https://www.supergiantgames.com/blog/hades-welcome-to-hell-update-patch-notes/) | Repeated encounters can become lore grinding, and characters may depend on conversation scheduling. Borrow progressive understanding, retroactive recognition, and quiet notification timing; do not require repeated canal uses just to finish a paragraph. |
| **Return of the Obra Dinn** | The book exposes the questions before their answers: identities, fates, chronology, and evidence. Blurred faces indicate insufficient identification evidence; correct fates are generally confirmed in batches of three, limiting immediate guess-testing. [Developer’s book design](https://dukope.com/devlogs/obra-dinn/tig-37/), [book mechanics](https://obradinn.fandom.com/wiki/General), [confirmation behavior](https://en.wikipedia.org/wiki/Return_of_the_Obra_Dinn) | Delayed confirmation is appropriate for deduction, but would make ordinary capability recognition opaque. Borrow “you have enough evidence to investigate this,” not delayed confirmation for successful actions. |
| **Hollow Knight Hunter’s Journal** | Most entries appear after an initial defeat; further encounters unlock the Hunter’s notes. Some entries instead come from inspecting objects or completing challenges. Identification and fuller understanding are separate. [Journal documentation](https://hollowknight.wiki/w/Hunter%27s_Journal_(Hollow_Knight)) | Kill quotas turn knowledge into grinding and privilege violence. Borrow the two-step structure, but let observation, study, taming, escape, or another appropriate interaction establish creature knowledge. |
| **Minecraft advancements** | Branches offer nearby goals, while hidden advancements preserve exceptional surprises. Data-pack definitions make new goals extensible; completing an advancement need not follow its display-tree order. [Advancement documentation](https://minecraft.wiki/w/Advancements), [developer introduction](https://www.minecraft.net/en-us/article/minecraft-snapshot-17w14a) | A completely hidden node cannot teach that its activity exists. A display tree can also imply mandatory progression. Borrow concise action prompts and extensibility; separate hint visibility from completion eligibility. |
| **Steam hidden achievements** | Valve’s hidden flag withholds an achievement from the player’s Community page until achieved. It protects names and descriptions from advance exposure. [Steamworks documentation](https://partner.steamgames.com/doc/features/achievements) | Concealment supplies no invitation to investigate. External achievement pages can expose secrets anyway. Use total hiding sparingly; most Utinni content needs a spoiler-safe promise before completion. |

The central distinction is **awareness, evidence, and participation**. A player can know a capability exists, encounter its subject, and still never try it. Utinni should preserve those differences.

**The common RimWorld foundation**

These five designs can share a modest implementation without sharing the same player experience.

An `RM_DiscoveryEntryDef` would declare stable identity, category, associated defs, visibility rules, LoreStages references, evidence requirements, optional first-use requirements, and destination links. A `DefModExtension` on a biome, creature, recipe, building, or other feature-owning def would reference its entries. Scripted chains could declare entries in standalone discovery defs.

**Def-declared triggers, Harmony hooks, and polling are complementary:**

- **Defs say what counts.** They select supported predicates and event types.
- **Direct callbacks detect Utinni-owned behavior.** Emit a discovery event after the custom mechanic commits its successful result.
- **Harmony observes vanilla or external behavior.** Prefer narrow success callbacks over broad job-start hooks.
- **Polling reconciles durable conditions.** Check unresolved entries on a staggered schedule, using relevant map lists or caches. It cannot reliably reconstruct a fleeting event that happened between checks.

A `GameComponent_RM_Discoveries` would store per-save evidence, first-use flags, unread status, and optional reward claims. `ExposeData()` would use `Scribe_Values` and `Scribe_Collections`; runtime indexes and event subscriptions would be rebuilt after loading.

For save safety:

- Store stable entry IDs and primitive evidence, with migration aliases for renamed entries.
- Preserve records for removed content as unavailable archives.
- Make repeated callbacks idempotent.
- Retain discovery after a pawn dies, a map disappears, or the ship departs.
- Identify destinations by **planet layer and tile**, not a bare tile index.
- Backfill durable facts from existing systems; do not invent historical evidence for transient actions.

Treat LoreStages, rites, unveiled gods, and vanilla hidden-item flags as their respective authorities. Observe `Find.HiddenItemsManager.SetDiscovered` transitions; **do not call it merely because the journal wants a checkmark**. **Unsure:** exact 1.6 hook signatures, discovery-query methods, and existing Utinni callback surfaces need inspection when building resumes.

Data-driven registration also needs an authoring rule. XML cannot infer “this tree regrows” from arbitrary code. Every discoverable feature must declare entries or an explicit exclusion reason. A developer coverage report should flag missing registration, dangling refs, absent trigger adapters, and entries without reachable hints.

**Five distinct designs**

**1. Scavenger’s Atlas — exploration organized by place**

**Experience.** The player opens **Discoveries**, chooses a biome, and browses its nine marks. Each mark contains promises and findings: unusual resources, a weather phenomenon, a technology lead, a creature encounter, or something to try with the ship.

**How entries become known.** Biome pages initially offer broad hints. Visiting with the clan reveals local leads; study and use reveal specifics. Example proposed wording: “Some roots refuse a final harvest.” It announces an unusual tree property without explaining the regeneration rules.

**Detection.** Def-declared biome associations combine with actual clan arrival, local observation, and mechanic-success events. Map generation alone does not establish a visit. Polling reconciles durable local conditions. Global evidence lives in the `GameComponent`; location records survive departure and map removal.

**UI.** A `MainButtonDef` opens a `MainTabWindow` with biome pages, filters, pins, and “things to try here.” Quiet messages recognize minor findings; major discoveries may use `Find.LetterStack.ReceiveLetter`.

**Registration.** A biome extension maps all nine marks to entry references or explicitly marks a slot inapplicable. Features register their own entries. Markdown scorecards guide authorship; runtime definitions supply the catalogue.

**Tier.** `RM_` storage, predicates, and catalogue infrastructure; `RUT_` nine-mark taxonomy, biome associations, hints, and visual identity.

**Biggest risk.** Turning ~225 biome/mark slots into chores. The marks are navigation categories, not nine mandatory achievements per biome. Shared mechanics should have one entry with several biome associations.

---

**2. Shipboard Rumor Net — exploration organized by connections**

**Experience.** Players follow threads: an urn suggests an inscription; the inscription points toward a place; a discovery there connects to an unveiling or technology. The central question is “Which lead interests us next?”

**How entries become known.** Rumors introduce unknown subjects. Nodes display a question or anonymous clue; confirmed facts replace speculation. A new rumor may reveal that a destination exists without identifying its contents.

**Detection.** Successful urn study, inscription reading, chain transitions, and arrival publish evidence events. Defs declare rumor edges separately from completion requirements. Already completing a discovery out of order still counts. Polling reconciles existing stage and chain flags; it does not manufacture provenance.

**UI.** A journal reached through a `MainButtonDef`, offering a graph and a linear accessible view. Each rumor records its source and investigation direction. A letter can introduce a major thread; ordinary node updates remain quiet.

**Registration.** Content declares nodes, rumor sources, and edges. Validation rejects important entries with no incoming hint path or initial seed. Saves retain learned fact IDs and source records, not graph coordinates as gameplay state.

**Tier.** `RM_` rumor/fact framework; `RUT_` authored connections and presentation. `RSW_` packs may add reusable Star Wars discoveries separately.

**Biggest risk.** Dependence on authored clue routes. One missed source can conceal a whole capability. Important features need alternative sources or an explicit player-requested hint.

---

**3. Jawa Field Codex — exploration through investigation**

**Experience.** Encountering something creates a partial record. Studying or interacting with it fills practical notes. The journal becomes a useful reference for creatures, materials, inscriptions, technologies, and unusual processes.

**How entries become known.** Proximity or eligible observation reveals a partial entry. Broad section introductions announce that subjects remain unrecorded. Descriptions advance from observation to explanation using LoreStages.

**Detection.** Encounter predicates require an unfogged subject and an eligible observer under the chosen observation rule. Study completion and mechanic-specific interactions deepen entries. For objects that never receive a study job, successful use is an alternative. Spatial checks should run through relevant cached objects, not every pawn against every thing.

**UI.** A codex main tab, with an optional inspection-pane link for encountered subjects. New-page messages replace frequent letters; the journal retains findings after the subject disappears.

**Registration.** Extensions identify subjects and accepted evidence: observe, study, harvest, tame, breed, operate, or read. Processes such as weather need standalone entry defs rather than a forced `ThingDef`.

**Tier.** `RM_` encounter/evidence codex; `RUT_` subjects, study rules, and staged prose.

**Biggest risk.** An extra study chore attached to everything. Found rites already have inscription study; this codex should consume that result and link to the Rites tab.

---

**4. Scavenger’s Apprenticeship — exploration through capabilities**

**Experience.** A capability tree presents concrete experiments: make a canal function, complete graffiti, breed vermin, use a newly available buildable, or take the ship somewhere unusual. Each entry explains an attainable next action.

**How entries become known.** Early capability groups are visible in plain language. Later nodes become hinted when relevant prerequisites or opportunities appear. Story-sensitive nodes use riddles; ordinary features can be explicit.

**Detection.** Completion primarily uses successful-action events, not possession or construction. Building a canal is distinct from operating it. Harmony can observe vanilla crafting or research; custom systems emit their own success signals. Polling establishes opportunity and prerequisites, while saved flags retain successful participation.

**UI.** A `MainTabWindow` with capability branches, concise instructions, and optional pinned goals. Completion produces a toast or message. Existing unveiling letters remain responsible for their narrative moments.

**Registration.** Each feature declares its first meaningful use and prerequisite hints. Tree placement controls presentation, while completion remains possible out of order. Nodes can link to research, rites, or the appropriate command surface.

**Tier.** `RM_` capability tracking and tree UI; `RUT_` campaign curriculum.

**Biggest risk.** Becoming a tutorial checklist that prescribes play. It is strongest at “go use this mod feature,” but weaker at preserving mystery and atmospheric discoveries.

---

**5. Clan Inquiry Dossiers — exploration through deduction**

**Experience.** The clan gathers evidence around questions: what an inscription describes, why a landscape behaves strangely, or which divine relationship explains a phenomenon. The player connects evidence and records a conclusion.

**How entries become known.** A dossier begins with an unanswered question, not a named secret. Finding enough evidence changes its status to “You can investigate this now.” The answer remains unrevealed until deduction or the existing scripted reveal confirms it.

**Detection.** Defs declare evidence bundles, accepted conclusions, and authoritative confirmation events. Harmony/direct callbacks record actual clue acquisition; polling reconciles persistent clue flags. Player hypotheses are scribed separately from verified discoveries. A guessed answer must never trigger `HiddenItemsManager` or advance an unveiling chain.

**UI.** A journal of dossiers, evidence cards, source links, and player notes. Major confirmations may issue letters; collecting every clue does not need a notification.

**Registration.** `RUT_` dossier defs reference discovery entries and existing chain/LoreStages milestones. Coverage validation checks that clues are obtainable and conclusions have a legitimate confirmation source. Simple capabilities still require straightforward records.

**Tier.** Prefer **`RUT_`-only dossiers** initially, consuming the generic `RM_` evidence service. The pantheon’s deduction grammar is campaign-specific.

**Biggest risk.** Creating a second puzzle game beside the existing unveilings. This adds substantial writing and validation work and is the weakest fit for ordinary capabilities such as graffiti.

**What I would choose for Utinni**

Pick **the Atlas**, with staged hints and explicit first-use records where appropriate. Its structure already exists in the biome scorecards; it can cover atmosphere, creatures, theology, technology, and mechanics without pretending they are all the same activity.

Keep three things independent:

| Dimension | Example states | Purpose |
|---|---|---|
| Awareness | Unlisted → hinted → identified | Communicates existence without immediately explaining it |
| Evidence | Encountered, studied, interpreted | Records what the clan actually learned |
| Participation | Untried → used successfully | Encourages playing with a capability |

Availability is another property: a feature can be unavailable in this world or absent from the active mod set. It should not look like an unfinished task.

Not every entry needs all three dimensions. Soundscape can be an encounter; technology can have knowledge and use; a god’s unveiling is a scripted milestone. Avoid one universal “complete” flag.

These are illustrative entry designs; exact success conditions must be supplied by their owning mechanics:

| Entry | Initial invitation | Evidence that should count |
|---|---|---|
| Canals/pits | “The clan can reshape how water moves here.” | Successful functional outcome emitted by the mechanic; construction alone records only construction |
| Graffiti | “The clan can leave its words on the world.” | First completed graffiti action |
| Sea-floor layer | A staged ship or cartography clue | Actual clan arrival on the sea-floor layer; discovering its existence remains separate |
| Regrowing giant tree | “Some roots refuse a final harvest.” | First encounter, then witnessed regeneration; spawning a mature tree proves neither regeneration nor understanding |
| Vermin breeding | “Even vermin have uses for a patient scavenger.” | A successful breeding outcome identified by that system |
| Found rite | Existing veiled invitation | Existing inscription-study/learned flag; link to the authoritative Rites row |
| God unveiling | Veiled presence or chain lead | Authoritative unveiling milestone |
| Weather/soundscape | Broad biome promise | Qualified experience on an occupied map; sound needs a text-accessible equivalent |

For soundscape, do not claim the player literally heard audio. Record that the corresponding experience was presented under suitable conditions, including for players using muted sound.

After all nine unveilings, **retire their veiled onboarding rules and retain their records**. That does not automatically reveal unrelated technologies, rites, or remaining mysteries.

LoreStages should continue supplying staged labels and descriptions. It is the text authority; the journal adds navigation and evidence. **Unsure:** whether its present tables already support every desired per-entry reveal rule. A global lore-stage advance and a specific local encounter may both be required.

Spoiler protection must cover titles, icons, tooltips, search results, destination names, and links. A riddle description is ineffective if the neighboring icon displays the secret creature.

**Why a small framework rather than VAE**

VAE is a reasonable choice for ordinary achievement cards with existing tracker types. Its 1.6 publication and gravship support make it more viable than the initial document suggests.

I would still choose a small framework because Utinni’s central requirements are **staged awareness, provenance, existing-system links, and recognition of bespoke mechanics**. VAE would supply useful tracking machinery, but much of the distinctive discovery experience would still need to be built. Its supported custom-tracker contract also remains uncertain.

Keep the proposed split narrow:

- **`RM_`:** entry schema, evidence storage, event routing, reconciliation, basic journal infrastructure, validation, settings.
- **`RSW_`:** reusable Star Wars discovery content only where it genuinely applies beyond Utinni.
- **`RUT_`:** campaign catalogue, nine marks, biome associations, pantheon, Antiquities, rites links, and hint prose.

A `RUT_` overlay can associate an existing `RM_` or `RSW_` feature with a campaign biome. Lower-tier mods should not need knowledge of Utinni.

The catalogue cannot remain complete through registration alone. Require every new campaign feature to declare **its invitation, evidence, meaningful use where applicable, and availability conditions**, or an explicit exclusion. The coverage report should make omissions visible to authors.

For Mod Settings, provide understandable presets—**Mystery, Guided, Explicit**—plus notification controls, pinning, completed-entry visibility, and optional counters. I recommend **Guided** by default. Ordinary discoveries should use quiet notifications; `Find.LetterStack` should be reserved for discoveries that merit a durable letter.

Rewards should be a separate optional executor, with **no points economy**. If enabled, each eligible entry gets a small authored reward and a scribed claim state. Recommend future discoveries only: toggling rewards on should not silently grant a campaign’s worth of accumulated gifts.

**Five decisions for the owner**

1. **What should players know at the start?**  
   Broad promises for every category give reliable coverage. Rumor-only revelation preserves mystery but risks missed capabilities. Explicit names and instructions make the catalogue easiest to use.

2. **What deserves recognition?**  
   First encounters suit creatures and atmosphere. Successful use suits capabilities. Study suits lore and technology. Approve this mixed approach, or accept the weaker meaning of one universal completion rule.

3. **How far does catalogue coverage extend?**  
   Utinni content plus the unique `RM_`/`RSW_` capabilities used in the campaign is manageable. Covering every active third-party feature is much broader and requires maintained adapters and authored metadata.

4. **How much reusable infrastructure is worth maintaining?**  
   A small `RM_` framework with `RUT_` content supports future campaigns. `RUT_`-only is faster to specialize. VAE is attractive if conventional cards are sufficient, with custom discovery integration still to verify.

5. **Should optional rewards ship initially?**  
   Reserving them for later keeps the first version focused. Shipping tiny rewards behind an off-by-default toggle adds immediate choice, but requires balancing and save-safe delivery. If included, choose future-only eligibility or an explicit backlog-claim option.