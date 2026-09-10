## spec
Owner-said: "Keep-curated." Curate VQE Ancients per the ratified verdict —
6 sub-parts: (1) CherryPicker-cut Levitation/Invisibility/InfernoSpew +
granting genes + the hellsphere cannon; (2) keep Herculean/Prowess as
scarce vault loot; (3) audit/strip its Empire FactionDef patch; (4) string
relabel pass (pre-collapse-human-civilization → Forsaken/Assailant
exonym); (5) verify VQE_AncientLabComplex's site tile lands in an
ANCIENT-ALLOW biome when it self-fires (~day 118); (6) feed
VQEA_Spliceling/Splicehulk/Splicefiend/Splicetoot into the
dungeon-guardians draft roster. BENCH note (same day): the canonical
save's `futureQuests` already schedules `VQE_Cryptoforge_Chapter1` at tick
1800000 (~day 30) — a self-scheduling pattern, not this item's mod, but
recorded as the mechanism VQE_AncientLabComplex uses too.

## done this session
- **Step 1**: CherryPicker-cut, verified live. Real defNames (none guessed
  — read off the donor's own `Abilities.xml`/`GeneDefs_Archite.xml`):
  `AbilityDef/VQEA_Levitation`, `GeneDef/VQEA_Levitation`,
  `AbilityDef/VQEA_Invisibility`, `GeneDef/VQEA_Invisibility`,
  `AbilityDef/VQEA_InfernoSpew`, `GeneDef/VQEA_InfernoSpew`. "The
  hellsphere cannon" turned out to be an ABILITY
  (`AbilityDef/VQEA_HellsphereBlast`, also a `GeneDef` of the same name)
  plus its projectile `ThingDef/VQEA_Bullet_HellsphereCannonGun` — no
  standalone weapon ThingDef exists, so cut all three. 9 keys added to the
  ratified list, `cherrypick_build.py --write` → 1972 keys, all 9
  confirmed `CUT` via `cherrypicker.py --source live --is-cut`. Checked
  the donor's own def tree for anything else referencing these 4 genes
  (a XenotypeDef forcing one, say) — only the paired `Hediffs_Genes.xml`
  entries reference them, which just go unused, not broken; no XenotypeDef
  in the donor requires any of the four. No `decisions_*.json` category
  fits genes/abilities (no such file exists), so this cut's provenance
  rests on the ratified file + this record, not a decisions-file entry.
- **Step 3**: audited. `RoyaltyPatch.xml` is the ONLY patch in the donor
  touching `FactionDef[defName="Empire"]`, and it only adds
  `VQE_NewVaultPlayerFaction` to `permanentEnemyToEveryoneExcept` — a
  faction-relations exception for quest mechanics, not an archite-gene
  grant. **Nothing archite ships to Empire through it** — audited and
  found clean, not silently skipped. Left in place; it's needed for the
  quest chains step 5 keeps.
- **Step 5, partially**: took the bridge for a read-only check (no
  mutation) — current campaign tick is 109173 (~day 1.8). Nowhere near
  day 30 or day 118; `VQE_AncientLabComplex` genuinely has not fired.
  Confirmed rather than assumed; nothing to verify yet.
- **Step 6**: `VQEA_Spliceling`/`Splicehulk`/`Splicefiend`/`Splicetoot`
  (exact defNames verified against the donor's `Races_Animal_Mutants.xml`
  — note `Splicetoot` is singular even though its containment building is
  `...SplicetootsContainment`) added to
  `design/Jawa/worldbuilding/review/round2/reserved_groups_draft.md`'s
  dungeon-guardians table, clearly marked as sourced from this item rather
  than blended into the original `fauna_assignment_register.decisions.json`
  extraction (VQE Ancients wasn't in that review pool).

## NOT done — step 2, step 4, rest of step 5
- **Step 2**: no action needed — Herculean/Prowess were never touched.
  Not separately re-verified as "still present" against a live dump this
  session; low risk since nothing in this pass could have cut them.
- **Step 4 (string relabel)**: the literal phrase "pre-collapse-human-
  civilization" does not exist anywhere in the donor mod (checked
  `Languages/`, `Defs/Quests/`, `Defs/RulePackDefs/`) — it's the owner's
  own paraphrase, not a quotable string. Found the real target: e.g.
  `Quest_AncientLabComplex.xml`'s `questDescriptionRules` says "injecting
  archites directly into human subjects." Read
  `AncientsAreRakata.xml` (the existing "six pawn-kind relabels" mechanism)
  to resolve the register properly: Rakata is the ENDONYM, **Forsaken**
  is the exonym for the ancients/survivors, and (confirmed from
  `reserved_groups_draft.md` §1 and Boomalope's own cut note, "Convert to
  a twisted thing the Assailants make in their dungeons") **Assailant** is
  the exonym for whatever attacked them with "self-replicating flesh."
  Register now understood, but applying it correctly across 6 quest
  chains' worth of `RulePackDefs`/`questDescriptionRules` — deciding which
  specific phrase becomes which exonym, and writing it as our own
  LanguageData/patch override rather than editing the donor — is a real
  text-curation pass, not a quick swap. Left for its own pass rather than
  guessing wrong on which lines get which register.
- **Rest of step 5**: the actual site-tile-biome check, owed once the
  quest fires for real (~day 30-118 depending which chain). Not
  chaseable before then.

## verify
Step 1: `cherrypicker.py --source live --is-cut`, all 9 → CUT (done).
Step 3: read the donor's patch file directly, confirmed no archite
content (done). Step 5: `ticksGame` read via bridge, confirmed quest
hasn't fired (done, partial). Step 6: entry added to the roster doc
(done). Steps 2/4/rest-of-5: not started.
