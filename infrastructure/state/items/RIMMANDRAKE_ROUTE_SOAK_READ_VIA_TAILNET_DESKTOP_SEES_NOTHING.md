## spec

**Measured 2026-11-17 evening PST, from the Desktop (`mt-515497`).**

`soak_read.py` and `fault_monitor.py` both reach SteveDesktop as `ssh <STEVE_WIN>` with
`STEVE_WIN = os.environ.get("STEVE_WIN", "stevedesktop")` (`fault_monitor.py:52-53`). On the Desktop that bare name
**does not resolve** — there is no `~/.ssh/config` entry for it here (the documented hosts `stevedesktop`,
`stevedesktop-lan`, `stevedesktop-wsl` live in *Archmagi's* ssh config, per
`~/dev/Machinist/knowledge/remote-access-relayed.md:96-100`) — and the tailnet IP `100.118.241.96:22` times out,
because this machine's only tailnet route is inside the Colima container `tailscale-gmail`, not on the host.

So on the Desktop:

| probe | reading |
|---|---|
| `python3 src/RimMandrake/Utils/steve_cpu_retest/soak_read.py` | exit **3**, `SOAK UNREACHABLE: could not read SteveDesktop (ssh down or timed out); nothing is known about the soak` |
| `ssh stevedesktop` | `Could not resolve hostname stevedesktop` |
| `ssh 100.118.241.96` | `Operation timed out` |
| `docker exec tailscale-gmail tailscale ping stevedesktop` | **pong in 11 ms** |
| `docker exec tailscale-gmail tailscale ssh stevedesktop-wsl "hostname"` | **`SteveDesktop`** |

And through that working route, the soak the Desktop called unreachable was **running**: run
`S20261118T012929Z`, 72 h to `2026-11-21T01:29:29Z`, `started: true`, resumed after the 01:39:36Z reboot,
`fails: 0`, at pass 8 as of 03:31:48Z, one `prime95.exe` in `tasklist`, and its CONTROL line passing twice
(`inject_fatal_seen=1 inject_died_seen=1 heat_seen=1 load_seen=1 ok=1`).

🔑 **`soak_read.py` itself is NOT the defect and must not be "fixed" into optimism.** It did exactly the right
thing: it said UNREACHABLE and exited 3, distinct from a measured zero and from a fault. That honesty is why this
was findable at all. **The defect is the ROUTE**: the tools have no way to reach Steve from this machine, so a
correct "could not look" is the only answer they can ever give here — and a reader who takes two UNREACHABLE
readings in a row as evidence about the soak will be wrong, which is what happened (a handoff pointer recorded the
soak dead and owed the owner a restart, on the strength of the blind instrument plus a log read hours earlier).

**The fix.** Give both tools the Desktop's route: resolve the host through the container
(`docker exec tailscale-gmail tailscale ssh stevedesktop-wsl …`, reading `C:\SteveDesktop\…` as
`/mnt/c/SteveDesktop/…`) when direct ssh cannot resolve or connect, selected from a measurement, never a
hard-coded per-machine branch — `~/dev/Lodestar/bin/lodestar_host.py` names the host and the global rule says code
reads the environment rather than naming a machine. Keep the four answers apart: a route that worked and found the
soak stopped is a FAULT; a route that worked and found it running clean is a measured zero; no route at all stays
UNREACHABLE with the cause naming WHICH route failed and how. An UNREACHABLE must still never read as a pass.

Also owed, in the same change or named as a follow-up: a reader of two consecutive UNREACHABLE passes should say
"the instrument has been blind for N minutes", because that is a fault in the monitoring, not news about the CPU.

## refs

file: src/RimMandrake/Utils/steve_cpu_retest/soak_read.py
file: src/RimMandrake/Utils/testq/fault_monitor.py
file: infrastructure/stevedesktop/RUNBOOK.md

## verify

python3 src/RimMandrake/Utils/steve_cpu_retest/selftest_soak_read.py

## criteria

- A1: on the Desktop, `soak_read.py` returns a real reading of the live soak (run id, started, fails, last pass)
  rather than UNREACHABLE, while SteveDesktop is up.
- A2: with every route genuinely down, it still reads UNREACHABLE and exits non-zero, naming which routes were
  tried and how each failed.
- A3: no machine name, tailnet IP or container name is hard-wired in the tools; the route comes from a measurement
  or one config/env value, and a missing one fails loudly by name.
- A4: a soak found stopped is reported differently from a soak found running clean, and both differently from
  UNREACHABLE.

## acceptance

Acceptance test: new cases in `selftest_soak_read.py` with the transport injected (the file already replaces the
ssh layer for tests): one where direct ssh fails to resolve and the container route answers with a live-soak
fixture, asserting a real reading; one where both routes fail, asserting UNREACHABLE, a non-zero exit and both
causes named; one asserting the stopped / running-clean / unreachable verdicts are three distinct values. Watched
FAILING on the base commit, where the first case cannot pass because no second route exists. The live half is the
command in A1, recorded UNRUN until it runs on this machine with Steve up.
