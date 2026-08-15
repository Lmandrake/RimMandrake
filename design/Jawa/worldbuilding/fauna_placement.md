# fauna_placement.md — where each creature belongs

DECIDE owns this. **Append-only register.** It feeds chain step 2 (normalize
weapons · armour · **beasts**), where every one of these becomes a `wildBiomes`
or commonality edit.

**Nothing here is a keep/cut decision.** Cuts live in Cherry Picker; this file is
only about *where* a surviving creature appears and how often. Existing biome and
commonality values are treated as **irrelevant** — the whole point of step 2 is
that we reassign them.

**The planet is tidally locked.** Temperature is arc distance from the subsolar
point, not latitude — a scorched dayside, a habitable ring at roughly 34–57° of
arc, and a frozen nightside. That geography is what most of these rules key on.

---

## Water and the green edge

**Owner, 2026-08-15.** The plant-based terrain that rings a body of water gets
its own fauna — it is the one wet, living margin on a thirst world, and it should
look inhabited.

| creature | defName |
|---|---|
| agaripawn | `AA_Agaripawn` |
| agaripod | `AA_Agaripod` |
| anima colossus | `AA_AnimaColossus` |
| animalisk | `AA_Animalisk` |
| wildpawn | `AA_Wildpawn` |
| wildpod | `AA_Wildpod` |
| cactus crab | `BMT_CactusCrab` — Biomes! Caverns |
| mantrap | `AA_Mantrap` |
| mantrap | `BMT_Creature_Mantrap` — Biomes! Polluted Lands. **A SECOND, different mantrap** — both exist |
| deermoss | `MA_Deermoss` — Mythic Ages |

Alpha Animals unless noted.

**Maps that contain a body of water may also include** the atispec `AA_Atispec` and the
gomphotaria `Gomphotaria` (Megafauna).
⚠️ It ships with a companion life stage, **`AA_LarvalAtispec`**, which must travel
with it or the adult has no juvenile form.

## The frozen nightside

**Owner, 2026-08-15:** anything named for cold spawns **only** on the frozen
nightside biomes. On a tidally locked world an arctic animal on the dayside is not
a balance problem, it is a continuity error.

18 creatures carry a cold name and still exist:

| mod | creatures |
|---|---|
| **Alpha Animals** | `AA_ArcticLion` · `AA_Blizzarisk` · `AA_BlizzariskClutchMother` · `AA_FrostAve` · `AA_FrostLynx` · `AA_FrostboundBehemoth` · `AA_Frostling` · `AA_Frostmite` |
| **Biomes! Caverns** | `BMT_FrostweaverSpider` · `BMT_HoarfrostMastodon` · `BMT_Snowstalker` |
| **Core** | `Fox_Arctic` · `Wolf_Arctic` · `Snowhare` |
| **Vanilla Animals Expanded** | `AEXP_ArcticCoyote` |
| **Dark Ages** | `DA_SnowTaraal` |
| **Vanilla Quests Expanded — Cryptoforge** | `VQE_IceCrawler` |
| **Jurassic Rimworld** | `JRWCryolophosaurus` — ⚠️ a dinosaur, and the dinosaurs are on hold pending the owner's image review. The placement rule applies only if it survives |

*(`DA_ArcticOwlcat` also matched and is already cut.)*

⚠️ **The list was built from NAMES.** A cold-adapted creature with a warm name
will be missed, and a creature merely *called* frost may not be cold-adapted.
Re-derive from `statBases` comfort temperatures during step 2 rather than trusting
this list to be complete.
