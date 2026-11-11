"""Production rewrite staging: Windows privilege refusal copies unchanged bytes; other failures still refuse/clean up."""
import os
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
import biomes_compose as B


def run():
    with tempfile.TemporaryDirectory() as tmp:
        src=Path(tmp)/'Mod'; src.mkdir()
        (src/'guard.xml').write_text('<Defs><ThingDef MayRequire="old.pkg"/></Defs>')
        payload=bytes(range(256))*4
        (src/'unchanged.dll').write_bytes(payload)
        scratch=Path(tmp)/'scratch'; scratch.mkdir()
        denied=OSError('Windows lacks symlink privilege'); denied.winerror=1314
        with patch.object(B,'scratch_dir',return_value=str(scratch)),patch.object(B.os,'symlink',side_effect=denied):
            out=Path(B.stage_rewritten(str(src),{'old.pkg':'new.pkg'},log=lambda *a:None))
        assert (out/'unchanged.dll').read_bytes()==payload
        assert not (out/'unchanged.dll').is_symlink()
        assert 'new.pkg' in (out/'guard.xml').read_text()
        assert 'old.pkg' in (src/'guard.xml').read_text()
        shutil.rmtree(out.parent)
        print('PASS Windows 1314 fallback preserves binary bytes and rewrites only staged XML')
        for error in (OSError('source vanished'),PermissionError('other refusal')):
            with patch.object(B,'scratch_dir',return_value=str(scratch)),patch.object(B.os,'symlink',side_effect=error):
                try: B.stage_rewritten(str(src),{'old.pkg':'new.pkg'},log=lambda *a:None)
                except OSError: pass
                else: raise AssertionError('unexpected symlink failure must propagate')
            assert list(scratch.iterdir())==[]
        print('PASS unexpected symlink failures propagate and leave no staging tree')
        with patch.object(B,'scratch_dir',return_value=str(scratch)),patch.object(B.os,'symlink',side_effect=denied),patch.object(B.shutil,'copy2',side_effect=OSError('copy failed')):
            try: B.stage_rewritten(str(src),{'old.pkg':'new.pkg'},log=lambda *a:None)
            except OSError: pass
            else: raise AssertionError('failed fallback must refuse')
        assert list(scratch.iterdir())==[]
        print('PASS failed fallback copy refuses and removes staging tree')

if __name__=='__main__': run()
