#!/usr/bin/env python3
"""Selftest of RIMMANDRAKE_FIX_DESIGNER_LAUNCH_ARGUMENT_LIST_TOO_LONG: a role run's prompt rides the unit's stdin
(StandardInput=file:), never the systemd-run argv. On 2026-11-27 the WreckedMachines Designer stage 3 packet reached
131,339 bytes (its record.json rendered at 78,876) and two launches died `OSError: [Errno 7] Argument list too long:
'systemd-run'`: Linux refuses any one argv string over MAX_ARG_STRLEN (131072 bytes).

Promise (design/specs/2026-11-27-role-launch-prompt-by-file/boundary.md):
  a-long-prompt-rides-stdin-never-argv
Pure: the real launch_argv and launch() with a fake runner; the shell layers (role-sync, role-pre-launch) are run for
real with a fake claude that writes what it reads on stdin."""
import os
import stat
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_dispatcher as SD  # noqa: E402  (its import sets the test state dirs)
import role_launch as RL  # noqa: E402
import form_fault as FF  # noqa: E402

FAILS = []
MAX_ARG_STRLEN = 131072     # the kernel's limit for one argv or environment string (PAGE_SIZE * 32)


def check(ok, msg):
    print("%s %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


def long_msg():
    """Over the limit, with distinct head and tail markers, so a cut or a lost part shows."""
    body = "".join("line %06d of the working record, with words in it\n" % i for i in range(4000))
    msg = "HEAD-MARKER\n" + body + "TAIL-MARKER"
    assert len(msg.encode()) > MAX_ARG_STRLEN + 50000
    return msg


def role(clone, **kw):
    return dict(RL.ROLE_DEFAULTS, name="Designer", seat="BENCH", model="opus", clone=clone, **kw)


def longest(argv):
    return max(len(a.encode()) for a in argv)


def stdin_file(argv):
    vals = [argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "-p" and argv[i + 1].startswith("StandardInput=")]
    return vals[0][len("StandardInput=file:"):] if vals and vals[0].startswith("StandardInput=file:") else None


def fake_claude(d):
    """A stand-in for claude_bounded.sh: writes its stdin to <d>/got.txt and its argv to <d>/argv.txt."""
    p = os.path.join(d, "fake_bounded.sh")
    with open(p, "w") as f:
        f.write('#!/bin/sh\ncat > "%s/got.txt"\nprintf "%%s\\n" "$@" > "%s/argv.txt"\n' % (d, d))
    os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR)
    return p


def run_unit_cmd(argv, d):
    """Run the unit's command (after "--") as systemd would: cwd the clone, stdin the StandardInput file."""
    cmd = argv[argv.index("--") + 1:]
    bounded = os.path.join(d, "src", "RimMandrake", "Utils", "claude_bounded.sh")
    cmd = [fake_claude(d) if x == bounded else x for x in cmd]
    src = stdin_file(argv)
    with open(src, "rb") if src else open(os.devnull, "rb") as fin:
        subprocess.run(cmd, cwd=d, stdin=fin, timeout=60, check=False)   # budget: danger=a hung fake holds the test
    try:
        return open(os.path.join(d, "got.txt"), encoding="utf-8").read()
    except OSError:
        return None


def t_launch_argv_by_file():
    d = os.path.join(SD.TMP, "c1")
    os.makedirs(d, exist_ok=True)
    msg = long_msg()
    pf = os.path.join(SD.TMP, "u1.prompt.md")
    argv = RL.launch_argv(role(d), "u1", msg, os.path.join(SD.TMP, "u1.json"), os.path.join(SD.TMP, "u1.err"),
                          "/usr/bin/claude", session="S", prompt_file=pf)
    check(longest(argv) <= MAX_ARG_STRLEN, "a-long-prompt-rides-stdin-never-argv: no argv string over the limit "
          "(longest %d bytes)" % longest(argv))
    check(not any("HEAD-MARKER" in a for a in argv), "the prompt is in no argv string")
    check(stdin_file(argv) == pf, "the unit reads its stdin from the prompt file")
    want = msg.rstrip() + "\n\n" + FF.BRIEF_LINE
    got = run_unit_cmd(argv, d)
    check(got == want, "the run receives the whole text, its repair line included (got %s bytes, want %d)"
          % (None if got is None else len(got.encode()), len(want.encode())))


def t_pre_steps_do_not_eat_stdin():
    """A pre-launch step runs before claude in the same unit; with the prompt on stdin, a step that reads stdin must
    not take it (each step's stdin is /dev/null, as it was before the prompt moved there)."""
    d = os.path.join(SD.TMP, "c2")
    os.makedirs(d, exist_ok=True)
    msg = long_msg()
    pf = os.path.join(SD.TMP, "u2.prompt.md")
    argv = RL.launch_argv(role(d, pre_launch=[["cat"], ["sh", "-c", "read x; true"]]), "u2", msg,
                          os.path.join(SD.TMP, "u2.json"), os.path.join(SD.TMP, "u2.err"), "/usr/bin/claude",
                          prompt_file=pf)
    got = run_unit_cmd(argv, d)
    check(got is not None and got.startswith("HEAD-MARKER") and "TAIL-MARKER" in got,
          "a pre-launch step that reads stdin leaves the whole prompt to claude")


def t_sync_step_does_not_eat_stdin():
    """A role's own clone runs `./sync` first in the same unit (role-sync); with the prompt on stdin, a sync that reads
    stdin must not take it. The layer is run for real: the test's dir is taken for a role clone, its ./sync reads
    stdin, and a pre-launch step sits between the two layers."""
    d = os.path.join(SD.TMP, "c6")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "sync"), "w") as f:
        f.write("#!/bin/sh\ncat > /dev/null\n")
    os.chmod(os.path.join(d, "sync"), 0o755)
    real = RL.role_clones.is_role_clone
    RL.role_clones.is_role_clone = lambda p: os.path.normpath(str(p)) == os.path.normpath(d)
    try:
        argv = RL.launch_argv(role(d, pre_launch=["true"]), "u6", long_msg(), os.path.join(SD.TMP, "u6.json"),
                              os.path.join(SD.TMP, "u6.err"), "/usr/bin/claude", prompt_file=os.path.join(SD.TMP,
                                                                                                         "u6.prompt.md"))
    finally:
        RL.role_clones.is_role_clone = real
    check("role-sync" in argv, "the role-sync layer is in the unit's command")
    got = run_unit_cmd(argv, d)
    check(got is not None and got.startswith("HEAD-MARKER") and "TAIL-MARKER" in got,
          "a role clone's ./sync that reads stdin leaves the whole prompt to claude")


def t_no_file_long_is_refused():
    """With no prompt file named, a message over the safe size is refused by name, never put on argv."""
    d = os.path.join(SD.TMP, "c3")
    try:
        RL.launch_argv(role(d), "u3", long_msg(), "/o", "/e", "/usr/bin/claude")
        check(False, "a long message with no prompt file is refused")
    except ValueError as e:
        check("prompt_file" in str(e), "a long message with no prompt file is refused, naming prompt_file: %s" % e)


def t_launch_writes_the_file():
    """launch() names the prompt file beside the run's out/err, writes it, and the unit reads it."""
    d = os.path.join(SD.TMP, "c4")
    os.makedirs(d, exist_ok=True)
    seen = []
    msg = long_msg()
    ok, out, rec = RL.launch(role(d), "rm-role-designer-9", msg, SD.TMP, "/usr/bin/claude",
                             runner=lambda argv, **k: seen.append(list(argv)) or subprocess.CompletedProcess([], 0, "", ""))
    argv = seen[0] if seen else []
    check(ok and argv, "launch started the fake unit: %s" % out)
    check(bool(argv) and longest(argv) <= MAX_ARG_STRLEN, "launch: no argv string over the limit (longest %s)"
          % (longest(argv) if argv else None))
    pf = stdin_file(argv) if argv else None
    check(pf == os.path.join(SD.TMP, "roles", "rm-role-designer-9.prompt.md"), "launch's prompt file sits beside the "
          "run's out and err: %s" % pf)
    got = open(pf, encoding="utf-8").read() if pf and os.path.exists(pf) else None
    check(got == msg.rstrip() + "\n\n" + FF.BRIEF_LINE, "launch wrote the whole text to the prompt file")


def t_codex_by_stdin():
    d = os.path.join(SD.TMP, "c5")
    os.makedirs(d, exist_ok=True)
    pf = os.path.join(SD.TMP, "u5.prompt.md")
    argv = RL.launch_argv(role(d, runner="codex"), "u5", long_msg(), os.path.join(SD.TMP, "u5.json"),
                          os.path.join(SD.TMP, "u5.err"), "/usr/bin/claude", prompt_file=pf)
    check(longest(argv) <= MAX_ARG_STRLEN and "--prompt" not in argv and stdin_file(argv) == pf,
          "a codex run reads the prompt on stdin too (agent_runner reads stdin when --prompt is absent)")


def t_a_long_prompt_rides_stdin_never_argv():
    for t in (t_launch_argv_by_file, t_pre_steps_do_not_eat_stdin, t_sync_step_does_not_eat_stdin,
              t_no_file_long_is_refused, t_launch_writes_the_file, t_codex_by_stdin):
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a raise on the parent is a FAIL, said
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))


def main():
    t_a_long_prompt_rides_stdin_never_argv()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
