# mondayreviewitems — design questions waiting on the owner

Assembled 2026-09-21 by BENCH, from a four-way sweep of the 247 live item files
plus the ledger's `needs=owner` flag. **Art/curation review sheets are deliberately
excluded** — this is the design-decision list only.

⚠️ Items decay. `python3 src/RimMandrake/rimflow/cli.py show <ID>` before acting on
any row; a question ruled since this file was written is not a question.

---

## 1. The big one, and it is ready

**`CAMPAIGN_STORY_SITTING_1` Phase B — the campaign story sitting.**

Phase A is DONE: `design/Jawa/campaign/CAMPAIGN_ARC_GATHER.md` (71 sourced entries,
committed `c5676331a`) holds the spine, places-with-purposes, 7 mentioned-but-unused
threads, the reveal moments, the transition tones, and 8 listed-not-resolved
contradictions.

The method is specced in the item: cards of 2–4 options, every option citing which
existing fragments it stitches, **no new places / factions / mechanisms unless a card
asks and says why the existing pieces cannot carry the stitch**, batched 4–6 by act,
with a running "the arc so far" shown between batches.

`D:\Luke\dev\Rimworld\design\Jawa\campaign\CAMPAIGN_ARC_GATHER.md`

---

## 2. Drafted and waiting — minutes each

| item | the decision |
|---|---|
| `BIOME_MOD_SPLIT_EXECUTION_1` | **4 biome names**, each with 4–5 candidates + a recommendation. Unblocks the 26-mod biome split. Drafts: `D:\Luke\dev\Rimworld\Transient\biome_name_drafts_2026-09-21.md` |
| `ARIDSHRUBLAND_SHIPPING_NAMES_1` | 5 names shipped live under working names: the fuzz, the giant, the tunnel snake, venomvine, the Stall/the Gale |
| `STAGGERSEED_SHIPPING_NAME_1` | 1 name; the plant is built and blocked only on this |

---

## 3. One-question cards

| item | the question |
|---|---|
| `SCRAPNEST_BIRD_BASE_THEFT_1` | Do the scrap-nest birds steal from the player's base, or only hoard in the wild? (5 options drafted) |
| `MOVING_DUNES_BUILD_1` | May sand bury a base permanently, or is there a hard cap? Shipping the cap as a placeholder until ruled |
| `FLOOD_WITNESS_EVENT_1` | Does surviving the flood unlock the "plant reached the tell" warning on the home map? |
| `FLOWWORKS_DOOR_FAMILY_1` | What size is a "small creature" the cheap Sluice door holds; does the grate door stop fire? |
| `SARLACC_HABITAT_BUILD_1` | Yes/no on the four stage names: Seeker / Debtor / Collector / Paid |
| `RUST_CATHEDRAL_MECHANICS_1` | Are roach parts sellable, and does the Cathedral's spirit react to harvesting them? |
| `FEATURE_DRAWCENTER_UNVERIFIED_1` | Split-region labels: average centre, biggest piece, or one per piece — a looking decision |
| `DESERT_FAMILY_PORT_EXECUTION_1` | The desert "Rat" — one word settles a conflict left deliberately open |

---

## 4. Real design sessions (a sitting, not a card)

| item | the shape of it |
|---|---|
| `RAKATAN_ARCHOTECH_MACHINES_1` | Where relics come from, what repairs them, whether the endgame may read the reliquary, plus the 0.75 rung's name |
| `FASCINATING_WORLD_JUNK_1` | Phase 3 roster: what flavours of Star Wars wreckage replace the generic tanks/trucks/cars per region — what each was, yields, risks |
| `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` | Ten forks, none ruled: graffiti style, whether every meme gets a sigil (incl. the tasteless ones), whether anti-Imperial stencils are allowed |
| `DROID_ORACLE_VOICE_DESIGN_1` | Seven questions on droids speaking through the in-game LLM — first person or not, and whether "I remember" may use the LLM at all |
| `BAZAAR_STOLEN_GOODS_PROPERTY_1` | Ruled in principle, full pass owed: the discount, how obviously stolen an item reads, how hard the owner retaliates |
| `TECHPRINT_FACTION_GATING_1` | Which of the twelve factions are tech-aligned, to which research domains. Mechanism proven pure-XML; the mapping is not guessable |
| `KYBER_TRADE_PLOT_1` | Cards K1/K2: who else traded kyber in the old mines; does smuggling to the Rebellion erase Imperial heat |
| `SPECIES_TRAITS_OVER_APTITUDES_1` | Which species have character no skill number can carry, and get a real gene/trait instead |
| `XENOTYPE_CANON_CORRECTION_1` | The owner's own open question: how to capture Geonosian hive structure genetically |
| `UNSUBSTANTIATED_SPECIES_ABILITIES_1` | Reverse audit — every species ability the defs grant that canon does not substantiate |
| `ECOSYSTEM_PYRAMID_LAW_1` | Food-pyramid law: small critters outnumber large in every biome roster |
| `EXPLOSIVE_PLANT_GROWTH_1` | The terminal moment per biome — currently agent-invented, marked INVENTED in §3 |
| `EXTREME_DESERT_GIANT_COMMENSALS_1` | Existing giant reskinned or a new one; what the shade commensals are; whether a giant's shadow speeds caravans |
| `DESERT_SHADE_PLANTS_DESIGN_1` | The 2–3 plants that hold the desert's shaded patches by injury |
| `INHABITED_AUGMENTATION_BUILD_1` | Per-faction palette materials — every faction stuff in `palette.json` is placeholder |
| `OCULAR_OVERDRIVE_SITE_1` | The Overdrive as a named site + custom dungeon, woven into the plot |
| `DUNGEON_SETPIECE_TEXT_1` | Assailant reveal letters + 6 Forsaken vault hand-finish texts, held for the owner |
| `REACTIVE_SHIP_LIGHTING_1` | No mod owns mood lighting / reactive pulses / lights that act alive — MEASURED 2026-09-16 |

---

## 5. Borderline — sheet-shaped, listed for completeness

- **`DEEPS_FAUNA_REPOPULATION_1`** — 12 alien hydrocarbon life-forms already written
  for the Lantern Deeps, awaiting keep/cut.
  `design/Jawa/worldbuilding/biomes/rosters/lantern_deeps_repopulation_proposals.md`.
  Creature design rather than art curation, but served as a sheet.

---

## Known flag defect

Five of the section-4 items (`FASCINATING_WORLD_JUNK_1`,
`GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`, `DROID_ORACLE_VOICE_DESIGN_1`,
`BAZAAR_STOLEN_GOODS_PROPERTY_1`, `TECHPRINT_FACTION_GATING_1`) carry
`needs offline` in the ledger while being blocked on the owner's word alone, so they
are invisible to a `needs=owner` query. Re-flagging is one `rimflow needs` call each.
