"""focus_heal.py - the stronger half of bringing RimWorld forward, and the loud failure when nothing works.

game_focus.focus_game() retries its gentle route (AttachThreadInput, then an Alt tap + AppActivate) a few times.
When a media window or browser keeps winning, it hands over to `heal()` here, which escalates:

    1. minimise_blocker       minimise whatever holds the foreground, then Alt tap + AppActivate RimWorld
    2. minimise_restore_game  minimise and restore RimWorld itself (Windows grants activation on restore)

each tried `rounds` times. If RimWorld is still not in front it raises FocusLost, carrying every attempt, which
live_queue's common.main turns into an UNMEASURED(FOCUS_LOST) record and exit code EXIT_FOCUS_LOST (3) -- a
distinct, greppable failure instead of rerun13's instant RuntimeError that read like any other abort.

Deliberately NOT a system_click: RimWorld runs borderless, so a click "on the game" lands on game UI (a cell, a
button), and the taskbar button's position is not knowable from here. Minimising the blocker is the strongest
move that cannot change the game. restore_focus() restores a minimised previous window (game_focus).

`escalate()` is pure control flow; selftest_belt_watchdog.py drives it with fakes.
"""
import sys
import time

EXIT_FOCUS_LOST = 3


class FocusLost(RuntimeError):
    """RimWorld would not come forward after every escalation. .attempts = [(method, title_after)]."""

    def __init__(self, msg, attempts=()):
        RuntimeError.__init__(self, msg)
        self.attempts = list(attempts)


def is_game(title):
    return "rimworld" in (title or "").lower()


_GET_RW = r'''
$p = Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $p) { "ERR|no RimWorldWin64 process"; exit }
$h = $p.MainWindowHandle
if ($h -eq 0) { "ERR|RimWorld has no main window handle"; exit }
'''
LADDER = [
    ("minimise_blocker", r'''
$fgH = [Fg]::GetForegroundWindow()
if ($fgH -ne $h -and $fgH -ne 0) { [void][Fg]::ShowWindow($fgH, 6) }
Start-Sleep -Milliseconds 300
$w = New-Object -ComObject WScript.Shell; $w.SendKeys('%'); Start-Sleep -Milliseconds 100
[void]$w.AppActivate($p.Id); [void][Fg]::SetForegroundWindow($h)
'''),
    ("minimise_restore_game", r'''
[void][Fg]::ShowWindow($h, 6); Start-Sleep -Milliseconds 400; [void][Fg]::ShowWindow($h, 9)
Start-Sleep -Milliseconds 200
$w = New-Object -ComObject WScript.Shell; $w.SendKeys('%'); [void]$w.AppActivate($p.Id)
[void][Fg]::SetForegroundWindow($h)
'''),
]


def escalate(steps, title_fn, rounds=2, sleep=time.sleep, pause_s=1.5, prior=()):
    """Run steps [(name, fn)] in order, `rounds` passes, until title_fn() names RimWorld.

    Returns the attempts list on success; raises FocusLost with every attempt (prior ones included) when nothing
    worked. A step raising RuntimeError is FATAL (no game process / no window): no retry can fix that.
    """
    attempts = list(prior)
    title = title_fn()
    if is_game(title):
        return attempts
    for r in range(rounds):
        for name, fn in steps:
            try:
                fn()
            except RuntimeError as e:
                attempts.append((name, "FATAL %s" % e))
                raise FocusLost("could not bring RimWorld forward: %s" % e, attempts)
            sleep(0.35)
            title = title_fn()
            attempts.append(("%s#%d" % (name, r + 1), title))
            if is_game(title):
                return attempts
        if r + 1 < rounds:
            sleep(pause_s)
    raise FocusLost(
        "FOCUS_LOST: could not bring RimWorld forward after %d attempts (%s); foreground is %r. Bridge calls that "
        "touch the game will time out until it is focused." % (len(attempts), ", ".join(a[0] for a in attempts),
                                                               title), attempts)


def heal(gentle_error, rounds=2):
    """Called by game_focus.focus_game after its gentle retries failed with `gentle_error`. Returns on success
    (RimWorld in front); raises FocusLost otherwise."""
    import game_focus

    def run(body):
        res = game_focus._ps(game_focus._PS_HELPER + _GET_RW + body)
        if res.startswith("ERR|"):
            raise RuntimeError(res[4:])

    if "no RimWorldWin64 process" in str(gentle_error) or "no main window" in str(gentle_error):
        raise FocusLost("FOCUS_LOST: %s" % gentle_error, [("gentle", "FATAL %s" % gentle_error)])
    steps = [(n, (lambda b=b: run(b))) for n, b in LADDER]
    attempts = escalate(steps, game_focus.foreground_title, rounds=rounds,
                        prior=[("gentle_retries", str(gentle_error)[:160])])
    print("focus_heal: RimWorld forward after %s" % " -> ".join(a[0] for a in attempts), file=sys.stderr)
    return attempts
