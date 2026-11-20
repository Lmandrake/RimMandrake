#!/usr/bin/env python3
"""Write ../MANIFEST.md: per package file its source, time range, row count, sha256, what it is, and what GPT saw.
Run: python3 -I make_manifest.py <package dir>."""
import hashlib, re, sys
from pathlib import Path

PKG = Path(sys.argv[1])
CALL1 = set("""gpt/call1_facts_neutral.md digest/chk_mismatch_analysis.md digest/watch_per_boot.tsv digest/watch_era_sensors.txt
digest/watch_per_cpu_by_era.tsv digest/watch_per_hour.tsv digest/soak_digest.md digest/winevents_digest.md
digest/winevents_app_crashes.tsv digest/testq_outcome_vs_window.txt digest/uefi_cpu_settings_20261120.txt
digest/ops_watch_steve_daily.tsv raw/fault_monitor_report.txt raw/fault_monitor_heat.txt findings/steve_diag/Program.cs
raw/tools_steve_cpu_retest/watch2.ps1 raw/tools_steve_cpu_retest/steve_cpu_soak.ps1 raw/tools_steve_cpu_retest/stevetemp.cs
raw/steve_logs/sweep.log raw/steve_logs/s4.log raw/steve_logs/s4-chk.log raw/steve_logs/chk.log digest/watch_bad_rows.log""".split())
CALL2 = set("""findings/steve_fault_diagnosis.md findings/item_STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO.txt
findings/item_RIMMANDRAKE_COUNT_STEVE_FAULTS_AFTER_VOLTAGE_RAISE_TO_CEILING.txt
findings/item_RIMMANDRAKE_READ_STEVE_SOAK_AT_24H_72H_REBOOT_PROVEN.txt findings/item_STEVEDESKTOP_DIAGNOSE_CPU18_FLUNKS_MATH.txt
findings/item_STEVE_HASHER_DIAGNOSE_WRONG_DIGESTS.txt findings/vcore_visit/BIOS_VISIT_STEPS.md findings/vcore_visit/BEFORE_STATE.md
gpt/call1_facts_neutral.md digest/chk_mismatch_analysis.md digest/watch_per_boot.tsv digest/watch_era_sensors.txt
digest/watch_per_cpu_by_era.tsv digest/soak_digest.md digest/winevents_digest.md digest/testq_outcome_vs_window.txt
digest/uefi_cpu_settings_20261120.txt raw/fault_monitor_report.txt findings/steve_diag/Program.cs""".split())
D = "D:\\ClaudeWork\\rimmandrake"
SRC = [  # (path prefix, source, what it is)
    ("raw/steve_logs/watch.log", r"SteveDesktop C:\SteveDesktop\diag\logs\watch.log (scp 2026-11-20 07:53Z)",
     "the 5-minute per-CPU watch: WATCH START, CONTROL and one CYCLE line per 300 s with bad CPUs, exit codes, heat and vcore"),
    ("raw/steve_logs/watch-chk.log", r"SteveDesktop C:\SteveDesktop\diag\logs\watch-chk.log",
     "the checker's per-run lines (CORE ... bad=) and first-5 MISMATCH want/got per run; times HH:MM:SS only"),
    ("raw/steve_logs/watch-ctl.log", r"SteveDesktop C:\SteveDesktop\diag\logs\watch-ctl.log", "the watch's CONTROL runs (injected fault)"),
    ("raw/steve_logs/", r"SteveDesktop C:\SteveDesktop\diag\logs\ (2026-10-31 per-CPU sweep and RAM walks)",
     "2026-10-31 remote hardware tests: Prime95 pinned, stevecheck, sha256, RAM walk logs"),
    ("raw/steve_soak/soak.log", r"SteveDesktop C:\SteveDesktop\diag\soak\soak.log", "the Prime95 soak step log (6 h run 11-17 and 72 h run from 11-18)"),
    ("raw/steve_soak/", r"SteveDesktop C:\SteveDesktop\diag\soak\ and " + D + r"\steve_diag\soak\\", "soak scripts, state and proof"),
    ("raw/winevents/", r"SteveDesktop Get-WinEvent query 2026-11-20 07:5xZ (scripts/evq_steve.ps1)",
     "Windows System + Application events since 2026-10-20: WHEA, Kernel-Power 41, BugCheck 1001, 6005/6006/6008/6009, 12/13, Application 1000/1001/1002/1026"),
    ("raw/uefi/", r"SteveDesktop UEFI variables via GetFirmwareEnvironmentVariableExW (read3.ps1), 2026-11-20",
     "firmware setup variables (raw base64) and their decode with the BIOS 3401 IFR"),
    ("raw/fault_snapshots/", D + r"\testq\fault_snapshots\\", "per-window snapshots the fault monitor took at onset"),
    ("raw/fault_windows.json", D + r"\testq\fault_windows.json", "the fault monitor's window table"),
    ("raw/fault_", D + r"\testq\\", "fault monitor state/heat/advisory files"),
    ("raw/paused.json", D + r"\testq\paused.json", "the testq lane pause record"),
    ("raw/fault_monitor_report.txt", "python3 src/RimMandrake/Utils/testq/fault_monitor.py report, 2026-11-20", "every fault window with onset, CPUs, jobs inside, heat"),
    ("raw/fault_monitor_heat.txt", "python3 src/RimMandrake/Utils/testq/fault_monitor.py heat, 2026-11-20", "per-boot temperature/vcore table"),
    ("raw/soak_read_output.txt", "python3 src/RimMandrake/Utils/steve_cpu_retest/soak_read.py, 2026-11-20 07:53Z", "the soak reader's verdict"),
    ("raw/ops_watch_steve.jsonl", D + r"\ops_watch\series\steve.jsonl", "the ops watch steve series (fault minutes, INVALID counts, jobs, seats)"),
    ("raw/archmagi_mirror_fault_watch.log", D + r"\testq\fault_watch.log", "Archmagi's mirror of watch.log (read by fault_monitor.py)"),
    ("raw/tools_steve_cpu_retest/", "repo src/RimMandrake/Utils/steve_cpu_retest/ and testq/fault_monitor.py", "the instruments' source"),
    ("findings/steve_diag/", D + r"\steve_diag\\", "diagnosis notes, the checker source Program.cs, driver A/B records, BIOS flash notes"),
    ("findings/vcore_visit/", D + r"\steve_diag\hw_20261115\\", "the voltage-raise visit: before-state, BIOS steps, probes, firmware/power readings"),
    ("findings/conductor/", D + r"\conductor\\", "the Conductor's 2026-11-17 retest, sweep and soak reports"),
    ("findings/item_", "python3 src/RimMandrake/rimflow/cli.py show <ID>, 2026-11-20", "ledger history of one item (notes are cut at display width; full text in ledger_steve_fault_events.md)"),
    ("findings/ledger_steve_fault_events", "repo infrastructure/state/ledger/events/*.jsonl, filtered", "every ledger event on a SteveDesktop item that mentions fault/CPU/soak/heat/crash terms, full text"),
    ("findings/", "repo infrastructure/state/ (facts, evidence, lessons, items/closed) and design/RimMandrake/ops_diagnoses/", "findings documents"),
    ("digest/", "scripts/make_digests.py and the analysis in REPORT.md", "faithful digests of the raw streams"),
    ("gpt/", "this run", "GPT prompts, answers and event streams"),
    ("scripts/", "this run", "the scripts that made the digests and the FP-lane model"),
]
TS = re.compile(r"(20\d\d-\d\d-\d\d[ T]\d\d:\d\d(?::\d\d)?Z?)")


def meta(rel):
    for pre, src, what in SRC:
        if rel.startswith(pre):
            return src, what
    return "?", "?"


rows = []
for p in sorted(PKG.rglob("*")):
    if not p.is_file() or p.name == "MANIFEST.md":
        continue
    rel = p.relative_to(PKG).as_posix()
    b = p.read_bytes()
    sha = hashlib.sha256(b).hexdigest()
    text = b[:20_000_000].decode("utf-8", "replace") if not rel.endswith((".zip", ".exe", ".png", ".dll")) else ""
    n = text.count("\n") if text else "-"
    ts = TS.findall(text) if text else []
    rng = "%s .. %s" % (min(ts), max(ts)) if ts else "-"
    src, what = meta(rel)
    seen = ("call 1 + call 2 whole" if rel in CALL1 and rel in CALL2 else "call 1 whole" if rel in CALL1
            else "call 2 whole" if rel in CALL2 else "not sent")
    if rel in ("raw/steve_logs/watch.log",):
        seen = "not sent whole; as digest/watch_per_boot.tsv, watch_per_hour.tsv, watch_per_cpu_by_era.tsv, watch_bad_rows.log"
    elif rel == "raw/steve_logs/watch-chk.log":
        seen = "not sent; as digest/chk_mismatch_analysis.md"
    elif rel == "raw/steve_soak/soak.log":
        seen = "not sent whole; as digest/soak_digest.md"
    elif rel.startswith("raw/winevents/events"):
        seen = "not sent whole; as digest/winevents_digest.md + winevents_app_crashes.tsv"
    elif rel == "raw/ops_watch_steve.jsonl":
        seen = "not sent whole; as digest/ops_watch_steve_daily.tsv"
    elif rel.startswith("raw/uefi/"):
        seen = "not sent whole; as digest/uefi_cpu_settings_20261120.txt"
    rows.append((rel, len(b), n, rng, sha, src, what, seen))

with open(PKG / "MANIFEST.md", "w") as o:
    o.write("# Evidence package: SteveDesktop CPU fault, built 2026-11-20\n\n")
    o.write("Root: `D:\\ClaudeWork\\rimmandrake\\steve_cpu_report_20261119\\package\\`. Files under 5 MB are also committed in the repo at "
            "`infrastructure/state/facts/stevedesktop_cpu_fault_2026-11-19/package/`. Row count = newline count. Time range = the "
            "earliest and latest full timestamps found in the text (UTC unless the file says otherwise; '-' = none found). "
            "Secret scan 2026-11-20: no keys, tokens, passwords or account logins found (patterns: sk-, ghp_, xox, AKIA, PRIVATE KEY, "
            "password=, api_key=, token=, Bearer, refresh_token).\n\n")
    o.write("| file | bytes | rows | time range | sha256 | source | what it is | GPT saw |\n|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        o.write("| `%s` | %d | %s | %s | `%s` | %s | %s | %s |\n" % (r[0], r[1], r[2], r[3], r[4], r[5].replace("|", "/"), r[6], r[7]))
print(len(rows), "files")
