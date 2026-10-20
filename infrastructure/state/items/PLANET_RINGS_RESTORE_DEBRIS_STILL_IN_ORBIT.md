# PLANET_RINGS_RESTORE_DEBRIS_STILL_IN_ORBIT

Owner (2026-10-20, AFK): *"I would also like to add back the Rings when we bring back the larger mod list."*
Facts: `design/RimMandrake/world_physics_audit_2026-10-20.md` §4. The Rings = RW - Planet Atmosphere
(`RWNodeTree.RWPlanetAtmosphere`, workshop 3272330410, dep Harmony only) + our ring settings + our
debris texture. Dropped in Wave 2 ("05 SAFE drop", `infrastructure/state/modlists/wave2_removed_118.txt`);
registry KEEP-TEMPORARILY-THEN-PHASE-OUT, owner C18: measure real memory first (`HEAVY_TEXTURES_MEASURE_REAL_VRAM`,
`PLANET_ATMOSPHERE_CLOUD_COST_1`). His 2026-10-20 words decide "add back"; the memory read rides the same load.

## Steps (when the larger list is next assembled; fold into that ONE cold load, never its own restart)
1. Pre-check, offline (no game needed):
   - `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3272330410\About\About.xml` packageId = `RWNodeTree.RWPlanetAtmosphere`.
   - `Config\Mod_3272330410_AtmosphereMod.xml` md5 = `deployed/config/Mod_3272330410_AtmosphereMod.TRUE-GLORIOUS-RING.xml` (ac1e8fa4);
     else copy that file over it (back up first). Must read `<ringMapPath>Ring/ring_debris</ringMapPath>`, `<ringFromTo>(14000000, 20000000)</ringFromTo>`.
   - `…\3272330410\Textures\Ring\ring_debris.png` md5 = `deployed/atmosphere_ring/ring_debris.png` (df22cd50); else copy it in
     (Steam updates wipe hand-added workshop files; the empty-path fallback is a flat grey disk that cuts the planet).
2. Add `rwnodetree.rwplanetatmosphere` to the larger list (FULL.LATEST successor) right after `mandrake.rut.empirepursuit`
   (its slot on every pre-Wave-2 full list), record the why (the owner's words above) in the list's wave notes;
   do the same in the SHIP list only if he says the Rings ship.
3. Cold load. Player.log: zero errors naming `RW_PlanetAtmosphere`/`AtmosphereSettings`; record load time vs the previous load and
   resident memory with/without (C18 measurement).
4. Check it renders: world view at orbit zoom, `system_screenshot.py` frame showing the debris ring clear of the planet surface
   and its shadow; settings readback via `jawa/static_call` not needed — the picture is the check, then the owner looks.
## criteria
- ring visible in a world-view screenshot on the larger list, ring_debris texture (not grey disk), clear of the surface
- 0 Player.log errors from RW_PlanetAtmosphere; memory delta recorded
