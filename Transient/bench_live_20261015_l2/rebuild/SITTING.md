# Pyrelands review save rebuild — 2026-10-15 evening

**Save:** `RM_pyre_review_20261015_r2` (game left RUNNING, paused, camera on station 1). The earlier
`RM_pyre_review_20261015` is untouched; Saves backed up before the rebuild to the BENCH seat tmp.

**Deployed from a clean `git archive` of e37e813934** (the dirty JawaBenchPawnKitTools.cs peer edit was not built):
- RimMandrake.Biomes (`--compose biomes --apply --prune`, 31 files): Pyrelands art (Ashwallow + dome S/E/N,
  Emberscythe N, Fire-hawk N + flight 4/5 E, Fire-wasp E/N), FireEcologyHook.dll, Stillsand dll + glass chain,
  LongShade items. Pruned: fulgurite + lightning-breaker defs/art and `RM_FE_QuickgrassA.png`.
- FlowWorks dll, GimmeSomeSlack dll, SWBestiary Dalgo N/S (10 files, no prune). EmpirePursuit, PyrelandsMechanics,
  UtinniPatches, WeatherSuite, LuminousPigment, MandrakePatches: already in sync.
- Companion `build.py --gm --apply` from the export.
- ModsConfig: the 23-mod ratchet_pilot + EmpirePursuit tier kept (copy: `ModsConfig.at_launch.xml`); owner backup
  `../ModsConfig.OWNER_BACKUP_before_review_walk.xml` untouched.

**Verified by state read:** 37/37 stations as built; 44/44 sign books, every title carries its DO line; furnace-beast
and control pen both 10.0 C at save; no fulgurite/breaker thing on the map; every creature pen holds four, turned
S/E/N/W, two male + two female (builder change, owner: *"You should put many creatures in each pen so they will have
different facings to study."*). Body texPaths of Gizka, Orray, Fire-hawk, Ashwallow, Emberscythe, Dalgo, Fire-wasp,
Ullai resolve to our packs; the deployed PNGs (incl. GizkaW_*, AshwallowDome_*) are byte-in-sync with HEAD.

**Open:**
- The test companion profile had expired (expiresUtc was 20:00Z, i.e. in the past in UTC); renewed to
  2026-10-16T09:00Z. Before that, burned-cell probes and safe_advance were refused.
- Four furnace-beasts warm their pen to ~23 C in 300 ticks (it caps at 24 C); the builder now re-chills both pens
  to 10 C after measuring, so the save starts cold.
- order_pawn reports the 3 colonists not all standing on the shelter cell (pre-existing note; they are in the shelter).
- GizkaW (the 80% alternate graphic) cannot be told apart by thing_explain; its files are deployed.
- Young/adult variety was not added (no per-life-stage selector in the builder yet).
