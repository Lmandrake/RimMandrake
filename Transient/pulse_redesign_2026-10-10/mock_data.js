// Real data, captured from the live pulse daemon (/api/now) and the artifact census at 2026-10-10 07:07-07:15.
// Ages are hours before capture. seat -> colour only; the names are never printed in the lists.
const RULINGS = [
  {seat:'FOUNDRY', id:'ART_TEXTURE_GAPS_FOLLOWUP_1', text:'only your art picks remain: Braskeen REDO v2, Ismerrow A?', age:0.3, ev:'gapart'},
  {seat:'FOUNDRY', id:'FIREHAWK_FLIGHT_BEHAVIOR_1', text:'needs a joint live session with you watching, ~20 spawned', age:24.5},
  {seat:'BENCH',   id:'BIOME_LANDMARK_REFINEMENT_1', text:'(no reason recorded on the needs event)', age:31.4},
  {seat:'FOUNDRY', id:'STARWARS_JUNK_RESKIN_1', text:'review sheet ready for your curation', age:148.0, ev:'sheet'},
  {seat:'FOUNDRY', id:'SWALE_CANAL_ART_REFERENCE_1', text:'v2 render landed; only your keep/replace remains', age:148.4, ev:'render'},
  {seat:'BENCH',   id:'SALVATION_RITES_UNIFICATION_1', text:'rites unified in mandrake.rut.rites; biomes teach rites', age:211.7},
  {seat:'FOUNDRY', id:'CRACKEDLANDS_FULL_RENAME_1', text:'live-tile check done; the rename is yours to approve', age:273.1},
  {seat:'BENCH',   id:'TWILIGHT_BOTTOM_CAST_1', text:'the Deepwater bottom cast: 6-8 named residents of the lit bottom', age:322.4},
];
const T = 'D:\\Luke\\dev\\RimMandrake\\Transient\\';
const ARTIFACTS = [
  {seat:'FOUNDRY', kind:'html', name:'codebase_health.html', what:'codebase health page', age:0.2, path:T+'codebase_health.html'},
  {seat:'BENCH',   kind:'sheets', name:'biome sheets', what:'27 biome sheets served · 10 never reviewed', age:0.1, path:'http://localhost:33679/ … (27 live)', n:27, unrev:10},
  {seat:'FOUNDRY', kind:'png', name:'icon_renders_contact_batch3', what:'icon renders, batch 3', age:3.0, thumb:'thumbs/icons3.jpg', path:T+'icon_renders_contact_batch3_20261010.png'},
  {seat:'FOUNDRY', kind:'png', name:'gap_art_contact', what:'texture-gap art picks', age:3.0, thumb:'thumbs/gapart.jpg', path:T+'gap_art_contact_20261010.png'},
  {seat:'BENCH',   kind:'png', name:'live_sheet_check/plants', what:'live sheet check · plants', age:4.9, thumb:'thumbs/plants.jpg', path:T+'live_sheet_check_2026-10-10\\plants.png'},
  {seat:'FOUNDRY', kind:'png', name:'live_sheet_check/portraits', what:'live sheet check · portraits', age:5.1, thumb:'thumbs/portraits.jpg', path:T+'live_sheet_check_2026-10-10\\portraits.png'},
  {seat:'FOUNDRY', kind:'png', name:'rot_v3_contact', what:'The Rot art, v3 contact', age:6.2, thumb:'thumbs/rotv3.jpg', path:T+'rot_v3_contact_20261010.png'},
  {seat:'FOUNDRY', kind:'dir', name:'messy_conduit_live', what:'Messy Conduit live shots ×8', age:8.8, thumb:'thumbs/conduit.jpg', path:T+'messy_conduit_live_20261002\\'},
];
// presence, sorted by last activity (seconds ago). state: run | idle | stale
const PRESENCE = [
  {label:'bench', seat:'BENCH', state:'run', agents:1, ago:180},
  {label:'foundry', seat:'FOUNDRY', state:'run', agents:3, ago:720},
  {label:'rimworld', state:'run', ago:28, note:'up · bridge free'},
  {label:'artpipe', state:'idle', ago:3, note:'0 queued'},
  {label:'mem', state:'idle', ago:1320, note:'pen ok ×24'},
  {label:'hestia', state:'stale', ago:47880},
  {label:'emerg', state:'stale', ago:47880},
  {label:'phone', state:'stale', ago:47880, note:'remote-control child (was "bench-61")'},
];
// one light per collector source
const LIGHTS = [['sessions',1],['ledger',1],['sheets',1],['game',1],['art',1],['kernel',1],['mem',1]];
const DONE_COUNT = 14;
function ageTxt(h){ if(h<1) return Math.max(1,Math.round(h*60))+'m'; if(h<48) return Math.round(h)+'h'; return Math.round(h/24)+'d'; }
function agoTxt(s){ if(s<60) return s+'s'; if(s<3600) return Math.round(s/60)+'m'; return Math.round(s/3600)+'h'; }
function presenceSorted(){ const rank={run:0,idle:1,stale:2}; return PRESENCE.slice().sort((a,b)=>rank[a.state]-rank[b.state]||a.ago-b.ago); }
