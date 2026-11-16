# RIMMANDRAKE_STRIP_SCRUB_TEXT_WARDENS_CUT_BUT_STILL_SLEEPING

Filed by RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_MANY_BARS_LEFT (BENCH, 2026-11-16).

## spec
The bark-wardens (SHRUBLAND_TREE_GUARDIAN_1) were CUT 2026-10-23 (comment in `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Plants/RM_SweetlineTree.xml`), and the locked 0.1.0 bars `cuts` / `bark_wardens_removed` require no player text promising them. Two shipped texts still do: `src/RimMandrake/LeaningScrub/About/About.xml` (a whole paragraph: "Also the bark-wardens ... two or three sleep on every sweetline tree ... drop on whoever harvests") and the felt item's description in `src/RimMandrake/LeaningScrub/Defs/ThingDefs_Items/RM_SweetlineTree_Items.xml` ("... under the bark-wardens."). Found offline while writing `scene_cuts` (validation.py), which reads these texts live and will go red at Stage 6 on them. Remove the promise from both texts; change no mechanic.

## verify
Acceptance test (offline): `python3 -c "import re,glob,sys; L='src/RimMandrake/LeaningScrub'; pat=re.compile(r'\bguardians?\b|bark[- ]wardens?|farmer camps?|vaporator farmers|drying scar',re.I); hits=[p for p in glob.glob(L+'/Defs/*/*.xml')+[L+'/About/About.xml'] if any(pat.search(m) for m in re.findall(r'<description>(.*?)</description>', re.sub(r'<!--.*?-->','',open(p,encoding='utf-8').read(),flags=re.S), re.S)) and 'FactionDefs' not in p]; print(hits); sys.exit(1 if hits else 0)"` — exit 0, prints `[]`. Watched FAIL on base 7c2f206ece: exit 1 with About.xml and RM_SweetlineTree_Items.xml (RM_CombHolds.xml, the hidden save-only banned faction, is excluded, as scene_cuts excludes hidden defs). Then the selftest `python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub.py` stays green.

## criteria
Both texts no longer promise bark-wardens; the grep above exits 0; no def, comp or mechanic changes.
