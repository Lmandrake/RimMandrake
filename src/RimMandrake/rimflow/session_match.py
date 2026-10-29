"""ONE rule for "is this live session the seat/hold window called N". The title hook (.claude/hooks/set_session_title.py)
renames a seat window to "<N> ▶ <current queue item>", so a window is N or N + " ▶ " + anything. Nothing else
(no "AGENT BENCHX", no prefix without the separator) matches."""
TITLE_SEP = " ▶ "


def name_matches(name, n):
    return bool(n) and isinstance(name, str) and (name == n or name.startswith(n + TITLE_SEP))
