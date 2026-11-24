A live script run with stderr into the same file as stdout glues a stderr line (the bridge client's split report at exit) onto a row's line, so a line-anchored reader loses that row: give stderr its own file (stage6_checks.sh).
item: RIMMANDRAKE_SEND_STAGE_SIX_CHECKS_TO_STEVE_GAMES_NONE_CARRY_A_BLOCK
