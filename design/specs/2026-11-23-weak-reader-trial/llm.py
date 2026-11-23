"""One clean `claude -p` call: no tools, no rule files, no MCP, no skills, no memory, fresh session. Returns a dict."""
import subprocess,json,os,hashlib
W="/mnt/d/ClaudeWork/scratch/weak_reader_trial"
ENV={k:v for k,v in os.environ.items() if not k.startswith("CLAUDE")}
def call(model,system,prompt,timeout=1200):  # danger guarded: a hung child; a real call takes under 2 minutes
    try:
        p=subprocess.run(["claude","-p","--model",model,"--tools","","--setting-sources","","--strict-mcp-config",
            "--disable-slash-commands","--no-session-persistence","--system-prompt",system,"--output-format","json"],
            input=prompt,capture_output=True,text=True,timeout=timeout,env=ENV,cwd=W+"/cwd")
        d=json.loads(p.stdout)
    except Exception as e:
        return dict(ok=False,error=repr(e)[:400],text="",usage=None,model=None)
    ok=not d.get("is_error") and d.get("subtype")=="success" and bool((d.get("result") or "").strip())
    return dict(ok=ok,error=None if ok else str(d.get("result"))[:400],text=d.get("result") or "",
                usage=d.get("modelUsage"),model=",".join((d.get("modelUsage") or {}).keys()))
import sys; sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"../../../src/RimMandrake/rimflow")))
def weighted(usage):
    from role_launch import MODEL_PRICES
    t=0.0;ref=float(MODEL_PRICES["claude-opus-5-5"]["input_tokens"])
    for m,u in (usage or {}).items():
        p={k:float(v) for k,v in MODEL_PRICES[m].items()}
        h=u.get("cacheCreationEphemeral1hInputTokens",0);f=u.get("cacheCreationInputTokens",0)-h
        t+=(u["inputTokens"]*p["input_tokens"]+f*p["cache_write_5m"]+h*p["cache_write_1h"]+u["cacheReadInputTokens"]*p["cache_read_input_tokens"]+u["outputTokens"]*p["output_tokens"])/ref
    return t
def js(text):
    a,b=text.find("{"),text.rfind("}"); return json.loads(text[a:b+1])
