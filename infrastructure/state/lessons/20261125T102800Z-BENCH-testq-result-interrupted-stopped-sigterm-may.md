A testq result INTERRUPTED 'stopped (SIGTERM)' may be a deliberate cancel: read the job record's cancelled/cancel_reason fields (testq.read_json of the done record) before tracing the stop on the host. On 2026-11-25 a control.py selftest ran its kill probe in the same second as the stop and looked guilty; the record said the owner had wound SteveDesktop down.
item: HARNESS_REPAIR_CAUSE_8135787B_3
