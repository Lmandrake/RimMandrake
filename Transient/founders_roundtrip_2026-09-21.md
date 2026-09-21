# Founders round trip — FOUNDERS_EXPORT_TO_REPO_1 step 2

**VERDICT: the round trip WORKS, observed in game, but only after one remap the
export's own README does not mention. As exported, the fragments lose a trait.**

Done 2026-09-20/21 against the live game on the full mod list (618 active), the
same mod set the fragments were exported against (`_modlist_at_export.txt`, 617).
No cold load was spent; no keeper save was written.

---

## 1. Def resolution (offline) — PASS, 0 unresolved

Instrument: the offline def dump captured from this very session —
`measure coverage` → `MEASURED 531 def types complete @ defs.sqlite
mods=618/a48bc71544df1a7e captured=2026-09-20T20:14:27Z`.

Extracted every def-bearing reference from all 8 fragments (`<def>`, `<kindDef>`,
`<childhood>`, `<adulthood>`, `<bodyType>`, `<headType>`, `<hair>`, `<beard>`,
`<faceTattoo>`, `<bodyTattoo>`, `<xenotype>`, `<favoriteColorDef>`, `<stuff>`,
`<thingDef>`, `<ideo>`, `<faction>`, `<source>`, `<sourcePrecept>`): **169 distinct
values, 134 of them `<def>` elements.** Checked all of them in one query with a
deliberate negative control (`ZZZ_NoSuchDef_Control`), which the query correctly
flagged.

**0 defs unresolved.** Only three values did not resolve, and two of them are
save-local indices rather than defs:

| value | class |
|---|---|
| `Faction_21` | save-local faction loadID — needs remap (README predicted it) |
| `Ideo_20` | save-local ideo loadID — **needs remap; the README does not mention it** |
| `ZZZ_NoSuchDef_Control` | the control, correctly detected |

## 2. Reference closure (offline) — PASS, better than the README claimed

- 22 Thing `<id>`s are **declared** by the fragments (8 pawns + 14 apparel/weapon
  items carried inline).
- 62 distinct `Thing_*` references appear across the 8 files.
- **0 of them point outside the declared set.** The fragments are a *closed*
  reference graph: nothing dangles back into the source save.
- Relation graph: 22 `directRelations` — a five-way `CAOutsiderRelation` clique
  among Nekko, Tobb, Griz, Yeku and Wim, plus two `Bond` edges (Yeku ↔ Marquee
  the Eyeling). Sekki Vosh and Geonosis the dewback carry none.

So "re-import all 6 together with IDs intact" is *sufficient*, and nothing else
from the source save has to travel with them.

## 3. Splice construction

**Destination:** a copy of `XENOTYPE_SKIN_REVIEW_2026-09-20.rws` — a scratch
review save on a **different world with a different player faction and different
ideos**, 250×250 map, player faction `Faction_17`, primary ideo `Ideo_12`,
`nextThingID` 22801, 69 colonists of its own, and **zero occurrences of any
founder thing id**. Picking a foreign save makes the test harder and models the
world remake exactly. The source file was read only, never written.

⚠️ A dev quicktest was deliberately NOT used: `rimworld/start_debug_game_ready`
hard-crashed RimWorld on the full ~578-mod stack on 2026-09-11, and a crash here
costs the ~21-minute load.

**Two saves were produced, in binary mode, preserving the source's UTF-8 BOM and
CRLF line endings:**

| save | what it tests | result |
|---|---|---|
| `FOUNDER_ROUNDTRIP_2026-09-21.rws` (11,049,881 B) | the remaps the README names (faction, ideo, map, pos) + uniqueID bumps | founders arrive, **but 5 of 6 lose one trait** |
| `FOUNDER_ROUNDTRIP_V2_2026-09-21.rws` (11,051,026 B) | the above **plus a `<loadID>` offset** | **clean** |

### Remaps required

| remap | from | to | flagged by the README? |
|---|---|---|---|
| faction | `Faction_21` | `Faction_17` | yes |
| ideo | `Ideo_20` | `Ideo_12` | **no** |
| map | `<map>0</map>` | unchanged (dest map uniqueID is 0) | yes |
| position | source cells e.g. `(174, 0, 132)` | a row at z=127, x=106…134 | yes |
| `uniqueIDsManager` counters | `nextThingID` 22801, `nextGeneID` 1634, `nextHediffID` 527, `nextJobID` 4 | 800000 / 2000000 / 2000000 / 2000000 | **no** |
| every `<loadID>` in the fragments, and every `Gene_<n>` reference | as exported (gene 329–2035, hediff 286–1773, job 36107–36112) | **+1,000,000** | **no** |

## 4. 🔴 The finding: gene `loadID` collision silently eats a trait

**Attempt 1 lost the `Wimp` trait from 5 of the 6 founders. Nothing was logged —
no `Repeat unique ID`, no `Could not load reference`, no exception.**

`Wimp` is the only trait any founder carries with a non-null `<sourceGene>`:

| founder | `Wimp` sourceGene | dest `nextGeneID` was 1634 | survived attempt 1? |
|---|---|---|---|
| Nekko Vok | `Gene_342` | collides | ❌ lost |
| Tobb Nkik | `Gene_382` | collides | ❌ lost |
| Griz Utinn | `Gene_422` | collides | ❌ lost |
| Yeku Yeku | `Gene_462` | collides | ❌ lost |
| Wim Ateeka | `Gene_814` | collides | ❌ lost |
| Sekki Vosh | `Gene_2009` | **above 1634, no collision** | ✅ kept |

6 of 6 agree with the collision hypothesis, including the one negative case. The
destination save had already issued gene loadIDs 0–1633 to its own 69 colonists,
so five of the six imported `sourceGene` references resolved into the destination's
own genes instead of the founders'. Offsetting every `<loadID>` in the fragments by
+1,000,000 (and the `Gene_<n>` references with them) fixed it completely.

🔑 **This is the class of defect the item was worried about**: a cross-reference
that is save-local, resolves *successfully* to the wrong object, and costs data
with no error. An export that is re-imported without the loadID offset looks fine
and is not.

## 5. Live verification (attempt 2, `FOUNDER_ROUNDTRIP_V2_2026-09-21`)

Loaded through `rimworld/load_game` + `rimbridge/wait_for_game_loaded`
(`ignoreModCompatibility: true`, playable in 21 s). All 8 pawns arrived in the
foreign colony alongside its own 69 colonists.

Compared field-by-field against a snapshot of the **same pawns in the canonical
world taken before the switch** (`jawa/pawn_get` + `pawn_traits` + `pawn_genes` +
`pawn_relations`), over: name, nickname, childhood, adulthood, bodyType, headType,
hair, beard, gender, biological age, chronological age, kindDef, developmental
stage, apparel (def + hit points + stuff), equipment, hediffs, all 12 skills
(raw level + passion + disabled), all traits (def + degree), all genes
(endogenes + xenogenes), and all social relations.

| pawn | result |
|---|---|
| Nekko 'Captain' Vok | **identical** — 5 traits, 40 genes, 12 skills, 2 apparel, 4 relations |
| Griz 'The Hands' Utinn | **identical** — 6 traits, 40 genes, 12 skills, 2 apparel, 4 relations |
| Wim 'Twice-Kin' Ateeka | **identical** — 4 traits, 40 genes, 12 skills, 3 apparel, 4 relations |
| Marquee (AA_Eyeling) | **identical**, bond intact |
| Geonosis (RSW_Dewback) | **identical** |
| Tobb 'Keeper' Nkik | identical except `ageChronologicalYears` 60 → 61 |
| Yeku 'First-Hatched' Yeku | identical except `ageChronologicalYears` 89 → 90 |
| Sekki 'The Long Pot' Vosh | identical except one **added** hediff, `MCR_MoodChainWatcher` |

The two non-identities are both expected and neither is a loss:

- **Chronological age** counts elapsed time since birth; the destination save sits
  at a different in-game date, so it shifts. Biological age is unchanged on all 8.
- **`MCR_MoodChainWatcher`** is a mod-applied watcher hediff the destination
  environment adds to pawns; it is an addition by the receiving game, not
  something the export dropped. (Nekko already carried it in both.)

**Relations resolved by name across pawns**, which is the real test of the
save-local `Thing_<id>` graph:

```
Captain        -> Keeper, The Hands, First-Hatched, Twice-Kin
Keeper         -> Captain, The Hands, First-Hatched, Twice-Kin
The Hands      -> Captain, Keeper, First-Hatched, Twice-Kin
Twice-Kin      -> Captain, Keeper, The Hands, First-Hatched
First-Hatched  -> Captain, Keeper, The Hands, Twice-Kin, Bond: Marquee
Marquee        -> Bond: First-Hatched
```

**Player.log for the V2 load:** the only Scribe complaints are 67
`Could not load reference to Verse.ResearchProjectDef` lines, identical in count to
the attempt-1 load — they belong to the destination save's own research record and
have nothing to do with the founders. One NRE appears, marked
`[Ref 785D44E7] Duplicate stacktrace`; the original occurrence is at log line 13900,
**before** the first founder load, so it predates this work. No
`Repeat unique ID`, no founder-related reference failure.

**Pictures** (`Transient/founders_roundtrip/`):

- `founders_roundtrip_v2_2026-09-21.png` — the six founders standing in a row in
  the foreign colony, correctly named and labelled.
- `founders_control_canonical_2026-09-21.png` and `portraits_canonical/*.png` — the
  same six in the canonical world, for appearance comparison.

⚠️ Unrelated observation, flagged not acted on: in **both** the canonical world and
the spliced save the founders' robe layer renders as a flat magenta block with a
red bandolier under a brown hood. It is identical in both, so it is **not** a
round-trip artefact — but magenta is what RimWorld draws when a texture fails to
resolve, and this is how they look in the canonical save today. Worth someone
checking `guy762_Robes_jawa`'s texture separately.

⚠️ Also observed: loading a 16-mod-meta save under 618 mods queues ~37 VEF
`Dialog_NewFactionSpawning` prompts. Noise from the chosen destination, not from
the founders.

## 6. Keeper-save integrity — clean

`rimworld/save_game` was **never called**. Baseline taken before any work, re-checked
after:

- `CANONICAL_ASHKARR_START_2026-09-12.rws` — md5 `75be9ecd4764a397e9802d997bb9e0b9`
  before and after (and it matches the md5 the export README recorded).
- `ASHKARR_FALLLINE_LABEL26_2026-09-21.rws` — md5 `31c981515d9e90dcacdb1f2110068527`
  before and after.
- A size+mtime manifest of all 31 `.rws*` files in the Saves folder differs in
  exactly two lines: the two new throwaways this work created. Nothing existing
  changed size or mtime.

The game was left loaded on `ASHKARR_FALLLINE_LABEL26_2026-09-21`, which is where
it was found.

## 7. What the export needs, to be a backup

The fragments themselves are sound and do not need re-exporting. What is missing is
the **importer half** — the export records a form nobody can re-import correctly
without rediscovering §4 the hard way. Concretely, `founders/README.md` needs:

1. `Ideo_20` added to the remap list beside `Faction_21`.
2. The `uniqueIDsManager` bump requirement (`nextThingID`, `nextGeneID`,
   `nextHediffID`, `nextJobID`).
3. 🔴 The `<loadID>` offset rule, with the reason: gene loadIDs are save-local and
   a collision resolves *successfully* to the wrong gene and silently drops the
   gene-sourced trait.

The strongest form would be a small committed `import_founders.py` next to the
fragments doing all four remaps against a named destination save — a script is a
backup, a prose caveat is a note. That is a judgement for whoever owns the item,
filed rather than done here.

## 8. Artifacts

| what | where |
|---|---|
| spliced save that round-trips clean | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\FOUNDER_ROUNDTRIP_V2_2026-09-21.rws` |
| first attempt, the one that loses the trait | `…\Saves\FOUNDER_ROUNDTRIP_2026-09-21.rws` |
| in-game picture, spliced | `D:\Luke\dev\Rimworld\Transient\founders_roundtrip\founders_roundtrip_v2_2026-09-21.png` |
| control pictures, canonical world | `D:\Luke\dev\Rimworld\Transient\founders_roundtrip\founders_control_canonical_2026-09-21.png` and `…\portraits_canonical\` |

Both throwaway saves were left in place as evidence; neither is a keeper and both
can be deleted on the owner's word.
