# STEVE_HASHER_DIAGNOSE_WRONG_DIGESTS progress (skeleton)
1 read VERDICT + hasher.ps1: pending
2 read controller state: pending
3 experiment: pending
4 update nvme_replacement.md: pending
5 file on item, ledger, commit: pending
- read hasher.ps1 + hashtree.ps1: both reuse one $sha across files; .NET HashAlgorithm.ComputeHash(stream) does Initialize() only on success. An exception inside ComputeHash leaves state, poisoning next file. Hypothesis A to test (err->next-line wrong). Timeline: hash_src/dst ran 08:03-08:42 local on UNMASKED 20 CPUs (after a logged fault 07:10Z, cpu17; cpu18 hash_distinct 27); hasher.ps1 09:16-11:49 local on MASKED 18. Steve UTC-8. CPU 10900K, 4x32 GB 2666.
- retest state END_FAULT (over, mask 18 restored). Fault Watch task running watch2.ps1. rps.py in scratchpad.
- hashes2.err = 434 errors ALL ctor (before ComputeHash) => stale-$sha poisoning not triggered via logged errors. a1.py: wrong digests by era: hash_dst (unmasked) 3 proven, h2new (MASKED 18, .NET) 80 proven; python fresh 0 on all. So mask did NOT stop .NET errors. Small files too (630 KB DLL). Next: watch.log, WHEA, hash3.py; discriminator C# arm: SHA256Managed+Cng on same chunks.
- BIG: watch.log core check bad on moving CPUs in MASKED boot 17:35-19:05Z (hasher ran 17:16-19:49Z), clean since; unmasked boot bad 07:10-16:11Z. Bad = ~70% rounds in a 4 s pinned run, ref differs too. Not fixed cpu. Candidates: CPU vs RAM vs lane load. Mismatch field split next (a=int buffer, f=FP stack only, h=sha of buffer). Local copy of watch.log in scratchpad.
- mismatch split (last 400): FP-only 168 etc; FP uses stack only => not main RAM; core check wrong in int, FP, SHA. Hasher .NET era: 0 bad in first 128 GB, then 80 proven bad in 128-464 GB (interpolated clock 17:34-18:22Z), matches watch bad 17:35+. Lane jobs (RimWorld) on Steve 16:44-19:10Z; first job of 20-CPU boot 07:03Z, first bad cycle 07:10Z (3.3 h idle clean before). Bad stopped at last job end 19:05-10Z. All Python runs 20:10Z+ were outside any job and any bad cycle => "Python clean" is a window effect, not method. Hypothesis: fault active only while RimWorld runs. 07:10-16:11 bad w/o job: check if RimWorld lingered.
- experiment launched 21:4xZ on Steve: D:\ClaudeWork\backup\subset_check\diag\x.ps1 -> runs.tsv (arms ps_exact, dual [Managed+Cng same chunks], python; masks all/cpu2/cpu9/cpu16; 12 rounds; Idle class). Stop by creating diag\STOP. Lane idle. CPUs 18/19 unreachable without reboot (no reboot) => unmasked set cannot be run.
- also: stevecheck.exe crashed 19:05:01Z and RimWorld 19:09:08Z (Application log); powershell crashes 09:40,11:47,12:21Z in bad window. Application log check pending: crashes vs window.
- 9 hash_src/dst disagreements all within 14-40 GB of the lists (interpolated dst 16:07-16:14Z, watch last bad 16:11Z); remaining 97 GB same script clean => same .NET code clean once fault stops. App crash log: RimWorld c000001d 19:09Z, stevecheck coreclr 19:05Z, wide crashes on 10-31.
- RAM: earlier 85 GB mem test ran while cpu2 failing: bad=0 (PROGRESS.md). FP stack-only mismatches. So CPU-side not DRAM.
- Method draft: clone in clean window (lane paused, watch clean); verify on never-booted target BEFORE first boot; two separate reads; MATCH is proof (fault cannot forge equal digests); MISMATCH never final: re-hash/byte compare in clean window. Vendor verify not independent. Exclude C:\...\old_computer (owner order).
- robocopy 13:52-14:48Z ran INSIDE watch bad period (07:10-16:11Z): copy may be hit too; D: copy verified only by 100 random + hashes. Experiment at 21:43Z: 42 lines clean, one mask done. Finish ~22:14Z.
- Doc plan: verify with independent per-side SHA-256 (not memcmp: a fault can flip one compare; cannot forge a hash match). Matches survive fault windows; mismatches only re-tested. Boot clone only after verify.
- skills loaded; nvme step d repointed; verifying section still owed; waiting for run ending ~22:14Z; C: 903 GiB used; Samsung is disk 1 now, doc said 0
- verify_clone.py written, testing on Steve diag\vt; experiment 0 wrong of 240 digests (688 GB-equivalent, likely page-cached reads)
- nvme doc + VERDICT updated. NEXT: ledger note, close, publish
