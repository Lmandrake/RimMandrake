# BUG_TURRET_ART_REDO_1 — redraw the cartoonish bug turrets

Owner, 2026-08-29 (verbatim): "Gotta redo the art on those cartoonish bug
turrets." Targets: VFEI2_Vilelobber, VFEI2_Thornworm (2x2) and
VFEI2_Thornspitter (1x1) — all three RULED into the Geonosian Foundry Hive
register on the turret canon (turret_register.json), with a proposed sonic
re-projectile still pending the owner's word.

Route: `generating-rimworld-sprites` (reference-matched canvas/alpha/silhouette,
offline validator) against the hive's existing art register; the current
textures live in VFE Insectoids 2 (texPaths in turret_register.json rows).
Deploy as a retexture patch, NOT an edit to the donor mod. Prove in-game per
the skill (texture binds by texPath — [[texture-binds-by-texpath-not-defname]]).

## criteria

- [x] Three new textures painted to the Geonosian Foundry Hive register (rust,
      chitin, riveted bone/skull trophies, a dark hive-mouth aperture), each
      def now unique — the Vilelobber/Thornworm texPath collision confirmed
      and fixed. Canvas kept at the donor's own size (256x256 / 256x256 /
      128x128 — already at the skill's 128px/cell target, no upscale needed).
      `src/Jawa/Jawa_Patches/Textures/Things/Building/InsectoidTurrets/Jawa_Vilelobber_Base.png`,
      `Jawa_Thornworm_Base.png`, `Jawa_ThornspitterSmall_Base.png`.
      Differentiated per the owner's brief: Vilelobber carries acid sacs and
      corrosive yellow-green ichor at the maw (it spits acid); Thornworm
      carries a crown of bone-white chitin thorns around a dark segmented
      worm-ring maw, no acid (it ejects thorns — this is the visual
      differentiator from Vilelobber); Thornspitter is the same thorn family
      deliberately simplified — one rusted collar, four thorns, no trophies —
      reading as the small/tiny sibling mound. All three passed
      `validate_sprite.py` against the donor's own reference PNGs (Vilelobber
      and Thornworm: PASS with a 0.2-0.8% faint-alpha warning, consistent with
      the acid-glow/highlight painting, confirmed intentional by eye; the
      first Thornspitter draft REJECTED on span/aspect/origin — an asymmetric
      trophy skewed the bbox — regenerated with a full-bleed symmetric
      composition and it PASSED clean).
- [x] `BugTurretRetexture_GeonosianHive.xml` — `PatchOperationFindMod` on
      "Vanilla Factions Expanded - Insectoids 2", one `PatchOperationReplace`
      per defName against `graphicData/texPath`. Mechanism verified, not
      guessed: `VFEI2_Vilelobber` and `VFEI2_Thornworm` both inherit
      `graphicData/texPath` from the abstract `ParentName="VFEI2_TurretBase"`
      (`Buildings_Insectoid.xml:2397`) with no override of their own — that
      inheritance is *why* they render identically today. RimWorld resolves
      `ParentName` before running patches, so the plain
      `Defs/ThingDef[defName="..."]/graphicData/texPath` xpath (no child-value
      predicate needed — unlike `GrimTerraTexPaths_Fix.xml`'s list-`li` case,
      each of these three defs has exactly one texPath node) resolves against
      the merged tree at patch time. `Thornspitter` declares its own
      `graphicData/texPath` directly and matched on-disk immediately.
      `validate_patch.py --defs <Mods> --defs <Workshop/294100> --live
      <2026-08-29T20-07-29Z capture>`: OK, 0 errors, 0 warnings — Vilelobber
      and Thornworm show "0 nodes on disk, but 'X' EXISTS in the live game"
      (expected for the ParentName case, confirmed by the grep above, not
      just trusted); Thornspitter matched 1 node on disk directly.
- [x] Deployed: `deploy_custom_mods.py --mod Jawa_Patches --apply` — 4 files
      (the patch XML + 3 PNGs), plan read before apply, `VERIFIED in sync`.
- [ ] **In-game confirmation owed on the next cold load — NOT done, game was
      DOWN this whole item.** `graphicClass` on all three is
      `Verse.Graphic_Single` (confirmed against the live def dump) — no
      facing suffixes, one texture each.
      PROVE   spawn or find a `VFEI2_Vilelobber`/`VFEI2_Thornworm`/
              `VFEI2_Thornspitter` on a map, default zoom, no rotation.
      EXPECT  Vilelobber and Thornworm read as visibly DIFFERENT turrets
              (acid-green drip vs. bone-thorn crown) rather than the old
              identical blob; Thornspitter reads as a smaller, cruder version
              of the same rust/chitin family, not the old olive lump.
      LIES    the bare-path fallback (`ContentFinder.Get` on the un-suffixed
              path) would silently draw nothing-changed if the deploy had
              missed a file — deploy's own `VERIFIED in sync` line rules that
              out, but only a live look proves the render itself, per
              [[texture-binds-by-texpath-not-defname]].
      Also unresolved by construction, correctly out of scope: the "sonic
      re-projectile" idea on Vilelobber's `turret_register.json` row is still
      `contested: true` and untouched — this item did not touch damage,
      projectiles, or stats on any of the three.
