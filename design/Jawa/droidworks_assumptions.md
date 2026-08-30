<!-- status: LIVE — the owner asked for this list verbatim, 2026-08-29:
     "Make a list of the assumptions you'd like me to check later." Check a box
     by ruling on it at the bench; each carries what changes if you rule the
     other way. -->
# Droidworks — assumptions awaiting the owner

## Platform boundaries
1. ✅ RULED YES (owner, 2026-08-29). **HAR stays as the one dependency.** "As independent as possible" read as
   independent of the DROID packs; HAR underpins 13 mostly non-droid mods in
   the load and stays regardless. If you want HAR gone too, races get
   reimplemented on raw humanlike ThingDefs — doable, roughly doubles the race
   authoring, and we lose HAR's body/needs tooling.
2. **"Retire" = remove from ModsConfig eventually, keep on disk.** Credits
   live in Droidworks' About.xml (guy762, Neronix17, JangoD'soul+Criz,
   Killathon). Private play, no redistribution — your words carried into the
   About text.
3. **Retiring ABF/Synstructs is NOT free**: KotOR Weapons and Armor + KotOR
   Resources/Materials (content we keep — the armoury uses those weapons)
   DECLARE it as a dependency. Assumed: declaration only, no hard runtime use —
   must be verified (minimal-list load without ABF, watch for errors) before
   ABF actually leaves ModsConfig. Same check for Asimov ← FSF Complex Jobs.

   **FOUNDRY-verified, 2026-08-30** (grep of the live install paths, mod-set
   fingerprint 2026-08-30T01-41-15Z, 585 mods — `guy762.mm.kotorcore` =
   `.../workshop/content/294100/3254370945`, `guy762.kotorweapons` =
   `.../2938932438`). **The "declaration only" premise is FALSE.** Both KotOR
   mods contain real, UNGATED (no `MayRequire`) C# class references into ABF's
   `ArtificialBeings.*` namespace, in content we keep, active under 1.6 today:
   - **KotOR Resources and Materials**, folder `1.6/AdditionalMods/_DroidsBase`
     (`LoadFolders.xml` gates this folder on `guy762.KotORDroids` only — no ABF
     gate at all): `AlienRace_KotORDroidBase.xml:121`
     `<compClass>ArtificialBeings.CompCoherenceNeed</compClass>` — this is the
     abstract race parent named in assumption 18
     (`guy762_KotORDroidBase`), so ABF's own need-comp is wired straight into
     the droid race every KotOR droid inherits. (Item 18's mod NAME is
     slightly off, workshop ID is right: this file lives in **KotOR Resources
     and Materials** / `guy762.mm.kotorcore`, workshop `3254370945` — not
     "guy762.KotORWeapons"; `guy762.kotorweapons` is the separate Weapons and
     Armor pack at workshop `2938932438`.) Same folder:
     `PawnKinds_PlayerDroidBase.xml:13` and `PawnKinds_RogueDroidsBase.xml:34,68`
     (`<li Class="ArtificialBeings.ABF_ArtificialPawnKindExtension">`, 3 sites)
     and `ThingDefs_DroidEquipment/ThingDefs_DroidBatteries.xml:50,73,113`
     (`ABF_NeedFulfillerExtension` / `IngestionOutcomeDoer_OffsetArtificialNeed`,
     3 sites) — 7 ungated sites total. (The parallel `_BnSDroidsBase` folder
     gates the same classes with `MayRequire="Killathon.ArtificialBeings.SynCore"`
     — except `ABF_NeedFulfillerExtension`, which is ungated there too — so
     whoever wrote `_BnSDroidsBase` later knew the guard was needed and mostly
     added it; `_DroidsBase` never got the fix.)
   - **KotOR Weapons and Armor**: `1.6/Defs/TraderKindDefs/OrbitalTrader_Baragwin.xml`
     and `BaseTrader_Baragwin.xml`, 2 `<li>` each (4 sites) —
     `<li MayRequire="guy762.KotORDroids" Class="ArtificialBeings.StockGenerator_Colonists">`
     stocking `KotORDroidColonist_*` pawnKinds on the Baragwin weaponsmith
     trader. Gated on KotOR Droids being active, NOT on ABF.
   - The mods' 1.5-only compat patches (KotOR Weapons' `AthenaFramework`
     folder — commented OUT of `LoadFolders.xml`'s `<v1.6>` block entirely;
     KotOR Resources' `MHC`/`ATC` folders, gated `IfModActive="Killathon.*"` at
     the LoadFolders level) self-exclude cleanly today and need no patch.
   - **Verdict: ABF/Synstructs — NEEDS PATCHES, not free.** 11 XML sites across
     3 files (2 in KotOR Weapons, the rest in KotOR Resources' `_DroidsBase`)
     must be patched (delete or reclass the `<li>`/`<compClass>` entries) before
     ABF/SynCore leave ModsConfig, or the droid race's own need-comp, its
     pawnKind extensions, its battery ingestibles, and 4 trader stock lines
     throw "could not find class" errors at load. This is exactly the wave-1
     "strip ABF comps/needs, add ours" work already scoped in
     `droid_system_build_spec.md` §7 — so it's a known, budgeted patch job, not
     a new blocker, but assumption 3's "declaration only" framing does not
     hold and should not be repeated.
   - **Asimov ← FSF Complex Jobs, and what "Asimov" means**: confirmed via the
     manifest that **Asimov = `Neronix17.Asimov`** (packageId
     `neronix17.asimov`), the real third-party auto-crafter framework mod that
     Outer Rim – Droid Depot rides for its buildable Droid Factory — NOT this
     project's own `Jawa_Doctrine/Patches/DroidsAreMachines.xml`. That doctrine
     file only sets `isOrganic` on the `Asimov_Automaton` and
     `ABF_FleshType_Synstruct_Base` FleshTypeDefs via `PatchOperationFindMod`
     gated on the mod's display name — it contains zero `Asimov.*`/
     `ArtificialBeings.*` class references, so it degrades to a clean no-op if
     either framework leaves. **`[FSF] Complex Jobs`** (packageId
     `frozensnowfox.complexjobs`) is confirmed a genuinely separate mod, and it
     DOES reference `Asimov.CompProperties_Automaton` at runtime — ~30 XML
     patches (one per added work type: Taming, Slaughter, Mechanoids, Paint,
     …) xpath into that comp's `enabledWorkTypes`. Every one of those patches
     wraps the whole `PatchOperationConditional` in
     `MayRequire="Neronix17.Asimov"`, so all ~30 cleanly no-op if Asimov is
     retired. No other kept mod (`Jawa_Patches`, `Jawa_PawnFlavor`,
     `Jawa_Armoury`, `JawaIonWeapons`, `JawaFactionSlate`, `Jawa_Doctrine`)
     references `Asimov.*` classes at all.
   - **Verdict: Asimov — retires clean**, apart from its own intentional rider
     (Outer Rim – Droid Depot, retired in the same wave by design). One loose
     end it leaves behind: see the item-14 addendum below — 82 stale
     `Asimov.Need_Energy` need instances sitting in the frozen v1 save, which
     will start throwing "could not find class" on THAT save's next load once
     Asimov is gone (harmless — see below — but worth a save-scrub note on the
     Asimov-retirement checklist).
4. ✅ RULED CAPTURABLE (owner, 2026-08-29). **JDS Separatists become capturable on port** (spec §8.3 recommendation;
   the 2026-08-13 "never taken alive" ruling was platform-forced). Unruled —
   wave 3 assumes yes; say no and they get high energy-density detonation
   flavor instead.

## Art
5. **Yank keeps original texPath structure** so generated defs reference art
   unchanged; you regenerate freely later by overwriting files in
   `src/Jawa/Droidworks/Textures/` (same path = same def, no XML edit needed).
6. Droid Depot 1.6 art comes out of Unity AssetBundles — assumed the extracted
   PNGs are the same assets the game renders (validated only by file
   inspection until a live look).

## Numbers I picked (tune at the bench, none are canon)
7. **Detonation**: damage `50 × charge × energyDensity`, radius
   `3.9 × sqrt(scale)`; wreck threshold: no boom below 5% charge.
8. **Power cadence**: fall/day — battle 1.0 (daily top-off), astromech/labour
   0.33, protocol 0.033 (~monthly), per the design spec's prose.
9. **Reboot restores 15% power** so the droid can walk to a charger (phase 0
   has no charging building yet — the trio [nimbus/dock/socket] is next).

## Mechanics assumed viable, unproven in engine
10. A humanlike race with our non-organic flesh type **goes Downed on the
    Consciousness cap** (capacity-based downing) — the one step never observed
    live; phase-0 pilot proves it (also flagged in droid_ruling.md §5A).
11. **Food/rest suppression via HAR race settings** suffices for droids (no
    Biotech genes involved). If HAR can't fully suppress, fallback is a
    hediff/Harmony layer — small but unbudgeted.
12. **Mindless/programmable/sapient work gating** via one Harmony postfix on
    WorkTagIsDisabled (phase 1) — pattern assumed from ABF's existence proof.
13. **No Harmony at all in phase 0** — state 4 is vanilla death-with-corpse,
    state 5 is our comp on Notify_Killed, state 3 is a no-decay hediff.
    If play shows droid "death" needs interception (e.g. corpse-vs-object
    semantics), phase 0 grows the one risky Harmony unit after all.

## Loose threads
14. **82 `Asimov_EnergyNeed` strings sit in the frozen world save** with zero
    droid pawns scribed — unexplained; must be understood before Asimov leaves
    the mod list (likely harmless need-registry residue; UNCERTAIN).

    **FOUNDRY-verified, 2026-08-30** (`rimworld-savegame` skill's grep method,
    `MEASURE_ALLOW_SCAN=1 grep -c '<def>Asimov_EnergyNeed</def>'` against
    `world/WORLDMAP_V1_original.rws`, 21.8 MB, confirmed **82**; every hit's
    parent structure walked by hand and cross-checked with a script that
    resolves each hit to its enclosing pawn's `<kindDef>`). Each occurrence is
    the same three-line pattern, sitting inside an ordinary pawn's
    `<needs><needs>` list next to `Need_Mood`/`Need_Food`/`Need_Rest`:
    ```
    <li Class="Asimov.Need_Energy">
      <def>Asimov_EnergyNeed</def>
      <curLevel>1</curLevel>
    </li>
    ```
    It is **not** a template, a comment, or a list-of-defs registry entry — it
    is a real, per-pawn `Need` instance. Resolving all 82 hits to their owning
    pawnKindDef found **zero droid kinds** (confirmed: neither the assumption
    doc's premise nor the "likely residue" guess was about a decoy — there
    really are no droids in this save) and instead a wide, ordinary cross-
    section: animals (11× Eopie, 7× Bantha, 6× Megascarab, 5× Corinathoth, 5×
    AA_Behemoth, 3× Bolotaur, 3× IridonianReek, 2× Uvak, 2× Manka, 1× each
    Lothcat/JRWGeralinura/BMT_FungalFerret/BMT_FacetMothLarvae/Behemoth),
    mechanoids (1× each Mech_Militor/Mech_CentipedeGunner/Mech_Pikeman), and
    humanlikes (4× plain `Colonist`, 1× `VQE_Inventor` — the pawn `Dr.
    Florence`, `Human62175` — plus 1× each `Jawa_Tribal_Elder`,
    `Jawa_DeepDesert_Leader`, `Jawa_Empire_Leader`; 17 hits' enclosing
    `<kindDef>` fell outside the backward scan window and were not resolved,
    but every SAMPLED one landed on a non-droid pawn). All 82 sit at
    `<curLevel>1</curLevel>` — full, and never once seen at any other value.

    **Plain-terms explanation**: Asimov's `Asimov_EnergyNeed` NeedDef carries
    no race restriction, so RimWorld's needs-tracker auto-adds one instance of
    it to every pawn's needs list on generation — animal, mechanoid, or
    human — regardless of whether that pawn's race actually uses
    `Asimov.Need_Energy` for anything. It fills to `1` on creation and nothing
    in a non-`Asimov_Automaton` pawn's think tree, job driver, or mood system
    ever reads or drains it, so it just sits there, inert, forever at full.
    This is exactly the "harmless need-registry residue" the assumption
    guessed — confirmed concretely, and CURED of the "UNCERTAIN": it is a
    known Asimov modding footgun (a global unrestricted NeedDef), not a
    Jawa-side bug, a corrupted save, or evidence of an unscribed droid.
    **One real, low-severity consequence for the Asimov retirement**: the
    `Asimov.Need_Energy` class lives in the Asimov assembly. If this exact
    save (`WORLDMAP_V1_original.rws`) is ever reloaded under a mod list with
    Asimov removed, Scribe will fail to instantiate those 82 `<li>` entries
    (the def-loader/Scribe distinction in the `rimworld-savegame` skill: this
    would be a "could not load reference to" Scribe-side failure, not a
    def-loader one) — 82 log lines, one per stale need, on that load. Harmless
    to play (the need entry is simply dropped, and none of the 82 owning pawns
    are droids so nothing downstream depends on it), but real log spam;
    scrubbing these 82 `<li>` blocks from the save (or letting a fresh
    needs-list regen overwrite them) before or at the Asimov-retirement save
    boundary is a cheap, worthwhile cleanup, not a blocker.
15. Our 4 existing `Jawa_Droid_*` kinds (Free Droid Enclaves) ride Droid Depot
    races today; wave 2 re-points them to Droidworks races **at a save
    boundary you pick** — live campaign droids of those kinds would dangle
    otherwise.
16. Droidworks is **not yet in ModsConfig** — activation is yours at a
    start-prep pass (rimworld-start-prep rules apply; RimSort refresh trap).
17. ✅ RULED QUEST-PACK-ON-TOP (owner, 2026-08-29). The shop CUSTOMER layer
    ships as a separate quest/incident mod later; Droidworks stays pure platform.
18. **A fifth mod holds KotOR droid plumbing**: the abstract race parent
    `guy762_KotORDroidBase` and the droid-slot equipment art
    (`droidshield_*`, `droidtech_*`, `hvyshield_*`) live in
    `guy762.KotORWeapons` (workshop 3254370945) — a mod we KEEP for the
    armoury regardless. Assumed fine to leave that art un-yanked for now;
    the def generator must read the base's fields from that mod's XML, not
    assume extraction.json has them. (Found by the art sweep, 2026-08-29.)
19. Two Droid Depot UI icons had bundle paths that differ from def texPaths
    (cultures/memes icons); extracted to the DEF paths. Assumed the def path
    is the truth (per reading-rimworld-graphics).
