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

## criteria

- Descent to the lair, bone field, brood-mother asleep with a readable wake warning (stir, rumble) before any lethal wake.
- Egg theft; carrying it triggers Witchfire storms at home; return-at-lip and defend options; hatching yields a tameable beast with a heavy food bill and long maturation.
- Brood-beast bone stuff.
- Wreck salvage yields a rich haul; the player's ship accepts only a defined set of parts and restores condition; refused parts say so; no second gravship exists.
- Salvage noise and light add wake pressure.
- Egg imprints only with a great bone installed on the player's ship; without it, it hatches wild, and the inspect text says why.
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
