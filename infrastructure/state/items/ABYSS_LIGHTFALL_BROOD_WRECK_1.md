# ABYSS_LIGHTFALL_BROOD_WRECK_1 — Lightfall's bottom: the dragons' brood, and the wrecked ship in the wall that repairs yours

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Review: `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` section 9 (Lightfall ruling, 2026-10-01 07:42 PDT). Options: `Transient/abyss_lightfall_2026-10-01/lightfall_options.md` (option C and GPT option E; GPT's prompt and answer beside it). Sitting: `BLACKCRAGS_BEDAZZLE_SITTING_1`. Rule: every mod ships Mod Settings; the free `RM_` tier carries invented content.

## spec

One place, two halves, both at the bottom of Lightfall.

**The Brood (option C, decision taken by question card).** The storm dragons (the ghorrumak, which becomes our own invented creature under `ABYSS_DONOR_BEASTS_FREED_1`; use the owner's name "Summ the All-Render" (`RUT_SummAllRender`), not ghorrumak) nest at Lightfall's bottom among giant bones. A living brood-mother sleeps coiled round a clutch of eggs. The player steals an egg past the sleeping brood-mother (light and noise wake her; her stirring and a low rumble are readable signs, but the exact threshold may be learned by save/load — owner 2026-10-01: *"It's ok to require load/save to learn the boundry, that's pretty normal in these games."*). Carrying the egg brings Witchfire storms home to the colony map (storm call is `ABYSS_DARK_BUILD_1`'s weather; the thunder is the readable warning, and one dragon comes looking). The egg can be returned at the lip or defended. Hatch it and raise your own beast: slow, ruinously hungry, regenerating, heavy food bill and long maturation (balance is the risk). Its bone (huge, light, stuffable) comes from the bone field. Not picked: the Sink, the Lowered, the Mercy Engine, the Lantern Tide.

**The Ship in the Wall (GPT option E, reshaped by his typed words).** A wrecked rescue gravship lies driven into the chasm wall in the brood's lair. It is NOT a second ship and does not become the player's ship. It is a SALVAGE SITE. His words, typed: "Improve the crashed ship. You can’t have two ships but you can cannibalize that one to improve yours. A rich haul. But only then do they discover that their ship only wants certain parts. It likes what it is and doesn’t want deep redesign. Just repair. This is a chance to restore much of its glory. While the sleeping dragons threaten to pummel you."

Read as:
- The player strips the wreck to improve their own gravship: a rich haul (parts, components, systems).
- The discovery comes only AFTER the haul is in hand: the player's own ship accepts only certain parts. It likes what it is and refuses deep redesign. Salvage REPAIRS and restores its lost glory (damaged or degraded ship systems, fittings and condition brought back), it does not reconfigure it. Parts the ship will not take must read as refused in plain words (no silent failure), and the unaccepted remainder is still loot.
- All of it happens inside the brood's lair: the dragons sleep, and noise and light from salvage work (cutting, hauling, power) risk waking them to pummel the party. The two halves share one wake-pressure system.

**🔴 NOT FANTASY DRAGONS — and greed wakes something unkillable (owner, typed, 2026-10-01).** His words: *"We must be careful with those dragons to make sure they don't turn into fantasy dragons. They must remain starwars-esque beasts from an alien world. We need to carefully tune and balance that risk down there: get too greedy to steal from the crashed ship, and you wake an essentially unkillable thing. It's ok to require load/save to learn the boundry, that's pretty normal in these games."*
- **Alien megafauna, never fantasy dragons:** no fire breath, no hoard, no wings-and-scales heraldry, no "dragon" in any player-facing text or defName. Read them like a krayt, a rancor or a zillo beast — a creature from an alien ecology with a biology (how it feeds on the Dark, why it nests here, why the storms answer it). Art briefs say so explicitly.
- **Greed is the dial.** Salvage and egg theft feed one wake meter; a modest haul is safe, a greedy one wakes the brood-mother, and **awake she is essentially unkillable** — the correct response is to flee, not fight. Tune so the line exists and is reachable, not so it is telegraphed to the last part.
- **Learning the line by save/load is acceptable** — readable signs (stirring, rumble) are still owed, but they need not reveal the exact threshold.

**🔴 The bond needs a great bone aboard; the beast is bane and boon (owner, typed, 2026-10-01).** His words: *"Perhaps you MUST have one of those great bones on your ship in order for the beast egg to bond with you? It will not imprint without it present. And the beast should be a bane and a boon. It should be very hungry and very aggressive, killing wildlife indescriminantly and semi-randomly. But it should also be deeply tough and powerful. UV sensitive but able to see in darkness."*
- **Imprinting requires a great bone on the player's ship.** One of the bone field's great bones must be hauled up and installed aboard the gravship; without it present the egg hatches but **will not imprint** (it does not bond and stays wild). This makes the bone field a second, separate retrieval from the lair. Say plainly in the egg's inspect text why it has not bonded.
- **Bane:** very hungry and very aggressive — it kills wildlife indiscriminately and semi-randomly, emptying the colony map's game and endangering tamed animals. Not reliably controllable.
- **Boon:** deeply tough and powerful; a fighter worth the cost.
- **UV-sensitive, sees in the dark:** suffers in sunlight/UV (penalties or harm outdoors in daylight; cf. Biotech's UV-sensitivity genes for a vanilla model) and is unimpaired by darkness and by the Dark (`ABYSS_DARK_BUILD_1`) — night and the Dark are when it is at its best.

Open for FOUNDRY/BENCH to ground in design (his typed text decides intent, these decide shape): which parts the ship accepts and why (a short authored list, signalled before salvage so the surprise is the ship's character, not a lost run), what "glory" restores mechanically, and the wake-pressure rules.

## existing lore and mechanics found (2026-10-01, cited so nothing is re-invented)

- No "the player's gravship has preferences/personality" mechanic exists in `src/` or the item set; none found by search. The nearest authored ideas: the Cradle-Mind (Kolyska), "a half-restored gravship grav-controller ... the ship's slow, ancient awareness" (`design/RimMandrake/llm_voice_preauthoring.md`, LLM persona text only, not a mechanic); `design/Jawa/art/gravship_wear_pass.md` (aspirational wear and rust look of the Jawa ship); `BIOME_SHIP_CONTRIBUTIONS_1` (every biome owes something to build INTO the ship; this item is the Abyss's answer, the repair haul).
- Wrecks as set pieces already planned: tile augmentation matrix SV28 "Beached gravship" (`design/Jawa/worldbuilding/tile_augmentation_matrix.md`), and `ABYSS_HIDDEN_SHIP_PROBES_1` (the player's ship hidden in the Abyss; this wreck is not that, but share art language).
- Gravship hook code lives behind `HarmonyPatch_DoGravship.cs` (`design/Jawa/worldbuilding/row8_build_order.md`); the pocket-map and cross-map transfer GPT proposed is NOT needed, since the ship is not transferred.
- The brood's creature art is NOT existing donor art; see `ABYSS_DONOR_BEASTS_FREED_1`.

- **Landscape-sized brood-mother (owner, typed 2026-10-01):** *"the brood mother must be landscape sized."* Summ the All-Render is the size of terrain: a huge drawSize or a multi-cell structure-like presence; feasibility is FOUNDRY's to decide.
- **The summing grows constantly, problematically (owner, typed 2026-10-01):** the juvenile/tamed Summ (`RM_Summing`) is *"not so little"* and keeps growing through its whole life; size, hunger and space problems keep escalating.

## criteria

- Descent to the lair, bone field, brood-mother asleep with a readable wake warning (stir, rumble) before any lethal wake.
- Egg theft; carrying it triggers Witchfire storms at home; return-at-lip and defend options; hatching yields a tameable beast with a heavy food bill and long maturation.
- Brood-beast bone stuff.
- Wreck salvage yields a rich haul; the player's ship accepts only a defined set of parts and restores condition; refused parts say so; no second gravship exists.
- Salvage noise and light add wake pressure.
- Egg imprints only with a great bone installed on the player's ship; without it, it hatches wild, and the inspect text says why.
- Brood-mother is landscape-sized (terrain scale), feasibility decided by FOUNDRY.
- The summing never stops growing: size, hunger and space needs escalate over its life, with no plateau.
- Tamed beast: very hungry, very aggressive, kills wildlife indiscriminately and semi-randomly; deeply tough and powerful; UV-sensitive (daylight penalty/harm); sees in darkness and the Dark unimpaired.
- Greed threshold: past it the brood-mother wakes and is effectively unkillable (flee, not fight); the threshold may be learned by save/load.
- No fantasy-dragon tells anywhere: no fire breath, no 'dragon' in labels/defNames/descriptions; alien-beast biology in descriptions and art briefs.
- Mod Settings: toggles for the brood, the wreck, and a beast-hunger slider; all off degrades gracefully.

## links

- `ABYSS_DONOR_BEASTS_FREED_1` (the dragon becomes ours: new name, new art, zero donor dependency).
- `ABYSS_DARK_BUILD_1` (Witchfire storm call).
- `ABYSS_HIDDEN_SHIP_PROBES_1`, `BIOME_SHIP_CONTRIBUTIONS_1` (ship contribution).

## verify

Offline build and selftests green; flight/storm/wake behaviour live proof is a joint session with him present.

## built (2026-10-07, FOUNDRY, offline only, never loaded)

The open shape questions, grounded by FOUNDRY (provisional numbers):
- **Wake rules** (`Source/RM_BroodWakeLogic.cs`): one meter. A salvage cut adds its part's greed (0.12; the field lattice 0.18), taking an egg adds 0.35 (putting it back near her refunds 80%), and each lit lamp within 14 cells adds 0.004 every 250 ticks. The hidden line is rolled once per lair in 0.85–1.15 times the "how deeply she sleeps" slider and saved, so it can be learned by save/load. Signs: stirring at 45% (message and thunder), rumbling at 70% (letter and camera shake). A single step that would jump past the line from below the rumble announces the rumble first and wakes her a few seconds later, so a sign always comes before the wake. Quiet days take off 0.05 a day, but never below half the peak. Striking her wakes her. Awake she takes 3% of incoming damage and feels no pain; flee.
- **The ship accepts** four fittings: hull plating, conduit loom, thruster liner and seal gaskets. Fitting one repairs worn buildings on substructure, up to 400 HP spread worst-first. That repair is the "glory": restoring what has worn, never redesign. **It refuses** three: the bridge console, the foreign grav-field lattice and the rescue berth. Their use gizmo is disabled with the reason in plain words, and they can be sold or smelted. The wreck's description warns that the cutting is loud. Which parts fit is learned from each part's description once it is in hand.
- **Placement**: a global genstep (MapCommonBase patch) that checks for itself. It builds on a tile that has the free tier's `RM_BroodLair` mutator (rare, Abyss only), or whose landmark def carries `RM_BroodLairExtension`. UtinniPatches puts that extension on `RUT_Lightfall`. Tile 9023 already holds the landmark, so a mutator added now would never reach it.
- **Landscape-sized**: while asleep she is a 7x7 impassable building drawn about 15 cells across. Awake she becomes the `RM_SummAllRender` pawn (an RM_Summ, age 150, drawn 15 across), named "the All-Render", and is permanently manhunter.
- **Naming deviation**: the defName is `RM_SummAllRender`, not `RUT_SummAllRender`. The name is invented, not IP (Q11a), and the whole kit lives in the free Abyss mod. Only the Lightfall marking is campaign content.
- Bond: an egg hatches (20 days) a summing that imprints only if a player-owned `RM_SummGreatBone` stands on substructure on that map. The great bone has `PlaceWorker_OnSubstructure` and is minifiable; the bone field has 4–6 of them and heaps of `RM_SummBone` (light, Woody-category stuff). Bane: a player-owned summ (`RM_CompSummBane`) hunts wild animals semi-randomly (18% per check when fed, 65% when hungry) and sometimes turns on a tame one. It carries `RM_SummRuinousHunger` at the slider's severity. Growth without a plateau already shipped (Elder/Ancient life stages).
- A stolen egg kept on a home map calls a Witchfire storm every 5–9 days, and a manhunting summ comes about 6000 ticks later.
- Settings: lair, wreck, egg storms, bane toggles; hunger and sleep-depth sliders.

L0 proof: `validation.py` BROOD LAIR static PASS; `Utils/selftest_abyss_brood.py` (C#, 127 checks); `Utils/selftest_abyss_brood_static.py` (planted breaks 12/12); validate_patch 0 errors (MapCommonBase 1 hit; the Lightfall nomatch branch hits RUT_Lightfall).

Owed: **L1** a load with no errors from these defs (an empty-ingredient salvage recipe, Graphic_Multi on a building, the egg's StackCount graphic). **L2** generate a map with the mutator and read the lair, then a salvage bill run, a refused-part gizmo reason, an egg hatch with and without a bone aboard, and the storm at home. **L3** a joint session with the owner to judge scale, feel and the greed line. **Art**: every texture is a placeholder (sleeping brood-mother, egg, great bone, wreck, seven fittings).
