#!/usr/bin/env python3
# selftest-timeout: 120
"""RIMMANDRAKE_RESTORE_KILLED_MUTANTS_SIGKILL_SKIPS_FINALLY: a mutation run killed mid-mutation (run_selftests' timeout is
SIGKILL, so run_mutations' `finally` never runs) must not leave its mutant in the production kernel for good. The next
run_mutations call restores it from the journal, and never clobbers a file someone edited after the kill.

  1 a SIGKILLed run leaves the kernel mutated (the defect's precondition: proves the instrument sees it)
  2 the next run_mutations restores it byte-identical before doing anything else
  3 a file edited after the kill (neither original nor the mutant) is left alone, its stale entry dropped
  4 a clean run leaves no journal entry behind

    python3 src/RimMandrake/Utils/selftest_mutation_journal.py
"""
import os
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mutate_explosivegrowth_fuzz as engine  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        FAILS.append(name)


def killed_run(kernel, wrapper):
    """Start run_mutations in its own process group, wait until the kernel reads mutated, SIGKILL the group."""
    code = ("import sys; sys.path.insert(0, %r); import mutate_explosivegrowth_fuzz as m; "
            "m.run_mutations(%r, %r, [('swap', 'ORIGINAL', 'MUTANT')])" % (HERE, kernel, wrapper))
    p = subprocess.Popen([sys.executable, "-c", code], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 30
    while time.time() < deadline and b"MUTANT" not in open(kernel, "rb").read():
        time.sleep(0.1)
    os.killpg(p.pid, signal.SIGKILL)
    p.wait()


def main():
    d = tempfile.mkdtemp(prefix="mutation_journal_")
    kernel = os.path.join(d, "Kernel.cs")
    wrapper = os.path.join(d, "slow_wrapper.py")
    open(wrapper, "w").write("import time\ntime.sleep(60)\n")
    orig = b"// a kernel\r\nreturn ORIGINAL;\r\n"

    open(kernel, "wb").write(orig)
    killed_run(kernel, wrapper)
    check("1 a SIGKILLed run leaves the kernel mutated", b"MUTANT" in open(kernel, "rb").read(), open(kernel, "rb").read())
    engine.run_mutations(kernel, wrapper, [])
    check("2 the next run restores it byte-identical", open(kernel, "rb").read() == orig, open(kernel, "rb").read())

    open(kernel, "wb").write(orig)
    killed_run(kernel, wrapper)
    edited = b"// someone's own edit after the kill\r\n"
    open(kernel, "wb").write(edited)
    engine.run_mutations(kernel, wrapper, [])
    check("3 a file edited after the kill is left alone", open(kernel, "rb").read() == edited, open(kernel, "rb").read())

    open(kernel, "wb").write(orig)
    engine.run_mutations(kernel, wrapper, [])
    jdir = getattr(engine, "JOURNAL", None)
    left = [f for f in os.listdir(jdir) if f.endswith(".json")] if jdir and os.path.isdir(jdir) else []
    mine = [f for f in left if f == os.path.basename(engine._journal_path(kernel))] if hasattr(engine, "_journal_path") else ["no journal"]
    check("4 a clean run leaves no journal entry behind", not mine and jdir is not None, (jdir, mine))

    print("RESULT: %s (%d failure(s))" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
