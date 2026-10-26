A live re-assert row must FAIL, not UNMEASURED, on any last-reason that only startup writes (e.g. 'surface placer registered'): seeing it last in a running game proves the FinalizeInit hook never ran. Only reasons a later proof could have written (proof:, settings changed) are UNMEASURED.
home: src/RimMandrake/Minerals/validation.py
