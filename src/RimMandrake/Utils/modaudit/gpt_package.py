#!/usr/bin/env python3
"""modaudit/gpt_package.py - compose design/RimMandrake/mod_audit/GPT_PACKAGE.md, the whole audit in one file for a GPT review.

    python3 src/RimMandrake/Utils/modaudit/gpt_package.py         # writes GPT_PACKAGE.md, refuses over 250 KB

Reads MASTER_REGISTRY.jsonl (merge_checks.py), facts/mod_facts.jsonl, SCENARIO_BRIEF.md, OWNER_CARDS.md, ACTIONS_NOW.md,
FACTS_REGEN_DELTA.md (if present). The prose sections (method, weaknesses, systematic errors, conflicts, questions) are
written below by the merge author and say what they are; every number in the tables is computed here.
"""
import json
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
AUDIT = os.path.join(ROOT, "design", "RimMandrake", "mod_audit")
OUT = os.path.join(AUDIT, "GPT_PACKAGE.md")
LIMIT = 250 * 1024
SHORT = {"KEEP": "KEEP", "KEEP-TEMPORARILY-THEN-PHASE-OUT": "PHASE", "REPLACE-NOW-WITH-OUR-OWN": "REPLACE",
         "ELIMINATE-COMPLETELY": "ELIM"}
KIND_ORDER = ("tps", "memory", "interaction", "log_noise", "complexity", "size", "maintenance")

QUESTIONS = """\
## What we want from you (GPT)

Answer each question in turn. Name the packageIds you mean. Mark anything you infer, as opposed to read off this file, as INFERRED.

1. **Donor exit sequencing.** Order the exits of the big donor families (Alpha*, Vanilla Expanded, Outer Rim, Star Wars
   Animal Collection, ReGrowth, GravTide, and the donors behind our own Baroque Biomes `mandrake.rm.biomes`). Use the
   dependency map in §10. For each step say what must be ported first, which of our mods have to change, and what the save
   or world remake has to absorb. Which exits are cheap now and which only make sense at the remake?
2. **Cluster-level decisions.** Many rows are not really separate decisions: frameworks and their consumers, rethemed
   factions and their suppressions, Cherry-Picker shells, authoring tools. Propose the clusters that should share one verdict.
   Name every row whose verdict is inconsistent with its cluster.
3. **Hidden risk in the KEEPs.** Which of the 363 KEEP rows carry the most risk that the audit could not see? Consider
   Harmony patch collisions with our mods, static constructors, tick flags on content spawned in numbers, abandoned upstreams,
   and AssetBundle art the texture proxy cannot read. Rank your top 20 and give a reason for each.
4. **Blind spots of the method.** What kinds of problem could this audit not see at all? Examples: runtime-only patch
   conflicts, load-order fragility, save-compat traps, Mod Settings state, per-mod TPS. What cheap instrument would expose each?
5. **The owner cards.** For each of the 23 cards in §7, is the recommendation right given the scenario brief? Is a card
   missing, or is one actually a measurement or a ruling already made?
6. **Disputed and changed rows.** Re-judge the 1 DISPUTED row and the 13 checker-changed rows in §4 from the evidence quoted.
7. **Performance.** The 550-mod list runs at 8-10 TPS. Using the session profile in §3 and the per-mod flags, which 20
   removals or Cherry-Picker trims would most plausibly buy TPS or memory? Say how confident you are in each, given that
   per-mod TPS is UNMEASURED.
8. **Anything the facts-regeneration delta (§9) should change** in a verdict, with the rule it fires.
"""

RUBRIC = """\
## 2. Rubric in brief (full text: RUBRIC.md)

- **Five questions per mod:** (1) what it adds, (2) forward plan, (3) likely problems, (4) is source available,
  (5) does it resonate with the scenario or clash with it.
- **Verdicts:**
  - `KEEP`: fit is neutral or resonant, and something of ours depends on it or it supplies something we will not build.
  - `KEEP-TEMPORARILY-THEN-PHASE-OUT` ("PHASE"): name what holds it in and the exit item.
  - `REPLACE-NOW-WITH-OUR-OWN`: concrete scope, a reason it cannot wait, and proof we have not already built it.
  - `ELIMINATE-COMPLETELY` ("ELIM"): it clashes with the scenario or duplicates ours, AND it passes the retirement-cost
    check (dependants, placed Things in the save, ParentName inheritance).
  - When evidence is missing, take the most conservative verdict.
- **Severity per kind** (0-3, or U = unmeasured):
  - `memory`: header-decoded texture estimate, <50 / 50-250 / >250 MB. This is a proxy, never a measurement.
  - `tps`: tick flags in the DLL, no per-mod measurement.
  - `log_noise`: attributed error blocks (attribution is a CANDIDATE).
  - `interaction`: patches into or from our mods.
  - `complexity`: XML-only / one DLL / Harmony + Prepatcher or more than 20 static ctors.
  - `size`: disk, <20 / 20-200 / >200 MB.
  - `maintenance`: source verified and recent / unverified / none or older than 2 years.
- **Confidence on every claim:** MEASURED (read off an instrument or a file), INFERRED, UNVERIFIED.
- **Forbidden shortcuts:**
  - judging by name;
  - "heavy" without a number;
  - treating a candidate log attribution as guilt;
  - reading def_total as "in game";
  - "unused" because `patched_by` is empty;
  - resolving a brief §5 contradiction inside a verdict;
  - inventing ledger items.
"""

METHOD = """\
## 3. Programme, method and known weaknesses

**Pipeline (stage 0, offline):**
- `universe.py`: FULL.LATEST (the 550-mod target list) plus our absent mods = 589 ids, resolved to disk by About.xml parse.
- `defscan.py`: def and patch census over a synthetic ModsConfig of the universe, with load folders resolved.
- `diskfacts.py`: About.xml, folder walk, DLL string flags, PNG/DDS header texture estimate.
- `runtime.py`: one measured 550-mod session on 2026-10-10. It gives a Player.log error attribution (100 of 344 blocks
  attributed), the LoadTracer static ctors, and a stage-level TPS profile.
- `sources.py`: gh api verification of linked repos.
- `assemble.py` writes `facts/mod_facts.jsonl`.
- `batches.py` cuts 16 batches by category.

**Stage 1:** one assessor agent per batch (Claude Sonnet 5.5) writes `assessments/batch_NN.jsonl` and `records/batch_NN.md`.

**Stage 2:** four independent checker groups (Claude Opus 5.5) re-derive every MEASURED number from facts and open every
cited ruling, ELIMINATE row and card_worthy row. They write `checks/check_group_N.jsonl`, with corrections as old/new/evidence.

**Merge:** `merge_checks.py` applies amendments field by field. A checker's verdict change is taken **only** when the merge
author opened the primary source it cited (23 spot-checks in `merge_inputs.json`; 13 accepted, 1 not confirmed, the rest
non-verdict claims). Otherwise the row is DISPUTED and both verdicts are kept.

**Known weaknesses of the first pass:**
- Per-mod TPS and memory are UNMEASURED. Memory is a header proxy. It is blind to AssetBundles and resources.assets, and
  it counted images under Source/ (fixed in the facts regeneration, §9).
- Log attribution covers 29% of error blocks. "0 errors" often means "not attributed".
- Placed Things in the campaign save were never measured for any ELIMINATE.
- Live Mod Settings (the Config folder) were not read by the assessors. Checkers found three rows where the live
  setting contradicts a ruling or a doc.
- `dependants` held only About.xml `modDependencies`. Load-order, class-reference, patch, FindMod and by-version edges
  were missing, and this hid real consumers (§5).
- Assessors searched `design/Jawa/mods/` for rulings. Rulings that live in the ledger, in commit bodies and in our own
  patch headers were missed.
- Several "ADOPTED" entries in required_mods.md are Fetcher-era recommendations, not owner decisions. They were not separated.
"""

SYSTEMATIC = """\
## 5. Systematic errors the checkers found (all four groups, merged)

| # | error | rows hit (examples) | consequence | fixed where |
|---|---|---|---|---|
| 1 | Rulings missed because they live outside `design/Jawa/mods/` (ledger, commit bodies, patch headers) | Orc Clan, MiningCo x4, Big and Small, Archon, Factional War, Route B fog, VSR retirement, lightsaber STAYS UPSTREAM | wrong ELIMINATEs, re-asked cards | merge (spot-checked), OWNER_CARDS "not carded" table |
| 2 | `dependants` only read `modDependencies` | aoba.framework (v1.6 by-version), jecstools, mineablesor, mines2patchouterrim, geneticheadsframework (11 class refs), Gender Works / Rosaline genes on the founders, Doors Expanded, SMYH, Better Trees | frameworks graded ELIMINATE while a KEEP consumer needs them | facts regen: `dependants_detail` with edge kinds |
| 3 | Cross-batch inconsistency: a framework does not follow its dependants | RimTek core/docmate/digipal, Genetic Heads, Nightmare Core, Titan vs races.core | contradictory verdicts in one dependency chain | merge (two accepted), card C21 |
| 4 | Card inflation: measurement questions or already-answered questions marked card-worthy; 10 card-worthy rows with no question; duplicate cards | batch 03 x10; MiningCo x3; world-map tools x5; remake x3 | about 130 raw questions | OWNER_CARDS: 23 cards + measurement tickets |
| 5 | Schema drift: `needs_owner` is a string in batch 02 and a list elsewhere | batch 02 | merge must normalise | merge_checks.norm_questions |
| 6 | "Searched, found nothing" labelled MEASURED; NOT_FOUND repos read as available; false-match repos used (pardeike/Harmony, MonoMod push date) | 6 batch-01 rows; Standalone Hot Spring, Stealing Mod; techlevelenforcement | maintenance and source scores wrong | facts regen: INFERRED + REJECTED |
| 7 | Texture proxy counted images under `Source/` (NuGet icons) | techlevelenforcement 433 MB | memory sev 3 for a mod with ~0 loaded art | facts regen |
| 8 | Def census blind to Cherry-Picker cuts and LoadFolders-gated defs | xmb.ancienturbanruins.mo, redmattis.bigsmall, shavius.medieval.flavour; btd KotOR VGE (0 counted, 7 real), jecstools 25 vs 92 files | three different verdicts for one shell situation | facts regen: `cherry_picker_shell`, `defs_outside_loaded_dirs` |
| 9 | Our own log errors charged to donors | research-tab collisions (ours: RUT_ResearchTabAssign.xml) charged to Roots of RimWorld and DBH Lite; VAEWaste errors charged to rut.patches; Biomes Fossils save dead refs charged sev 3 | wrong log severities | merge amendments; ACTIONS_NOW C1 |
| 10 | Live Config never read | Land On Anything (ruled OFF, live ON), Bigger Gravships (12 values not 4), Faction Raid Cooldown (+13 h), Better Ambushes (no file, so defaults) | rulings silently not in effect | ACTIONS_NOW B1-B2, tickets |
| 11 | "No item file, so unfiled": the items glob is not the ledger | 5 items exist in the ledger without prose | invented "unfiled" exits | (merge leaves the text; use `rimflow show`) |
| 12 | Grep artefacts accepted as evidence | "Stillsand mentions trystan" = `entryStandable`; LuminousPigment shared-defName edges | a REPLACE with no real basis | merge (trystan accepted) |
| 13 | Stale CLAUDE.md north-star claims repeated | FlowWorks "VALIDATED" (DRAFT today) | wrong status in records | ACTIONS_NOW C8 |
| 14 | Shipping status of 38 absent own mods conflated: only 14 are owner-ruled adds | rut.weathersuite, restrainingbolts, ... | KEEP means "keep the source", not "ship" | noted per row |
"""

CONFLICTS = """\
## 6. Ruling conflicts (unresolved on purpose; the owner card that settles each is named)

| conflict | sources | card / action |
|---|---|---|
| Permanent residents (2026-09-11) vs port everything (2026-09-20) | `mod_config_rulings.md:71` vs `DONOR_DEFS_PORT_TO_OURS_1` | C01 |
| Land On Anything flags: ruled OFF, live ON | `GRAVSHIP_LANDING_CRUSH_1.md:5-11` vs live Config | ACTIONS B1 |
| Bigger Gravships: doc 4 values, live 12 | `ship_designs.py` vs live Config | ACTIONS B2, C12 |
| FULL.LATEST vs retirements | `STAT_NORM_WAVE3_RETIRE_1`, `CRYSTAL_INGEST_EXECUTION_1`, Beasts of the Rim checklist | ACTIONS A1-A3, A5 |
| RimAI adopted (required_mods:1127) vs PARK (:930) vs `claude -p` only (2026-09-05) | required_mods.md, CLAUDE.md | C23 |
| Storyteller Enhanced adopted vs Randy ratified (R-S7) | required_mods.md:871 vs SCENARIO_SETTINGS_SPEC | C09 (incident patches only) |
| Yayo's Combat 3 vs the "equivalent total combat overhaul" ban | forbidden_mods.md:151-153 vs weapon register AP calibration | C14 |
| Archon: retheme (2026-09-11) and suppression (OnlyOurFactions) both live | VREArchon_MortisRename.xml vs OnlyOurFactions.xml | C20 |
| Better Infestations events vs the planet-wide infestation ban | ADOPT 2026-08-04 vs ban 2026-09-24 | C09 |
| Warcasket "alternative to ... ocean access" vs "ship or nothing" | 2026-09-28 vs 2026-09-26 | C03 |
| Vehicle-raid test ("drop the frameworks") vs Neolithic cart reskin in progress | V2_DREAMS §0b vs §0c | C11 |
| Trim-not-uninstall doctrine vs 8-10 TPS on the 550 list | 01_campaign.md pillars vs measured session | C22 |
| Ancient Urban Ruins: keep Hit Point, forbid AURAD vs cut the family | forbidden_mods.md vs ANCIENT_RUINS_MOD_AUDIT_1 | C22 |
| VFE Factory "sole industrial tree" vs the anti-automation line | required_mods.md vs brief | C13 |
| VQE Ancients "drop entirely" (2026-08-03) vs about 60 patches written since | ruling vs src | C15 |
| Anomaly: campaign header vs canon reintegration ruling ② | 01_campaign.md vs canon_reintegration_plan.md | verdict-neutral, not carded |
| CLAUDE.md north-star state vs `modcheck status` | CLAUDE.md vs measured | ACTIONS C8 |
"""


def jl(p):
    return [json.loads(x) for x in open(p) if x.strip()]


def words(s, n=20):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    first = re.split(r"(?<=[.;])\s", s, maxsplit=1)[0]
    w = first.split()
    return " ".join(w[:n]) + ("…" if len(w) > n else "")


def top_problem(r):
    best = None
    for k in KIND_ORDER:
        v = r.get("sev_" + k)
        if isinstance(v, int) and v > 0 and (best is None or v > best[1]):
            best = (k, v)
    return "%s%d" % best if best else "-"


def src_short(r):
    k = r.get("source_kind") or "?"
    u = r.get("source_url") or ""
    m = re.search(r"github\.com/([^/\s]+/[^/\s)]+)", u)
    return "%s:%s" % (k, m.group(1)) if m else k


def esc(s):
    return str(s).replace("|", "/")


def main():
    M = jl(os.path.join(AUDIT, "MASTER_REGISTRY.jsonl"))
    F = {r["packageId"]: r for r in jl(os.path.join(AUDIT, "facts", "mod_facts.jsonl"))}
    by = {r["packageId"]: r for r in M}
    out = []
    w = out.append
    w("# Mod audit: the whole picture, for a GPT review\n")
    w("RimWorld 1.6 campaign (a Jawa scavenger clan on a hand-made desert world, with Star Wars flavour). The target mod list "
      "is 550 mods plus our own absent mods: **589 rows**. Generated by `src/RimMandrake/Utils/modaudit/gpt_package.py` from "
      "`MASTER_REGISTRY.jsonl` (merge of 16 assessor batches and 4 checker groups) and `facts/mod_facts.jsonl`. "
      "Every number here is computed. The prose sections are the merge author's summary of the checker reports. "
      "Glossary: PHASE = keep temporarily then phase out; ELIM = eliminate completely; sev 0-3/U; OURS = mandrake.rm/rsw/rut.\n")
    w(QUESTIONS)
    w("## 1. Scenario brief (verbatim, SCENARIO_BRIEF.md)\n")
    brief = open(os.path.join(AUDIT, "SCENARIO_BRIEF.md")).read()
    w(re.sub(r"(?m)^(#+) ", lambda m: "#" + m.group(1) + " ", brief.split("\n", 1)[1]))
    w(RUBRIC)
    w(METHOD)
    try:
        ctx = json.load(open(os.path.join(AUDIT, "facts", "session_context.json")))
        tps = ctx.get("tps") or {}
        w("**Measured session context:** %s\n" % esc(json.dumps({k: tps.get(k) for k in list(tps)[:8]})[:1500]))
    except (OSError, ValueError):
        pass
    # 4. counts
    av = Counter(r["assessor_decision"] for r in M)
    fv = Counter(r["final_decision"] for r in M)
    st = Counter(r["decision_status"] for r in M)
    cls = Counter(r["class"] for r in M)
    w("## 4. Decisions: before and after the merge\n")
    w("| decision | assessor | final |\n|---|---|---|")
    for k in ("KEEP", "KEEP-TEMPORARILY-THEN-PHASE-OUT", "REPLACE-NOW-WITH-OUR-OWN", "ELIMINATE-COMPLETELY"):
        w("| %s | %d | %d |" % (k, av[k], fv[k]))
    w("\nStatus: %s. Classes: %s. Checker verdicts: %s.\n" % (dict(st), dict(cls), dict(Counter(r["checker_verdict"] for r in M))))
    w("Final decision by class:\n")
    w("| class | KEEP | PHASE | REPLACE | ELIM |\n|---|---|---|---|---|")
    for c in sorted(cls):
        cc = Counter(r["final_decision"] for r in M if r["class"] == c)
        w("| %s | %d | %d | %d | %d |" % (c, cc["KEEP"], cc["KEEP-TEMPORARILY-THEN-PHASE-OUT"], cc["REPLACE-NOW-WITH-OUR-OWN"],
                                         cc["ELIMINATE-COMPLETELY"]))
    w("\n**Changed by checker (spot-checked) and disputed:**\n")
    w("| packageId | assessor -> final | status | why (spot-check) |\n|---|---|---|---|")
    for r in M:
        if r["decision_status"] != "AGREED":
            w("| %s | %s -> %s | %s | %s |" % (r["packageId"], SHORT[r["assessor_decision"]], SHORT[r["final_decision"]],
                                              r["decision_status"], esc(words(r["decision_change_reason"], 45))))
    w("")
    w(SYSTEMATIC)
    w(CONFLICTS)
    # 7/8 embed cards + actions
    cards = open(os.path.join(AUDIT, "OWNER_CARDS.md")).read()
    w("## 7. Consolidated owner cards (OWNER_CARDS.md)\n")
    w(re.sub(r"(?m)^(#+) ", lambda m: "#" + m.group(1) + " ", cards.split("\n", 1)[1]))
    acts = open(os.path.join(AUDIT, "ACTIONS_NOW.md")).read()
    w("## 8. Actions needing no owner decision (ACTIONS_NOW.md)\n")
    w(re.sub(r"(?m)^(#+) ", lambda m: "#" + m.group(1) + " ", acts.split("\n", 1)[1]))
    # 9 delta
    w("## 9. Facts regeneration delta (FACTS_REGEN_DELTA.md)\n")
    dp = os.path.join(AUDIT, "FACTS_REGEN_DELTA.md")
    if os.path.isfile(dp):
        d = open(dp).read().split("\n", 1)[1]
        w(re.sub(r"(?m)^(#+) ", lambda m: "#" + m.group(1) + " ", d[:14000]) + ("\n…(truncated; full file FACTS_REGEN_DELTA.md)\n" if len(d) > 14000 else ""))
    else:
        w("(not yet written)\n")
    # 9b textures
    w("## 9b. Memory estimates that are UNMEASURED: top 30 by header-decoded texture estimate\n")
    w("The estimate is w*h*4*1.33 over PNG/DDS headers. It does not see AssetBundles (column `bundles MB`) or Core/DLC "
      "resources.assets. No per-mod memory has ever been measured.\n")
    w("| packageId | class | final | tex est MB | images | bundles MB | disk MB |\n|---|---|---|---|---|---|---|")
    rows = sorted(F.values(), key=lambda f: -(f.get("texture_decoded_mb_est") or 0))[:30]
    for f in rows:
        b = ((f.get("disk_by_kind") or {}).get("assetbundles") or {}).get("mb", 0)
        r = by.get(f["packageId"], {})
        w("| %s | %s | %s | %s | %s | %s | %s |" % (f["packageId"], f["class"], SHORT.get(r.get("final_decision"), "?"),
                                                f.get("texture_decoded_mb_est"), f.get("texture_count"), b, f.get("disk_mb")))
    bund = sorted(F.values(), key=lambda f: -(((f.get("disk_by_kind") or {}).get("assetbundles") or {}).get("mb", 0)))[:10]
    w("\nLargest AssetBundle payloads (art invisible to the estimate): " + ", ".join(
        "%s %.1f MB" % (f["packageId"], ((f.get("disk_by_kind") or {}).get("assetbundles") or {}).get("mb", 0))
        for f in bund if ((f.get("disk_by_kind") or {}).get("assetbundles") or {}).get("mb", 0) > 0) + "\n")
    # 10 donor map
    w("## 10. Dependency and absorption map of the biggest donors\n")
    w("`ours refs` = xpath defName references from our mods into the donor's defs (a lower bound). `our patchers` = our mods "
      "with the most refs. `hard deps` = mods that list the donor as a dependency. Edge kinds come from the regenerated facts "
      "when present.\n")
    fams = [("Alpha (sarg.alpha*)", lambda p: p.startswith("sarg.alpha")),
            ("Vanilla Expanded (vanillaexpanded.* / oskarpotocki.*)", lambda p: p.startswith(("vanillaexpanded.", "oskarpotocki."))),
            ("Outer Rim (neronix17.outerrim*)", lambda p: p.startswith("neronix17.outerrim")),
            ("Star Wars Animal Collection", lambda p: p == "mlie.starwarsanimalcollection"),
            ("ReGrowth", lambda p: p.startswith("regrowth.")),
            ("GravTide", lambda p: p.startswith("gravtide")),
            ("Biome donors behind Baroque Biomes", lambda p: p in ("grimterra.biomesmod", "zylle.morevanillabiomes",
                                                                    "mlie.advancedbiomes", "biomesteam.biomesfossils",
                                                                    "kopp.biomecompatibilityproject"))]
    for title, pred in fams:
        mem = sorted([f for p, f in F.items() if pred(p)], key=lambda f: -(f.get("patched_by_ours_refs") or 0))
        if not mem:
            continue
        tot = sum(f.get("patched_by_ours_refs") or 0 for f in mem)
        w("### %s: %d mods, %d refs from ours\n" % (title, len(mem), tot))
        w("| packageId | final | card | ours refs | our patchers (top 4) | hard deps / other edges | tex MB |\n|---|---|---|---|---|---|---|")
        for f in mem:
            r = by.get(f["packageId"], {})
            ours = [(k, v) for k, v in (f.get("patched_by") or {}).items() if k.startswith("mandrake.")][:4]
            det = f.get("dependants_detail")
            if det:
                dd = "; ".join("%s(%s)" % (x.get("packageId"), ",".join(x.get("kinds") or [])) for x in det[:6])
            else:
                dd = ", ".join(f.get("dependants") or []) or "-"
            w("| %s | %s | %s | %d | %s | %s | %s |" % (
                f["packageId"], SHORT.get(r.get("final_decision"), "?"), ",".join(r.get("owner_question_ids") or []) or "-",
                f.get("patched_by_ours_refs") or 0, ", ".join("%s %d" % (k.replace("mandrake.", ""), v) for k, v in ours) or "-",
                esc(dd)[:150], f.get("texture_decoded_mb_est")))
        w("")
    bb = F.get("mandrake.rm.biomes") or {}
    w("**Baroque Biomes (`mandrake.rm.biomes`, ours) depends on:** hard %s; patches into: %s.\n" % (
        ", ".join(bb.get("dependencies") or []) or "-",
        ", ".join("%s %d" % kv for kv in list((bb.get("patches_mods") or {}).items())[:12])))
    # 11 master table
    w("## 11. MASTER table (one line per mod)\n")
    w("Columns: id | name | class (O = ours, 3 = third party, D = core/DLC) | final decision (`*` = changed by checker, "
      "`?` = disputed) | fit | key reason (<= 20 words, the assessor's first sentence) | top problem (kind + severity) | "
      "source | owner card / ticket.\n")
    w("| id | name | c | final | fit | key reason | top | source | card |\n|---|---|---|---|---|---|---|---|---|")
    cmap = {"OURS": "O", "THIRD_PARTY": "3", "CORE_DLC": "D"}
    for r in M:
        mark = "*" if r["decision_changed_by_checker"] else "?" if r["decision_status"] == "DISPUTED" else ""
        tag = ",".join((r.get("owner_question_ids") or []) + ["m:" + t for t in (r.get("measure_tickets") or [])]
                       + ["a:" + a for a in (r.get("action_ids") or [])]) or "-"
        w("| %s | %s | %s | %s%s | %s | %s | %s | %s | %s |" % (
            r["packageId"], esc((r.get("name") or "")[:40]), cmap.get(r["class"], "?"), SHORT[r["final_decision"]], mark,
            (r.get("fit") or "?")[:4], esc(words(r.get("verdict_reason"))), top_problem(r), esc(src_short(r)), tag))
    w("\n(`card` column: C## = OWNER_CARDS card; `m:` = measurement ticket; `a:` = ACTIONS_NOW action.)\n")
    w(QUESTIONS.replace("## What we want from you (GPT)", "## 12. The questions again (answer these)"))
    text = "\n".join(out)
    size = len(text.encode("utf-8"))
    if size > LIMIT:
        raise SystemExit("GPT_PACKAGE would be %d bytes > %d - refusing; trim a section" % (size, LIMIT))
    with open(OUT, "w") as fh:
        fh.write(text)
    print("wrote %s (%d bytes, %d rows)" % (os.path.relpath(OUT, ROOT), size, len(M)))


if __name__ == "__main__":
    main()
