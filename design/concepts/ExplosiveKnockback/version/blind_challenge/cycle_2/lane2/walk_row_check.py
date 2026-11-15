#!/usr/bin/env python3
"""Blind cycle 2, fix RIMMANDRAKE_CORRECT_FLYING_OFF_WALK_ROW_TO_ITS_BAR: the walk row for flyingGoods off follows the
locked bar settings_scale_and_switch (goods in the air off = loose goods are not thrown at all, never the old hop).
rc 0 when every carrier of the row says so; rc 1 naming each file that still carries the stale row or lacks the new one.
    python3 walk_row_check.py [--repo <checkout>]"""
import argparse, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser(); ap.add_argument("--repo", default=os.path.abspath(os.path.join(HERE, *[".."] * 7)))
R = ap.parse_args().repo
STALE, NEW = "off_is_the_instant_move", "off_goods_unthrown"
FILES = ["src/RimMandrake/ExplosiveKnockback/validation.py", "design/concepts/ExplosiveKnockback/version/bar_lists_map.json",
         "design/validation_walks/RimMandrake/ExplosiveKnockback.md", "src/RimMandrake/Utils/modcheck/required_checks.json"]
bad = []
for f in FILES:
    try:
        t = open(os.path.join(R, f), encoding="utf-8").read()
    except OSError as e:
        bad.append("%s unreadable (%s)" % (f, e.strerror)); continue
    if STALE in t:
        bad.append("%s still carries %s" % (f, STALE))
    if NEW not in t:
        bad.append("%s lacks %s" % (f, NEW))
v = open(os.path.join(R, FILES[0]), encoding="utf-8").read()
if not re.search(r'\("goods_fly_off",\s*"flying_goods",\s*"%s"' % NEW, v):
    bad.append("validation.py: scene goods_fly_off does not map to flying_goods.%s" % NEW)
m = json.load(open(os.path.join(R, FILES[1]), encoding="utf-8"))
if ("flying_goods." + NEW) not in json.dumps(m):
    bad.append("bar_lists_map.json: no row slug flying_goods.%s" % NEW)
p = open(os.path.join(R, "src/RimMandrake/ExplosiveKnockback/Source/RM_KnockbackProof.cs"), encoding="utf-8").read()
i = p.find('case "goods_fly_off":')
if i < 0 or "flying_off" not in p[i:i + 3000]:
    bad.append("RM_KnockbackProof.cs: scene goods_fly_off does not expect skip flying_off")
print("walk row follows its bar: %s" % ("PASS" if not bad else "FAIL -- " + "; ".join(bad)))
sys.exit(1 if bad else 0)
