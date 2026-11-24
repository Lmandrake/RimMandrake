argparse exits 2 on a bad command line. In a tool whose exit 2 means 'could not look', a typo then reads as an unreadable source. Override ArgumentParser.error (and pass parser_class to add_subparsers) so that a bad command line is the tool's own refusal code. Found in account_plan.py, where a selftest's unknown command killed the whole selftest process with exit 2.
item: RIMMANDRAKE_DESIGN_ACCOUNT_PLAN_ONE_FILE_COMMANDED_IN_ONE_LINE
home: NONE
