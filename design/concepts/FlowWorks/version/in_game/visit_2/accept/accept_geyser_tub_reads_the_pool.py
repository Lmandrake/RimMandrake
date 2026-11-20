#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_POINT_FLOWWORKS_GEYSER_CHECK_AT_VISIT_ONE_RUNNER (FlowWorks 0.1.0, visit 2).

sc_geyser_tub FAILed live because the test table's command runs the draft concept_scenes.scene_geyser_tub: it inspects
the SteamGeyser's own cell and waits for a 'HotSpring' need, which the mod never writes. Visit 1 built the real reads in
geyser_tub_live.py (after geyser_pit_scene.py stage): the pool cell's ProofPitLabel says "Hot tub", RM_HotPoolSoak and
RM_HotPoolAfterglow on an ordered soak. On the same build and map it read PASS 4 of 4 (evidence/exp/geyser_tub_live.json).

Passes when the check that decides sc_geyser_tub reads the pool, by either fix:
  (1) test_table.json's sc_geyser_tub runs geyser_tub_live.py (its command names it), or
  (2) concept_scenes._geyser_tub reads ProofPitLabel and RM_HotPoolSoak, and no 'HotSpring' need.
Red at the filing commit (the table runs the draft scene, and the draft reads 'HotSpring').
"""
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
NS = ROOT / 'src/RimMandrake/FlowWorks/northstar'
sys.path.insert(0, str(NS))


def main():
    table = json.loads((ROOT / 'design/concepts/FlowWorks/version/test_table.json').read_text(encoding='utf-8'))
    t = (table.get('tests') or {}).get('sc_geyser_tub') or {}
    via_table = 'geyser_tub_live.py' in str(t.get('command', '')) or str(t.get('file', '')).endswith('geyser_tub_live.py')
    import concept_scenes as C
    src = inspect.getsource(C._geyser_tub)
    via_scene = 'ProofPitLabel' in src and 'RM_HotPoolSoak' in src and 'HotSpring' not in src
    print('%s  (1) test table runs geyser_tub_live.py: %s (%s)' % ('ok  ' if via_table else '--  ', via_table,
                                                                    str(t.get('command'))[:120]))
    print('%s  (2) scene_geyser_tub reads the pool, no HotSpring need: %s' % ('ok  ' if via_scene else '--  ', via_scene))
    ok = via_table or via_scene
    print('accept_geyser_tub_reads_the_pool: %s' % ('ok' if ok else 'FAIL'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
