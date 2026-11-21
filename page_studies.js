/* ===== Humbird's design with one study's assumptions at a time =====
   The data is MODEL.tp.studies, from study_assumptions.py (page_data): `mods`, each with a label that starts with its study, the
   lever settings it applies in the page's own vocabulary ({traits, held, plant, vm, device}) or `not_representable` and the reason;
   and `studies`, each study's own reported cost. A ticked box writes the settings into the page's state (SCS) on top of Humbird's
   best estimate (the page's starting point ST.base_key: fed-batch, clean rooms, his financing, hydrolysate, growth factors bought),
   so every chart, the readout and the levers follow. The cost of each modification alone is the page's own engine on a state
   built here (tpPointFor), the path the reader's settings take. `studies` also carries each study's most favourable estimate as
   a kilo of wet cells in 2025 dollars, and `below` the estimates under this model's most favourable case (ST.all_favourable)
   with the assumptions that break a limit. tests/test_study_assumptions.py checks the figures against Python. */
const ST=MODEL.tp.studies;
const ST_MODS=ST.mods.filter(m=>!m.not_representable), ST_NOTES=ST.mods.filter(m=>m.not_representable);
const ST_KEY=ST.base_key, ST_B=ST.base;            // the starting point the modifications are defined on, and its tank, plant and device
function stOnBase(st){ return st.base==="humbird"&&(st.hbKey||"humbird")===ST_KEY; }
function stBaseVM(st){ st.hb.mode=ST_B.vm[1]==="fedbatch"?"fedbatch":"perfusion"; st.vessel=ST_B.vm[0]; st.vmode=null; }
// write lever settings into a state (the page's, or one built here)
function stApplyTo(st,s){
  Object.assign(st.traits,s.traits||{}); Object.assign(st.held,s.held||{});
  if(s.plant) st.hb.plant=s.plant;
  if(s.device) st.device=s.device;
  if(s.vm){ const v=s.vm[0], m=s.vm[1], plain=v==="stirred"&&(m==="perfusion"||m==="fedbatch");
    st.hb.mode=(plain&&m==="fedbatch")?"fedbatch":"perfusion"; st.vessel=v; st.vmode=plain?null:m; }
}
// put the levers a modification moves back to Humbird's design
function stClear(st,s){
  Object.keys(s.traits||{}).forEach(k=>{ delete st.traits[k]; }); Object.keys(s.held||{}).forEach(k=>{ delete st.held[k]; });
  if(s.plant) st.hb.plant=ST_B.plant;
  if(s.device) st.device=ST_B.device;
  if(s.vm) stBaseVM(st);
}
// Humbird's best estimate with a list of modifications (where two set the same lever, the later is used)
function stState(list){
  const st={base:"humbird", hbKey:ST_KEY, choice:Object.assign({},SC.presets[TP_CH0].choice), hb:{plant:ST_B.plant}, traits:{}, held:{},
            device:ST_B.device, clean:tpCleanNone()};
  stBaseVM(st);
  list.forEach(m=>stApplyTo(st,m.settings)); return st;
}
function stLevers(s){ return Object.keys(s.traits||{}).map(k=>"trait:"+k).concat(Object.keys(s.held||{}).map(k=>"held:"+k), ["plant","vm","device"].filter(k=>s[k])); }
function stClash(a,b){ const L=stLevers(a.settings); return stLevers(b.settings).some(k=>L.indexOf(k)>=0); }
const ST_COST={};
function stCostOf(list){ return tpPointFor(stState(list)).point; }
function stAlone(m){ if(!(m.key in ST_COST)) ST_COST[m.key]=stCostOf([m]); return ST_COST[m.key]; }
function stBase(){ if(!("__base" in ST_COST)) ST_COST.__base=stCostOf([]); return ST_COST.__base; }
// what the tests read: the starting point, each modification alone, and all together
function stCosts(){ const rows={}; ST_MODS.forEach(m=>{ rows[m.key]=stCostOf([m]); }); return {base:stCostOf([]), rows:rows, all:stCostOf(ST_MODS)}; }
// is the modification on in the page's state?
function stOn(m){
  if(!stOnBase(SCS)) return false;
  const s=m.settings, same=(a,b)=>a!==undefined&&Math.abs(a-b)<=1e-9*Math.max(1,Math.abs(b));
  if(!Object.keys(s.traits||{}).every(k=>same(SCS.traits[k],s.traits[k]))) return false;
  if(!Object.keys(s.held||{}).every(k=>same(SCS.held[k],s.held[k]))) return false;
  if(s.plant&&SCS.hb.plant!==s.plant) return false;
  if(s.device&&(SCS.device||ST_B.device)!==s.device) return false;
  if(s.vm&&((SCS.vessel||"stirred")!==s.vm[0]||tpVMode()!==s.vm[1])) return false;
  return true;
}
function stToggle(key,on){
  const m=ST_MODS.find(x=>x.key===key); if(!m) return;
  if(!stOnBase(SCS)) tpLoad(ST_KEY);                             // the modifications are defined on Humbird's best estimate
  if(on){ ST_MODS.forEach(o=>{ if(o!==m&&stOn(o)&&stClash(o,m)) stClear(SCS,o.settings); }); stApplyTo(SCS,m.settings); }
  else stClear(SCS,m.settings);
  tpTouched(); tpCommit();
}
function stReset(){ tpLoad(ST_KEY); }
const stUSD=v=>"$"+v.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
function stRender(){
  const host=document.getElementById("tp_studies"); if(!host) return;
  const base=stBase(), onH=stOnBase(SCS), ticked=ST_MODS.filter(stOn), now=pgPointCost();
  const diff=c=>{ const d=c-base; return Math.abs(d)<0.005?"no change":(d>0?"+":"−")+stUSD(Math.abs(d)); };
  let h='<p class="small">Published cost studies give figures from under $2 to over $400,000 a kilo, mainly because they assume different things. '+
    'Each box takes Humbird\'s best estimate of 2021 as this page opens on it, '+stUSD(base)+' a kilo of cells in 2025 dollars, and changes only what one study assumes. '+
    'That starting point is his own published design: fed-batch in 20 m³ tanks with clean rooms, 7.5% interest over 10 years, plant hydrolysate and growth factors bought.</p>'+
    '<p><button type="button" onclick="stReset()">Load Humbird\'s best estimate</button> <span class="small" id="st_now">'+
    (onH?(ticked.length?'With the '+(ticked.length===1?'box':ticked.length+' boxes')+' ticked, the settings on the page now give ':'The settings on the page now give ')+'<b>'+stUSD(now)+'</b> a kilo of cells.'
        :'The page is not on Humbird\'s best estimate now. Ticking a box loads it first.')+'</span></p>';
  h+='<div class="stlist">'+ST_MODS.map(m=>{ const c=stAlone(m), on=stOn(m);
    return '<div class="stmod"><label><input type="checkbox" id="st_'+m.key+'" onchange="stToggle(\''+m.key+'\',this.checked)"'+(on?' checked':'')+'> <b>'+pgEsc(m.label)+'</b></label>'+
      '<p class="small">Alone on Humbird\'s best estimate: <b>'+stUSD(c)+'</b> a kilo of cells ('+diff(c)+'). The study itself reports: '+pgEsc(m.own)+'.<br>'+
      pgEsc(m.text)+' <span class="alt">'+pgEsc(m.solid)+'</span></p></div>'; }).join("")+'</div>';
  h+='<p class="small">Ticking a box unticks any box that sets the same lever. Each box moves the levers in the side bar, so you can go on from there by hand.</p>';
  h+='<h4>Assumptions this page cannot apply, or that change nothing</h4><ul class="small">'+ST_NOTES.map(m=>'<li><b>'+pgEsc(m.label)+'.</b> '+pgEsc(m.text)+' '+pgEsc(m.reason)+'</li>').join("")+'</ul>';
  // each study's own most favourable estimate against this model's most favourable case
  const fav=ST.all_favourable, nb=ST.below.length;
  h+='<h4>Published estimates below this model\'s most favourable case, and why</h4>'+
    '<p class="small" id="st_fav">This model\'s most favourable case costs <b>'+stUSD(fav)+'</b> a kilo of cells: every lever at the most favourable value among this model\'s own, Humbird\'s and what any of these studies assumes without breaking a limit. '+
    'The limits are: cells cannot be built from fewer nutrients than they hold and burn; a culture stops flowing when cells are about a quarter of its volume; a tank passes only so much oxygen and CO₂; waste builds up to what the cells tolerate; no animal cell line has been measured doubling faster than about 15 hours; and a plant has to be repaid with interest. '+
    (nb?'No published estimate that respects those limits is below '+stUSD(fav)+'. '+(nb===1?'One estimate is':nb+' estimates are')+' below it:':'No published estimate is below it.')+'</p>';
  if(nb) h+='<div class="scrollx"><table class="sctab stack" id="st_below"><thead><tr><th>Study</th><th>Its estimate</th><th>What it assumes</th><th>The limit it breaks</th></tr></thead><tbody>'+
    ST.below.map(b=>b.assumptions.map((a,i)=>'<tr>'+(i===0?'<td data-label="Study" rowspan="'+b.assumptions.length+'"><b>'+pgEsc(b.name)+'</b></td><td data-label="Its estimate" rowspan="'+b.assumptions.length+'">'+pgEsc(b.published)+
        '; '+stUSD(b.today)+' a kilo of wet cells in 2025 dollars'+(b.inside?'. With these assumptions brought inside the limits ('+pgEsc(b.inside_how)+'), this page\'s engine gives '+stUSD(b.inside)+' a kilo':'')+'</td>':'')+
      '<td data-label="What it assumes">'+pgEsc(a.assumption)+' ('+pgEsc(a.ref)+')</td><td data-label="The limit it breaks"><b>'+pgEsc(a.limit.charAt(0).toUpperCase()+a.limit.slice(1))+'.</b> '+pgEsc(a.why)+'</td></tr>').join("")).join("")+'</tbody></table></div>';
  h+='<h4>What each study itself reports</h4><div class="scrollx"><table class="sctab stack"><thead><tr><th>Study</th><th>What it models</th><th>Its reported cost</th><th>A cost of what</th><th>Its lowest estimate, a kilo of wet cells, 2025 dollars</th><th>Why it differs from the figure here</th></tr></thead><tbody>'+
    ST.studies.map(s=>'<tr><td data-label="Study"><b>'+pgEsc(s.name)+'</b></td><td data-label="What it models">'+pgEsc(s.system)+'</td><td data-label="Its reported cost">'+pgEsc(s.cost)+
      '</td><td data-label="A cost of what">'+pgEsc(s.basis)+'</td><td data-label="Lowest estimate, 2025 dollars">'+(s.today===null||s.today===undefined?'None: '+pgEsc(s.today_how):'<b>'+stUSD(s.today)+'</b> (from '+pgEsc(s.published)+': '+pgEsc(s.today_how)+')')+
      '</td><td data-label="Why it differs">'+pgEsc(s.explains)+'</td></tr>').join("")+'</tbody></table></div>';
  host.innerHTML=h;
}
