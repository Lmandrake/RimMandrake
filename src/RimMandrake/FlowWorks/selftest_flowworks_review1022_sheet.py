#!/usr/bin/env python3
"""Review 2026-10-22 (offline, no game) of RM_LiquidFire.cs, RM_SheetMath.cs, Sheet/RM_MapComponent_Sheet.cs and
Sheet/RM_SheetFire.cs. Each check reads FlowWorks source and fails on the pre-fix code; each carries a planted regression that
must fail (can-fail).

CHANNEL_LIGHTS_SPILL: the channel's flame is an RM_LiquidFlame, not a vanilla Fire, so the Fire.SpawnSetup hook never saw it:
  an ordinary fuel canal burning beside its own spill never lit it (only an inferno's halo fires did), although D5 says fire
  crosses both ways. RM_LiquidFire.Maintain now lights the burnable spill on each burning square's N/E/S/W neighbours.
SHEET_TO_CHANNEL_QUEUED: the sheet lit a channel square through IgniteNow (debug/bridge API), which forces a whole extra
  channel-fire Tick (every effect, rain douse roll and the detonation budget again) once per sheet check for every smothered or
  detonating channel square beside a burning spill. It now offers the square to the front (OfferLight, no forced Tick).
ANYWET_NEW_GAME: the static anyWet gate was only lowered in MapRemoved, which a game torn down by loading another save never
  calls, so a stale count kept the PathGrid postfix's gate open for the rest of the session. A new Game resets it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []


def check(name, ok, detail=""):
    print("  %-5s %s %s" % ("ok" if ok else "FAIL", name, detail if not ok else ""))
    if not ok:
        FAILS.append(name)


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


def channel_lights_spill(maintain):
    """True when Maintain, for each burning square still alight, offers its cardinal neighbours to the sheet."""
    return ("RM_MapComponent_Sheet.Of(map)" in maintain and "sheet.TryLight(c + GenAdj.CardinalDirections[d])" in maintain
            and maintain.index("sheet.TryLight(") > maintain.index("Extinguish(map, c, i, false);"))


def check_channel_lights_spill():
    fire = read("RM_LiquidFire.cs")
    m = body_of(fire, "private void Maintain(Map map, RM_MapComponent_Excavation ex, bool effects)")
    check("channel->spill: Maintain lights the spill beside a burning channel square", channel_lights_spill(m))
    check("channel->spill: gated on a wet sheet (no per-cell work on a dry map)",
          "bool lightSheet = sheet != null && sheet.WetCells > 0;" in m and "if (lightSheet)" in m)
    old = m.replace("sheet.TryLight(c + GenAdj.CardinalDirections[d]);", "")
    check("channel->spill: can-fail, the pre-fix Maintain lights no spill", not channel_lights_spill(old))


def sheet_queues(fire_tick):
    return "e.LiquidFire.OfferLight(map, e, n)" in fire_tick and "IgniteNow(" not in fire_tick


def check_sheet_to_channel():
    sf = read("Sheet/RM_SheetFire.cs")
    ft = body_of(sf, "private void FireTick()")
    check("spill->channel: the sheet offers the channel square to the front", sheet_queues(ft))
    fire = read("RM_LiquidFire.cs")
    ol = body_of(fire, "public bool OfferLight(Map map, RM_MapComponent_Excavation ex, IntVec3 c)")
    check("spill->channel: OfferLight queues and never forces a Tick",
          "TryQueue(map, ex, c, Find.TickManager.TicksGame, 0);" in ol and "Tick(" not in ol and "nextCheckTick" not in ol)
    check("spill->channel: OfferLight honours the canal-fire switch and needs burnable liquid",
          "canalFireEnabled" in ol and "BurnableFluidAt(map, ex, c) == null" in ol)
    old = ft.replace("e.LiquidFire.OfferLight(map, e, n)", "e.LiquidFire.IgniteNow(map, e, n)")
    check("spill->channel: can-fail, the pre-fix IgniteNow call is refused", not sheet_queues(old))


def resets_on_new_game(tick):
    i = tick.find("anyWetGame != Current.Game")
    j = tick.find("anyWet += w - countedWet;")
    return i >= 0 and j > i and "anyWet = 0;" in tick[i:j] and "anyWetGame = Current.Game;" in tick[i:j]


def check_anywet():
    s = read("Sheet/RM_MapComponent_Sheet.cs")
    tick = body_of(s, "public override void MapComponentTick()")
    check("anyWet: a new Game resets the gate before this map adds its count", resets_on_new_game(tick))
    check("anyWet: the owning Game is remembered", "private static Game anyWetGame;" in s)
    old = tick.replace("anyWet = 0;", "")
    check("anyWet: can-fail, no reset leaves the old game's count", not resets_on_new_game(old))


def main():
    print("selftest_flowworks_review1022_sheet")
    check_channel_lights_spill()
    check_sheet_to_channel()
    check_anywet()
    if FAILS:
        print("FAIL (%d): %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
