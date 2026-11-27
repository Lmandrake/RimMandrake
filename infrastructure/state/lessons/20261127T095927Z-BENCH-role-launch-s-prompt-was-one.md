A role launch's prompt was one argv string and died E2BIG once a Designer stage packet passed 131072 bytes (MAX_ARG_STRLEN, per string, not the total): measure the longest argv string, not the sum, and carry any unbounded text on the unit's stdin (StandardInput=file:), with every pre-step given </dev/null so it cannot eat the prompt.
item: RIMMANDRAKE_FIX_DESIGNER_LAUNCH_ARGUMENT_LIST_TOO_LONG
home: design/specs/2026-11-27-role-launch-prompt-by-file/boundary.md
