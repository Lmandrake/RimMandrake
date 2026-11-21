"""load_site.py <site> [logpath]: load a disposable test site (test_site_saves.load_site, e.g. calm) and write its verified read
to logpath (visit 3 helper; the log is what run_row.py --site-log reads). exit 0 verified, 2 not."""
import json
import os
import sys

U = os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6, "src", "RimMandrake", "Utils")
sys.path.insert(0, U)
sys.path.insert(0, os.path.join(U, "modcheck"))
import validation_core as V  # noqa: E402
import test_site_saves as T  # noqa: E402

B = V.Bridge()
loaded = T.load_site(B.call, sys.argv[1])
text = "site %s verified=%s %s" % (sys.argv[1], loaded.get("verified"), json.dumps(loaded, default=str)[:600])
print(text)
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8").write(text + "\n")
sys.exit(0 if loaded.get("verified") else 2)
