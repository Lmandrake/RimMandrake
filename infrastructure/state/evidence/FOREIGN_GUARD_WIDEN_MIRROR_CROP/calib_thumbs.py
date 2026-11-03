# Frozen copy from D:\ClaudeWork\rimmandrake\guard_vet\mirrorcrop; it reads thumbs2.pkl and artpipe\done there. Judged offline by check_calib.py.
# Resumable: plain + centre-square thumbs (clone's codex_image) for census outputs and every codex cache render.
import sys, time, pickle, glob
from pathlib import Path
sys.path.insert(0, '/home/mandrake/rm/relentless/clones/FOREIGN_GUARD_WIDEN_MIRROR_CROP/skills/generating-images/scripts')
import codex_image as ci
store = Path(__file__).with_name('thumbs2.pkl')
data = pickle.loads(store.read_bytes()) if store.exists() else {}
census = [p for p, v in pickle.loads(Path(__file__).parent.joinpath('../thumbs.pkl').read_bytes()).items() if v]
cache = sorted(glob.glob('/mnt/c/Users/Mandrake/.codex/generated_images/*/*') +
               glob.glob('/mnt/c/Users/Mandrake/.codex_workers/*/*/generated_images/*/*'))
cache = [c for c in cache if Path(c).suffix.lower() in ci.IMAGE_SUFFIXES]
t0, n = time.time(), 0
for kind, lst in (('out', census), ('cache', cache)):
    for p in lst:
        if p in data: continue
        try:
            st = Path(p).stat()
        except OSError:
            data[p] = None; continue
        im = ci._open_rgba(Path(p))
        if im is None:
            data[p] = None; continue
        c = ci._centre_square(im)
        data[p] = (kind, im.size, st.st_mtime, ci._thumb_of(im), ci._thumb_of(c) if c is not None else None)
        n += 1
        if time.time() - t0 > float(sys.argv[1]): break
    if time.time() - t0 > float(sys.argv[1]): break
store.write_bytes(pickle.dumps(data))
print('added', n, 'total', len(data), 'census', len(census), 'cache', len(cache), f'{time.time()-t0:.0f}s')
