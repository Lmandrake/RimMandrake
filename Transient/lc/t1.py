import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    print(type(s.tools), list(s.tools)[:2] if not isinstance(s.tools,dict) else list(s.tools.items())[:1])
    names=list(s.tools)
    print([n for n in names if any(k in n for k in ("spawn","tick","quest","incident","settings","mote","fleck","count","census","state","probe","read","eval","lua","script","def"))])
    for n in ("jawa/get_def","jawa/get_defs","rimworld/step_game_ticks","jawa/mod_settings_field","jawa/comp_read"):
        if n in s.tools: pj(s.tools[n] if isinstance(s.tools,dict) else n)
