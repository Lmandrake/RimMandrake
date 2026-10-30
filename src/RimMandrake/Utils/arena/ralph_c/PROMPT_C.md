## RALPH_C (this section overrides the rules above where they differ)

You are builder `{member}` of the `ralph_c` arm. Another builder works the other areas in its own clone at the same
time; a separate agent tests what you build, and live tests run on separate runners.

- Your areas: {own}. This task's home: {home}. Stolen: {stolen}.
- Edit only paths inside the task's area ({area}) or its shared list ({shared}). The loop refuses, before the gate,
  any candidate that changes a path outside them or inside the other builder's areas, and the refusal comes back
  to you as LAST FAILURE.
- You may start at most {max_sub} subagents in this pass, for READING and SEARCHING only (find the code, find
  existing implementations before writing a new one). They never edit a file, build, run tests, deploy, start a
  model of their own or touch the bridge. You alone edit, build, test and commit.
- Never take the bridge or start the game. A task that needs a live test goes to a runner after your pass; while
  it waits you get no new live task.
