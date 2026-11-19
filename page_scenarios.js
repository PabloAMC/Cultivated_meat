/* ===== scenarios: the switches, the presets and what to prioritise =====
   A line-for-line mirror of scenarios.py (run, design, priorities, interactions); tests/run_parity.py checks the two agree.
   Included into the page's script by build_interactive.py. Everything is computed by floorExplore (the mirror of
   floor_physics.explore) from the settings of the switches in MODEL.sc; nothing here is typed in by hand. */
const SC=MODEL.sc;
const INIT_HASH=(typeof location!=="undefined")?location.hash.slice(1):"";   // a link to a level (#moves): the settings hash replaces it, so remember it
const SCS={choice:Object.assign({},SC.presets[SC.start].choice), preset:SC.start, src:"scenario", customCost:null};   // src: "scenario" (the ten switches) | "custom" (the all-levers panel)
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


/* =====================================================================================================================
   THE PAGE. One case drives everything: one of the three named cases (MODEL.page.cases) or the reader's own settings.
   Nothing below changes the model's arithmetic: it calls the engine (floorExplore, penetration, shareCalc, effConsts)
   and draws what comes back. Headline numbers for a named case are the medians of the precomputed draws (SC.bands for
   the world, MODEL.page.region_bands by region); for the reader's own settings there are no draws, so they are single
   estimates and are labelled as such.
   ===================================================================================================================== */
const PG=MODEL.page;
const PGS={base:SC.start, l2sel:null, dirty:{}};          // base: the named case last picked (what "your own settings" started from)
const scMoney=(v,d)=>"$"+v.toFixed(d===undefined?1:d);
const pgUSD=v=>"$"+Math.round(v).toLocaleString("en-US");
const pgEsc=t=>String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
// a share in percent as text: one decimal from 0.1 up, two below it, three below 0.01, "under 0.001" below that (mirror of scenarios.pct_num)
function pgPct(v){ return v<0.00095?"under 0.001":(v<0.0095?v.toFixed(3):(v<0.095?v.toFixed(2):v.toFixed(1))); }
const scPct=pgPct;
const pgPctS=v=>pgPct(v)+"%";
function pgRange(a,b,f){ return f(a)===f(b)?f(a):"between "+f(a)+" and "+f(b); }
function pgCaseDef(k){ return PG.cases.find(c=>c.key===k)||null; }
function pgCaseLabel(k){ const c=pgCaseDef(k); return c?c.label:PG.own_label; }
function pgCaseWords(f){ return f.key==="own"?"your own settings":"the "+f.label+(/case$/.test(f.label)?"":" case"); }
function pgRegionName(r){ const x=PG.regions.find(q=>q[0]===(r||state.region)); return x?x[1]:r; }
function pgRegionOf(){ return state.region==="global"?"the world's":pgRegionName()+"'s"; }
// every shopper setting at the model's value (the share at equal price aside: a case carries its own)
function pgShoppersDefault(){
  const ok=MODEL.sliders.every(s=>{ if(s.key==="equal_price_share"||s.key==="income") return true;
    if(s.solved) return !state[s.key+"_ovr"];
    return Math.abs(state[s.key]-s.start)<1e-9; });
  return ok&&MODEL.toggles.every(t=>!state[t.key])&&Math.abs(state.income-C.REGION_INCOME[state.region])<1e-6;
}
// the case the page is on: "today" | "central" | "best" when every setting is that case's, "own" as soon as one is not
function pgCase(){
  if(SCS.src!=="scenario"||!SCS.preset) return "own";
  const c=pgCaseDef(SCS.preset); if(!c) return "own";
  if(Math.abs(state.equal_price_share-c.eqs)>1e-9) return "own";
  return pgShoppersDefault()?c.key:"own";
}
function scOwnName(){ return pgCaseLabel(pgCase()); }
function pgPointCost(){ return SCS.src==="custom"?SCS.customCost:scEval(SCS.choice).total; }   // every estimate at its most likely value
function pgCostBand(){ return (SCS.src==="scenario"&&SCS.preset&&SC.bands[SCS.preset])?SC.bands[SCS.preset].cost:null; }
function pgHeadCost(){ const b=pgCostBand(); return b?b[1]:pgPointCost(); }                    // the median where there are draws
function pgShareK(cost,K,over){ const sv=KP; KP=K;
  try{ return penetration(Object.assign({},state,over||{},{cost_override:cost})).tv*100; } finally{ KP=sv; } }
function pgPlantBased(){ return penetration(Object.assign({},state,{cost_override:1e6})).tvp*100; }   // with no cultivated meat on sale
function pgAbout(v){ return String(Math.round(v*10)/10); }
// the facts of the first screen, for the page's current state
function pgFacts(){
  const key=pgCase(), cb=pgCostBand(), point=pgPointCost(), cost=cb?cb[1]:point;
  const sb=(key!=="own")?PG.region_bands[key][state.region]:null;
  const retail=shelfPrice(cost,state), conv=C.p_conv_anchor*state.meat_tax;
  return {key:key, label:pgCaseLabel(key), region:state.region, cost:cost, cb:cb, point:point, retail:retail, conv:conv, mult:retail/conv,
          share:sb?sb[1]:scShare(cost,state.region), sb:sb, pb:pgPlantBased(), parity:parityCost(state), eqs:state.equal_price_share};
}
function pgTilesHTML(f){
  const tile=(lab,big,txt)=>'<div class="tile"><div class="tl">'+lab+'</div><div class="tb">'+big+'</div><p class="td">'+txt+'</p></div>';
  const where=state.region==="global"?"world meat and seafood":"meat and seafood, "+pgRegionName();
  const t1=f.cb?"Median. 8 in 10 draws: $"+Math.round(f.cb[0])+"–"+Math.round(f.cb[2])+". "+scMoney(f.point)+" if every estimate lands on its most likely value."
              :"Every estimate at its most likely value. There are no draws for settings you have changed.";
  const t2=f.mult.toFixed(1)+" times everyday meat ("+scMoney(f.conv,0)+" a kilo). "+(f.cb?"At the median cost, after ":"After ")+scMoney(state.markup_add)+
           " a kilo to reach the shelf and the shop's "+(state.retail_margin*100).toFixed(0)+"% margin.";
  const pb="Plant-based meat today: about "+pgAbout(f.pb)+"%.";
  const t3=f.sb?"Median. 8 in 10 draws: "+(f.sb[2]<0.00095?"under 0.001%":pgPct(f.sb[0])+"% to "+pgPct(f.sb[2])+"%")+". "+pb
               :"A single estimate at "+(f.cb?"the median cost":"this cost")+" and the shopper settings as set. "+pb;
  return tile("Cost to grow a kilo of cells",(f.cb?"About ":"")+pgUSD(f.cost),t1)+
         tile("Price in the shop",pgUSD(f.retail)+" a kilo",t2)+
         tile("Long-run share of "+where,pgPctS(f.share),t3);
}
function pgDeck(f){
  const who=f.key==="own"?"With your own settings":(f.key==="today"?"With the published cells":"In the "+f.label);
  const c=f.cb?"about "+pgUSD(f.cost)+" (8 in 10 draws between $"+Math.round(f.cb[0])+" and $"+Math.round(f.cb[2])+")":pgUSD(f.cost)+" (a single estimate)";
  const s=f.sb?(f.sb[2]<0.00095?"under 0.001% of "+pgRegionOf()+" meat and seafood":"about "+pgPctS(f.share)+" of "+pgRegionOf()+" meat and seafood (8 in 10 draws between "+pgPct(f.sb[0])+"% and "+pgPct(f.sb[2])+"%)")
              :pgPctS(f.share)+" of "+pgRegionOf()+" meat and seafood (a single estimate)";
  return who+", growing a kilo of cultivated-meat cells costs "+c+", and in the long run it takes "+s+".";
}

/* ---------- picking a case ---------- */
function pgResetShoppers(){          // every shopper setting back to the model's value (keeps the region)
  MODEL.sliders.forEach(s=>{ state[s.key]=s.start; if(s.solved) state[s.key+"_ovr"]=false; });
  MODEL.toggles.forEach(t=>{ state[t.key]=false; });
  state.income=C.REGION_INCOME[state.region];
  if(typeof pgSyncControls==="function") pgSyncControls();
}
function scApply(key){               // a named case: its switches, its share at equal price, and every other setting at the model's value
  if(!SC.presets[key]) return;
  pgResetShoppers();
  SCS.src="scenario"; SCS.choice=Object.assign({},SC.presets[key].choice); SCS.preset=key; if(pgCaseDef(key)) PGS.base=key;
  scSetEqs(SC.presets[key].eqs); scCommit();
}
// a case carries its demand: the share choosing cultivated meat at equal price once familiar (the best case's is higher)
function scSetEqs(v){
  state.equal_price_share=v;
  if(typeof document==="undefined") return;
  const r=document.getElementById("r_equal_price_share"); if(r) r.value=v;
  const s=(typeof MODEL!=="undefined")?MODEL.sliders.find(x=>x.key==="equal_price_share"):null; if(s&&typeof setReadout==="function") setReadout(s);
}
function scApplyChoice(o){ SCS.choice=Object.assign({},SC.presets[SC.start].choice,o); SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scPick(k,v){ SCS.choice[k]=v; SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scDesignNow(){ SCS.choice=scDesign(SCS.choice); SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function scPickTwo(a,i,b,j){ SCS.choice[a]=i; SCS.choice[b]=j; SCS.src="scenario"; SCS.preset=scPresetOf(SCS.choice); scCommit(); }
function pgSetCost(){ state.cost_override=pgHeadCost(); }      // the cost every shopper chart runs at
function scCommit(){ pgSetCost(); recompute(); }
function scSettingsHash(){ return SCS.src==="custom"?"custom:"+SCS.customCost.toFixed(3):(SCS.preset||SC.keys.map(k=>k+":"+SCS.choice[k]).join(",")); }
function scReadHash(v){
  if(!v) return;
  if(v.indexOf("custom:")===0){ const c=parseFloat(v.slice(7)); if(isFinite(c)&&c>0){ SCS.src="custom"; SCS.preset=null; SCS.customCost=c; } return; }
  if(SC.presets[v]){ SCS.choice=Object.assign({},SC.presets[v].choice); SCS.preset=v; if(pgCaseDef(v)) PGS.base=v; return; }
  const ch=Object.assign({},SCS.choice);
  v.split(",").forEach(kv=>{ const [k,x]=kv.split(":"); if(k in ch && scSwitch(k) && scSetting(k,x)) ch[k]=x; });
  SCS.choice=ch; SCS.preset=scPresetOf(ch);
}

/* ---------- the case bar and the first screen ---------- */
function pgBuildBar(){
  const host=document.getElementById("casebtns"); if(!host) return;
  host.innerHTML=PG.cases.map(c=>'<button type="button" id="case_'+c.key+'" title="'+pgEsc(c.say)+'" onclick="scApply(\''+c.key+'\')">'+c.label+'</button>').join("")+
    '<button type="button" id="case_own" onclick="pgOwnHint()">'+PG.own_label+'</button>';
  const sel=document.getElementById("regionsel");
  if(sel){ sel.innerHTML=PG.regions.map(r=>'<option value="'+r[0]+'">'+r[1]+'</option>').join("");
    sel.onchange=()=>{ state.region=sel.value; setIncome(C.REGION_INCOME[state.region]); fillCurveSel(); recompute(); }; }
  const eq=document.getElementById("eqs");
  if(eq) eq.oninput=()=>{ scSetEqs(parseFloat(eq.value)/100); recompute(); };
}
function pgOwnHint(){ const h=document.getElementById("casehint"); if(h&&h.classList) h.classList.toggle("on",pgCase()!=="own"); }
function pgRenderBar(f){
  PG.cases.forEach(c=>{ const b=document.getElementById("case_"+c.key); if(b) b.setAttribute("aria-pressed",f.key===c.key?"true":"false"); });
  const o=document.getElementById("case_own");
  if(o){ o.setAttribute("aria-pressed",f.key==="own"?"true":"false"); o.setAttribute("aria-disabled",f.key==="own"?"false":"true"); }
  const h=document.getElementById("casehint"); if(h&&h.classList&&f.key==="own") h.classList.remove("on");
  const sel=document.getElementById("regionsel"); if(sel) sel.value=state.region;
  const bar=document.getElementById("casebar");
  if(bar&&bar.offsetHeight&&document.documentElement&&document.documentElement.style) document.documentElement.style.setProperty("--barh",(bar.offsetHeight+10)+"px");
}
function pgRenderFirst(){
  if(typeof document==="undefined") return;
  const f=pgFacts(), set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  pgRenderBar(f);
  set("deck",pgDeck(f)); set("tiles",pgTilesHTML(f));
  const eq=document.getElementById("eqs"); if(eq) eq.value=Math.round(f.eqs*100);
  set("eqs_v",Math.round(f.eqs*100)+"%");
  const at=R=>shareCalc(R,KP,{ax:state.accept_x,tfM:state.theta_free_M,income:C.income_ref,nbx:state.neophobia_x,hx:state.health_x})*100;
  const free=at(0);
  set("eqs_read","At half the price of meat: <b>"+at(0.5).toFixed(0)+"%</b>. If it were free: <b>"+free.toFixed(0)+"%</b>, so "+(100-free).toFixed(0)+
    "% would not take it at any price. These follow from the model, in which shoppers differ widely in how much they like it. "+
    "The setting is a judgement: "+PG.cases.map(c=>c.label+" "+Math.round(c.eqs*100)+"%").join(", ")+".");
  l0Draw(f);
}

/* ---------- the first chart: long-run share against the cost of a kilo of cells, banded by the share at equal price ---------- */
const L0_LEVELS=[0.05,0.10,0.20,0.30,0.40,0.55,0.70];
const L0_Y=[0.003,80];
let l0Cache={key:null}, l0Geo=null;
function pgShopperKey(){ return MODEL.sliders.filter(s=>s.key!=="equal_price_share").map(s=>state[s.key]+(s.solved&&state[s.key+"_ovr"]?"p":"")).join(",")+"|"+state.region+"|"+state.income; }
function l0Grid(xmax){ const g=[]; for(let c=0;c<=xmax+1e-9;c+=(c<24?1:(c<70?2:5))) g.push(c); return g; }
function l0Curves(xmax){
  const key=pgShopperKey()+"|"+xmax;
  if(l0Cache.key!==key){ const grid=l0Grid(xmax);
    l0Cache={key:key, grid:grid, own:{}, levels:L0_LEVELS.map(L=>{ const K=effConsts(Object.assign({},state,{equal_price_share:L})); return grid.map(c=>pgShareK(c,K)); })}; }
  const ek=state.equal_price_share.toFixed(4);
  if(!l0Cache.own[ek]){ l0Cache.own={}; l0Cache.own[ek]=l0Cache.grid.map(c=>pgShareK(c,KP)); }
  return {grid:l0Cache.grid, levels:l0Cache.levels, own:l0Cache.own[ek]};
}
function pgInterp(xs,ys,x){ if(x<=xs[0]) return ys[0]; for(let i=1;i<xs.length;i++){ if(x<=xs[i]){ const t=(x-xs[i-1])/(xs[i]-xs[i-1]); return ys[i-1]+t*(ys[i]-ys[i-1]); } } return ys[ys.length-1]; }
function pgCross(xs,ys,level){        // the cost at which a falling curve passes `level` (null if it never does)
  if(ys[0]<level) return null;
  for(let i=1;i<xs.length;i++){ if(ys[i]<level){ const t=(Math.log(ys[i-1])-Math.log(level))/(Math.log(ys[i-1])-Math.log(ys[i])); return xs[i-1]+t*(xs[i]-xs[i-1]); } }
  return null;
}
function pgWidth(id,dflt){ const e=document.getElementById(id); const w=e&&e.clientWidth?e.clientWidth:0; return w>0?w:(dflt||720); }
function l0Dots(f){          // the cases as (median cost, median share) with the 8-in-10 range of cost; the reader's own point when active
  const d=PG.cases.map(c=>{ const b=SC.bands[c.key].cost, s=PG.region_bands[c.key][state.region];
    return {key:c.key,label:c.label,x:b[1],lo:b[0],hi:b[2],y:s[1],sel:f.key===c.key}; });
  if(f.key==="own") d.push({key:"own",label:PG.own_label,x:f.cost,lo:f.cb?f.cb[0]:f.cost,hi:f.cb?f.cb[2]:f.cost,y:f.share,sel:true});
  return d;
}
function l0Draw(f){
  const svg=document.getElementById("l0chart"); if(!svg||!KP) return;
  f=f||pgFacts();
  const W=Math.max(300,pgWidth("l0plot",860)), small=W<560, H=small?350:420, mL=small?44:52, mR=small?10:16, mT=28, mB=small?46:42;
  const selx=f.cb?f.cb[2]:f.cost, xmax=Math.max(70,Math.ceil(selx*1.1/10)*10);
  const cv=l0Curves(xmax), grid=cv.grid;
  const X=v=>mL+(W-mL-mR)*Math.min(v,xmax)/xmax, ly=Math.log10(L0_Y[0]), hy=Math.log10(L0_Y[1]);
  const Y=v=>mT+(H-mT-mB)*(1-(Math.log10(Math.min(L0_Y[1],Math.max(L0_Y[0],v)))-ly)/(hy-ly));
  const path=ys=>grid.map((c,i)=>(i?"L":"M")+X(c).toFixed(1)+" "+Y(ys[i]).toFixed(1)).join(" ");
  let g='<rect x="'+mL+'" y="'+mT+'" width="'+(W-mL-mR)+'" height="'+(H-mT-mB)+'" fill="none"/>';
  // gridlines and y labels (log scale)
  [0.01,0.1,1,10].forEach(v=>{ g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+Y(v)+'" y2="'+Y(v)+'" style="stroke:var(--grid)"/>'+
    '<text x="'+(mL-6)+'" y="'+(Y(v)+4)+'" font-size="11" text-anchor="end">'+v+'%</text>'; });
  g+='<text x="'+(mL-6)+'" y="'+(Y(L0_Y[1])+4)+'" font-size="11" text-anchor="end">80%</text>';
  // the bands, light to dark
  for(let i=0;i<L0_LEVELS.length-1;i++){
    const lo=cv.levels[i], hi=cv.levels[i+1];
    let d=grid.map((c,k)=>(k?"L":"M")+X(c).toFixed(1)+" "+Y(hi[k]).toFixed(1)).join(" ");
    for(let k=grid.length-1;k>=0;k--) d+=" L"+X(grid[k]).toFixed(1)+" "+Y(lo[k]).toFixed(1);
    g+='<path d="'+d+' Z" style="fill:var(--b'+(i+1)+')"/>';
  }
  // axes
  g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+(H-mB)+'" y2="'+(H-mB)+'" style="stroke:var(--axis)"/>';
  const xstep=xmax>200?50:(xmax>100?(small?40:20):(small?20:10));
  for(let v=0;v<=xmax+1e-9;v+=xstep) g+='<text x="'+X(v)+'" y="'+(H-mB+15)+'" font-size="11" text-anchor="middle">$'+v+'</text>';
  g+='<text x="'+((mL+W-mR)/2)+'" y="'+(H-6)+'" font-size="11" text-anchor="middle">Cost to grow a kilo of cells</text>';
  g+='<text x="0" y="12" font-size="11" class="b">Long-run share of meat and seafood (log scale)</text>';
  // reference lines: plant-based meat today, and the cost at which the shop price matches everyday meat
  const yp=Y(f.pb), xp=X(f.parity);
  g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+yp+'" y2="'+yp+'" style="stroke:var(--ink);stroke-dasharray:2 3;stroke-width:1.2"/>'+
     '<text x="'+(W-mR-4)+'" y="'+(yp-5)+'" font-size="11" text-anchor="end" class="b" style="paint-order:stroke;stroke:var(--card);stroke-width:3px">'+(small?'plant-based today: ':'plant-based meat today: ')+pgAbout(f.pb)+'%</text>';
  g+='<line x1="'+xp+'" x2="'+xp+'" y1="'+mT+'" y2="'+(H-mB)+'" style="stroke:var(--ink);stroke-dasharray:2 3;stroke-width:1.2"/>'+
     '<text x="'+(xp+5)+'" y="'+(H-mB-8)+'" font-size="11" class="b" style="paint-order:stroke;stroke:var(--card);stroke-width:3px">'+(small?'same price as meat: ':'same shop price as everyday meat: ')+scMoney(f.parity)+'</text>';
  // the selected case's own setting
  g+='<path d="'+path(cv.own)+'" fill="none" style="stroke:var(--card);stroke-width:5"/><path d="'+path(cv.own)+'" fill="none" style="stroke:var(--caseline);stroke-width:2.5"/>';
  // the cases
  const dots=l0Dots(f), off=[];
  dots.forEach(d=>{
    if(d.x>xmax){ off.push(d); return; }
    const cx=X(d.x), low=d.y<L0_Y[0], cy=low?H-mB:Y(d.y), r=d.sel?6:4.5;
    if(d.hi>d.lo) g+='<line x1="'+X(d.lo)+'" x2="'+X(d.hi)+'" y1="'+cy+'" y2="'+cy+'" style="stroke:var(--card);stroke-width:5"/>'+
       '<line x1="'+X(d.lo)+'" x2="'+X(d.hi)+'" y1="'+cy+'" y2="'+cy+'" style="stroke:var(--ink);stroke-width:'+(d.sel?2:1.3)+'"/>'+
       '<line x1="'+X(d.lo)+'" x2="'+X(d.lo)+'" y1="'+(cy-4)+'" y2="'+(cy+4)+'" style="stroke:var(--ink);stroke-width:1.3"/>'+
       '<line x1="'+X(d.hi)+'" x2="'+X(d.hi)+'" y1="'+(cy-4)+'" y2="'+(cy+4)+'" style="stroke:var(--ink);stroke-width:1.3"/>';
    g+=d.key==="own"?'<rect x="'+(cx-r)+'" y="'+(cy-r)+'" width="'+(2*r)+'" height="'+(2*r)+'" transform="rotate(45 '+cx+' '+cy+')" style="fill:var(--ink);stroke:var(--card);stroke-width:2"/>'
                    :'<circle cx="'+cx+'" cy="'+cy+'" r="'+r+'" style="fill:'+(d.sel?'var(--ink)':'var(--card)')+';stroke:'+(d.sel?'var(--card)':'var(--ink)')+';stroke-width:2"/>';
    const txt=d.label+(low?" (under 0.003%)":""), wide=txt.length*6.4, right=cx+10+wide<W-mR;
    g+='<text x="'+(right?cx+10:cx-10)+'" y="'+(cy-9)+'" font-size="'+(d.sel?12:11)+'" text-anchor="'+(right?"start":"end")+'" class="b" style="paint-order:stroke;stroke:var(--card);stroke-width:3.5px'+(d.sel?'':';font-weight:400')+'">'+txt+'</text>';
  });
  if(off.length&&!small) g+='<text x="'+(W-mR)+'" y="12" font-size="11" text-anchor="end">'+off.map(d=>d.label+': about '+pgUSD(d.x)+' and '+pgPctS(d.y)).join("; ")+' (right of this chart) \u2192</text>';
  // the crosshair
  g+='<g id="l0cross" style="display:none" pointer-events="none"><line id="l0cl" y1="'+mT+'" y2="'+(H-mB)+'" style="stroke:var(--ink);stroke-width:1"/>'+
     '<circle id="l0cd" r="4.5" style="fill:var(--caseline);stroke:var(--card);stroke-width:2"/></g>'+
     '<rect id="l0hit" x="'+mL+'" y="'+mT+'" width="'+(W-mL-mR)+'" height="'+(H-mT-mB)+'" fill="transparent"/>';
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H); svg.setAttribute("tabindex","0");
  svg.innerHTML=g;
  l0Geo={W:W,H:H,mL:mL,mR:mR,mT:mT,mB:mB,xmax:xmax,X:X,Y:Y,cv:cv,f:f,at:null};
  l0Wire(svg);
  // the legend, the sentence that reads the chart, and the table behind it
  const lg=document.getElementById("l0legend");
  if(lg) lg.innerHTML='<span class="lt">Share of shoppers who would choose it at equal price, once it is familiar:</span>'+
    L0_LEVELS.slice(0,-1).map((L,i)=>'<span class="li"><span class="sw" style="background:var(--b'+(i+1)+')"></span>'+Math.round(L*100)+'–'+Math.round(L0_LEVELS[i+1]*100)+'%</span>').join("")+
    '<span class="li"><span class="ln"></span>'+(f.key==="own"?"your setting":"this case's own setting")+': '+Math.round(f.eqs*100)+'%</span>'+
    '<span class="li"><span class="dt"></span>a case: median cost and share, with the range for 8 in 10 draws of cost</span>'+
    '<span class="li"><span class="dn"></span>reference lines</span>';
  const one=pgCross(grid,cv.own,1), at10=[pgInterp(grid,cv.levels[0],10),pgInterp(grid,cv.levels[6],10)];
  const alt=document.getElementById("l0alt");
  if(alt) alt.innerHTML="<b>What the chart shows.</b> "+(one===null?"At a setting of "+Math.round(f.eqs*100)+"% the share stays under 1% at any cost on this chart. "
      :(one>=xmax?"At a setting of "+Math.round(f.eqs*100)+"% the share is above 1% across this chart. ":"At a setting of "+Math.round(f.eqs*100)+"% the share stays under 1% until a kilo of cells costs less than about "+pgUSD(one)+". "))+
    "Below that, how much shoppers like it matters as much as cost: at $10 a kilo the share is "+pgPctS(at10[0])+" if 5% would choose it at equal price and "+pgPctS(at10[1])+" if 70% would. "+
    dots.map(d=>d.label+": about "+pgUSD(d.x)+" a kilo and "+pgPctS(d.y)).join(". ")+". A dot can sit off the line, because it is the median of draws in which the shopper settings vary too.";
  const tb=document.getElementById("l0table");
  if(tb){ const rows=[5,10,15,20,30,40,50,70].concat(xmax>70?[100,150,200,300].filter(v=>v<=xmax):[]);
    tb.innerHTML='<table class="num"><thead><tr><th>Cost of a kilo of cells</th>'+L0_LEVELS.map(L=>'<th>'+Math.round(L*100)+'% at equal price</th>').join("")+'<th>'+Math.round(f.eqs*100)+'% (the line)</th></tr></thead><tbody>'+
      rows.map(c=>'<tr><td>$'+c+'</td>'+cv.levels.map(ys=>'<td>'+pgPctS(pgInterp(grid,ys,c))+'</td>').join("")+'<td>'+pgPctS(pgInterp(grid,cv.own,c))+'</td></tr>').join("")+
      '</tbody></table><p class="note">Long-run share of '+pgRegionOf()+' meat and seafood, at the shopper settings as set. Single estimates, not medians of draws.</p>'; }
}
function l0Show(cost){
  const G=l0Geo, tip=document.getElementById("l0tip"), cr=document.getElementById("l0cross"); if(!G||!tip||!cr) return;
  cost=Math.max(0,Math.min(G.xmax,cost)); G.at=cost;
  const own=pgInterp(G.cv.grid,G.cv.own,cost), x=G.X(cost);
  cr.style.display=""; const l=document.getElementById("l0cl"); l.setAttribute("x1",x); l.setAttribute("x2",x);
  const d=document.getElementById("l0cd"); d.setAttribute("cx",x); d.setAttribute("cy",G.Y(own));
  const shop=shelfPrice(cost,state);
  tip.innerHTML='<b>$'+cost.toFixed(0)+' a kilo of cells</b><br>'+pgUSD(shop)+' in the shop, '+(shop/G.f.conv).toFixed(1)+' times meat'+
    '<div class="tr"><span><span class="sw" style="background:var(--caseline)"></span>at '+Math.round(G.f.eqs*100)+'% (the line)</span><b>'+pgPctS(own)+'</b></div>'+
    '<div class="tr" style="margin-top:3px"><span>if the share at equal price were</span><span></span></div>'+
    L0_LEVELS.slice().reverse().map((L,i)=>{ const k=L0_LEVELS.length-1-i; return '<div class="tr"><span>'+Math.round(L*100)+'%</span><span>'+pgPctS(pgInterp(G.cv.grid,G.cv.levels[k],cost))+'</span></div>'; }).join("");
  tip.style.display="block";
  const tw=tip.offsetWidth||200, left=x+14+tw>G.W?x-14-tw:x+14;
  tip.style.left=Math.max(0,left)+"px"; tip.style.top=(G.mT+6)+"px";
}
function l0Hide(){ const tip=document.getElementById("l0tip"), cr=document.getElementById("l0cross"); if(tip) tip.style.display="none"; if(cr) cr.style.display="none"; }
function l0Wire(svg){
  if(svg._wired||!svg.addEventListener) return; svg._wired=true;
  const move=e=>{ const G=l0Geo; if(!G) return; const r=svg.getBoundingClientRect(), px=(e.clientX-r.left)*G.W/r.width;
    if(px<G.mL-4||px>G.W-G.mR+4){ l0Hide(); return; } l0Show((px-G.mL)/(G.W-G.mL-G.mR)*G.xmax); };
  svg.addEventListener("pointermove",move); svg.addEventListener("pointerdown",move); svg.addEventListener("pointerleave",l0Hide);
  svg.addEventListener("focus",()=>{ if(l0Geo) l0Show(l0Geo.at===null?Math.min(l0Geo.xmax,l0Geo.f.cost):l0Geo.at); });
  svg.addEventListener("blur",l0Hide);
  svg.addEventListener("keydown",e=>{ if(!l0Geo) return; const step=e.shiftKey?10:1;
    if(e.key==="ArrowLeft"){ l0Show((l0Geo.at===null?l0Geo.f.cost:l0Geo.at)-step); e.preventDefault(); }
    if(e.key==="ArrowRight"){ l0Show((l0Geo.at===null?l0Geo.f.cost:l0Geo.at)+step); e.preventDefault(); }
    if(e.key==="Escape") l0Hide(); });
}

/* ---------- Level 1: what each case assumes, and the steps between the cases ---------- */
function pgTag(t){ return '<span class="tag">'+t+'</span>'; }
function scTagChip(t){ return pgTag(SC.tag_plain[t]); }
function l1Render(){
  const f=pgFacts(), host=document.getElementById("l1_case"); if(!host) return;
  const c=pgCaseDef(f.key==="own"?PGS.base:f.key);
  host.innerHTML='<h3>'+c.label+'</h3>'+(f.key==="own"?'<p class="callout">You have changed settings, so the page shows your own case. The text below describes '+
    pgCaseWords({key:c.key,label:c.label})+', which you started from.</p>':'')+c.text;
  const L=PG.ladder, max=Math.ceil(L[0].cost[2]*1.05/10)*10, pc=v=>(Math.min(v,max)/max*100).toFixed(2)+"%";
  const par=parityCost(state);
  let h='', rowsT='';
  L.forEach((s,i)=>{
    const prev=i?L[i-1].cost[1]:null, med=s.cost[1];
    const save=i?'Saves about '+pgUSD(prev-med)+'.':'The starting point.';
    h+='<div class="hb'+(s.key===f.key?' sel':'')+'"><div class="hl"><b>'+(i+1)+'. '+s.name+'.</b> '+pgTag(s.tag)+'<br><span class="hv">About '+pgUSD(med)+' a kilo (8 in 10 draws: $'+
       Math.round(s.cost[0])+'–'+Math.round(s.cost[2])+'). '+save+'</span></div><div class="ht">'+
       '<span class="vline" style="left:'+pc(par)+'"></span>'+
       (i?'<span class="bar save" style="left:'+pc(med)+';width:'+((prev-med)/max*100).toFixed(2)+'%"></span>':'')+
       '<span class="bar" style="left:0;width:'+pc(med)+'"></span>'+
       '<span class="wh" style="left:'+pc(s.cost[0])+';width:'+((s.cost[2]-s.cost[0])/max*100).toFixed(2)+'%"></span>'+
       '<span class="dotm" style="left:'+pc(med)+'"></span></div></div>';
    rowsT+='<tr><td>'+(i+1)+'. '+s.name+'</td><td>'+s.tag+'</td><td>'+pgUSD(med)+'</td><td>$'+Math.round(s.cost[0])+'–'+Math.round(s.cost[2])+'</td><td>'+scMoney(s.point)+'</td><td>'+(i?pgUSD(prev-med):'')+'</td></tr>';
  });
  const ticks=[]; for(let v=0;v<=max;v+=(max>120?50:20)) ticks.push(v);
  h+='<div class="hb axis"><div class="hl"><span class="hv">Solid bar: cost after the step. Pale bar: what the step saves. Dot and thin line: the median and the range for 8 in 10 draws. '+
     'Dotted line: '+scMoney(par)+', where the shop price matches everyday meat.</span></div><div class="ht">'+ticks.map(v=>'<span class="tk" style="left:'+pc(v)+'">$'+v+'</span>').join("")+'</div></div>';
  const ch=document.getElementById("l1chart"); if(ch) ch.innerHTML=h;
  const first=L[0].cost[1], cen=L[2].cost[1], last=L[L.length-1].cost[1];
  const alt=document.getElementById("l1alt");
  if(alt) alt.innerHTML="<b>What the chart shows.</b> The cost falls from about "+pgUSD(first)+" a kilo to about "+pgUSD(last)+". Of that fall, "+
    Math.round((first-L[3].cost[1])/(first-last)*100)+"% comes before any genetic engineering: "+pgUSD(first-L[1].cost[1])+" from the process and cheaper inputs, "+
    pgUSD(L[1].cost[1]-cen)+" from selected cells and "+pgUSD(cen-L[3].cost[1])+" from a cheaper plant. The last step, to the Best case, saves "+pgUSD(L[3].cost[1]-last)+
    " and needs engineered cells. "+(last>par?"No step reaches ":"The last step passes ")+scMoney(par)+", the cost at which the shop price matches everyday meat.";
  const tb=document.getElementById("l1table");
  if(tb) tb.innerHTML='<table class="num"><thead><tr><th>Step</th><th>What it needs</th><th>Median cost, a kilo of cells</th><th>8 in 10 draws</th><th>Most-likely-values cost</th><th>Saved by the step</th></tr></thead><tbody>'+rowsT+'</tbody></table>';
}

/* ---------- Level 2: what would move it most ---------- */
function l2Fmt(e,v){ const x=v*(e.scale||1); const d=e.digits!=null?e.digits:(Math.abs(x)>=100?0:(Math.abs(x)>=10?1:2));
  return (e.pre||"")+(+x.toFixed(d)).toLocaleString("en-US")+(e.unit?(e.unit.charAt(0)==="%"?"":" ")+e.unit:""); }
function l2Rows(){
  const ch=SCS.choice, p0=scParams(ch), base=scEval(ch).total, bsh=scShare(base,state.region), rows=[];
  // a setting whose column loop fails the page's two checks is said to fail them, so a saving that needs it is not read as free
  const loopFails=(k,v)=>{ const d=scEval(Object.assign({},ch,{[k]:v})).column; return !!(d&&(d.ph_vs_safe>1+1e-9||!d.passes_tested)); };
  const lab=(k,v)=>scSetting(k,v).label+(loopFails(k,v)?"; this fails the checks on the column's loop":"");
  scPriorities(ch,false).forEach(r=>{ const sw=scSwitch(r.switch);
    rows.push({kind:"choice", id:"sw_"+r.switch, name:sw.name, what:sw.q+".", now:scSetting(r.switch,r.now).label,
      lo:r.costs[r.best], hi:r.costs[r.worst], loT:lab(r.switch,r.best), hiT:lab(r.switch,r.worst),
      why:scSetting(r.switch,r.now).note, tag:"a choice"}); });
  PG.estimates.forEach(e=>{ if(e.cells&&e.cells.indexOf(ch.cells)<0) return;
    const a=floorExplore(Object.assign({},p0,{[e.arg]:e.lo})).total, b=floorExplore(Object.assign({},p0,{[e.arg]:e.hi})).total;
    const lo=Math.min(a,b), hi=Math.max(a,b), now=p0[e.arg];
    rows.push({kind:"estimate", id:"es_"+e.arg, name:e.name, what:"", now:null, lo:lo, hi:hi, loT:l2Fmt(e,a<=b?e.lo:e.hi), hiT:l2Fmt(e,a<=b?e.hi:e.lo),
      why:e.why, tag:"an estimate nobody has measured at scale"}); });
  rows.forEach(r=>{ r.shLo=scShare(r.lo,state.region); r.shHi=scShare(r.hi,state.region); });
  const cost=rows.filter(r=>r.hi-r.lo>=0.05).sort((x,y)=>(y.hi-y.lo)-(x.hi-x.lo)), none=rows.filter(r=>r.hi-r.lo<0.05);
  // the judgements about shoppers: they move the share, not the cost
  const rk=(PGS.base==="best")?"best":"central", dem=[];
  PG.judgements.forEach(j=>{ const rg=j.ranges[rk]; let a,b;
    if(j.key==="cut_cells"){ a=pgShareK(base,KP,{cut_cells:rg[0]}); b=pgShareK(base,KP,{cut_cells:rg[1]}); }
    else { a=pgShareK(base,effConsts(Object.assign({},state,{[j.key]:rg[0]}))); b=pgShareK(base,effConsts(Object.assign({},state,{[j.key]:rg[1]}))); }
    const f=v=>j.fmt==="pct"?Math.round(v*100)+"%":(+v.toFixed(1))+" times";
    dem.push({kind:"judgement", id:"jd_"+j.key, name:j.name, lo:Math.min(a,b), hi:Math.max(a,b), loT:f(a<=b?rg[0]:rg[1]), hiT:f(a<=b?rg[1]:rg[0]),
      nowT:f(state[j.key]), why:j.why, tag:"a judgement about shoppers"}); });
  dem.sort((x,y)=>Math.log(Math.max(y.hi,1e-6)/Math.max(y.lo,1e-6))-Math.log(Math.max(x.hi,1e-6)/Math.max(x.lo,1e-6)));
  return {base:base, bsh:bsh, cost:cost, none:none, dem:dem};
}
function l2Pick(id){ PGS.l2sel=(PGS.l2sel===id?null:id); l2Render(); }
function l2Render(){
  const host=document.getElementById("l2chart"); if(!host||!KP) return;
  const R=l2Rows(), f=pgFacts(), base=R.base;
  const ext=R.cost.map(r=>r.hi).sort((a,b)=>b-a);
  const xmax=Math.max(base*1.3,Math.min(ext[0]||base,Math.max(base*2.2,(ext[1]||base)*1.1))), xmin=Math.max(0,Math.min.apply(null,R.cost.map(r=>r.lo).concat([base]))*0.9);
  const pc=v=>((Math.min(Math.max(v,xmin),xmax)-xmin)/(xmax-xmin)*100).toFixed(2)+"%", wd=(a,b)=>((Math.min(b,xmax)-Math.max(a,xmin))/(xmax-xmin)*100).toFixed(2)+"%";
  let h='<div class="hbh">What moves the cost of a kilo of cells. Start: '+scMoney(base)+' with every estimate at its most likely value.</div>';
  R.cost.forEach(r=>{ const sel=PGS.l2sel===r.id;
    h+='<div class="hb click'+(sel?' sel':'')+'" role="button" tabindex="0" aria-expanded="'+sel+'" onclick="l2Pick(\''+r.id+'\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();l2Pick(\''+r.id+'\')}">'+
       '<div class="hl"><b>'+r.name+'</b> '+pgTag(r.tag)+'<br><span class="hv">'+
       (r.lo<base-0.05?'Down to '+scMoney(r.lo)+' ('+r.loT+')':'No lower than now')+'. '+(r.hi>base+0.05?'Up to '+scMoney(r.hi)+' ('+r.hiT+')'+(r.hi>xmax?', off the scale':''):'No higher than now')+'.</span></div>'+
       '<div class="ht"><span class="vbase" style="left:'+pc(base)+'"></span>'+
       (r.lo<base-0.05?'<span class="bar dn" style="left:'+pc(r.lo)+';width:'+wd(r.lo,base)+'"></span>':'')+
       (r.hi>base+0.05?'<span class="bar up'+(r.hi>xmax?' clip':'')+'" style="left:'+pc(base)+';width:'+wd(base,r.hi)+'"></span>':'')+'</div></div>'; });
  const tick=[]; const step=(xmax-xmin)>120?50:((xmax-xmin)>50?20:((xmax-xmin)>20?10:5));
  for(let v=Math.ceil(xmin/step)*step;v<=xmax;v+=step) tick.push(v);
  h+='<div class="hb axis"><div class="hl"><span class="hv">Bars left of the line lower the cost, bars right of it raise it. Select a row for what it is and where its range comes from.</span></div>'+
     '<div class="ht">'+tick.map(v=>'<span class="tk" style="left:'+pc(v)+'">$'+v+'</span>').join("")+'</div></div>';
  if(R.none.length) h+='<p class="note">No effect on this case: '+R.none.map(r=>r.name.toLowerCase()).join("; ")+'.</p>';
  // the shopper block, on a log scale of share
  const lmin=Math.log10(L0_Y[0]), lmax=Math.log10(L0_Y[1]), ps=v=>((Math.log10(Math.min(L0_Y[1],Math.max(L0_Y[0],v)))-lmin)/(lmax-lmin)*100);
  h+='<div class="hbh">What moves the long-run share at that cost. Start: '+pgPctS(R.bsh)+' of '+pgRegionOf()+' meat and seafood.</div>';
  R.dem.forEach(r=>{ const sel=PGS.l2sel===r.id;
    h+='<div class="hb click'+(sel?' sel':'')+'" role="button" tabindex="0" aria-expanded="'+sel+'" onclick="l2Pick(\''+r.id+'\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();l2Pick(\''+r.id+'\')}">'+
       '<div class="hl"><b>'+r.name+'</b> '+pgTag(r.tag)+'<br><span class="hv">Now '+r.nowT+'. Share '+pgPctS(r.lo)+' at '+r.loT+', and '+pgPctS(r.hi)+' at '+r.hiT+'.</span></div>'+
       '<div class="ht"><span class="bar sh" style="left:'+ps(r.lo).toFixed(2)+'%;width:'+Math.max(0.6,ps(r.hi)-ps(r.lo)).toFixed(2)+'%"></span><span class="vbase" style="left:'+ps(R.bsh).toFixed(2)+'%"></span></div></div>'; });
  h+='<div class="hb axis"><div class="hl"><span class="hv">Each bar runs from the share at one end of the range to the share at the other. The line is the share now. Log scale.</span></div>'+
     '<div class="ht">'+[0.01,0.1,1,10].map(v=>'<span class="tk" style="left:'+ps(v).toFixed(2)+'%">'+v+'%</span>').join("")+'</div></div>';
  host.innerHTML=h;
  const sub=document.getElementById("l2sub");
  if(sub) sub.innerHTML="For "+pgCaseWords(f)+", "+pgRegionName()+". These are single estimates, so the starting cost is the most-likely-values figure ("+scMoney(base)+
    "), not the median of the draws"+(f.cb?" ("+pgUSD(f.cb[1])+")":"")+"."+(SCS.src==="custom"?" Your case comes from “All the levers”; this chart follows the ten switches, which that panel does not set.":"");
  const all=R.cost.concat(R.dem), s=all.find(r=>r.id===PGS.l2sel), card=document.getElementById("l2card");
  if(card){ card.style.display=s?"":"none";
    if(s) card.innerHTML='<p><b>'+s.name+'.</b> '+pgTag(s.tag)+'</p>'+
      (s.kind==="choice"?'<p>'+s.what+' Now: '+s.now+'. '+s.why+'</p><p>Cheapest setting: '+s.loT+', '+scMoney(s.lo)+' a kilo and a long-run share of '+pgPctS(s.shLo)+
          '. Dearest setting: '+s.hiT+', '+scMoney(s.hi)+' and '+pgPctS(s.shHi)+'. Change it under <a href="#engineering">Check the engineering</a>.</p>'
       :s.kind==="estimate"?'<p>Range: '+s.loT+' gives '+scMoney(s.lo)+' a kilo (share '+pgPctS(s.shLo)+'); '+s.hiT+' gives '+scMoney(s.hi)+' (share '+pgPctS(s.shHi)+').</p><p>Where the value comes from: '+s.why+'.</p>'
       :'<p>'+s.why+'</p><p>At '+s.loT+' the long-run share is '+pgPctS(s.lo)+'. At '+s.hiT+' it is '+pgPctS(s.hi)+'. Change it under <a href="#shoppers">Check the shopper model</a>.</p>'); }
  const tb=document.getElementById("l2table");
  if(tb) tb.innerHTML='<table class="num"><thead><tr><th>What moves</th><th>Kind</th><th>Favourable end</th><th>Cost there</th><th>Share there</th><th>Unfavourable end</th><th>Cost there</th><th>Share there</th></tr></thead><tbody>'+
    R.cost.map(r=>'<tr><td>'+r.name+'</td><td>'+r.tag+'</td><td>'+r.loT+'</td><td>'+scMoney(r.lo)+'</td><td>'+pgPctS(r.shLo)+'</td><td>'+r.hiT+'</td><td>'+scMoney(r.hi)+'</td><td>'+pgPctS(r.shHi)+'</td></tr>').join("")+
    R.dem.map(r=>'<tr><td>'+r.name+'</td><td>'+r.tag+'</td><td>'+r.hiT+'</td><td>'+scMoney(base)+'</td><td>'+pgPctS(r.hi)+'</td><td>'+r.loT+'</td><td>'+scMoney(base)+'</td><td>'+pgPctS(r.lo)+'</td></tr>').join("")+'</tbody></table>';
}

/* ---------- Level 3: where and when ---------- */
function l3Name(n){ n=n.replace("proc.","processed").replace("ground/","minced or "); return n.charAt(0).toUpperCase()+n.slice(1); }
function l3Render(){
  const host=document.getElementById("l3types"); if(!host||!KP) return;
  const f=pgFacts(), s=state, p=penetration(s), market=MODEL.markets[s.region], bases=speciesBases(market);
  let Wvol=0; market.forEach(mt=>{Wvol+=mt.w_vol;});
  const rows=p.rows.map(r=>({name:l3Name(r.mt.name), kind:r.t==="basic"?"mince or processed":(r.t==="premium"?"a premium cut":"a cut or fillet"), R:r.R, sh:r.sh*100,
    w:r.mt.w_vol/Wvol*100, part:r.mt.w_vol/Wvol*r.sh*100, price:r.mt.p_conv})).sort((a,b)=>b.part-a.part);
  const top=Math.max.apply(null,rows.map(r=>r.sh)), nice=[0.01,0.02,0.04,0.1,0.2,0.4,1,2,4,10,20,40,100], max=nice.find(v=>v>=top*1.05)||100;
  const pc=v=>(Math.min(v,max)/max*100).toFixed(2)+"%";
  let h=rows.map(r=>'<div class="hb"><div class="hl"><b>'+r.name+'</b> '+pgTag(r.kind)+'<br><span class="hv">'+pgPctS(r.sh)+' of this type. It is '+r.w.toFixed(1)+
      '% of all meat and seafood, and cultivated costs '+r.R.toFixed(1)+' times its $'+r.price.toFixed(0)+' a kilo.</span></div><div class="ht"><span class="bar" style="left:0;width:'+pc(r.sh)+'"></span></div></div>').join("");
  h+='<div class="hb axis"><div class="hl"><span class="hv">Bar: the share of each type of meat that cultivated meat takes in the long run. Types are in order of how much they add to the total.</span></div>'+
     '<div class="ht">'+[0,0.25,0.5,0.75,1].map(t=>'<span class="tk" style="left:'+(t*100)+'%">'+(+(max*t).toPrecision(2))+'%</span>').join("")+'</div></div>';
  host.innerHTML=h;
  const total=p.tv*100, set=(id,t)=>{ const e=document.getElementById(id); if(e) e.innerHTML=t; };
  const basis=(f.cb?"the median cost of "+pgUSD(f.cost)+" a kilo":"a cost of "+scMoney(f.cost)+" a kilo")+" and the shopper settings as set";
  set("l3_intro","Cultivated meat costs about the same whatever animal it copies, but conventional prices differ. So it competes where meat is dear and stays out where meat is cheap. "+
    "Everything in this level is a single estimate at "+basis+". It adds up to "+pgPctS(total)+" of "+pgRegionOf()+" meat and seafood by weight ("+pgPctS(p.tval*100)+" by value)."+
    (f.sb?" The headline "+pgPctS(f.share)+" is the median of draws in which the shopper settings vary as well, so the two differ.":""));
  set("l3asub",pgRegionName()+", "+pgCaseWords(f)+". A cut is "+Math.round(s.cut_cells*100)+"% cells bound with plant protein, so shoppers like it a little less than mince, and premium products less again.");
  const t3=rows.slice(0,3), dear=rows.filter(r=>/chicken|pork/i.test(r.name)&&!/organic|heritage/i.test(r.name));
  set("l3aalt","<b>What the chart shows.</b> The three types that add most to the total are "+t3.map(r=>r.name.toLowerCase()+" ("+pgPctS(r.sh)+" of the type)").join(", ")+
    ". "+(dear.length?"Ordinary chicken and pork stay at "+pgRange(Math.min.apply(null,dear.map(r=>r.R)),Math.max.apply(null,dear.map(r=>r.R)),v=>v.toFixed(1))+" times the conventional price.":""));
  set("l3atable",'<table class="num"><thead><tr><th>Type of meat</th><th>Kind</th><th>Conventional price, a kilo</th><th>Cultivated price, as a multiple</th><th>Share of the type</th><th>The type\'s share of all meat and seafood</th><th>Adds to the total</th></tr></thead><tbody>'+
    rows.map(r=>'<tr><td>'+r.name+'</td><td>'+r.kind+'</td><td>$'+r.price.toFixed(1)+'</td><td>'+r.R.toFixed(2)+'</td><td>'+pgPctS(r.sh)+'</td><td>'+r.w.toFixed(1)+'%</td><td>'+pgPctS(r.part)+'</td></tr>').join("")+'</tbody></table>');
  // regions
  const named=f.key!=="own";
  set("l3rsub",named?"The median of the draws for "+pgCaseWords(f)+", with the range that holds 8 in 10 draws. The same draws of cost are used for every region."
                    :"Single estimates at your settings. There are no draws for settings you have changed.");
  set("l3regions",'<table class="num"><thead><tr><th>Region</th><th>Long-run share of meat and seafood'+(named?", median":"")+'</th>'+(named?'<th>8 in 10 draws</th>':'')+'</tr></thead><tbody>'+
    PG.regions.map(r=>{ if(named){ const b=PG.region_bands[f.key][r[0]]; return '<tr><td>'+r[1]+'</td><td><b>'+pgPctS(b[1])+'</b></td><td>'+(b[2]<0.00095?"under 0.001%":pgPct(b[0])+"% to "+pgPct(b[2])+"%")+'</td></tr>'; }
      return '<tr><td>'+r[1]+'</td><td><b>'+pgPctS(scShare(f.cost,r[0]))+'</b></td></tr>'; }).join("")+'</tbody></table>');
  l3Time(f,total);
}
let l3Geo=null;
function l3Path(years){          // the whole market's path: rollout (Bass) times the long-run share at each year's wariness
  const s=state, x=[], pb=[]; let F=0, E=0, t90=null;
  const at=(nx,np)=>{ const r=penetration(Object.assign({},s,{neophobia_x:nx,neophobia_p:np})); return [r.tv*100,r.tvp*100]; };
  const L=at(s.neophobia_x,s.neophobia_p);
  for(let k=0;k<=200;k++){
    const nx=s.neophobia_x+(s.neophobia_x0-s.neophobia_x)*Math.exp(-s.accept_rate*E), np=s.neophobia_p+(s.neophobia_p0-s.neophobia_p)*Math.exp(-s.accept_rate*E);
    if(k<=years||t90===null){ const v=at(nx,np); if(k<=years){ x.push(F*v[0]); pb.push(F*v[1]); } if(t90===null&&L[0]>0&&F*v[0]>=0.9*L[0]) t90=k; }
    if(k>years&&t90!==null) break;
    const dF=(s.p_innov+s.q_imit*F)*(1-F); F=Math.min(1,F+dF); E+=F;
  }
  return {x:x,pb:pb,ceil:L[0],pbL:L[1],t90:t90};
}
function l3Time(f,total){
  const svg=document.getElementById("l3time"); if(!svg) return;
  const yrs=40, P=l3Path(yrs), W=Math.max(300,pgWidth("l3tplot",860)), small=W<560, H=small?280:320, mL=small?52:58, mR=small?12:150, mT=18, mB=40;
  const showPb=P.pbL<=P.ceil*3, top=Math.max(P.ceil,showPb?Math.max.apply(null,P.pb):0)*1.12||1;
  const nice=[0.0001,0.0002,0.0004,0.001,0.002,0.004,0.01,0.02,0.04,0.1,0.2,0.4,1,2,4,10,20,40,100], ymax=nice.find(v=>v>=top)||100;
  const X=k=>mL+(W-mL-mR)*k/yrs, Y=v=>mT+(H-mT-mB)*(1-Math.min(v,ymax)/ymax), fy=v=>(+v.toPrecision(2))+"%";
  let g='';
  [0,0.25,0.5,0.75,1].forEach(t=>{ const v=ymax*t; g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+Y(v)+'" y2="'+Y(v)+'" style="stroke:var(--grid)"/><text x="'+(mL-6)+'" y="'+(Y(v)+4)+'" font-size="11" text-anchor="end">'+fy(v)+'</text>'; });
  g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+(H-mB)+'" y2="'+(H-mB)+'" style="stroke:var(--axis)"/>';
  for(let k=0;k<=yrs;k+=(small?10:5)) g+='<text x="'+X(k)+'" y="'+(H-mB+15)+'" font-size="11" text-anchor="middle">'+k+'</text>';
  g+='<text x="'+((mL+W-mR)/2)+'" y="'+(H-6)+'" font-size="11" text-anchor="middle">Years since it went on sale</text>';
  const line=a=>a.map((v,k)=>(k?"L":"M")+X(k).toFixed(1)+" "+Y(v).toFixed(1)).join(" ");
  g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+Y(P.ceil)+'" y2="'+Y(P.ceil)+'" style="stroke:var(--s1);stroke-dasharray:6 4;stroke-width:1.3"/>';
  if(showPb) g+='<path d="'+line(P.pb)+'" fill="none" style="stroke:var(--s2);stroke-width:2"/>';
  g+='<path d="'+line(P.x)+'" fill="none" style="stroke:var(--s1);stroke-width:2.5"/>';
  if(P.t90!==null&&P.t90<=yrs) g+='<line x1="'+X(P.t90)+'" x2="'+X(P.t90)+'" y1="'+Y(P.x[P.t90])+'" y2="'+(H-mB)+'" style="stroke:var(--ink);stroke-dasharray:2 3"/>'+
     '<circle cx="'+X(P.t90)+'" cy="'+Y(P.x[P.t90])+'" r="4.5" style="fill:var(--s1);stroke:var(--card);stroke-width:2"/>'+
     '<text x="'+(X(P.t90)+(X(P.t90)+190>W-mR?-8:8))+'" y="'+(Y(P.x[P.t90])+18)+'" font-size="11" text-anchor="'+(X(P.t90)+190>W-mR?"end":"start")+'" class="b" style="paint-order:stroke;stroke:var(--card);stroke-width:3px">year '+P.t90+': nine tenths of the way</text>';
  if(small){ g+='<text x="'+(W-mR-2)+'" y="'+(Y(P.ceil)-5)+'" font-size="11" text-anchor="end" class="b" style="paint-order:stroke;stroke:var(--card);stroke-width:3px">long-run share '+pgPctS(P.ceil)+'</text>'; }
  else { g+='<text x="'+(W-mR+8)+'" y="'+(Y(P.ceil)-2)+'" font-size="11" class="b">long-run share</text><text x="'+(W-mR+8)+'" y="'+(Y(P.ceil)+12)+'" font-size="11">'+pgPctS(P.ceil)+'</text>';
    const ye=Y(P.x[yrs]); g+='<text x="'+(W-mR+8)+'" y="'+(Math.max(ye,Y(P.ceil)+28)+4)+'" font-size="11" class="b">cultivated meat</text>';
    if(showPb) g+='<text x="'+(W-mR+8)+'" y="'+(Y(P.pb[yrs])+(Math.abs(Y(P.pb[yrs])-ye)<30?(Y(P.pb[yrs])<ye?-22:44):4))+'" font-size="11" class="b">plant-based meat</text>'; }
  g+='<g id="l3cross" style="display:none" pointer-events="none"><line id="l3cl" y1="'+mT+'" y2="'+(H-mB)+'" style="stroke:var(--ink);stroke-width:1"/><circle id="l3cd" r="4.5" style="fill:var(--s1);stroke:var(--card);stroke-width:2"/></g>'+
     '<rect x="'+mL+'" y="'+mT+'" width="'+(W-mL-mR)+'" height="'+(H-mT-mB)+'" fill="transparent"/>';
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H); svg.setAttribute("tabindex","0"); svg.innerHTML=g;
  l3Geo={W:W,mL:mL,mR:mR,mT:mT,yrs:yrs,X:X,Y:Y,P:P,showPb:showPb,at:null};
  if(!svg._wired&&svg.addEventListener){ svg._wired=true;
    const show=k=>{ const G=l3Geo, tip=document.getElementById("l3ttip"); if(!G||!tip) return; k=Math.max(0,Math.min(G.yrs,Math.round(k))); G.at=k;
      document.getElementById("l3cross").style.display=""; const l=document.getElementById("l3cl"); l.setAttribute("x1",G.X(k)); l.setAttribute("x2",G.X(k));
      const d=document.getElementById("l3cd"); d.setAttribute("cx",G.X(k)); d.setAttribute("cy",G.Y(G.P.x[k]));
      tip.innerHTML='<b>Year '+k+'</b><div class="tr"><span>cultivated meat</span><b>'+pgPctS(G.P.x[k])+'</b></div>'+(G.showPb?'<div class="tr"><span>plant-based meat</span><span>'+pgPctS(G.P.pb[k])+'</span></div>':'')+
        '<div class="tr"><span>long-run share</span><span>'+pgPctS(G.P.ceil)+'</span></div>';
      tip.style.display="block"; const tw=tip.offsetWidth||190, x=G.X(k); tip.style.left=Math.max(0,x+14+tw>G.W?x-14-tw:x+14)+"px"; tip.style.top=(G.mT+4)+"px"; };
    const hide=()=>{ const t=document.getElementById("l3ttip"), c=document.getElementById("l3cross"); if(t) t.style.display="none"; if(c) c.style.display="none"; };
    const move=e=>{ const G=l3Geo; if(!G) return; const r=svg.getBoundingClientRect(), px=(e.clientX-r.left)*G.W/r.width; if(px<G.mL-4||px>G.W-G.mR+4){ hide(); return; } show((px-G.mL)/(G.W-G.mL-G.mR)*G.yrs); };
    svg.addEventListener("pointermove",move); svg.addEventListener("pointerdown",move); svg.addEventListener("pointerleave",hide);
    svg.addEventListener("focus",()=>show(l3Geo&&l3Geo.at!==null?l3Geo.at:10)); svg.addEventListener("blur",hide);
    svg.addEventListener("keydown",e=>{ if(!l3Geo) return; if(e.key==="ArrowLeft"){ show((l3Geo.at||0)-1); e.preventDefault(); } if(e.key==="ArrowRight"){ show((l3Geo.at||0)+1); e.preventDefault(); } }); }
  const set=(id,t)=>{ const e=document.getElementById(id); if(e) e.innerHTML=t; };
  set("l3tsub",pgRegionName()+", "+pgCaseWords(f)+". The solid line is cultivated meat's share of all meat and seafood, year by year. The dashed line is the long-run share it climbs towards."+
    (showPb?" The second line is plant-based meat under the same rules.":""));
  set("l3talt","<b>What the chart shows.</b> The share is "+pgPctS(P.x[10])+" after 10 years, "+pgPctS(P.x[20])+" after 20 and "+pgPctS(P.x[yrs])+" after "+yrs+", against a long-run share of "+pgPctS(P.ceil)+". "+
    (P.t90===null?"It does not get nine tenths of the way within 200 years.":"It gets nine tenths of the way in year "+P.t90+".")+
    (showPb?" Plant-based meat levels off at "+pgPctS(P.pbL)+", because its taste and price gaps do not fade.":" Plant-based meat levels off at "+pgPctS(P.pbL)+", above the top of this chart: its taste and price gaps do not fade, so it stalls there."));
}

/* ---------- Level 4: the ten switches, where the cost goes, two switches together ---------- */
function scBuild(){
  const host=document.getElementById("sc_switches"); if(!host) return;
  host.innerHTML="";
  SC.switches.forEach(sw=>{
    const d=document.createElement("div"); d.className="ctl scsw";
    d.innerHTML='<label for="sc_sel_'+sw.key+'"><span class="nm">'+sw.name+'</span></label><select id="sc_sel_'+sw.key+'" onchange="scPick(\''+sw.key+'\',this.value)">'+
      sw.settings.map(t=>'<option value="'+t.key+'">'+t.label+'</option>').join("")+'</select>'+
      '<p class="fxn" id="sc_note_'+sw.key+'"></p>';
    host.appendChild(d); });
  const a=document.getElementById("sc_ga"), b=document.getElementById("sc_gb");
  [a,b].forEach(sel=>{ if(sel) sel.innerHTML=SC.switches.map(sw=>'<option value="'+sw.key+'">'+sw.name+'</option>').join(""); });
  const fs=document.getElementById("fx_sc");
  if(fs) fs.innerHTML='<option value="">Humbird\'s optimistic design</option>'+PG.cases.map(c=>'<option value="'+c.key+'">'+c.label+'</option>').join("");
}
function scResultHTML(ch,r){
  const f=pgFacts(), cost=r.total;
  const lim=(SC.limit_plain[r.limit]||r.limit).replace("CO2","CO₂");
  const med=(SC.medium_plain[r.medium_set_by]||r.medium_set_by);
  const need=scNeeds(ch).filter(x=>x[2]!=="nothing new");
  let h='<p><b>'+f.label+': '+scMoney(cost)+' a kilo of cells with every estimate at its most likely value.</b> '+
    (f.cb?'The median of the draws is '+pgUSD(f.cb[1])+' (8 in 10 draws between $'+Math.round(f.cb[0])+' and $'+Math.round(f.cb[2])+'), and that is the figure the rest of the page uses.'
         :'There are no draws for switches you have changed, so the rest of the page uses this figure.')+'</p>'+
    '<p>The tank holds '+r.density.toFixed(0)+' g of cells a litre, limited by <b>'+lim+'</b>, and works '+(r.uptime*100).toFixed(0)+'% of the year. '+
    ((r.column&&r.limit==="oxygen supply")?'Oxygen, not CO₂, limits it because the column beside the tank takes the CO₂ out, and antifoam takes a quarter of the oxygen the bubbles deliver. Without the column, CO₂ would limit it first. ':'')+
    'Each kilo of cells needs '+r.medium_l.toFixed(0)+' litres of medium, set by <b>'+med+'</b>.</p>';
  if(need.length){ h+='<p class="scneed"><b>What has to go right:</b> '+need.map(x=>x[1]+' ('+SC.tag_plain[x[2]]+')').join(". ")+'.</p>'; }
  const d=r.column;
  if(d && (d.ph_vs_safe>1+1e-9 || !d.passes_tested))
    h+='<p><b>Warning.</b> This tank design pumps the culture through the column harder than the checks allow. It uses '+d.passes.toFixed(0)+
       ' passes an hour, and dense cultures have taken up to 15–24. The alkaline culture in the loop is '+d.ph_vs_safe.toFixed(1)+' times the exposure judged safe. '+
       'Treat the cost as too low, or use the button below to pick the cheapest design that passes.</p>';
  if(SCS.src==="custom") h+='<p><b>Note.</b> The page is using the case from “All the levers” ($'+SCS.customCost.toFixed(1)+' a kilo), not these switches. Move a switch, or pick a case at the top, to come back to them.</p>';
  return h;
}
function scGridHTML(ch,a,b){
  const sa=scSwitch(a), sb=scSwitch(b);
  const cost=sa.settings.map(i=>sb.settings.map(j=>scEval(Object.assign({},ch,{[a]:i.key,[b]:j.key})).total));
  const all=[].concat.apply([],cost), mn=Math.min.apply(null,all), mx=Math.max.apply(null,all);
  const col=v=>{ const t=(v-mn)/Math.max(1e-9,mx-mn); return "rgb("+Math.round(232-52*t)+","+Math.round(240-36*t)+","+Math.round(252-16*t)+")"; };   // one hue, pale (cheap) to deeper (dear)
  let h='<table class="scgrid"><thead><tr><th>'+sa.name+' ↓ &nbsp; '+sb.name+' →</th>'+sb.settings.map(j=>'<th>'+j.short+'</th>').join("")+'</tr></thead><tbody>';
  sa.settings.forEach((i,ii)=>{ h+='<tr><th>'+i.short+'</th>'+sb.settings.map((j,jj)=>{
    const cur=(ch[a]===i.key&&ch[b]===j.key);
    return '<td style="background:'+col(cost[ii][jj])+(cur?';outline:2px solid #0b0b0b;outline-offset:-2px;font-weight:700':'')+'" onclick="scPickTwo(\''+a+'\',\''+i.key+'\',\''+b+'\',\''+j.key+'\')" title="Set both'+(cur?' (the setting now)':'')+'">'+scMoney(cost[ii][jj])+'</td>'; }).join("")+'</tr>'; });
  return h+'</tbody></table>';
}
function scGridSet(){ scPair=[document.getElementById("sc_ga").value,document.getElementById("sc_gb").value]; l4Render(); }
// Where the cost goes: the six parts of a kilo's cost for the chosen switches, on a dollar axis, so the whole bar shrinks or
// grows as the switches move. The first four parts scale with the litres of medium. Colours follow the part, never its rank.
const SC_PARTS=[
  {key:"medium", name:"Medium (the nutrients)", col:"#029E73", litres:true, get:r=>r.feedstock},
  {key:"gf", name:"Growth factors", col:"#DE8F05", litres:true, get:r=>r.growth_factors},
  {key:"protect", name:"Bubble protectant", col:"#CC78BC", litres:true, get:r=>r.protectant},
  {key:"membranes", name:"Filter membranes", col:"#D55E00", litres:true, get:r=>r.membranes},
  {key:"running", name:"Running the plant (staff, power, other supplies)", col:"#56B4E9", litres:false,
   get:r=>r.labour+r.utilities+(r.consumables-r.membranes-r.protectant)+r.extra_opex},
  {key:"plant", name:"The plant (yearly charge on its capital)", col:"#0173B2", litres:false, get:r=>r.capital}];
function scPartsSVG(r, ref, refName, gfInMedium){
  const W=720, x0=16, x1=W-16, by=64, bh=22, rowH=21, ly=by+bh+62;
  const parts=SC_PARTS.map(p=>({p, name:(p.key==="gf"&&gfInMedium?"Growth factors (inside the medium's price)":p.key==="medium"&&gfInMedium?"Medium (the nutrients, with growth factors in the price)":p.name),
    v:Math.max(0,p.get(r)), vr:ref?Math.max(0,p.get(ref)):null}));
  const total=parts.reduce((s,q)=>s+q.v,0), litres=parts.filter(q=>q.p.litres).reduce((s,q)=>s+q.v,0);
  const par=parityCost(state);
  const top=Math.max(total, ref?ref.total:0, par)*1.08, step=top>120?50:top>60?20:top>25?10:5, xmax=Math.ceil(top/step)*step;
  const X=v=>x0+(x1-x0)*v/xmax, f2=v=>"$"+v.toFixed(2), f1=v=>"$"+v.toFixed(1);
  const H=ly+parts.length*rowH+8;
  let g='<svg class="w720" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Where the cost of a kilo of cells goes: '+parts.map(q=>q.name+" "+f2(q.v)).join(", ")+'">';
  g+='<text x="'+x0+'" y="14" font-size="11" class="b">'+f1(total)+' a kilo of cells, every estimate at its most likely value</text>';
  g+='<text x="'+x0+'" y="29" font-size="9.5">'+(total>0?Math.round(litres/total*100):0)+'% of it scales with the litres of medium ('+r.medium_l.toFixed(0)+' L a kilo): the first four parts. Hover over a part for its value.</text>';
  const marksAt=[par].concat(ref&&Math.abs(ref.total-total)>0.005?[ref.total]:[]);
  for(let t=0;t<=xmax+1e-9;t+=step){ g+='<line x1="'+X(t)+'" x2="'+X(t)+'" y1="'+(by-6)+'" y2="'+(by+bh+6)+'" stroke="#eee"/>';
    if(!marksAt.some(m=>Math.abs(X(m)-X(t))<18)) g+='<text x="'+X(t)+'" y="'+(by+bh+18)+'" font-size="9.5" text-anchor="middle">$'+t+'</text>'; }
  let acc=0;
  parts.forEach(q=>{ if(q.v<=0) return; const a=X(acc), b=X(acc+q.v); acc+=q.v;
    g+='<rect x="'+a.toFixed(1)+'" y="'+by+'" width="'+Math.max(0.5,b-a-2).toFixed(1)+'" height="'+bh+'" rx="3" fill="'+q.p.col+'"><title>'+
       q.name+': '+f2(q.v)+' a kilo ('+(q.v/total*100).toFixed(0)+'%)</title></rect>';
    const pct=Math.round(q.v/total*100)+'%', both=f1(q.v)+' · '+pct;      // dollars and share where the part has room
    const lab=b-a>8+both.length*6.2?both:(b-a>8+pct.length*6.2?pct:'');
    if(lab) g+='<text class="on" x="'+(a+5).toFixed(1)+'" y="'+(by+15)+'" font-size="9.5" font-weight="700" pointer-events="none">'+lab+'</text>'; });
  if(litres>0){ const a=X(0), b=X(litres)-2; g+='<path d="M'+a+' '+(by-4)+' V'+(by-9)+' H'+b+' V'+(by-4)+'" fill="none" stroke="#999"/>'+
     '<text x="'+((a+b)/2).toFixed(1)+'" y="'+(by-12)+'" font-size="9.5" text-anchor="middle">scales with litres: '+f1(litres)+'</text>'; }
  const mark=(v,lab,dash)=>'<line x1="'+X(v)+'" x2="'+X(v)+'" y1="'+(by+bh+2)+'" y2="'+(by+bh+24)+'" stroke="#333" stroke-dasharray="'+dash+'"/>'+
     '<text x="'+(X(v)+3)+'" y="'+(by+bh+32)+'" font-size="9.5">'+lab+'</text>';
  g+=mark(par,"same shop price as meat: "+f1(par),"2 2");
  if(ref&&Math.abs(ref.total-total)>0.005&&Math.abs(X(ref.total)-X(par))>150) g+=mark(ref.total,refName+": "+f1(ref.total),"5 3");
  const showRef=ref&&Math.abs(ref.total-total)>0.005;
  g+='<text x="'+(x0+530)+'" y="'+(ly-17)+'" font-size="9.5" text-anchor="end">$ a kilo</text>'+
     '<text x="'+(x0+590)+'" y="'+(ly-17)+'" font-size="9.5" text-anchor="end">share</text>'+
     (showRef?'<text x="'+x1+'" y="'+(ly-17)+'" font-size="9.5" text-anchor="end">against '+refName+'</text>':'');
  parts.forEach((q,i)=>{ const y=ly+i*rowH, d=showRef?q.v-q.vr:0;
    g+='<rect x="'+x0+'" y="'+(y-9)+'" width="10" height="10" rx="2" fill="'+q.p.col+'"/>'+
       '<text x="'+(x0+16)+'" y="'+y+'" font-size="9.5" class="b" style="font-weight:400">'+q.name+'</text>'+
       '<text x="'+(x0+530)+'" y="'+y+'" font-size="9.5" text-anchor="end" class="b" style="font-weight:400">'+f2(q.v)+'</text>'+
       '<text x="'+(x0+590)+'" y="'+y+'" font-size="9.5" text-anchor="end">'+(total>0?(q.v/total*100).toFixed(0):0)+'%</text>'+
       (showRef?'<text x="'+x1+'" y="'+y+'" font-size="9.5" text-anchor="end">'+(Math.abs(d)<0.005?"same":(d>0?"+":"−")+f2(Math.abs(d)))+'</text>':''); });
  return g+'</svg>';
}
function l4Render(){
  const host=document.getElementById("sc_result"); if(!host||!KP) return;
  const ch=SCS.choice, r=scEval(ch), p=scParams(ch);
  SC.keys.forEach(k=>{ const e=document.getElementById("sc_sel_"+k); if(e) e.value=ch[k];
    const n=document.getElementById("sc_note_"+k); if(n) n.innerHTML=scTagChip(scSetting(k,ch[k]).tag)+' '+scSetting(k,ch[k]).note; });
  host.innerHTML=scResultHTML(ch,r);
  const gfIn=(p.gf_in_medium||0)>0&&r.growth_factors<0.005;
  const ph=document.getElementById("sc_parts");      // where the cost goes, against Central (or the best case when Central is chosen)
  if(ph){ const refKey=SCS.preset==="central"?"best":"central"; ph.innerHTML=scPartsSVG(r,scEval(SC.presets[refKey].choice),pgCaseLabel(refKey),gfIn); }
  const pn=document.getElementById("sc_parts_note");
  if(pn) pn.innerHTML=gfIn?"The medium's price is taken to include the growth factors, so they show as $0.00 here. The growth-factor switch then acts as a floor: the medium cannot cost less than its nutrients plus the growth factors bought. "+
      "With all of them bought at Humbird's price this case would cost "+scMoney(scEval(Object.assign({},ch,{gf:"all"})).total)+" a kilo."
    :"The filter membranes are paid for by the litre of medium filtered. No device yet holds cells back in a tank this size, so that line is an estimate from pharma runs.";
  const pri=scPriorities(ch,false);
  if(!scPair) scPair=[pri[0].switch,pri[1].switch];
  const ga=document.getElementById("sc_ga"), gb=document.getElementById("sc_gb");
  if(ga&&gb){ ga.value=scPair[0]; gb.value=scPair[1]; if(scPair[0]===scPair[1]) gb.value=(SC.keys.find(k=>k!==scPair[0])); }
  const gh=document.getElementById("sc_grid"); if(gh) gh.innerHTML=scGridHTML(ch,ga?ga.value:scPair[0],gb?gb.value:scPair[1]);
  if(typeof vmRender==="function") vmRender();     // the vessel-by-mode table follows the switches (page_vessels.js)
  const its=scInteractions(ch), nh=document.getElementById("sc_notes");
  if(nh) nh.innerHTML=its.length?'<ul>'+its.map(x=>'<li>'+x.text+'</li>').join("")+'</ul>':
    '<p class="small">No two switches interact strongly around these settings. Each saves about the same whatever the other is.</p>';
  drawCost(state); if(typeof fxRender==="function"&&fxDefaults) fxRender();
}
function l5Render(){
  const s=state, b=biomass(s), retail=shelfPrice(b,s), conv=C.p_conv_anchor*s.meat_tax;
  drawCalc(s,b,retail,conv,retail/conv); drawCurve(s); drawBreakdown(s); drawMC(s); drawMilk(s); drawFoothold(s);
}
function l6Render(){ /* the method text is static; the tables are filled once at load */ }

/* ---------- which levels are open, and drawing only those ---------- */
const PG_LEVELS=[["assumes",l1Render],["moves",l2Render],["where",l3Render],["engineering",l4Render],["shoppers",l5Render],["method",l6Render]];
function pgRenderLevels(){
  if(typeof document==="undefined") return;
  PG_LEVELS.forEach(([id,fn])=>{ const d=document.getElementById(id); if(d&&d.open){ fn(); PGS.dirty[id]=false; } else PGS.dirty[id]=true; });
}
function pgOpenFor(el){          // open every level and sub-section that holds an element, so a link to it lands on something visible
  let n=el, opened=false;
  while(n&&n.tagName){ if(n.tagName==="DETAILS"&&!n.open){ n.open=true; opened=true; } n=n.parentNode; }
  return opened;
}
function pgGoto(id,scroll){
  const t=id?document.getElementById(id):null; if(!t) return;
  pgOpenFor(t); PGS.anchor=id;
  if(scroll!==false&&t.scrollIntoView) setTimeout(()=>t.scrollIntoView({block:"start"}),30);
}
function pgInit(){
  if(typeof document==="undefined"||!document.querySelectorAll) return;
  pgBuildBar();
  PG_LEVELS.forEach(([id,fn])=>{ const d=document.getElementById(id); if(!d||!d.addEventListener) return;
    d.addEventListener("toggle",()=>{ if(d.open){ fn(); PGS.dirty[id]=false; } }); });
  document.querySelectorAll('a[href^="#"]').forEach(a=>{ if(a.addEventListener) a.addEventListener("click",e=>{
    const id=(a.getAttribute("href")||"").slice(1); if(!id||!document.getElementById(id)) return;
    e.preventDefault(); pgGoto(id); if(typeof pgWriteHash==="function") pgWriteHash(); }); });
  if(typeof window!=="undefined"&&window.addEventListener){
    let rz=null; window.addEventListener("resize",()=>{ clearTimeout(rz); rz=setTimeout(()=>{ l0Cache.key=l0Cache.key; pgRenderFirst(); pgRenderLevels(); },120); });
    window.addEventListener("hashchange",()=>{ const h=location.hash.slice(1); if(h&&h.indexOf("=")<0) pgGoto(h); });
  }
}

/* ---------- the all-levers panel starts from a case ---------- */
const FX_GLC_DEFAULT=C.fx.glc_kg;
// what a case carries that the panel has no lever for: the ammonia its cells tolerate, glucose from the cells' own balance,
// and growth factors inside the medium's price. fxRender adds these to the levers while the panel still holds that case.
let fxCarry=null;
function fxFromScenario(key){
  fxCarry=null;
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
    if(p.do_mmol!==undefined) set("fx_do",p.do_mmol);
    fxCarry={nh3_limit:p.nh3_limit, gf_in_medium:p.gf_in_medium||0, glc_balance:!!p.glc_balance, gk:document.getElementById("fx_gk").value};
  }
  fxRender();
}
