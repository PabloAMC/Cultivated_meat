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
/* ---------- starting sets: every assumption of one study that the page has a lever for, together on Humbird's best estimate
   (study_assumptions.SETS). The side bar's buttons load one; the cost is the page's own engine with those settings. ---------- */
const ST_SETS=ST.sets||[];
function stSet(k){ return ST_SETS.find(e=>e.key===k)||null; }
function stLoadSet(k){ const e=stSet(k); if(!e) return;
  tpLoad(ST_KEY,true); stApplyTo(SCS,e.settings); SCS.ref=null; SCS.set=k; SCS.fromSet=k; tpCommit(); }
function stSetCosts(){ const o={}; ST_SETS.forEach(e=>{ o[e.key]=stCostOf([e]); }); return o; }      // what the tests read
const stUSD=v=>"$"+v.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
function stRender(){
  const host=document.getElementById("tp_studies"); if(!host) return;
  const base=stBase(), onH=stOnBase(SCS), ticked=ST_MODS.filter(stOn), now=pgPointCost();
  const diff=c=>{ const d=c-base; return Math.abs(d)<0.005?"no change":(d>0?"+":"−")+stUSD(Math.abs(d)); };
  let h='<p class="small">Published cost studies give figures from under $2 to over $400,000 a kilo, mainly because they assume different things. '+
    'They report costs of production, before transport and the shop\'s margin (Garrison 2022 also counts packing and delivery), so compare them with the production cost on this page, not with its price in the shop. '+
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

/* ---------- plant against running costs: each study as it reports it and as this page's model gives its set (the owner,
   2026-11-24: "an interactive plot depicting the OPEX vs CAPEX of the different TEAs and the limit"). "Plant" is the yearly
   payment with interest, maintenance and insurance, a kilo; "running" is everything else. Hollow: the study's own figures
   (study_assumptions.SPLITS, 2025 dollars); filled: its starting set on this page's engine; a line joins the two. The limits:
   the nutrient floor (running costs cannot fall below what the cells eat) and the all-favourable case. Click a filled point
   to load its set. ---------- */
const ST_SPL={};                     // the sets' plant and running costs on this page's engine (they do not depend on the reader)
function stSplitOf(list){ const r=tpPointFor(stState(list)).res; return {plant:r.capital, running:r.total-r.capital, total:r.total}; }
function stSplits(){ if(!ST_SPL.__done){ ST_SPL.humbird_best=stSplitOf([]); ST_SETS.forEach(e=>{ ST_SPL[e.key]=stSplitOf([e]); }); ST_SPL.__done=true; } return ST_SPL; }
let stPvrSel=null;
function stPvrPick(k){ stPvrStudy=k; if(k==="humbird_best") tpLoad("humbird_best"); else stLoadSet(k); }
/* ---------- how one study's set differs from the study (the owner, 2026-11-24: "explain exactly how our assumptions differ for
   the concrete study we are analyzing"): its plant and running costs as it reports them and on this model, and every assumption
   the set does not keep as the study has it (study_assumptions.audit_rows, every row but "Kept"). ---------- */
let stPvrStudy=null;
function stPvrSetStudy(k){ stPvrStudy=k; stPvrDiff(); }
function stPvrDiff(){
  const host=document.getElementById("st_pvr_diff"); if(!host||!ST_SETS.length) return;
  const k=stPvrStudy||(SCS.set&&stSet(SCS.set)?SCS.set:"pasitka"), e=stSet(k)||ST_SETS[0], S=stSplits(), m=S[e.key], rep=ST.splits.find(x=>x.set===e.key);
  const usd=v=>"$"+(v>=100?v.toFixed(0):v.toFixed(2));
  const sel='<label class="small">Study: <select onchange="stPvrSetStudy(this.value)">'+ST_SETS.map(x=>'<option value="'+x.key+'"'+(x.key===e.key?' selected':'')+'>'+pgEsc(x.label)+'</option>').join("")+'</select></label>';
  const nums=_table2(["","Plant","Running","In all","Counts"],[
      ["As the study reports it"].concat(rep?[usd(rep.plant),usd(rep.running),usd(rep.plant+rep.running),pgEsc(rep.basis)]:["not published","","",""]),
      ["Its set on this page's model",usd(m.plant),usd(m.running),usd(m.total),"a kilo of cells"]]);
  const diff=e.audit_rows.filter(r=>r.why!=="Kept");
  host.innerHTML='<div class="pvrdiff"><p class="limt">How the set differs from the study '+sel+'</p>'+nums+
    (rep&&!rep.same?'<p class="small">The study\'s split is for a different case from the set\'s: '+pgEsc(rep.how)+'.</p>':'')+
    '<p class="small">'+diff.length+' of its '+e.audit_rows.length+' listed assumptions are not kept as the study has them; the other '+(e.audit_rows.length-diff.length)+' are. Anything not listed is Humbird\'s best estimate.</p>'+
    _table2(["Assumption","The study","The set","Why"],diff.map(r=>[pgEsc(r.item),pgEsc(r.study),pgEsc(r.used),'<b>'+pgEsc(r.why)+'</b>']))+
    '<p class="small"><a href="#" onclick="stLoadSet(\''+e.key+'\');return false">Load this set</a> to see it on the rest of the page; the side bar then lists every assumption, the kept ones too.</p></div>'; }
function _table2(head,rows){ return '<div class="scrollx"><table class="sctab vt"><thead><tr>'+head.map(h=>'<th>'+h+'</th>').join("")+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+r.map(c=>'<td>'+c+'</td>').join("")+'</tr>').join("")+'</tbody></table></div>'; }
function stPvrHover(i){ stPvrSel=i; const e=document.getElementById("st_pvr_read"); if(e&&STPVR[i]) e.innerHTML=STPVR[i].say; }
let STPVR=[];
function stPvrDraw(f){
  const svg=document.getElementById("st_pvr"); if(!svg||!ST.splits) return;
  const W=Math.max(300,pgWidth("st_pvr_plot",860)), small=W<560, fs=small?10.5:12, H=small?360:440;
  const L=small?44:58, R=W-(small?8:16), T=14, B=H-(small?40:46);
  const x0=0.5, x1=60, y0=1.5, y1=80, lx=v=>L+(Math.log(Math.min(x1,Math.max(x0,v)))-Math.log(x0))/(Math.log(x1)-Math.log(x0))*(R-L),
        ly=v=>B-(Math.log(Math.min(y1,Math.max(y0,v)))-Math.log(y0))/(Math.log(y1)-Math.log(y0))*(B-T);
  const usd=v=>"$"+(v>=100?v.toFixed(0):v>=10?v.toFixed(1):v.toFixed(2));
  const S=stSplits(), fl=C.FEEDSTOCK_FLOOR, af=ST.af_split, res=f.cloud.res, me={plant:res.capital, running:res.total-res.capital};
  let g='<defs><pattern id="st_pvr_h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="var(--axis)" stroke-width="1.5"/></pattern></defs>';
  // grid and axes
  [0.5,1,2,5,10,20,50].forEach(v=>{ const x=lx(v); g+='<line x1="'+x+'" x2="'+x+'" y1="'+T+'" y2="'+B+'" stroke="var(--grid)"/><text x="'+x+'" y="'+(B+fs+4)+'" text-anchor="middle" font-size="'+fs+'" fill="var(--ink2)">$'+v+'</text>'; });
  [2,5,10,20,50].forEach(v=>{ const y=ly(v); g+='<line x1="'+L+'" x2="'+R+'" y1="'+y+'" y2="'+y+'" stroke="var(--grid)"/><text x="'+(L-5)+'" y="'+(y+4)+'" text-anchor="end" font-size="'+fs+'" fill="var(--ink2)">$'+v+'</text>'; });
  g+='<text x="'+((L+R)/2)+'" y="'+(H-4)+'" text-anchor="middle" font-size="'+fs+'" fill="var(--ink2)">Plant: payment with interest, maintenance and insurance, $ a kilo (log scale)</text>';
  g+='<text transform="translate('+(small?11:14)+','+((T+B)/2)+') rotate(-90)" text-anchor="middle" font-size="'+fs+'" fill="var(--ink2)">Running: medium, labour, energy, supplies, $ a kilo (log scale)</text>';
  // below the nutrient floor: impossible
  g+='<rect x="'+L+'" y="'+ly(fl)+'" width="'+(R-L)+'" height="'+(B-ly(fl))+'" fill="url(#st_pvr_h)" opacity="0.5"/>';
  g+='<line x1="'+L+'" x2="'+R+'" y1="'+ly(fl)+'" y2="'+ly(fl)+'" stroke="var(--ink2)" stroke-width="1.5"/>';
  g+='<text x="'+(R-4)+'" y="'+(ly(fl)+fs+3)+'" text-anchor="end" font-size="'+fs+'" fill="var(--ink)">below $'+fl.toFixed(2)+' of running cost: less than the cells eat</text>';
  // lines of equal total cost
  const iso=(tot,style,lab,at)=>{ let d="", first=true; for(let i=0;i<=80;i++){ const xp=Math.exp(Math.log(x0)+i/80*(Math.log(Math.min(x1,tot-y0))-Math.log(x0))), yp=tot-xp;
      if(xp>=tot||yp<y0) continue; d+=(first?"M":"L")+lx(xp).toFixed(1)+","+ly(yp).toFixed(1); first=false; }
    if(!d) return ""; const lxp=Math.max(x0*1.08,Math.min(tot*(at||0.03),x1)), lyp=tot-lxp;
    return '<path d="'+d+'" fill="none" '+style+'/>'+(lab&&lyp>y0&&lyp<y1?'<text x="'+(lx(lxp)+3)+'" y="'+(ly(lyp)-4)+'" font-size="'+(fs-1)+'" fill="'+(at?'#D85A30':'var(--muted)')+'">'+lab+'</text>':''); };
  // the totals that long-run shares of all meat need at the reader's shopper setting (the owner, 2026-11-24: "Can we also
  // report the 5%, 10%, 25% and 50%?"); a share no cost reaches, or one needing a total below the chart, is listed under it
  const SH=[1,5,10,25,50].map(p=>({p:p, t:tpCostFor(p,f.buyers)})), drawn=SH.filter(o=>o.t!==null&&o.t>x0+y0);
  const nearShare=t=>drawn.some(o=>Math.abs(Math.log(t/o.t))<0.35);      // a share line's label takes the place of a grey curve's near it
  [5,10,20,50].forEach(t=>{ g+=iso(t,'stroke="var(--axis)" stroke-width="1"',nearShare(t)?"":"$"+t+" in all"); });
  drawn.forEach(o=>{ g+=iso(o.t,'stroke="#D85A30" stroke-width="1.5" stroke-dasharray="5 4"',o.p+"%: "+tpUSDk(o.t)+" in all",0.031); });
  const sl=document.getElementById("st_pvr_shares");
  if(sl) sl.innerHTML="<b>The total a long-run share of "+pgEsc(tpRegionMeat())+" needs</b>, with "+tpPctB(f.buyers)+" of meat buyers picking it at the same price (the dashed lines): "+
    SH.map(o=>o.p+"%, "+(o.t===null?"not reached at any cost down to $0.50":tpUSDk(o.t)+" a kilo of cells"+(o.t<=x0+y0?" (below the chart)":""))).join("; ")+
    ". Move the shoppers' setting in the side bar and they move.";
  // the points: each study as it reports it (hollow) and its set on this page's model (filled), joined
  STPVR=[]; let pts="", labs=[], allDots=[];
  const add=(p,kind,label,say,click)=>{ const i=STPVR.length; STPVR.push({say:say}); const x=lx(p.plant), y=ly(p.running), off=p.plant>x1||p.running>y1; allDots.push({x:x-7,y:y-7,w:14,h:14});
    const ev=' onmouseenter="stPvrHover('+i+')" onfocus="stPvrHover('+i+')"'+(click?' onclick="'+(kind==="rep"?"stPvrSetStudy":"stPvrPick")+'(\''+click+'\')" style="cursor:pointer"':'')+' tabindex="0"';
    if(kind==="rep") pts+='<circle cx="'+x+'" cy="'+y+'" r="5.5" fill="var(--card)" stroke="var(--ink2)" stroke-width="1.8"'+ev+'><title>'+pgEsc(say.replace(/<[^>]+>/g,""))+'</title></circle>';
    else if(kind==="set") pts+='<circle cx="'+x+'" cy="'+y+'" r="6" fill="var(--accent)"'+ev+'><title>'+pgEsc(say.replace(/<[^>]+>/g,""))+'</title></circle>';
    else if(kind==="af") pts+='<path d="M'+x+','+(y-8)+'L'+(x+8)+','+y+'L'+x+','+(y+8)+'L'+(x-8)+','+y+'Z" fill="var(--ink)"'+ev+'><title>'+pgEsc(say.replace(/<[^>]+>/g,""))+'</title></path>';
    else pts+='<circle cx="'+x+'" cy="'+y+'" r="8" fill="none" stroke="#D85A30" stroke-width="3"'+ev+'><title>'+pgEsc(say.replace(/<[^>]+>/g,""))+'</title></circle>';
    if(label) labs.push({x:x,y:y,t:label+(off?" (off the scale)":""),kind:kind}); return i; };
  const setName={humbird_best:"Humbird's best estimate (2021)"}; ST_SETS.forEach(e=>{ setName[e.key]=e.name; });
  const setLab={humbird_best:"Humbird best"}; ST_SETS.forEach(e=>{ setLab[e.key]=e.label.replace("Humbird 2021, ","Humbird "); });
  const done={};
  ST.splits.forEach(s=>{ const m=s.set?S[s.set]:null;
    if(m){ g+='<line x1="'+lx(s.plant)+'" y1="'+ly(s.running)+'" x2="'+lx(m.plant)+'" y2="'+ly(m.running)+'" stroke="var(--ink2)" stroke-width="1" stroke-dasharray="2 3" opacity="0.8"/>'; }
    add(s,"rep",m?null:s.label.replace(" Ltd 2024"," 2024"),"<b>"+pgEsc(s.label)+", as the study reports it</b> ("+pgEsc(s.basis)+", 2025 dollars): plant "+usd(s.plant)+", running "+usd(s.running)+", "+usd(s.plant+s.running)+" in all. "+pgEsc(s.how.charAt(0).toUpperCase()+s.how.slice(1))+"."+(m?" The filled point joined to it is its starting set on this page's model. Click to compare the two below.":""),m&&s.set!=="humbird_best"?s.set:null); });
  Object.keys(S).filter(k=>k!=="__done").forEach(k=>{ const m=S[k], rep=ST.splits.find(s=>s.set===k);
    add(m,"set",setLab[k],"<b>"+pgEsc(setName[k])+", on this page's model</b>: plant "+usd(m.plant)+", running "+usd(m.running)+", "+usd(m.total)+" a kilo of cells."+
      (rep?" The study's own figures ("+usd(rep.plant+rep.running)+") are the hollow point joined to it"+(rep.same?"":"; they are for a different case, as the note under the buttons explains")+".":" The study publishes no split.")+" Click to load it.",k); });
  add(af,"af","all-favourable","<b>The all-favourable example</b>: every lever at its most favourable value within the model's limits. Plant "+usd(af.plant)+", running "+usd(af.running)+", "+usd(af.total)+" a kilo of cells. No published estimate that respects the limits is below it.",null);
  const onSet=Object.keys(S).filter(k=>k!=="__done").find(k=>Math.abs(S[k].plant-me.plant)<1e-6*Math.max(1,me.plant)&&Math.abs(S[k].running-me.running)<1e-6*Math.max(1,me.running));
  if(onSet){ const l=labs.find(x=>x.kind==="set"&&x.t===setLab[onSet]); if(l) l.t+=" (your settings)"; }
  add(me,"me",onSet?null:"your settings","<b>Your settings</b>: plant "+usd(me.plant)+", running "+usd(me.running)+", "+usd(res.total)+" a kilo of cells.",null);
  g+=pts;
  // labels beside the points: right, left, above or below, the first that overlaps no other label or point
  const placed=[], dots=allDots, hit=(r,q)=>r.x<q.x+q.w&&r.x+r.w>q.x&&r.y<q.y+q.h&&r.y+r.h>q.y;
  labs.forEach(l=>{ const w=tpTextW(l.t,fs-1), h=fs;
    const cands=[[l.x+9,l.y-h/2],[l.x-9-w,l.y-h/2],[l.x-w/2,l.y-9-h],[l.x-w/2,l.y+9],[l.x+9,l.y-h*1.5],[l.x+9,l.y+h*0.5],[l.x-9-w,l.y-h*1.5],[l.x-9-w,l.y+h*0.5]]
      .map(c=>({x:Math.max(L+2,Math.min(R-w-2,c[0])),y:c[1],w:w,h:h}));
    const ok=c=>!placed.some(p=>hit(c,p))&&!dots.some(d=>hit(c,d)), c=cands.find(ok)||cands[0]; placed.push(c);
    g+='<text x="'+c.x.toFixed(1)+'" y="'+(c.y+h-2).toFixed(1)+'" font-size="'+(fs-1)+'" fill="'+(l.kind==="set"?"var(--accent)":l.kind==="me"?"#D85A30":l.kind==="rep"?"var(--ink2)":"var(--ink)")+'"'+(l.kind==="af"||l.kind==="me"?' font-weight="700"':'')+'>'+pgEsc(l.t)+'</text>'; });
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H); svg.innerHTML=g;
  const rd=document.getElementById("st_pvr_read"); if(rd&&(stPvrSel===null||!STPVR[stPvrSel])) rd.innerHTML="Point at a dot for its figures and where they come from; click a filled dot to load that set.";
  else if(rd) rd.innerHTML=STPVR[stPvrSel].say;
  stPvrDiff();
  const alt=document.getElementById("st_pvr_alt"); if(alt) alt.textContent="Plant against running costs of a kilo of cells. As each study reports it: "+ST.splits.map(s=>s.label+" "+usd(s.plant)+" and "+usd(s.running)).join("; ")+
    ". On this page's model: "+Object.keys(S).filter(k=>k!=="__done").map(k=>setLab[k]+" "+usd(S[k].plant)+" and "+usd(S[k].running)).join("; ")+". All-favourable example "+usd(af.plant)+" and "+usd(af.running)+"; your settings "+usd(me.plant)+" and "+usd(me.running)+". Running costs cannot fall below $"+fl.toFixed(2)+".";
}
