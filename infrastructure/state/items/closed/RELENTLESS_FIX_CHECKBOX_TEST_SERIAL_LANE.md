# RELENTLESS_FIX_CHECKBOX_TEST_SERIAL_LANE

## spec

WP-02 leftovers. (a) selftest_relentless_checkbox (33 checks) is not in the run_selftests dotnet serial lane; add it there so it runs with the other dotnet-using tests, never in parallel. (b) The cv2 venv is host-only (~/.local/venvs/checkbox); provision it beyond this host (every clone/seat that runs the E5 toolchain check) via a scripted, idempotent installer.

Done when: run_selftests runs the checkbox test in the serial lane and a second host/clone passes E5 toolchain cv2 after the provisioning script.

Source: /mnt/d/ClaudeWork/rimmandrake/conductor/redesign_2026-11-06/stage4_log.md WP-02 line and FOLLOWUPS (cont.)
