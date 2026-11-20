#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_REPIN_SOURCE_PAYS_FILM_IS_NOT_A_LEAK (FlowWorks 0.1.0, visit 2).

Live, sc_source_pays read SRC_flow_stops_when_empty FAIL: every pond square was under the wet line, yet the unlimited
sink still drew the film (evidence/exp/source_pays_long.json: 545.4 -> 548.35 L, 53 L left). His ruling
POND_PUMP_FIX_LAST_DROP_COUNTS ("ponds pump to last dL") says it must. So the row must judge "the drained total stops
once the pond's litres reach 0", never "the drained total stops once every square is under the wet line".

The fake is selftest_source_pays_scene.Fake with one change: below the wet line (0.05 notch a square) the sink draws the
film slowly, as the live game does. Cases:
  film_drains   the film drains slowly to 0 L, then the sink stops       -> the row reads PASS
  film_stuck    the sink stops with the film left (the old last-dL bug)  -> the row reads FAIL (never PASS)
  endless_pond  the pond never empties                                   -> the row reads FAIL (kept from the selftest)
Red at the filing commit (film_drains reads FAIL). Exit 0 only when all three hold.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
NS = ROOT / 'src/RimMandrake/FlowWorks/northstar'
sys.path.insert(0, str(NS))
import selftest_source_pays_scene as T  # noqa: E402

FILM = 0.05        # notch a square: the scene's wet line (max filled dl / (core levels x 10)) in the fake's units
FILM_RATE = 0.03   # notch a pulse the sink draws once the reached squares are under the wet line


class FilmFake(T.Fake):
    def one_pulse(self):
        if self.fault not in ('film_drains', 'film_stuck'):
            return T.Fake.one_pulse(self)
        for (sx, sz), s in self.sinks.items():
            reach = [q for q in ((sx, sz), (sx + 1, sz), (sx - 1, sz), (sx, sz + 1), (sx, sz - 1)) if q in self.dug]
            for q in reach:
                comp = next(c for c in self.comps() if q in c)
                vol = sum(self.water.get(p, 0.0) for p in comp)
                above = vol - sum(max(0.0, -self.dug[q] + self.dug[p]) for p in comp)
                # what the comp holds above this square's floor when its surface sits at the wet line: the film
                reserve = sum(max(0.0, -self.dug[q] + FILM + self.dug[p]) for p in comp)
                if s['rate'] >= 0:
                    take = min(s['rate'], max(0.0, above))
                elif vol > reserve + 1e-9:
                    take = min(100.0, vol - reserve)        # fast down to the wet line, as the healthy fake
                else:
                    take = min(0.0 if self.fault == 'film_stuck' else FILM_RATE, max(0.0, above))
                if take < 1e-9:
                    continue
                h = self.surface(comp, vol - take)
                for p in comp:
                    self.water[p] = max(0.0, h + self.dug[p])
                s['drained'] += take
        if self.weather == 'Rain':
            for q in self.dug:
                self.water[q] = min(self.dug[q], self.water.get(q, 0.0) + 0.1)
        self.level()


def row_of(C, sigs, fault):
    F = FilmFake(fault, False, sigs)
    out = C.scene_source_pays(F, lambda: None, lambda: None, {'calls': []})
    r = next((x for x in out['rows'] if x['id'] == 'SRC_flow_stops_when_empty'), None)
    return (r or {}).get('status'), (r or {}).get('detail', '')


def main():
    import concept_scenes as C
    sigs, _ = T.bridge_contract()
    want = {'film_drains': ('PASS',), 'film_stuck': ('FAIL',), 'endless_pond': ('FAIL',)}
    bad = []
    for fault, ok in want.items():
        got, detail = row_of(C, sigs, fault)
        print('%s  %-13s SRC_flow_stops_when_empty %-10s (want %s) %s' % (
            'ok  ' if got in ok else 'FAIL', fault, got, '/'.join(ok), str(detail)[:160]))
        if got not in ok:
            bad.append(fault)
    print('accept_source_pays_last_decilitre: %s' % ('FAIL %s' % bad if bad else 'ok'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
