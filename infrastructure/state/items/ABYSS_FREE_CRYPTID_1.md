# ABYSS_FREE_CRYPTID_1 — the Nhaleth: the Abyss's free-tier cryptid (Utinni relabels to the Forsakens)

Biome: the Abyss (`RM_Abyss` in `src/RimMandrake/Abyss/`, composed into `mandrake.rm.biomes`; campaign twin `RUT_Abyss`). Spec: `design/Jawa/worldbuilding/biomes/abyss_free_cryptid_2026-10-01.md`. Sitting: `BLACKCRAGS_BEDAZZLE_SITTING_1`, card item 1 (cryptid name).

## spec

Owner, typed 2026-10-01: free tier gets its own invented cryptid; the Star Wars tier keeps "the Forsakens", whose whisper is the SITH (corrected the same day: "the Star Wars versions will whsisper of the sith not the Rakatans"). Never tie the cryptid to the Rakata.

Free tier: **the Nhaleth** — visitors who come for the Dark, never seen; whisper "they are whoever stays". Ban 7 holds (never on screen, never certain); nothing vanishes without a readable sign. Build list = spec §7: RulePackDef `RM_AbyssCryptid` (name + whisper, single source), rumor-sites (0–2/map, sharing the durrgak's placement so neither is certain), the exchange (unwatched item on a circle in the Dark → ring + cache + letter), no-source clear pocket hook, whisper InteractionDef + long-stay ThoughtDef, art-tale grammar, settings toggle, Utinni `Abyss_CryptidForsakens.xml` (→ "the Forsakens" + Sith whisper, no Rakata wording). Neutral defNames, never the cryptid's name.

Depends on `ABYSS_DURRGAK_BUILD_1` and `ABYSS_DARK_BUILD_1`.

## criteria

- No pawn/faction/certain structure of the cryptid exists in either tier.
- Name appears in exactly one RM_ def plus per-description Utinni replaces; campaign build shows "the Forsakens" with the Sith whisper and no "Nhaleth" text.
- Settings toggle off → biome whole, no cryptid content.

## verify

Offline build + selftests + validate_patch.py; live look is a joint session with the owner.
