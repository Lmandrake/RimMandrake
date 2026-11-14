"""Throwaway: apply the coverage judge's CORRECTION gaps (g1 g3 g5 g11 g12 g13) to Pyrelands test text.
Only scenes.json text, tree.json oracle_proposed/scenario (never experience or red), sheet.md and record.json prose."""
import sys
P = 'design/concepts/Pyrelands/'
PROBE = 'ash depth on the sand grid (ProbeAsh)'
E = {
 'scenes.json': [
  ('g1', 'counting loose ash and reading light each hour', 'reading ' + PROBE + ' and light each hour'),
  ('g1', '"blackened ruins on deep ash with loose ash in them"', '"blackened ruins on deep ash with ash lying in them (ProbeAsh over the ruin footprint: ashed cells above zero)"'),
  ('g1', '"a loose-ash patch laid and counted"', '"an ash patch laid on the sand grid and its depth read (ProbeAsh)"'),
  ('g1', 'loose ash falls under black rain', 'the ash patch\'s depth (ProbeAsh depthSum) falls under black rain'),
  ('g1', 'no loose-ash filth on the pad (asserted: count 0)', 'no ash on the pad (asserted: ProbeAsh ashed 0)'),
  ('g1', 'count RM_FE_Filth_LooseAsh on the pad', 'read ' + PROBE + ' on the pad'),
  ('g1', 'at least one loose-ash filth on the burned pad', 'ashed cells on the burned pad above zero (ProbeAsh)'),
  ('g1', 'no loose ash on the pad beyond what a pad left unburned beside it banks', 'no more ash depth on the pad (ProbeAsh) than a pad left unburned beside it banks'),
  ('g3', 'fertility about 140% watered and about 40% dry', 'fertility about 140% watered and about 70% dry'),
  ('g3', 'reads dry-ash fertility (about 40%)', 'reads dry-ash fertility (about 70%)'),
  ('g3', 'dry fresh scar about 90%', 'dry fresh scar about 120%'),
  ('g11', '"why": "he approved the art sheet; the floor\'s art and reads_as lines run on these scenes\' captures, and the biome text is read offline"',
          '"why": "the shipped art rests on his approval of the art sheet (OWNER:1792122659817386516, 2026-10-16); sc_three_skies\' captures carry the floor\'s art and reads_as lines for the skies only; sc_populations takes no capture and checks only that the shipped cast is the biome\'s own; the biome text is read offline"'),
 ],
 'tree.json': [
  ('g1', 'loose-ash count rises each hour of ash fall and light level drops; loose ash on the burned pad after the fire, none beyond ambient drift with ash-dusting off',
         PROBE + ' rises each hour of ash fall and light level drops; ash depth on the burned pad after the fire, none beyond ambient drift with ash-dusting off'),
  ('g1', 'count loose-ash filth and read the light level each hour', 'read ' + PROBE + ' and the light level each hour'),
  ('g1', 'footprint terrain is deep ash and loose-ash filth is present', 'footprint terrain is deep ash and ash lies on it (ProbeAsh ashed cells above zero)'),
  ('g1', 'fire count falls and loose ash washes away under black rain', 'fire count falls and ' + PROBE + ' falls under black rain'),
  ('g3', 'about 90% on the dry fresh scar', 'about 120% on the dry fresh scar'),
 ],
 'sheet.md': [
  ('g12', '- Furnace-beast herds no longer migrate across the world map: that leg was cut by your card on 2026-10-23; the description text still promising it is owed a fix\n', ''),
  ('g13', 'and showcase 3 is weathering the sky with a furnace-beast in a blackened ruin, as the most new ground after the burn line',
          'and showcase 3 is the sky and shelter: the three skies forced in turn over a fire pad and an ash patch, two closed rooms with and without a furnace-beast, the blackened ruins read where they stand, and furnace-beasts asleep on grass, as the most new ground after the burn line'),
  ('g5', 'stays as built and nothing checks it. It ships off, labelled unsupported, by your card 2026-11-13',
         'stays as built and is outside the promise; only its shipped default is checked (off, offline, by selftest_pyrelands_site.py). It ships off, labelled unsupported, by your card 2026-11-13'),
 ],
 'record.json': [
  ('g12', 'About.xml and the race description still promise it (owed: PYRELANDS_TEXT_FIX_ENGINEERED_NEVER_SAID)',
          'About.xml and the race descriptions no longer mention it (grep -i migrat over About, Defs, Languages and Patches finds only herdMigrationAllowed false and a patch comment, measured 2026-11-14); the absence is checked offline by T_CUT_STAYS_CUT (version/test_table.json, specified)'),
  ('g5', 'stays as built and is outside the promise: no leaf, no scene, no check.',
         'stays as built and is outside the promise: no leaf and no scene; only its shipped default (off, his card 2026-11-13) is checked, offline, by selftest_pyrelands_site.py.'),
  ('g1', '"src/RimMandrake/Pyrelands/Defs/ThingDefs_Ash/Filth_LooseAsh.xml",', '"src/RimMandrake/Pyrelands/Source/PyrelandsAshSand.cs",'),
 ],
}
bad = 0
for f, reps in E.items():
    s = open(P + f).read()
    for gid, a, b in reps:
        n = s.count(a)
        if n != 1:
            print('MISS', f, gid, n, a[:70]); bad += 1; continue
        s = s.replace(a, b)
    open(P + f, 'w').write(s)
print('applied with', bad, 'misses'); sys.exit(1 if bad else 0)
