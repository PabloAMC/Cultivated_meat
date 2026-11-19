/* ===== scenarios: the switches, the presets and what to prioritise =====
   A line-for-line mirror of scenarios.py (run, design, priorities, interactions); tests/run_parity.py checks the two agree.
   Included into the page's script by build_interactive.py. Everything is computed by floorExplore (the mirror of
   floor_physics.explore) from the settings of the switches in MODEL.sc; nothing here is typed in by hand. */
const SC=MODEL.sc;
const INIT_HASH=(typeof location!=="undefined")?location.hash.slice(1):"";   // a link to a level (#moves): the settings hash replaces it, so remember it
// The page's one state. choice: the ten switches; base: "switches" (a choice) or "humbird" (Humbird's design, explore()'s defaults);
// ref: the reference point loaded and not changed since (null once anything moves); from: the last one loaded; traits: the cell
// traits the reader has set (held, not drawn); held: the plant estimates the reader has set (capex_x, cpl = filter cost per
// litre, medium_price); hb: Humbird's tank mode and plant; buyers: meat buyers who would pick it at the same price (the map's y).
const SCS={choice:Object.assign({},SC.presets[SC.start].choice), preset:SC.start, src:"scenario", customCost:null,
  base:"switches", ref:SC.start, from:SC.start, redesign:true, traits:{}, held:{}, hb:{mode:"perfusion",plant:"sterile"}, buyers:null};
// what every scEval adds to a choice's explore arguments: the reader's traits and plant estimates (empty unless the reader set
// them, so the pure mirror of scenarios.run that tests/run_parity.py checks is unchanged)
let SC_EXTRA={};
function scWithExtra(x,fn){ const sv=SC_EXTRA; SC_EXTRA=x; try{ return fn(); } finally{ SC_EXTRA=sv; } }
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
  // a fed-batch plant restarts each tank every few days, so the shared-medium plant keeps Humbird's full seed train (scenarios.explore_kwargs)
  if(p.vm&&p.vm.kind==="cyclic"&&p.items&&p.items.seed==="two") p.items=Object.assign({},p.items,{seed:"full"});
  return Object.assign(p,SC_EXTRA);
}
function scEval(ch){
  const k=SC.keys.map(x=>ch[x]).join("|")+JSON.stringify(SC_EXTRA);
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
   THE PAGE. The reader sets the cells (four traits), the plant and how many meat buyers would pick it at the same price;
   the page draws the cost of a kilo of cells as a cloud of draws over the estimates nobody has measured, places it on a
   contour map of the long-run share, and says which routes have shown each trait. Reference points load trait values; they
   are not forecasts. Nothing below changes the model's arithmetic: it calls the engine (floorExplore, penetration, shareCalc)
   and draws what comes back. tests/run_parity.py checks the cloud and the routes verdict against scenarios.py and
   cell_traits.py.
   ===================================================================================================================== */
const PG=MODEL.page, TP=MODEL.tp;
const PGS={l2sel:null, dirty:{}, cloud:null, grid:null, gridKey:null, gridBusy:false, readDismissed:false};
const TRAIT_KEYS=["nh3_kg","lac_yield","doubling_h","mass_pg"];
const scMoney=(v,d)=>"$"+v.toFixed(d===undefined?1:d);
const pgUSD=v=>"$"+Math.round(v).toLocaleString("en-US");
const pgEsc=t=>String(t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
// a share in percent as text: one decimal from 0.1 up, two below it, three below 0.01, "under 0.001" below that (mirror of scenarios.pct_num)
function pgPct(v){ return v<0.00095?"under 0.001":(v<0.0095?v.toFixed(3):(v<0.095?v.toFixed(2):v.toFixed(1))); }
const scPct=pgPct;
const pgPctS=v=>pgPct(v)+"%";
function pgRange(a,b,f){ return f(a)===f(b)?f(a):"between "+f(a)+" and "+f(b); }
// a cost in dollars rounded to the precision its range allows: whole dollars from $10 up, one decimal below
const tpUSD=v=>v>=9.95?pgUSD(v):"$"+v.toFixed(1);
function pgRegionName(r){ const x=PG.regions.find(q=>q[0]===(r||state.region)); return x?x[1]:r; }
function pgRegionOf(){ const n=pgRegionName(); return state.region==="global"?"the world's":(state.region==="us"?"the United States'":n+(/s$/.test(n)?"'":"'s")); }
function tpRef(k){ return TP.refs.find(r=>r.key===k)||null; }
function tpLabel(k){ const r=tpRef(k); return r?r.label:"Your settings"; }
const pgCaseLabel=tpLabel;
function pgAbout(v){ return String(Math.round(v*10)/10); }

/* ---------- the routes verdict (mirror of cell_traits.routes_needed) ---------- */
// Python's f"{v:g}" for the values a slider can take
function tpG(v){ return String(Number((+v).toPrecision(6))); }
function tpTraitRoute(t,v){
  const d=TP.routes.traits[t].dir;
  for(const [r,level] of TP.routes.routes[t]){ if(d<0?v>=level-1e-12:v<=level+1e-12) return r; }
  return null;
}
function tpCombination(tr){
  const out=[], nh3=tr.nh3_kg, td=tr.doubling_h, feed=TP.routes.routes.nh3_kg.find(x=>x[0]==="feed")[1];
  if(nh3!==undefined&&td!==undefined&&nh3<=feed+1e-12&&td<TP.routes.td_low_ammonia-1e-9)
    out.push("Low ammonia ("+tpG(nh3)+" mol/kg or less) and a doubling under 42.9 hours have not been shown together in a meat cell: "+
             "the low-ammonia feed slowed the cells that showed it (Hubalek 2023).");
  return out;
}
function tpRoutesNeeded(tr){
  const per={}, T=TP.routes.traits;
  TRAIT_KEYS.forEach(t=>{ if(tr[t]===undefined) return; const r=tpTraitRoute(t,+tr[t]);
    per[t]={value:+tr[t], route:r, text:TP.routes.route_text[String(r===null?"None":r)], name:T[t].name, unit:T[t].unit}; });
  const ks=Object.keys(per), none=ks.filter(t=>per[t].route===null), eng=ks.filter(t=>per[t].route==="engineering"),
        other=ks.filter(t=>per[t].route==="select_other");
  const lst=ts=>ts.map(t=>per[t].name+" at "+tpG(per[t].value)+" "+per[t].unit).join("; ");
  let verdict, short;
  if(none.length){ verdict="Not yet shown by any route: "+lst(none)+"."; short="not shown by any route"; }
  else if(eng.length){ verdict="These traits have so far been shown only with genetic engineering: "+lst(eng)+"."; short="some traits shown only with genetic engineering"; }
  else if(other.length){ verdict="No genetic engineering needed: each trait has been shown without it, but "+lst(other)+" only in other cells (CHO), not in meat cells.";
    short="shown without engineering, some only in other cells"; }
  else { verdict="No genetic engineering needed: each trait has been shown without it, in meat cells."; short="shown in meat cells"; }
  const together=tpCombination(tr);
  if(together.length){ verdict+=" Not shown together: "+together.join(" "); short+="; not yet together in one meat cell"; }
  return {traits:per, verdict:verdict, short:short, together:together, rank:none.length?3:(eng.length?2:(other.length?1:0))};
}
// the same verdict in the page's own words (plain names, a cell's weight in ng)
function tpTraitText(t,v){ const T=TP.traits[t]; return T.name.replace(/ \(.*\)$/,"").toLowerCase()+" at "+tpG(v*T.scale)+" "+T.unit; }
function tpVerdictPlain(rn){
  const ks=Object.keys(rn.traits), pick=r=>ks.filter(t=>rn.traits[t].route===r).map(t=>tpTraitText(t,rn.traits[t].value));
  let s;
  if(rn.rank===3) s="Not yet shown by any route: "+pick(null).join("; ")+".";
  else if(rn.rank===2) s="So far shown only with genetic engineering: "+pick("engineering").join("; ")+". Each other trait has been shown without it.";
  else if(rn.rank===1) s="No genetic engineering needed: each trait has been shown without it, but "+pick("select_other").join("; ")+" only in other cells (CHO: hamster cells that make drugs), not yet in meat cells.";
  else s="No genetic engineering needed: each trait has been shown without it, in meat cells.";
  if(rn.together.length) s+=" Not yet shown together in one meat cell: low ammonia and a doubling under 42.9 hours (the low-ammonia feed slowed the cells that showed it, Hubalek 2023).";
  return s;
}
function tpVerdictShort(rn){
  return ["No genetic engineering has been needed for traits like these.",
          "No genetic engineering has been needed for traits like these, though some were shown only in other cells.",
          "Some of these traits have so far been shown only with genetic engineering.",
          "Some of these traits have not been shown by any route."][rn.rank]+(rn.together.length?" They have not been shown together in one meat cell.":"");
}

/* ---------- the reader's explore arguments ---------- */
function tpResolvePlant(p){ if(p.plantKey){ if(p.plantKey==="lean"){ p.plant="sanitary"; p.items=C.fx.plant_items.lean; }
  else p.plant=(p.plantKey==="sterile"?"sanitary":p.plantKey); delete p.plantKey; } return p; }
function tpHeldKw(h){ const o={}; h=h||{};
  if(h.capex_x!==undefined) o.capex_x=h.capex_x;
  if(h.cpl!==undefined) o.membrane_life=TP.plant.mem_price/h.cpl;     // a held cost per litre: membrane life at the model's membrane price
  if(h.medium_price!==undefined) o.medium_price=h.medium_price;
  return o; }
// explore arguments for a state {base, choice, hb, traits, held}; without traits or held: the reference point itself
function tpParamsFor(st){
  const extra=Object.assign({},st.traits||{},tpHeldKw(st.held));
  if(st.base==="humbird"){
    const p=Object.assign({},tpRef("humbird").base);
    if(st.hb.mode!=="perfusion") Object.assign(p,JSON.parse(JSON.stringify(scSetting("mode",st.hb.mode).p)));
    if(st.hb.plant!=="sterile") Object.assign(p,scSetting("plant",st.hb.plant).p);
    tpResolvePlant(p);
    if(p.vm&&p.vm.kind==="cyclic"&&p.items&&p.items.seed==="two") p.items=Object.assign({},p.items,{seed:"full"});
    return Object.assign(p,extra);
  }
  return scWithExtra(extra,()=>scParams(st.choice));
}
function tpParams(){ return tpParamsFor(SCS); }
function tpMode(){ return SCS.base==="humbird"?SCS.hb.mode:SCS.choice.mode; }
function tpPlant(){ return SCS.base==="humbird"?SCS.hb.plant:SCS.choice.plant; }
// the four traits as the page shows them: the reader's where set, else the reference point's (or the switches')
function tpTraitsShown(){
  const base=SCS.base==="humbird"?tpRef("humbird").traits:(()=>{ const p=scWithExtra({},()=>scParams(SCS.choice)); const o={}; TRAIT_KEYS.forEach(k=>o[k]=p[k]); return o; })();
  return Object.assign({},base,SCS.traits);
}

/* ---------- the cloud: draws over the estimates nobody has measured (mirror of scenarios.scenario_mc) ---------- */
// One draw: the same estimates scenario_mc draws, for a scenario (isScen) or Humbird's design. Keys starting with "_" are inputs of
// the datasheet (protectant dose, membrane price, amino-acid price) that explore() reads from the registry.
function tpCloudDraw(isScen,kw0,cells,lean){
  const P=TP.cloud.priors, M=TP.cloud.mc, pd=n=>{ const q=P[n]; return q[3]==="lognormal"?lognorm(q[0],q[1],q[2],q[4],q[5]):triang(q[0],q[1],q[2]); };
  const o={};
  o.capex_x=triang(lean?TP.cloud.lean_capex_lo:M.capex_x[0],M.capex_x[1],M.capex_x[2]);
  o.medium_price=triang(M.medium_price[0],M.medium_price[1],M.medium_price[2])*(kw0.medium_price===undefined?0.15:kw0.medium_price);
  o.hazard=triang(M.hazard[0],M.hazard[1],M.hazard[2])*(kw0.hazard||0);
  o.charge=pd("plant_charge_mature"); o.membrane_life=pd("rt_membrane_life"); o.maint=pd("pf_maintenance_share");
  if(TP.cloud.wide&&isScen&&(cells==="selected"||cells==="measured")) o.nh3_kg=pd("sc_nh3_selected");
  if(TP.cloud.wide){
    TP.cloud.estimates.forEach(([k,n])=>{ if(isScen&&TP.cloud.scenario_priors[k]) o[k]=pd(TP.cloud.scenario_priors[k]); else if(!(k in kw0)) o[k]=pd(n); });
    o._dose=pd("pf_protectant_dose"); o._memprice=pd("rt_membrane_price"); o._aa=pd("aa_bulk_price");
    if(isScen) o.mass_pg=pd("sc_mass_selected_pg");
  }
  return o;
}
// the cost of one draw: the reader's arguments with the drawn estimates in place
function tpCloudCost(p,o){
  const q=Object.assign({},p), F=C.fx, sv=[F.protect_dose,F.tff.mem_price,F.aa];
  for(const k in o) if(k.charAt(0)!=="_") q[k]=o[k];
  if(o._dose!==undefined) F.protect_dose=o._dose;
  if(o._memprice!==undefined) F.tff.mem_price=o._memprice;
  if(o._aa!==undefined) F.aa=TP.cloud.aa_intensity*o._aa;
  try{ return floorExplore(q).total; } finally{ F.protect_dose=sv[0]; F.tff.mem_price=sv[1]; F.aa=sv[2]; }
}
// which draws a state's own settings remove from the cloud: the traits and plant estimates the reader has set
function tpDrop(o,st){
  Object.keys(st.traits||{}).forEach(k=>{ delete o[k]; });
  const h=st.held||{};
  if(h.capex_x!==undefined) delete o.capex_x;
  if(h.cpl!==undefined){ delete o.membrane_life; delete o._memprice; }
  if(h.medium_price!==undefined) delete o.medium_price;
  return o;
}
// n draws for a state (the same seed for every state, so the cloud moves smoothly as a setting moves): the costs, sorted, and
// the 10th, 50th and 90th percentiles; `draws` lets a test pass in Python's draws
function tpCloudFor(st,n,draws){
  n=n||TP.cloud.n;
  const p=tpParamsFor(st), isScen=st.base!=="humbird";
  const kw0=isScen?scWithExtra({},()=>scParams(st.choice)):Object.assign({},tpRef("humbird").base);
  const cells=isScen?st.choice.cells:null, lean=isScen&&st.choice.plant==="lean";
  if(!draws){ _seedRng(TP.cloud.seed); draws=[]; for(let i=0;i<n;i++) draws.push(tpDrop(tpCloudDraw(isScen,kw0,cells,lean),st)); }
  else draws=draws.map(o=>tpDrop(Object.assign({},o),st));
  const cost=draws.map(o=>tpCloudCost(p,o)), srt=cost.slice().sort((a,b)=>a-b), r0=floorExplore(p);
  return {cost:cost, sorted:srt, q:[pctl(srt,10),pctl(srt,50),pctl(srt,90)], point:r0.total, res:r0, n:draws.length};
}
const TP_REFC={};
function tpRefCloud(k){            // a reference point's own cloud (its traits drawn as scenario_mc draws them)
  if(!TP_REFC[k]){ const r=tpRef(k);
    if(r.kind==="company") TP_REFC[k]={q:[r.cost,r.cost,r.cost], point:r.cost, sorted:[r.cost]};
    else TP_REFC[k]=tpCloudFor(r.kind==="humbird"?{base:"humbird",hb:{mode:"perfusion",plant:"sterile"},traits:{},held:{}}
                                              :{base:"switches",choice:r.choice,traits:{},held:{}}); }
  return TP_REFC[k];
}

/* ---------- shoppers: the map's y is the share of meat buyers who pick it at the same price ---------- */
// the mean liking that makes `b` of meat buyers pick it at equal price, at neutral settings (mirror of
// scenarios.all_choices_for_meat_buyers followed by the calibration's _solve_liking)
const TP_LM=new WeakMap();
function tpLmean(b){
  if(!TP_LM.has(KP)) TP_LM.set(KP,{});
  const M=TP_LM.get(KP), key=b.toFixed(6);
  if(M[key]!==undefined) return M[key];
  const g=C.liking_grid; let lo=g[0], hi=g[g.length-1];
  for(let i=0;i<80;i++){ const mid=0.5*(lo+hi); if(shareCalc(1,KP,{ax:1,tfM:0,nbx:0,hx:0,lmean:mid,which:"x_meat"})<b) lo=mid; else hi=mid; }
  return M[key]=0.5*(lo+hi);
}
// the share-of-all-choices dial for `b` of meat buyers (what the shopper model's own setting is)
function tpDial(b){ return shareCalc(1,KP,{ax:1,tfM:0,nbx:0,hx:0,lmean:tpLmean(b)}); }
function tpBuyersOfDial(e){ return shareCalc(1,KP,{ax:1,tfM:0,nbx:0,hx:0,eqs:e,which:"x_meat"}); }
// long-run share (%) of a region's meat and seafood at `cost` a kilo of cells and `b` of meat buyers, the other shopper settings as set
function tpShare(cost,b,region){
  region=region||state.region;
  const s=Object.assign({},state,{region:region,income:region===state.region?state.income:C.REGION_INCOME[region],cost_override:cost,lmean:tpLmean(b)});
  return penetration(s).tv*100;
}
// the cost of cells at which the share is `target` % (null if not reached even at $0.5): mirror of scenarios.cost_for_share
const TP_CF=new WeakMap();
function tpCostFor(target,b,region){
  if(!TP_CF.has(KP)) TP_CF.set(KP,{});
  const M=TP_CF.get(KP), key=target+"|"+b.toFixed(6)+"|"+(region||state.region)+"|"+state.income+"|"+state.markup_add+"|"+state.retail_margin+"|"+state.cut_cells;
  if(key in M) return M[key];
  return M[key]=tpCostForRaw(target,b,region);
}
function tpCostForRaw(target,b,region){
  let lo=0.5, hi=400;
  if(tpShare(lo,b,region)<target) return null;
  for(let i=0;i<50;i++){ const mid=Math.sqrt(lo*hi); if(tpShare(mid,b,region)>=target) lo=mid; else hi=mid; }
  return lo;
}
// the region's volume-weighted price of a kilo of meat and seafood, and the cost of cells at which the shop price matches it
function tpAvgPrice(region){ let W=0,V=0; MODEL.markets[region||state.region].forEach(m=>{ W+=m.w_vol; V+=m.w_vol*m.p_conv; }); return V/W; }
function tpParity(region){ return tpAvgPrice(region)*(1-state.retail_margin)-state.markup_add; }
function pgPlantBased(){ return penetration(Object.assign({},state,{cost_override:1e6})).tvp*100; }   // with no cultivated meat on sale

/* ---------- the facts of the first screen ---------- */
function tpChanged(){ return SCS.ref===null; }
function tpWho(){ return SCS.ref?tpLabel(SCS.ref):"Your settings"; }
function pgFacts(){
  const cl=PGS.cloud||(PGS.cloud=tpCloudFor(SCS)), b=SCS.buyers, q=cl.q, cost=q[1];
  const retail=shelfPrice(cost,state), conv=C.p_conv_anchor*state.meat_tax, rn=tpRoutesNeeded(tpTraitsShown());
  const sh=[tpShare(q[2],b),tpShare(q[1],b),tpShare(q[0],b)];
  const one=tpCostFor(1,b), ten=tpCostFor(10,b);
  return {key:SCS.ref||"own", label:tpWho(), region:state.region, cost:cost, cb:q, point:cl.point, retail:retail, conv:conv, mult:retail/conv,
          avg:tpAvgPrice(), share:sh[1], sb:sh, pb:pgPlantBased(), parity:tpParity(), buyers:b, eqs:state.equal_price_share, rn:rn, cloud:cl,
          one:one, ten:ten, groups:tpCostGroups(cl.res||floorExplore(tpParams())), animals:tpByAnimal(cost,b)};
}
function pgPointCost(){ return (PGS.cloud||(PGS.cloud=tpCloudFor(SCS))).point; }
function pgHeadCost(){ return (PGS.cloud||(PGS.cloud=tpCloudFor(SCS))).q[1]; }
function pgSetCost(){ state.cost_override=pgHeadCost(); }      // the cost every shopper chart runs at: the median of the cloud
function pgCaseWords(f){ return f.key==="own"?"your settings":f.label; }
function scOwnName(){ return tpWho(); }

function tpRangeUSD(a,b){ const f=tpUSD; return f(a)===f(b)?f(a):f(a)+"–"+f(b).replace("$",""); }
function tpPctB(b){ const v=b*100; return (Math.abs(v-Math.round(v))<0.05?Math.round(v).toFixed(0):v.toFixed(1))+"%"; }

/* ---------- the first screen's words: ratios and fractions said plainly ---------- */
const TP_NUM=["zero","one","two","three","four","five","six","seven","eight","nine","ten","eleven","twelve"];
// a ratio above 1 in words: "nearly twice", "about eight times", "over five times", "1.4 times", "51 times"
function tpTimes(r){
  const n=Math.round(r), dev=(r-n)/Math.max(1,n);
  if(r<1.75||Math.abs(dev)>0.12) return (r<10?r.toFixed(1):String(Math.round(r)))+" times";
  const w=n===2?"twice":(n<=12?TP_NUM[n]+" times":n+" times");
  return (Math.abs(dev)<=0.04?"about ":(dev<0?"nearly ":"over "))+w;
}
// a fraction in words: "two-thirds", "nearly nine-tenths", "over a quarter"
const TP_FRAC=[[0.1,"a tenth"],[0.2,"a fifth"],[0.25,"a quarter"],[1/3,"a third"],[0.4,"two-fifths"],[0.5,"half"],[0.6,"three-fifths"],
               [2/3,"two-thirds"],[0.75,"three-quarters"],[0.8,"four-fifths"],[0.9,"nine-tenths"]];
function tpFrac(x){
  if(x>=0.95) return "nearly all"; if(x<0.07) return "under a tenth";
  const b=TP_FRAC.reduce((a,c)=>Math.abs(c[0]-x)<Math.abs(a[0]-x)?c:a), d=x-b[0];
  return (Math.abs(d)<0.02?"":(d<0?"nearly ":"over "))+b[1];
}
const tpCap=t=>t.charAt(0).toUpperCase()+t.slice(1);
// a yardstick's cost (what a share needs): one decimal below $100, so $19.7 is not rounded to $20
const tpUSDk=v=>v>=99.5?pgUSD(v):"$"+v.toFixed(1);
function tpRegionThe(){ return state.region==="us"?"the United States":pgRegionName(); }
// "the world's meat and seafood" / "meat in Europe" in a label
function tpRegionMeat(short){ return state.region==="global"?(short?"world meat":"the world's meat and seafood"):(short?"meat in "+tpRegionThe():pgRegionOf()+" meat and seafood"); }
function tpEatenWhere(){ return state.region==="global"?"in the world":"in "+tpRegionThe(); }

/* ---------- where the money goes, grouped by what drives it (the engine's own cost result, floorExplore) ---------- */
// (a) what scales with the litres of medium, (b) what scales with the time the cells spend in the tank (the plant's yearly charge
// and the staff, both divided by what a tank makes in a year), (c) everything else. tests/run_parity.py checks the items against
// floor_physics.explore's components for each reference point, and that they add up to its total.
function tpCostGroups(r){
  const ml=r.medium_l, perL=v=>ml>0?" ($"+(v/ml).toFixed(2)+" a litre)":"";
  const groups=[
    {key:"litres", name:"Scales with the litres of medium", what:"the litres of medium the cells need", note:ml.toFixed(0)+" litres a kilo of cells", items:[
      {key:"membranes", name:"Filter membranes", note:perL(r.membranes), v:r.membranes},
      {key:"medium", name:"The medium itself", note:perL(r.feedstock), v:r.feedstock},
      {key:"protectant", name:"Bubble protectant", note:perL(r.protectant), v:r.protectant},
      {key:"gf", name:"Growth factors bought on top", note:perL(r.growth_factors), v:r.growth_factors}]},
    {key:"time", name:"Scales with time in the tank", what:"the time the cells spend in the tank", note:"the plant and its staff, paid by the year and shared over what a tank makes", items:[
      {key:"capital", name:"The plant's yearly capital charge", note:"", v:r.capital},
      {key:"labour", name:"Labour", note:"", v:r.labour}]},
    {key:"other", name:"Everything else", what:"neither", note:"", items:[
      {key:"energy", name:"Energy and gas", note:"", v:r.utilities+(r.extra_opex||0)},
      {key:"supplies", name:"Other supplies", note:"", v:r.consumables-r.membranes-r.protectant}]}];
  groups.forEach(g=>{ g.items=g.items.filter(i=>(i.key!=="gf"&&i.key!=="membranes"&&i.key!=="protectant")||i.v>0); g.v=g.items.reduce((a,i)=>a+i.v,0); });
  const sum=groups.reduce((a,g)=>a+g.v,0);
  return {groups:groups, total:r.total, sum:sum, ml:ml};
}

/* ---------- where it would sell: the engine's per-type roll-up (penetration) gathered by animal (animalOf) ---------- */
const TP_ANIMALS={"Beef":"beef","Sheep/goat":"sheep and goat","Seafood":"seafood","Pork":"pork","Chicken":"chicken"};
const TP_OTHER={"Duck":"duck and goose","Rabbit":"rabbit","Turkey":"turkey"};
function tpByAnimal(cost,b,region){
  region=region||state.region;
  const s=Object.assign({},state,{region:region,income:region===state.region?state.income:C.REGION_INCOME[region],cost_override:cost,lmean:tpLmean(b)});
  const p=penetration(s); let W=0; p.rows.forEach(r=>{ W+=r.mt.w_vol; });
  const by={};
  p.rows.forEach(r=>{ const a=animalOf(r.mt.name), k=(a in TP_ANIMALS)?a:"Other";
    const o=by[k]||(by[k]={key:k,w:0,x:0,pv:0,members:[]});
    o.w+=r.mt.w_vol/W; o.x+=r.mt.w_vol/W*r.sh; o.pv+=r.mt.w_vol/W*r.mt.p_conv;
    if(k==="Other"){ const n=TP_OTHER[a]||a.toLowerCase(); if(o.members.indexOf(n)<0) o.members.push(n); } });
  const rows=Object.keys(by).map(k=>{ const o=by[k];
    return Object.assign(o,{name:k==="Other"?"Other: "+o.members.join(", "):tpCap(TP_ANIMALS[k]), word:k==="Other"?"other meats":TP_ANIMALS[k],
      price:o.pv/o.w, within:o.x/o.w*100, part:p.tv>0?o.x/p.tv:0}); });
  rows.sort((a,c)=>((a.key==="Other")-(c.key==="Other"))||(c.price-a.price));
  return {rows:rows, total:p.tv*100, avg:tpAvgPrice(region)};
}
// the animals that bring most of the sales (enough to pass 60%, at most two), and the cheap ones that bring little
function tpSellers(A){
  const by=A.rows.slice().sort((a,c)=>c.part-a.part), top=[by[0]];
  if(by[0].part<0.6&&by[1]) top.push(by[1]);
  const cheap=A.rows.filter(r=>r.key!=="Other"&&r.price<A.avg);
  return {top:top, part:top.reduce((a,r)=>a+r.part,0), dear:top.reduce((a,r)=>a+r.w*r.price,0)/top.reduce((a,r)=>a+r.w,0)>A.avg*1.15,
          cheap:cheap, cheapW:cheap.reduce((a,r)=>a+r.w,0), cheapPart:cheap.reduce((a,r)=>a+r.part,0)};
}
const tpAnd=l=>l.length<2?l.join(""):l.slice(0,-1).join(", ")+" and "+l[l.length-1];

/* ---------- the live sentence ---------- */
function pgDeck(f){
  const who=f.key==="own"?"With your settings":"With "+f.label, c=f.cost;
  let one;
  if(f.one===null) one="even free cells would not reach 1% of "+tpRegionMeat()+" with these shoppers";
  else if(c>=1.1*f.one) one=tpTimes(c/f.one)+" what it would need to reach 1% of "+tpRegionMeat()+" ("+tpUSDk(f.one)+")";
  else if(c>0.9*f.one) one="about what 1% of "+tpRegionMeat()+" needs ("+tpUSDk(f.one)+")";
  else one="below the "+tpUSDk(f.one)+" that 1% of "+tpRegionMeat()+" needs"+(f.ten!==null&&c<0.9*f.ten?", and below even the "+tpUSDk(f.ten)+" that 10% needs":"");
  const pr=c/f.parity, eaten="the price of the average kilo eaten "+tpEatenWhere()+" ($"+f.avg.toFixed(2)+" in the shop)";
  const par=pr>=1.1?tpTimes(pr)+" the "+tpUSD(f.parity)+" a kilo of cells that would match "+eaten
           :(pr>0.9?"about the "+tpUSD(f.parity)+" a kilo of cells that would match "+eaten:"below the "+tpUSD(f.parity)+" a kilo of cells that would match "+eaten);
  const G=f.groups, big=G.groups.reduce((a,g)=>g.v>a.v?g:a);
  const drv=big.key==="other"?"Most of the cost is energy, gas and other supplies.":
    tpCap(tpFrac(big.v/G.total))+" of the cost scales with "+big.what+(big.key==="litres"?" ("+G.ml.toFixed(0)+" litres a kilo)":"")+".";
  const A=f.animals, sl=tpSellers(A);
  const sh=f.sb[2]<0.00095?"under 0.001% of "+tpRegionMeat():"about "+pgPctS(f.share)+" of "+tpRegionMeat();
  const sold=sl.part>=0.45?", sold mostly as "+tpAnd(sl.top.map(r=>r.word))+(sl.dear?", where meat is dear":""):", spread across many kinds of meat";
  return who+", a kilo of cells costs about "+tpUSD(c)+" to grow (8 in 10 draws: "+tpUSD(f.cb[0])+" to "+tpUSD(f.cb[2])+"): "+one+", and "+par+". "+drv+
    " If "+tpPctB(f.buyers)+" of meat buyers would pick it at the same price, it would take "+sh+" in the long run"+sold+". "+tpVerdictShort(f.rn);
}

/* ---------- figure 1: how far the cost is from what matters (one log axis) ---------- */
function tpTextW(t,fs,bold){            // the width of a label in px at the page's font (an estimate where there is no canvas)
  try{ if(typeof getComputedStyle!=="undefined"){ const c=tpTextW.c||(tpTextW.c=document.createElement("canvas").getContext("2d"));
    c.font=(bold?"600 ":"400 ")+fs+"px "+(tpTextW.fam||(tpTextW.fam=getComputedStyle(document.body).fontFamily)); const w=c.measureText(t).width; if(w>0) return w; } }catch(e){}
  return t.length*fs*(bold?0.6:0.56);
}
// labels set in rows above an axis, each beside its own upright line (to its right, else to its left): a label goes in the lowest row
// where it overlaps no other label, crosses no line that reaches that row, and its own line crosses no label below it
function tpTiers(labs,W,pad,gap){
  const placed=[];
  labs.forEach(l=>{
    for(let t=0;t<8;t++){ for(const side of (l.x>W*0.8?[-1,1]:[1,-1])){
      const x0=side>0?l.x+4:l.x-4-l.w, x1=x0+l.w;
      if(x0<pad||x1>W-pad) continue;
      const clash=placed.some(o=>(o.tier===t&&x0<o.x1+gap&&o.x0<x1+gap)||(o.tier>=t&&o.x>x0-3&&o.x<x1+3)||(o.tier<=t&&l.x>o.x0-3&&l.x<o.x1+3))||
        (t===0&&labs.some(o=>o!==l&&placed.indexOf(o)<0&&o.x>x0-3&&o.x<x1+3));      // every line reaches the lowest row
      if(!clash){ Object.assign(l,{tier:t,side:side,x0:x0,x1:x1}); placed.push(l); return; } } }
    const x0=Math.max(pad,Math.min(W-pad-l.w,l.x+4)); Object.assign(l,{tier:8,side:1,x0:x0,x1:x0+l.w}); placed.push(l); });
  return placed;
}
function tpLineDraw(f){
  const svg=document.getElementById("tp_costline"); if(!svg) return;
  const W=Math.max(300,pgWidth("tp_costline_plot",900)), small=W<560, fs=small?11:12, pad=6;
  const refTop=Math.max.apply(null,TP.refs.map(r=>tpRefCloud(r.key).q[1]).concat([f.cb[2]]))*1.05;
  const lo=1, hi=[10,20,30,50,100,200,300,500,1000,2000,5000].find(v=>v>=refTop)||refTop;
  const X=v=>pad+(Math.log(Math.max(lo,Math.min(hi,v)))-Math.log(lo))/(Math.log(hi)-Math.log(lo))*(W-2*pad);
  const fl=C.FEEDSTOCK_FLOOR, fr=TP.frontier, inR=v=>v!==null&&v>=lo&&v<=hi;
  const meName=f.key==="own"?"Your settings":(small?f.label.replace(", all favourable","").replace("Humbird's optimistic design","Humbird's design"):f.label);
  const labs=[{kind:"me", x:X(f.cost), l1:meName, l2:"median "+tpUSD(f.cost), bold:true}];
  if(inR(f.one)) labs.push({kind:"one", x:X(f.one), l1:"1% of "+tpRegionMeat(true), l2:"needs "+tpUSDk(f.one)});
  if(inR(f.parity)) labs.push({kind:"par", x:X(f.parity), l1:"Price parity", l2:tpUSD(f.parity)});
  if(inR(f.ten)) labs.push({kind:"ten", x:X(f.ten), l1:"10%", l2:"needs "+tpUSDk(f.ten)});
  labs.forEach(l=>{ l.w=Math.max(tpTextW(l.l1,fs,l.bold),tpTextW(l.l2,fs,l.bold)); });
  tpTiers(labs,W,pad,10);
  const nT=1+Math.max.apply(null,labs.map(l=>l.tier)), tierH=2*fs+12, sy=6+nT*tierH, sh=small?30:34, sb=sy+sh;
  const H=sb+(small?78:82);
  const mut='class="ax"', col={me:"var(--ink)",one:"#D85A30",ten:"#D85A30",par:"var(--ink2)"}, dash={par:' stroke-dasharray="4 3"',ten:' stroke-dasharray="6 3"'};
  let g='<defs><pattern id="clhd" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#444441"/><line x1="0" y1="0" x2="0" y2="5" stroke="#B4B2A9" stroke-width="1.5"/></pattern>'+
    '<pattern id="clhl" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#85B7EB"/><line x1="0" y1="0" x2="0" y2="6" stroke="#185FA5" stroke-width="1.3"/></pattern></defs>';
  g+='<rect x="'+pad+'" y="'+sy+'" width="'+(W-2*pad)+'" height="'+sh+'" class="clstrip"/>';
  g+='<rect x="'+X(fl).toFixed(1)+'" y="'+sy+'" width="'+(X(fr)-X(fl)).toFixed(1)+'" height="'+sh+'" fill="url(#clhl)" opacity="0.55"/>';
  g+='<rect x="'+pad+'" y="'+sy+'" width="'+(X(fl)-pad).toFixed(1)+'" height="'+sh+'" fill="url(#clhd)"/>';
  // the cloud: one dot per draw, spread up and down only so that the dots can be seen
  f.cloud.cost.forEach((c,i)=>{ const u=((i*0.6180339887)%1)-0.5;
    g+='<circle class="cldot" cx="'+X(c).toFixed(1)+'" cy="'+(sy+sh/2+u*(sh-10)).toFixed(1)+'" r="'+(small?1.8:2.1)+'"/>'; });
  // the lines and their labels
  labs.slice().sort((a,c)=>(a.kind==="me")-(c.kind==="me")).forEach(l=>{
    const ty=sy-6-l.tier*tierH, top=ty-2*fs-4;
    if(l.kind!=="me") g+='<line x1="'+l.x.toFixed(1)+'" x2="'+l.x.toFixed(1)+'" y1="'+top+'" y2="'+sb+'" stroke="'+col[l.kind]+'" stroke-width="'+(l.kind==="one"?2:1.5)+'"'+(dash[l.kind]||"")+'/>';
    else g+='<line x1="'+l.x.toFixed(1)+'" x2="'+l.x.toFixed(1)+'" y1="'+top+'" y2="'+(sy+sh/2-8)+'" stroke="var(--ink)" stroke-width="1"/>';
    g+='<text x="'+l.x0.toFixed(1)+'" y="'+(ty-fs-4)+'" font-size="'+fs+'"'+(l.bold?' class="b"':'')+'>'+pgEsc(l.l1)+'</text>'+
       '<text x="'+l.x0.toFixed(1)+'" y="'+ty+'" font-size="'+fs+'"'+(l.bold?' class="b"':'')+'>'+pgEsc(l.l2)+'</text>'; });
  const px=X(f.cost);
  g+='<circle class="clme" cx="'+px.toFixed(1)+'" cy="'+(sy+sh/2)+'" r="'+(small?6:7)+'"/>';
  // the range that holds 8 in 10 draws, under the line
  const a=X(f.cb[0]), b=X(f.cb[2]), by=sb+9, rl="8 in 10 draws: "+tpUSD(f.cb[0])+" to "+tpUSD(f.cb[2]), rw=tpTextW(rl,fs);
  g+='<path d="M'+a.toFixed(1)+' '+(by-4)+' V'+by+' H'+b.toFixed(1)+' V'+(by-4)+'" fill="none" stroke="var(--ink)" stroke-width="1.5"/>';
  const rx=Math.max(pad+rw/2,Math.min(W-pad-rw/2,(a+b)/2));
  g+='<text x="'+rx.toFixed(1)+'" y="'+(by+fs+3)+'" text-anchor="middle" font-size="'+fs+'">'+rl+'</text>';
  // the axis
  const ty=by+2*fs+14;
  let lastX=-1e9; const tks=[1,2,5,10,20,50,100,200,500,1000,2000,5000].filter(v=>v>=lo&&v<=hi);
  tks.forEach(v=>{ const x=X(v), t="$"+v, w=tpTextW(t,fs), xc=Math.max(pad+w/2,Math.min(W-pad-w/2,x));
    g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+sb+'" y2="'+(sb+4)+'" '+mut+'/>';
    if(xc-w/2>lastX+6){ g+='<text x="'+xc.toFixed(1)+'" y="'+ty+'" text-anchor="middle" font-size="'+fs+'" class="m">'+t+'</text>'; lastX=xc+w/2; } });
  g+='<text x="'+(W/2)+'" y="'+(ty+fs+6)+'" text-anchor="middle" font-size="'+fs+'" class="m">Cost to grow a kilo of cells (log scale)</text>';
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H);
  svg.innerHTML=g;
}
function tpLineText(f){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const fl=C.FEEDSTOCK_FLOOR, fr=TP.frontier;
  set("tp_cl_fl","below $"+fl.toFixed(2)+": below what the cells must eat");
  set("tp_cl_fr","$"+fl.toFixed(2)+" to $"+fr.toFixed(2)+": beyond every known limit");
  set("tp_cl_note","Price parity: at "+scMoney(f.parity,2)+" a kilo of cells, it would sell at the price of the average kilo eaten "+tpEatenWhere()+" ($"+f.avg.toFixed(2)+
    "), after "+scMoney(state.markup_add)+" a kilo to reach the shelf and the shop's "+(state.retail_margin*100).toFixed(0)+"% margin. "+
    "The 1% and 10% lines are the costs those long-run shares need with "+tpPctB(f.buyers)+" of meat buyers picking it at the same price (your assumption, below the map)"+
    (f.one===null?"; with these shoppers no cost reaches 1%":(f.ten===null?"; with these shoppers no cost reaches 10%":(f.ten<1?"; 10% would need under $1":"")))+". "+
    "Dots: "+f.cloud.n+" draws of the estimates nobody has measured; your point is their median. With every estimate at its most likely value, it is "+scMoney(f.point)+".");
  set("tp_cl_alt","A log scale of the cost to grow a kilo of cells, from $1 up. Below $"+fl.toFixed(2)+" is impossible (what the cells must eat); up to $"+fr.toFixed(2)+
    " needs some lever past every known limit. Price parity with the average kilo eaten "+tpEatenWhere()+": "+scMoney(f.parity,2)+". "+
    (f.one===null?"No cost reaches 1% with these shoppers. ":"1% of "+tpRegionMeat()+" needs "+tpUSDk(f.one)+(f.ten!==null?"; 10% needs "+tpUSDk(f.ten):"")+". ")+
    f.label+": median "+tpUSD(f.cost)+", 8 in 10 draws "+tpUSD(f.cb[0])+" to "+tpUSD(f.cb[2])+".");
}

/* ---------- figure 2: where the money goes, by what drives it ---------- */
const TP_GCOL={litres:"var(--s1)", time:"var(--s3)", other:"var(--s4)"};
function tpGroupsDraw(f){
  const svg=document.getElementById("tp_groups"); if(!svg) return;
  const G=f.groups, W=Math.max(280,pgWidth("tp_groups_plot",440)), small=W<420, fs=small?11:12, pad=4;
  const xmax=Math.max(G.total,f.one||0)*1.04, step=[1,2,5,10,20,25,50,100,200,500].find(s=>xmax/s<=(small?4:6))||1000;
  const X=v=>pad+(W-2*pad)*v/xmax, by=fs+14, bh=small?26:30, H=by+bh+fs+14;
  let g='', acc=0;
  G.groups.forEach(gr=>{ gr.items.forEach(it=>{ if(it.v<=0) return; const a=X(acc), b=X(acc+it.v); acc+=it.v;
      g+='<rect x="'+a.toFixed(1)+'" y="'+by+'" width="'+Math.max(0.5,b-a-1.5).toFixed(1)+'" height="'+bh+'" fill="'+TP_GCOL[gr.key]+'"><title>'+pgEsc(it.name)+': $'+it.v.toFixed(2)+' a kilo</title></rect>'; }); });
  acc=0;
  G.groups.forEach(gr=>{ const a=X(acc), b=X(acc+gr.v); acc+=gr.v; const t=Math.round(gr.v/G.total*100)+"%";
    if(b-a>tpTextW(t,fs,true)+8) g+='<text x="'+(a+4).toFixed(1)+'" y="'+(by+bh/2+fs*0.36).toFixed(1)+'" font-size="'+fs+'" class="on" font-weight="700">'+t+'</text>'; });
  if(f.one!==null){ const x=X(f.one), t="1% of "+tpRegionMeat(true)+" needs "+tpUSDk(f.one), w=tpTextW(t,fs), cx=Math.max(pad+w/2,Math.min(W-pad-w/2,x));
    g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+(by-6)+'" y2="'+(by+bh+4)+'" stroke="#D85A30" stroke-width="2"/>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(by-9)+'" text-anchor="middle" font-size="'+fs+'">'+pgEsc(t)+'</text>'; }
  for(let t=0;t<=xmax+1e-9;t+=step){ const x=X(t), s="$"+t, w=tpTextW(s,fs), xc=Math.max(pad+w/2,Math.min(W-pad-w/2,x));
    g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+(by+bh)+'" y2="'+(by+bh+4)+'" class="ax"/><text x="'+xc.toFixed(1)+'" y="'+(by+bh+fs+6)+'" text-anchor="middle" font-size="'+fs+'" class="m">'+s+'</text>'; }
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H);
  svg.innerHTML=g;
}
function tpGroupsText(f){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const G=f.groups, $2=v=>"$"+v.toFixed(2), pc=v=>Math.round(v/G.total*100)+"%";
  set("tp_groups_sub",scMoney(G.total)+" a kilo of cells with every estimate at its most likely value"+(Math.abs(G.total-f.cost)>0.05?" (the median of the draws, "+tpUSD(f.cost)+", is the figure above)":"")+".");
  set("tp_groups_table",'<table class="num grp"><tbody>'+G.groups.map(gr=>
    '<tr class="gh"><td><span class="sw" style="background:'+TP_GCOL[gr.key]+'"></span>'+gr.name+(gr.note?' <span class="gn">'+gr.note+'</span>':'')+'</td><td>'+$2(gr.v)+'</td><td>'+pc(gr.v)+'</td></tr>'+
    gr.items.map(it=>'<tr><td class="it">'+it.name+(it.note?' <span class="gn">'+it.note+'</span>':'')+'</td><td>'+$2(it.v)+'</td><td></td></tr>').join("")).join("")+
    '<tr class="gt"><td>Total, a kilo of cells</td><td>'+$2(G.sum)+'</td><td></td></tr></tbody></table>');
  const L=G.groups[0], T=G.groups[1], rm=tpRegionMeat();
  let s;
  if(f.one===null) s="With these shoppers no cost of cells reaches 1% of "+rm+".";
  else if(G.total<=f.one) s="For 1% of "+rm+" the whole kilo must cost "+tpUSDk(f.one)+": at "+scMoney(G.total)+" this one does, with "+scMoney(f.one-G.total)+" to spare.";
  else if(Math.max(L.v,T.v)>f.one) s="For 1% of "+rm+" the whole kilo must cost "+tpUSDk(f.one)+": "+(L.v>=T.v?"the litres alone ("+scMoney(L.v)+") cost":"the time in the tank alone ("+scMoney(T.v)+") costs")+" more than that.";
  else s="For 1% of "+rm+" the whole kilo must cost "+tpUSDk(f.one)+", "+scMoney(G.total-f.one)+" less than this: the litres are "+scMoney(L.v)+" of it, the time in the tank "+scMoney(T.v)+".";
  set("tp_groups_say",s);
  set("tp_groups_alt","A bar of "+scMoney(G.total)+" split by what drives the cost: "+G.groups.map(gr=>gr.name.toLowerCase()+" "+$2(gr.v)+" ("+pc(gr.v)+")").join("; ")+
    (f.one!==null?". A line marks the "+tpUSDk(f.one)+" that 1% of "+rm+" needs.":"."));
}

/* ---------- figure 3: where it would sell, share within each kind of meat ---------- */
function tpAnimalsRender(f){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const A=f.animals, top=Math.max.apply(null,A.rows.map(r=>r.within)), nice=[1e-4,2e-4,5e-4,1e-3,2e-3,5e-3,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5,10,20,50,100],
        max=nice.find(v=>v>=top*1.02)||100, rw=tpRegionMeat(true), part=v=>v<0.005?"under 1%":Math.round(v*100)+"%",
        wp=v=>{ const x=v*100; return x<9.5?x.toFixed(1):x.toFixed(0); };
  set("tp_animals_sub",pgRegionName()+", at the median cost of "+tpUSD(f.cost)+" and "+tpPctB(f.buyers)+" of meat buyers picking it at the same price. Most expensive meat first.");
  set("tp_animals",A.rows.map(r=>'<div class="anrow"><div class="anhd"><b>'+r.name+'</b><span class="anv">'+pgPctS(r.within)+(r.key==="Other"?' of these':' of '+r.word)+'</span></div>'+
      '<div class="antr"><span class="anbar" style="width:'+(Math.min(r.within,max)/max*100).toFixed(2)+'%"></span></div>'+
      '<div class="ansub">'+wp(r.w)+'% of '+rw+', $'+r.price.toFixed(2)+' a kilo on average; '+part(r.part)+' of its sales</div></div>').join("")+
    '<div class="anrow antot"><div class="anhd"><b>All meat and seafood</b><span class="anv">'+pgPctS(A.total)+'</span></div>'+
    '<div class="ansub">$'+A.avg.toFixed(2)+' a kilo on average. Plant-based meat today: about '+pgAbout(f.pb)+'%.</div></div>');
  set("tp_animals_scale","Bars on one scale, from 0 to "+(+max.toPrecision(2))+"% of each kind of meat. Shares by weight, in the long run.");
  const sl=tpSellers(A), cheapN=tpAnd(sl.cheap.map(r=>r.word));
  let s=tpCap(tpAnd(sl.top.map(r=>r.word)))+" bring "+tpFrac(sl.part)+" of its sales.";
  if(sl.cheap.length&&sl.cheapW>=0.3&&sl.cheapPart<0.6*sl.cheapW)
    s+=" "+tpCap(cheapN)+" "+(sl.cheap.length>1?"are":"is")+" "+tpFrac(sl.cheapW)+" of "+tpRegionMeat()+" but cheap, so it sells little there"+
       (f.sb[2]<0.00095?".":": that is why the share of all meat and seafood is only "+pgPctS(A.total)+".");
  else if(sl.cheap.length) s+=" "+tpCap(cheapN)+", the cheaper meats, bring "+part(sl.cheapPart)+".";
  set("tp_animals_say",s);
  set("tp_animals_alt","Long-run share within each kind of meat, "+pgRegionName()+": "+A.rows.map(r=>r.name+" "+pgPctS(r.within)+" ("+wp(r.w)+"% of all meat, "+part(r.part)+" of its sales)").join("; ")+
    ". All meat and seafood: "+pgPctS(A.total)+".");
}

/* ---------- setting things ---------- */
function pgResetShoppers(){          // every shopper setting back to the model's value (keeps the region)
  MODEL.sliders.forEach(s=>{ state[s.key]=s.start; if(s.solved) state[s.key+"_ovr"]=false; });
  MODEL.toggles.forEach(t=>{ state[t.key]=false; });
  state.income=C.REGION_INCOME[state.region];
  if(typeof pgSyncControls==="function") pgSyncControls();
}
function tpSetBuyers(b){ SCS.buyers=Math.min(0.99,Math.max(0.01,b)); }
function tpLoad(k){
  const r=tpRef(k); if(!r||r.kind==="company") return;
  SCS.ref=k; SCS.from=k; SCS.traits={}; SCS.held={}; SCS.src="scenario";
  if(r.kind==="humbird"){ SCS.base="humbird"; SCS.hb={mode:"perfusion",plant:"sterile"}; SCS.choice=Object.assign({},SC.presets[SC.start].choice); SCS.redesign=false; }
  else { SCS.base="switches"; SCS.choice=Object.assign({},r.choice); SCS.redesign=r.redesign; }
  SCS.preset=scPresetOf(SCS.choice);
  tpSetBuyers(r.buyers); tpCommit();
}
const scApply=tpLoad;
// after the reader changes the cells or the plant: the tank design chosen again for the new case (scenarios._design_traits), unless
// the reference point keeps its own (Published cells: no tank tricks, an ordinary tall tank)
function tpRedesign(){
  if(SCS.base!=="switches"||!SCS.redesign) return;
  SCS.choice=scWithExtra(Object.assign({},SCS.traits),()=>scDesign(SCS.choice));
}
function tpTouched(){ SCS.ref=null; SCS.src="scenario"; }
function tpExtraNow(){ SC_EXTRA=Object.assign({},SCS.traits,tpHeldKw(SCS.held)); }
// a light update while a slider moves: the cloud, the map's point and the numbers (no new calibration)
function tpLive(){ tpSchedule(()=>{ tpExtraNow(); PGS.cloud=tpCloudFor(SCS); pgSetCost(); tpRenderFirst(); }); }
// slider moves are drawn at most once a frame
function tpSchedule(fn){ PGS.rafFn=fn; if(typeof requestAnimationFrame==="undefined"){ fn(); return; }
  if(!PGS.raf) PGS.raf=requestAnimationFrame(()=>{ PGS.raf=null; const f=PGS.rafFn; PGS.rafFn=null; if(f) f(); }); }
// a full update: everything on the page
function tpCommit(){
  PGS.rafFn=null;
  tpRedesign(); tpExtraNow(); SCS.preset=scPresetOf(SCS.choice);
  PGS.cloud=null;
  if(KP) state.equal_price_share=tpDial(SCS.buyers);
  recompute();
}
function scCommit(){ tpCommit(); }
function scPick(k,v){                // a switch in "Check the engineering"
  if(SCS.base==="humbird"){ SCS.base="switches"; SCS.redesign=true; }
  SCS.choice[k]=v;
  if(k==="cells") ["nh3_kg","lac_yield","mass_pg"].forEach(t=>delete SCS.traits[t]);
  if(k==="growth") delete SCS.traits.doubling_h;
  if(k==="tricks"||k==="shape") SCS.redesign=false;               // the reader chose the tank design
  tpTouched(); tpCommit(); }
function scDesignNow(){ SCS.redesign=true; tpTouched(); tpCommit(); }
function scPickTwo(a,i,b,j){ SCS.choice[a]=i; SCS.choice[b]=j; if([a,b].some(k=>k==="tricks"||k==="shape")) SCS.redesign=false; tpTouched(); tpCommit(); }
function scApplyChoice(o){ SCS.base="switches"; SCS.choice=Object.assign({},SC.presets[SC.start].choice,o); SCS.traits={}; SCS.held={}; SCS.redesign=false; tpTouched(); tpCommit(); }
function tpSetTrait(k,v,live){ SCS.traits[k]=v; tpTouched(); if(live) tpLive(); else tpCommit(); }
function tpFreeTrait(k){ delete SCS.traits[k]; tpTouched(); tpCommit(); }
function tpSetHeld(k,v,live){ SCS.held[k]=v; tpTouched(); if(live) tpLive(); else tpCommit(); }
function tpFreeHeld(k){ delete SCS.held[k]; tpTouched(); tpCommit(); }
function tpSetMode(m){
  if(SCS.base==="humbird") SCS.hb.mode=m; else SCS.choice.mode=m;
  if(m!=="perfusion") delete SCS.held.cpl;
  tpTouched(); tpCommit(); }
function tpSetPlant(v){ if(SCS.base==="humbird") SCS.hb.plant=v; else SCS.choice.plant=v; tpTouched(); tpCommit(); }

/* ---------- the address: the settings in the hash (#tp=...) ---------- */
function scSettingsHash(){
  if(SCS.ref&&Math.abs(SCS.buyers-tpRef(SCS.ref).buyers)<1e-9) return SCS.ref===SC.start?"":SCS.ref;
  const parts=["from:"+SCS.from,"base:"+SCS.base,"buyers:"+(+SCS.buyers.toFixed(4))];
  if(SCS.ref) parts.push("ref:"+SCS.ref);
  if(SCS.base==="humbird") parts.push("hb:"+SCS.hb.mode+"/"+SCS.hb.plant); else parts.push("ch:"+SC.keys.map(k=>SCS.choice[k]).join("/"), "rd:"+(SCS.redesign?1:0));
  Object.keys(SCS.traits).forEach(k=>parts.push("t."+k+":"+(+SCS.traits[k].toPrecision(6))));
  Object.keys(SCS.held).forEach(k=>parts.push("h."+k+":"+(+SCS.held[k].toPrecision(6))));
  return parts.join(",");
}
function scReadHash(v){
  if(!v) return;
  if(tpRef(v)&&tpRef(v).kind!=="company"){ const r=tpRef(v); SCS.ref=v; SCS.from=v; SCS.buyers=r.buyers;
    if(r.kind==="humbird"){ SCS.base="humbird"; SCS.redesign=false; } else { SCS.choice=Object.assign({},r.choice); SCS.redesign=r.redesign; } return; }
  const kv={}; v.split(",").forEach(x=>{ const i=x.indexOf(":"); if(i>0) kv[x.slice(0,i)]=x.slice(i+1); });
  if(tpRef(kv.from)) SCS.from=kv.from;
  SCS.base=kv.base==="humbird"?"humbird":"switches"; SCS.ref=tpRef(kv.ref)?kv.ref:null;
  const b=parseFloat(kv.buyers); if(isFinite(b)) tpSetBuyers(b);
  if(kv.hb){ const [m,p]=kv.hb.split("/"); if(scSetting("mode",m)) SCS.hb.mode=m; if(scSetting("plant",p)) SCS.hb.plant=p; }
  if(kv.ch){ const vals=kv.ch.split("/"); SC.keys.forEach((k,i)=>{ if(vals[i]&&scSetting(k,vals[i])) SCS.choice[k]=vals[i]; }); }
  SCS.redesign=kv.rd==="1";
  SCS.traits={}; SCS.held={};
  Object.keys(kv).forEach(k=>{ const x=parseFloat(kv[k]); if(!isFinite(x)) return;
    if(k.indexOf("t.")===0&&TRAIT_KEYS.indexOf(k.slice(2))>=0) SCS.traits[k.slice(2)]=x;
    if(k.indexOf("h.")===0&&["capex_x","cpl","medium_price"].indexOf(k.slice(2))>=0) SCS.held[k.slice(2)]=x; });
  SCS.preset=scPresetOf(SCS.choice);
}

/* ---------- the first screen: the controls ---------- */
function tpFmtTrait(k,v){ const T=TP.traits[k], x=v*T.scale; return (k==="doubling_h"?x.toFixed(1).replace(/\.0$/,""):(k==="mass_pg"?x.toFixed(2):x.toFixed(k==="nh3_kg"?3:2)))+" "+T.unit; }
function tpBuildControls(){
  const refs=document.getElementById("tp_refs");
  if(refs) refs.innerHTML=TP.refs.filter(r=>r.kind!=="company").map(r=>'<button type="button" class="refbtn" id="ref_'+r.key+'" onclick="tpLoad(\''+r.key+'\')" title="'+pgEsc(r.text)+'">'+r.label+'</button>').join("");
  const host=document.getElementById("tp_traits");
  if(host) host.innerHTML=TRAIT_KEYS.map(k=>{ const T=TP.traits[k];
    return '<div class="ctl tr"><label for="tr_'+k+'"><span class="nm">'+T.name+', '+T.unit+'</span><span class="q" tabindex="0" data-tip="'+pgEsc(T.help)+'">?</span><span class="val" id="trv_'+k+'"></span></label>'+
      '<input type="range" id="tr_'+k+'" min="'+T.min+'" max="'+T.max+'" step="'+T.step+'" aria-describedby="trs_'+k+'">'+
      '<div class="trs" id="trs_'+k+'"></div></div>'; }).join("");
  TRAIT_KEYS.forEach(k=>{ const e=document.getElementById("tr_"+k); if(!e||!e.addEventListener) return; const T=TP.traits[k];
    e.addEventListener("input",()=>tpSetTrait(k,parseFloat(e.value)/T.scale,true));
    e.addEventListener("change",()=>tpSetTrait(k,parseFloat(e.value)/T.scale,false)); });
  const by=document.getElementById("tp_buyers");
  if(by&&by.addEventListener){ by.addEventListener("input",()=>{ tpSetBuyers(parseFloat(by.value)/100); tpTouched(); tpSchedule(tpRenderFirst); });
    by.addEventListener("change",()=>{ tpSetBuyers(parseFloat(by.value)/100); tpTouched(); tpCommit(); }); }
  const wire=(id,fn)=>{ const e=document.getElementById(id); if(!e||!e.addEventListener) return;
    e.addEventListener("input",()=>fn(parseFloat(e.value),true)); e.addEventListener("change",()=>fn(parseFloat(e.value),false)); };
  wire("pl_capex",(v,l)=>tpSetHeld("capex_x",v,l)); wire("pl_cpl",(v,l)=>tpSetHeld("cpl",v,l)); wire("pl_med",(v,l)=>tpSetHeld("medium_price",v,l));
  const sel=document.getElementById("regionsel");
  if(sel){ sel.innerHTML=PG.regions.map(r=>'<option value="'+r[0]+'">'+r[1]+'</option>').join("");
    sel.onchange=()=>{ state.region=sel.value; setIncome(C.REGION_INCOME[state.region]); if(typeof fillCurveSel==="function") fillCurveSel(); recompute(); }; }
  const ps=document.getElementById("pl_plant");
  if(ps) ps.innerHTML=scSwitch("plant").settings.map(t=>'<option value="'+t.key+'">'+t.label+'</option>').join("");
  const vs=document.getElementById("pl_size");
  if(vs) vs.innerHTML=scSwitch("mode").settings.filter(t=>t.key!=="perfusion").reverse().map(t=>'<option value="'+t.key+'">'+(t.key==="fedbatch"?"20 m³: the size pharma and Upside Foods run":(t.key==="fedbatch50"?"50 m³: twice the largest animal-cell tank":"100 m³: nobody has grown animal cells this big"))+'</option>').join("");
  try{ PGS.readDismissed=localStorage.getItem("tp_read_off")==="1"; }catch(e){ PGS.readDismissed=false; }
  const rp=document.getElementById("tpramp");
  if(rp) rp.innerHTML=[0.001,0.01,0.1,1,10,50].map(v=>'<span><i style="background:'+tpCol(v)+'"></i>'+v+'%</span>').join("");
  if(document.querySelectorAll) document.querySelectorAll(".q[data-tip]").forEach(q=>{ if(!q.addEventListener) return; const t=q.getAttribute("data-tip");
    q.addEventListener("mouseenter",e=>showTip(e,t)); q.addEventListener("mouseleave",hideTip);
    q.addEventListener("focus",e=>showTip(e,t)); q.addEventListener("blur",hideTip);
    q.addEventListener("click",e=>{ const tp=document.getElementById("tip"); if(tp&&tp.style.display==="block") hideTip(); else showTip(e,t); }); });
}
function tpDismissRead(){ PGS.readDismissed=true; try{ localStorage.setItem("tp_read_off","1"); }catch(e){} const r=document.getElementById("tp_read"); if(r) r.style.display="none"; }
function tpRenderControls(f){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  TP.refs.forEach(r=>{ const b=document.getElementById("ref_"+r.key); if(b) b.setAttribute("aria-pressed",SCS.ref===r.key?"true":"false"); });
  set("tp_refnote",SCS.ref?"Loaded: <b>"+tpLabel(SCS.ref)+"</b>. <span class=\"long\">"+pgEsc(tpRef(SCS.ref).text)+"</span>"
     :"Your own settings, started from <b>"+tpLabel(SCS.from)+"</b>. Load a reference point to start again.");
  const tr=tpTraitsShown(), drawn=TP.cloud.wide&&SCS.base!=="humbird";
  TRAIT_KEYS.forEach(k=>{ const T=TP.traits[k], e=document.getElementById("tr_"+k), v=tr[k];
    if(e&&document.activeElement!==e) e.value=v*T.scale;
    set("trv_"+k,tpFmtTrait(k,v));
    const isDrawn=!(k in SCS.traits)&&drawn&&(k==="mass_pg"||(k==="nh3_kg"&&(SCS.choice.cells==="selected"||SCS.choice.cells==="measured")));
    const q=TP.cloud.priors[k==="mass_pg"?"sc_mass_selected_pg":"sc_nh3_selected"];
    set("trs_"+k,(isDrawn?'<span class="drawn">The cloud draws it between '+tpFmtTrait(k,q[0]).split(" ")[0]+' and '+tpFmtTrait(k,q[2])+' until you move it.</span> ':"")+
      ((k in SCS.traits)?'<button type="button" class="lnk" onclick="tpFreeTrait(\''+k+'\')">Back to '+tpLabel(SCS.from)+'</button>':"")); });
  // the routes verdict
  const rn=f.rn, chip={feed:"feed change, meat cells",select_meat:"selection, meat cells",select_other:"without engineering, other cells only",engineering:"only with genetic engineering","null":"not shown by any route"};
  set("tp_verdict",'<p class="vsent"><b>'+tpVerdictPlain(rn)+'</b></p><table class="vt"><tbody>'+TRAIT_KEYS.map(k=>{ const p=rn.traits[k], best=TP.routes.routes[k];
      return '<tr><td>'+TP.traits[k].name.replace(/ \(.*\)$/,"")+'<br><span class="alt">'+tpFmtTrait(k,p.value)+'</span></td><td><span class="tag rt rt'+(p.route===null?"none":p.route)+'">'+chip[String(p.route)]+'</span>'+
        '<br><span class="alt">Best shown: '+best.map(x=>chip[x[0]].split(",")[0]+" "+tpFmtTrait(k,x[1]).replace(/ [a-z].*$/,"")).join("; ")+'</span></td></tr>'; }).join("")+'</tbody></table>'+
    '<p class="note">Each trait is judged alone, against the best level each route has shown. It says what has been shown, not what is possible. '+
    '<a href="'+TP.trait_note+'">The evidence for each route</a>.</p>');
  // the plant
  const mode=tpMode(), fb=mode!=="perfusion", plant=tpPlant();
  const pr=document.getElementById("pl_perf"), fr=document.getElementById("pl_fbr"), sz=document.getElementById("pl_size"), ps=document.getElementById("pl_plant");
  if(pr) pr.checked=!fb; if(fr) fr.checked=fb; if(sz){ sz.disabled=!fb; if(fb) sz.value=mode; } if(ps) ps.value=plant;
  const p=tpParams(), hd=SCS.held;
  const cx=document.getElementById("pl_capex"); if(cx&&document.activeElement!==cx) cx.value=hd.capex_x===undefined?1:hd.capex_x;
  set("pl_capex_v",(hd.capex_x===undefined?1:hd.capex_x).toFixed(2)+"×");
  const other=Object.assign({},SCS,{choice:Object.assign({},SCS.choice,{mode:fb?"perfusion":"fedbatch"}),hb:Object.assign({},SCS.hb,{mode:fb?"perfusion":"fedbatch"})});
  const otherCost=floorExplore(tpParamsFor(other)).total;
  set("pl_capex_s",(hd.capex_x===undefined?'<span class="drawn">Drawn between '+(SCS.base!=="humbird"&&plant==="lean"?TP.cloud.lean_capex_lo.toFixed(2):TP.plant.capex[0].toFixed(2))+'× and '+TP.plant.capex[1]+'× until you set it.</span> ':'<button type="button" class="lnk" onclick="tpFreeHeld(\'capex_x\')">Let it vary again</button> ')+
    'At these settings, every estimate at its most likely value: '+(fb?'fed-batch '+scMoney(f.point)+', perfusion '+scMoney(otherCost):'perfusion '+scMoney(f.point)+', fed-batch at 20 m³ '+scMoney(otherCost))+' a kilo.');
  const cp=document.getElementById("pl_cpl"), cplNow=hd.cpl===undefined?TP.plant.mem_price/TP.plant.mem_life:hd.cpl;
  if(cp){ cp.disabled=fb; if(document.activeElement!==cp) cp.value=cplNow; }
  const r0=floorExplore(p);
  set("pl_cpl_v",fb?"no filter":"$"+cplNow.toFixed(2)+" a litre");
  set("pl_cpl_s",fb?"Fed-batch has no filter: the cells stay in the tank until the harvest."
    :(hd.cpl===undefined?'<span class="drawn">Drawn: membranes last 900–5,500 litres per m² until you set it.</span> ':'<button type="button" class="lnk" onclick="tpFreeHeld(\'cpl\')">Let it vary again</button> ')+
     'This is a membrane life of '+Math.round(TP.plant.mem_price/cplNow).toLocaleString("en-US")+' litres per m² at $'+TP.plant.mem_price.toLocaleString("en-US")+' a m²'+
     (r0.membranes>0&&r0.medium_l>0?'; with runs lost early, the membranes add $'+(r0.membranes/r0.medium_l).toFixed(2)+' to each litre of medium here':'')+'.');
  const md=document.getElementById("pl_med"), mNow=hd.medium_price===undefined?(p.medium_price===undefined?0.15:p.medium_price):hd.medium_price;
  if(md&&document.activeElement!==md) md.value=mNow;
  set("pl_med_v",mNow<0.005?"at the nutrient floor":"$"+mNow.toFixed(2)+" a litre");
  set("pl_med_s",(hd.medium_price===undefined?'<span class="drawn">Drawn between 0.6 and 1.5 times this until you set it.</span> ':'<button type="button" class="lnk" onclick="tpFreeHeld(\'medium_price\')">Let it vary again</button> ')+
    (r0.medium_floor?"The medium cannot cost less than the nutrients the cells eat, so the floor sets it here. ":"")+
    "Each kilo of cells takes "+r0.medium_l.toFixed(0)+" litres.");
  set("pl_design",SCS.base==="humbird"?"Humbird's design has no tank tricks: gas bubbled in at the base of an ordinary tall tank."
    :"The tank design: "+scSetting("tricks",SCS.choice.tricks).label.charAt(0).toLowerCase()+scSetting("tricks",SCS.choice.tricks).label.slice(1)+"; "+
     scSetting("shape",SCS.choice.shape).label.charAt(0).toLowerCase()+scSetting("shape",SCS.choice.shape).label.slice(1)+". "+
     (SCS.redesign?"Chosen again whenever the cells or the plant change: the cheapest design that passes the checks on the CO₂ loop.":"Kept as set: Published cells keep an ordinary tall tank with no tricks, and a design you pick under Check the engineering stays."));
  const by=document.getElementById("tp_buyers"); if(by&&document.activeElement!==by) by.value=(SCS.buyers*100).toFixed(1);
  set("tp_buyers_v",tpPctB(SCS.buyers));
  const lm=tpLmean(SCS.buyers), at=R=>shareCalc(R,KP,{ax:state.accept_x,tfM:state.theta_free_M,income:C.income_ref,nbx:state.neophobia_x,hx:state.health_x,lmean:lm,which:"x_meat"})*100;
  const free=at(0);
  set("tp_buyers_read","If it cost half as much as meat, "+at(0.5).toFixed(0)+"% of meat buyers would pick it; if it were free, "+free.toFixed(0)+"%, so "+(100-free).toFixed(0)+
    "% would not take it at any price. Nobody has measured this. Surveys run from about 5% to 60%. The model's own setting is "+tpPctB(tpRef("central").buyers)+
    "; Engineered cells, all favourable assumes "+tpPctB(tpRef("best").buyers)+"; 50% means no preference.");
  const sel=document.getElementById("regionsel"); if(sel) sel.value=state.region;
}

/* ---------- the contour map ---------- */
const TPM={x0:1.5, x1:400, levels:[0.01,0.1,1,10,30,50], nx:26,
  ramp:["#E6F1FB","#B5D4F4","#85B7EB","#378ADD","#185FA5","#0C447C","#042C53"], line:"#D85A30", halo:"#1a1a19"};
TPM.xs=Array.from({length:TPM.nx},(_,i)=>TPM.x0*Math.pow(TPM.x1/TPM.x0,i/(TPM.nx-1)));
TPM.ys=Array.from({length:20},(_,j)=>0.025+0.05*j);
function tpCol(z){ const R=TPM.ramp, hex=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
  let t=(Math.log10(Math.max(z,1e-4))+3)/4.8; t=Math.max(0,Math.min(1,t))*(R.length-1);
  const i=Math.min(R.length-2,Math.floor(t)), f=t-i, a=hex(R[i]), b=hex(R[i+1]);
  return "rgb("+a.map((v,k)=>Math.round(v+(b[k]-v)*f)).join(",")+")"; }
function tpGridKey(){ return pgShopperKey()+"|"+state.markup_add+"|"+state.retail_margin; }
function pgShopperKey(){ return MODEL.sliders.filter(s=>s.key!=="equal_price_share").map(s=>state[s.key]+(s.solved&&state[s.key+"_ovr"]?"p":"")).join(",")+"|"+state.region+"|"+state.income; }
function tpGridRow(b){ return TPM.xs.map(x=>tpShare(x,b)); }
// the grid is computed a few rows at a time so the page stays responsive; the map is drawn without it meanwhile
function tpGridEnsure(){
  const key=tpGridKey();
  if(PGS.gridKey===key&&PGS.grid&&PGS.grid.done) return;
  if(PGS.gridBusy===key) return;
  PGS.gridBusy=key; const z=[]; let j=0;
  const step=()=>{ if(PGS.gridBusy!==key) return;
    for(let k=0;k<4&&j<TPM.ys.length;k++,j++) z.push(tpGridRow(TPM.ys[j]));
    if(j<TPM.ys.length){ setTimeout(step,0); return; }
    PGS.grid={z:z, done:true}; PGS.gridKey=key; PGS.gridBusy=false; tpMapDraw(); };
  if(typeof setTimeout==="undefined"){ while(j<TPM.ys.length) z.push(tpGridRow(TPM.ys[j++])); PGS.grid={z:z,done:true}; PGS.gridKey=key; PGS.gridBusy=false; }
  else setTimeout(step,0);
}
// where an iso-share line crosses each row: [cost, y] pairs (share falls as cost rises along a row)
function tpContour(z,L){
  const out=[];
  TPM.ys.forEach((y,j)=>{ const r=z[j];
    for(let i=0;i<r.length-1;i++){ if(r[i]>=L&&r[i+1]<L){ const t=(Math.log(r[i])-Math.log(L))/(Math.log(r[i])-Math.log(r[i+1]));
      out.push([Math.exp(Math.log(TPM.xs[i])+t*(Math.log(TPM.xs[i+1])-Math.log(TPM.xs[i]))),y]); break; } } });
  return out;
}
function tpInterp(cx,cy){
  const G=PGS.grid; if(!G||!G.done) return null;
  const X=TPM.xs, Y=TPM.ys; let i=0; while(i<X.length-2&&X[i+1]<cx) i++; let j=0; while(j<Y.length-2&&Y[j+1]<cy) j++;
  const tx=Math.max(0,Math.min(1,(Math.log(cx)-Math.log(X[i]))/(Math.log(X[i+1])-Math.log(X[i])))), ty=Math.max(0,Math.min(1,(cy-Y[j])/(Y[j+1]-Y[j])));
  const g=(a,b)=>Math.log(Math.max(a,1e-9))*(1-tx)+Math.log(Math.max(b,1e-9))*tx;
  return Math.exp(g(G.z[j][i],G.z[j][i+1])*(1-ty)+g(G.z[j+1][i],G.z[j+1][i+1])*ty);
}
// labels are placed greedily: each tries its candidate spots in order and takes the first that overlaps nothing placed
function tpPlacer(){ const boxes=[];
  const hit=(a)=>boxes.some(b=>a.x0<b.x1&&b.x0<a.x1&&a.y0<b.y1&&b.y0<a.y1);
  return { block:(x0,y0,x1,y1)=>boxes.push({x0,y0,x1,y1}),
    box:(x,y,txt,fs,anchor,rot)=>{ const w=txt.length*fs*0.58+2, h=fs*1.15;
      let x0=anchor==="end"?x-w:(anchor==="middle"?x-w/2:x), y0=y-fs*0.85;
      if(rot){ const len=w; return anchor==="end"?{x0:x-fs*0.9,x1:x+fs*0.3,y0:y,y1:y+len}:{x0:x-fs*0.9,x1:x+fs*0.3,y0:y-len,y1:y}; }
      return {x0:x0,y0:y0,x1:x0+w,y1:y0+h}; },
    tryPut:function(cands,within){ for(const c of cands){ const b=this.box(c.x,c.y,c.t,c.fs,c.anchor,c.rot);
        if(within&&(b.x0<within[0]||b.x1>within[2]||b.y0<within[1]||b.y1>within[3])) continue;
        if(!hit(b)){ boxes.push(b); return c; } } return null; } };
}
function tpLabelSVG(c,cls){
  const rot=c.rot?' transform="rotate(-90 '+c.x.toFixed(1)+' '+c.y.toFixed(1)+')"':'';
  return '<text class="ml'+(cls?" "+cls:"")+'" x="'+c.x.toFixed(1)+'" y="'+c.y.toFixed(1)+'" font-size="'+c.fs+'" text-anchor="'+(c.anchor||"start")+'"'+rot+'>'+pgEsc(c.t)+'</text>';
}
let TPGEO=null;
function tpMapDraw(f){
  const svg=document.getElementById("tpmap"); if(!svg||!KP) return;
  f=f||pgFacts();
  const W=Math.max(300,pgWidth("tpplot",860)), small=W<560, H=small?Math.round(W*0.95):Math.min(520,Math.round(W*0.66));
  const L=small?50:62, R=W-(small?10:18), T=small?46:58, B=H-(small?44:46);
  const lx=v=>L+(Math.log(v)-Math.log(TPM.x0))/(Math.log(TPM.x1)-Math.log(TPM.x0))*(R-L), ly=v=>B-v*(B-T);
  const G=PGS.grid&&PGS.grid.done&&PGS.gridKey===tpGridKey()?PGS.grid:null;
  const fl=C.FEEDSTOCK_FLOOR, fr=TP.frontier, par=f.parity, avg=f.avg, mut='class="ax"';
  const pl=tpPlacer(), within=[L+2,T+2,R-2,B-2];
  let g='<defs><pattern id="hd" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#444441"/><line x1="0" y1="0" x2="0" y2="5" stroke="#B4B2A9" stroke-width="1.5"/></pattern>'+
    '<pattern id="hl" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#ffffff" stroke-width="1.3" stroke-opacity="0.45"/></pattern>'+
    '<clipPath id="tpclip"><rect x="'+L+'" y="'+T+'" width="'+(R-L)+'" height="'+(B-T)+'"/></clipPath></defs>';
  g+='<g clip-path="url(#tpclip)">';
  if(G){ const xe=TPM.xs.map((v,i)=>i===0?TPM.x0:Math.sqrt(v*TPM.xs[i-1])).concat([TPM.x1]), ye=TPM.ys.map((v,j)=>j===0?0:(v+TPM.ys[j-1])/2).concat([1]);
    TPM.ys.forEach((y,j)=>TPM.xs.forEach((x,i)=>{ const x0=lx(xe[i]),x1=lx(xe[i+1]),y0=ly(ye[j+1]),y1=ly(ye[j]);
      g+='<rect x="'+x0.toFixed(1)+'" y="'+y0.toFixed(1)+'" width="'+(x1-x0+0.6).toFixed(1)+'" height="'+(y1-y0+0.6).toFixed(1)+'" fill="'+tpCol(G.z[j][i])+'"/>'; })); }
  else g+='<rect x="'+L+'" y="'+T+'" width="'+(R-L)+'" height="'+(B-T)+'" fill="#85B7EB" opacity="0.35"/>';
  g+='<rect x="'+L+'" y="'+T+'" width="'+(lx(fr)-L).toFixed(1)+'" height="'+(B-T)+'" fill="url(#hl)"/><rect x="'+L+'" y="'+T+'" width="'+(lx(fl)-L).toFixed(1)+'" height="'+(B-T)+'" fill="url(#hd)"/>';
  const lines={};
  if(G) TPM.levels.forEach(Lv=>{ const pts=tpContour(G.z,Lv); lines[Lv]=pts; if(pts.length<2) return;
    const s=pts.map(q=>lx(q[0]).toFixed(1)+","+ly(q[1]).toFixed(1)).join(" ");
    g+='<polyline points="'+s+'" fill="none" stroke="#fff" stroke-width="4" stroke-opacity="0.5"/><polyline points="'+s+'" fill="none" stroke="'+TPM.line+'" stroke-width="2"/>'; });
  g+='<line x1="'+L+'" x2="'+R+'" y1="'+ly(0.5)+'" y2="'+ly(0.5)+'" stroke="#fff" stroke-width="1.2" stroke-dasharray="5 4"/>';
  [fl,fr].forEach(v=>{ g+='<line x1="'+lx(v).toFixed(1)+'" x2="'+lx(v).toFixed(1)+'" y1="'+T+'" y2="'+B+'" stroke="#fff" stroke-width="1.5"/>'; });
  g+='<line x1="'+lx(par).toFixed(1)+'" x2="'+lx(par).toFixed(1)+'" y1="'+T+'" y2="'+B+'" stroke="#fff" stroke-width="1.5" stroke-dasharray="3 3"/>';
  // the cloud: one dot per draw at its cost; spread up and down a little only so that the dots can be seen
  const yp=ly(f.buyers), jit=small?9:12, cl=f.cloud;
  cl.cost.forEach((c,i)=>{ const u=((i*0.6180339887)%1)-0.5;
    g+='<circle class="cd" cx="'+lx(Math.min(TPM.x1,Math.max(TPM.x0,c))).toFixed(1)+'" cy="'+(yp+u*2*jit).toFixed(1)+'" r="'+(small?1.9:2.3)+'"/>'; });
  g+='</g>';
  // the reference points (small, fixed), then the reader's point
  const dots=[];
  TP.refs.forEach(r=>{ if(r.key===SCS.ref) return; const q=tpRefCloud(r.key).q; const x=lx(Math.min(TPM.x1,q[1])), y=ly(r.buyers);
    dots.push({x:x,y:y,lab:r.label,key:r.key}); g+='<circle class="rd" cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(small?3.4:4)+'"/>'; pl.block(x-5,y-5,x+5,y+5); });
  const px=lx(Math.min(TPM.x1,Math.max(TPM.x0,f.cost)));
  g+='<circle class="me" cx="'+px.toFixed(1)+'" cy="'+yp.toFixed(1)+'" r="'+(small?6:7)+'"/>'; pl.block(px-8,yp-8,px+8,yp+8);
  // labels, most important first
  const labs=[]; const fs=small?11:12;
  const meLab=f.key==="own"?"Your settings":(small?f.label.replace(", all favourable","").replace("Humbird's optimistic design","Humbird's design"):f.label);
  const meC=[]; [[-10,22],[-24,36],[-38,50]].forEach(([u,d])=>{ meC.push({x:px+11,y:yp+u,t:meLab,fs:fs+1,anchor:"start"},{x:px-11,y:yp+u,t:meLab,fs:fs+1,anchor:"end"},
    {x:px+11,y:yp+d,t:meLab,fs:fs+1,anchor:"start"},{x:px-11,y:yp+d,t:meLab,fs:fs+1,anchor:"end"},{x:px,y:yp+u,t:meLab,fs:fs+1,anchor:"middle"},{x:px,y:yp+d,t:meLab,fs:fs+1,anchor:"middle"}); });
  const me=pl.tryPut(meC,within)||pl.tryPut(meC.map(c=>Object.assign({},c,{fs:fs})),null)||meC[0];   // the reader's label always goes on
  if(me) labs.push(tpLabelSVG(me,"mb"));
  dots.forEach(d=>{ const t=small?d.lab.replace(", all favourable","").replace("Humbird's optimistic design","Humbird's design"):d.lab;
    const c=pl.tryPut([{x:d.x+8,y:d.y-7,t:t,fs:fs-1},{x:d.x-8,y:d.y-7,t:t,fs:fs-1,anchor:"end"},{x:d.x+8,y:d.y+15,t:t,fs:fs-1},{x:d.x-8,y:d.y+15,t:t,fs:fs-1,anchor:"end"},
                       {x:d.x+8,y:d.y-20,t:t,fs:fs-1},{x:d.x-8,y:d.y+28,t:t,fs:fs-1,anchor:"end"}],within);
    if(c) labs.push(tpLabelSVG(c)); });
  const zf=small?10:11;
  const zl=[[lx(fl)+zf+2,B-6,small?"floor: what cells eat":"$"+fl.toFixed(2)+" floor: what the cells must eat","start"],
            [lx(fr)+zf+2,T+6,small?"every lever at its limit":"$"+fr.toFixed(2)+": every lever at its limit","end"],
            [lx(par)-4,B-6,small?"same price as average kilo":"same price as the average kilo eaten here","start"]];
  zl.forEach(([x,y,t,a])=>{ const c=pl.tryPut([{x:x,y:y,t:t,fs:zf,anchor:a,rot:true}],[L,T,R,B]); if(c) labs.push(tpLabelSVG(c)); });
  if(G){ const ord=[1,10,0.1,30,0.01,50], fracs=[0.35,0.3,0.42,0.25,0.5,0.2,0.58,0.15,0.66,0.72,0.8];
    ord.forEach(Lv=>{ const pts=lines[Lv]; if(!pts||pts.length<2) return; if(small&&(Lv===0.01||Lv===50||Lv===30)) return;
      const t=(Lv<1?String(Lv):Lv)+"%", cands=[];
      (Lv>=30?[0.8,0.9,0.72,0.62]:fracs).forEach(fy=>{ const q=pts.reduce((a,b)=>Math.abs(b[1]-fy)<Math.abs(a[1]-fy)?b:a);
        cands.push({x:lx(q[0])+5,y:ly(q[1])+4,t:t,fs:fs}); cands.push({x:lx(q[0])-5,y:ly(q[1])+4,t:t,fs:fs,anchor:"end"}); });
      const c=pl.tryPut(cands,within); if(c) labs.push(tpLabelSVG(c)); }); }
  g+=labs.join("");
  // axes
  const xt=small?[2,5,10,20,50,100,400]:[2,5,10,20,50,100,200,400];
  xt.forEach(v=>{ g+='<line x1="'+lx(v).toFixed(1)+'" x2="'+lx(v).toFixed(1)+'" y1="'+B+'" y2="'+(B+5)+'" '+mut+'/><text x="'+lx(v).toFixed(1)+'" y="'+(B+18)+'" text-anchor="middle" font-size="11">$'+v+'</text>'; });
  g+='<text x="'+((L+R)/2)+'" y="'+(B+36)+'" text-anchor="middle" font-size="12">Cost to grow a kilo of cells (log scale)</text>';
  const mults=(small?[1,2,5,10,30]:[1,2,3,5,10,20,40]).filter(r=>{ const c=r*avg*(1-state.retail_margin)-state.markup_add; return c>TPM.x0&&c<TPM.x1; });
  mults.forEach(r=>{ const c=r*avg*(1-state.retail_margin)-state.markup_add, x=lx(c).toFixed(1);
    g+='<line x1="'+x+'" x2="'+x+'" y1="'+(T-5)+'" y2="'+T+'" '+mut+'/><text x="'+x+'" y="'+(T-9)+'" text-anchor="middle" font-size="11">'+r+'×</text>'; });
  g+='<text x="'+((L+R)/2)+'" y="'+(T-(small?28:30))+'" text-anchor="middle" font-size="'+(small?11:12)+'">'+(small?'Shop price against the average kilo eaten here':'Price in the shop, as a multiple of the average kilo eaten here ($'+avg.toFixed(2)+')')+'</text>';
  [0,0.25,0.5,0.75,1].forEach(v=>{ g+='<line x1="'+(L-5)+'" x2="'+L+'" y1="'+ly(v)+'" y2="'+ly(v)+'" '+mut+'/><text x="'+(L-8)+'" y="'+(ly(v)+4)+'" text-anchor="end" font-size="11">'+(v*100)+'%</text>'; });
  g+='<text x="'+(small?10:16)+'" y="'+((T+B)/2)+'" text-anchor="middle" font-size="'+(small?11:12)+'" transform="rotate(-90 '+(small?10:16)+' '+((T+B)/2)+')">'+(small?'Meat buyers picking it at equal price':'Meat buyers who would pick it at the same price')+'</text>';
  g+='<rect id="tphit" x="'+L+'" y="'+T+'" width="'+(R-L)+'" height="'+(B-T)+'" fill="transparent"/>';
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H);
  svg.innerHTML=g;
  TPGEO={W:W,L:L,R:R,T:T,B:B,lx:lx,ly:ly,f:f};
  tpMapWire(svg);
  tpMapText(f,G);
  if(!G) tpGridEnsure();
}
function tpZone(c){ const fl=C.FEEDSTOCK_FLOOR, fr=TP.frontier;
  return c<fl?"Impossible: below what the cells must eat ($"+fl.toFixed(2)+" a kilo, the nutrient floor).":
         (c<fr?"Beyond every known limit: below $"+fr.toFixed(2)+" a kilo needs some lever past what the evidence supports.":""); }
function tpReadAt(cx,cy){
  const z=tpInterp(cx,Math.max(TPM.ys[0],Math.min(TPM.ys[TPM.ys.length-1],cy))), shop=shelfPrice(cx,state);
  return "Cells at "+tpUSD(cx)+" a kilo (shop price "+tpUSD(shop)+", "+(shop/tpAvgPrice()).toFixed(1)+" times the average kilo eaten here), "+tpPctB(cy)+
    " of meat buyers picking it at the same price: long-run share about "+(z===null?"(still computing)":pgPctS(z))+" of "+pgRegionOf()+" meat and seafood. "+tpZone(cx);
}
function tpMapWire(svg){
  if(svg._wired||!svg.addEventListener) return; svg._wired=true;
  const read=document.getElementById("tp_hover");
  const move=e=>{ const G=TPGEO; if(!G||!read) return; const r=svg.getBoundingClientRect(), px=(e.clientX-r.left)*G.W/r.width, py=(e.clientY-r.top)*G.W/r.width;
    if(px<G.L||px>G.R||py<G.T||py>G.B){ tpHoverReset(); return; }
    const cx=Math.exp(Math.log(TPM.x0)+(px-G.L)/(G.R-G.L)*(Math.log(TPM.x1)-Math.log(TPM.x0))), cy=(G.B-py)/(G.B-G.T);
    read.textContent=tpReadAt(cx,cy); };
  svg.addEventListener("pointermove",move); svg.addEventListener("pointerdown",move); svg.addEventListener("pointerleave",tpHoverReset);
}
function tpHoverReset(){ const r=document.getElementById("tp_hover"); if(r&&TPGEO) r.textContent="Point at the map to read the share anywhere on it. Your point: "+tpReadAt(TPGEO.f.cost,TPGEO.f.buyers); }
function tpMapText(f,G){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const one=tpCostFor(1,f.buyers), ten=tpCostFor(10,f.buyers);
  set("tp_read_txt","<b>How to read the map.</b> Follow the orange 1% line. To its right, cultivated meat stays a niche. To cross it with "+tpPctB(f.buyers)+
    " of meat buyers picking it at the same price, cells must cost under about "+(one===null?"(out of reach)":tpUSDk(one))+" a kilo; for 10%, under about "+(ten===null?"$0.5: out of reach":tpUSDk(ten))+
    ". Your point sits at "+tpUSD(f.cost)+". Moving up the map is a judgement about shoppers; moving left is cheaper cells.");
  const rd=document.getElementById("tp_read"); if(rd) rd.style.display=PGS.readDismissed?"none":"";
  set("tp_map_region",pgRegionName());
  tpHoverReset();
  const tb=document.getElementById("tp_table");
  if(tb&&G){ const cs=[3,5,10,20,40,80,150,300], bs=[0.05,0.145,0.25,0.5,0.75,0.95];
    tb.innerHTML='<table class="num"><thead><tr><th>Cost of a kilo of cells</th>'+bs.map(b=>'<th>'+tpPctB(b)+' of meat buyers</th>').join("")+'</tr></thead><tbody>'+
      cs.map(c=>'<tr><td>$'+c+'</td>'+bs.map(b=>'<td>'+pgPctS(tpInterp(c,b))+'</td>').join("")+'</tr>').join("")+'</tbody></table>'+
      '<p class="note">Long-run share of '+pgRegionOf()+' meat and seafood, read from the map\'s grid, at the shopper settings as set.</p>'; }
  set("tp_alt","Upright lines: the nutrient floor ($"+C.FEEDSTOCK_FLOOR.toFixed(2)+" a kilo of cells: nothing can cost less), the cost at which the shop price matches the average kilo eaten here ("+
    scMoney(f.parity,2)+", dashed), and every lever at its limit ($"+TP.frontier.toFixed(2)+"). The map shades the long-run share of "+pgRegionOf()+" meat and seafood for every cost of cells (across) and every share of meat buyers who would pick it at the same price (up). "+
    "Your point: "+tpUSD(f.cost)+" and "+tpPctB(f.buyers)+", a share of "+pgPctS(f.share)+". Reference points: "+
    TP.refs.map(r=>r.label+" about "+tpUSD(tpRefCloud(r.key).q[1])).join("; ")+".");
}
function tpRenderFirst(){
  if(typeof document==="undefined") return;
  const f=pgFacts(), set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  set("deck",pgDeck(f));
  tpLineDraw(f); tpLineText(f); tpGroupsDraw(f); tpGroupsText(f); tpAnimalsRender(f);
  tpRenderControls(f); tpMapDraw(f);
}
const pgRenderFirst=tpRenderFirst;
function pgWidth(id,dflt){ const e=document.getElementById(id); const w=e&&e.clientWidth?e.clientWidth:0; return w>0?w:(dflt||720); }
function pgInterp(xs,ys,x){ if(x<=xs[0]) return ys[0]; for(let i=1;i<xs.length;i++){ if(x<=xs[i]){ const t=(x-xs[i-1])/(xs[i]-xs[i-1]); return ys[i-1]+t*(ys[i]-ys[i-1]); } } return ys[ys.length-1]; }

/* ---------- what it would take: the table scenarios.what_it_would_take generates ---------- */
function tpWitRender(){
  const host=document.getElementById("tp_wit"); if(!host) return;
  const mode=m=>m==="perfusion"?"perfusion":"fed-batch, 20 m³";
  host.innerHTML='<table class="sctab stack wit"><thead><tr><th>Long-run share of world meat and seafood</th><th>Meat buyers who pick it at the same price</th><th>Cells must cost</th>'+
    '<th>The least intrusive cells tried that get there</th><th>Their traits have been</th></tr></thead><tbody>'+
    TP.wit.map((r,i)=>{ const p=r.pick;
      return '<tr><td data-label="Share"><b>'+r.target+'%</b></td><td data-label="Meat buyers">'+tpPctB(r.buyers)+'</td><td data-label="Cells must cost">'+(r.need===null?"out of reach, even at $0.5":tpUSD(r.need)+" a kilo or less")+'</td>'+
        '<td data-label="Cells">'+(p?TRAIT_KEYS.map(k=>tpFmtTrait(k,p.traits[k])).join(", ")+'<br><span class="alt">'+tpUSD(p.cost)+' a kilo in '+TP.plant_names[p.plant].charAt(0).toLowerCase()+TP.plant_names[p.plant].slice(1)+', '+mode(p.mode)+'.</span> '+
          '<button type="button" class="lnk" onclick="tpTryWit('+i+')">Try these cells</button>':"none of the "+TP.n_wit_sets+" sets tried")+'</td>'+
        '<td data-label="Traits have been">'+(p?p.short:"")+'</td></tr>'; }).join("")+'</tbody></table>';
}
function tpTryWit(i){ const p=TP.wit[i].pick; if(!p) return;
  SCS.base="switches"; SCS.choice=Object.assign({},p.choice); SCS.traits=Object.assign({},p.traits); SCS.held={}; SCS.redesign=true;
  tpSetBuyers(TP.wit[i].buyers); tpTouched(); tpCommit();
  const t=document.getElementById("first"); if(t&&t.scrollIntoView) t.scrollIntoView({block:"start"}); }

/* ---------- Level 1: the reference points, and the steps from the published cells to every favourable setting ---------- */
function pgTag(t){ return '<span class="tag">'+t+'</span>'; }
function scTagChip(t){ return pgTag(SC.tag_plain[t]); }
// a rung of the ladder: its cloud, drawn exactly as the first screen draws a reference point's
const L1_C={};
function l1Cloud(k){ return L1_C[k]||(L1_C[k]=tpCloudFor({base:"switches",choice:SC.presets[k].choice,traits:{},held:{}})); }
function l1Render(){
  const host=document.getElementById("l1_refs"); if(!host) return;
  const f=pgFacts();
  host.innerHTML='<div class="refcards">'+TP.refs.map(r=>{ const q=tpRefCloud(r.key).q, sh=tpShare(q[1],r.buyers,"global"), on=SCS.ref===r.key;
    const rn=r.traits?tpRoutesNeeded(r.traits):null;
    return '<div class="refcard'+(on?' on':'')+'"><h4>'+r.label+(on?' <span class="tag">loaded</span>':'')+'</h4><p>'+pgEsc(r.text)+'</p>'+
      '<p class="small">'+(r.kind==="company"?'Its own figure: '+scMoney(r.cost)+' a kilo of cells. ':'About '+tpUSD(q[1])+' a kilo of cells (8 in 10 draws '+tpRangeUSD(q[0],q[2])+'). ')+
      'With '+tpPctB(r.buyers)+' of meat buyers picking it at the same price: '+pgPctS(sh)+' of world meat and seafood in the long run.'+
      (rn?' Cells: '+TRAIT_KEYS.map(k=>tpFmtTrait(k,r.traits[k])).join(", ")+'. Their traits have been '+rn.short+'.':'')+'</p>'+
      (r.kind==="company"?'':'<button type="button" class="btn small" onclick="tpLoad(\''+r.key+'\')">Load it</button>')+'</div>'; }).join("")+'</div>';
  const L=SC.order.filter(k=>SC.presets[k]&&PG.ladder.some(s=>s.key===k)).map(k=>{ const s=PG.ladder.find(x=>x.key===k), c=l1Cloud(k); return {key:k,name:s.name,tag:s.tag,cost:c.q,point:c.point}; });
  const max=Math.ceil(L[0].cost[2]*1.05/10)*10, pc=v=>(Math.min(v,max)/max*100).toFixed(2)+"%";
  const par=tpParity("global");
  let h='', rowsT='';
  L.forEach((s,i)=>{
    const prev=i?L[i-1].cost[1]:null, med=s.cost[1];
    const save=i?'Saves about '+tpUSD(prev-med)+'.':'The starting point.';
    h+='<div class="hb"><div class="hl"><b>'+(i+1)+'. '+s.name+'.</b> '+pgTag(s.tag)+'<br><span class="hv">About '+tpUSD(med)+' a kilo (8 in 10 draws: '+
       tpRangeUSD(s.cost[0],s.cost[2])+'). '+save+'</span></div><div class="ht">'+
       '<span class="vline" style="left:'+pc(par)+'"></span>'+
       (i?'<span class="bar save" style="left:'+pc(med)+';width:'+((prev-med)/max*100).toFixed(2)+'%"></span>':'')+
       '<span class="bar" style="left:0;width:'+pc(med)+'"></span>'+
       '<span class="wh" style="left:'+pc(s.cost[0])+';width:'+((s.cost[2]-s.cost[0])/max*100).toFixed(2)+'%"></span>'+
       '<span class="dotm" style="left:'+pc(med)+'"></span></div></div>';
    rowsT+='<tr><td>'+(i+1)+'. '+s.name+'</td><td>'+s.tag+'</td><td>'+tpUSD(med)+'</td><td>'+tpRangeUSD(s.cost[0],s.cost[2])+'</td><td>'+scMoney(s.point)+'</td><td>'+(i?tpUSD(prev-med):'')+'</td></tr>';
  });
  const ticks=[]; for(let v=0;v<=max;v+=(max>120?50:20)) ticks.push(v);
  h+='<div class="hb axis"><div class="hl"><span class="hv">Solid bar: cost after the step. Pale bar: what the step saves. Dot and thin line: the median and the range for 8 in 10 draws. '+
     'Dotted line: '+scMoney(par)+', where the shop price matches the average kilo of meat and seafood eaten in the world.</span></div><div class="ht">'+ticks.map(v=>'<span class="tk" style="left:'+pc(v)+'">$'+v+'</span>').join("")+'</div></div>';
  const ch=document.getElementById("l1chart"); if(ch) ch.innerHTML=h;
  const at=k=>L.find(s=>s.key===k).cost[1], first=L[0].cost[1], last=L[L.length-1].cost[1], eng=L.findIndex(s=>s.key==="engineered");
  const before=eng>0?L[eng-1].cost[1]:last;
  const alt=document.getElementById("l1alt");
  if(alt) alt.innerHTML="<b>What the chart shows.</b> The cost falls from about "+tpUSD(first)+" a kilo to about "+tpUSD(last)+". Of that fall, "+
    Math.round((first-before)/(first-last)*100)+"% comes before the cells' waste is cut to the engineered cells' level: "+tpUSD(first-at("process"))+" from the process and cheaper inputs, "+
    tpUSD(at("process")-at("selected"))+" from selected cells, "+tpUSD(at("selected")-at("central"))+" from perfusion and "+tpUSD(at("central")-before)+" from a cheaper plant. "+
    (last>par?"No step reaches ":"The last step passes ")+scMoney(par)+". The steps are reference points, not a forecast: each adds one kind of change.";
  const tb=document.getElementById("l1table");
  if(tb) tb.innerHTML='<table class="num"><thead><tr><th>Step</th><th>What it needs</th><th>Median cost, a kilo of cells</th><th>8 in 10 draws</th><th>Most-likely-values cost</th><th>Saved by the step</th></tr></thead><tbody>'+rowsT+'</tbody></table>';
}

/* ---------- Level 2: what would move it most ---------- */
function l2Fmt(e,v){ const x=v*(e.scale||1); const d=e.digits!=null?e.digits:(Math.abs(x)>=100?0:(Math.abs(x)>=10?1:2));
  return (e.pre||"")+(+x.toFixed(d)).toLocaleString("en-US")+(e.unit?(e.unit.charAt(0)==="%"?"":" ")+e.unit:""); }
// a share at another calibration K (a shopper setting moved), at the reader's meat buyers
function pgShareK(cost,K,over){ const sv=KP; KP=K;
  try{ return penetration(Object.assign({},state,over||{},{cost_override:cost,lmean:tpLmean(SCS.buyers)})).tv*100; } finally{ KP=sv; } }
const L0_Y=[0.003,80];
function l2Rows(){
  const ch=SCS.choice, p0=tpParams(), base=floorExplore(p0).total, b0=SCS.buyers, bsh=tpShare(base,b0), rows=[];
  // a setting whose column loop fails the page's two checks is said to fail them, so a saving that needs it is not read as free
  const loopFails=(k,v)=>{ const d=scEval(Object.assign({},ch,{[k]:v})).column; return !!(d&&(d.ph_vs_safe>1+1e-9||!d.passes_tested)); };
  const lab=(k,v)=>scSetting(k,v).label+(loopFails(k,v)?"; this fails the checks on the column's loop":"");
  if(SCS.base==="switches") scPriorities(ch,false).forEach(r=>{ if(r.switch==="cells"||r.switch==="growth") return;   // the traits stand for these two
    const sw=scSwitch(r.switch);
    rows.push({kind:"choice", id:"sw_"+r.switch, name:sw.name, what:sw.q+".", now:scSetting(r.switch,r.now).label,
      lo:r.costs[r.best], hi:r.costs[r.worst], loT:lab(r.switch,r.best), hiT:lab(r.switch,r.worst),
      why:scSetting(r.switch,r.now).note, tag:"a choice"}); });
  // the four traits, each from the published cells' level to the engineered cells' (a cell's weight over the range the cloud draws)
  const pub=tpRef("today").traits, eng=tpRef("best").traits, mq=TP.cloud.priors.sc_mass_selected_pg;
  TRAIT_KEYS.forEach(k=>{ const T=TP.traits[k], ends=k==="mass_pg"?[mq[0],mq[2]]:[pub[k],eng[k]];
    const c=ends.map(v=>floorExplore(Object.assign({},p0,{[k]:v})).total), lo=Math.min(c[0],c[1]), hi=Math.max(c[0],c[1]);
    const iLo=c[0]<=c[1]?0:1, rt=v=>TP.routes.route_text[String(tpTraitRoute(k,v)===null?"None":tpTraitRoute(k,v))];
    rows.push({kind:"trait", id:"tr_"+k, name:T.name, what:T.help, now:tpFmtTrait(k,tpTraitsShown()[k]), lo:lo, hi:hi,
      loT:tpFmtTrait(k,ends[iLo]), hiT:tpFmtTrait(k,ends[1-iLo]),
      why:T.help+" At "+tpFmtTrait(k,ends[iLo])+" it has been "+rt(ends[iLo])+"; at "+tpFmtTrait(k,ends[1-iLo])+", "+rt(ends[1-iLo])+".", tag:"a trait of the cells"}); });
  PG.estimates.forEach(e=>{ if(e.cells&&(SCS.base==="humbird"||e.cells.indexOf(ch.cells)<0)) return; if(e.arg==="nh3_kg") return;   // the ammonia is a trait row
    const a=floorExplore(Object.assign({},p0,{[e.arg]:e.lo})).total, b=floorExplore(Object.assign({},p0,{[e.arg]:e.hi})).total;
    const lo=Math.min(a,b), hi=Math.max(a,b);
    rows.push({kind:"estimate", id:"es_"+e.arg, name:e.name, what:"", now:null, lo:lo, hi:hi, loT:l2Fmt(e,a<=b?e.lo:e.hi), hiT:l2Fmt(e,a<=b?e.hi:e.lo),
      why:e.why, tag:"an estimate nobody has measured at scale"}); });
  rows.forEach(r=>{ r.shLo=tpShare(r.lo,b0); r.shHi=tpShare(r.hi,b0); });
  const cost=rows.filter(r=>r.hi-r.lo>=0.05).sort((x,y)=>(y.hi-y.lo)-(x.hi-x.lo)), none=rows.filter(r=>r.hi-r.lo<0.05);
  // the judgements about shoppers: they move the share, not the cost
  const rk=(SCS.from==="best")?"best":"central", dem=[];
  PG.judgements.forEach(j=>{ const rg=j.ranges[rk]; let a,b,f;
    if(j.key==="equal_price_share"){ const m=rg.map(tpBuyersOfDial); a=tpShare(base,m[0]); b=tpShare(base,m[1]);
      dem.push({kind:"judgement", id:"jd_"+j.key, name:"Meat buyers who would pick it at the same price, once familiar", lo:Math.min(a,b), hi:Math.max(a,b),
        loT:tpPctB(a<=b?m[0]:m[1]), hiT:tpPctB(a<=b?m[1]:m[0]), nowT:tpPctB(b0), why:j.why.replace("The range is the middle nine tenths of the draws for this case.","The range is the middle nine tenths of the model's draws, in meat buyers.")+" Set it under the map.", tag:"your assumption"}); return; }
    if(j.key==="cut_cells"){ a=pgShareK(base,KP,{cut_cells:rg[0]}); b=pgShareK(base,KP,{cut_cells:rg[1]}); }
    else { a=pgShareK(base,effConsts(Object.assign({},state,{[j.key]:rg[0]}))); b=pgShareK(base,effConsts(Object.assign({},state,{[j.key]:rg[1]}))); }
    f=v=>j.fmt==="pct"?Math.round(v*100)+"%":(+v.toFixed(1))+" times";
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
    "), not the median of the draws ("+tpUSD(f.cb[1])+"). Each row moves one thing across its range, with everything else as set."+(SCS.base==="humbird"?" Humbird's design is not built from the switches, so they are not ranked here.":"");
  const all=R.cost.concat(R.dem), s=all.find(r=>r.id===PGS.l2sel), card=document.getElementById("l2card");
  if(card){ card.style.display=s?"":"none";
    if(s) card.innerHTML='<p><b>'+s.name+'.</b> '+pgTag(s.tag)+'</p>'+
      (s.kind==="trait"?'<p>Now: '+s.now+'. '+s.why+'</p><p>At '+s.loT+': '+scMoney(s.lo)+' a kilo and a long-run share of '+pgPctS(s.shLo)+'. At '+s.hiT+': '+scMoney(s.hi)+' and '+pgPctS(s.shHi)+'. Set it under <a href="#tp_cells">Change the cells</a>.</p>'
       :s.kind==="choice"?'<p>'+s.what+' Now: '+s.now+'. '+s.why+'</p><p>Cheapest setting: '+s.loT+', '+scMoney(s.lo)+' a kilo and a long-run share of '+pgPctS(s.shLo)+
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
  const basis="the median cost of "+tpUSD(f.cost)+" a kilo, "+tpPctB(f.buyers)+" of meat buyers picking it at the same price, and the other shopper settings as set";
  set("l3_intro","Cultivated meat costs about the same whatever animal it copies, but conventional prices differ. So it competes where meat is dear and stays out where meat is cheap. "+
    "Everything in this level is at "+basis+". It adds up to "+pgPctS(total)+" of "+pgRegionOf()+" meat and seafood by weight ("+pgPctS(p.tval*100)+" by value).");
  set("l3asub",pgRegionName()+", "+pgCaseWords(f)+". A cut is "+Math.round(s.cut_cells*100)+"% cells bound with plant protein, so shoppers like it a little less than mince, and premium products less again.");
  const t3=rows.slice(0,3), dear=rows.filter(r=>/chicken|pork/i.test(r.name)&&!/organic|heritage/i.test(r.name));
  set("l3aalt","<b>What the chart shows.</b> The three types that add most to the total are "+t3.map(r=>r.name.toLowerCase()+" ("+pgPctS(r.sh)+" of the type)").join(", ")+
    ". "+(dear.length?"Ordinary chicken and pork stay at "+pgRange(Math.min.apply(null,dear.map(r=>r.R)),Math.max.apply(null,dear.map(r=>r.R)),v=>v.toFixed(1))+" times the conventional price.":""));
  set("l3atable",'<table class="num"><thead><tr><th>Type of meat</th><th>Kind</th><th>Conventional price, a kilo</th><th>Cultivated price, as a multiple</th><th>Share of the type</th><th>The type\'s share of all meat and seafood</th><th>Adds to the total</th></tr></thead><tbody>'+
    rows.map(r=>'<tr><td>'+r.name+'</td><td>'+r.kind+'</td><td>$'+r.price.toFixed(1)+'</td><td>'+r.R.toFixed(2)+'</td><td>'+pgPctS(r.sh)+'</td><td>'+r.w.toFixed(1)+'%</td><td>'+pgPctS(r.part)+'</td></tr>').join("")+'</tbody></table>');
  // regions: the same cloud of cost draws, at each region's own prices and incomes
  set("l3rsub","The median of the "+f.cloud.n+" cost draws, with the range that holds 8 in 10 of them, at "+tpPctB(f.buyers)+" of meat buyers picking it at the same price and the other shopper settings as set.");
  set("l3regions",'<table class="num"><thead><tr><th>Region</th><th>Average kilo of meat and seafood</th><th>Long-run share, median</th><th>8 in 10 draws</th></tr></thead><tbody>'+
    PG.regions.map(r=>{ const sh=[tpShare(f.cb[2],f.buyers,r[0]),tpShare(f.cb[1],f.buyers,r[0]),tpShare(f.cb[0],f.buyers,r[0])];
      return '<tr><td>'+r[1]+'</td><td>$'+tpAvgPrice(r[0]).toFixed(2)+'</td><td><b>'+pgPctS(sh[1])+'</b></td><td>'+(sh[2]<0.00095?"under 0.001%":pgPct(sh[0])+"% to "+pgPct(sh[2])+"%")+'</td></tr>'; }).join("")+'</tbody></table>');
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
  if(fs) fs.innerHTML='<option value="">Humbird\'s optimistic design</option>'+TP.refs.filter(r=>r.kind==="scenario").map(r=>'<option value="'+r.key+'">'+r.label+'</option>').join("");
}
function scResultHTML(ch,r){
  const f=pgFacts(), cost=r.total;
  const lim=(SC.limit_plain[r.limit]||r.limit).replace("CO2","CO₂");
  const med=(SC.medium_plain[r.medium_set_by]||r.medium_set_by);
  const need=scNeeds(ch).filter(x=>x[2]!=="nothing new");
  let h=(SCS.base==="humbird"?'<p class="callout">The page is on Humbird\'s optimistic design, which is not built from these switches. They show Selected cells\' switches; moving one starts your own settings from them.</p>':'')+
    '<p><b>'+f.label+': '+scMoney(cost)+' a kilo of cells with every estimate at its most likely value.</b> '+
    'The median of the draws is '+tpUSD(f.cb[1])+' (8 in 10 draws '+tpRangeUSD(f.cb[0],f.cb[2])+'), and that is the figure the rest of the page uses.'+
    (Object.keys(SCS.traits).length?' Your cell traits stand in for the kind of cells and the growth speed.':'')+'</p>'+
    '<p>The tank holds '+r.density.toFixed(0)+' g of cells a litre, limited by <b>'+lim+'</b>, and works '+(r.uptime*100).toFixed(0)+'% of the year. '+
    ((r.column&&r.limit==="oxygen supply")?'Oxygen, not CO₂, limits it because the column beside the tank takes the CO₂ out, and antifoam takes a quarter of the oxygen the bubbles deliver. Without the column, CO₂ would limit it first. ':'')+
    'Each kilo of cells needs '+r.medium_l.toFixed(0)+' litres of medium, set by <b>'+med+'</b>.</p>';
  if(need.length){ h+='<p class="scneed"><b>What has to go right:</b> '+need.map(x=>x[1]+' ('+SC.tag_plain[x[2]]+')').join(". ")+'.</p>'; }
  const d=r.column;
  if(d && (d.ph_vs_safe>1+1e-9 || !d.passes_tested))
    h+='<p><b>Warning.</b> This tank design pumps the culture through the column harder than the checks allow. It uses '+d.passes.toFixed(0)+
       ' passes an hour, and dense cultures have taken up to 15–24. The alkaline culture in the loop is '+d.ph_vs_safe.toFixed(1)+' times the exposure judged safe. '+
       'Treat the cost as too low, or use the button below to pick the cheapest design that passes.</p>';
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
  const ch=SCS.choice, r=SCS.base==="humbird"?floorExplore(tpParams()):scEval(ch), p=SCS.base==="humbird"?tpParams():scParams(ch);
  SC.keys.forEach(k=>{ const e=document.getElementById("sc_sel_"+k); if(e) e.value=ch[k];
    const n=document.getElementById("sc_note_"+k); if(n) n.innerHTML=scTagChip(scSetting(k,ch[k]).tag)+' '+scSetting(k,ch[k]).note; });
  host.innerHTML=scResultHTML(ch,r);
  const gfIn=(p.gf_in_medium||0)>0&&r.growth_factors<0.005;
  const ph=document.getElementById("sc_parts");      // where the cost goes, against Central (or the best case when Central is chosen)
  if(ph){ const refKey=SCS.ref==="central"?"best":"central"; ph.innerHTML=scPartsSVG(r,scWithExtra({},()=>scEval(SC.presets[refKey].choice)),tpLabel(refKey),gfIn); }
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
  tpBuildControls(); tpWitRender();
  KP=effConsts(state);
  if(SCS.buyers===null) tpSetBuyers(tpRef(SCS.from).buyers);
  state.equal_price_share=tpDial(SCS.buyers); tpRedesign(); tpExtraNow(); PGS.cloud=null;
  PG_LEVELS.forEach(([id,fn])=>{ const d=document.getElementById(id); if(!d||!d.addEventListener) return;
    d.addEventListener("toggle",()=>{ if(d.open){ fn(); PGS.dirty[id]=false; } }); });
  document.querySelectorAll('a[href^="#"]').forEach(a=>{ if(a.addEventListener) a.addEventListener("click",e=>{
    const id=(a.getAttribute("href")||"").slice(1); if(!id||!document.getElementById(id)) return;
    e.preventDefault(); pgGoto(id); if(typeof pgWriteHash==="function") pgWriteHash(); }); });
  if(typeof window!=="undefined"&&window.addEventListener){
    let rz=null; window.addEventListener("resize",()=>{ clearTimeout(rz); rz=setTimeout(()=>{ pgRenderFirst(); pgRenderLevels(); },120); });
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
