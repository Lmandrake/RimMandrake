"""Offline selftest for prove_stillsand_content.py (STILLSAND_CONTENT_LIVE_PROOF_1): its live judges over the scripted
fake (selftest_stillsand.Fake plus jawa/running_mods) and its offline judges over can-fail probes. The offline clauses
themselves read the repo and are the item's proof, not this test: O1 is red until the Vaalok south is redrawn."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.exit(subprocess.call([sys.executable, os.path.join(HERE, "prove_stillsand_content.py"), "--selftest"]))
