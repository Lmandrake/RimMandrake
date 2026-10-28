winbuild.py builds in a stage then copies the DLL back; a 'timeout 500' that fires during copy-back leaves the repo DLL stale while the build log says succeeded. Use timeout 540 and confirm 'BUILT ... (source <sha>+dirty)' is the last line, and md5 the deployed DLL against the repo one.
home: NONE
