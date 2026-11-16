selftest_leaningscrub.py runs about 340-420 s alone but had no '# selftest-timeout:' tag, so run_selftests --only reported it as CRASH [timeout] at the 240 s default; the direct run's own verdict was green. Fix: tag the header '# selftest-timeout: 600'. Any selftest whose direct runtime is over 240 s needs that tag, or the sweep can never show it green.
item: RIMMANDRAKE_AUTOBUILD_LEANINGSCRUB_FIFTY_NINE_BARS_LEFT
home: src/RimMandrake/Utils/run_selftests.py
