winbuild.py compiles the working tree, so a FlowWorks DLL built in a shared clone includes other seats' uncommitted .cs files (and the .srchash says +dirty). Before committing the DLL, check git status for others' dirty FlowWorks source; commit only when the srchash source matches committed source, or rebuild after they commit.
home: NONE
