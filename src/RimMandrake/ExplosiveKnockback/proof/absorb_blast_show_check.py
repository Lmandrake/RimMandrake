#!/usr/bin/env python3
"""The structural check of RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS grew into T_BLAST_SHOW_OFFLINE,
src/RimMandrake/ExplosiveKnockback/selftest_explosiveknockback_blast_show.py (2026-11-24). Its first form asked for two
switches, blastShow and blastShowBig, which the design of record replaced with one on/off per part
(design/specs/2026-11-24-knockback-blast-show/design.md §5). This file only runs that selftest.

    python3 src/RimMandrake/ExplosiveKnockback/proof/absorb_blast_show_check.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.exit(subprocess.call([sys.executable, os.path.join(HERE, "..", "selftest_explosiveknockback_blast_show.py")]))
