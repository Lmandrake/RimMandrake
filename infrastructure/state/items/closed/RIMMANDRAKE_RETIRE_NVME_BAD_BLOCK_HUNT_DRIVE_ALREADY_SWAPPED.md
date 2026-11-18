## spec

The handoff pointer `STEVE_NVME_46000_EVENTS` asked for a drive-by-serial read of "~46,000 `bad block` events on
the Samsung 970 since 2026-10-30, SMART counters empty, Health=Healthy, still unexamined", backing up first. That
read was taken 2026-11-17 PST through the Colima tailscale route, and it retires the hunt. Evidence:
`Transient/steve_nvme_measured_20261117.txt` (pinned), landed at b7608ac8f754.

**Three measurements, each with its own probe so an empty answer could not be a query bug.**

1. **There is no Samsung in the machine.** `Get-Disk` by serial reads `KINGSTON SNV3S1000G`
   (`0000_…_0026_B768_7A27_5965.`, NVMe, Healthy, 1000204886016 = 1 TB) and `WDC WD141KFGX-68FH9N0` (`9RHGSAEL`,
   SATA, 14 TB). The ledger's own note *"1 TB drive ordered, due today"* is fitted. The pointer named a drive that
   is not there — exactly the check the independent hardware review asked for ("verify the disk identity by serial
   number").
2. **The 30328 events are ONE repeated message, not 30328 distinct blocks.** Grouped by message,
   every `disk`-provider event reads `The device, \Device\Harddisk1\DR1, has a bad block.` The review had already
   warned that "those events are also not necessarily 46,000 distinct bad blocks"; that is now measured, not
   assumed. (7 further events came from provider `cdrom`.)
3. **The flood is closed.** Over 30 days: 45674 System events, 30335 bad-block ones, newest
   `2026-11-01T17:25:38`, oldest `2026-10-31T06:49:16`. Over 7 days: **3473 System events, 0 bad-block events.**
   The non-zero 3473 is the probe that proves the 0 is a measured zero and not a blind instrument.

So the hunt as filed cannot proceed and need not: its subject left the machine, its count was a misreading of a
repeated message, and its symptom stopped sixteen days ago. **Close this item with that reading.** No backup is
owed, no vendor tool run is owed.

**What is NOT measured, and is deliberately left so:** the Kingston controller's own error log by serial (SMART
summary is not that; it needs a vendor tool for this drive). It is unnecessary while the count is zero. The one
thing that would reopen this is events RESUMING — and the honest version of that is an alarm, not a memory: if
`Harddisk1\DR1` bad-block events appear again, they belong to the Kingston and are a new finding about a new
drive, filed fresh, never a continuation of the Samsung's record.

🔑 For the fault analysis this pointer was entangled with: this removes the SSD from the CPU-fault candidate list
on measurement rather than on argument, which is the thing the second opinion said I had not earned
(`infrastructure/state/evidence/STEVE_CPU_SWAP_SECOND_OPINION_2026-11-17.md`: I "had not earned calling it
unrelated"). It does not change that review's split, because the drive it was reasoning about is gone.

## refs

file: Transient/steve_nvme_measured_20261117.txt
file: infrastructure/state/evidence/STEVE_CPU_SWAP_SECOND_OPINION_2026-11-17.md
file: infrastructure/state/lessons/20261118T033537Z-UNSEATED-46-000-nvme-bad-block-events.md

## verify

none (a reading already taken; the evidence file is the record)

## criteria

- A1: closed with the three measurements and their probes named in the close note.

## acceptance

Acceptance test: none, a measurement already taken and recorded; the drive identity, the message grouping and the
7-day zero are each in the pinned evidence file with the probe that makes the zero readable. A future resumption is
a new item about the Kingston, not a reopening of this one.
