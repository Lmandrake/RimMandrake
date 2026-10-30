"""Tester baseline for critic calibration: ralph_a's TESTER.md pass through the calib Critic interface
(CRITIC_CALIB_MEASURE_AGAINST_TESTER_BASELINE). Same sandbox, model, timeout and budget as L4OpusCritic; only the
prompt and the verdict parsing differ. Load it as `--critic arena_critic_tester:RalphATester`.

Copied from the scratch plug-in that made run tester-ralpha-baseline (ClaudeWork, 2026-10-30) with ONE change: the
whole answer is kept in meta["answer"] (it kept only an 800-char reason and a 1500-char tail, so a finding listed
early was invisible to the blind reason matcher of arena_critic_mutants and the tester was scored on a truncated
write-up while L4 was scored on its full reasons). That change gives it a new critic_fingerprint, so runs of the old
copy (tester-ralpha-baseline) are not reusable as seeds; arena_critic_mutants runs it fresh on every candidate.
Editing the class again changes the fingerprint again."""
import json, os, re, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import arena_critic_calib as C  # noqa: E402

TESTER_MD = (Path(__file__).resolve().parent / "ralph_a" / "TESTER.md").read_text()


def tester_prompt(c):
    spec = {"criteria": c.criteria, "prompt": c.prompt}
    plan = ("Acceptance criteria:\n%s\n\nProof command (run it yourself):\nNone\n\nAlso run "
            "`python3 src/RimMandrake/Utils/run_selftests.py --only <selftest>` for every selftest the diff adds or "
            "changes, then try to break the change: inputs the criteria name but the tests do not, error paths, "
            "boundary values, anything the diff claims without a test.\n" % c.criteria)
    return (TESTER_MD + "\n## FROZEN SPEC\n" + json.dumps(spec, indent=1, sort_keys=True) + "\n\n## TEST PLAN\n"
            + plan + "\n## DIFF\n" + c.diff + "\n")


class RalphATester(C.L4OpusCritic):
    name = "ralpha-tester"

    def review(self, c):
        import shutil
        home = c.work / "home"
        (home / ".claude").mkdir(parents=True, exist_ok=True)
        cred = Path.home() / ".claude" / ".credentials.json"
        if cred.exists():
            shutil.copy2(cred, home / ".claude" / ".credentials.json")
        if len(c.diff) > C.INLINE_DIFF_MAX:
            (c.work / "change.diff").write_text(c.diff)
            c = C.CriticInput(c.cid, c.prompt, c.criteria, "(%d lines, too long to inline: it is in the file "
                              "../change.diff relative to your current directory; read it in parts)"
                              % c.diff.count("\n"), c.tree, c.work)
        prompt = tester_prompt(c)
        argv = self.exe + ["-p", "--model", self.model, "--output-format", "json",
                           "--tools", "Bash,Read,Grep,Glob,Write,Edit", "--dangerously-skip-permissions",
                           "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence",
                           "--max-budget-usd", str(self.max_usd)]
        env = {"PATH": "/usr/local/bin:/usr/bin:/bin:" + str(Path.home() / ".local" / "bin"), "HOME": str(home),
               "LANG": "C.UTF-8", "USER": os.environ.get("USER", "u"), "TERM": "dumb"}
        t0 = time.time()
        timeout = self.timeout
        if self.deadline is not None:
            timeout = min(timeout, self.deadline - t0)
            if timeout < C.MIN_CALL_S:
                return C.CriticVerdict("invalid", ["skipped: budget spent"], {"skipped": True})
        proc = subprocess.Popen(C.sandbox_argv(argv, c.work, c.tree), cwd="/", stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, start_new_session=True)
        try:
            out, err = proc.communicate(prompt.encode("utf-8"), timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            out, err = proc.communicate()
            rc = 124
        meta = {"rc": rc, "wall_s": round(time.time() - t0, 1), "model_arg": self.model}
        if rc == 124 and timeout < self.timeout:
            meta["budget_cut"] = True
        try:
            d = json.loads(out.decode("utf-8", "replace"))
        except ValueError:
            meta["stderr_tail"] = err.decode("utf-8", "replace")[-400:]
            return C.CriticVerdict("invalid", ["no JSON envelope (rc %d)" % rc], meta)
        meta.update({"cost_usd": d.get("total_cost_usd"), "turns": d.get("num_turns"), "is_error": d.get("is_error")})
        if rc != 0 or d.get("is_error"):
            return C.CriticVerdict("invalid", ["claude error: %s" % str(d.get("result"))[:300]], meta)
        res = (d.get("result") or "").rstrip()
        meta["answer_tail"] = res[-1500:]
        meta["answer"] = res
        m = re.search(r"VERDICT:\s*(PASS|FAIL)\s*\**\s*$", res)
        if not m:
            return C.CriticVerdict("invalid", ["no VERDICT line"], meta)
        return C.CriticVerdict("accept" if m.group(1) == "PASS" else "reject", [res[-800:]], meta)
