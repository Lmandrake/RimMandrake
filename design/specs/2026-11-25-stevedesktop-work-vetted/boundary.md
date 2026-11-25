# Boundary: the host work switch and the age filter on runs

Item: RIMMANDRAKE_VET_WORK_BOUND_FOR_STEVEDESKTOP_HE_SAW_FIREHAWK_AGAIN.

Code: `src/RimMandrake/rimflow/host_work_switch.py`, `src/RimMandrake/rimflow/work_bundle.py`, `src/RimMandrake/rimflow/list_dispatch.py`, `src/RimMandrake/Utils/maturation_now.py`. The parts:

- `src/RimMandrake/rimflow/host_work_switch.py` and `host_work_switch.json`;
- `work_bundle.switch_refusal`, `work_bundle.launch_remote` and `work_bundle.age_refusal`. `bundle_command` and
  `list_dispatch.join_candidates` read `age_refusal`;
- `list_dispatch.switch_refuses`;
- `maturation_now.switch_line`.

The testq readers have their own page: `testq/boundary.md` beside this one.

## ACCEPTS

- **switch-row.** A row `{host, mode: pipeline, date, said | per_ruling+why}`.
  - A set or a lift takes his words (`--said`).
  - It can also take the Conductor's act (`--per-ruling RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS --why`).
    Only the Conductor window can do this act.
  - Machine names: SteveDesktop, Steve1, Steve2, `stevedesktop.b`, Archmagi, ArchBig, ArchSmall, in any case.
- **ticket.** An item of the model, or a dict that has `created_at` and the failure fields. The verdict of its test
  comes from the reality sort.

## DOES NOT SURVIVE

- **hand-revert.** A hand `git revert` of the switch file. That is a commit with its author, the same as a lift with no
  words.
- **lagging-clone.** A clone that lags origin reads the switch as it was at its last sync.
- **prose-only-failure.** `failure_recorded` cannot see a failure that a ticket states only in its prose.

## PROMISES

- **switch.** A set or a lift needs his words, or the Conductor window's act. A run with `RM_ROLE_UNIT` cannot lift by
  the ruling. A lift keeps the lifted row. An unreadable file reads as switched.
- **age-filter.** These tickets enter a run:
  - an old ticket (filed before 2026-11-13) only with a test that is red today;
  - a newer ticket with a red test or a recorded failure.
- **bundle-command-filters.** `bundle_command` leaves the unvetted members out, each with its reason.
- **mod-work-not-sent-to-a-switched-host.** A mod bundle is not sent to a switched host, and no ssh runs. The list
  launcher gives a mod ticket, or a ticket whose mod cannot be read, no room on that host.
- **status-page-shows-it.** The status page names the switch and its lift, or says that no machine is switched.

## LIMITS

There are none. The switch has no expiry on purpose: an order of the owner stays until he or the Conductor lifts it.
