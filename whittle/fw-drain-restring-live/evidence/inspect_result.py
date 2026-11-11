"""Read-only extra observations from the untouched production aerial result."""
import json
from pathlib import Path
import sys


def inspect(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    assert data['script'] == 'validation_aerial.py' and data['mode'] == 'live' and not data.get('aborted')
    assert isinstance(data['started'], str) and 'T' in data['started']
    assert data['rows'] and all(r['status'] == 'PASS' for r in data['rows'])
    rows = {}
    for name in ('M15e_restring_is_a_colonist_job', 'M15f_restring_joined_run_one_look'):
        matches = [r for r in data['rows'] if r['id'] == name]
        assert len(matches) == 1 and matches[0]['class'] == 'MOD'
        rows[name] = matches[0]
    detail = rows['M15f_restring_joined_run_one_look']['detail']
    assert detail['jobDef'] == 'RM_RestringSpan' and detail['schema'] == 1
    assert detail['after'][0] == detail['after'][1] and detail['after'][0] in detail['before']
    assert detail['before'][0][0:2] == ['Modern', None]
    assert detail['before'][1][0] == 'Industrial'
    # Masts carry the four look styles. Modern colour variants belong to conduit definitions.
    assert detail['before'][0][2] == 'RM_AerialMast_Modern'
    assert detail['before'][1][2] == 'RM_AerialMast_Industrial'
    assert len(set(detail['splitNets'])) == len(set(detail['splitRuns'])) == 2
    assert len(set(detail['joinedNets'])) == len(set(detail['joinedRuns'])) == 1
    assert all(type(n) is int and n >= 0 for k in ('splitNets', 'splitRuns', 'joinedNets', 'joinedRuns') for n in detail[k])
    styles = [r['reply'] for r in detail['readings'] if r['cmd'] == 'cstyles']
    assert len(styles) == 3
    before, after = styles[1:]
    assert before['counters']['pending'] == after['counters']['pending'] == 0
    assert after['counters']['linkBridges'] > before['counters']['linkBridges']
    censuses = [r['reply'] for r in detail['readings'] if r['cmd'] == 'census']
    joined = censuses[-1]
    members = {m['id']: m for m in after['members']}
    anchors = [a for a in joined['anchors'] if a['net'] == detail['joinedNets'][0]]
    assert len(anchors) == 3
    for a in anchors:
        m = members[a['id']]
        assert m['run'] == detail['joinedRuns'][0]
        assert [m['look'], m['colour'], m['rawStyle']] == detail['after'][0]
    assert detail['job']['cut'] == 1
    for counter in ('jobsDone', 'spansRestrung'):
        assert detail['job'][counter] == detail['order'][counter]
        assert detail['completion'][counter] == detail['order'][counter] + 1
    assert detail['completion']['cut'] == 0 and detail['completion']['designated'] is False
    return dict(status='PASS', rows=len(data['rows']), split_nets=detail['splitNets'], joined_nets=detail['joinedNets'],
                split_runs=detail['splitRuns'], joined_runs=detail['joinedRuns'], before=detail['before'], after=detail['after'],
                job=detail['job'], completion=detail['completion'], all_joined_anchors=anchors,
                link_bridges=[before['counters']['linkBridges'], after['counters']['linkBridges']])


if __name__ == '__main__':
    print(json.dumps(inspect(sys.argv[1]), indent=2))
