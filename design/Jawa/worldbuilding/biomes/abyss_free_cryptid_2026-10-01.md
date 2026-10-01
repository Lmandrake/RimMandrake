# The Abyss's free-tier cryptid: the Nhaleth (2026-10-01)

Item: `ABYSS_FREE_CRYPTID_1` (FOUNDRY). Sitting: `BLACKCRAGS_BEDAZZLE_SITTING_1`. Sheet:
`design/Jawa/worldbuilding/biomes/abyss.md` §6 ban 7 and §8. Review:
`design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §2, "The word
'Forsaken' survives elsewhere", and §6 card item 1.

## 1. Ruling

The owner typed this on 2026-10-01 at 07:32 PDT, answering card item 1's cryptid question:

> *"For the Star Wars part we had already written rumors that they might be the with races
> themselves. For the free version we would make our own. Do so."*

He then corrected how it had been read, also typed on 2026-10-01:

> *"That's not what I said the Star Wars versions will whsisper of the sith not the Rakatans."*

Together these mean:

- **Star Wars tier (Utinni):** the cryptid stays **"the Forsakens"**. The whisper is that they
  may be **the Sith** themselves. They are **not** the Rakata. The sheet's §8 already says
  this: *"that they are the Zabraks, the 'Nightbrothers', bringing this strangeness with their
  twisted Sith associations."*
- **Free tier (`RM_`, `mandrake.rm.biomes`):** the cryptid gets its own invented people,
  defined below. It carries no Star Wars word and no Star Wars dependency.

## 2. The name

**The Nhaleth** (pronounced *n'HAH-leth*). The singular and plural are the same: "a Nhaleth",
"the Nhaleth". The adjective is "Nhaleth" as well ("a Nhaleth circle").

The opening *nh-* is a hush, the sound someone makes when they don't want to say a word out
loud. That suits a name that is only ever whispered. It sits beside the biome's harsher cast
names (vrakk, durrgak, ghorrumak, skarnix) and doesn't sound like one of the animals.

**Collision check:** `git grep -il` over `src/`, `design/` and `infrastructure/state/items/`
found 0 hits for this name or any runner-up below. The probe `gharrek` returned 3 files and
`rakata` returned 250, so the search can find words that are there. A search of the
Wookieepedia search API returned 0 results for each name. The probe `rakata` returned Rakata
pages, so the API was answering.

**Runner-ups** (each passed both checks; any one can be swapped in for the name):

1. **the Ommerai**: softer and more ceremonial, like a people with rites.
2. **the Sennoth**: colder. It reads as a family name, a lineage.
3. **the Thessuin**: hissed rather than hushed. It is the most alien of the four.

## 3. Who the Nhaleth are (free tier)

This keeps the sheet's §8 shape, because it is the owner's 2026-09-06 ruling and only the
whisper changes between tiers:

- They are **visitors who come to the Abyss for the Dark**. The Dark is rare, and they seek it.
  They don't live here. They aren't organized or present enough to treat as a faction, and
  nobody alive has seen one. They are the Abyss's Loch Ness monster: nobody credible swears to
  them, and everybody believes in them a little.
- Some of the biome's creatures seem **suspiciously suited to this one place, as though someone
  put them here**. This is the only line both tiers share word for word.
- **The free-tier whisper, the fear nobody says out loud:** *that the Nhaleth are not visitors
  at all. They are whoever stays.* On this reading, everyone who lived in the Dark long enough
  stopped needing light, stopped coming home, and now comes back only to tend the places they
  left. People whisper it so that it won't come true. For a colony that has settled in the
  Abyss, the rumour is about them. That makes it the richest free-tier option, and it needs no
  other franchise to work.

Why not invent a lore race with a homeworld and a history? The rule for an `RM_` biome is to be
as rich as the campaign version, not thinner. The campaign's whisper has force because it points
at something the player fears (the Sith). The free tier needs something with the same pull, and
the player's own colonists are the one subject every player already cares about. A made-up
history would be thinner, not richer.

## 4. Signs, never sightings

Ban 7 still holds in both tiers: **no Nhaleth faction, pawn or structure that is certainly
theirs, and no on-screen Nhaleth.** The owner's planet-wide rule also holds: **nothing vanishes
without a sign the player can read.** Every sign below can be **explained away**, and most of
them by an animal already admitted to the biome:

| Sign | What the player sees | The deniable explanation | Builds on |
|---|---|---|---|
| **Rumor-sites** (sheet §8) | 0–2 per Abyss map at generation: a stone circle, a den stocked too neatly, a tidy cache of salvage | The durrgak (admitted 2026-09-30) lays obsidian rings and neat caches. *"Someone was here, and it never says who."* | `ABYSS_DURRGAK_BUILD_1`. Rumor-sites use the **same placement output** as durrgak work, so neither can be told apart from the other with certainty |
| **The exchange** | An item left **unwatched** on a stone circle during the Dark is sometimes **gone** by morning. In its place is a small cache in a ring, plus a letter that says something took it and something was left. Nothing is ever taken while a colonist can see the circle. | A tamed or wild durrgak tidies (its tamed behaviour). The swap is a sign, never a disappearance: the ring and cache are the sign | durrgak tidy job |
| **A clear pocket around nothing** | Very rarely, a clear pocket in the Dark opens over empty ground with no heat source, then closes | Heat opens pockets, and maybe something warm was there | `ABYSS_DARK_BUILD_1` (one hook in its pocket logic) |
| **The whisper** | A rare social interaction between colonists on an Abyss map, "whispered of the Nhaleth". After a long stay, an occasional dream memory: *"Dreamt I didn't need the light."* | It's talk and dreams. Nobody saw anything | the free-tier whisper (§3) |
| **Tales** | Art made on an Abyss map can depict the Nhaleth, always unseen: a figure at the edge of the glow, or an empty ring | Art is not evidence | grammar rules (§5) |

⛔ **Not owed:** a body, a corpse, a pawn of any kind, a raid, a quest giver, or a reveal. If a
build gives the player certainty, it breaks ban 7.

## 5. How the two tiers split

**The layering already in use:** a free def carries the free label and text, and a Utinni
patch in `src/RimUtinni/UtinniPatches/Patches/` replaces the label and description with
`PatchOperationConditional` gated on the def's own xpath. See `Abyss_Rename.xml` and
`RotSpecies_NamesAndSizes.xml`. It is label-only: no defName, stat or art field changes. The
cryptid uses the same pattern.

- **The name lives in one place.** Proposed: a `RulePackDef` `RM_AbyssCryptid` whose rules
  hold `cryptid_name` → "the Nhaleth" and `cryptid_whisper` → the §3 whisper. Every grammar
  consumer resolves through it: the letters, the interaction, the art tales and the thought
  text where the engine supports it. Static `description` fields can't resolve grammar, so
  each of those (for example the rumor-site ThingDefs) also gets its own Utinni replace.
  ⚠️ FOUNDRY must check against RimSage which consumers really resolve a custom rulepack
  symbol. This doc doesn't assert it.
- **defNames are neutral, never the name** (`RM_AbyssRumorCircle`, not `RM_NhalethCircle`).
  Players never see a defName, and a neutral one lets Utinni rename the label without leaving
  "Nhaleth" in the campaign build.
- **Utinni patch `Abyss_CryptidForsakens.xml`:** replaces `cryptid_name` with "the Forsakens"
  and `cryptid_whisper` with the Sith whisper (sheet §8: the Nightbrothers and their Sith
  associations). It also replaces each static description that names the cryptid. ⛔ **No
  Rakata, Rakatan, ancients or terraformer wording in that patch.** The owner's correction rules
  it out.
- **Settings:** one toggle in the unified biomes mod, "Abyss: cryptid signs" (default on),
  covering rumor-sites, the exchange and the whisper. This follows `MOD_OPTIONS_RETROFIT_1`.
  With it off, the biome is whole and simply has no cryptid.

## 6. What already exists in src/

All of this was searched on origin/main at `0989f63a3`:

- **No cryptid content is built in either tier.** `git grep -i cryptid` over `src/` finds 0
  files, and "Forsakens" appears in no def as a cryptid.
- `src/RimMandrake/Abyss/` is a BiomeDef, a worker and a settings stub. Its `About.xml` (around
  line 42) says the Forsakens *"are campaign plot content and stay in Utinni entirely."* That
  stays true for the Star Wars name. The free tier now owes its own cryptid, so the
  description is owed a line (listed in §8).
- **Machinery admitted but not yet built** that this item depends on: `ABYSS_DURRGAK_BUILD_1`
  (the ring and cache placer, and the tamed tidy job) and `ABYSS_DARK_BUILD_1` (clear pockets).
  Neither has shipped yet, so this item **builds after them** or alongside them.

## 7. Build work owed (`ABYSS_FREE_CRYPTID_1`, FOUNDRY)

1. `RulePackDef RM_AbyssCryptid` (name and whisper), in `src/RimMandrake/Abyss/`.
2. Rumor-site defs (a stone circle, a stocked den, a salvage cache) and a map-generation step
   that places 0–2 on `RM_Abyss` and `RUT_Abyss` maps, reusing the durrgak's placement code.
3. The exchange: an unwatched item on a circle during the Dark is replaced by a ring and cache,
   and a letter is sent. It never fires while a colonist can see the circle.
4. A no-source clear pocket hook in the Dark's pocket logic. This is coordinated with
   `ABYSS_DARK_BUILD_1` and should not fork it.
5. An `InteractionDef` for the whisper, and a `ThoughtDef` for the long-stay dream memory.
6. Art-tale grammar rules for the Abyss.
7. The settings toggle.
8. A Utinni patch, `Abyss_CryptidForsakens.xml`: the rename to the Forsakens with the Sith
   whisper, gated per def, and no Rakata wording.
9. Offline build, selftests and `validate_patch.py`. A live look is a joint session with the
   owner.

## 8. Docs that tie the cryptid to the Rakata (BENCH to correct; not edited here)

The owner's correction says the Star Wars whisper is **Sith, not Rakatan**. These files say the
biome's "Forsakens" race and the Rakata ancients are the same people. ⚠️ Separate this from his
**2026-08-20 ruling** that *"the Forsaken"* is our people's exonym for the Rakata
(`VQEQuestText_AreForsaken.xml`). That ruling stands. What the correction rules out is merging
the **cryptid** into it.

- `design/Jawa/reconciled_lore/03_deep_history.md` lines ~9–10: *"The `AB_RockyCrags` biome's
  own description of 'a mysterious humanoid alien race simply known as Forsakens' is the same
  people."*
- `design/Jawa/worldbuilding/what_the_machines_are.md` lines ~168–178: *"Whose world was it? The
  Forsakens'."*
- `design/Jawa/worldbuilding/hydrology_and_fire_ecology.md` line ~528: the crags' terraforming
  race "the Forsakens (true as the first stage…)".
- `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_RustCathedral.xml` line ~45, in a comment:
  *"canon-sitting naming propagation (Forsakens=Rakatans=Ancients)"*.
- `design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §2: the review
  frames the cryptid against the Rakata exonym. That framing is fine as a description of a
  naming collision, but it is not a lore tie.
- The task brief for this doc also said the Star Wars rumour was that they are "the ancient
  terraforming race". **That reading was wrong**, and the owner's correction above replaces it.

**One free-tier leak to rule on:** `src/RimMandrake/Inhabited/Defs/CastRosters/CastRoster_DROIDS.xml`
line ~657 is in `mandrake.rm.inhabited` (the free tier) and has a droid who *"tells the story of
the Forsakens and the First Waking"*. That is a campaign name in a free mod. Either the
storyteller says "the Nhaleth", or Utinni relabels the line. BENCH should decide which.
