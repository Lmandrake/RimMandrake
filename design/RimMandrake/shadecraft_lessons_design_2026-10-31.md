# Shade gear learned by study: the design (2026-10-31)

Item `SHADECRAFT_LESSONS_DESIGN_1`. Build item: `SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS`.
Every question was answered by the owner on the ledger; this page joins those answers and fills in
what they left to agents. Only section 1 is his. Sections 2 onward are agent decisions.

## 1. What was ruled

| Date | Way | Ruling |
|---|---|---|
| 2026-10-03 | card | Plain research always unlocks shade gear. Lessons make it faster or cheaper. |
| 2026-10-03 | card | Lessons teach ideas (keeping dew off, portable shade, deeper shade cloth). Pieces need combinations. |
| 2026-10-03 | card | The herd-crossing lesson progresses automatically for a colonist within sight of a crossing. |
| 2026-10-03 | card | Progress shows as hidden research projects (Forge spunstone pattern). |
| 2026-10-08 | card | Each hot biome teaches its own lesson for the same gear. Vanilla hidden research, not a GameComponent of its own. |
| 2026-10-09 | card | Each shade piece needs two ideas. |
| 2026-10-19 | card and words | Parasols and tents only. "Tents are just a quick structure (any roof structure will do the same)." The sun shield is gone. |

## 2. The model

**Two gear projects, always visible.** They are the plain route, and nothing hides them.

| Project (new) | Unlocks | baseCost | Tech |
|---|---|---|---|
| `RM_Research_Parasol` | `RM_Parasol` recipe | 400 | Neolithic |
| `RM_Research_ShadeTent` | `RM_ShadeTent` building | 400 | Neolithic |

**Three idea projects, hidden.** Each uses `RM_FoundTechStudy`: hidden until the colony's study
points for it reach `knowledgeToReveal`, then a letter, then ordinary research.

| Project (new) | Idea | baseCost | Reveal at |
|---|---|---|---|
| `RM_ShadeIdea_DewOff` | keeping dew off | 100 | 12 points |
| `RM_ShadeIdea_PortableShade` | portable shade | 100 | 12 crossings seen |
| `RM_ShadeIdea_DeepCloth` | deeper shade cloth | 100 | 12 points |

**Each piece needs two ideas.**

| Piece | Ideas |
|---|---|
| Parasol | portable shade + deeper shade cloth |
| Shade tent | portable shade + keeping dew off |

**What a combination buys.** When the second idea of a pair finishes, that piece's gear project is
raised to at least 75% complete, so the plain route is never needed in full. One idea alone buys
nothing, because the ruling says pieces need combinations. Parasol by study costs 100 + 100 + 100
against 400 plain, plus the study time; a colony that already holds the shared portable-shade idea
pays 200 for the second piece. All numbers are PROVISIONAL.

This reconciles "plain research always unlocks" with "each piece needs two ideas": the two ideas are
needed for the discount, never for the gear.

**A tent cannot really be locked, and this design does not try.** Any roof gives the same cover, so
`RM_Research_ShadeTent` gates only the minifiable 3×3 awning, which is a convenience: a roof you can
pack up. Roofs stay free.

**Mirrak hide's shade bonus is not gated.** `RM_ShadeClothExtension` works on any hide from the
start. Studying the hide teaches the idea; it does not switch the hide on.

## 3. Herd crossings teach portable shade everywhere

A herd crossing is not a Long Shade thing. It is a wild animal running `RM_ShadeDash`, which runs on
every map with Direct Sun. Under the Direct Sun ruling that becomes every sunlit map, so each hot
biome's own animals teach the same idea, and no biome needs a source for it.

- **A crossing** is one `RM_ShadeDash` reaching its landing cell.
- **Seen** means at least one colonist within 20 cells of the landing cell, with line of sight
  (`GenSight.LineOfSight`), awake, not downed, not in a mental state.
- **Points:** one per crossing however many colonists watched, added to the idea's colony counter
  and credited to the nearest watcher. No job and no work priority.
- **Any wild animal counts**, not only `race.herdAnimal`, because some hot biomes may have no herd
  species and the lesson must not silently die there.

## 4. One local lesson per hot biome

With portable shade free everywhere, each biome owes one local source for one other idea. That
biome's colony then has a discount on one piece; the other piece stays on plain research or waits
for a trip elsewhere. The Long Shade teaches both. The picks are delegated agent taste, each chosen
from the thing's own description, and any of them can be swapped without changing the design.

| Biome | Source (existing def) | Idea | Why |
|---|---|---|---|
| Long Shade | `RM_Dewfringe` | dew off | the ruled lesson |
| Long Shade | `RM_Leather_Mirrak` | deep cloth | the ruled lesson |
| Stillsand | `RM_Ollim` | deep cloth | a bone-white shield on a flat-topped trunk |
| Cracked Lands | `RM_Nabbuq` | dew off | bladders on the shade line that keep their water |
| Weeping Stones | `RM_Dripfringe` | dew off | a curtain of drip-tips |
| Contagion | `RM_Bleedleaf` | dew off | leaves that shed fluid from their tips |
| Pyrelands | `RM_FE_Plant_ScorchFruit` | deep cloth | a casing sealed against heat until fire cracks it |
| Webwork | `RM_Dulloth` | deep cloth | door-sized leaves that meet pane to pane, a ceiling |
| Rust Cathedral | `RM_CathedralRoachShell` | dew off | a curved plate; this biome has no plant of ours to study |
| The Forge | `RM_HeatsinkFungus` | deep cloth | a body that takes heat in |
| The Scald | `RM_Seepcandle` | dew off | a waxy skin that sheds its melt |
| Fever Wood | `RM_GiantLeaf` | deep cloth | a leaf that shelters a grown man |
| Greentide | `RM_Veluthar` | deep cloth | one tier of paddle leaves, like an opened umbrella |
| Scarlands | `RM_Glower` | deep cloth | a varnish that eats radiation on hot ground |
| Miasma | `RM_Vellamine` | deep cloth | broad leaves laid over one another with no gap |

The biome list is the extreme-heat table in `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md`.
The `RUT_` twins are not listed: their casts differ, so the build checks each twin's cast and adds a
row only where a source above is absent.

## 5. Code facts the build must respect

- **Reuse the kit.** `CompProperties_FoundTechStudy` already keeps one counter per project across
  any number of source things, which is what "same gear, own lesson" needs.
- **Add the comps from one patch file in EnvironmentalHazards.** Use `PatchOperationConditional` on
  the def's xpath. Do not use `PatchOperationFindMod`: these mods are composed into
  `mandrake.rm.biomes`, so a member's own packageId never loads.
- **`RM_FoundTechRegistry` needs a change.** It finds hidden projects only by scanning ThingDef
  comps. `RM_ShadeIdea_PortableShade` has no studiable thing, so it would never hide. Add an explicit
  registration, or add the gate by a project-side list.
- **Assembly direction.** EnvironmentalHazards references CreatureBehaviors, not the reverse, and the
  kit lives in EnvironmentalHazards. So `RM_JobDriver_ShadeDash` raises a static event in
  CreatureBehaviors at the end of its sprint, and EnvironmentalHazards subscribes.
- **The discount hook.** `researchMods` is present in the 1.6 `Assembly-CSharp.dll` (name measured;
  read the signature before use), and `ReapplyAll` means `Apply` may run again on load, so the credit
  must be idempotent: raise progress to 75%, never add 75%. `Find.ResearchManager.AddProgress` has
  three callers in `src/`. The test reads the project's completed percentage, not raw points, because
  the cost factor scales with tech level.
- **Do not touch what `DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES` deletes** (`RM_SunShield`, heat kinds,
  the gear factors). This build needs none of it and does not wait for it. Until that item lands,
  crossings happen only on biomes that already carry sun heat.

## 6. Mod Settings

One toggle, "Shade gear is learned by study", gate key `EnvironmentalHazards.ShadeLessons`, default
on. Off: sources are not studiable, crossings add nothing, and the kit shows the idea projects as
ordinary visible research, whose discount still works. The gear projects are the same either way.
