# RESEARCH_TRIO_RETIRE_1 — retire steppingstones + als.gravtech x2, reconcile the recost

Filed (ledger, `file`, 2026-09-11T06:33:37Z, BENCH): retire `steppingstones` and
`als.gravtech` (both variants), re-run the research-recost validator, reconcile
the "112 collision rows" carried over from `STAT_NORMALIZATION_AUDIT_1` Wave 3.
The research-normalization pass this was meant to fold into is already closed,
so this item carries the remaining work solo. Owner ruling cited: 2026-09-11,
"fold into the research pass" (Wave 3, four cards).

## 🔴 ESCALATED — NOT EXECUTED. `ModsConfig.xml` untouched, no def cut.

Full diligence run (FOUNDRY, 2026-09-11), but the retirement was **not**
performed. This is not a stale-drop — real, load-bearing content is at stake
and the item as filed does not decide what happens to it.

### What "retire" would actually delete

The three packageIds and their live state (`ModsConfig.xml`, 579 active mods,
confirmed the FULL campaign list — not a crash-recovery minimal list — matches
the `daeef583` "FULL.LATEST modlist baseline (579 active)" commit):

| packageId | display name | own `ResearchProjectDef`s carried in `research_manifest_draft.csv` (2026-09-04, RESEARCH_RECOST_PREREQ_JOIN_1) |
|---|---|---|
| `petetimessix.researchreinvented.steppingstones` | Research Reinvented: Stepping Stones | 10 rows, all `fate=untouched` |
| `als.gravtech` | GravTech | 6 rows, all `fate=untouched` |
| `als.gravtech.bc` | GravTech - Big Cannons | 1 row, `fate=untouched` |

**These are not reference residue or dead scaffolding — they are the ONLY
place these `ResearchProjectDef`s are defined.** Confirmed by reading the
mods' own XML on disk:

- `als.gravtech`'s `1.6/Defs/Research_GT.xml` and `ThingDefs_Buildings/GravForge_GT.xml`
  define `GravForge`, `GravWeapon`, `GravTuning`, `AdvShipParts`, `BlackHole_GT`,
  `GravBionics` natively. Our repo never re-authors these — `src/RimUtinni/ResearchRetag/Patches/RUT_ResearchRetag.xml`
  and `RUT_ResearchTabAssign.xml` only PATCH tab/tier/prereqs onto the donor's
  own defs. Remove the donor, the underlying def is gone and the patch becomes
  a silent no-match (`PatchOperationConditional` — "a patch that matches
  nothing logs nothing").
- Same pattern for `als.gravtech.bc`'s `GTbc_BigCannons`.
- Same pattern for steppingstones' 10 `RR_*` rows (`RR_ElectricityBasics`,
  `RR_BasicApparel`, `RR_BasicCraftingFacilities`, `RR_BasicFoodPrep`,
  `RR_HeatingElements`, `RR_IncendiaryWeapons`, `RR_LateralThinking`,
  `RR_Organization`, `RR_PowerGenerators`, `RR_EMP`) — patched by our own
  `RUT_ResearchRetag.xml`/`RUT_ResearchTabAssign.xml` into the **Jawa
  Scavenging** and **The Workshop** tabs, several forming their own prereq
  chain (`RR_ElectricityBasics → RR_HeatingElements`/`RR_PowerGenerators`).

All 17 defNames confirmed **MEASURED present** in the live def dump
(`2026-09-11T06-28-49Z` capture, fingerprint `9d4f383502c115d3`, 579 mods —
matches the live `ModsConfig.xml` mod count) and referenced in the current
campaign save (`CANONICAL_ASHKARR_2026-09-09.rws`, mtime 2026-09-10 23:57).

### This is exactly the class of mod `stat_normalization_audit_2026-09-09.md`
### §2B already named and gated

Both `als.gravtech`+`.bc` and `petetimessix.researchreinvented.steppingstones`
sit in that doc's **2B "Conflicts that ALSO add content"** table (lines
145-146), whose own preamble reads: *"These are the same class as the
donor-retirement items: a cut here is a port."* Every other 2B mod in that
table (ReGrowth, Alpha Biomes, More Vanilla Biomes, etc.) is being handled
under the established donor-retirement discipline — port the content first,
or explicitly accept the loss — never a bare uninstall. Nothing filed against
this item does either for the research trio.

Worse, several of the at-risk rows carry **specific, dated prior owner
rulings** that a bare retirement would silently reverse:

- `GravWeapon` — owner ruling, 2026-09-01 (question card): "associate this
  ultra-powerful GravTech as something only the Rust Cathedral can grant as a
  boon. The weapon tech of the Rataka." Faction-held by `RustCathedralDroids`,
  tab `The Strange Schools`.
- `GravForge` — owner ruling, 2026-09-01: restore it on Cherry Picker rather
  than cut, "leave it in for now, handle anti-exponential another way later."
- `GravBionics` — same Rust Cathedral boon-gate as `GravWeapon` (owner card,
  2026-09-04), faction-held.
- `AdvShipParts`, `GravTuning`, `BlackHole_GT`, `GTbc_BigCannons` — all
  T4, tab `The Utinni`, explicitly named as the campaign's Ship-tree gravtech
  row cluster.
- The 10 `RR_*` steppingstones rows are wired into **Jawa Scavenging**, the
  clan's own early-game tab, with real prereq edges to `VFET_Tribalwear`,
  `VFET_Fire`, `VFET_Bow`, `Machining`.

Retiring the three mods as filed deletes all 17 nodes outright — no port, no
replacement, and no owner sign-off on losing the Rust Cathedral gravtech
branch or the Jawa Scavenging `RR_*` scaffold specifically (the 2026-09-11
Wave 3 ruling addressed this as a numeric "recost collision," not as
"delete the Ship-tree Rust Cathedral tech and part of the Jawa Scavenging
tree").

### The "112 collision rows" figure, precisely

`stat_normalization_audit_2026-09-09.md` line 145: steppingstones performs
**656 `ResearchProjectDef` operations** total (rewrites cost/prereqs across
most of the tree), of which **112 land on projects our own patches also
touch** — i.e. defNames NOT owned by steppingstones itself, where removing
the mod just drops a redundant/conflicting write (no content loss for those
112; this part is mechanical and would resolve itself once the mod is gone).
**The real risk is the 17 rows above, which are steppingstones'/gravtech's
OWN content**, not part of the 112 collision count and not something the
recost validator's mechanical checks (orphan/prereq/band/coverage/cycle) can
decide for you — those checks will faithfully report 17 new orphan/dead-prereq
FAILs once the mods are gone; they do not know whether that is acceptable.

### Baseline validator run (before any change, for reference)

`python3 src/RimMandrake/Utils/research_manifest_validate.py --inventory` —
dump matches live (579 mods), cut list 2,135 defs (live CherryPicker settings).
397 live `ResearchProjectDef`. One pre-existing defect found, unrelated to
this item's execution (may well be a symptom of the same mod collisions):
**`RR_ElectricityBasics -> RR_ElectricityBasics`** self-loop prereq cycle —
not the documented `RimFridge_PowerFactorSetting` known quirk, a genuine FAIL.
Our own `RUT_ResearchRetag.xml` (line 3114-3126) only *removes* that project's
`prerequisites` (dropping a tier-inverted `Smithing` edge per the manifest);
it does not add a self-reference, so the loop is coming from steppingstones
or another co-writer. Worth a look independently of this item, not chased
further here (not in RESEARCH_TRIO_RETIRE_1's scope).

Also present (pre-existing, unrelated): `--inventory` reports `GravForge`
"on the Cherry Picker cut list" — this is the same any-type-match false
positive the manifest's own `GravForge` note already documents and corrects
(`ThingDef/GravForge` + `RecipeDef/Make_GravcoreGF` were cut and restored
2026-09-01; `ResearchProjectDef/GravForge` itself was never on the list).
`inventory_orphans()` uses `cuts.cut_name()` (any-type) rather than the typed
check `check_orphans()` uses for a manifest run — a known, already-documented
gap in `--inventory` mode, not a new defect.

### Dependency sweep (fresh, 579-mod live list)

Full-tree grep of every installed mod (workshop + local) for each of the three
packageIds, `About.xml` only (`modDependencies`/`loadAfter`/`MayRequire` etc.):

- `als.gravtech`: referenced by `Joe.MO.Tweaks` (loadAfter), `als.anomalygravship`
  (loadAfter — Anomaly-for-Gravship submod), `als.gravtech.bc` (hard
  `modDependencies` + loadAfter — Big Cannons REQUIRES base GravTech), and our
  own `Armoury` + `ResearchRetag` (loadAfter hints, not hard dependencies —
  their real gates are `PatchOperationConditional`/`PatchOperationFindMod`).
- `als.gravtech.bc`: referenced by its own retexture `HalituisAmaricanous.gravtechbigcannons`
  (hard `modDependencies` + loadAfter) and our own `Armoury`/`ResearchRetag`
  (same as above).
- `petetimessix.researchreinvented.steppingstones`: **zero** external
  references by packageId in any active mod (including our own) — but see
  above, our own patches reference its *defNames* directly, which a
  packageId-string sweep cannot see.

So: retiring `als.gravtech` without also retiring `als.gravtech.bc` and
`HalituisAmaricanous.gravtechbigcannons` (its dependent retexture, currently
classified cosmetic-only/inert in the audit's §2D bucket) would leave a hard
`modDependencies` failure at load (Big Cannons requires base GravTech). The
item as filed only names the trio; the retexture companion is a 4th mod that
would also need to go, or `als.gravtech.bc` would need to stay.

## What this item needs before it can execute

An owner call on the 17 at-risk rows — none of the three options below is
something FOUNDRY can pick on its own, per this repo's "a cut is a port"
donor-retirement doctrine and the CHARTER rule that a reversal of a dated
owner ruling is the owner's, not a subagent's:

1. **Port first** — re-author the 6 GravTech + 1 Big-Cannons + 10 steppingstones
   rows as native `RimUtinni`-owned `ResearchProjectDef`s (same tab/tier/
   prereqs/faction-gate) before removing the donor mods, exactly like the
   established donor-retirement pattern elsewhere in this project
   (`WEAPONS_DONOR_RETIREMENT_1`, `MLIE_FAUNA_ABSORPTION_1`).
2. **Accept the loss** — explicitly rule that the Rust Cathedral gravtech
   branch (Ship tree T4 + `The Strange Schools`/`The Reach` faction-gated
   rows) and the 10 Jawa-Scavenging `RR_*` early nodes are cut with no
   replacement, and say what (if anything) re-fills those tab/prereq slots so
   `check_coverage`/`check_prereqs` don't just report a hole.
3. **Counter-patch only, keep the mods** — same shape as Wave 4's MV Textures
   resolution: neutralize the specific colliding fields (steppingstones' cost/
   prereq rewrites, gravtech's 9 `baseCost` replaces + `damageAmountBase` +
   `statBases`) with our own counter-patch instead of removing the mods, so
   the content and the prior owner rulings both survive untouched.

Whichever the owner picks, re-running
`research_manifest_validate.py --inventory` (or against the manifest once one
of the three routes updates it) is the correct verification step — it is
already proven working against the current 579-mod list (see baseline run
above) and will show the 17-row hole (or its absence) precisely.

## verify (once a route is chosen)
- Route 1: the 17 rows exist as native defs post-port; `--inventory` shows no
  new orphans/dead-prereqs where they used to sit; the two mods' removal from
  `ModsConfig.xml` (backed up first, delta count confirmed) plus their now-dead
  companion retexture if `als.gravtech` goes.
- Route 2: manifest rows for the 17 updated to `fate=cut` with prereq
  re-anchoring (same mechanism `RESEARCH_RECOST_PREREQ_JOIN_1` already used for
  106 tier-inverted edges), owner sign-off recorded, `check_prereqs`/
  `check_coverage` clean against the post-cut dump.
- Route 3: no `ModsConfig.xml` change; a new counter-patch neutralizes the 9+14
  colliding fields; `--inventory`/manifest run shows the collision gone and the
  17 rows still present, untouched.

## done
Not started — escalated, per this item's own "escalate if the 112 rows can't
be resolved without inventing a research-tree placement decision" clause.
