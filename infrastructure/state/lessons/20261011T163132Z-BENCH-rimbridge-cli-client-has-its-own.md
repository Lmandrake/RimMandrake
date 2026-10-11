The rimbridge CLI client has its own default wait (~30 s) separate from a tool's timeoutSeconds/timeoutMs parameter: a tool that legitimately needs 30-90 s (quicktest boot, an ordered_job wait) needs --timeout <N> on the CLI call too, or it times out client-side first. Source: FOUNDRY_REBOOT_HANDOFF_202609140417.md.
home: skills/rimbridge/references/traps.md
