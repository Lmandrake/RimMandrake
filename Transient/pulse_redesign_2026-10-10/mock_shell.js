// Shared title bar + presence strip for the proposals.
function titleBar(){
  const l = LIGHTS.map(([n,ok]) => `<span class="light ${ok?'':'stale'}" title="${n} collector"><i></i>${n}</span>`).join('');
  return `<div class="stripes"></div><div class="tb"><span class="mark">pulse</span><span class="sp"></span>
    <span class="lights">${l}</span><span class="fresh"><i></i>live 3s</span><span class="btn">▾</span></div>`;
}
function presenceStrip(){
  const ps = presenceSorted();
  let h = '', gapDone = false;
  const stale = ps.filter(p => p.state === 'stale');
  for (const p of ps.filter(p => p.state !== 'stale')) {
    const cls = 'chip ' + p.state + ' s-' + (p.seat || 'OTHER');
    const extra = p.agents ? `<small>×${p.agents}</small>` : (p.state === 'stale' ? `<small>${agoTxt(p.ago)}</small>` : '');
    h += `<span class="${cls}" title="${p.note||''}"><i></i>${p.label}${extra}</span>`;
  }
  h += '<span class="gap"></span>';
  if (stale.length) h += `<span class="chip stale" title="${stale.map(p => p.label + ' ' + agoTxt(p.ago) + (p.note ? ' (' + p.note + ')' : '')).join(' · ')}"><i></i>${stale.map(p => p.label).join(' · ')} <small>${agoTxt(Math.min(...stale.map(p => p.ago)))}</small></span>`;
  return `<div class="strip">${h}<span class="done" title="finished since 02:09">✓${DONE_COUNT}</span></div>`;
}
