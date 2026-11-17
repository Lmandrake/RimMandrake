bar_rule.DETECT does not catch a bare numeral or a percent ('30%', 'per cent', '0.4'): a bar sentence carrying a number passes it as number-free. designer_cleanse.py adds its own NUMERAL detector over says/accept/reject (test_detector: 10 numbered and 6 name/version texts; a mutation back to bar_rule alone fails it). Any other reader that relies on bar_rule.detect for 'has a number' has the same blind spot.
item: RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED
home: src/RimMandrake/rimflow/bar_rule.py
