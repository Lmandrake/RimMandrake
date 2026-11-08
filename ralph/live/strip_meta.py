#!/usr/bin/env python3
"""Make a COPY of an old player save loadable on the small list: rewrite only its <meta> mod lists to the mods active now, so the load
does not refuse it for missing mods. Things from the missing mods are then dropped by the game's own loader, with errors.

    python3 ralph/live/strip_meta.py gss_real_omega

Refuses any save whose name does not start with gss_real_ (the originals are never written).
"""
import os, re, sys

name = sys.argv[1]
assert name.startswith("gss_real_"), "only a gss_real_ copy"
ud = os.environ["RM_GAME_USERDATA"]
path = os.path.join(ud, "Saves", name + ".rws")
cfg = open(os.path.join(ud, "Config", "ModsConfig.xml"), encoding="utf-8").read()
active = re.findall(r"<li>([^<]+)</li>", cfg.split("<activeMods>")[1].split("</activeMods>")[0])
head_len = 200000
raw = open(path, "rb").read()
head = raw[:head_len].decode("utf-8", "replace")
meta_end = head.index("</meta>")
meta = head[:meta_end]


def block(tag, items):
    return "<%s>\n" % tag + "".join("\t\t\t<li>%s</li>\n" % i for i in items) + "\t\t</%s>" % tag


meta2 = re.sub(r"<modIds>.*?</modIds>", block("modIds", active), meta, flags=re.S)
meta2 = re.sub(r"<modSteamIds>.*?</modSteamIds>", block("modSteamIds", ["0"] * len(active)), meta2, flags=re.S)
meta2 = re.sub(r"<modNames>.*?</modNames>", block("modNames", active), meta2, flags=re.S)
out = meta2.encode("utf-8") + raw[len(meta.encode("utf-8")):]
open(path, "wb").write(out)
print("rewrote", name, "mods", len(active), "bytes", len(raw), "->", len(out))
