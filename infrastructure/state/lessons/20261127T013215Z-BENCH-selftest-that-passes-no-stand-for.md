A selftest that passes no stand-in for a live-state reader (here maturation_dispatch.pilot_ledger, which reads the real modledger) goes red on every clone the day the live state changes, and ./publish then blames the next unrelated commit. When a pipeline check turns red after your commit, rerun it with your change pulled out before you debug your change; then pin the reader in the test's fx.
item: OPS_STEVE_DIAGNOSE_INVALID_SHARE_UKDG
home: skills/clone-landing-commits
