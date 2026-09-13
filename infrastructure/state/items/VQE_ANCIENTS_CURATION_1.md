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

## NOT done — step 2, rest of step 5
- **Step 2**: no action needed — Herculean/Prowess were never touched.
  Not separately re-verified as "still present" against a live dump this
  session; low risk since nothing in this pass could have cut them.
- **Rest of step 5**: the actual site-tile-biome check, owed once the
  quest fires for real (~day 30-118 depending which chain). Not
  chaseable before then.

## done this session (2026-09-13) — step 4 (string relabel)
Read the donor mod's actual quest XML off disk (found via `About.xml`
matching packageId `vanillaquestsexpanded.ancients`, display name "Vanilla
Quests Expanded - Ancients", at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3618306875`
— same Workshop tree `AncientsAreRakata.xml`'s own guard string points at):
all 6 `Defs/Quests/Quest_*.xml` chains (`AncientLabComplex`,
`AncientResearchVault`, `ArchiteArraySite`, `ArchiteControlVault`,
`InhibitorResearchLab`, `SpliceframeBlacksite`) plus the
`QuestChain_TheAncientLab.xml` wrapper — `questNameRules`,
`questDescriptionRules`, and the `QuestChainDef`'s own label/description.
Confirmed the item's own earlier note: no literal "pre-collapse-human-
civilization" phrase, and also no "self-replicating flesh" phrase — that's
all owner paraphrase, not donor text.

Read `AncientsAreRakata.xml` for the register (Rakata endonym / **Forsaken**
exonym for the ancients-survivors / **Assailant** exonym for their attacker)
and its mechanism: our own `PatchOperation*` file in
`src/RimUtinni/UtinniPatches/Patches/`, guarded by
`PatchOperationFindMod` on the donor's display name, never touching the
donor's own files.

**New file: `src/RimUtinni/UtinniPatches/Patches/VQEQuestText_AreForsaken.xml`**
(guarded `PatchOperationFindMod` / "Vanilla Quests Expanded - Ancients", same
as `VQEPatients_AreRakata.xml`). 7 `PatchOperationReplace` ops, each
targeting one exact `<li>`/`<label>`/`<description>` node by xpath (the
`rulesStrings` lists have no dictionary keys to collide on and no other mod
patches this donor's quest text, so a positional `li[n]` xpath is the
smallest safe surface — full rationale in the file's header comment).
Relabeled every literal "ancient" (adjective for the pre-collapse
civilization/its works) → **Forsaken** ("an ancient X" → "a Forsaken X"):
  - `Quest_AncientLabComplex`: "an ancient military supersoldier program",
    "some kind of ancient broadcasting station", "ancient traps may still
    be functional", "producing ancient supersoldiers" (2 `<li>`s, 4 phrases)
  - `Quest_AncientResearchVault`: "loot the site for ancient technology"
  - `Quest_ArchiteControlVault`: "an additional ancient laboratory site"
  - `Quest_InhibitorResearchLab`: "some ancient network...", "that of an
    ancient reconnaissance worker" (2 phrases, 1 `<li>`)
  - `QuestChain_TheAncientLab`: label "The Ancient Lab" → "The Forsaken
    Lab"; description "created by the ancient military" → "...Forsaken
    military"

**Left as-is, explicitly, per the item's own warning against guessing
wrong:**
  - `Quest_ArchiteArraySite.xml` and `Quest_SpliceframeBlacksite.xml` — zero
    occurrences of "ancient" in their quest text; nothing to relabel.
  - `Quest_AncientResearchVault`'s four "story" `<li>`s (patient-uprising /
    cult / telepath / shapeshifter vignettes) — never say "ancient", never
    name an attacker; read as the program's own internal staff-vs-patients
    conflict. Relabeling "doctors"/"patients"/"executives"/"monstrosities"
    would be inventing a register the text never invokes.
  - "injecting archites directly into human subjects"
    (`Quest_AncientLabComplex`) — describes the Archogen Injector's general
    function, ambiguous whether historical (the ancients' own victims) or
    prospective (the player's future use). Left alone.
  - **The Assailant register was not used anywhere** — none of the six
    quest chains names or describes whatever attacked the ancients; the
    donor's own text never invokes an attacker at all, so there was no
    correct place to apply it. Not a gap; a finding.

Validated: `validate_patch.py` (see `## verify`) — 0 errors, 0 warnings, all
7 ops hit exactly 1 live node each in the donor's quest XML.

## verify
Step 1: `cherrypicker.py --source live --is-cut`, all 9 → CUT (done).
Step 3: read the donor's patch file directly, confirmed no archite
content (done). Step 4: `python3 skills/rimworld-modding/scripts/validate_patch.py
src/RimUtinni/UtinniPatches/Patches/VQEQuestText_AreForsaken.xml --defs
"/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" --defs
"/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100" --defs
"/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods"
--mods-config "<LocalLow>/Config/ModsConfig.xml"` → OK, 0 errors, 0
warnings, 7/7 ops 1 match each (done). Step 5: `ticksGame` read via bridge,
confirmed quest hasn't fired (done, partial). Step 6: entry added to the
roster doc (done). Steps 2/rest-of-5: not started. Step 4's live-game
liveness (deploy + Player.log check) is unverified — this pass only wrote
and offline-validated the patch; it has not been deployed to the Mods
folder or loaded in-game.
