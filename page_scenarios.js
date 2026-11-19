/* ===== scenarios: the switches, the presets and what to prioritise =====
   A line-for-line mirror of scenarios.py (run, design, priorities, interactions); tests/run_parity.py checks the two agree.
   Included into the page's script by build_interactive.py. Everything is computed by floorExplore (the mirror of
   floor_physics.explore) from the settings of the switches in MODEL.sc; nothing here is typed in by hand. */
const SC=MODEL.sc;
const INIT_ANCHOR=(typeof location!=="undefined")?location.hash.slice(1):"";   // a link to a section (#build): the settings hash replaces it, so remember it
const SCS={choice:Object.assign({},SC.presets[SC.start].choice), preset:SC.start, src:"scenario", customCost:null};   // src: "scenario" | "reported" | "custom" (the all-levers panel)
function scOwnName(){ return SCS.src==="reported"?"As a company reports":SCS.src==="custom"?"Your own levers":(SCS.preset?SC.presets[SCS.preset].name:"Your own switches"); }
const scCache={};
let scPair=null;                                   // the two switches shown against each other
function scSwitch(k){ return SC.switches.find(s=>s.key===k); }
function scSetting(k,v){ return scSwitch(k).settings.find(t=>t.key===v); }
function scSame(a,b){ return SC.keys.every(k=>a[k]===b[k]); }
function scPresetOf(ch){ return SC.order.find(k=>scSame(SC.presets[k].choice,ch))||null; }
function scParams(ch){          // the explore arguments of a choice (mirror of scenarios.explore_kwargs)
  const p={doubling_h:24,mass_pg:3000,vessel_m3:20,plant:"sanitary",mode:"perfusion",charge:C.fx.charge_mature};
  SC.switches.forEach(sw=>Object.assign(p,scSetting(sw.key,ch[sw.key]).p));
  if(p.medium_complete && SC.medium_complete_on){ p.gf_in_medium=p.growth_factors||0; p.growth_factors=0; }  // a complete medium's price already pays for growth factors, and cannot cost less than nutrients + them (scenarios.explore_kwargs)
  delete p.medium_complete;
  Object.assign(p,SC.always);                 // what every scenario carries (scenarios.always: the dissolved-oxygen setpoint)
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
    const how=gap<0?"The two overlap, because one does part of the other’s job.":"The two reinforce each other.";
    out.push({a:a,b:b,gap:gap,ga:ga,ga_with_b:gaWithB,
      text:"Setting "+sa.name.toLowerCase()+" to “"+la+"” would save $"+ga.toFixed(1)+" a kilo as things stand. It would save $"+gaWithB.toFixed(1)+
           " if "+sb.name.toLowerCase()+" were “"+lb+"”. "+how});
  }));
  const rk=x=>Math.round(Math.abs(x.gap)*1e9);          // ties keep the switches' order (as scenarios.interactions)
  return out.sort((x,y)=>(rk(y)-rk(x))||(SC.keys.indexOf(x.a)-SC.keys.indexOf(y.a))||(SC.keys.indexOf(x.b)-SC.keys.indexOf(y.b))).slice(0,top);
}

/* ---------- the page ---------- */
const scMoney=(v,d)=>"$"+v.toFixed(d===undefined?1:d);
const scPct=v=>(v<0.095?v.toFixed(2):v.toFixed(1));      // a share in percent: two decimals below 0.1 (mirror of scenarios.pct_num)
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
  if(key==="reported"){ SCS.src="reported"; SCS.preset=null; scSetEqs(C.eqs_default); }
  else { SCS.src="scenario"; SCS.choice=Object.assign({},SC.presets[key].choice); SCS.preset=key; scSetEqs(SC.presets[key].eqs); }
  scCommit();
}
// a scenario carries its demand: the share choosing cultivated meat at equal price once familiar (the best case's is higher)
function scSetEqs(v){
  state.equal_price_share=v;
  if(typeof document==="undefined") return;
  const r=document.getElementById("r_equal_price_share"); if(r) r.value=v;
  const s=(typeof MODEL!=="undefined")?MODEL.sliders.find(x=>x.key==="equal_price_share"):null; if(s&&typeof setReadout==="function") setReadout(s);
}
function easyEqs(v){ scSetEqs(v/100); recompute(); }
function scApplyChoice(o){ SCS.choice=Object.assign({},SC.presets[SC.start].choice,o); SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit();
  const e=document.getElementById("decide"); if(e&&e.scrollIntoView) e.scrollIntoView({behavior:"smooth",block:"start"}); }
function scPick(k,v){ SCS.choice[k]=v; SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scDesignNow(){ SCS.choice=scDesign(SCS.choice); SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scCommit(){
  state.cost_override=(SCS.src==="reported"?null:SCS.src==="custom"?SCS.customCost:scEval(SCS.choice).total);
  scSyncRail(); recompute();
}
// the three cost sliders and the clean-room toggle describe the process one company reports; they are live only then
function scSyncRail(){
  const reported=(SCS.src==="reported");
  ["media_price","efficiency","overhead"].forEach(k=>{ const e=document.getElementById("r_"+k); if(e) e.disabled=!reported; });
  const cb=document.getElementById("t_cleanroom"); if(cb) cb.disabled=!reported;
  scLockNotes(reported);
  const n=document.getElementById("sc_railnote");
  if(n) n.innerHTML=reported?"The cost comes from the three sliders below. They describe the process one company reports.":
    "The cost comes from the scenario chosen above (<b>"+scOwnName()+"</b>). The medium price, plant cost and cell efficiency sliders apply only to “As a company reports”.";
  const sel=document.getElementById("sc_railsel"); if(sel) sel.value=reported?"reported":(SCS.src==="custom"?"own":(SCS.preset||"own"));
}
// under each locked slider: what the chosen scenario uses instead, which switch sets it, and how to unlock the slider
function scLockNotes(reported){
  const r=(SCS.src==="scenario")?scEval(SCS.choice):null;
  const mp=r?scSetting("medium",SCS.choice.medium).p.medium_price:null;
  const own=SCS.src==="custom"?"the levers you set in “All the levers”":"the scenario chosen above";
  const txt={
    media_price: r?'This scenario uses <b>$'+mp.toFixed(2)+' a litre</b>, set by the switch “Price of the medium” in <a href="#decide">What decides it</a>.':'Set by '+own+'.',
    overhead: r?'This scenario’s plant and running costs come to <b>$'+(r.total-r.feedstock-r.growth_factors).toFixed(1)+' a kilo</b>, built from the plant, the tank, the gas and the losses switches in <a href="#decide">What decides it</a>.':'Set by '+own+'.',
    efficiency: r?'This scenario’s cells need <b>'+r.medium_l.toFixed(0)+' litres of medium a kilo</b>, set by the switches “Kind of cells” and “Growth speed”.':'Set by '+own+'.'};
  ["media_price","efficiency","overhead"].forEach(k=>{
    const e=document.getElementById("r_"+k); if(!e) return;
    const ctl=e.closest(".ctl"); let nt=ctl.querySelector(".locknote");
    if(!nt){ nt=document.createElement("div"); nt.className="locknote"; ctl.appendChild(nt); }
    nt.style.display=reported?"none":"block";
    if(!reported) nt.innerHTML='Locked: this slider describes the process one company reports. '+txt[k]+
      ' <a href="#" onclick="scApply(\'reported\');return false">Use the company’s process</a> to move it.';
  });
}
function scRailBuild(){
  const sel=document.getElementById("sc_railsel"); if(!sel) return;
  sel.innerHTML=SC.order.map(k=>'<option value="'+k+'">'+SC.presets[k].name+'</option>').join("")+
    '<option value="reported">As a company reports</option><option value="own" disabled>Your own switches</option>';
  sel.onchange=()=>scApply(sel.value);
}
function scResultHTML(ch,r){
  const markup=state.markup_add, cost=r.total, retail=shelfPrice(cost,state), R=retail/(C.p_conv_anchor*state.meat_tax);
  const world=scShare(cost,"global"), us=scShare(cost,"us"), eu=scShare(cost,"eu");
  const lim=(SC.limit_plain[r.limit]||r.limit).replace("CO2","CO₂");
  const med=(SC.medium_plain[r.medium_set_by]||r.medium_set_by);
  const need=scNeeds(ch).filter(x=>x[2]!=="nothing new");
  const bd=(SCS.src==="scenario"&&SCS.preset)?SC.bands[SCS.preset]:null;      // the band is computed for the named scenarios only
  const shareStrip=bd?'<b>'+scPct(bd.share[1])+'%</b> of world meat in the long run (the median, with 80% of draws between '+scPct(bd.share[0])+'% and '+scPct(bd.share[2])+'%)'
    :'<b>'+scPct(world)+'%</b> of world meat in the long run (point estimate)';
  const strip='<span class="scbig">'+scMoney(cost)+'<span> a kilo of cells</span></span> &nbsp; <b>'+scMoney(retail,0)+'</b> in the shop ('+R.toFixed(2)+
    '&times; everyday meat) &nbsp; '+shareStrip;
  const el0=document.getElementById("sc_strip"); if(el0) el0.innerHTML=strip;
  const usEu=' (US '+scPct(us)+'%, Europe '+scPct(eu)+'%). ';
  let h='<p>The long-run share of world meat is '+(bd?'<b>'+scPct(bd.share[1])+'%</b>. This is the median of the draws. 80% of draws fall between '+scPct(bd.share[0])+'% and '+scPct(bd.share[2])+'%, with cost and demand both uncertain. The band exists only for the named scenarios, not for settings you change. At the cost above and the demand settings you have set, the point estimate is '+scPct(world)+'%'+usEu
      :'<b>'+scPct(world)+'%</b> by weight'+usEu+'This is a point estimate. There is no band for settings you have changed. ')+
    'The shop price adds '+scMoney(markup,1)+' a kilo for forming, packing and cold chain, then the shop\'s '+(state.retail_margin*100).toFixed(0)+'% margin: '+scMoney(retail,0)+' a kilo. Everyday meat costs $'+(C.p_conv_anchor*state.meat_tax).toFixed(0)+' a kilo.</p>'+
    '<p>The tank holds '+r.density.toFixed(0)+' g of cells a litre, limited by <b>'+lim+'</b>, and works '+(r.uptime*100).toFixed(0)+'% of the year. '+
    ((r.column&&r.limit==="oxygen supply")?'Oxygen, not CO₂, limits it because the column beside the tank takes the CO₂ out, and antifoam takes a quarter of the oxygen the bubbles deliver. Without the column, CO₂ would limit it first. ':'')+
    'Each kilo of cells needs '+r.medium_l.toFixed(0)+' litres of medium, set by <b>'+med+'</b>.</p>';
  if(need.length){ h+='<p class="scneed"><b>What has to go right:</b> '+scTagChip(scHardest(ch))+' at the hardest. '+
    need.map(x=>x[1]+' <i>('+x[2]+')</i>').join(". ")+'.</p>'; }
  const d=r.column;
  if(d && (d.ph_vs_safe>1+1e-9 || !d.passes_tested))
    h+='<p class="scwarn">This tank design pumps the culture through the column harder than the checks allow. It uses '+d.passes.toFixed(0)+
       ' passes an hour, and dense cultures have taken up to 15–24. The alkaline culture in the loop is '+d.ph_vs_safe.toFixed(1)+' times the exposure judged safe. '+
       'Treat the cost as too low, or use the button below to pick the cheapest design that passes.</p>';
  if(SCS.src==="reported") h+='<p class="scwarn">The charts below are using the process one company reports, not these switches.</p>';
  if(SCS.src==="custom") h+='<p class="scwarn">The charts below are using the case from “All the levers” ($'+SCS.customCost.toFixed(1)+' a kilo), not these switches.</p>';
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
      const lab='+$'+r.d_worst.toFixed(1)+(clip?', off the scale':'')+(r.share_worst!==undefined?' ('+scPts(r.share_worst)+')':'');
      // a clipped bar runs to the edge of the chart, so its label goes inside the bar, not after it
      g+=clip?'<text x="'+(x1-10)+'" y="'+(y+13)+'" font-size="10" text-anchor="end" fill="#fff" font-weight="600">'+lab+'</text>'
             :'<text x="'+(x1+3)+'" y="'+(y+13)+'" font-size="10" fill="#CC3311">'+lab+'</text>';
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
// Where the cost goes: the six parts of a kilo's cost for the chosen switches, on a dollar axis shared with Central, so the
// whole bar shrinks or grows as the switches move. The first four parts scale with the litres of medium. Colours follow the
// part, never its rank, and match the repo's figures (floor_physics.fig_floor_tiers); validated for colour-blind separation.
const SC_PARTS=[
  {key:"medium", name:"Medium (the nutrients)", col:"#029E73", litres:true, get:r=>r.feedstock},
  {key:"gf", name:"Growth factors", col:"#DE8F05", litres:true, get:r=>r.growth_factors},
  {key:"protect", name:"Bubble protectant", col:"#CC78BC", litres:true, get:r=>r.protectant},
  {key:"membranes", name:"Filter membranes", col:"#D55E00", litres:true, get:r=>r.membranes},
  {key:"running", name:"Running the plant (staff, power, other supplies)", col:"#56B4E9", litres:false,
   get:r=>r.labour+r.utilities+(r.consumables-r.membranes-r.protectant)+r.extra_opex},
  {key:"plant", name:"The plant (yearly charge on its capital)", col:"#0173B2", litres:false, get:r=>r.capital}];
function scPartsSVG(r, ref, refName){
  const W=720, x0=16, x1=W-16, by=78, bh=22, rowH=21, ly=by+bh+62;
  const parts=SC_PARTS.map(p=>({p, v:Math.max(0,p.get(r)), vr:ref?Math.max(0,p.get(ref)):null}));
  const total=parts.reduce((s,q)=>s+q.v,0), litres=parts.filter(q=>q.p.litres).reduce((s,q)=>s+q.v,0);
  const par=parityCost(state);
  const top=Math.max(total, ref?ref.total:0, par)*1.08, step=top>60?20:top>25?10:5, xmax=Math.ceil(top/step)*step;
  const X=v=>x0+(x1-x0)*v/xmax, f2=v=>"$"+v.toFixed(2), f1=v=>"$"+v.toFixed(1);
  const H=ly+parts.length*rowH+8;
  let g='<svg viewBox="0 0 '+W+' '+H+'" width="100%" style="max-width:'+W+'px;min-width:520px" role="img" aria-label="Where the cost of a kilo of cells goes">';
  g+='<text x="'+x0+'" y="16" font-size="13" font-weight="700" style="fill:var(--ink)">Where the cost goes: '+f1(total)+' a kilo of cells</text>';
  g+='<text x="'+x0+'" y="33" font-size="10.5" style="fill:var(--muted)">'+(total>0?Math.round(litres/total*100):0)+'% of it scales with the litres of medium ('+r.medium_l.toFixed(0)+
     ' L a kilo): the first four parts.</text>'+
     '<text x="'+x0+'" y="47" font-size="10.5" style="fill:var(--muted)">The bar is drawn in dollars, so it shrinks as the cost falls. Hover over a part for its value.</text>';
  const marksAt=[par].concat(ref&&Math.abs(ref.total-total)>0.005?[ref.total]:[]);
  for(let t=0;t<=xmax+1e-9;t+=step){ if(marksAt.some(m=>Math.abs(X(m)-X(t))<16)) { g+='<line x1="'+X(t)+'" x2="'+X(t)+'" y1="'+(by-6)+'" y2="'+(by+bh+6)+'" stroke="#eee"/>'; continue; } g+='<line x1="'+X(t)+'" x2="'+X(t)+'" y1="'+(by-6)+'" y2="'+(by+bh+6)+'" stroke="#eee"/>'+
     '<text x="'+X(t)+'" y="'+(by+bh+18)+'" font-size="9.5" text-anchor="middle" style="fill:var(--muted)">$'+t+'</text>'; }
  let acc=0;
  parts.forEach(q=>{ if(q.v<=0) return; const a=X(acc), b=X(acc+q.v); acc+=q.v;
    g+='<rect x="'+a.toFixed(1)+'" y="'+by+'" width="'+Math.max(0.5,b-a-2).toFixed(1)+'" height="'+bh+'" rx="3" fill="'+q.p.col+'"><title>'+
       q.p.name+': '+f2(q.v)+' a kilo ('+(q.v/total*100).toFixed(0)+'%)</title></rect>';
    const pct=Math.round(q.v/total*100)+'%', both=f1(q.v)+' \u00b7 '+pct;      // dollars and share where the part has room
    const lab=b-a>8+both.length*6.2?both:(b-a>8+pct.length*6.2?pct:'');
    if(lab) g+='<text x="'+(a+5).toFixed(1)+'" y="'+(by+15)+'" font-size="10" fill="#fff" font-weight="700" pointer-events="none">'+lab+'</text>'; });
  // the bracket over the litre-driven parts
  if(litres>0){ const a=X(0), b=X(litres)-2; g+='<path d="M'+a+' '+(by-4)+' V'+(by-9)+' H'+b+' V'+(by-4)+'" fill="none" stroke="#999"/>'+
     '<text x="'+((a+b)/2).toFixed(1)+'" y="'+(by-12)+'" font-size="9.5" text-anchor="middle" style="fill:var(--muted)">scales with litres: '+f1(litres)+'</text>'; }
  // reference marks: parity, and the named scenario to compare with
  const mark=(v,lab,dash)=>'<line x1="'+X(v)+'" x2="'+X(v)+'" y1="'+(by+bh+2)+'" y2="'+(by+bh+24)+'" stroke="#333" stroke-dasharray="'+dash+'"/>'+
     '<text x="'+(X(v)+3)+'" y="'+(by+bh+30)+'" font-size="9.5" style="fill:#333">'+lab+'</text>';
  g+=mark(par,"parity "+f1(par),"2 2");
  if(ref&&Math.abs(ref.total-total)>0.005&&Math.abs(X(ref.total)-X(par))>70) g+=mark(ref.total,refName+" "+f1(ref.total),"5 3");
  // the list: one row per part, with what it costs and its share; the change against the reference when there is one
  const showRef=ref&&Math.abs(ref.total-total)>0.005;
  g+='<text x="'+(x0+560)+'" y="'+(ly-17)+'" font-size="9.5" text-anchor="end" style="fill:var(--muted)">$ a kilo</text>'+
     '<text x="'+(x0+620)+'" y="'+(ly-17)+'" font-size="9.5" text-anchor="end" style="fill:var(--muted)">share</text>'+
     (showRef?'<text x="'+x1+'" y="'+(ly-17)+'" font-size="9.5" text-anchor="end" style="fill:var(--muted)">vs '+refName+'</text>':'');
  parts.forEach((q,i)=>{ const y=ly+i*rowH, d=showRef?q.v-q.vr:0;
    g+='<rect x="'+x0+'" y="'+(y-9)+'" width="10" height="10" rx="2" fill="'+q.p.col+'"/>'+
       '<text x="'+(x0+16)+'" y="'+y+'" font-size="11" style="fill:var(--ink)">'+q.p.name+'</text>'+
       '<text x="'+(x0+560)+'" y="'+y+'" font-size="11" text-anchor="end" style="fill:var(--ink)">'+f2(q.v)+'</text>'+
       '<text x="'+(x0+620)+'" y="'+y+'" font-size="11" text-anchor="end" style="fill:var(--muted)">'+(total>0?(q.v/total*100).toFixed(0):0)+'%</text>'+
       (showRef?'<text x="'+x1+'" y="'+y+'" font-size="11" text-anchor="end" style="fill:var(--muted)">'+(Math.abs(d)<0.005?"same":(d>0?"+":"−")+f2(Math.abs(d)).slice(0))+'</text>':''); });
  return g+'</svg>';
}
function scRender(){
  const host=document.getElementById("sc_result"); if(!host||!KP) return;
  const ch=SCS.choice, r=scEval(ch);
  SC.keys.forEach(k=>{ const e=document.getElementById("sc_sel_"+k); if(e) e.value=ch[k];
    const n=document.getElementById("sc_note_"+k); if(n) n.innerHTML=scTagChip(scSetting(k,ch[k]).tag)+' '+scSetting(k,ch[k]).note; });
  SC.order.concat(["reported"]).forEach(k=>{ const b=document.getElementById("sc_pre_"+k); if(b) b.classList.toggle("on",k==="reported"?SCS.src==="reported":(SCS.src==="scenario"&&SCS.preset===k)); });
  host.innerHTML=scResultHTML(ch,r);
  const ph=document.getElementById("sc_parts");      // where the cost goes, against Central (or the best case when Central is chosen)
  if(ph){ const refKey=SCS.preset==="central"?"best":"central"; ph.innerHTML=scPartsSVG(r,scEval(SC.presets[refKey].choice),refKey==="central"?"Central":"the best case"); }
  const ownName=document.getElementById("sc_ownname");
  if(ownName) ownName.textContent=scOwnName();
  const pri=scPriorities(ch,true), tor=document.getElementById("sc_tornado");
  if(tor) tor.innerHTML=scTornadoSVG(pri,r.total);
  if(!scPair) scPair=[pri[0].switch,pri[1].switch];
  const ga=document.getElementById("sc_ga"), gb=document.getElementById("sc_gb");
  if(ga&&gb){ ga.value=scPair[0]; gb.value=scPair[1]; if(scPair[0]===scPair[1]) gb.value=(SC.keys.find(k=>k!==scPair[0])); }
  const gh=document.getElementById("sc_grid"); if(gh) gh.innerHTML=scGridHTML(ch,ga?ga.value:scPair[0],gb?gb.value:scPair[1]);
  scChain();
  document.querySelectorAll("#answer tr[data-sc]").forEach(tr=>{ const k=tr.getAttribute("data-sc");
    tr.classList.toggle("sel",k==="reported"?SCS.src==="reported":(SCS.src==="scenario"&&SCS.preset===k)); });
  if(typeof vmRender==="function") vmRender();     // the vessel-by-mode table follows the switches (page_vessels.js)
  easyRender();
  const its=scInteractions(ch), nh=document.getElementById("sc_notes");
  if(nh) nh.innerHTML=its.length?'<ul>'+its.map(x=>'<li>'+x.text+'</li>').join("")+'</ul>':
    '<p class="fxn">No two switches interact strongly around these settings. Each saves about the same whatever the other is.</p>';
}
function scChain(){        // the one-line chain under the table, for the chosen cost
  const s=state, b=biomass(s), retail=shelfPrice(b,s), conv=C.p_conv_anchor*s.meat_tax, R=retail/conv;
  const sh=shareCalc(R,KP,{ax:s.accept_x,tfM:s.theta_free_M,income:C.income_ref});
  const yrs=yearsToStabilize({R:R,nb0:s.neophobia_x0,nbL:s.neophobia_x,rate:s.accept_rate,p:s.p_innov,q:s.q_imit,ax:s.accept_x,tfM:s.theta_free_M,income:C.income_ref,which:"x"});
  const set=(id,t)=>{ const e=document.getElementById(id); if(e) e.innerHTML=t; };
  set("ch_cost","$"+b.toFixed(1)+"/kg"); set("ch_costl","to grow ("+(SCS.src==="scenario"&&SCS.preset?SC.presets[SCS.preset].name.split(":")[0].toLowerCase():scOwnName().toLowerCase())+")");
  set("ch_shop","$"+retail.toFixed(0)); set("ch_shopl","in the shop, "+R.toFixed(2)+"&times; everyday meat");
  set("ch_share","~"+(sh*100).toFixed(sh<0.1?1:0)+"%"); set("ch_years","~"+yrs+" years");
}
function scSettingsHash(){ return SCS.src==="reported"?"reported":SCS.src==="custom"?"custom:"+SCS.customCost.toFixed(3):(SCS.preset||SC.keys.map(k=>k+":"+SCS.choice[k]).join(",")); }
function scReadHash(v){
  if(!v) return;
  if(v==="reported"){ SCS.src="reported"; SCS.preset=null; return; }
  if(v.indexOf("custom:")===0){ const c=parseFloat(v.slice(7)); if(isFinite(c)&&c>0){ SCS.src="custom"; SCS.preset=null; SCS.customCost=c; } return; }
  if(SC.presets[v]){ SCS.choice=Object.assign({},SC.presets[v].choice); SCS.preset=v; return; }
  const ch=Object.assign({},SCS.choice);
  v.split(",").forEach(kv=>{ const [k,x]=kv.split(":"); if(k in ch && scSwitch(k) && scSetting(k,x)) ch[k]=x; });
  SCS.choice=ch; SCS.preset=scPresetOf(ch);
}

/* ---------- the all-levers panel starts from a scenario ---------- */
/* ===== the short version: a view switch, three numbers for the chosen case, every long section folded =====
   Nothing is computed here that the full page does not compute: the cost is the chosen scenario's (biomass), the shop price is
   shelfPrice, the share is the scenario's band (or the point estimate for settings the reader changed). */
let VIEW="easy";
function easyStored(){ try{ return localStorage.getItem("cm_view"); }catch(e){ return null; } }
function setView(v,keep){
  VIEW=(v==="full"?"full":"easy");
  if(document.body&&document.body.classList) document.body.classList.toggle("easy",VIEW==="easy");
  ["easy","full"].forEach(k=>{ const b=document.getElementById("view_"+k); if(b&&b.classList) b.classList.toggle("on",VIEW===k); });
  if(!keep){ try{ localStorage.setItem("cm_view",VIEW); }catch(e){} }
}
function easyOpenFor(el){        // open the folded section that holds an element (a link to #build, or a click in the section list)
  const sec=(el&&el.closest)?el.closest("section[data-easy]"):null;
  if(sec&&sec.classList){ sec.classList.add("open"); const h=sec.querySelector("h2"); if(h) h.setAttribute("aria-expanded","true"); }
}
function easyInit(){
  if(typeof document==="undefined"||!document.querySelectorAll) return;
  document.querySelectorAll("section[data-easy]").forEach(sec=>{
    const h=sec.querySelector("h2"); if(!h||!h.addEventListener) return;
    h.setAttribute("tabindex","0"); h.setAttribute("role","button"); h.setAttribute("aria-expanded","false");
    const tog=()=>{ if(VIEW!=="easy") return; const open=sec.classList.toggle("open"); h.setAttribute("aria-expanded",open?"true":"false"); };
    h.addEventListener("click",tog);
    h.addEventListener("keydown",e=>{ if(e.key==="Enter"||e.key===" "){ e.preventDefault(); tog(); } }); });
  document.querySelectorAll("nav.jump a").forEach(a=>{ if(a.addEventListener) a.addEventListener("click",()=>{
    easyOpenFor(document.getElementById((a.getAttribute("href")||"").slice(1))); }); });
  const pick=document.getElementById("easy_pick");
  if(pick) pick.innerHTML=C.easy.cases.map(c=>'<button class="btn" id="easy_btn_'+c.key+'" onclick="scApply(\''+c.key+'\')">'+c.label+'</button>').join("");
  setView(easyStored()==="full"?"full":"easy",true);
}
function easyRender(){
  const host=document.getElementById("easy_nums"); if(!host) return;
  const cost=biomass(state), retail=shelfPrice(cost,state), conv=C.p_conv_anchor*state.meat_tax;
  const picked=(SCS.src==="scenario"&&SCS.preset)?SCS.preset:null;
  const named=(picked&&Math.abs(state.equal_price_share-SC.presets[picked].eqs)<1e-9)?picked:null, bd=named?SC.bands[named]:null;   // the band holds only at the case's own demand
  const eq=document.getElementById("easy_eqs"), eqv=document.getElementById("easy_eqs_v");
  if(eq) eq.value=Math.round(state.equal_price_share*100); if(eqv) eqv.textContent=Math.round(state.equal_price_share*100)+"%";
  const share=bd?bd.share[1]:scShare(cost,"global");
  const pct=v=>scPct(v)+"%";
  const tile=(big,txt)=>'<div class="easytile"><div class="easybig">'+big+'</div>'+txt+'</div>';
  host.innerHTML='<div class="easytiles">'+
    tile(scMoney(cost),"to grow a kilo of cells")+
    tile(scMoney(retail,0),"a kilo in the shop: "+(retail/conv).toFixed(1)+" times everyday meat ($"+conv.toFixed(0)+")")+
    tile(pct(share),"of the world's meat in the long run"+(bd?(bd.share[0]<0.005?" (most likely "+pct(bd.share[2])+" or less)":" (most likely between "+pct(bd.share[0])+" and "+pct(bd.share[2])+")"):" (a single estimate for your own settings)"))+
    '</div>';
  C.easy.cases.forEach(c=>{ const b=document.getElementById("easy_btn_"+c.key); if(b&&b.classList) b.classList.toggle("on",picked===c.key); });
  const mine=C.easy.cases.find(c=>c.key===picked), say=document.getElementById("easy_say");
  if(say) say.innerHTML='<b>'+(mine?mine.label:scOwnName())+'.</b> '+(mine?mine.say:"These are settings chosen further down the page.")+
    ' To cost the same as everyday meat in the shop, a kilo of cells would have to cost about '+scMoney(parityCost(state))+'.';
  const ph=document.getElementById("easy_parts");
  if(ph) ph.innerHTML=(SCS.src==="scenario")?scPartsSVG(scEval(SCS.choice),null,null):"";
}
const FX_GLC_DEFAULT=C.fx.glc_kg;
function fxFromScenario(key){
  const box=document.getElementById("fx"); if(!box||!fxDefaults) return;
  box.querySelectorAll("input,select").forEach(e=>{ if(e.id in fxDefaults){ if(e.type==="checkbox") e.checked=fxDefaults[e.id]; else e.value=fxDefaults[e.id]; } });
  fxPco2Range=C.fx.species.model[5]; document.getElementById("fx_spn").innerHTML=C.fx.species.model[7];
  const sel=document.getElementById("fx_sc"); if(sel) sel.value=key||"";
  if(key){
    const p=scParams(SC.presets[key].choice), set=(id,v)=>{ const e=document.getElementById(id); if(e) e.value=v; };
    set("fx_dh",p.doubling_h); set("fx_m",p.mass_pg/1000);
    set("fx_pl",p.items?"lean":p.plant); set("fx_gv",p.gas_v===undefined?C.fx.gas_v*1000:p.gas_v*1000);
    set("fx_col",p.column||"none"); if(p.col_pout!==undefined) set("fx_cp",p.col_pout);
    set("fx_pt",p.p_top===undefined?0.33:p.p_top); set("fx_ar",p.aspect===undefined?C.fx.aspect:p.aspect);
    set("fx_hz",(p.hazard||0)*100); set("fx_rf",p.restart_fail===undefined?3:p.restart_fail);
    set("fx_gf",(p.growth_factors||0)*100); set("fx_mp",p.medium_price===undefined?0.15:p.medium_price);
    if(p.nh3_kg!==undefined){ set("fx_wm","sep"); set("fx_nh",p.nh3_kg); set("fx_ly",p.lac_yield); set("fx_gk",p.glc_kg===undefined?FX_GLC_DEFAULT:p.glc_kg); }
    set("fx_mo","perfusion");
  }
  fxRender();
}
