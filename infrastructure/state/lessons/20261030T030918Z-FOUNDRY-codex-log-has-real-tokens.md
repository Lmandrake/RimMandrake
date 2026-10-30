codex exec writes the real token count to its log as 'tokens used' then a number on the next line (e.g. 6,261 for a 4186-char prompt + 87-char answer whose chars/4 estimate is ~1150). Meter GPT from that line, not from chars/4, which ran 3-5x low on the two samples (and ignores reasoning tokens and images).
home: skills/chatgpt-consult
