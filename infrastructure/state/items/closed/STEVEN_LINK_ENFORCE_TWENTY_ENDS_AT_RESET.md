# STEVEN_LINK_ENFORCE_TWENTY_ENDS_AT_RESET

## Spec
Operations alarm run 2026-11-04T03:10Z. The transient timer rm-account-handover-steven (account_handover.py check --from steven --to system --at 20) carries the owner's one-week allowance (OWNER note 2026-11-04T02:21:40Z on RUNNING_PAGE_BUILD_TOKEN_FUEL_GAUGE: "He has authorized using another 20% of his account"; memory: this week only). It has no expiry: after steven's weekly reset (~2026-11-04 13:59 PST, meter hours_to_reset) it would let us draw him to 20% left, against slot_rules.json lent_accounts.steven (max_used_by_us_pct 48, "Leave at 52% left"). switching_plan.py is passive (owner HOLD 2026-10-28), so nothing else stops it, and nothing switches back to lukas at his reset (~15:00 PST).
Fix before steven's reset: give the link an expiry (or stop it at the reset and start a --from steven --to <next> --at 52 link), and ask the Conductor whether lukas should take over again at his reset while the HOLD stands. The two handover timers are systemd-run transients and die on a WSL restart.
Verify: after the reset, systemctl --user shows no steven link below 52; account_handover log names the change.
