# wt/gitlab timing experiments (2026-10-01) - findings kept before deletion 2026-10-08

Assessed NO VALUE: nested repos were clones of origin/main (seat, e4/repo, e2_*, e3 against local scratch remote.git); 0 stashes, 0 commits not on a remote except 4 in e3/w (local scratch remote). Raw experiment outputs below.

## e1.out
```
status drvfs ([12.19, 12.18, 11.88], 12.18)
status ext4 ([0.05, 0.04, 0.04], 0.04)
add+commit [0.08, 0.07, 0.07]
worktree add full [12.43, 9.51, 10.99]
4.1G	/home/mandrake/wt/gitlab/wtfull0

worktree add sparse [1.05, 0.95, 0.93]
318M	/home/mandrake/wt/gitlab/wtsp0
29494
8
0

status in full wt ([1.06, 0.04, 0.04], 0.04)
status in sparse wt ([0.01, 0.01, 0.01], 0.01)
```

## e2.out
```
a secs 4.7 lessons present 40 /40; jsonl records 40 /40; own-lines 40 /40; commits on main 10932 ; lesson lines (dups?) 40
  per-agent {"1": {"conflicts": 4, "retries": 6, "fail": 0, "push_rej": 2}, "0": {"conflicts": 0, "retries": 0, "fail": 0, "push_rej": 0}, "2": {"conflicts": 12, "retries": 20, "fail": 0, "push_rej": 8}, "3": {"conflicts": 8, "retries": 12, "fail": 0, "push_rej": 4}}
b secs 4.6 lessons present 40 /40; jsonl records 40 /40; own-lines 40 /40; commits on main 10932 ; lesson lines (dups?) 40
  per-agent {"3": {"conflicts": 0, "retries": 18, "fail": 0, "push_rej": 18}, "1": {"conflicts": 0, "retries": 0, "fail": 0, "push_rej": 0}, "2": {"conflicts": 0, "retries": 9, "fail": 0, "push_rej": 9}, "0": {"conflicts": 0, "retries": 27, "fail": 0, "push_rej": 27}}
c secs 4.7 lessons present 40 /40; jsonl records 40 /40; own-lines 40 /40; commits on main 10932 ; lesson lines (dups?) 0
  per-agent {"1": {"conflicts": 0, "retries": 18, "fail": 0, "push_rej": 18}, "3": {"conflicts": 0, "retries": 0, "fail": 0, "push_rej": 0}, "2": {"conflicts": 0, "retries": 9, "fail": 0, "push_rej": 9}, "0": {"conflicts": 0, "retries": 27, "fail": 0, "push_rej": 27}}
a secs 4.6 lessons present 40 /40; jsonl records 40 /40; own-lines 40 /40; commits on main 10932 ; lesson lines (dups?) 40
  per-agent {"0": {"conflicts": 8, "retries": 12, "fail": 0, "push_rej": 4}, "1": {"conflicts": 0, "retries": 0, "fail": 0, "push_rej": 0}, "2": {"conflicts": 4, "retries": 5, "fail": 0, "push_rej": 1}, "3": {"conflicts": 12, "retries": 18, "fail": 0, "push_rej": 6}}
b secs 4.8 lessons present 40 /40; jsonl records 40 /40; own-lines 40 /40; commits on main 10932 ; lesson lines (dups?) 40
  per-agent {"1": {"conflicts": 0, "retries": 18, "fail": 0, "push_rej": 18}, "0": {"conflicts": 0, "retries": 9, "fail": 0, "push_rej": 9}, "3": {"conflicts": 0, "retries": 27, "fail": 0, "push_rej": 27}, "2": {"conflicts": 0, "retries": 0, "fail": 0, "push_rej": 0}}
c secs 4.7 lessons present 40 /40; jsonl records 40 /40; own-lines 40 /40; commits on main 10932 ; lesson lines (dups?) 0
  per-agent {"3": {"conflicts": 0, "retries": 9, "fail": 0, "push_rej": 9}, "1": {"conflicts": 0, "retries": 0, "fail": 0, "push_rej": 0}, "2": {"conflicts": 0, "retries": 27, "fail": 0, "push_rej": 27}, "0": {"conflicts": 0, "retries": 18, "fail": 0, "push_rej": 18}}
```

## e3.out
```
--- T1 both append to end of same file
$ git merge-tree --write-tree app1 app2 
  rc= 1 
  6a32df2a3fcef1ba57c66fe2ba64bcc40f337f69
  100644 f0f23074642919bb50ab5b6e4ec489706127f061 1	e3/log.txt
  100644 d25106e4c21c8981fc39783cea822e4806dc2daf 2	e3/log.txt
  100644 43c6bf2ed44263e572467a849d480104c425a9ea 3	e3/log.txt
  
  Auto-merging e3/log.txt
  CONFLICT (content): Merge conflict in e3/log.txt
--- T1b with --name-only/--messages
$ git merge-tree --write-tree --name-only app1 app2 
  rc= 1 
  6a32df2a3fcef1ba57c66fe2ba64bcc40f337f69
  e3/log.txt
  
  Auto-merging e3/log.txt
  CONFLICT (content): Merge conflict in e3/log.txt
--- T2 rename on one side, edit of old path on other
$ git merge-tree --write-tree ren editold 
  rc= 0 
  7f6adb05b0f168fd8b65d5af38d6d6cb48753864
--- T2b rename vs append (should be clean via rename detection)
$ git merge-tree --write-tree ren app1 
  rc= 0 
  19f628fa7c2fb2156eb6e5c093342ba45d33ea64
--- T3 same-line edits
$ git merge-tree --write-tree edit_same_line edit_same_line2 
  rc= 1 
  c967420c77311e2ecb8f2a9e83ddb9f7647e9de6
  100644 f0f23074642919bb50ab5b6e4ec489706127f061 1	e3/log.txt
  100644 be7b072c99a315cb0a448557e385ab17cf95e34d 2	e3/log.txt
  100644 87b4c69c61179d2a4432b08095d7206bd5fa1831 3	e3/log.txt
  
  Auto-merging e3/log.txt
  CONFLICT (content): Merge conflict in e3/log.txt
--- T4 pipeline: clean merge (ren + app1), no worktree touch
$ git commit-tree 19f628fa7c2fb2156eb6e5c093342ba45d33ea64 -p ren -p app1 -m "merge via merge-tree" 
  rc= 0 
  89658cabba5430063dab1edea731f43b2e337376
$ git push /home/mandrake/wt/gitlab/e3/remote.git 89658cabba5430063dab1edea731f43b2e337376:refs/heads/merged-ren-app1 
  rc= 0 
  To /home/mandrake/wt/gitlab/e3/remote.git
   * [new branch]          89658cabba5430063dab1edea731f43b2e337376 -> merged-ren-app1
$ git --git-dir=/home/mandrake/wt/gitlab/e3/remote.git log --oneline -3 merged-ren-app1 
  rc= 0 
  89658cabb merge via merge-tree
  e95e64a8a ren
  1d8e36f03 app1
$ git --git-dir=/home/mandrake/wt/gitlab/e3/remote.git ls-tree -r --name-only merged-ren-app1 -- e3 
  rc= 0 
  e3/log.txt
  e3/new_name.txt
worktree/HEAD unchanged: True
--- T5 pipeline on app1+app2 conflict (rc 1, tree printed with markers)
rc 1 tree 6a32df2a3fcef1ba57c66fe2ba64bcc40f337f69
$ git cat-file -p 6a32df2a3fcef1ba57c66fe2ba64bcc40f337f69:e3/log.txt 
  rc= 0 
  l1
  l2
  l3
  <<<<<<< app1
  from-app1
  =======
  from-app2
  >>>>>>> app2
--- T6 push-to-main race: FF-publish pattern: merge-tree onto a moved remote main, then compare-and-swap push
$ git push --force-with-lease=main:1d8e36f03177f602f8347380fb2031b18f51a2ea origin 1a575510939ba42b1b26ada50a4863bee29689c4:refs/heads/main 
  rc= 0 
  To /home/mandrake/wt/gitlab/e3/remote.git
     1d8e36f03..1a5755109  1a575510939ba42b1b26ada50a4863bee29689c4 -> main
$ git status --porcelain 
  rc= 0 
  
```

## e4d.out
```
== D1 non-ff push test
$ [repo] jj git fetch
    Nothing changed.
$ [repo] jj new main@origin -m base
    Working copy  (@) now at: zyxvrvpy 39266bfe (empty) base
    Parent commit (@-)      : unmtvlmn 02307665 main | a0 r4
$ [ws1] jj workspace update-stale
    Attempted recovery, but the working copy is not stale.
$ [ws2] jj workspace update-stale
    Working copy  (@) now at: rksqxrqy/0 ff51769d (divergent) (empty) (no description set)
    Parent commit (@-)      : ypslmrup 56f61c1c a3 r4
    Added 0 files, modified 1 files, removed 1 files
    Updated working copy to fresh commit ff51769d2f00
remote main X=02307665dce3f860295c81149af425fcc54bc53c
$ [ws1] jj new main@origin
    Working copy  (@) now at: zypursrt bef89c9a (empty) (no description set)
    Parent commit (@-)      : unmtvlmn 02307665 main | a0 r4
    Added 3 files, modified 2 files, removed 0 files
$ [ws2] jj new main@origin
    Working copy  (@) now at: rvupklzt a7e0180e (empty) (no description set)
    Parent commit (@-)      : unmtvlmn 02307665 main | a0 r4
    Added 2 files, modified 1 files, removed 0 files
$ [ws1] jj commit -m c1
    Working copy  (@) now at: uumsuwqv 4d2ab967 (empty) (no description set)
    Parent commit (@-)      : zypursrt 051c619b c1
$ [ws2] jj commit -m c2
    Working copy  (@) now at: uyvtywpt f2711b8f (empty) (no description set)
    Parent commit (@-)      : rvupklzt 23a99c12 c2
$ [ws1] jj bookmark set main -r @-
    Moved 1 bookmarks to zypursrt 051c619b main* | c1
$ [ws1] jj git push -b main
    Changes to push to origin:
      bookmark: main [move forward from 02307665dce3 to 051c619b145d]
remote main now 051c619b145da77fef69ab56153fb8f23b1ba1e1 (c1 landed)
-- ws2 (built on X) tries bookmark set main WITHOUT --allow-backwards:
$ [ws2] jj bookmark set main -r @-
    Error: Refusing to move bookmark backwards or sideways: main
    Hint: Use --allow-backwards to allow it.
-- ws2 with --allow-backwards then push (simulating a sloppy agent):
$ [ws2] jj bookmark set main -r @- --allow-backwards
    Moved 1 bookmarks to rvupklzt 23a99c12 main* | c2
$ [ws2] jj git push -b main
    Changes to push to origin:
      bookmark: main [move sideways from 051c619b145d to 23a99c12892e]
remote main now 23a99c12892e48562a934058c0138ab9cf457cc4; contains c1 file? 0 ; c2 file? 1
```

## e4u.out
```
== D2 jj undo across workspaces
$ [ws1] jj workspace update-stale
    Attempted recovery, but the working copy is not stale.
$ [ws3] jj workspace update-stale
    Attempted recovery, but the working copy is not stale.
$ [ws1] jj new main@origin
    Working copy  (@) now at: ktzxpmrt 67d11243 (empty) (no description set)
    Parent commit (@-)      : rvupklzt 23a99c12 main* | c2
    Added 1 files, modified 0 files, removed 1 files
$ [ws3] jj new main@origin
    Working copy  (@) now at: ysvuzxpm 85fe1468 (empty) (no description set)
    Parent commit (@-)      : rvupklzt 23a99c12 main* | c2
    Added 3 files, modified 1 files, removed 0 files
$ [ws1] jj commit -m A_work
    Working copy  (@) now at: xvoonoop d2179fdb (empty) (no description set)
    Parent commit (@-)      : ktzxpmrt 0adfe3b7 A_work
$ [ws3] jj commit -m B_work
    Working copy  (@) now at: xzwsztsy 1a614eec (empty) (no description set)
    Parent commit (@-)      : ysvuzxpm cfc7361e B_work
-- ws1 op log top 3
    63edcb758158 commit d7e1b734501549429a60464cd43a323073772fe1
    5fe91336f2cd snapshot working copy
    fee68f2fb3cf commit f2e1dad56f07960ffc5ae99fde600bc4469ead44
-- ws1 runs plain jj undo (agent A thinks it undoes its own commit)
$ [ws1] jj undo
    Undid operation: 63edcb758158 (2026-10-01 23:45:53) commit d7e1b734501549429a60464cd43a323073772fe1
    Restored to operation: 5fe91336f2cd (2026-10-01 23:45:53) snapshot working copy
-- ws3 view: is B_work still there? (log -r 'description(B_work)')
$ [ws3] jj log --no-graph -r description(B_work) -T description
-- ws1 view: A_work still there?
$ [ws1] jj log --no-graph -r description(A_work) -T description
-- ws3 status after A's undo:
$ [ws3] jj st
    Working copy changes:
    A u_b.txt
    Working copy  (@) : ysvuzxpm d7e1b734 (no description set)
    Parent commit (@-): rvupklzt 23a99c12 main* | c2
-- ws3 file b exists on disk? /home/mandrake/wt/gitlab/e4/ws3/u_b.txt
```
