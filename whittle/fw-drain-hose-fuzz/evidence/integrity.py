"""Hash all tracked FlowWorks/GSS files, shared sources, and wrapper/tool inputs."""
import hashlib, json, subprocess, sys, time
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[2]
paths=subprocess.check_output(['git','ls-files','src/RimMandrake/FlowWorks','src/RimMandrake/GimmeSomeSlack','src/RimMandrake/_Shared','src/RimMandrake/Utils','src/Directory.Build.targets','src/Directory.Build.props'],cwd=root,text=True).splitlines()
paths += ['whittle/fw-drain-selftest-resume/evidence/reference/RimWorld/Pawn_NeedsTracker.cs']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(): return {p:sha(root/p) for p in paths}
def snapshot():
    return dict(time=time.time(),HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),sha256=hashes(),status=subprocess.check_output(['git','status','--short'],cwd=root,text=True))
def staged_hashes():
    sys.path.insert(0,str(root/'src/RimMandrake/Utils'))
    import selftest_winstage, winbuild
    project=root/'src/RimMandrake/FlowWorks/Source/SelfTest/RimMandrakeFlowWorks.SelfTest.csproj'
    stage=Path(winbuild.BUILD_ROOT)/selftest_winstage.stage_name_for(str(project),str(root))
    # The wrapper deliberately excludes media/bin/obj; snapshot still hashes all media.
    import fnmatch
    def excluded(p):
        return any((e.endswith('/') and e[:-1] in Path(p).parts) or
                   (not e.endswith('/') and fnmatch.fnmatch(Path(p).name,e)) for e in winbuild.RSYNC_EXCLUDES)
    skipped=[p for p in paths if p.startswith('src/') and excluded(p)]
    want=[p for p in paths if p.startswith('src/') and not excluded(p)]
    actual={p:sha(stage/p) for p in want if (stage/p).is_file()}
    artifacts={str(p.relative_to(stage)):dict(sha256=sha(p),bytes=p.stat().st_size,mtime=p.stat().st_mtime) for p in (stage/project.relative_to(root).parent/'bin/Release/net8.0').glob('RimMandrakeFlowWorks.SelfTest.*')}
    provenance=stage/'BUILD_SOURCE.json'
    return dict(stage=str(stage),build_source=json.loads(provenance.read_text()) if provenance.exists() else None,artifacts=artifacts,excluded_media_or_build_outputs=skipped,sha256=actual,missing=[p for p in want if p not in actual],mismatch=[p for p in want if p in actual and sha(root/p)!=actual[p]])
if __name__=='__main__':
    mode=sys.argv[1]; target=here/('integrity_'+mode+'.json')
    assert not target.exists()
    result=snapshot()
    if mode != 'original':
        original=json.loads((here/'integrity_original.json').read_text())['sha256']
        result['changed_since_original']=[p for p,h in result['sha256'].items() if original.get(p)!=h]
    if mode in ('after_test','before_review','after_review','after_final_review'):
        result['staged']=staged_hashes()
        result['same_as_test_input']=result['sha256']==json.loads((here/'integrity_before.json').read_text())['sha256']
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('sha256','staged')},indent=2))
    if 'staged' in result:
        print(json.dumps({k:v for k,v in result['staged'].items() if k!='sha256'},indent=2))
        assert result['same_as_test_input'] and not result['staged']['missing'] and not result['staged']['mismatch']
