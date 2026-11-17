Relaunching a killed detached run with detached_helper.py launch --resume does not carry the old run's spend cap: --budget-usd defaults to 15, so a whole-mod run first launched with --budget-usd 0 comes back under a $15 spend_watchdog stop that ends it early (2026-11-17, GSS Fable relaunch ...-1794925337, stopped and relaunched as ...-1794925467). Read the old record's budget_usd and max_s and pass both explicitly on any relaunch; the launch line prints them as 'bound X, $Y' - read it.
item: NONE
home: NONE
