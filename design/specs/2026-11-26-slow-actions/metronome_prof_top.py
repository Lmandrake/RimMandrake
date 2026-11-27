#!/usr/bin/env python3
"""Top entries of each cProfile file named, for metronome_profile.md: by own time, and the ops_watch/collector
functions by cumulative time. python3 metronome_prof_top.py <prof>..."""
import pstats, sys
for p in sys.argv[1:]:
    s = pstats.Stats(p)
    print("=" * 20, p, "total %.2f s" % s.total_tt)
    rows = []
    for (f, ln, fn), (cc, nc, tt, ct, _) in s.stats.items():
        rows.append((tt, ct, nc, "%s:%d(%s)" % (f.split("/")[-1], ln, fn)))
    print(" own time:")
    for tt, ct, nc, n in sorted(rows, reverse=True)[:14]:
        print("   %7.2f s own %7.2f cum %9d calls  %s" % (tt, ct, nc, n))
    print(" cumulative (repo code):")
    for tt, ct, nc, n in sorted(((r[1], r[0], r[2], r[3]) for r in rows if (".py:" in r[3] and not r[3].startswith(("<", "subprocess", "selectors", "json", "decoder", "__init__", "threading", "pathlib", "os.py", "posixpath", "re", "_", "enum", "argparse", "encoder", "genericpath", "fnmatch", "datetime", "functools", "shutil", "tempfile", "codecs", "ast.py", "inspect", "typing"))) ), reverse=True)[:22]:
        print("   %7.2f s cum %7.2f own %9d calls  %s" % (tt, ct, nc, n))
