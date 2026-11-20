#!/usr/bin/env python3
"""Offline: pit_look_1114_live.py exits 0 all PASS, 1 any FAIL, 2 when nothing FAILed but a row could not look (or no row ran).
RIMMANDRAKE_SPLIT_PIT_LOOK_EXIT_UNMEASURED_READ_AS_FAIL: in visit 2 a run with 19 PASS, 0 FAIL, 1 UNMEASURED exited 1 and was recorded FAIL."""
import os
import re,sys
s=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pit_look_1114_live.py")).read()
m=re.search(r'bad = \[r for r in ROWS if r\[1\] is not True\][\s\S]*?sys\.exit\(([^\n]+)\)', s)
expr=m.group(1)
def code(rows):
    ROWS=rows; bad=[r for r in ROWS if r[1] is not True]
    return eval(expr)
cases={"all pass":([("a",True,"")],0),"one unmeasured":([("a",True,""),("b",None,"")],2),"one fail":([("a",False,""),("b",None,"")],1),"empty":([],2)}
bad=[k for k,(rows,want) in cases.items() if code(rows)!=want]
print("FAIL" if bad else "PASS", bad); sys.exit(1 if bad else 0)
