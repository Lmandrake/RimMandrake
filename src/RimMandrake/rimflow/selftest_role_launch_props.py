#!/usr/bin/env python3
"""Property tests (Hypothesis) for role_launch's local-calendar helpers -- prev_day, slot_key, slot_epoch -- across DST.

The dispatcher keys every scheduled slot by local calendar day (review dispatcher-full #6/#7). Generated instants sit
within two days of a real DST transition in zones that shift at 02:00/03:00 (Berlin, Los Angeles, Sydney), at
MIDNIGHT (Santiago, Havana: the day's 00:xx does not exist) and by half an hour (Lord Howe), plus plain instants:
  D1 day_of(prev_day(now)) is exactly the calendar day before now's local day.
  D2 slot_key(day, slot) is "<day_of(day)> <slot>" for plain and weekday slots.
  D3 slot_epoch(now, slot) falls on now's local day; when the wall time exists it is exactly that wall time.
Expectations come from zoneinfo (datetime), the code under test from time.localtime/mktime with TZ set: two readers
of the same tzdata. Deterministic (derandomize, no example database). Needs hypothesis. MUTANTS_HUNT_ON_IDLE_STEVE.
"""
import datetime
import os
import sys
import time
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as R  # noqa: E402
try:
    from hypothesis import given, settings, strategies as st, HealthCheck  # noqa: E402
except ImportError:                    # pinned in infrastructure/stevedesktop/mutation_requirements.txt
    print("hypothesis is not installed: UNMEASURED, not a pass or a fail")
    sys.exit(0)

ZONES = ("Europe/Berlin", "America/Los_Angeles", "Australia/Sydney", "America/Santiago", "America/Havana",
         "Australia/Lord_Howe", "UTC")
SET = settings(max_examples=400, derandomize=True, database=None, deadline=None,
               suppress_health_check=[HealthCheck.too_slow])
FAILS = []
T0 = int(datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc).timestamp())
T1 = int(datetime.datetime(2028, 1, 1, tzinfo=datetime.timezone.utc).timestamp())


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def transitions(zone):
    z, out, prev = ZoneInfo(zone), [], None
    for t in range(T0, T1, 1800):
        off = datetime.datetime.fromtimestamp(t, z).utcoffset()
        if prev is not None and off != prev:
            out.append(t)
        prev = off
    return out


TRANS = {z: transitions(z) for z in ZONES}


def use(zone):
    os.environ["TZ"] = zone
    time.tzset()


def local(t, zone):
    return datetime.datetime.fromtimestamp(t, ZoneInfo(zone))


def exists(zone, d, h, m):
    """Does wall time d h:m exist (once or twice) in zone? fold round-trip through UTC."""
    z = ZoneInfo(zone)
    for fold in (0, 1):
        w = datetime.datetime(d.year, d.month, d.day, h, m, fold=fold, tzinfo=z)
        back = w.astimezone(datetime.timezone.utc).astimezone(z)
        if (back.date(), back.hour, back.minute) == (d, h, m):
            return True
    return False


@st.composite
def instant(draw):
    zone = draw(st.sampled_from(ZONES))
    tr = TRANS[zone]
    if tr and draw(st.integers(0, 4)):                 # mostly near a transition
        t = draw(st.sampled_from(tr)) + draw(st.integers(-2 * 86400, 2 * 86400))
    else:
        t = draw(st.integers(T0, T1))
    return zone, t


hhmm = st.tuples(st.sampled_from([0, 0, 0, 1, 1, 2, 2, 3, 3, 12, 23]) | st.integers(0, 23),
                 st.sampled_from([0, 30, 59]) | st.integers(0, 59))


@SET
@given(instant())
def d1(zt):
    zone, now = zt
    use(zone)
    want = local(now, zone).date() - datetime.timedelta(days=1)
    got = R.day_of(R.prev_day(now))
    assert got == want.isoformat(), (zone, now, local(now, zone).isoformat(), got, want.isoformat())


@SET
@given(instant(), hhmm, st.booleans())
def d2(zt, hm, weekly):
    zone, now = zt
    use(zone)
    slot = ("Wed " if weekly else "") + "%02d:%02d" % hm
    assert R.slot_key(now, slot) == "%s %s" % (local(now, zone).date().isoformat(), slot), (zone, now, slot)


@SET
@given(instant(), hhmm)
def d3(zt, hm):
    zone, now = zt
    use(zone)
    h, m = hm
    d = local(now, zone).date()
    t = R.slot_epoch(now, "%02d:%02d" % (h, m))
    lt = local(t, zone)
    assert lt.date() == d, ("off the day", zone, d.isoformat(), "%02d:%02d" % (h, m), lt.isoformat())
    if exists(zone, d, h, m):
        assert (lt.hour, lt.minute) == (h, m), ("wrong wall time", zone, d.isoformat(), h, m, lt.isoformat())


def run(fn, label):
    try:
        fn()
        check(True, label)
    except AssertionError as e:
        check(False, "%s -- falsified: %s" % (label, str(e)[:400]))


def main():
    old = os.environ.get("TZ")
    try:
        check(all(len(TRANS[z]) >= 4 for z in ZONES if z != "UTC"),
              "probe: tzdata shows >= 4 transitions 2025-2027 in every DST zone: %s"
              % {z: len(v) for z, v in TRANS.items()})
        run(d1, "D1 prev_day lands on the calendar day before, across DST (incl. midnight shifts)")
        run(d2, "D2 slot_key is '<local day> <slot>' for plain and weekday slots")
        run(d3, "D3 slot_epoch stays on now's local day and keeps any wall time that exists")
    finally:
        if old is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old
        time.tzset()
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
