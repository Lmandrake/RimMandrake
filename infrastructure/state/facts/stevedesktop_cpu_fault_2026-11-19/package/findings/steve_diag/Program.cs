// stevecheck: deterministic CPU and RAM checks. Non-destructive; writes one log file.
//   core <cpu> <seconds> <log>          pin to a logical CPU; every round recomputes known work and compares
//   mem  <gb> <passes> <threads> <log>  walk gb of committed RAM with address-seeded patterns
//   add "inject" as the last argument to flip a bit: proves the instrument can see a fault.
using System;using System.Diagnostics;using System.IO;using System.Linq;using System.Runtime.InteropServices;
using System.Runtime.Intrinsics;using System.Runtime.Intrinsics.X86;using System.Security.Cryptography;using System.Threading;
unsafe static class P{
 static string logp; static readonly object L=new object();
 static void Log(string s){lock(L){File.AppendAllText(logp,DateTime.UtcNow.ToString("HH:mm:ss")+" "+s+"\n");}}
 [DllImport("kernel32")] static extern IntPtr GetCurrentThread();
 [DllImport("kernel32")] static extern UIntPtr SetThreadAffinityMask(IntPtr h,UIntPtr m);
 [DllImport("kernel32")] static extern uint GetCurrentProcessorNumber();
 [DllImport("kernel32",SetLastError=true)] static extern void* VirtualAlloc(void* a,nuint n,uint t,uint p);
 [DllImport("kernel32")] static extern bool VirtualFree(void* a,nuint n,uint t);
 static ulong Mix(ulong x){x^=x>>12;x^=x<<25;x^=x>>27;return x*0x9E3779B97F4A7C15UL;}
 // Integer AVX2: multiply, shuffle, add over a buffer. Result is a pure function of seed.
 static ulong IntAvx(ulong* b,int n,ulong seed,int reps){
  var k=Vector256.Create(seed|1,seed*3|1,seed*5|1,seed*7|1);var a=Vector256.Create(seed);
  for(int r=0;r<reps;r++)for(int i=0;i+4<=n;i+=4){var v=Avx.LoadVector256(b+i);
   var lo=Avx2.Multiply(v.AsUInt32(),k.AsUInt32());var s=Avx2.Shuffle(v.AsUInt32(),0x1B).AsUInt64();
   a=Avx2.Add(Avx2.Xor(a,lo),s);a=Avx2.Or(Avx2.ShiftLeftLogical(a,7),Avx2.ShiftRightLogical(a,57));
   Avx.Store(b+i,Avx2.Add(v,a));}
  return a.GetElement(0)^a.GetElement(1)^a.GetElement(2)^a.GetElement(3);}
 // FMA doubles. IEEE exact, so bit identical on every healthy core.
 static ulong Fp(int n,ulong seed,int reps){double* d=stackalloc double[64];
  for(int i=0;i<64;i++)d[i]=1.0+(Mix(seed+(ulong)i)>>12)*1e-16;
  var a=Vector256.Create(1.0000001);var c=Vector256.Create(0.9999999);var acc=Vector256.Create(1.0);
  for(int r=0;r<reps;r++)for(int i=0;i+4<=64;i+=4){var v=Avx.LoadVector256(d+i);
   acc=Fma.MultiplyAdd(acc,v,c);acc=Avx.Divide(acc,Avx.Sqrt(Avx.Add(Avx.Multiply(acc,acc),a)));Avx.Store(d+i,Fma.MultiplySubtract(v,a,Avx.Multiply(acc,c)));}
  ulong h=0;for(int i=0;i<4;i++)h=Mix(h^BitConverter.DoubleToUInt64Bits(acc.GetElement(i)));return h;}
 static string Round(ulong seed,ulong[] buf,byte[] by,bool inject){
  for(int i=0;i<buf.Length;i++)buf[i]=Mix(seed+(ulong)i);
  ulong a,f=Fp(64,seed,20000);fixed(ulong* p=buf){a=IntAvx(p,buf.Length,seed,3);}
  if(inject)a^=1;
  Buffer.BlockCopy(buf,0,by,0,by.Length);var h=SHA256.HashData(by);
  return a.ToString("x16")+f.ToString("x16")+Convert.ToHexString(h).Substring(0,16);}
 static int Core(string[] v){int cpu=int.Parse(v[1]);int secs=int.Parse(v[2]);logp=v[3];bool inj=v.Last()=="inject";
  Thread.BeginThreadAffinity();SetThreadAffinityMask(GetCurrentThread(),(UIntPtr)(1UL<<cpu));Thread.Sleep(5);
  var buf=new ulong[1<<20];var by=new byte[8<<20];var seeds=Enumerable.Range(0,8).Select(i=>0x1234567UL*(ulong)(i+1)).ToArray();
  var refd=new string[8];long rounds=0,bad=0,moved=0;var sw=Stopwatch.StartNew();
  for(int i=0;i<8;i++)refd[i]=Round(seeds[i],buf,by,false);
  while(sw.Elapsed.TotalSeconds<secs){int i=(int)(rounds%8);var got=Round(seeds[i],buf,by,inj&&rounds==5);rounds++;
   if(GetCurrentProcessorNumber()!=(uint)cpu)moved++;
   if(got!=refd[i]){bad++;if(bad<=5)Log($"MISMATCH cpu={cpu} round={rounds} want={refd[i]} got={got}");}}
  var all=Convert.ToHexString(SHA256.HashData(System.Text.Encoding.ASCII.GetBytes(string.Join(",",refd)))).Substring(0,16);
  Log($"CORE cpu={cpu} rounds={rounds} bad={bad} moved={moved} ref={all}");return bad>0?1:0;}
 static int Mem(string[] v){long gb=long.Parse(v[1]);int passes=int.Parse(v[2]);int th=int.Parse(v[3]);logp=v[4];bool inj=v.Last()=="inject";
  nuint bytes=(nuint)(gb<<30);ulong* m=(ulong*)VirtualAlloc(null,bytes,0x3000,4);if(m==null){Log("ALLOC FAILED err="+Marshal.GetLastWin32Error());return 2;}
  long words=(long)(bytes/8);long bad=0;Log($"MEM start gb={gb} passes={passes} threads={th}");
  void Par(Action<long,long> w){var ts=new Thread[th];long c=words/th;for(int t=0;t<th;t++){long s=t*c,e=t==th-1?words:s+c;ts[t]=new Thread(()=>w(s,e),1<<20);ts[t].Start();}foreach(var x in ts)x.Join();}
  for(int p=0;p<passes;p++){var sw=Stopwatch.StartNew();ulong salt=Mix((ulong)p+77);
   foreach(int phase in new[]{0,1,2,3}){ // 0 random,1 inverted,2 walking stripes,3 shifted thread pairing: verify on a different thread
    ulong pat(long i)=>phase==0?Mix(salt+(ulong)i):phase==1?~Mix(salt+(ulong)i):phase==2?((i&1)==0?0x5555555555555555UL:0xAAAAAAAAAAAAAAAAUL)^(ulong)(i>>9):Mix(~salt^(ulong)i);
    Par((s,e)=>{for(long i=s;i<e;i++)m[i]=pat(i);});
    if(inj&&p==0&&phase==0)m[words/2]^=1UL<<17;
    Thread.Sleep(phase==3?60000:0); // retention dwell on the last phase
    var vb=new Action<long,long>((s,e)=>{long shift=phase==3?(e-s)/2:0;for(long j=s;j<e;j++){long i=j+shift;if(i>=e)i-=e-s;ulong got=m[i],want=pat(i);if(got!=want){ulong re=m[i];long n=Interlocked.Increment(ref bad);if(n<=40)Log($"BAD pass={p} phase={phase} va={(nuint)(m+i):x} want={want:x16} got={got:x16} reread={re:x16} xor={(got^want):x16}");}}});
    Par(vb);
    Log($"pass={p} phase={phase} done bad={bad} t={sw.Elapsed.TotalSeconds:F0}s");}}
  VirtualFree(m,0,0x8000);Log($"MEM end gb={gb} bad={bad}");return bad>0?1:0;}
 // hold: keep a known value in a YMM register; only compare, never recompute. A hit = register state changed under us.
 // exec: fresh load, integer AVX2 multiply, compare against scalar truth, each iteration: window is nanoseconds.
 [System.Runtime.CompilerServices.MethodImpl(System.Runtime.CompilerServices.MethodImplOptions.AggressiveOptimization)]
 static long HoldLoop(ulong* want,long iters,ref Vector256<ulong> outv){
  var a=Avx.LoadVector256(want);var c=Avx.LoadVector256(want+4);long i=0;
  for(;i<iters;i++){var e=Avx2.CompareEqual(a,c);if(Avx2.MoveMask(e.AsByte())!=-1){outv=a;break;}}
  return i;}
 static int Hold(string[] v){int cpu=int.Parse(v[1]);int secs=int.Parse(v[2]);logp=v[3];
  Thread.BeginThreadAffinity();SetThreadAffinityMask(GetCurrentThread(),(UIntPtr)(1UL<<cpu));Thread.Sleep(5);
  ulong* w=stackalloc ulong[8];w[0]=0x0123456789ABCDEFUL;w[1]=0xFEDCBA9876543210UL;w[2]=0x5555AAAA5555AAAAUL;w[3]=0xDEADBEEFCAFEF00DUL;for(int q=0;q<4;q++)w[q+4]=w[q];
  var sw=Stopwatch.StartNew();long hits=0;double last=0;var gaps=new System.Collections.Generic.List<double>();long done=0;
  while(sw.Elapsed.TotalSeconds<secs){Vector256<ulong> got=default;long it=HoldLoop(w,20000000,ref got);done+=it;
   if(it<20000000){hits++;double t=sw.Elapsed.TotalMilliseconds;gaps.Add(t-last);last=t;
    if(hits<=12)Log($"HOLD cpu={cpu} t={t:F2}ms got={got.GetElement(3):x16}_{got.GetElement(2):x16}_{got.GetElement(1):x16}_{got.GetElement(0):x16}");}}
  gaps.Sort();Log($"HOLDSUM cpu={cpu} hits={hits} iters={done} gapMedMs={(gaps.Count>0?gaps[gaps.Count/2]:0):F2} gapMinMs={(gaps.Count>0?gaps[0]:0):F2}");return hits>0?1:0;}
 static int Main(string[] v){return v[0]=="hold"?Hold(v):v[0]=="core"?Core(v):Mem(v);}
}
