/* ===== scenarios: the switches, the presets and what to prioritise =====
   A line-for-line mirror of scenarios.py (run, design, priorities, interactions); tests/run_parity.py checks the two agree.
   Included into the page's script by build_interactive.py. Everything is computed by floorExplore (the mirror of
   floor_physics.explore) from the settings of the switches in MODEL.sc; nothing here is typed in by hand. */
const SC=MODEL.sc;
const SCS={choice:Object.assign({},SC.presets[SC.start].choice), preset:SC.start, src:"scenario"};
const scCache={};
let scPair=null;                                   // the two switches shown against each other
function scSwitch(k){ return SC.switches.find(s=>s.key===k); }
function scSetting(k,v){ return scSwitch(k).settings.find(t=>t.key===v); }
function scSame(a,b){ return SC.keys.every(k=>a[k]===b[k]); }
function scPresetOf(ch){ return SC.order.find(k=>scSame(SC.presets[k].choice,ch))||null; }
function scParams(ch){          // the explore arguments of a choice (mirror of scenarios.explore_kwargs)
  const p={doubling_h:24,mass_pg:3000,vessel_m3:20,plant:"sanitary",mode:"perfusion",charge:C.fx.charge_mature};
  SC.switches.forEach(sw=>Object.assign(p,scSetting(sw.key,ch[sw.key]).p));
  if(p.plantKey){ if(p.plantKey==="lean"){ p.plant="sanitary"; p.items=C.fx.plant_items.lean; }
    else p.plant=(p.plantKey==="sterile"?"sanitary":p.plantKey); delete p.plantKey; }
  return p;
}
function scEval(ch){
  const k=SC.keys.map(x=>ch[x]).join("|");
  if(!(k in scCache)) scCache[k]=floorExplore(scParams(ch));
  return scCache[k];
}
function scShare(cost,region){      // long-run share of meat sold by weight (%), at the current demand settings
  region=region||"global";
  const s=Object.assign({},state,{region:region,income:C.REGION_INCOME[region],cost_override:cost});
  return penetration(s).tv*100;
}
// the cheapest pair of tank settings (tricks, shape) whose loop a pH-safe pass rate dense cultures have taken allows
function scDesign(ch){
  let best=null;
  scSwitch("tricks").settings.forEach(a=>scSwitch("shape").settings.forEach(b=>{
    const c=Object.assign({},ch,{tricks:a.key,shape:b.key}), r=scEval(c), d=r.column;
    if(d && (d.ph_vs_safe>1+1e-9 || !d.passes_tested)) return;
    if(best===null || r.total<best[0]-1e-12) best=[r.total,c];
  }));
  return best[1];
}
function scNeeds(ch){            // [switch name, setting label, tag], hardest need first
  const rows=SC.keys.map(k=>[scSwitch(k).name,scSetting(k,ch[k]).label,scSetting(k,ch[k]).tag]);
  return rows.sort((a,b)=>SC.tags.indexOf(b[2])-SC.tags.indexOf(a[2]));
}
function scHardest(ch){ return SC.keys.map(k=>scSetting(k,ch[k]).tag).reduce((a,b)=>SC.tags.indexOf(b)>SC.tags.indexOf(a)?b:a); }
function scPriorities(ch,withShare){
  const base=scEval(ch).total, bsh=withShare?scShare(base):0;
  const rows=SC.switches.map(sw=>{
    const costs={}; sw.settings.forEach(t=>{ costs[t.key]=scEval(Object.assign({},ch,{[sw.key]:t.key})).total; });
    let kb=sw.settings[0].key, kw=kb;
    sw.settings.forEach(t=>{ if(costs[t.key]<costs[kb]) kb=t.key; if(costs[t.key]>costs[kw]) kw=t.key; });
    const row={switch:sw.key,name:sw.name,now:ch[sw.key],costs:costs,best:kb,worst:kw,d_best:costs[kb]-base,d_worst:costs[kw]-base};
    if(withShare){ row.share_best=scShare(costs[kb])-bsh; row.share_worst=scShare(costs[kw])-bsh; }
    return row;
  });
  return rows.sort((a,b)=>(b.d_worst-b.d_best)-(a.d_worst-a.d_best));
}
function scInteractions(ch,top,minGap){
  top=top||4; minGap=(minGap===undefined?0.25:minGap);
  const base=scEval(ch).total, best={};
  SC.switches.forEach(sw=>{
    const c={}; sw.settings.forEach(t=>{ c[t.key]=scEval(Object.assign({},ch,{[sw.key]:t.key})).total; });
    let k=sw.settings[0].key; sw.settings.forEach(t=>{ if(c[t.key]<c[k]) k=t.key; });
    best[sw.key]=[k,base-c[k]];
  });
  const out=[];
  SC.keys.forEach((a,i)=>SC.keys.slice(i+1).forEach(b=>{
    const [ka,ga]=best[a], [kb,gb]=best[b];
    if(ka===ch[a]||kb===ch[b]) return;
    const both=scEval(Object.assign({},ch,{[a]:ka,[b]:kb})).total, onlyB=scEval(Object.assign({},ch,{[b]:kb})).total;
    const gaWithB=onlyB-both, gap=gaWithB-ga;
    if(Math.abs(gap)<minGap) return;
    const sa=scSwitch(a), sb=scSwitch(b), la=scSetting(a,ka).label, lb=scSetting(b,kb).label;
    const how=gap<0?"they overlap: one does part of the other’s job":"they reinforce each other";
    out.push({a:a,b:b,gap:gap,ga:ga,ga_with_b:gaWithB,
      text:sa.name+": “"+la+"” would save $"+ga.toFixed(1)+" a kilo as things stand, and $"+gaWithB.toFixed(1)+
           " if "+sb.name.toLowerCase()+" were “"+lb+"”: "+how+"."});
  }));
  return out.sort((x,y)=>Math.abs(y.gap)-Math.abs(x.gap)).slice(0,top);
}

/* ---------- the page ---------- */
const scMoney=(v,d)=>"$"+v.toFixed(d===undefined?1:d);
const scPts=v=>(v>=0?"+":"−")+Math.abs(v).toFixed(1)+" pts";
function scTagChip(t){ const cls=t==="genetic engineering"?"ge":t==="selection or adaptation"?"sel":t==="feed or process"?"feed":"none";
  return '<span class="tagchip '+cls+'">'+SC.tag_plain[t]+'</span>'; }
function scBuild(){
  const host=document.getElementById("sc_switches"); if(!host) return;
  host.innerHTML="";
  SC.switches.forEach(sw=>{
    const d=document.createElement("div"); d.className="ctl scsw";
    d.innerHTML='<label><span class="nm">'+sw.name+'</span></label><select id="sc_sel_'+sw.key+'" onchange="scPick(\''+sw.key+'\',this.value)">'+
      sw.settings.map(t=>'<option value="'+t.key+'">'+t.label+'</option>').join("")+'</select>'+
      '<p class="fxn" id="sc_note_'+sw.key+'"></p>';
    host.appendChild(d); });
  const pr=document.getElementById("sc_presets"); if(pr){
    pr.innerHTML=SC.order.map(k=>'<button class="btn scbtn" id="sc_pre_'+k+'" onclick="scApply(\''+k+'\')">'+SC.presets[k].name+'</button>').join("")+
      '<button class="btn scbtn" id="sc_pre_reported" onclick="scApply(\'reported\')">As a company reports</button>'; }
  const a=document.getElementById("sc_ga"), b=document.getElementById("sc_gb");
  [a,b].forEach(sel=>{ if(sel) sel.innerHTML=SC.switches.map(sw=>'<option value="'+sw.key+'">'+sw.name+'</option>').join(""); });
}
function scApply(key){
  if(key==="reported"){ SCS.src="reported"; SCS.preset=null; }
  else { SCS.src="scenario"; SCS.choice=Object.assign({},SC.presets[key].choice); SCS.preset=key; }
  scCommit();
}
function scApplyChoice(o){ SCS.choice=Object.assign({},SC.presets[SC.start].choice,o); SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit();
  const e=document.getElementById("decide"); if(e&&e.scrollIntoView) e.scrollIntoView({behavior:"smooth",block:"start"}); }
function scPick(k,v){ SCS.choice[k]=v; SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scDesignNow(){ SCS.choice=scDesign(SCS.choice); SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scCommit(){
  state.cost_override=(SCS.src==="reported"?null:scEval(SCS.choice).total);
  scSyncRail(); recompute();
}
// the three cost sliders and the clean-room toggle describe the process one company reports; they are live only then
function scSyncRail(){
  const reported=(SCS.src==="reported");
  ["media_price","efficiency","overhead"].forEach(k=>{ const e=document.getElementById("r_"+k); if(e) e.disabled=!reported; });
  const cb=document.getElementById("t_cleanroom"); if(cb) cb.disabled=!reported;
  const n=document.getElementById("sc_railnote");
  if(n) n.innerHTML=reported?"The cost comes from the three sliders below: the process one company reports.":
    "The cost comes from the scenario chosen above (<b>"+(SCS.preset?SC.presets[SCS.preset].name:"your own switches")+"</b>). The medium price, plant cost and cell efficiency sliders apply only to “As a company reports”.";
  const sel=document.getElementById("sc_railsel"); if(sel) sel.value=reported?"reported":(SCS.preset||"own");
}
function scRailBuild(){
  const sel=document.getElementById("sc_railsel"); if(!sel) return;
  sel.innerHTML=SC.order.map(k=>'<option value="'+k+'">'+SC.presets[k].name+'</option>').join("")+
    '<option value="reported">As a company reports</option><option value="own" disabled>Your own switches</option>';
  sel.onchange=()=>scApply(sel.value);
}
function scResultHTML(ch,r){
  const markup=state.markup_add, cost=r.total, retail=cost+markup, R=retail/(C.p_conv_anchor*state.meat_tax);
  const world=scShare(cost,"global"), us=scShare(cost,"us"), eu=scShare(cost,"eu");
  const lim=(SC.limit_plain[r.limit]||r.limit).replace("CO2","CO₂");
  const med=(SC.medium_plain[r.medium_set_by]||r.medium_set_by);
  const need=scNeeds(ch).filter(x=>x[2]!=="nothing new");
  const strip='<span class="scbig">'+scMoney(cost)+'<span> a kilo of cells</span></span> &nbsp; <b>'+scMoney(retail,0)+'</b> in the shop ('+R.toFixed(2)+
    '&times; everyday meat) &nbsp; <b>'+world.toFixed(1)+'%</b> of world meat in the long run';
  const el0=document.getElementById("sc_strip"); if(el0) el0.innerHTML=strip;
  let h='<p>Long-run share of world meat: about <b>'+world.toFixed(1)+'%</b> by weight (US '+us.toFixed(1)+'%, Europe '+eu.toFixed(1)+'%). '+
    'The shop price adds '+scMoney(markup,0)+' a kilo for processing, packaging and retail margin; everyday meat costs $'+(C.p_conv_anchor*state.meat_tax).toFixed(0)+' a kilo.</p>'+
    '<p>The tank holds '+r.density.toFixed(0)+' g of cells a litre, limited by <b>'+lim+'</b>, and works '+(r.uptime*100).toFixed(0)+'% of the year. '+
    'Each kilo of cells needs '+r.medium_l.toFixed(0)+' litres of medium, set by <b>'+med+'</b>.</p>';
  if(need.length){ h+='<p class="scneed"><b>What has to go right:</b> '+scTagChip(scHardest(ch))+' at the hardest. '+
    need.map(x=>x[1]+' <i>('+x[2]+')</i>').join("; ")+'.</p>'; }
  const d=r.column;
  if(d && (d.ph_vs_safe>1+1e-9 || !d.passes_tested))
    h+='<p class="scwarn">This tank design pumps the culture through the column harder than the checks allow ('+d.passes.toFixed(0)+
       ' passes an hour; dense cultures have taken up to 15–24, and the alkaline culture in the loop is '+d.ph_vs_safe.toFixed(1)+' times the exposure judged safe). '+
       'Treat the cost as optimistic, or use the button below to pick the cheapest design that passes.</p>';
  if(SCS.src==="reported") h+='<p class="scwarn">The charts below are using the process one company reports, not these switches.</p>';
  return h;
}
function scTornadoSVG(rows,base){
  const W=680,L=176,R=14,rh=40,top=18,H=top+rows.length*rh+8;
  const ext=rows.map(r=>Math.max(-r.d_best,r.d_worst)).sort((a,b)=>b-a);
  const mx=Math.max(1,Math.min(ext[0],Math.max(6,2*(ext[1]||0))));        // one huge bar must not flatten the rest: it is clipped and marked
  const mid=L+(W-L-R)/2, X=d=>mid+d/mx*((W-L-R)/2-90);
  const esc=t=>String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;");
  let g='<svg viewBox="0 0 '+W+' '+H+'" width="100%" style="max-width:'+W+'px;min-width:520px" role="img" aria-label="What each switch is worth">';
  g+='<line x1="'+mid+'" x2="'+mid+'" y1="'+(top-6)+'" y2="'+(H-4)+'" stroke="#444"/>';
  g+='<text x="'+mid+'" y="11" font-size="10" text-anchor="middle" fill="#444">now: '+scMoney(base)+'</text>';
  rows.forEach((r,i)=>{
    const y=top+i*rh, sw=scSwitch(r.switch);
    g+='<text x="'+(L-8)+'" y="'+(y+12)+'" font-size="11" text-anchor="end" fill="#1a1a1a">'+esc(r.name)+'</text>';
    g+='<text x="'+(L-8)+'" y="'+(y+25)+'" font-size="9" text-anchor="end" fill="#777">now: '+esc(scSetting(r.switch,r.now).short)+'</text>';
    if(r.d_best<-0.005){ const x0=X(Math.max(r.d_best,-mx));
      g+='<rect x="'+x0+'" y="'+(y+2)+'" width="'+(mid-x0)+'" height="14" fill="#029E73" opacity="0.85"/>';
      g+='<text x="'+(x0-3)+'" y="'+(y+13)+'" font-size="10" text-anchor="end" fill="#029E73">−$'+Math.abs(r.d_best).toFixed(1)+(r.share_best!==undefined?' ('+scPts(r.share_best)+')':'')+'</text>';
      g+='<text x="'+(mid-4)+'" y="'+(y+28)+'" font-size="9" text-anchor="end" fill="#777">'+esc(scSetting(r.switch,r.best).short)+'</text>'; }
    if(r.d_worst>0.005){ const clip=r.d_worst>mx*1.001, x1=X(Math.min(r.d_worst,mx*1.0));
      g+='<rect x="'+mid+'" y="'+(y+2)+'" width="'+(x1-mid)+'" height="14" fill="#CC3311" opacity="0.85"/>'+(clip?'<rect x="'+(x1-6)+'" y="'+(y+2)+'" width="6" height="14" fill="#fff" opacity="0.7"/>':'');
      g+='<text x="'+(x1+3)+'" y="'+(y+13)+'" font-size="10" fill="#CC3311">+$'+r.d_worst.toFixed(1)+(clip?' (off the scale)':'')+(r.share_worst!==undefined?' ('+scPts(r.share_worst)+')':'')+'</text>';
      g+='<text x="'+(mid+4)+'" y="'+(y+28)+'" font-size="9" fill="#777">'+esc(scSetting(r.switch,r.worst).short)+'</text>'; }
  });
  return g+'</svg>';
}
function scGridHTML(ch,a,b){
  const sa=scSwitch(a), sb=scSwitch(b), base=scEval(ch).total;
  const cost=sa.settings.map(i=>sb.settings.map(j=>scEval(Object.assign({},ch,{[a]:i.key,[b]:j.key})).total));
  const all=[].concat.apply([],cost), mn=Math.min.apply(null,all), mx=Math.max.apply(null,all);
  const col=v=>{ const t=(v-mn)/Math.max(1e-9,mx-mn); const r=Math.round(214+(255-214)*t), g=Math.round(238-(238-214)*t), bl=Math.round(224-(224-200)*t); return "rgb("+r+","+g+","+bl+")"; };
  let h='<table class="scgrid"><thead><tr><th>'+sa.name+' ↓ &nbsp; '+sb.name+' →</th>'+sb.settings.map(j=>'<th>'+j.short+'</th>').join("")+'</tr></thead><tbody>';
  sa.settings.forEach((i,ii)=>{ h+='<tr><th>'+i.short+'</th>'+sb.settings.map((j,jj)=>{
    const cur=(ch[a]===i.key&&ch[b]===j.key);
    return '<td style="background:'+col(cost[ii][jj])+(cur?';outline:2px solid #1a1a1a;outline-offset:-2px;font-weight:700':'')+'" onclick="scPickTwo(\''+a+'\',\''+i.key+'\',\''+b+'\',\''+j.key+'\')" title="Set both">'+scMoney(cost[ii][jj])+'</td>'; }).join("")+'</tr>'; });
  return h+'</tbody></table>';
}
function scPickTwo(a,i,b,j){ SCS.choice[a]=i; SCS.choice[b]=j; SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scGridSet(){ scPair=[document.getElementById("sc_ga").value,document.getElementById("sc_gb").value]; scRender(); }
function scRender(){
  const host=document.getElementById("sc_result"); if(!host||!KP) return;
  const ch=SCS.choice, r=scEval(ch);
  SC.keys.forEach(k=>{ const e=document.getElementById("sc_sel_"+k); if(e) e.value=ch[k];
    const n=document.getElementById("sc_note_"+k); if(n) n.innerHTML=scTagChip(scSetting(k,ch[k]).tag)+' '+scSetting(k,ch[k]).note; });
  SC.order.concat(["reported"]).forEach(k=>{ const b=document.getElementById("sc_pre_"+k); if(b) b.classList.toggle("on",k==="reported"?SCS.src==="reported":(SCS.src==="scenario"&&SCS.preset===k)); });
  host.innerHTML=scResultHTML(ch,r);
  const ownName=document.getElementById("sc_ownname");
  if(ownName) ownName.textContent=SCS.src==="reported"?"As a company reports":(SCS.preset?SC.presets[SCS.preset].name:"Your own switches");
  const pri=scPriorities(ch,true), tor=document.getElementById("sc_tornado");
  if(tor) tor.innerHTML=scTornadoSVG(pri,r.total);
  if(!scPair) scPair=[pri[0].switch,pri[1].switch];
  const ga=document.getElementById("sc_ga"), gb=document.getElementById("sc_gb");
  if(ga&&gb){ ga.value=scPair[0]; gb.value=scPair[1]; if(scPair[0]===scPair[1]) gb.value=(SC.keys.find(k=>k!==scPair[0])); }
  const gh=document.getElementById("sc_grid"); if(gh) gh.innerHTML=scGridHTML(ch,ga?ga.value:scPair[0],gb?gb.value:scPair[1]);
  scChain();
  document.querySelectorAll("#answer tr[data-sc]").forEach(tr=>{ const k=tr.getAttribute("data-sc");
    tr.classList.toggle("sel",k==="reported"?SCS.src==="reported":(SCS.src==="scenario"&&SCS.preset===k)); });
  const its=scInteractions(ch), nh=document.getElementById("sc_notes");
  if(nh) nh.innerHTML=its.length?'<ul>'+its.map(x=>'<li>'+x.text+'</li>').join("")+'</ul>':
    '<p class="fxn">No two switches interact strongly around these settings: each saves about the same whatever the other is.</p>';
}
function scChain(){        // the one-line chain under the table, for the chosen cost
  const s=state, b=biomass(s), retail=b+s.markup_add, conv=C.p_conv_anchor*s.meat_tax, R=retail/conv;
  const sh=shareCalc(R,KP,{ax:s.accept_x,tfM:s.theta_free_M,income:C.income_ref});
  const yrs=yearsToStabilize({R:R,nb0:s.neophobia_x0,nbL:s.neophobia_x,rate:s.accept_rate,p:s.p_innov,q:s.q_imit,ax:s.accept_x,tfM:s.theta_free_M,income:C.income_ref,which:"x"});
  const set=(id,t)=>{ const e=document.getElementById(id); if(e) e.innerHTML=t; };
  set("ch_cost","$"+b.toFixed(1)+"/kg"); set("ch_costl","to grow: "+(SCS.src==="reported"?"as a company reports":(SCS.preset?SC.presets[SCS.preset].name.split(":")[0].toLowerCase():"your own switches")));
  set("ch_shop","$"+retail.toFixed(0)); set("ch_shopl","in the shop, "+R.toFixed(2)+"&times; everyday meat");
  set("ch_share","~"+(sh*100).toFixed(sh<0.1?1:0)+"%"); set("ch_years","~"+yrs+" years");
}
function scSettingsHash(){ return SCS.src==="reported"?"reported":(SCS.preset||SC.keys.map(k=>k+":"+SCS.choice[k]).join(",")); }
function scReadHash(v){
  if(!v) return;
  if(v==="reported"){ SCS.src="reported"; SCS.preset=null; return; }
  if(SC.presets[v]){ SCS.choice=Object.assign({},SC.presets[v].choice); SCS.preset=v; return; }
  const ch=Object.assign({},SCS.choice);
  v.split(",").forEach(kv=>{ const [k,x]=kv.split(":"); if(k in ch && scSwitch(k) && scSetting(k,x)) ch[k]=x; });
  SCS.choice=ch; SCS.preset=scPresetOf(ch);
}
