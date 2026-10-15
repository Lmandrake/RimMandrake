# Plan: convert the Star Wars Animal Collection pack to our own defs

Item `DONOR_DEFS_PORT_TO_OURS_1`. Owner ruling 2026-10-11 (card): copy the whole cheap pack wholesale first, then the 102-row
`sarg.alphaanimals` pack; keep/cut stays with each biome's own sitting (evictions stopped).
Numbers are from `Transient/donor_pack_port_census_2026-10-14.md` (agent census, 2026-10-14; twins matched by NAME only).

## Where we stand (160 species in the pack)
| class | species |
|---|---:|
| already ported and wired | 24 |
| wired, but a donor roster row remains | 18 |
| twin exists, not wired | 59 |
| not ported | 59 (5 are named in rosters: Snoruuk, Tauntaun, Tibidee, Vapaad, Wyyyschokk) |

Rosters: 86 BiomeDef rows (68 species) plus 4 patch-injected rows name the donor; all carry `MayRequire`. About 66 rows need repointing.
No new C# is needed anywhere. Mynock is permanently declined (not ported). The item's vendored-source path does not exist; the donor lives in the workshop folder `3497316713`.

## Waves (cheapest and most roster-relevant first)
| wave | work | size | checks |
|---|---|---|---|
| W0 | Prove the 59+18 twins really equal the donor (diff stats, body, lifestage, texPath), since the census matched by name only | 77 species, one script | L0 diff report; any mismatch becomes a fix row |
| W1 | Repoint the ~66 donor-named roster rows to the proven twins in the `RUT_*` BiomeDefs and `UtinniPatches/Patches/WildAnimals_*.xml`, dropping the donor `MayRequire` | ~66 rows, 29 files | validate_patch.py with --defs and --live; roster parsed as XML elements |
| W2 | Port the 5 roster-named species first, then the 13 plain-XML species, then the 7 plain-with-dependencies | 25 species | each gets def, PawnKindDef, own texPath, and a roster wire |
| W3 | Port the 39 species needing a custom BodyDef, batched by shared body; 27 of them also need items or abilities | 39 species | body shared once per batch |
| W4 | Retire the donor: remove it from a minimal test list, then run a donor-off load with every biome still generating | one load | L2 on a quicktest map |
| W5 | Same pipeline for `sarg.alphaanimals` (102 rows), after W4 is clean | later | its own census first |

## How
- Writers are sonnet workers, one wave at a time, each in its own file set; I integrate. Recipe is the hand pipeline in
  `items/closed/MLIE_FAUNA_ABSORPTION_1.md` (there is no port script); art comes out with `extract_bundle.py`.
- Porting and renaming stay separate jobs: keep the twin's existing name (NONCANON_BEAST_RENAME_1 owns renames).
- Never infer a def's owner from its prefix; read `MayRequire`. Texture binds by `texPath`, not defName.

## Open questions for the owner
1. **Art:** the donor's art is a 33.5 MB AssetBundle and "no donor art kept" is ruled, so every one of the 59 NOT_PORTED species owes
   art of our own. Do twins already carry our own art, and may ports reuse extracted donor art until a render exists?
2. **Scope check:** W3's 39 body-sharing ports are the bulk of the cost. Port them all now, or only those a roster names?

Not started: nothing in this plan has been executed.
