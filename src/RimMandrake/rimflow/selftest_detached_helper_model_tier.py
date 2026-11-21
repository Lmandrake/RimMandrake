#!/usr/bin/env python3
"""A launch names its model by tier (fable, opus, sonnet). A full model id is a fault of form: the launcher
repairs it to its tier and goes on. Seen 2026-11-21: the tick passed 'claude-fable-5-2', the launch was refused
three times and FlowWorks paused on the fault loop.

Promise model-id-is-repaired-to-its-tier: `model_tier` maps a full id or any case to its tier; a banned or
unknown model stays as given, so the H4 gate still refuses it (Haiku is banned)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detached_helper as DH  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS  " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def main():
    fn = getattr(DH, "model_tier", None)
    check(fn is not None, "detached_helper.model_tier exists")
    if fn is None:
        return 1
    for given, want in (("claude-fable-5-2", "fable"), ("claude-opus-5-5", "opus"), ("claude-sonnet-5-5", "sonnet"),
                        ("Opus", "opus"), (" fable ", "fable"), ("opus", "opus"), ("sonnet", "sonnet"),
                        ("us.anthropic.claude-opus-5-5-v1:0", "opus"), ("claude-opus-5-5[1m]", "opus")):
        check(fn(given) == want, "%r -> %r (got %r)" % (given, want, fn(given)))
    for given in ("claude-haiku-5-5", "haiku", "gpt-6.1", "", None):
        check(fn(given) not in DH.MODELS, "%r is not repaired into an allowed tier (got %r)" % (given, fn(given)))
    # the launcher uses it: a full id passes the H4 gate's test
    check(DH.model_tier("claude-fable-5-2") in DH.MODELS, "a full Fable id passes the model gate after repair")
    print("selftest_detached_helper_model_tier: %s" % ("all PASS" if not FAILS else "%d FAIL" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
