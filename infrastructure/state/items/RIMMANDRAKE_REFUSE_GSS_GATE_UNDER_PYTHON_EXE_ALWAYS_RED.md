## spec
found-by: BENCH detached helper on RIMMANDRAKE_PROVE_GSS_SWITCHBOARD_DENSE, 2026-11-12, SteveDesktop.

**HARNESS.** `python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --live` (no --skip-offline) runs the offline gate
under Windows Python. O3_core_selftest then runs `sys.executable Utils/selftest_gimmesomeslack.py`, which dies at import:
`ModuleNotFoundError: No module named 'fcntl'` (winbuild -> a Unix-only lock), measured on Steve. O3 is therefore red on every
python.exe run and is charged as MOD. Every live line written that way was refused before going live: GSS_SWITCHES A2
(J20261112T153400Z-78ae04) and this item's A1 (J20261113T054742Z-eab648, J20261113T055523Z-782657). The two lines now pass
--skip-offline (71f90b1e96). The trap stays for the next line author.

Fix: under win32, proof_all's gate refuses as HARNESS ("run the offline gate under WSL python3") instead of a MOD O3 FAIL, or it
runs the gate through wsl.exe python3.

Also seen on Steve under WSL python3 (same day): the C# SelfTest's slice bound failed (a planned E=248 build held 50.6 ms against
a 30 ms bound) and then an AccessViolationException. That is Steve's advisory fault window; it was not diagnosed (no hardware
diagnosis by ruling).

Acceptance test: on SteveDesktop, `cd ~/rm/runner && python.exe src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py --offline-gate`
reports O3 as HARNESS/UNMEASURED with the python3 hint (or PASS when run through WSL), never `O3_core_selftest FAIL MOD`. It
reported FAIL MOD at 8c2b474bf7 and at 4ff9d1df8b (the refused jobs above).
