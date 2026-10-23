## spec
Seven Cauldron overlay textures the defs name do not exist anywhere in `src/` (measured 2026-10-16):
`Things/Plant/RM_AssayFlecks/Flecks_Light`, `.../Flecks_Heavy` (on RM_TreeMartyr and RM_TwistingThornwood via
`RM_AssayFlecksExtension`), and the five dew variants `Things/Plant/RM_Dewfall/<def>_dew` (CrystalFlower,
BloodBouquet, RedBugloss, KeeningCordax, GiantToxicFlower). The C# tolerates the gap (`RM_AssayFlecks` logs
"assay fleck overlays not on disk yet" and skips), so nothing errors and nothing shows.

Effect on the sprint: `src/RimMandrake/Cauldron/preflight_cauldron.py` row O-TEX (kickoff M2) FAILs on
RM_TreeMartyr and RM_TwistingThornwood until the flecks exist. Packet §1.1 Art set lists them; the dew-variant set
is an S1 rider (which accent plants get dew; the XML default of five stands).

Route: artpipe jobs (check `artpipe_state.py find` first), shown on the S1 sheet at true scale, installed with
`art.py enact` / art ledger. Cosmetic: the owner sees them before install.

## done when
`preflight_cauldron.py --rows O-TEX` PASS on a fresh composite deploy.
