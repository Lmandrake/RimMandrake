## spec
REP swept `infrastructure/state/TEST_PLAN.md` on 2026-08-22 with a subagent: most of it verified,
**six assertions did not.** It is a pre-flight plan, so a wrong anchor in it costs a load.

⚠️ **Subagent findings, not REP measurements — verify each before editing.**

| line | says | actually |
|---|---|---|
| 64 | "ten art-fix mods are live" | **7 active** in `ModsConfig.xml` (msedroidfix, sauridfrillfix, gravshipastronautfix, toolbeltfix, blastdoorframeasyncfix, researchkiteastfix, desertvehiclereskin). `mandrake.cereanmanefix` **is not in the list at all** |
| 71-73 | "Part 1 — the EIGHT live mods… seven art-fix plus the sled reskin" | 7 live (6 art-fix + sled). The table's own row 6 is struck closed, so the header contradicts its own table |
| 127-128 | "`Jawa_Patches/Textures/` holds exactly two PNGs" | **14 PNGs** under `src/Jawa/Jawa_Patches/Textures/` (Things/ and World/). The no-collision conclusion may still hold; the count behind it does not |
| 217-218 | "the real signature is `…/JawaBenchTerrainTools.cs:69`" | `SetTerrain` is declared at **line 61**; `string terrainDef` is at **73**. The parameter-name claim itself is TRUE — only the anchor is wrong |
| 60, 88 | "`Apparel_FieldKits.xml:62`" and "`:51`" | that mod (294100/2868392160) ships only `v1.4/` and `v1.5/` — **no 1.6 folder**; in v1.5 `texPath` is line 50 and `wornGraphicPath` line 61 |
| 126 | "My `C12` double-ship warning was STALE… Struck" | `C12` was never filed in the ledger; `design/V2_DREAMS.md:248` uses C12 for an unrelated launch-gate item, so the ID points at the wrong thing |

**UNMEASURED, and it matters:** line 198 row 1 claims *"✅ ALREADY PASSED LIVE — 144 cells, 0
failed verify."* **No capture of that run exists in either `observed/` directory** — the root one
and `observed/` were both checked. Either produce the capture or downgrade
the row from PASSED to UNMEASURED. To measure: re-run `jawa/set_terrain` and read back with
`rimworld/get_cell_info`.

## verify
Every line anchor re-resolved against the file it names; every count re-derived from disk or
`ModsConfig.xml`; row 1 either evidenced or downgraded.

## criteria
No anchor in TEST_PLAN.md points at the wrong line, and no row claims PASSED without a capture
that resolves.

## Watch out
🪤 **Two directories are named `observed/`** — the repo root one holds harvested logs,
`observed/` holds per-experiment captures. A bare `observed/…` in evidence
means the ROOT one. Checking only one has produced a false "evidence missing" verdict three times.
