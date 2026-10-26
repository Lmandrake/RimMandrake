jawa/static_call reads args='' as ZERO params, so a one-string-arg method (e.g. Minerals ProofState(string)) is not found; pass a single space ' ' for one empty arg (fixed in Minerals/validation.py _one_arg at e4b94cec9b).
home: rimbridge
