<!-- status: draft — Fable handoff sprint 2026-08-30, item FABLE_HANDOFF_SPRINT_1; feeds RESEARCH_TREE_NORMALIZATION_1 (execution stays gated) -->
# Research Normalization — principles before surgery

_This doc de-risks RESEARCH_TREE_NORMALIZATION_1 ("restructure ALL research for
the whole game — full normalization pass, after the droids land") without
executing it. Audience: Opus 5 + the owner. The execution stays gated; the
thinking should not wait for the gate._

## 1. The problem, stated honestly

~584 mods each graft research into the tree with no knowledge of each other.
The result: duplicate capabilities at wildly different costs, prereq chains
that reference cut or absent projects, tech that ignores the campaign's
tier logic, and a tab bar of per-mod silos. "Full normalization" means:

- **Tier coherence** — a project's cost and position reflect what it actually
  unlocks, campaign-wide, not its home mod's internal economy.
- **No orphan prereqs** — nothing requires a project that Cherry Picker cut or
  another mod failed to load (silent no-match is the stack's signature trap).
- **Cost sanity** — comparable capability, comparable price; the vanilla
  techLevel cost multiplier (colony techLevel vs project techLevel) is part of
  this arithmetic and the Jawa faction's techLevel choice is therefore a
  NORMALIZATION INPUT, not an afterthought (OPEN-FOR-OWNER, §6).
- **The buildable whitelist** — "Jawa-buildable" becomes a decided, auditable
  set instead of an accident of 584 load orders (the trap renaissance and
  armoury absorptions both currently cite it as UNMEASURED).

What it must **NOT** mean: rewriting content mods' internals. No renaming
defNames (breaks saves and mod C# that checks research keys), no editing mod
C# hooks, no flattening a mod's identity into mush. We move projects' *tree
position, cost, and prereqs*; we never touch what completing them does.

## 2. The theology mapping — the tree IS a temptation gradient

Canon (§2.0c): Intellectual feeds **Ohm** (machine-advance) AND **Ozzik**
(research-as-ambition) — one of the few shared inputs. Normalization is where
that stops being flavor and becomes structure:

1. **Pride-weight per tier.** Every research completion fires `↑Ohm` (small,
   flat — the machine loves all daring) and `↑Ozzik` scaled by the project's
   tier: scavenger-tier utility (neolithic/early industrial — stills, traps,
   salvage benches) is pride-FREE; trade/industrial is a drip; spacer is a
   spike plus Visibility cost; ultra/archotech is the trap's teeth — the
   pride-crisis machinery (F13's Ozzik−Ishko gap) billing every step of the
   climb. **The research screen becomes the campaign's temptation diagram:
   the player can SEE the ambition gradient before clicking.**
2. **Restore ≠ transcend, in the tree itself.** Research that unlocks the
   REPAIR/RESTORATION of original ship systems is Rekko-tagged and
   pride-NEUTRAL (the canon line: restoring what was always there is humble
   work). The same capability built NEW beyond original spec sits on a
   different, Ozzik-weighted project. Where one mod project covers both, the
   manifest (§3) splits the theology, not the def.
3. **The droid branch is the flashpoint chain.** Ohm demands it (his hands),
   Oomo protests it (`↓Oomo` small per droid-tech completion — metal where
   eggs should be). Normalization should gather droid research into one
   visible branch so the argument is legible: the player walks INTO the
   Ohm/Oomo war knowingly, project by project.
4. **Ship-memory research** (ties the cradle_memory ruling): some projects
   should be HIDDEN until the ship surfaces them — the Rakatan story is
   learned FROM the vessel as events unfold, and `hiddenPrerequisites` +
   event-driven reveal is the vanilla-shaped mechanism. The Narrator announces
   a remembered schematic; a project appears. Research as revelation, not
   just spend.

## 3. Mechanical approach — three options, one recommendation

- **A. Patch-based prereq surgery** (XML PatchOperations per mod): 584 mods of
  xpath, every one a silent no-match risk, load-order sensitive, unmaintainable
  the first time any mod updates. Rejected.
- **B. RECOMMENDED — runtime normalization pass driven by a curated manifest.**
  A small C# `StaticConstructorOnStartup` pass that rewrites
  `ResearchProjectDef` fields (cost, prereqs, tab, techLevel, tags) from ONE
  data table (CSV/JSON in the mod, generated from the audit and hand-curated).
  Owner-rules-as-data, not prose: the manifest is diffable, auditable, and — 
  the decisive advantage over XML — **an unmatched manifest row LOGS LOUDLY**
  instead of silently matching nothing. Survives mod updates (defNames are
  stabler than XML structure). The theology tags (§2) live in the same rows,
  so the satiation engine reads the SAME manifest for pride-weights — one
  source, two consumers.
- **C. Suppress + replace** (Cherry-Pick foreign research, author our own tree
  granting the content): maximum control, catastrophic cost — re-homing
  thousands of unlockables, and mod C# that checks its own project keys breaks
  invisibly. Rejected as the general approach; kept as the scalpel for the
  handful of projects we genuinely ban (Cherry Picker already does this and
  its cuts are invisible to the dump — the audit must read cuts via
  cherrypicker.py, never a ninth regex).

## 4. The audit that must precede surgery

No surgery until a census under the measuring-large-artifacts discipline,
against the frozen official dump (fingerprint-checked), producing MEASURED:

- Total `ResearchProjectDef` count and per-mod breakdown. ⚠️ First verify the
  def type is populated in the dump at all — 79 def-type files are empty
  (absent from the dump ≠ absent from the game); if empty, the census goes to
  mod XML and says UNMEASURED where it cannot see post-patch truth.
- **Orphan prereqs**: every prereq reference resolved; unresolved = the defect
  list surgery must clear. Cross-check against the Cherry Picker cut list —
  a cut project's dependents are the invisible breakage class.
- Cost distribution by techLevel; duplicate-capability clusters (two mods,
  same unlock class); `requiredResearchBuilding` / techprint dependencies
  (each is a hard gate the manifest must respect); ResearchTabDef inventory.
- Deliverable: an audit table in the trap-audit mold, which then BECOMES the
  manifest's first draft (census → curation → manifest → runtime pass).

## 5. Sequencing — why gated, what can start now

Gated on droids landing because the droid work and the armoury absorptions
(WEAPONS_ABSORPTION_WAVE_1, trap renaissance, VEHICLE_ION_TIER_1) all re-home
defs under research gates — normalizing first means normalizing twice. Safe to
start before the gate: the §4 audit, the manifest schema, the §3B loader spike
(compile a minimal field-rewriting pass and prove the log-loudly behavior),
the tier taxonomy, and the tab design. The taste pass and the final curation
wait for the settled content inventory.

## 6. OPEN-FOR-OWNER — the taste calls only he can make

1. **The ceiling**: which tech eras may the Jawa ever reach? (Interacts with
   faction techLevel and the cost multiplier — a deliberately low colony
   techLevel makes the high tree EXPENSIVE, which is itself an
   anti-exponential lever already in the vanilla engine.)
2. **Theology-locked research** — the exciting option: highest-tier projects
   gated on Ozzik's standing ("the god of ambition holds the keys" — court him
   or the bench refuses you), and/or grand research BLOCKED during his
   grief-pall. Flag: gorgeous, but it hard-couples engine and tree; rule it
   deliberately.
3. **Tab philosophy**: keep mod tabs, or consolidate into campaign tabs
   (Scavenger / The Ship / The Machine / The Reach — the last one
   pride-marked)?
4. **Whether the manifest's theology tags ship in the core RimMandrake mod or
   the campaign layer** (RimMandrake moniker rules all shipping names).
