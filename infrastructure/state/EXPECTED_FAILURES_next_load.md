# Expected signatures — Rites + ResearchRetag first load, written 2026-09-04 BEFORE launch (BENCH)

⛔ SUPERSEDED 2026-09-04 by `infrastructure/state/items/COLD_LOAD_RUN_SHEET_3.md`
§1 entry 1 — this table now lives there, folded into the run sheet that
scores the next full-list load. Read it there.

Supersedes the RESTART_7 deploy-debt entry — that batch rode its restart
2026-09-04 and verified clean (commit 34885539).

Two NEW XML-only mods activated at the ModsConfig tail (591 active now;
backup at ModsConfig.xml.pre_rites_retag_20260904):

| cargo | expected-PRESENT | failure looks like |
|---|---|---|
| `mandrake.rut.rites` (5 ResearchProjectDefs + 1 ResearchTabDef, defs only) | "the rites" tab visible in the research window; `measure`/dump shows 527 ResearchProjectDef (was 522) | red XML error naming RUT_Rites_*; tab absent |
| `mandrake.rut.researchretag` (269 defs patched: 185 techLevel, 103 baseCost, 113 prereq lists, all match/nomatch-guarded) | patch-failure count stays at baseline 6 (the 6th is the pre-existing lightsaber FindMod); spot-check via bridge: `guy762_ResearchKotOR_blasters` prereq = hvyblasters, baseCost matches manifest | "[Research Retag] Patch operation ... failed" lines; a red-error storm at def resolution naming research defs; `Could not resolve cross-reference` naming a research defName |

⚠️ The retag's effect is INVISIBLE on the minimal list (conditionals no-op
without the content mods) — proof requires the FULL-list load. A fresh dump
after that load also folds the 5 Rites rows into the manifest (coverage
becomes 527) — rerun `research_manifest_validate.py` then.
