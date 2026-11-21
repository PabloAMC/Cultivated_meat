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
// vessel, vmode: the vessel type and the way it is run when they are not a stirred tank in perfusion or fed-batch (vessels.py);
// device: the device that holds the cells back in perfusion (retention.py; "tff" is the model's own membrane loop).
// hbKey: which of Humbird's reference points the base "humbird" is ("humbird_best": his best estimate, a fed-batch plant with
// clean rooms; "humbird": this model's perfusion variation on his cells). Each carries its explore arguments (`base`), the way
// the tank is run and the plant it starts with (`hb`) and its financing (`finance`).
const TP_START=MODEL.tp.start;                    // the page opens on Humbird's best estimate (2021), the best-known published analysis
const TP_CH0=MODEL.tp.start_choice;               // the switches' own starting choice (the published cells)
const TP_REF0=MODEL.tp.refs.find(r=>r.key===TP_START);
const SCS={choice:Object.assign({},TP_REF0.kind==="scenario"?TP_REF0.choice:SC.presets[TP_CH0].choice), preset:TP_CH0, src:"scenario", customCost:null,
  base:TP_REF0.kind==="humbird"?"humbird":"switches", hbKey:TP_REF0.kind==="humbird"?TP_START:"humbird", ref:TP_START, from:TP_START,
  redesign:TP_REF0.kind==="scenario"&&!!TP_REF0.redesign, traits:{}, held:{}, hb:Object.assign({mode:"perfusion",plant:"sterile"},TP_REF0.hb||{}), buyers:null,
  vessel:"stirred", vmode:null, device:"tff", clean:{route:"none",share:null,wash:null}};
// clean: cleaning and reusing the medium (floorExplore's clean, clean_share and wash_price; medium_reuse.py): the route, the share
// of the waste it handles that it takes out (null: the share that costs least), and the price of the litres that only wash waste
// out (null: the full price of the medium)
function tpCleanNone(){ return {route:"none",share:null,wash:null}; }
function tpCleanKw(st){ const c=(st&&st.clean)||{}, o={};
  if(c.route&&c.route!=="none"){ o.clean=c.route; if(c.share!==null&&c.share!==undefined) o.clean_share=c.share; }
  if(c.wash!==null&&c.wash!==undefined) o.wash_price=c.wash;
  return o; }
let TP_FXSIG="";                                  // the datasheet constants the reader has set (part of every cache key)
// what every scEval adds to a choice's explore arguments: the reader's traits and plant estimates (empty unless the reader set
// them, so the pure mirror of scenarios.run that tests/run_parity.py checks is unchanged)
let SC_EXTRA={};
function scWithExtra(x,fn){ const sv=SC_EXTRA; SC_EXTRA=x; try{ return fn(); } finally{ SC_EXTRA=sv; } }
const scCache={};
let scPair=null;                                   // the two switches shown against each other
function scSwitch(k){ return SC.switches.find(s=>s.key===k); }
function scSetting(k,v){ return scSwitch(k).settings.find(t=>t.key===v); }
function scSame(a,b){ return SC.keys.every(k=>a[k]===b[k])&&(a.extra||null)===(b.extra||null)&&(a.thin||null)===(b.thin||null); }
// the extra settings a choice names (mirror of scenarios.extra_kwargs): what the switches cannot say. `always` applies whatever
// the switches; a `when` entry applies only while its switch is at its setting, so moving the switch moves the lever with it
function scExtraKw(ch){ const e=ch.extra&&SC.extras?SC.extras[ch.extra]:null, o={}; if(!e) return o;
  Object.assign(o,e.always); e.when.forEach(w=>{ if(ch[w[0]]===w[1]) Object.assign(o,w[2]); }); return o; }
function scPresetOf(ch){ return SC.order.find(k=>scSame(SC.presets[k].choice,ch))||null; }
function scParams(ch){          // the explore arguments of a choice (mirror of scenarios.explore_kwargs)
  const p={doubling_h:24,mass_pg:3000,vessel_m3:20,plant:"sanitary",mode:"perfusion",charge:C.fx.charge_mature};
  SC.switches.forEach(sw=>Object.assign(p,scSetting(sw.key,ch[sw.key]).p));
  if(p.medium_complete && SC.medium_complete_on){ p.gf_in_medium=p.growth_factors||0; p.growth_factors=0; }  // a complete medium's price already pays for growth factors, and cannot cost less than nutrients + them (scenarios.explore_kwargs)
  delete p.medium_complete;
  Object.assign(p,SC.always);                 // what every scenario carries (scenarios.always: the dissolved-oxygen setpoint, the ammonia and lactate the cells tolerate)
  Object.assign(p,scExtraKw(ch));             // the case's own extra settings (scenarios.EXTRAS: the all-favourable example's)
  if(p.plantKey){ if(p.plantKey==="lean"){ p.plant="sanitary"; p.items=C.fx.plant_items.lean; }
    else p.plant=(p.plantKey==="sterile"?"sanitary":p.plantKey); delete p.plantKey; }
  // a fed-batch plant restarts each tank every few days, so the shared-medium plant keeps Humbird's full seed train (scenarios.explore_kwargs)
  if(p.vm&&p.vm.kind==="cyclic"&&p.items&&p.items.seed==="two") p.items=Object.assign({},p.items,{seed:"full"});
  if(ch.thin){ const vm=Object.assign({},p.vm||{}); vm.caps=Object.assign({},vm.caps||{},{[SC.loop_cap]:+ch.thin}); p.vm=vm; }   // a thinned design (scenarios.explore_kwargs)
  return Object.assign(p,SC_EXTRA);
}
function scEval(ch){
  const k=SC.keys.map(x=>ch[x]).join("|")+"|"+(ch.extra||"")+"|"+(ch.thin||"")+JSON.stringify(SC_EXTRA)+TP_FXSIG;
  if(!(k in scCache)) scCache[k]=floorExplore(scParams(ch));
  return scCache[k];
}
function scShare(cost,region){      // long-run share of meat sold by weight (%), at the current demand settings
  region=region||"global";
  const s=Object.assign({},state,{region:region,income:C.REGION_INCOME[region],cost_override:cost});
  return penetration(s).tv*100;
}
// the cheapest pair of tank settings (tricks, shape) whose loop a pH-safe pass rate dense cultures have taken allows; a pair whose
// loop fails at full density is tried with the culture held thinner (mirror of scenarios.design and thinned, 2026-11-21)
function scLoopOk(r){ const d=r.column; return !d||(d.ph_vs_safe<=1+1e-9&&d.passes_tested); }
function scThinned(c,xHi){ let lo=0, hi=xHi, ok=null;
  for(let i=0;i<SC.thin_steps;i++){ const mid=0.5*(lo+hi), r=scEval(Object.assign({},c,{thin:mid}));
    if(scLoopOk(r)){ lo=mid; ok=[mid,r]; } else hi=mid; }
  return ok; }
function scDesign(ch){
  let best=null; const base=Object.assign({},ch); delete base.thin;
  scSwitch("tricks").settings.forEach(a=>scSwitch("shape").settings.forEach(b=>{
    let c=Object.assign({},base,{tricks:a.key,shape:b.key}), r=scEval(c);
    if(!scLoopOk(r)){ const t=scThinned(c,r.density); if(t===null) return; c=Object.assign({},c,{thin:t[0]}); r=t[1]; }
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
   the page draws the cost of a kilo of cells as the median and 8-in-10 range of draws over the estimates nobody has measured
   (the draws are computed, not drawn as dots), places it on a contour map of the long-run share, and marks on each trait the
   best level measured in meat cells (no routes). Reference points load trait values; they are not forecasts. Nothing below
   changes the model's arithmetic: it calls the engine (floorExplore, penetration, shareCalc) and draws what comes back.
   tests/run_parity.py checks the draws against scenarios.py and the measurements against cell_traits.py.
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
// two significant figures, for a pair of shares read side by side (0.18% and 0.15%, not 0.2% and 0.1%)
const tpPct2=v=>(v<0.00095?"under 0.001":(v>=10?v.toFixed(0):String(+v.toPrecision(2))))+"%";
function pgRange(a,b,f){ return f(a)===f(b)?f(a):"between "+f(a)+" and "+f(b); }
// a cost in dollars rounded to the precision its range allows: whole dollars from $10 up, one decimal below
const tpUSD=v=>v>=9.95?pgUSD(v):"$"+v.toFixed(1);
function pgRegionName(r){ const x=PG.regions.find(q=>q[0]===(r||state.region)); return x?x[1]:r; }
function pgRegionOf(){ const n=pgRegionName(); return state.region==="global"?"the world's":(state.region==="us"?"the United States'":n+(/s$/.test(n)?"'":"'s")); }
function tpRef(k){ return TP.refs.find(r=>r.key===k)||null; }
// Humbird's reference point a state is based on, and a fresh state for one of them
function tpHb(st){ return tpRef(((st||SCS).hbKey)||"humbird"); }
function tpHbState(k){ return {base:"humbird",hbKey:k,hb:Object.assign({},tpRef(k).hb),traits:{},held:{},device:"tff"}; }
// the financing the levers start from: the starting point's own (Humbird's 7.5% over 10 years for his best estimate), else the
// model's mature-industry values
function tpFin(st){ st=st||SCS; return (st.base==="humbird"&&tpHb(st).finance)||TP.finance; }
function tpLabel(k){ const r=tpRef(k); return r?r.label:"Your settings"; }
const pgCaseLabel=tpLabel;
function pgAbout(v){ return String(Math.round(v*10)/10); }

/* ---------- what has been measured in meat cells (cell_traits.best_in_meat_cells): data only, no routes ---------- */
// Python's f"{v:g}" for the values a slider can take
function tpG(v){ return String(Number((+v).toPrecision(6))); }
// "Best measured in meat cells: 0.14 mol a kilo (Hubalek 2023, bovine fat-precursor cells fed without glutamine)"
function tpBestText(k){ const T=TP.traits[k];
  return T.best===null||T.best===undefined?"Not measured in meat cells.":"Best measured in meat cells: "+tpFmtTrait(k,T.best)+" ("+T.best_src+")."; }
// the traits of a set that go beyond the best measured in meat cells (mirror of cell_traits.beyond_measured)
function tpBeyond(tr){ return TRAIT_KEYS.filter(k=>{ const T=TP.traits[k], b=T.best; if(b===null||b===undefined||tr[k]===undefined) return false;
  return TP_DIR[k]<0?tr[k]<b-1e-12:tr[k]>b+1e-12; }); }
const TP_DIR={nh3_kg:-1,lac_yield:-1,doubling_h:-1,mass_pg:1};
const TP_TRAIT_WORD={nh3_kg:"ammonia",lac_yield:"lactate",doubling_h:"doubling time",mass_pg:"cell weight"};

/* ---------- the reader's explore arguments ---------- */
function tpResolvePlant(p){ if(p.plantKey){ if(p.plantKey==="lean"){ p.plant="sanitary"; p.items=C.fx.plant_items.lean; }
  else p.plant=(p.plantKey==="sterile"?"sanitary":p.plantKey); delete p.plantKey; } return p; }
// The reader's further settings (MODEL.tp.params, from build_interactive.PAGE_PARAMS). A "kw" setting is a floorExplore argument;
// an "fx" setting replaces a constant of the datasheet (C.fx) and an "fxx" one multiplies it, as inputs.py would if the input were
// changed there. Values are held in the slider's unit (the model's unit times `scale`).
const TP_PAR={}; TP.params.forEach(q=>{ TP_PAR[q.key]=q; });
const TP_FX0={};
function tpFxAt(path){ const ks=path.split("."); let o=C.fx; for(let i=0;i<ks.length-1;i++) o=o[ks[i]]; return [o,ks[ks.length-1]]; }
function tpFx0(path){ if(!(path in TP_FX0)){ const a=tpFxAt(path); TP_FX0[path]=a[0][a[1]]; } return TP_FX0[path]; }
// A starting point may start some levers at its own value, not the model's (MODEL.tp.refs[].levers, in the slider's unit: Humbird's
// best estimate starts the model's five additions at none). tpHeld: those values with whatever the reader has set on top; a
// lever the starting point sets is not drawn in the cloud either.
function tpRefLevers(st){ st=st||SCS; return st.base==="humbird"?(tpHb(st).levers||null):null; }
function tpHeld(st){ st=st||SCS; const L=tpRefLevers(st); return L?Object.assign({},L,st.held||{}):(st.held||{}); }
// tpApplyFx writes only what the reader has set into the datasheet's constants (C.fx); a starting point's own values of those
// constants go to the engine with the case itself (floorExplore's p.fxo, in tpParamsFor), so nothing else on the page sees them.
function tpApplyFx(st){ const h=(st||SCS).held||{}, sig=[];
  TP.params.forEach(q=>{ if(q.kind!=="fx"&&q.kind!=="fxx") return; const a=tpFxAt(q.arg), v0=tpFx0(q.arg), v=h[q.key];
    a[0][a[1]]=v===undefined?v0:(q.kind==="fxx"?v0*v:v/q.scale); if(v!==undefined) sig.push(q.key+"="+v); });
  TP_FXSIG=sig.length?"|fx:"+sig.join(";"):""; }
function tpHeldKw(h,st){ const o={}; h=h||{};
  if(h.capex_x!==undefined) o.capex_x=h.capex_x;
  if(h.medium_price!==undefined) o.medium_price=h.medium_price;
  if(h.mem_price!==undefined) o.membrane_price=h.mem_price;      // also as an argument, so it wins over a case that carries its own membrane (the all-favourable example)
  TP.params.forEach(q=>{ if(q.kind==="kw"&&h[q.key]!==undefined) o[q.arg]=h[q.key]/q.scale; });
  if(tpFinHeld(h)) o.charge=tpFinCharge(h,st);
  return o; }
// the yearly charge on the plant from its three parts: the payment that repays the plant with interest over its years (as a
// mortgage's), plus maintenance and insurance (MODEL.tp.finance: the model's own 5.4% over 20 years plus 9%)
function tpFinHeld(h){ return h.fin_rate!==undefined||h.fin_life!==undefined||h.fin_upkeep!==undefined; }
function tpFinCharge(h,st){ const F=tpFin(st), i=(h.fin_rate===undefined?F.rate:h.fin_rate)/100, n=h.fin_life===undefined?F.life:h.fin_life, u=(h.fin_upkeep===undefined?F.upkeep:h.fin_upkeep)/100;
  return (i>1e-9?i/(1-Math.pow(1+i,-n)):1/n)+u; }
// the value a setting has when the reader has not set it, in the slider's unit
function tpParamDefault(q,p){ const L=tpRefLevers(SCS); if(L&&L[q.key]!==undefined) return L[q.key];
  if(q.key==="mem_price"&&p.membrane_price!==undefined) return p.membrane_price;      // a case that carries its own membrane
  if(q.kind==="fin") return tpFin(SCS)[q.arg]; if(q.kind==="fxx") return 1; if(q.kind==="fx") return tpFx0(q.arg)*q.scale;
  const v=p[q.arg]; return (v!==undefined?v:tpFx0(q.dflt))*q.scale; }
// the vessel and the way it is run, when they are not the stirred tank's own perfusion or fed-batch (page_vessels.js)
function tpVesselKw(st,p){ const v=st.vessel||"stirred", m=st.vmode;
  if(!m||(v==="stirred"&&(m==="perfusion"||m==="fedbatch"))) return p;
  const size=v==="stirred"&&st.held&&st.held.tank_m3!==undefined?st.held.tank_m3:null;      // a stirred tank keeps the size the reader set
  const r=tpAtSize(size,()=>vmResolve(v,m,p)); return r?r.kw:p; }
// the vessel table prices a stirred tank at its own 20 m³; another size is the same calculation with the size put in
function tpAtSize(size,fn){ if(size===null||size===undefined) return fn(); const V=VM.vessels.stirred, sv=V.size; V.size=size; try{ return fn(); } finally{ V.size=sv; } }
const TP_SIZES=[50,100];            // the larger stirred tanks shown in the table of vessels (the lever goes to 250)
function tpPickVM(v,m,size){ if(size) SCS.held.tank_m3=size; else delete SCS.held.tank_m3; tpSetVM(v,m); }
// one case with the reader's retention device (page_retention.js); the membrane loop is floorExplore itself
function tpEval(st,p){ const d=st.device;
  if(d&&d!=="tff"&&typeof rtCost==="function"){ const vm=p.vm||{}, washed=vm.washed!==undefined?vm.washed:p.mode==="perfusion";
    if(washed&&!vm.own_retention){ const c=rtCost(d,p);
      if(c&&c.res) return Object.assign({},c.res,{device:d, device_running:c.device_running_kg||0, device_capital:c.device_capital_kg||0, device_loss:c.loss, device_impossible:c.impossible||"", device_beyond:!!c.beyond}); } }
  return floorExplore(p); }
// explore arguments for a state {base, choice, hb, traits, held}; without traits or held: the reference point itself
// The datasheet constants in force (C.fx) must be the state's own when this is called (tpApplyFx), as for tpEval.
function tpParamsFor(st){
  const extra=Object.assign({},st.traits||{},tpHeldKw(tpHeld(st),st),tpCleanKw(st));
  if(st.base==="humbird"){
    const R=tpHb(st), own=R.own||null, p=Object.assign({},R.base);
    if(st.hb.mode!=="perfusion") Object.assign(p,JSON.parse(JSON.stringify(scSetting("mode",st.hb.mode).p)));
    if(st.hb.plant!=="sterile") Object.assign(p,scSetting("plant",st.hb.plant).p);
    tpResolvePlant(p);
    if(p.vm&&p.vm.kind==="cyclic"&&p.items&&p.items.seed==="two") p.items=Object.assign({},p.items,{seed:"full"});
    if(own){                         // what is Humbird's own and has no lever (humbird_check.conditions)
      if(st.hb.plant===own.plant) Object.assign(p,own.plant_p);                                     // his plant's cost, while the plant is his
      if(tpHisWay(st,p)){ p.vm=Object.assign({},p.vm,own.vm); Object.assign(p,JSON.parse(JSON.stringify(own.kw))); } }   // his filter sets and his count of a batch, while the tank is run his way
    if(R.levers){ const fo={}, hd=st.held||{};      // the starting point's own value of a datasheet constant the reader has not set
      TP.params.forEach(x=>{ if((x.kind==="fx"||x.kind==="fxx")&&R.levers[x.key]!==undefined&&hd[x.key]===undefined) fo[x.arg]=x.kind==="fxx"?tpFx0(x.arg)*R.levers[x.key]:R.levers[x.key]/x.scale; });
      if(Object.keys(fo).length) p.fxo=Object.assign({},p.fxo||{},fo); }
    Object.assign(p,extra);
    const q=tpVesselKw(st,p);
    // his nutrients cost what he gives for a kilo of cells grown, whatever the litres: the price a litre follows from the litres
    // (two passes, as humbird_check.reproduce), unless the reader has set a price a litre
    if(own&&own.nutrients_kg!==undefined&&extra.medium_price===undefined){ const r0=floorExplore(Object.assign({},q,{medium_price:0}));
      q.medium_price=own.nutrients_kg/(r0.medium_l*r0.harvested_share); }
    return q;
  }
  return tpVesselKw(st,scWithExtra(extra,()=>scParams(st.choice)));
}
// is the tank run Humbird's way: a stirred tank in fed-batch (any size), not another vessel or mode from the vessel table
function tpHisWay(st,p){ return !!(p.vm&&p.vm.kind==="cyclic")&&(st.vessel||"stirred")==="stirred"&&!st.vmode; }
function tpParams(){ return tpParamsFor(SCS); }
function tpMode(){ return SCS.base==="humbird"?SCS.hb.mode:SCS.choice.mode; }
// the way the tank is run, in the vessel table's words (batch, fedbatch, filldraw, chemostat, perfusion)
function tpVMode(){ return SCS.vmode||(tpMode()==="perfusion"?"perfusion":"fedbatch"); }
function tpSparged(p){ const vm=p.vm||{}; return (vm.o2_gas!==false||vm.co2_gas!==false)&&!vm.no_protectant; }   // do the cells meet sparged gas?
function tpWashed(p){ const vm=p.vm||{}; return vm.washed!==undefined?vm.washed:p.mode==="perfusion"; }
function tpPlant(){ return SCS.base==="humbird"?SCS.hb.plant:SCS.choice.plant; }
// the four traits as the page shows them: the reader's where set, else the reference point's (or the switches')
function tpTraitsShown(){
  const base=SCS.base==="humbird"?tpHb(SCS).traits:(()=>{ const p=scWithExtra({},()=>scParams(SCS.choice)); const o={}; TRAIT_KEYS.forEach(k=>o[k]=p[k]); return o; })();
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
    o._kla=pd("tc_kla_exp"); o._thin=pd("tc_thin");      // a thick culture's oxygen uptake, drawn last (scenarios.MC_VISCOUS_INPUTS)
  }
  return o;
}
// the cost of one draw: the reader's arguments with the drawn estimates in place
function tpCloudCost(p,o,st){
  const q=Object.assign({},p), F=C.fx, sv=[F.protect_dose,F.tff.mem_price,F.aa,F.kla_exp,F.kla_thin];
  for(const k in o) if(k.charAt(0)!=="_") q[k]=o[k];
  if(o._dose!==undefined) F.protect_dose=o._dose;
  if(o._memprice!==undefined) F.tff.mem_price=o._memprice;
  if(o._aa!==undefined) F.aa=TP.cloud.aa_intensity*o._aa;
  if(o._kla!==undefined) F.kla_exp=o._kla;
  if(o._thin!==undefined) F.kla_thin=o._thin;
  try{ return tpEval(st||SCS,q).total; } finally{ F.protect_dose=sv[0]; F.tff.mem_price=sv[1]; F.aa=sv[2]; F.kla_exp=sv[3]; F.kla_thin=sv[4]; }
}
// which draws a state's own settings remove from the cloud: the traits and plant estimates the reader has set
function tpDrop(o,st){
  Object.keys(st.traits||{}).forEach(k=>{ delete o[k]; });
  const h=tpHeld(st);
  if(st.base==="humbird"&&tpHb(st).finance) delete o.charge;      // a starting point with its own financing keeps it
  if(h.capex_x!==undefined) delete o.capex_x;
  if(h.medium_price!==undefined) delete o.medium_price;
  TP.params.forEach(q=>{ if(h[q.key]!==undefined) q.drop.forEach(k=>{ delete o[k]; }); });
  return o;
}
// n draws for a state (the same seed for every state, so the cloud moves smoothly as a setting moves): the costs, sorted, and
// the 10th, 50th and 90th percentiles; `draws` lets a test pass in Python's draws
// the cost at the settings shown, every estimate at its value on the page (no draws): what the first screen reports
function tpPointFor(st){ tpApplyFx(st); try{ const r=tpEval(st,tpParamsFor(st)); return {point:r.total, res:r, q:[r.total,r.total,r.total], n:0, sorted:[r.total], light:true}; } finally{ tpApplyFx(SCS); } }
function tpCloudFor(st,n,draws){
  n=n||TP.cloud.n;
  tpApplyFx(st);                     // the datasheet constants this state sets (put back to the reader's own below)
  try{ return tpCloudFor_(st,n,draws); } finally{ tpApplyFx(SCS); }
}
function tpCloudFor_(st,n,draws){
  const p=tpParamsFor(st), isScen=st.base!=="humbird";
  const kw0=isScen?scWithExtra({},()=>scParams(st.choice)):(tpHb(st).own?tpParamsFor(Object.assign({},st,{traits:{},held:{}})):Object.assign({},tpHb(st).base));
  const cells=isScen?st.choice.cells:null, lean=isScen&&st.choice.plant==="lean";
  // what the case's extra settings fix is held, not drawn (scenarios.scenario_mc); the draws are still made
  const fixed=isScen?Object.keys(scExtraKw(st.choice)):[], hold=o=>{ fixed.forEach(k=>{ delete o[k]; }); return o; };
  if(!draws){ _seedRng(TP.cloud.seed); draws=[]; for(let i=0;i<n;i++) draws.push(tpDrop(hold(tpCloudDraw(isScen,kw0,cells,lean)),st)); }
  else draws=draws.map(o=>tpDrop(hold(Object.assign({},o)),st));
  const cost=draws.map(o=>tpCloudCost(p,o,st)), srt=cost.slice().sort((a,b)=>a-b), r0=tpEval(st,p);
  return {cost:cost, sorted:srt, q:[pctl(srt,10),pctl(srt,50),pctl(srt,90)], point:r0.total, res:r0, n:draws.length};
}
const TP_REFP={};
function tpRefPoint(k){ if(!(k in TP_REFP)){ const r=tpRef(k);
  TP_REFP[k]=r.kind==="company"?r.cost:tpPointFor(r.kind==="humbird"?tpHbState(k):{base:"switches",choice:r.choice,traits:{},held:{},device:"tff"}).point; }
  return TP_REFP[k]; }
const TP_REFC={};
function tpRefCloud(k){            // a reference point's own cloud (its traits drawn as scenario_mc draws them)
  if(!TP_REFC[k]){ const r=tpRef(k);
    if(r.kind==="company") TP_REFC[k]={q:[r.cost,r.cost,r.cost], point:r.cost, sorted:[r.cost]};
    else TP_REFC[k]=tpCloudFor(r.kind==="humbird"?tpHbState(k)
                                              :{base:"switches",choice:r.choice,traits:{},held:{},device:"tff"}); }
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
  const M=TP_CF.get(KP), key=target+"|"+b.toFixed(6)+"|"+(region||state.region)+"|"+state.income+"|"+state.markup_add+"|"+state.retail_margin+"|"+state.cut_cells+"|"+state.mk_supply+"|"+state.closed_level+"|"+state.closed_custom;
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
  const cl=PGS.cloud||(PGS.cloud=tpPointFor(SCS)), b=SCS.buyers, q=cl.q, cost=cl.point;
  const retail=shelfPrice(cost,state), conv=C.p_conv_anchor*state.meat_tax;
  const sh=[tpShare(q[2],b),tpShare(q[1],b),tpShare(q[0],b)];
  const one=tpCostFor(1,b), ten=tpCostFor(10,b);
  return {key:SCS.ref||"own", label:tpWho(), region:state.region, cost:cost, cb:q, point:cl.point, retail:retail, conv:conv, mult:retail/conv,
          avg:tpAvgPrice(), share:sh[1], sb:sh, pb:pgPlantBased(), parity:tpParity(), buyers:b, eqs:state.equal_price_share, cloud:cl,
          one:one, ten:ten, groups:tpCostGroups(cl.res||floorExplore(tpParams())), animals:tpByAnimal(cost,b)};
}
function pgPointCost(){ return (PGS.cloud||(PGS.cloud=tpPointFor(SCS))).point; }
function pgHeadCost(){ return pgPointCost(); }
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
  // a route that cleans the medium (floorExplore's clean): its equipment's yearly charge (inside r.capital) and its running cost
  // (inside r.consumables; the part that is cell-filter membranes for the litres it cleans is inside r.membranes) get their own lines
  const ccap=r.clean_capital||0, crun=r.clean_opex||0, cfm=r.clean_filter_membranes||0;
  const groups=[
    {key:"litres", name:"Scales with the litres of medium", what:"the litres of medium the cells need", note:ml.toFixed(0)+" litres a kilo of cells", items:[
      {key:"membranes", name:r.device?"The retention device's running cost ("+MODEL.rt.devices[r.device].name.toLowerCase()+")":"Filter membranes", note:perL(r.membranes-cfm+(r.device_running||0)), v:r.membranes-cfm+(r.device_running||0)},
      {key:"medium", name:"The medium itself", note:perL(r.feedstock), v:r.feedstock},
      {key:"protectant", name:"Bubble protectant", note:perL(r.protectant), v:r.protectant},
      {key:"gf", name:"Growth factors bought on top", note:perL(r.growth_factors), v:r.growth_factors},
      {key:"clean_cap", name:"Cleaning the medium: its equipment", note:"", v:ccap},
      {key:"clean_run", name:"Cleaning the medium: running it", note:r.clean_loop>0?" ("+r.clean_loop.toFixed(0)+" litres a kilo cleaned and returned)":"", v:crun}]},
    {key:"time", name:"Scales with time in the tank", what:"the time the cells spend in the tank", note:"the plant and its staff, paid by the year and shared over what a tank makes", items:[
      {key:"capital", name:"The plant: paying it back with interest, maintenance and insurance", note:"", v:r.capital-ccap},
      {key:"labour", name:"Labour", note:"", v:r.labour}]},
    {key:"other", name:"Everything else", what:"neither", note:"", items:[
      {key:"energy", name:"Energy and gas", note:"", v:r.utilities+(r.extra_opex||0)-(r.device_running||0)},
      {key:"supplies", name:"Other supplies", note:"", v:r.consumables-r.membranes-r.protectant-(crun-cfm)}]}];
  groups.forEach(g=>{ g.items=g.items.filter(i=>(i.key!=="gf"&&i.key!=="membranes"&&i.key!=="protectant"&&i.key!=="clean_cap"&&i.key!=="clean_run")||i.v>0); g.v=g.items.reduce((a,i)=>a+i.v,0); });
  const sum=groups.reduce((a,g)=>a+g.v,0);
  return {groups:groups, total:r.total, sum:sum, ml:ml};
}

/* ---------- where it would sell: the engine's per-type roll-up (penetration) gathered by animal (animalOf) ---------- */
const TP_ANIMALS={"Beef":"beef","Sheep/goat":"sheep and goat","Seafood":"seafood","Pork":"pork","Chicken":"chicken"};
const TP_OTHER={"Duck":"duck and goose","Rabbit":"rabbit","Turkey":"turkey"};
function tpByAnimal(cost,b,region){
  region=region||state.region;
  const s=Object.assign({},state,{region:region,income:region===state.region?state.income:C.REGION_INCOME[region],cost_override:cost,lmean:tpLmean(b)});
  const p=penetration(s); let W=0, cells=0; p.rows.forEach(r=>{ W+=r.mt.w_vol; });
  // by weight of cells: a steak or fillet is s.cut_cells cells, the rest plant protein; mince is all cells
  p.rows.forEach(r=>{ cells+=r.mt.w_vol/W*r.sh*(r.mt.structured?s.cut_cells:1); });
  const by={};
  p.rows.forEach(r=>{ const a=animalOf(r.mt.name), k=(a in TP_ANIMALS)?a:"Other";
    const o=by[k]||(by[k]={key:k,w:0,x:0,pv:0,members:[]});
    o.w+=r.mt.w_vol/W; o.x+=r.mt.w_vol/W*r.sh; o.pv+=r.mt.w_vol/W*r.mt.p_conv;
    if(k==="Other"){ const n=TP_OTHER[a]||a.toLowerCase(); if(o.members.indexOf(n)<0) o.members.push(n); } });
  const rows=Object.keys(by).map(k=>{ const o=by[k];
    return Object.assign(o,{name:k==="Other"?"Other: "+o.members.join(", "):tpCap(TP_ANIMALS[k]), word:k==="Other"?"other meats":TP_ANIMALS[k],
      price:o.pv/o.w, within:o.x/o.w*100, part:p.tv>0?o.x/p.tv:0}); });
  rows.sort((a,c)=>((a.key==="Other")-(c.key==="Other"))||(c.price-a.price));
  const types=p.rows.map(r=>({name:r.mt.name, animal:animalOf(r.mt.name), tier:r.t, sh:r.sh, shp:r.shp, R:r.R, w:r.mt.w_vol/W, price:r.mt.p_conv, structured:!!r.mt.structured}));
  return {rows:rows, types:types, total:p.tv*100, cells:cells*100, value:p.tval*100, pbv:p.tvp*100, pbval:p.tvalp*100, avg:tpAvgPrice(region), cut:s.cut_cells};
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

/* ---------- the page's opening: only the best the model can find, as a range (the author, 2026-11-19: "I would not lead with any
   number except perhaps the best we can possibly do (if only a range)"; published cells are not the state of the art, because
   companies do not publish theirs) ---------- */
function pgLead(){
  const fl=C.FEEDSTOCK_FLOOR, fr=TP.frontier, ms=tpMeats(), a=ms[0], b=ms.find(m=>/steak/i.test(m.name))||ms[ms.length-1], d=v=>"$"+Math.round(v);
  return "<p>Cultivated meat is animal meat grown from cells in tanks. This page works out what a kilo would cost and how much conventional meat it could replace. "+
    "You set what the cells do, how the tank is run, what the medium costs and how shoppers feel.</p>"+
    "<p>Two costs frame the answer. The amino acids, sugar and salts that a kilo of cells is grown from cost about "+d(fl)+" at feed-grade prices, so cells grown this way cannot cost less. (A chicken is cheaper to feed: it builds its meat from soy and grain, not from purified amino acids.) With every part of the process at the best level known (the all-favourable example), the model gives about "+d(fr)+
    " a kilo, which is "+d(shelfPrice(fl,state))+" to "+d(shelfPrice(fr,state))+" in the shop as mince. "+tpCap(a.plain)+" sells for "+d(a.price)+" a kilo "+tpEatenWhere()+" and "+b.plain+" for "+d(b.price)+".</p>"+
    "<p>The levers start at the best estimate of Humbird's 2021 analysis, the best-known published one, which this page reproduces to within about 2%. No meat cell has been shown to match its cells: “Published cells” loads the best values published for meat cells instead. Companies say their own cells do better and have not published them, so move the levers to what you think can be done.</p>";
}

/* ---------- the live sentence ---------- */
function pgDeck(f){
  const who=f.key==="own"?"With your settings":"With "+f.label, c=f.cost;
  let one;
  if(f.one===null) one="even free cells would not reach 1% of "+tpRegionMeat()+" with these shoppers";
  else if(c>=1.1*f.one) one=tpTimes(c/f.one)+" what it would need to reach 1% of "+tpRegionMeat()+" ("+tpUSDk(f.one)+")";
  else if(c>0.9*f.one) one="about what 1% of "+tpRegionMeat()+" needs ("+tpUSDk(f.one)+")";
  else one="below the "+tpUSDk(f.one)+" that 1% of "+tpRegionMeat()+" needs"+(f.ten!==null&&c<0.9*f.ten?", and below even the "+tpUSDk(f.ten)+" that 10% needs":"");
  const ms=tpMeats(), m0=ms[0], m1=ms[ms.length-1], rr=m=>m.shop(c)/m.price;
  const cmp=m=>(rr(m)>=1.1?tpX(rr(m))+" the price of ":(rr(m)>0.9?"about the price of ":"cheaper than "))+m.plain+" ($"+m.price.toFixed(2)+" a kilo "+tpEatenWhere()+")";
  const par="in the shop it would cost "+cmp(m0)+" and "+cmp(m1);
  const G=f.groups, big=G.groups.reduce((a,g)=>g.v>a.v?g:a);
  const drv=big.key==="other"?"Most of the cost is energy, gas and other supplies.":
    tpCap(tpFrac(big.v/G.total))+" of the cost scales with "+big.what+(big.key==="litres"?" ("+G.ml.toFixed(0)+" litres a kilo)":"")+".";
  const A=f.animals, sl=tpSellers(A);
  const sh=f.sb[2]<0.00095?"under 0.001% of "+tpRegionMeat():"about "+tpPct2(A.total)+" of "+tpRegionMeat()+" by weight of product ("+tpPct2(A.cells)+" by weight of cells)";
  const sold=sl.part>=0.45?", sold mostly as "+tpAnd(sl.top.map(r=>r.word))+(sl.dear?", where meat is dear":""):", spread across many kinds of meat";
  return who+", a kilo of cells costs about "+tpUSD(c)+" to grow: "+one+"; "+par+". "+drv+
    " If "+tpPctB(f.buyers)+" of meat buyers would pick it at the same price, it would take "+sh+" in the long run"+sold+". "+tpCutWords(A.cut)+".";
}
// how a steak or fillet is made up, in the sentence's words
function tpCutWords(c){ const p=Math.round((1-c)*100);
  return p<1?"Steaks and fillets are all cells":"Steaks and fillets are "+p+"% plant protein and "+(100-p)+"% cells, mince all cells"; }

// the estimates the draws vary for the current state (what the reader has set leaves the list), in plain words
function tpVaried(st){
  st=st||SCS; const isScen=st.base!=="humbird", h=tpHeld(st), tr=st.traits||{}, out=[];
  const p=tpParamsFor(st), perf=(p.mode||"perfusion")==="perfusion"&&!(p.vm&&p.vm.kind==="cyclic");
  if(h.capex_x===undefined) out.push("what the plant costs to build");
  if(!tpFinHeld(h)&&!(st.base==="humbird"&&tpHb(st).finance)) out.push("the yearly charge on the plant");
  if(h.medium_price===undefined) out.push("the price of the medium");
  if(isScen&&(p.hazard||0)>0) out.push("how often runs are lost");
  const memb=perf&&(st.device||"tff")==="tff"&&!(p.vm&&p.vm.own_retention);
  if(memb&&h.mem_life===undefined) out.push("how long the filter membranes last");
  if(memb&&h.mem_price===undefined&&TP.cloud.wide) out.push("what the filter membranes cost");
  if(h.maint===undefined) out.push("the share of a cell's oxygen spent on upkeep");
  if(TP.cloud.wide){
    if(h.nh3_limit===undefined) out.push("the ammonia the cells tolerate");
    if(h.lac_limit===undefined) out.push("the lactate the cells tolerate");
    if(h.killx===undefined&&tpSparged(p)) out.push("how many cells bursting bubbles kill");
    if(h.protect_dose===undefined||h.protect_price===undefined) out.push("the price and dose of the bubble protectant");
    if(h.min_perfusion===undefined) out.push("the least medium flow the cells need");
    if(p.antifoam_otr===undefined) out.push("what antifoam costs the oxygen transfer");
    if(h.aa_price===undefined) out.push("the price of amino acids");
    if(isScen&&tr.mass_pg===undefined) out.push("the weight of a cell");
    if(isScen&&tr.nh3_kg===undefined&&(st.choice.cells==="selected"||st.choice.cells==="measured")) out.push("the ammonia the cells make");
  }
  return out;
}
function tpVariedTip(st){ return "The 8 in 10 range: the draws vary "+tpAnd(tpVaried(st))+". Whatever you set yourself leaves the list."; }

// published costs shown for comparison on the cost axis only (they are costs, not shares): the published cells as this model prices
// them, Humbird's 2021 design as this model prices it, and one company's own report
// The kinds of meat a cost is compared with, by name (the author, 2026-11-19: "different meats have different prices"): the cheapest
// large kind, the one most eaten, a steak and the dearest, each with its shop price and the cost of cells at which the cultivated
// product would sell at that price (its shop price is linear in the cost of cells, so two evaluations give it).
// a kind of meat in two or three plain words: "chicken mince", "beef steak", "pork cuts", "sushi-grade fish"
function tpMeatShort(name){
  const m=name.match(/^([^(]+?)\s*\((.*)\)$/); if(!m) return name.toLowerCase().replace("/"," and ");
  const a=m[1].toLowerCase().replace("duck/goose","duck").replace("sheep/goat","lamb"), k=m[2].toLowerCase(), fish=a==="seafood";
  if(/sushi/.test(k)) return "sushi-grade fish"; if(/premium fillet/.test(k)) return "premium fish fillet"; if(/whole fish/.test(k)) return "ordinary fish";
  if(/mince\/canned/.test(k)) return "canned or minced fish";
  if(/ground|proc\./.test(k)) return a+" mince"; if(/^processed$/.test(k)) return "processed "+a; if(/steak/.test(k)) return a+" steak";
  if(/wagyu|prime/.test(k)) return "prime "+a; if(/organic|heritage/.test(k)) return k.split(",")[0]+" "+a; if(/^cuts$|breast/.test(k)) return a+" cuts"; if(/whole/.test(k)) return "whole "+a;
  return fish?"fish":a; }
function tpMeats(region){
  const key=(region||state.region)+"|"+state.markup_add+"|"+state.retail_margin+"|"+state.cut_cells+"|"+state.scaffold;
  if(PGS.meatsKey===key) return PGS.meats;
  const at=c=>tpByAnimal(c,0.5,region).types, a=at(10), b=at(20);
  const all=a.map((t,i)=>{ const sl=(b[i].R-t.R)/10, c0=10+(1-t.R)/sl; return {name:t.name, plain:tpMeatShort(t.name), price:t.price, w:t.w, structured:t.structured, parity:c0, shop:c=>(t.R+sl*(c-10))*t.price}; });
  const big=all.filter(t=>t.w>0.02), pick=[];
  const add=t=>{ if(t&&pick.indexOf(t)<0) pick.push(t); };
  add(big.slice().sort((x,y)=>x.price-y.price)[0]); { const an=animalOf(pick[0].name), rest=all.filter(t=>animalOf(t.name)!==an&&!/steak/i.test(t.name)); if(rest.length) add(rest.reduce((x,y)=>y.w>x.w?y:x)); }   // the most eaten kind of another animal
  add(all.filter(t=>/steak/i.test(t.name))[0]); add(all.filter(t=>t.w>0.003).sort((x,y)=>y.price-x.price)[0]);
  PGS.meatsKey=key; return PGS.meats=pick.sort((x,y)=>x.price-y.price);
}
const tpX=r=>(r>=9.5?r.toFixed(0):r.toFixed(1))+" times";
const TP_PUBS=["today","humbird_best","company"];
const TP_PUBL={today:"Published cells",humbird_best:"Humbird's best estimate",company:"A company's report"};
// what cultivated mince at `cost` a kilo of cells costs against the cheapest and the dearest large kinds of meat, in words
function tpMultAt(cost,which){ const A=tpByAnimal(cost,SCS.buyers), ts=A.types.filter(t=>!t.structured&&t.w>0.02).sort((a,b)=>a.price-b.price);
  const t=which==="cheap"?ts[0]:A.types.slice().sort((a,b)=>b.price-a.price).find(x=>x.w>0.005), r=shelfPrice(cost,state)/t.price;
  return r.toFixed(1)+" times the price of "+l3Name(t.name).toLowerCase(); }

/* ---------- the shoppers' result for one kind of meat: the share of its buyers who pick the cultivated one, by price ---------- */
// At the same price the share IS the reader's setting (that is its definition), so the curve passes through (1x, setting). Each kind
// of meat sits at its own multiple for one cost of cells, which is why the world total differs from the setting.
function tpOneDraw(f){
  const svg=document.getElementById("tp_one"); if(!svg||!KP) return;
  const W=Math.max(300,pgWidth("tp_one_plot",860)), small=W<560, H=small?290:310, L=small?44:56, R=W-14, T=62, B=H-52, fs=small?11:12;
  const lm=tpLmean(f.buyers), at=r=>shareCalc(r,KP,{ax:state.accept_x,tfM:state.theta_free_M,income:C.income_ref,nbx:state.neophobia_x,hx:state.health_x,lmean:lm,which:"x_meat"})*100;
  const types=f.animals.types.filter(t=>t.w>0.004), rmax=Math.max(8,Math.min(200,Math.max.apply(null,types.map(t=>t.R))*1.3)), x0=0.25, x1=rmax;
  const X=r=>L+(Math.log(Math.max(x0,Math.min(x1,r)))-Math.log(x0))/(Math.log(x1)-Math.log(x0))*(R-L), Y=v=>B-v/100*(B-T);
  let g='';
  [0,25,50,75,100].forEach(v=>{ g+='<line x1="'+L+'" x2="'+R+'" y1="'+Y(v)+'" y2="'+Y(v)+'" stroke="var(--grid)"/><text x="'+(L-6)+'" y="'+(Y(v)+4)+'" text-anchor="end" font-size="'+fs+'" class="m">'+v+'%</text>'; });
  [0.25,0.5,1,2,5,10,20,50,100].filter(r=>r>=x0&&r<=x1).forEach(r=>{ g+='<line x1="'+X(r).toFixed(1)+'" x2="'+X(r).toFixed(1)+'" y1="'+B+'" y2="'+(B+4)+'" class="ax"/><text x="'+X(r).toFixed(1)+'" y="'+(B+fs+6)+'" text-anchor="middle" font-size="'+fs+'" class="m">'+(r<1?(small?r+"×":(r===0.5?"half the price":"a quarter")):(r===1&&!small?"the same price":r+"×"))+'</text>'; });
  g+='<text x="'+((L+R)/2)+'" y="'+(B+2*fs+14)+'" text-anchor="middle" font-size="'+fs+'" class="m">'+(small?"Shop price against the meat beside it":"Price in the shop, against the conventional meat beside it (log scale)")+'</text>';
  const pts=[]; for(let i=0;i<=80;i++){ const r=x0*Math.pow(x1/x0,i/80); pts.push(X(r).toFixed(1)+","+Y(at(r)).toFixed(1)); }
  g+='<polyline points="'+pts.join(" ")+'" fill="none" stroke="#378ADD" stroke-width="2.5"/>';
  const b=f.buyers*100;
  g+='<line x1="'+X(1).toFixed(1)+'" x2="'+X(1).toFixed(1)+'" y1="'+T+'" y2="'+B+'" stroke="var(--ink2)" stroke-dasharray="4 3"/>'+
     '<line x1="'+L+'" x2="'+X(1).toFixed(1)+'" y1="'+Y(b).toFixed(1)+'" y2="'+Y(b).toFixed(1)+'" stroke="var(--ink2)" stroke-dasharray="4 3"/>'+
     '<circle cx="'+X(1).toFixed(1)+'" cy="'+Y(b).toFixed(1)+'" r="6" fill="var(--card)" stroke="var(--ink)" stroke-width="3"/>'+
     '<text x="'+(X(1)+10).toFixed(1)+'" y="'+(Y(b)-9).toFixed(1)+'" font-size="'+fs+'" class="b">same price: '+tpPctB(f.buyers)+' (your setting)</text>';
  // where each kind of meat sits at your cost of cells: a mark on the axis, three of them named
  const srt=types.slice().sort((a,c)=>a.R-c.R), big=types.reduce((a,c)=>c.w>a.w?c:a), named=[srt[0],big,srt[srt.length-1]].filter((t,i,a)=>a.indexOf(t)===i);
  types.forEach(t=>{ const x=X(t.R), over=t.R>x1; g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+(B-10)+'" y2="'+B+'" stroke="#D85A30" stroke-width="'+(1+Math.min(4,t.w*20)).toFixed(1)+'" opacity="'+(over?0.35:0.85)+'"><title>'+pgEsc(l3Name(t.name)+": "+t.R.toFixed(1)+" times the price of the conventional one; "+pgPctS(t.sh*100)+" of it would be cultivated")+'</title></line>'; });
  let ly=fs+2; named.forEach(t=>{ const x=X(t.R), end=x>(L+R)/2; g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+(ly+3)+'" y2="'+(B-10)+'" stroke="#D85A30" stroke-width="1" opacity="0.6"/>'+
    '<text x="'+(x+(end?-5:5)).toFixed(1)+'" y="'+ly+'" text-anchor="'+(end?"end":"start")+'" font-size="'+fs+'" fill="#D85A30">'+pgEsc(l3Name(t.name)+(t.R>x1?" (off the scale)":"")+": "+(t.R>=10?t.R.toFixed(0):t.R.toFixed(1))+"×")+'</text>'; ly+=fs+5; });
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H); svg.innerHTML=g;
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const txt="At the same price as the conventional meat beside it, "+tpPctB(f.buyers)+" of that meat's buyers pick the cultivated one: that is what your setting means, so the curve passes through it. "+
    "At twice the price, "+at(2).toFixed(at(2)<10?1:0)+"%; at five times, "+at(5).toFixed(at(5)<10?1:0)+"%; at half the price, "+at(0.5).toFixed(0)+"%. "+
    "The orange marks show where each kind of meat sits with cells at "+tpUSD(f.cost)+" a kilo (thicker marks: more of the meat eaten): from "+l3Name(srt[0].name).toLowerCase()+" at "+srt[0].R.toFixed(1)+
    " times its conventional price to "+l3Name(srt[srt.length-1].name).toLowerCase()+" at "+srt[srt.length-1].R.toFixed(0)+" times. One cost of cells puts every meat at a different point of this curve, and the total for all meat is their sum.";
  set("tp_one_note",txt); set("tp_one_alt",txt);
}

/* ---------- figure 1: how far the cost is from what matters (one log axis) ---------- */
function tpTextW(t,fs,bold){            // the width of a label in px at the page's font (an estimate where there is no canvas)
  try{ if(typeof getComputedStyle!=="undefined"){ const c=tpTextW.c||(tpTextW.c=document.createElement("canvas").getContext("2d"));
    c.font=(bold?"600 ":"400 ")+fs+"px "+(tpTextW.fam||(tpTextW.fam=getComputedStyle(document.body).fontFamily)); const w=c.measureText(t).width; if(w>0) return w; } }catch(e){}
  return t.length*fs*(bold?0.6:0.56);
}
// labels set in rows beside an axis, each beside its own upright line (to its right, else to its left): a label goes in the row nearest
// the axis where it overlaps no other label, crosses no line that reaches that row, and its own line crosses no label nearer the axis.
// Labels are placed in the order given, so a label placed first never moves for one placed after it.
function tpTiers(labs,W,pad,gap){
  const placed=[];
  labs.forEach(l=>{
    for(let t=0;t<8;t++){ for(const side of (l.pref?[l.pref,-l.pref]:(l.x>W*0.75?[-1,1]:[1,-1]))){
      const x0=side>0?l.x+4:l.x-4-l.w, x1=x0+l.w;
      if(x0<pad||x1>W-pad) continue;
      const clash=placed.some(o=>(o.tier===t&&x0<o.x1+gap&&o.x0<x1+gap)||(o.tier>=t&&o.x>x0-3&&o.x<x1+3)||(o.tier<=t&&l.x>o.x0-3&&l.x<o.x1+3));
      if(!clash){ Object.assign(l,{tier:t,side:side,x0:x0,x1:x1}); placed.push(l); return; } } }
    const x0=Math.max(pad,Math.min(W-pad-l.w,l.x+4)); Object.assign(l,{tier:8,side:1,x0:x0,x1:x0+l.w}); placed.push(l); });
  return placed;
}
// tpTiers over every order and side preference of a few labels: the arrangement with no label left unplaced, then the fewest rows.
// It depends only on the labels given, so labels that do not move do not jump when others (placed in another set) move.
function tpTiersBest(labs,W,pad,gap){
  if(labs.length<2){ tpTiers(labs,W,pad,gap); return labs; }
  const orders=labs.length===2?[[0,1],[1,0]]:[labs.map((_,i)=>i)], sides=[0,1,-1], fixed=labs.map(l=>l.pref);
  let best=null;
  orders.forEach(o=>{ sides.forEach(a=>{ sides.forEach(b=>{
    const L=o.map(i=>Object.assign({},labs[i]));
    L.forEach((l,k)=>{ const pr=[a,b][k]; l.pref=pr===0?fixed[o[k]]:pr; });
    tpTiers(L,W,pad,gap);
    const bad=L.filter(l=>l.tier>=8).length, rows=Math.max.apply(null,L.map(l=>l.tier)), sum=L.reduce((x,l)=>x+l.tier,0);
    const sc=bad*1000+rows*10+sum; if(!best||sc<best.sc) best={sc:sc,L:L,o:o}; }); }); });
  best.o.forEach((i,k)=>{ Object.assign(labs[i],{tier:best.L[k].tier,side:best.L[k].side,x0:best.L[k].x0,x1:best.L[k].x1}); });
  return labs;
}
function tpLineDraw(f){
  const svg=document.getElementById("tp_costline"); if(!svg) return;
  const W=Math.max(300,pgWidth("tp_costline_plot",900)), small=W<560, fs=small?11:12, pad=6, lh=fs+4;
  const pubs=TP_PUBS.filter(k=>k!==SCS.ref).map(k=>({key:k, cost:tpRefPoint(k), label:TP_PUBL[k]}));
  const refTop=Math.max.apply(null,TP_PUBS.map(tpRefPoint).concat([f.cost]))*1.05;
  const lo=1, hi=[10,20,30,50,100,200,300,500,1000,2000,5000].find(v=>v>=refTop)||refTop;
  const X=v=>pad+(Math.log(Math.max(lo,Math.min(hi,v)))-Math.log(lo))/(Math.log(hi)-Math.log(lo))*(W-2*pad);
  const fl=C.FEEDSTOCK_FLOOR, fr=TP.frontier, inR=v=>v!==null&&v>=lo&&v<=hi;
  const meName=f.key==="own"?"Your settings":(small?f.label.replace(", all favourable","").replace("Humbird's optimistic design","Humbird's design").replace("Humbird's best estimate (2021)","Humbird's best estimate"):f.label);
  const bt=tpPctB(f.buyers)+" of meat buyers";
  // above the strip: what the meat buyers' setting moves (the costs 1% and 10% need), placed 1% first; below it: what it does not
  // move (your point and price parity), placed your point first. So moving the meat-buyers slider never moves a label below.
  const up=[], dn=[];
  if(inR(f.one)) up.push({kind:"one", x:X(f.one), lines:["1% of "+tpRegionMeat(true)+" needs "+tpUSDk(f.one),"at "+bt]});
  if(inR(f.ten)) up.push({kind:"ten", x:X(f.ten), lines:["10% needs "+tpUSDk(f.ten),"at "+bt]});
  dn.push({kind:"me", x:X(f.cost), bold:true, lines:[meName+": "+tpUSD(f.cost)]});
  tpMeats().forEach(m=>{ if(inR(m.parity)) dn.push({kind:"par", x:X(m.parity), lines:["same price as "+m.plain,tpUSD(m.parity)+" ($"+m.price.toFixed(2)+" in the shop)"]}); });

  [up,dn].forEach(L=>L.forEach(l=>{ l.w=Math.max.apply(null,l.lines.map((t,i)=>tpTextW(t,fs,l.bold&&i===0))); }));
  // 10% always sits left of 1% (it needs a lower cost): its label goes to the left of its line and 1%'s to the right, so neither
  // line crosses the other's label; if 1%'s label has no room on the right, 10% is placed first and 1% goes above it, to the left
  up.forEach(l=>{ l.pref=l.kind==="one"?1:-1; });
  tpTiersBest(up,W,pad,10); tpTiersBest(dn,W,pad,10);
  if(up.some(l=>l.tier>=8)){            // a narrow chart: shorter words, the meat buyers' share kept on each label
    const pb=tpPctB(f.buyers);
    up.forEach(l=>{ l.lines=[(l.kind==="one"?"1%":"10%")+" needs "+tpUSDk(l.kind==="one"?f.one:f.ten),"at "+pb+" of buyers"]; l.w=Math.max.apply(null,l.lines.map(t=>tpTextW(t,fs))); l.pref=l.kind==="one"?1:-1; });
    tpTiersBest(up,W,pad,6); }
  const rowsOf=L=>{ const h=[]; L.forEach(l=>{ h[l.tier]=Math.max(h[l.tier]||0,l.lines.length); }); return h; };
  const hu=rowsOf(up), hd=rowsOf(dn), tierTop=(h,t)=>{ let y=0; for(let i=0;i<t;i++) y+=(h[i]||0)*lh+(h[i]?8:0); return y; };
  // the room above the strip is kept for two rows of two lines whatever the meat buyers' setting, so the strip and everything
  // below it stay put as that slider moves the 1% and 10% lines
  const upH=Math.max(tierTop(hu,hu.length),2*(2*lh+8)), dnH=tierTop(hd,hd.length);
  const sy=6+upH+(upH?4:0), sh=small?30:34, sb=sy+sh, ay=sb+8+dnH+6, H=ay+2*fs+20;
  const col={me:"var(--ink)",one:"#D85A30",ten:"#D85A30",par:"var(--ink2)",ref:"var(--ink2)"}, dash={par:' stroke-dasharray="4 3"',ten:' stroke-dasharray="6 3"'};
  let g='<defs><pattern id="clhd" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#444441"/><line x1="0" y1="0" x2="0" y2="5" stroke="#B4B2A9" stroke-width="1.5"/></pattern>'+
    '<pattern id="clhl" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#85B7EB"/><line x1="0" y1="0" x2="0" y2="6" stroke="#185FA5" stroke-width="1.3"/></pattern></defs>';
  g+='<rect x="'+pad+'" y="'+sy+'" width="'+(W-2*pad)+'" height="'+sh+'" class="clstrip"/>';
  g+='<rect x="'+X(fl).toFixed(1)+'" y="'+sy+'" width="'+(X(fr)-X(fl)).toFixed(1)+'" height="'+sh+'" fill="url(#clhl)" opacity="0.55"/>';
  g+='<rect x="'+pad+'" y="'+sy+'" width="'+(X(fl)-pad).toFixed(1)+'" height="'+sh+'" fill="url(#clhd)"/>';
  // the lines above the strip and their labels (rows go up from the strip)
  up.forEach(l=>{ const top=sy-4-tierTop(hu,l.tier)-hu[l.tier]*lh;
    g+='<line x1="'+l.x.toFixed(1)+'" x2="'+l.x.toFixed(1)+'" y1="'+top+'" y2="'+sb+'" stroke="'+col[l.kind]+'" stroke-width="'+(l.kind==="one"?2:1.5)+'"'+(dash[l.kind]||"")+'/>';
    l.lines.forEach((t,i)=>{ g+='<text x="'+l.x0.toFixed(1)+'" y="'+(top+fs+i*lh)+'" font-size="'+fs+'">'+pgEsc(t)+'</text>'; }); });
  // the range for 8 in 10 draws: a thin whisker through your point, with the estimates it varies in its tooltip
  const a=X(f.cb[0]), b=X(f.cb[2]), my=sy+sh/2, px=X(f.cost), tip=pgEsc(tpVariedTip());
  if(b-a>1) g+='<g class="clwh"><title>'+tip+'</title><path d="M'+a.toFixed(1)+' '+(my-6)+' V'+(my+6)+' M'+a.toFixed(1)+' '+my+' H'+b.toFixed(1)+' M'+b.toFixed(1)+' '+(my-6)+' V'+(my+6)+'" fill="none" stroke="var(--ink)" stroke-width="1.5"/>'+
     '<rect x="'+a.toFixed(1)+'" y="'+(my-8)+'" width="'+Math.max(4,b-a).toFixed(1)+'" height="16" fill="transparent"/></g>';
  // the lines below the strip and their labels (rows go down from the strip)
  dn.forEach(l=>{ const top=sb+8+tierTop(hd,l.tier);
    g+='<line x1="'+l.x.toFixed(1)+'" x2="'+l.x.toFixed(1)+'" y1="'+(l.kind==="me"?my+8:sy)+'" y2="'+(top+4)+'" stroke="'+col[l.kind]+'" stroke-width="'+(l.kind==="me"?1:1.5)+'"'+(dash[l.kind]||"")+'/>';
    l.lines.forEach((t,i)=>{ g+='<text x="'+l.x0.toFixed(1)+'" y="'+(top+fs+i*lh)+'" font-size="'+fs+'"'+(l.bold&&i===0?' class="b"':'')+'>'+pgEsc(t)+'</text>'; }); });
  // published costs: a short tick across the strip with a letter; the note under the chart names each with its cost
  pubs.forEach(q=>{ if(!inR(q.cost)) return; const x=X(q.cost);
    g+='<g><title>'+pgEsc(q.label+": "+tpUSD(q.cost)+" a kilo of cells")+'</title><line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+(sy+3)+'" y2="'+(sb-3)+'" stroke="var(--ink2)" stroke-width="2"/>'+
       '<text x="'+(x+4).toFixed(1)+'" y="'+(sy+fs+2)+'" font-size="'+(fs-1)+'" class="b">'+q.label.charAt(0)+'</text></g>'; });
  g+='<circle class="clme" cx="'+px.toFixed(1)+'" cy="'+my+'" r="'+(small?6:7)+'"><title>'+tip+'</title></circle>';
  // the axis, under everything
  const mut='class="ax"';
  g+='<line x1="'+pad+'" x2="'+(W-pad)+'" y1="'+ay+'" y2="'+ay+'" '+mut+'/>';
  let lastX=-1e9; const tks=[1,2,5,10,20,50,100,200,500,1000,2000,5000].filter(v=>v>=lo&&v<=hi);
  tks.forEach(v=>{ const x=X(v), t="$"+v, w=tpTextW(t,fs), xc=Math.max(pad+w/2,Math.min(W-pad-w/2,x));
    g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+ay+'" y2="'+(ay+4)+'" '+mut+'/>';
    if(xc-w/2>lastX+6){ g+='<text x="'+xc.toFixed(1)+'" y="'+(ay+fs+5)+'" text-anchor="middle" font-size="'+fs+'" class="m">'+t+'</text>'; lastX=xc+w/2; } });
  g+='<text x="'+(W/2)+'" y="'+(ay+2*fs+12)+'" text-anchor="middle" font-size="'+fs+'" class="m">Cost to grow a kilo of cells (log scale)</text>';
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H);
  svg.innerHTML=g;
}
function tpLineText(f){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const fl=C.FEEDSTOCK_FLOOR, fr=TP.frontier;
  set("tp_cl_fl","below $"+fl.toFixed(2)+": below what the cells must eat");
  set("tp_cl_fr","$"+fl.toFixed(2)+" to $"+fr.toFixed(2)+": beyond every known limit");
  const q=document.getElementById("tp_cl_wq"); if(q&&q.setAttribute) q.setAttribute("data-tip",tpVariedTip());
  const ms=tpMeats(), plist=tpAnd(ms.map(m=>m.plain+" at "+tpUSD(m.parity)+" a kilo of cells ($"+m.price.toFixed(2)+" a kilo in the shop)"));
  set("tp_cl_note","<b>Each kind of meat has its own price</b>, so there is no single cost at which cultivated meat matches meat. It would sell at the same shop price as "+plist+
    ", after "+scMoney(state.markup_add)+" a kilo to reach the shelf and the shop's "+(state.retail_margin*100).toFixed(0)+"% margin (a steak or fillet also carries its plant protein and assembly). These do not depend on shoppers. "+
    "The 1% and 10% lines are the costs those long-run shares of all meat and seafood need with "+tpPctB(f.buyers)+" of meat buyers picking it at the same price (your setting in section 4): move that slider and they move"+
    (f.one===null?"; with these shoppers no cost reaches 1%":(f.ten===null?"; with these shoppers no cost reaches 10%":(f.ten<1?"; 10% would need under $1":"")))+". "+
    "Your point is the cost at your settings. The lettered ticks are published costs: "+tpAnd(TP_PUBS.filter(k=>k!==SCS.ref).map(k=>TP_PUBL[k].charAt(0)+", "+TP_PUBL[k]+" as this model prices it, "+tpUSD(tpRefPoint(k))).map(t=>t.replace("A company's report as this model prices it","a company's own report")))+".");
  set("tp_cl_alt","A log scale of the cost to grow a kilo of cells, from $1 up. Below $"+fl.toFixed(2)+" is impossible (what the cells must eat); up to $"+fr.toFixed(2)+
    " needs some lever past every known limit. Same shop price as "+plist+". "+
    (f.one===null?"No cost reaches 1% with these shoppers. ":"With "+tpPctB(f.buyers)+" of meat buyers, 1% of "+tpRegionMeat()+" needs "+tpUSDk(f.one)+(f.ten!==null?"; 10% needs "+tpUSDk(f.ten):"")+". ")+
    f.label+": "+tpUSD(f.cost)+".");
}

/* ---------- figure 2: where the money goes, by what drives it ---------- */
// each group its own hue (litres of medium: blue, time in the tank: amber, everything else: grey), each item a shade of it; the CSS
// variables (--g-*) are set for light and dark, each with the text colour that reads on it (--g-*-i)
const TP_GCOL={litres:"var(--g-l1)", time:"var(--g-t1)", other:"var(--g-o1)"};
const TP_ICOL={membranes:"l1", medium:"l2", protectant:"l3", gf:"l4", clean_cap:"l5", clean_run:"l6", capital:"t1", labour:"t2", energy:"o1", supplies:"o2"};
const TP_ISHORT={membranes:"Membranes", medium:"Medium", protectant:"Protectant", gf:"Growth factors", clean_cap:"Cleaning: equipment", clean_run:"Cleaning: running", capital:"Plant", labour:"Labour", energy:"Energy", supplies:"Supplies"};
const TP_GSHORT={litres:["Litres of medium","Litres"], time:["Time in the tank","Time"], other:["Everything else","Else"]};
function tpICol(k){ return "var(--g-"+TP_ICOL[k]+")"; }
function tpGroupsDraw(f){
  const svg=document.getElementById("tp_groups"); if(!svg) return;
  const G=f.groups, W=Math.max(280,pgWidth("tp_groups_plot",440)), small=W<420, fs=small?11:12, pad=4;
  const xmax=Math.max(G.total,f.one||0)*1.04, step=[1,2,5,10,20,25,50,100,200,500].find(s=>xmax/s<=(small?4:6))||1000;
  const X=v=>pad+(W-2*pad)*v/xmax, gy=fs+2, by=gy+12, bh=small?30:34, ay=by+bh, oneY=ay+fs+12;
  const H=oneY+(f.one!==null?2*(fs+4)+6:0)+4;
  let g='', acc=0;
  // the items: one shade each, a thin gap of the card's colour between them, the item's name inside where it fits
  const x1=f.one!==null?X(f.one):null;
  G.groups.forEach(gr=>{ gr.items.forEach(it=>{ if(it.v<=0) return; const a=X(acc), b=X(acc+it.v); acc+=it.v; const w=Math.max(0.5,b-a-1.5);
      g+='<rect x="'+a.toFixed(1)+'" y="'+by+'" width="'+w.toFixed(1)+'" height="'+bh+'" fill="'+tpICol(it.key)+'"><title>'+pgEsc(gr.name+": "+it.name)+': $'+it.v.toFixed(2)+' a kilo</title></rect>';
      // the item's name inside its segment where it fits, kept off the 1% line (to the line's right, else its left, else left out)
      const nm=TP_ISHORT[it.key], tw=tpTextW(nm,fs);
      let lx=null; if(w>tw+8){ lx=a+4; if(x1!==null&&x1>lx-3&&x1<lx+tw+3) lx=(x1+4+tw<=a+w-2)?x1+4:((x1-4-tw>=a+2)?x1-4-tw:null); }
      if(lx!==null) g+='<text x="'+lx.toFixed(1)+'" y="'+(by+bh/2+fs*0.36).toFixed(1)+'" font-size="'+fs+'" style="fill:var(--g-'+TP_ICOL[it.key]+'-i)">'+nm+'</text>'; }); });
  // each group: a bracket over its items with its name and its part of the cost
  acc=0; let lastR=-1e9;
  G.groups.forEach(gr=>{ const a=X(acc), b=X(acc+gr.v)-1.5; acc+=gr.v; if(b-a<3) return;
    const pc=Math.round(gr.v/G.total*100)+"%", cands=[TP_GSHORT[gr.key][0]+" "+pc,TP_GSHORT[gr.key][1]+" "+pc,pc];
    g+='<path d="M'+a.toFixed(1)+' '+(by-2)+' V'+(by-7)+' H'+b.toFixed(1)+' V'+(by-2)+'" fill="none" stroke="'+TP_GCOL[gr.key]+'" stroke-width="1.5"/>';
    const t=cands.find(c=>tpTextW(c,fs,true)<=Math.max(b-a,0)+((gr.key==="other")?0:0))||null;
    if(t&&a>lastR+4){ g+='<text x="'+a.toFixed(1)+'" y="'+gy+'" font-size="'+fs+'" class="b">'+t+'</text>'; lastR=a+tpTextW(t,fs,true); } });
  // the axis, with no tick label where the 1% line comes down
  for(let t=0;t<=xmax+1e-9;t+=step){ const x=X(t), s="$"+t, w=tpTextW(s,fs), xc=Math.max(pad+w/2,Math.min(W-pad-w/2,x));
    g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+ay+'" y2="'+(ay+4)+'" class="ax"/>';
    if(x1===null||Math.abs(xc-x1)>w/2+4) g+='<text x="'+xc.toFixed(1)+'" y="'+(ay+fs+5)+'" text-anchor="middle" font-size="'+fs+'" class="m">'+s+'</text>'; }
  // what 1% needs, at the reader's meat buyers: a line through the bar, labelled under the axis
  if(f.one!==null){ const l1="1% of "+tpRegionMeat(true)+" needs "+tpUSDk(f.one), l2="at "+tpPctB(f.buyers)+" of meat buyers";
    const w=Math.max(tpTextW(l1,fs),tpTextW(l2,fs)), cx=Math.max(pad+w/2,Math.min(W-pad-w/2,x1));
    g+='<line x1="'+x1.toFixed(1)+'" x2="'+x1.toFixed(1)+'" y1="'+(by-4)+'" y2="'+(oneY-2)+'" stroke="#D85A30" stroke-width="2"/>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(oneY+fs)+'" text-anchor="middle" font-size="'+fs+'">'+pgEsc(l1)+'</text>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(oneY+2*fs+4)+'" text-anchor="middle" font-size="'+fs+'">'+pgEsc(l2)+'</text>'; }
  svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H);
  svg.innerHTML=g;
}
function tpGroupsText(f){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const G=f.groups, $2=v=>"$"+v.toFixed(2), pc=v=>Math.round(v/G.total*100)+"%";
  set("tp_groups_sub",scMoney(G.total)+" a kilo of cells with every estimate at its most likely value"+(Math.abs(G.total-f.cost)>0.05?" (the median of the draws, "+tpUSD(f.cost)+", is the figure above)":"")+".");
  set("tp_groups_table",'<table class="num grp"><tbody>'+G.groups.map(gr=>
    '<tr class="gh"><td><span class="sw gsw" style="border-color:'+TP_GCOL[gr.key]+'"></span>'+gr.name+(gr.note?' <span class="gn">'+gr.note+'</span>':'')+'</td><td>'+$2(gr.v)+'</td><td>'+pc(gr.v)+'</td></tr>'+
    gr.items.map(it=>'<tr><td class="it"><span class="sw" style="background:'+tpICol(it.key)+'"></span>'+it.name+(it.note?' <span class="gn">'+it.note+'</span>':'')+'</td><td>'+$2(it.v)+'</td><td></td></tr>').join("")).join("")+
    '<tr class="gt"><td>Total, a kilo of cells</td><td>'+$2(G.sum)+'</td><td></td></tr></tbody></table>');
  const L=G.groups[0], T=G.groups[1], rm=tpRegionMeat(), at=" with "+tpPctB(f.buyers)+" of meat buyers picking it at the same price";
  let s;
  if(f.one===null) s="With these shoppers no cost of cells reaches 1% of "+rm+".";
  else if(G.total<=f.one) s="For 1% of "+rm+at+" the whole kilo must cost "+tpUSDk(f.one)+": at "+scMoney(G.total)+" this one does, with "+scMoney(f.one-G.total)+" to spare.";
  else if(Math.max(L.v,T.v)>f.one) s="For 1% of "+rm+at+" the whole kilo must cost "+tpUSDk(f.one)+": "+(L.v>=T.v?"the litres alone ("+scMoney(L.v)+") cost":"the time in the tank alone ("+scMoney(T.v)+") costs")+" more than that.";
  else s="For 1% of "+rm+at+" the whole kilo must cost "+tpUSDk(f.one)+", "+scMoney(G.total-f.one)+" less than this: the litres are "+scMoney(L.v)+" of it, the time in the tank "+scMoney(T.v)+".";
  set("tp_groups_say",s);
  set("tp_groups_alt","A bar of "+scMoney(G.total)+" split by what drives the cost: "+G.groups.map(gr=>gr.name.toLowerCase()+" "+$2(gr.v)+" ("+pc(gr.v)+": "+
    gr.items.map(it=>it.name.toLowerCase()+" "+$2(it.v)).join(", ")+")").join("; ")+
    (f.one!==null?". A line marks the "+tpUSDk(f.one)+" that 1% of "+rm+" needs with "+tpPctB(f.buyers)+" of meat buyers picking it at the same price.":"."));
}

/* ---------- figure 3: where it would sell, by species and type of meat: bars (default) or a disk ---------- */
// The original page's two charts (git 7a3165d: drawBars, drawPie), ported to the first screen's engine: they follow the reader's
// cells, plant, meat buyers, plant-protein share of a cut and region. Bars: one bar per product, coloured by type (mince, cut,
// premium), cultivated meat solid with plant-based meat stacked on it, paler; dashed lines are the totals. Disk: one wedge per
// species, sized by weight eaten (or by money spent), with cultivated meat's share solid from the inside out.
const TP_TIER={basic:["mince and processed","var(--t-basic)"], cut:["cuts and fillets","var(--t-cut)"], premium:["premium","var(--t-prem)"]};
function tpSellView(){ return PGS.sellView||"bars"; }
function tpSetSellView(v){ PGS.sellView=v; try{ localStorage.setItem("tp_sell_view",v); }catch(e){} tpAnimalsRender(PGS.lastF||pgFacts()); }
function tpSetDiskBasis(v){ PGS.diskBasis=v; tpAnimalsRender(PGS.lastF||pgFacts()); }
function tpProdShort(n){ const m=n.match(/\(([^)]*)\)/); return m?m[1].replace("proc.","processed").split(", ")[0]:"all"; }
function tpGroupsBySpecies(A){
  const by={}; A.types.forEach(t=>{ (by[t.animal]=by[t.animal]||[]).push(t); });
  const TO={basic:0,cut:1,premium:2};
  return Object.keys(by).map(a=>{ const it=by[a].sort((p,q)=>TO[p.tier]-TO[q.tier]||p.price-q.price), w=it.reduce((x,t)=>x+t.w,0);
    return {animal:a, items:it, avg:it.reduce((x,t)=>x+t.w*t.price,0)/w}; }).sort((a,b)=>a.avg-b.avg);
}
function tpSellBars(A){
  const svg=document.getElementById("tp_sbars"); if(!svg) return;
  const W=Math.max(300,pgWidth("tp_sell_plot",720)), fs=W<560?11:12, G=tpGroupsBySpecies(A);
  const top=Math.max.apply(null,A.types.map(t=>t.sh+t.shp)), nice=[0.0005,0.001,0.002,0.005,0.01,0.02,0.03,0.05,0.08,0.1,0.12,0.15,0.2,0.3,0.4,0.5,0.6,0.8,1];
  const yTop=nice.find(v=>v>=top*1.12)||1, pct=v=>pgPctS(v*100);
  const tip=t=>pgEsc(l3Name(t.name)+": cultivated "+pct(t.sh)+", plant-based "+pct(t.shp)+" of it; in the shop "+t.R.toFixed(2)+" times the price of the meat it copies, $"+t.price.toFixed(2)+" a kilo");
  let g='';
  if(W>=560){                                  // upright bars, as the original
    const totT=["cultivated, by weight "+pgPctS(A.total),"cultivated, by value "+pgPctS(A.value),"plant-based, by weight "+pgPctS(A.pbv),"plant-based, by value "+pgPctS(A.pbval)];
    const mL=44, mR=Math.round(Math.max.apply(null,totT.map(t=>tpTextW(t,fs)))+16), mB=2*fs+14;
    const slots=G.reduce((a,gr)=>a+Math.max(2,gr.items.length),0)+0.8*(G.length-1), sw=(W-mL-mR)/slots, bw=Math.min(24,sw*0.72);
    const lab=t=>pct(t.sh), lw=Math.max.apply(null,A.types.map(t=>tpTextW(lab(t),fs,true))), rot=lw>Math.min(sw,bw*1.15)-3;
    const mT=(rot?lw+8:fs+8)+4, H=mT+200+mB;
    const Y=v=>H-mB-(H-mT-mB)*v/yTop;
    const st=[0.0001,0.0002,0.0005,0.001,0.002,0.0025,0.005,0.01,0.02,0.025,0.05,0.1,0.2].find(x=>yTop/x<=6)||0.25; for(let v=0;v<=yTop+1e-12;v+=st){ g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+Y(v).toFixed(1)+'" y2="'+Y(v).toFixed(1)+'" class="grid"/>'+
      '<text x="'+(mL-5)+'" y="'+(Y(v)+4).toFixed(1)+'" text-anchor="end" font-size="'+fs+'" class="m">'+(v<1e-12?"0":tpPct2(v*100))+'</text>'; }
    let x=mL;
    G.forEach(gr=>{ const n=Math.max(2,gr.items.length), gx=x, gw=n*sw;
      gr.items.forEach((t,j)=>{ const cx=gx+gw/2+(j-(gr.items.length-1)/2)*bw*1.15, c=TP_TIER[t.tier][1], y0=Y(t.sh), y1=Y(t.sh+t.shp);
        g+='<g><title>'+tip(t)+'</title><rect x="'+(cx-bw/2).toFixed(1)+'" y="'+y0.toFixed(1)+'" width="'+bw.toFixed(1)+'" height="'+Math.max(0.5,H-mB-y0).toFixed(1)+'" fill="'+c+'"/>'+
           (t.shp>0?'<rect x="'+(cx-bw/2+0.5).toFixed(1)+'" y="'+y1.toFixed(1)+'" width="'+(bw-1).toFixed(1)+'" height="'+Math.max(0,y0-y1).toFixed(1)+'" fill="'+c+'" fill-opacity="0.32" stroke="'+c+'" stroke-width="1"/>':'')+'</g>';
        const ly=Math.min(y0,y1)-4;
        g+=rot?'<text x="'+(cx+fs*0.35).toFixed(1)+'" y="'+ly.toFixed(1)+'" font-size="'+fs+'" class="b" transform="rotate(-90 '+(cx+fs*0.35).toFixed(1)+' '+ly.toFixed(1)+')">'+lab(t)+'</text>'
              :'<text x="'+cx.toFixed(1)+'" y="'+ly.toFixed(1)+'" font-size="'+fs+'" text-anchor="middle" class="b">'+lab(t)+'</text>'; });
      const nm=gr.animal.replace("/",", ");
      g+='<text x="'+(gx+gw/2).toFixed(1)+'" y="'+(H-mB+fs+6)+'" text-anchor="middle" font-size="'+fs+'">'+pgEsc(nm)+'</text>';
      x+=gw+0.8*sw; });
    g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+(H-mB)+'" y2="'+(H-mB)+'" class="ax"/>';
    // the totals: cultivated and plant-based, by weight and by value, each a dashed line labelled in the right-hand gutter
    const tot=[[A.total/100,"var(--ink)",totT[0],"6 3"],[A.value/100,"var(--ink)",totT[1],"1.5 3"],[A.pbv/100,"var(--pbg)",totT[2],"6 3"],[A.pbval/100,"var(--pbg)",totT[3],"1.5 3"]];
    const L=tot.map(([v,c,t,d],i)=>({y:Y(Math.min(v,yTop)),yl:Y(Math.min(v,yTop)),c:c,t:t,d:d})).sort((a,b)=>b.y-a.y);
    for(let k=1;k<L.length;k++) if(L[k-1].y-L[k].y<fs+3) L[k].y=L[k-1].y-(fs+3);
    const over=mT-(L[L.length-1].y-fs); if(over>0) L.forEach(o=>{ o.y+=over; });
    L.forEach(o=>{ g+='<line x1="'+mL+'" x2="'+(W-mR)+'" y1="'+o.yl.toFixed(1)+'" y2="'+o.yl.toFixed(1)+'" stroke="'+o.c+'" stroke-width="1.2" stroke-dasharray="'+o.d+'"/>'+
      '<line x1="'+(W-mR)+'" x2="'+(W-mR+6)+'" y1="'+o.yl.toFixed(1)+'" y2="'+(o.y-4).toFixed(1)+'" stroke="'+o.c+'" stroke-width="0.8"/>'+
      '<text x="'+(W-mR+8)+'" y="'+o.y.toFixed(1)+'" font-size="'+fs+'" style="fill:'+o.c+'">'+pgEsc(o.t)+'</text>'; });
    svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H);
  } else {                                     // narrow screens: the same bars laid on their side, one row per product
    const lw=Math.min(130,Math.round(W*0.34)), vw=84, x0=lw, x1=W-vw, rh=fs+9, hh=fs+10;
    const X=v=>x0+(x1-x0)*Math.min(v,yTop)/yTop;
    let y=fs+8;
    g+='<text x="'+x0+'" y="'+(fs)+'" font-size="'+fs+'" class="m">0</text><text x="'+x1+'" y="'+fs+'" font-size="'+fs+'" text-anchor="end" class="m">'+tpPct2(yTop*100)+'</text>';
    const y0=y;
    G.forEach(gr=>{ g+='<text x="0" y="'+(y+fs).toFixed(1)+'" font-size="'+fs+'" class="b">'+pgEsc(gr.animal.replace("/",", "))+'</text>'; y+=hh;
      gr.items.forEach(t=>{ const c=TP_TIER[t.tier][1];
        g+='<g><title>'+tip(t)+'</title><text x="8" y="'+(y+fs-1).toFixed(1)+'" font-size="'+fs+'">'+pgEsc(tpProdShort(t.name))+'</text>'+
           '<rect x="'+x0+'" y="'+(y+1).toFixed(1)+'" width="'+Math.max(0.5,X(t.sh)-x0).toFixed(1)+'" height="'+(rh-6)+'" fill="'+c+'"/>'+
           (t.shp>0?'<rect x="'+X(t.sh).toFixed(1)+'" y="'+(y+1.5).toFixed(1)+'" width="'+Math.max(0,X(t.sh+t.shp)-X(t.sh)).toFixed(1)+'" height="'+(rh-7)+'" fill="'+c+'" fill-opacity="0.32" stroke="'+c+'" stroke-width="1"/>':'')+
           '<text x="'+W+'" y="'+(y+fs-1).toFixed(1)+'" font-size="'+fs+'" text-anchor="end" class="b">'+pct(t.sh)+'</text></g>';
        y+=rh; }); });
    const xt=X(A.total/100);
    g+='<line x1="'+xt.toFixed(1)+'" x2="'+xt.toFixed(1)+'" y1="'+(y0-2)+'" y2="'+(y+2)+'" stroke="var(--ink)" stroke-width="1.2" stroke-dasharray="6 3"/>'+
       '<text x="'+Math.min(xt+4,x1-60).toFixed(1)+'" y="'+(y+fs+4)+'" font-size="'+fs+'">all meat, by weight: '+pgPctS(A.total)+'</text>';
    const H=y+fs+10;
    svg.setAttribute("viewBox","0 0 "+W+" "+H); svg.setAttribute("width",W); svg.setAttribute("height",H);
  }
  svg.innerHTML=g;
}
function tpSellDisk(A){
  const svg=document.getElementById("tp_disk"); if(!svg) return;
  const byVal=PGS.diskBasis==="val", G=tpGroupsBySpecies(A).map(gr=>{ const w=gr.items.reduce((a,t)=>a+t.w,0), v=gr.items.reduce((a,t)=>a+t.w*t.price,0);
    return Object.assign(gr,{wt:byVal?v:w, w:w, v:v, cf:(byVal?gr.items.reduce((a,t)=>a+t.w*t.price*t.sh,0)/v:gr.items.reduce((a,t)=>a+t.w*t.sh,0)/w),
                            pf:(byVal?gr.items.reduce((a,t)=>a+t.w*t.price*t.shp,0)/v:gr.items.reduce((a,t)=>a+t.w*t.shp,0)/w)}); }).sort((a,b)=>b.wt-a.wt);
  const tot=G.reduce((a,gr)=>a+gr.wt,0), S=Math.min(300,Math.max(240,pgWidth("tp_disk_box",300))), cx=S/2, cy=S/2, rO=S/2-6, rI=rO*0.55;
  const P=(r,a)=>[cx+r*Math.cos(a),cy+r*Math.sin(a)];
  const arc=(r0,r1,a0,a1)=>{ const [x0,y0]=P(r1,a0),[x1,y1]=P(r1,a1),[xa,ya]=P(r0,a1),[xb,yb]=P(r0,a0), big=(a1-a0)>Math.PI?1:0;
    return "M"+x0.toFixed(2)+" "+y0.toFixed(2)+" A"+r1+" "+r1+" 0 "+big+" 1 "+x1.toFixed(2)+" "+y1.toFixed(2)+" L"+xa.toFixed(2)+" "+ya.toFixed(2)+" A"+r0+" "+r0+" 0 "+big+" 0 "+xb.toFixed(2)+" "+yb.toFixed(2)+" Z"; };
  let g='', a=-Math.PI/2;
  G.forEach(gr=>{ const a1=a+gr.wt/tot*2*Math.PI, col=colOf(gr.animal), rC=rI+(rO-rI)*gr.cf, rP=rC+(rO-rI)*gr.pf;
    const t=pgEsc(gr.animal.replace("/",", ")+": "+Math.round(gr.wt/tot*100)+"% of all meat "+(byVal?"by value":"by weight")+"; cultivated "+pgPctS(gr.cf*100)+", plant-based "+pgPctS(gr.pf*100));
    g+='<g><title>'+t+'</title><path d="'+arc(rI,rO,a,a1)+'" fill="'+col+'" fill-opacity="0.22" stroke="var(--card)" stroke-width="1.5"/>'+
       (gr.cf>0?'<path d="'+arc(rI,rC,a,a1)+'" fill="'+col+'"/>':'')+(gr.pf>0?'<path d="'+arc(rC,rP,a,a1)+'" fill="'+col+'" fill-opacity="0.55"/>':'')+'</g>';
    a=a1; });
  const total=byVal?A.value:A.total, pb=byVal?A.pbval:A.pbv;
  g+='<text x="'+cx+'" y="'+(cy-4)+'" text-anchor="middle" font-size="24" class="b">'+tpPct2(total)+'</text>'+
     '<text x="'+cx+'" y="'+(cy+14)+'" text-anchor="middle" font-size="12">cultivated, '+(byVal?"by value":"by weight")+'</text>'+
     '<text x="'+cx+'" y="'+(cy+29)+'" text-anchor="middle" font-size="11" class="m">plant-based '+tpPct2(pb)+'</text>';
  svg.setAttribute("viewBox","0 0 "+S+" "+S); svg.setAttribute("width",S); svg.setAttribute("height",S);
  svg.innerHTML=g;
  const tb=document.getElementById("tp_disk_table");
  if(tb) tb.innerHTML='<table class="num dk"><thead><tr><th>Meat</th><th>$ a kilo</th><th>Of all meat</th><th>Cultivated</th><th>Plant-based</th></tr></thead><tbody>'+
    G.map(gr=>'<tr><td><span class="sw" style="background:'+colOf(gr.animal)+'"></span>'+pgEsc(gr.animal.replace("/",", "))+'</td><td>$'+(gr.v/gr.w).toFixed(2)+'</td><td>'+Math.round(gr.wt/tot*100)+'%</td><td>'+pgPctS(gr.cf*100)+'</td><td>'+pgPctS(gr.pf*100)+'</td></tr>').join("")+
    '</tbody></table>';
}
function tpAnimalsRender(f){
  PGS.lastF=f;
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  const A=f.animals, part=v=>v<0.005?"under 1%":Math.round(v*100)+"%", wp=v=>{ const x=v*100; return x<9.5?x.toFixed(1):x.toFixed(0); };
  const view=tpSellView(), byVal=PGS.diskBasis==="val";
  ["bars","disk"].forEach(v=>{ const b=document.getElementById("tp_sv_"+v); if(b){ b.className=v===view?"on":""; b.setAttribute("aria-pressed",v===view?"true":"false"); }
    const p=document.getElementById("tp_sell_"+v); if(p) p.style.display=v===view?"":"none"; });
  ["vol","val"].forEach(v=>{ const b=document.getElementById("tp_db_"+v); if(b){ const on=(v==="val")===byVal; b.className=on?"on":""; b.setAttribute("aria-pressed",on?"true":"false"); } });
  set("tp_animals_sub",pgRegionName()+", at the cost of "+tpUSD(f.cost)+" and "+tpPctB(f.buyers)+" of meat buyers picking it at the same price. "+
    tpCutWords(A.cut)+". Shares by weight, in the long run.");
  set("tp_animals_total","<b>All meat and seafood: "+tpPct2(A.total)+" by weight of product, "+tpPct2(A.cells)+" by weight of cells</b> ($"+A.avg.toFixed(2)+
    " a kilo on average). Plant-based meat: about "+tpPct2(f.pb)+" with no cultivated meat on sale, "+tpPct2(A.pbv)+" beside it.");
  if(view==="bars") tpSellBars(A); else tpSellDisk(A);
  const sl=tpSellers(A), cheapN=tpAnd(sl.cheap.map(r=>r.word));
  let s=tpCap(tpAnd(sl.top.map(r=>r.word)))+" bring "+tpFrac(sl.part)+" of its sales.";
  if(sl.cheap.length&&sl.cheapW>=0.3&&sl.cheapPart<0.6*sl.cheapW)
    s+=" "+tpCap(cheapN)+" "+(sl.cheap.length>1?"are":"is")+" "+tpFrac(sl.cheapW)+" of "+tpRegionMeat()+" but cheap, so it sells little there"+
       (f.sb[2]<0.00095?".":": that is why the share of all meat and seafood is "+tpPct2(A.total)+", well below its share of the dearer meats.");
  else if(sl.cheap.length) s+=" "+tpCap(cheapN)+", the cheaper meats, bring "+part(sl.cheapPart)+".";
  set("tp_animals_say",s);
  set("tp_animals_scale",view==="bars"?"Bars: cultivated meat's long-run share of each product, by weight, solid; plant-based meat's stacked on it, paler. Colour: mince and processed, cuts and fillets, or premium. Point at a bar for its numbers.":
    "Disk: each wedge is a kind of meat, sized by "+(byVal?"the money spent on it":"the weight eaten")+". From the inside out: cultivated meat's share (solid, to scale, so a small share is a thin line), plant-based meat's (lighter), the rest (palest).");
  set("tp_animals_alt","Long-run share of each product, "+pgRegionName()+": "+tpGroupsBySpecies(A).map(gr=>gr.animal.replace("/",", ")+": "+gr.items.map(t=>tpProdShort(t.name)+" "+pgPctS(t.sh*100)+" cultivated, "+pgPctS(t.shp*100)+" plant-based").join("; ")).join(". ")+
    ". By kind of meat: "+A.rows.map(r=>r.name+" "+pgPctS(r.within)+" ("+wp(r.w)+"% of all meat, "+part(r.part)+" of its sales)").join("; ")+
    ". All meat and seafood: "+tpPct2(A.total)+" by weight of product, "+tpPct2(A.cells)+" by weight of cells.");
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
  SCS.ref=k; SCS.from=k; SCS.traits={}; SCS.held={}; SCS.src="scenario"; SCS.vessel="stirred"; SCS.vmode=null; SCS.device="tff"; SCS.clean=tpCleanNone();
  if(r.kind==="humbird"){ SCS.base="humbird"; SCS.hbKey=k; SCS.hb=Object.assign({},r.hb); SCS.choice=Object.assign({},SC.presets[TP_CH0].choice); SCS.redesign=false; }
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
function tpExtraNow(){ tpApplyFx(SCS); SC_EXTRA=Object.assign({},SCS.traits,tpHeldKw(tpHeld(SCS),SCS),tpCleanKw(SCS)); }
// a light update while a slider moves: the cloud, the map's point and the numbers (no new calibration)
function tpLive(){ tpSchedule(()=>{ tpExtraNow(); PGS.cloud=tpPointFor(SCS); pgSetCost(); tpRenderFirst(); }); }
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
function scPick(k,v){                // a switch in "The tank and plant in detail"
  if(SCS.base==="humbird"){ SCS.base="switches"; SCS.redesign=true; }
  SCS.choice[k]=v; delete SCS.choice.thin;                        // a thinned design is chosen again (tpRedesign) or dropped
  if(k==="cells") ["nh3_kg","lac_yield","mass_pg"].forEach(t=>delete SCS.traits[t]);
  if(k==="growth") delete SCS.traits.doubling_h;
  if(k==="tricks"||k==="shape") SCS.redesign=false;               // the reader chose the tank design
  tpTouched(); tpCommit(); }
function scDesignNow(){ SCS.redesign=true; tpTouched(); tpCommit(); }
function scPickTwo(a,i,b,j){ SCS.choice[a]=i; SCS.choice[b]=j; delete SCS.choice.thin; if([a,b].some(k=>k==="tricks"||k==="shape")) SCS.redesign=false; tpTouched(); tpCommit(); }
function scApplyChoice(o){ SCS.base="switches"; SCS.choice=Object.assign({},SC.presets[TP_CH0].choice,o); SCS.traits={}; SCS.held={}; SCS.clean=tpCleanNone(); SCS.redesign=false; tpTouched(); tpCommit(); }
function tpSetTrait(k,v,live){ SCS.traits[k]=v; tpTouched(); if(live) tpLive(); else tpCommit(); }
function tpFreeTrait(k){ delete SCS.traits[k]; tpTouched(); tpCommit(); }
/* ---------- Humbird's best estimate: what this model counts and he does not (the owner, 2026-11-20: "stick to Humbird design unless he
   missed something important"). Five levers start at his value, none; the button sets all five to the model's own values, a
   second click puts his back. ---------- */
function tpAddsRef(st){ st=st||SCS; const L=tpRefLevers(st); return L?tpHb(st):null; }
function tpAddModel(k){ const q=TP_PAR[k]; return q.kind==="fxx"?1:tpFx0(q.kind==="fx"?q.arg:q.dflt)*q.scale; }   // the model's own value, in the slider's unit
function tpAddsOn(st){ st=st||SCS; const R=tpAddsRef(st); return !!R&&R.adds.every(a=>st.held[a[0]]!==undefined&&Math.abs(st.held[a[0]]-tpAddModel(a[0]))<1e-9); }
function tpAddsSet(on){ const R=tpAddsRef(SCS); if(!R) return; R.adds.forEach(a=>{ if(on) SCS.held[a[0]]=tpAddModel(a[0]); else delete SCS.held[a[0]]; }); }
function tpToggleAdds(){ if(!tpAddsRef(SCS)) return; tpAddsSet(!tpAddsOn(SCS)); tpTouched(); tpCommit(); }
// what each addition adds at the reader's other settings: each lever switched on alone, from all five at Humbird's value
function tpAddsLive(st){ st=st||SCS; const R=tpAddsRef(st); if(!R) return null;
  const off=Object.assign({},st.held); R.adds.forEach(a=>{ off[a[0]]=R.levers[a[0]]; });
  const cost=h=>tpPointFor(Object.assign({},st,{held:h})).point, base=cost(off), all=Object.assign({},off);
  const rows=R.adds.map(a=>{ const v=tpAddModel(a[0]); all[a[0]]=v; return {key:a[0], name:a[1], value:v, adds:cost(Object.assign({},off,{[a[0]]:v}))-base}; });
  return {base:base, rows:rows, all:cost(all)}; }
function tpAddsText(A){
  const amt=d=>Math.abs(d)<0.05?"nothing at these settings":"$"+Math.abs(d).toFixed(1)+" a kilo", verb=(d,pl)=>(d<-0.05?(pl?"take off ":"takes off "):(pl?"add ":"adds "));
  const how={kla_exp:v=>" ("+tpFmtParam(TP_PAR.kla_exp,v)+")", min_perfusion:v=>" ("+tpFmtParam(TP_PAR.min_perfusion,v)+")", killx:v=>"", harvest_loss:v=>" ("+tpFmtParam(TP_PAR.harvest_loss,v)+" of the cells grown)", protect_dose:v=>" ("+tpFmtParam(TP_PAR.protect_dose,v)+")"};
  return A.rows.map(r=>r.name+(how[r.key]?how[r.key](r.value):"")+" "+verb(r.adds,/^Cells/.test(r.name))+amt(r.adds)+".").join(" ")+
    " Each is switched on alone; all five together bring "+tpUSD(A.base)+" to "+tpUSD(A.all)+" a kilo."; }
function tpSetHeld(k,v,live){ SCS.held[k]=v; tpTouched(); if(live) tpLive(); else tpCommit(); }
function tpFreeHeld(k){ delete SCS.held[k]; tpTouched(); tpCommit(); }
function tpSetMode(m){
  if(SCS.base==="humbird") SCS.hb.mode=m; else SCS.choice.mode=m;
  SCS.vessel="stirred"; SCS.vmode=null;
  tpTouched(); tpCommit(); }
// the vessel and the way it is run (either may be null: keep the current one). A stirred tank in perfusion or fed-batch is the
// switches' own case; anything else is the vessel table's combination on top of the perfusion case.
function tpSetVM(v,m){
  v=v||SCS.vessel||"stirred"; m=m||tpVMode();
  if(!vmPossible(v,m)) m=VM.morder.slice().reverse().find(x=>vmPossible(v,x));
  const plain=v==="stirred"&&(m==="perfusion"||m==="fedbatch");
  const base=plain?(m==="perfusion"?"perfusion":(tpMode()==="perfusion"?"fedbatch":tpMode())):"perfusion";
  if(SCS.base==="humbird") SCS.hb.mode=base; else SCS.choice.mode=base;
  SCS.vessel=v; SCS.vmode=plain?null:m;
  tpTouched(); tpCommit(); }
function tpSetSize(k){ tpSetMode(k); }
function tpSetDevice(d){ SCS.device=d; tpTouched(); tpCommit(); }
// cleaning the medium: picking a route starts its share at the one that costs least at the settings shown
function tpCleanBest(){ const st=Object.assign({},SCS,{clean:Object.assign({},SCS.clean,{share:null})});
  tpApplyFx(SCS); const r=tpEval(st,tpParamsFor(st)); return r.clean_share||0; }
function tpSetClean(route){ if(!TP.clean.routes[route]) return;
  SCS.clean=Object.assign({},SCS.clean,{route:route,share:null});
  if(route!=="none") SCS.clean.share=tpCleanBest();
  tpTouched(); tpCommit(); }
function tpSetCleanShare(v,live){ if(v===null) v=tpCleanBest(); SCS.clean=Object.assign({},SCS.clean,{share:Math.min(1,Math.max(0,v))}); tpTouched(); if(live) tpLive(); else tpCommit(); }
function tpSetWash(v,live){ SCS.clean=Object.assign({},SCS.clean,{wash:v===null?null:Math.max(0,v)}); tpTouched(); if(live) tpLive(); else tpCommit(); }
function tpSetPlant(v){ if(SCS.base==="humbird") SCS.hb.plant=v; else SCS.choice.plant=v; tpTouched(); tpCommit(); }

/* ---------- the address: the settings in the hash (#tp=...) ---------- */
// the address names a setting of the cells by its traits, never by a kind of cell
const TP_HASHW={selected:"lowlactate", engineered:"lowwaste", measured:"published"}, TP_HASHR={lowlactate:"selected", lowwaste:"engineered", published:"measured"};
function scSettingsHash(){
  if(SCS.ref&&Math.abs(SCS.buyers-tpRef(SCS.ref).buyers)<1e-9) return SCS.ref===TP_START?"":SCS.ref;
  const parts=["from:"+SCS.from,"base:"+SCS.base,"buyers:"+(+SCS.buyers.toFixed(4))];
  if(SCS.ref) parts.push("ref:"+SCS.ref);
  if(SCS.base==="humbird"){ parts.push("hb:"+SCS.hb.mode+"/"+SCS.hb.plant); if(SCS.hbKey!=="humbird") parts.push("hk:"+SCS.hbKey); } else { parts.push("ch:"+SC.keys.map(k=>TP_HASHW[SCS.choice[k]]||SCS.choice[k]).join("/"), "rd:"+(SCS.redesign?1:0));
    if(SCS.choice.extra) parts.push("ex:"+SCS.choice.extra); }      // the case's extra settings (scenarios.EXTRAS)
  Object.keys(SCS.traits).forEach(k=>parts.push("t."+k+":"+(+SCS.traits[k].toPrecision(6))));
  Object.keys(SCS.held).forEach(k=>parts.push("h."+k+":"+(+SCS.held[k].toPrecision(6))));
  if(SCS.vmode) parts.push("vs:"+SCS.vessel+"/"+SCS.vmode);
  if(SCS.device&&SCS.device!=="tff") parts.push("dv:"+SCS.device);
  if(SCS.clean.route!=="none") parts.push("cl:"+SCS.clean.route+(SCS.clean.share===null?"":"/"+(+SCS.clean.share.toFixed(4))));
  if(SCS.clean.wash!==null) parts.push("wp:"+(+SCS.clean.wash.toPrecision(6)));
  return parts.join(",");
}
function scReadHash(v){
  if(!v) return;
  if(tpRef(v)&&tpRef(v).kind!=="company"){ const r=tpRef(v); SCS.ref=v; SCS.from=v; SCS.buyers=r.buyers;
    if(r.kind==="humbird"){ SCS.base="humbird"; SCS.hbKey=v; SCS.hb=Object.assign({},r.hb); SCS.redesign=false; }
    else { SCS.base="switches"; SCS.choice=Object.assign({},r.choice); SCS.redesign=r.redesign; } return; }
  const kv={}; v.split(",").forEach(x=>{ const i=x.indexOf(":"); if(i>0) kv[x.slice(0,i)]=x.slice(i+1); });
  if(tpRef(kv.from)) SCS.from=kv.from;
  SCS.base=kv.base==="humbird"?"humbird":"switches"; SCS.ref=tpRef(kv.ref)?kv.ref:null;
  SCS.hbKey=(tpRef(kv.hk)&&tpRef(kv.hk).kind==="humbird")?kv.hk:"humbird"; SCS.hb=Object.assign({},tpRef(SCS.hbKey).hb);   // a link from before 2026-11-20 has no hk: the perfusion variation
  const b=parseFloat(kv.buyers); if(isFinite(b)) tpSetBuyers(b);
  if(kv.hb){ const [m,p]=kv.hb.split("/"); if(scSetting("mode",m)) SCS.hb.mode=m; if(scSetting("plant",p)) SCS.hb.plant=p; }
  if(kv.ch){ const vals=kv.ch.split("/").map(v=>TP_HASHR[v]||v); SC.keys.forEach((k,i)=>{ if(vals[i]&&scSetting(k,vals[i])) SCS.choice[k]=vals[i]; });
    if(kv.ex&&SC.extras&&SC.extras[kv.ex]) SCS.choice.extra=kv.ex; else delete SCS.choice.extra; }
  SCS.redesign=kv.rd==="1";
  SCS.traits={}; SCS.held={};
  Object.keys(kv).forEach(k=>{ const x=parseFloat(kv[k]); if(!isFinite(x)) return;
    if(k.indexOf("t.")===0&&TRAIT_KEYS.indexOf(k.slice(2))>=0) SCS.traits[k.slice(2)]=x;
    if(k.indexOf("h.")===0&&(["capex_x","medium_price"].indexOf(k.slice(2))>=0||TP_PAR[k.slice(2)])) SCS.held[k.slice(2)]=x; });
  if(kv.vs){ const a=kv.vs.split("/"); if(VM.vessels[a[0]]&&VM.modes[a[1]]&&vmPossible(a[0],a[1])){ SCS.vessel=a[0]; SCS.vmode=a[1]; } }
  if(kv.dv&&MODEL.rt&&MODEL.rt.devices&&MODEL.rt.devices[kv.dv]) SCS.device=kv.dv;
  SCS.clean=tpCleanNone();
  if(kv.cl){ const a=kv.cl.split("/"), sh=parseFloat(a[1]); if(TP.clean.routes[a[0]]&&a[0]!=="none"){ SCS.clean.route=a[0]; SCS.clean.share=isFinite(sh)?Math.min(1,Math.max(0,sh)):null; } }
  if(kv.wp!==undefined){ const w=parseFloat(kv.wp); if(isFinite(w)&&w>=0) SCS.clean.wash=w; }
  SCS.preset=scPresetOf(SCS.choice);
}

/* ---------- the first screen: the controls ---------- */
function tpFmtTrait(k,v){ const T=TP.traits[k], x=v*T.scale; return (k==="doubling_h"?x.toFixed(1).replace(/\.0$/,""):(k==="mass_pg"?x.toFixed(2):x.toFixed(k==="nh3_kg"?3:2)))+" "+T.unit; }
const TP_SHOWN=["humbird_best","today"];        // the starting points offered: Humbird's best estimate (2021), and what has been published for meat cells
const TP_GROUPS=["cells","reactor","medium"];
// the reference values under a lever: chips that set it (MODEL.tp.lever_refs, from build_interactive.LEVER_REFS)
function tpRefChips(key,call,fmt){ const L=(TP.lever_refs||{})[key]; if(!L||!L.length) return "";
  return '<div class="refs">References: '+L.map(r=>'<button type="button" class="chip" onclick="'+call(r[0])+'" title="Set this lever to '+pgEsc(fmt(r[0]))+'"><b>'+pgEsc(fmt(r[0]))+'</b> '+pgEsc(r[1])+'</button>').join("")+'</div>'; }
function tpWhy(text){ return '<details class="why"><summary>What this is</summary><p>'+pgEsc(text)+'</p></details>'; }
function tpBuyersTo(v){ tpSetBuyers(v/100); tpTouched(); tpCommit(); }
function tpParamHTML(q){
  return '<div class="ctl tr"><label for="pp_'+q.key+'"><span class="nm">'+q.name+(q.unit==="×"?"":", "+q.unit)+'</span><span class="q" tabindex="0" data-tip="'+pgEsc(q.help+" The model's source: "+q.source)+'">?</span><span class="val" id="ppv_'+q.key+'"></span></label>'+
    '<input type="range" id="pp_'+q.key+'" min="'+q.min+'" max="'+q.max+'" step="'+q.step+'" aria-describedby="pps_'+q.key+'"><div class="trs" id="pps_'+q.key+'"></div><div class="fxn idlenote" id="ppi_'+q.key+'"></div>'+
    tpRefChips(q.key,v=>"tpSetHeld('"+q.key+"',"+v+",false)",v=>tpFmtParam(q,v).replace(" "+q.unit,""))+tpWhy(q.help+" The model's source: "+q.source)+'</div>'; }
function tpFmtParam(q,v){ return (q.unit==="×"?v.toFixed(2)+"×":(q.unit.charAt(0)==="$"?"$"+v.toLocaleString("en-US",{minimumFractionDigits:q.digits,maximumFractionDigits:q.digits})+q.unit.slice(1):v.toFixed(q.digits)+(q.unit==="%"?"%":" "+q.unit))); }
function tpBuildControls(){
  const refs=document.getElementById("tp_refs");
  if(refs) refs.innerHTML=TP.refs.filter(r=>TP_SHOWN.indexOf(r.key)>=0).map(r=>'<button type="button" class="refbtn" id="ref_'+r.key+'" onclick="tpLoad(\''+r.key+'\')" title="'+pgEsc(r.text)+'">'+r.label+'</button>').join("");
  const host=document.getElementById("tp_traits");
  if(host) host.innerHTML=TRAIT_KEYS.map(k=>{ const T=TP.traits[k];
    return '<div class="ctl tr"><label for="tr_'+k+'"><span class="nm">'+T.name+', '+T.unit+'</span><span class="q" tabindex="0" data-tip="'+pgEsc(T.help+" "+tpBestText(k))+'">?</span><span class="val" id="trv_'+k+'"></span></label>'+
      '<div class="slw"><input type="range" id="tr_'+k+'" min="'+T.min+'" max="'+T.max+'" step="'+T.step+'" aria-describedby="trs_'+k+' trb_'+k+'">'+tpMarkHTML(T.best===null?null:T.best*T.scale,T.min,T.max,"best measured in meat cells")+'</div>'+
      '<div class="trs" id="trs_'+k+'"></div>'+tpRefChips(k,v=>"tpSetTrait('"+k+"',"+(v/T.scale)+",false)",v=>String(v))+tpWhy(T.help+" "+tpBestText(k))+'<p class="sr" id="trb_'+k+'">'+pgEsc(tpBestText(k))+'</p></div>'; }).join("");
  const setH=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  setH("pl_capex_refs",tpRefChips("capex_x",v=>"tpSetHeld('capex_x',"+v+",false)",v=>v+"×").replace('<div class="refs">',"").replace(/<\/div>$/,""));
  setH("pl_med_refs",tpRefChips("medium_price",v=>"tpSetHeld('medium_price',"+v+",false)",v=>"$"+v.toFixed(2)).replace('<div class="refs">',"").replace(/<\/div>$/,""));
  setH("tp_buyers_refs",tpRefChips("buyers",v=>"tpBuyersTo("+v+")",v=>v+"%").replace('<div class="refs">',"").replace(/<\/div>$/,""));
  const cuth=document.getElementById("tp_cuthost");
  if(cuth) cuth.innerHTML='<div class="ctl tr"><label for="tp_cut"><span class="nm">Plant protein in a steak or fillet; the rest is cells</span><span class="q" tabindex="0" data-tip="A steak or fillet is made by binding harvested cells with plant protein. Products on sale are 10 to 30% plant protein and binder. More plant protein makes a cut cheaper, and shoppers like it less. Mince is all cells. The model\'s setting is '+Math.round((1-MODEL.sliders.find(x=>x.key==="cut_cells").default)*100)+'%.">?</span><span class="val" id="tp_cut_v"></span></label>'+
      '<input type="range" id="tp_cut" min="0" max="90" step="5" aria-describedby="tp_cut_s"><p class="fxn" id="tp_cut_s" aria-live="polite"></p>'+tpRefChips("cut",v=>"tpSetCut("+(1-v/100)+",false)",v=>v+"%")+'</div>';
  const mkh=document.getElementById("tp_mkhost");
  if(mkh) mkh.innerHTML='<div class="ctl tr"><label for="tp_mk"><span class="nm">How much conventional meat\'s price falls as it loses sales (supply elasticity)</span><span class="q" tabindex="0" data-tip="As cultivated meat takes sales, farms and packers shrink and conventional meat gets cheaper, which holds cultivated meat\'s share back. The fall is larger the less easily supply shrinks: a supply elasticity of 2 with a demand elasticity of '+C.mk_demand+' lowers the price by about 4% for each 10% of the market taken. Ten-year supply elasticities: cattle 3.2, hogs 1.8, poultry 14 (Brester, Marsh and Atwood 2004).">?</span><span class="val" id="tp_mk_v"></span></label>'+
      '<input type="range" id="tp_mk" min="0.5" max="10" step="0.1" aria-describedby="tp_mk_s"><p class="fxn" id="tp_mk_s" aria-live="polite"></p>'+
      '<div class="refs">References: '+[[0.5,"inelastic supply"],[2,"this model"],[10,"poultry-like supply"]].map(r=>'<button type="button" class="chip" onclick="tpSetMk('+r[0]+',false)"><b>'+r[0]+'</b> '+r[1]+'</button>').join("")+
      '<button type="button" class="chip" onclick="tpSetMk(Infinity,false)"><b>fixed price</b> conventional meat\'s price does not move</button></div></div>'+
      '<div class="ctl tr"><label for="tp_cl"><span class="nm">Share of the meat market it cannot be sold into</span><span class="q" tabindex="0" data-tip="Laws that ban the sale of cultivated meat, weighted by the share of the region\'s people they cover (a stand-in for its share of meat eaten). The model\'s setting counts the permanent bans in five US states.">?</span><span class="val" id="tp_cl_v"></span></label>'+
      '<input type="range" id="tp_cl" min="0" max="30" step="0.5" aria-describedby="tp_cl_s"><p class="fxn" id="tp_cl_s" aria-live="polite"></p>'+
      '<div class="refs">References: '+(TP.lever_refs.closed||[]).map(r=>'<button type="button" class="chip" onclick="tpSetClosedLevel('+r[0]+')"><b id="tp_clref_'+r[0]+'"></b> '+pgEsc(r[1])+'</button>').join("")+'</div></div>';
  TRAIT_KEYS.forEach(k=>{ const e=document.getElementById("tr_"+k); if(!e||!e.addEventListener) return; const T=TP.traits[k];
    e.addEventListener("input",()=>tpSetTrait(k,parseFloat(e.value)/T.scale,true));
    e.addEventListener("change",()=>tpSetTrait(k,parseFloat(e.value)/T.scale,false)); });
  const by=document.getElementById("tp_buyers");
  if(by&&by.addEventListener){ by.addEventListener("input",()=>{ tpSetBuyers(parseFloat(by.value)/100); tpTouched(); tpSchedule(tpRenderFirst); });
    by.addEventListener("change",()=>{ tpSetBuyers(parseFloat(by.value)/100); tpTouched(); tpCommit(); }); }
  const wire=(id,fn)=>{ const e=document.getElementById(id); if(!e||!e.addEventListener) return;
    e.addEventListener("input",()=>fn(parseFloat(e.value),true)); e.addEventListener("change",()=>fn(parseFloat(e.value),false)); };
  TP_GROUPS.forEach(g=>{ const h=document.getElementById("tp_g_"+g); if(h) h.innerHTML=TP.params.filter(q=>q.group===g).map(tpParamHTML).join(""); });
  TP.params.forEach(q=>wire("pp_"+q.key,(v,l)=>tpSetHeld(q.key,v,l)));
  wire("pl_capex",(v,l)=>tpSetHeld("capex_x",v,l)); wire("pl_med",(v,l)=>tpSetHeld("medium_price",v,l));
  const cls=document.getElementById("pl_clean"); if(cls) cls.innerHTML=TP.clean.order.map(k=>'<option value="'+k+'">'+pgEsc(TP.clean.routes[k].name)+'</option>').join("");
  wire("pl_clean_share",(v,l)=>tpSetCleanShare(v/100,l)); wire("pl_wash",(v,l)=>tpSetWash(v,l));
  setH("pl_wash_refs",'References: <button type="button" class="chip" onclick="tpSetWash(null,false)" title="Charge every litre at the price of the medium"><b>the full price</b> every litre as fresh medium; this model</button>'+
    tpRefChips("wash_price",v=>"tpSetWash("+v+",false)",v=>"$"+v.toFixed(3)).replace('<div class="refs">References: ',"").replace(/<\/div>$/,""));
  const vsl=document.getElementById("pl_vessel"); if(vsl) vsl.innerHTML=VM.vorder.map(v=>'<option value="'+v+'">'+VM.vessels[v].name+' ('+vmSize(VM.vessels[v].size).replace(" a unit","")+')</option>').join("");
  const vmd=document.getElementById("pl_vmode"); if(vmd) vmd.innerHTML=VM.morder.map(m=>'<option value="'+m+'">'+VM.modes[m].name+(m==="chemostat"?" (continuous, no cell retention)":(m==="perfusion"?" (continuous, cells held back)":""))+'</option>').join("");
  const dvs=document.getElementById("pl_device"); if(dvs&&MODEL.rt) dvs.innerHTML=MODEL.rt.order.map(d=>'<option value="'+d+'">'+MODEL.rt.devices[d].name.replace(" (the model's default)","")+'</option>').join("");
  ["cmp_vm","cmp_rt"].forEach(id=>{ const d=document.getElementById(id); if(d&&d.addEventListener) d.addEventListener("toggle",()=>{ if(d.open) tpCompareRender(); }); });
  const cd=document.getElementById("calc"); if(cd&&cd.addEventListener) cd.addEventListener("toggle",()=>{ if(cd.open) tpCalcRender(); });
  const un=document.getElementById("unc"); if(un&&un.addEventListener) un.addEventListener("toggle",()=>{ if(un.open) tpUncRender(); });
  wire("tp_cut",(v,l)=>tpSetCut(1-v/100,l));
  wire("tp_mk",(v,l)=>tpSetMk(v,l)); wire("tp_cl",(v,l)=>tpSetClosed(v/100,l));
  try{ const sv=localStorage.getItem("tp_sell_view"); if(sv==="bars"||sv==="disk") PGS.sellView=sv; }catch(e){}
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
  if(document.querySelectorAll) document.querySelectorAll(".q[data-tip]").forEach(q=>{ if(!q.addEventListener) return; const t=()=>q.getAttribute("data-tip");
    q.addEventListener("mouseenter",e=>showTip(e,t())); q.addEventListener("mouseleave",hideTip);
    q.addEventListener("focus",e=>showTip(e,t())); q.addEventListener("blur",hideTip);
    q.addEventListener("click",e=>{ const tp=document.getElementById("tip"); if(tp&&tp.style.display==="block") hideTip(); else showTip(e,t()); }); });
}
// cleaning and reusing the medium: the route, its share and the price of the washing litres, with what they do at these settings
function tpCleanRender(f,p,washed){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; }, show=(id,on)=>{ const e=document.getElementById(id); if(e&&e.style) e.style.display=on?"":"none"; };
  const c=SCS.clean, R=TP.clean.routes[c.route]||TP.clean.routes.none, r=f.cloud.res, m2=v=>"$"+v.toFixed(2);
  const sel=document.getElementById("pl_clean"); if(sel) sel.value=c.route;
  const on=c.route!=="none";
  let why=pgEsc(R.what)+(R.shown?" <b>Shown so far:</b> "+pgEsc(R.shown):"")+(R.limits?" <b>What limits it:</b> "+pgEsc(R.limits):"");
  if(on&&!washed) why+=" <b>It changes nothing here:</b> only a tank whose waste is washed out (perfusion) has spent medium to clean.";
  set("pl_clean_why",why);
  show("pl_clean_share_ctl",on&&washed);
  if(on&&washed){ const sh=(r.clean_share||0)*100, e=document.getElementById("pl_clean_share"); if(e&&document.activeElement!==e) e.value=sh;
    set("pl_clean_share_v",sh.toFixed(0)+"%");
    const none=tpEval(SCS,tpParamsFor(Object.assign({},SCS,{clean:Object.assign({},c,{route:"none",share:null})}))).total, d=none-r.total;
    set("pl_clean_share_s",'<button type="button" class="lnk" onclick="tpSetCleanShare(null,false)">Set the share that costs least</button> '+
      r.clean_loop.toFixed(1)+" litres a kilo of cells are cleaned and returned, so the fresh medium falls from "+r.medium_l_unclean.toFixed(1)+" to "+r.medium_l.toFixed(1)+" litres a kilo. "+
      "The route's equipment costs "+m2(r.clean_capital)+" a kilo of cells and running it "+m2(r.clean_opex)+". "+
      (Math.abs(d)<0.005?"At this share the cost of a kilo of cells is the same as with no cleaning."
        :"At this share a kilo of cells costs "+m2(Math.abs(d))+(d>0?" less":" more")+" than with no cleaning ("+m2(none)+")."));
  }
  const mp=p.medium_price===undefined?0.15:p.medium_price, w=document.getElementById("pl_wash"), wNow=c.wash===null?mp:c.wash;
  if(w&&document.activeElement!==w) w.value=wNow;
  set("pl_wash_v",c.wash===null?"the full price, "+m2(mp)+" a litre":"$"+wNow.toFixed(3)+" a litre");
  const live=r.harvested_share===undefined?1:r.harvested_share, carry=Math.min(r.medium_l,C.fx.medium_l/live), rest=Math.max(0,r.medium_l-carry);
  set("pl_wash_s",(c.wash===null?"":'<button type="button" class="lnk" onclick="tpSetWash(null,false)">Back to the full price</button> ')+
    (rest<0.05?"Every litre here carries nutrients, so this price changes nothing."
      :"Of the "+r.medium_l.toFixed(1)+" litres a kilo of cells, "+carry.toFixed(1)+" carry the nutrients and are charged at "+m2(mp)+"; the other "+rest.toFixed(1)+" only wash waste out and are charged at $"+wNow.toFixed(3)+"."+
        (r.medium_floor?" The nutrients the cells must eat cost more than these litres, so the nutrients set the medium's cost.":"")));
}
// a mark under a slider at value v (a range input's track runs between the thumb's half-widths, about 8 px each side)
function tpMarkHTML(v,min,max,label,id){
  if(v===null||v===undefined||!isFinite(v)) return '<span class="slmark none"'+(id?' id="'+id+'"':'')+'></span>';
  const p=Math.max(0,Math.min(1,(v-min)/(max-min))), al=p<0.15?"l":(p>0.85?"r":"c");
  return '<span class="slmark '+al+'"'+(id?' id="'+id+'"':'')+' style="left:calc(8px + '+(p*100).toFixed(2)+'% - '+(p*16).toFixed(2)+'px)" aria-hidden="true"><i></i><b>'+pgEsc(label)+'</b></span>';
}
// the plant protein in a steak or fillet: a shopper setting (cut_cells), so it changes no cell trait and keeps the reference point
function tpSetCut(c,live){ state.cut_cells=Math.min(1,Math.max(0.1,c)); tpTouched();
  const r=document.getElementById("r_cut_cells"), sl=MODEL.sliders.find(x=>x.key==="cut_cells"); if(r) r.value=state.cut_cells; if(sl&&typeof setReadout==="function") setReadout(sl);
  if(live) tpSchedule(tpRenderFirst); else recompute(); }
// conventional meat's price response and the closed share of the market (meat_market._rollup): the shopper model's own state
function tpSetMk(v,live){ state.mk_supply=v; tpTouched(); if(live) tpSchedule(tpRenderFirst); else recompute(); }
function tpSetClosed(v,live){ state.closed_custom=v; tpTouched(); if(live) tpSchedule(tpRenderFirst); else recompute(); }
function tpSetClosedLevel(lv){ state.closed_level=lv; state.closed_custom=null; tpTouched(); recompute(); }
function tpDismissRead(){ PGS.readDismissed=true; try{ localStorage.setItem("tp_read_off","1"); }catch(e){} const r=document.getElementById("tp_read"); if(r) r.style.display="none"; }
function tpRenderControls(f){
  const set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  TP.refs.forEach(r=>{ const b=document.getElementById("ref_"+r.key); if(b) b.setAttribute("aria-pressed",SCS.ref===r.key?"true":"false"); });
  { const R=tpAddsRef(SCS), box=document.getElementById("tp_adds"), btn=document.getElementById("tp_adds_btn");
    if(box&&box.style) box.style.display=R?"":"none";
    if(R){ const on=tpAddsOn(SCS); if(btn) btn.setAttribute("aria-pressed",on?"true":"false");
      set("tp_adds_text",(on?"<b>Switched on.</b> Click again to put Humbird's values back. ":"Five levers start at Humbird's value, which is none. ")+pgEsc(tpAddsText(tpAddsLive(SCS)))); } }
  set("tp_refnote",SCS.ref?"Loaded: <b>"+tpLabel(SCS.ref)+"</b>. <span class=\"long\">"+pgEsc(tpRef(SCS.ref).text)+"</span>"
     :"Your own settings, started from <b>"+tpLabel(SCS.from)+"</b>. Load a reference point to start again.");
  const tr=tpTraitsShown(), drawn=TP.cloud.wide&&SCS.base!=="humbird";
  TRAIT_KEYS.forEach(k=>{ const T=TP.traits[k], e=document.getElementById("tr_"+k), v=tr[k];
    if(e&&document.activeElement!==e) e.value=v*T.scale;
    set("trv_"+k,tpFmtTrait(k,v));
    const isDrawn=!(k in SCS.traits)&&drawn&&(k==="mass_pg"||(k==="nh3_kg"&&(SCS.choice.cells==="selected"||SCS.choice.cells==="measured")));
    const q=TP.cloud.priors[k==="mass_pg"?"sc_mass_selected_pg":"sc_nh3_selected"];
    set("trs_"+k,
      ((k in SCS.traits)?'<button type="button" class="lnk" onclick="tpFreeTrait(\''+k+'\')">Back to '+tpLabel(SCS.from)+'</button>':"")); });
  // the plant
  const mode=tpMode(), fb=mode!=="perfusion", plant=tpPlant();
  const sz=document.getElementById("pl_size"), ps=document.getElementById("pl_plant");
  const vNow=SCS.vessel||"stirred", mNow=tpVMode(), plainFb=vNow==="stirred"&&mNow==="fedbatch";
  if(sz&&plainFb) sz.value=mode; if(ps) ps.value=plant;
  const show=(id,on)=>{ const e=document.getElementById(id); if(e&&e.style) e.style.display=on?"":"none"; };
  show("pl_size_ctl",false);       // the tank's size is a lever of its own (tank_m3)
  const p=tpParams(), hd=SCS.held, washed=tpWashed(p), ownRet=!!(p.vm&&p.vm.own_retention);
  const vsl=document.getElementById("pl_vessel"); if(vsl) vsl.value=vNow;
  const vmd=document.getElementById("pl_vmode"); if(vmd){ vmd.value=mNow;
    if(vmd.options) Array.prototype.forEach.call(vmd.options,o=>{ o.disabled=!vmPossible(vNow,o.value); }); }
  const V=VM.vessels[vNow], Mo=VM.modes[mNow], tag=VM.tags[vNow+"|"+mNow];
  set("pl_vessel_s",pgEsc(V.what)+" "+pgEsc(V.limits||""));
  set("pl_vmode_s",pgEsc(Mo.what)+(tag?" <b>"+pgEsc(tag[0].charAt(0).toUpperCase()+tag[0].slice(1))+"</b>: "+pgEsc(tag[1]):""));
  show("pl_device_ctl",washed&&!ownRet);
  const dvs=document.getElementById("pl_device"), dev=SCS.device||"tff"; if(dvs) dvs.value=dev;
  if(MODEL.rt&&washed&&!ownRet){ const D=MODEL.rt.devices[dev], rc=dev==="tff"?null:rtCost(dev,p);
    set("pl_device_s",pgEsc(tpCap(D.how))+". Shown so far: "+pgEsc(D.shown)+"."+
      (rc&&rc.impossible?" <b>Not possible at these settings:</b> "+pgEsc(rc.impossible):"")+
      (rc&&rc.beyond?" <b>This culture is denser than the device has been shown to hold.</b>":"")+
      (rc&&rc.loss>0?" It destroys or lets go "+(rc.loss*100).toFixed(1)+"% of the cells grown.":"")); }
  TP.params.forEach(q=>{ const e=document.getElementById("pp_"+q.key), d0=tpParamDefault(q,scWithExtra(Object.assign({},SCS.traits),()=>tpParamsFor(Object.assign({},SCS,{held:{}})))), v=hd[q.key]===undefined?d0:hd[q.key];
    if(e&&document.activeElement!==e) e.value=v;
    let extra="";
    if(q.key==="o2x"){ const rr=f.cloud.res, td=tpTraitsShown(); extra=" With your cells: "+(rr.o2_kg*Math.LN2/td.doubling_h*td.mass_pg*1e-12*1e9*24).toFixed(1)+" pmol of oxygen a cell a day ("+rr.o2_kg.toFixed(0)+" mol a kilo of cells grown)."; }
    if(q.kind==="fin"){ const F=tpFin(SCS), i=(hd.fin_rate===undefined?F.rate:hd.fin_rate)/100, n=hd.fin_life===undefined?F.life:hd.fin_life, pay=(i>1e-9?i/(1-Math.pow(1+i,-n)):1/n)*100, ch=tpFinCharge(hd,SCS)*100;
      extra=q.key==="fin_upkeep"?" Yearly charge on the plant: "+pay.toFixed(1)+"% to pay it back with interest + "+(ch-pay).toFixed(1)+"% = "+ch.toFixed(1)+"% of what it cost to build.":(q.key==="fin_rate"?" With the years below, the yearly payment is "+pay.toFixed(1)+"% of the plant's cost.":""); }
    if(q.key==="mem_price"||q.key==="mem_life") extra=" Price over life: $"+((hd.mem_price===undefined?tpFx0("tff.mem_price"):hd.mem_price)/(hd.mem_life===undefined?(p.membrane_life||tpFx0("tff.mem_life")):hd.mem_life)).toFixed(2)+" of membrane for each litre filtered.";
    set("ppv_"+q.key,tpFmtParam(q,v));
    set("pps_"+q.key,(hd[q.key]===undefined?"":'<button type="button" class="lnk" onclick="tpFreeHeld(\''+q.key+'\')">Back to '+tpFmtParam(q,d0)+'</button>')+extra); });
  { const rr=f.cloud.res, mp=p.medium_price===undefined?0.15:p.medium_price, byL=rr.medium_l*mp, fl=!!rr.medium_floor;
    set("pl_med_why",fl?"<b>The ingredients set the medium's cost here:</b> the cells must eat $"+rr.nutrients.toFixed(2)+" of amino acids, sugar and salts a kilo, more than "+rr.medium_l.toFixed(0)+" litres at $"+mp.toFixed(2)+" ($"+byL.toFixed(2)+"). The prices under “What the medium is made of” are in use."
      :"<b>The price a litre sets the medium's cost here:</b> "+rr.medium_l.toFixed(0)+" litres × $"+mp.toFixed(2)+" = $"+byL.toFixed(2)+" a kilo of cells. Its ingredients alone would cost $"+rr.nutrients.toFixed(2)+". The model takes the larger of the two, never their sum, so the prices of amino acids and glucose below change nothing until the ingredients cost more than the litres.");
    ["aa_price","glucose_price"].forEach(k=>{ const e=document.getElementById("pp_"+k), c=e&&e.parentNode; if(c&&c.classList) c.classList.toggle("idle",!fl); set("ppi_"+k,fl?"":"Not in use at these settings: the price a litre sets the medium's cost."); }); }
  tpCleanRender(f,p,washed);
  tpCellsRender(f); tpCompareRender();
  const cx=document.getElementById("pl_capex"); if(cx&&document.activeElement!==cx) cx.value=hd.capex_x===undefined?1:hd.capex_x;
  const r0=f.cloud.res;
  set("pl_capex_v","$"+Math.round(r0.capex).toLocaleString("en-US")+"k per m³ of tank ("+(hd.capex_x===undefined?1:hd.capex_x).toFixed(2)+"× the model's estimate)");
  const other=Object.assign({},SCS,{choice:Object.assign({},SCS.choice,{mode:fb?"perfusion":"fedbatch"}),hb:Object.assign({},SCS.hb,{mode:fb?"perfusion":"fedbatch"})});
  const otherCost=tpEval(SCS,tpParamsFor(Object.assign(other,{vessel:"stirred",vmode:null}))).total;
  set("pl_capex_s",(hd.capex_x===undefined?'':'<button type="button" class="lnk" onclick="tpFreeHeld(\'capex_x\')">Let it vary again</button> ')+
    'At these settings, every estimate at its most likely value: '+scMoney(f.point)+' a kilo of cells; in a stirred tank run '+(fb?'in perfusion':'as a 20 m³ fed-batch')+' instead, '+scMoney(otherCost)+'.');
  const md=document.getElementById("pl_med"), medNow=hd.medium_price===undefined?(p.medium_price===undefined?0.15:p.medium_price):hd.medium_price;
  if(md&&document.activeElement!==md) md.value=medNow;
  const mlGrown=r0.medium_l*(r0.harvested_share===undefined?1:r0.harvested_share);   // nutrients are per kilo of cells grown, so are these litres (medium_l is per kilo harvested)
  const flL=r0.nutrients/mlGrown, flT="$"+(flL<0.1?flL.toFixed(3):flL.toFixed(2));
  set("pl_med_v",(medNow<0.005?"at the nutrient floor":"$"+medNow.toFixed(2)+" a litre")+" (nutrient floor "+flT+" a litre)");
  const mk=document.getElementById("pl_med_mark"); if(mk) mk.outerHTML=tpMarkHTML(flL,0,0.60,"nutrient floor "+flT,"pl_med_mark");
  const mq=document.getElementById("pl_med_q"); if(mq&&mq.setAttribute) mq.setAttribute("data-tip","The nutrient liquid the cells grow in. Companies announce $0.20 a litre and report $0.30 to $0.50, with growth factors in that price. "+
    "The nutrient floor is what the cells must eat: $"+r0.nutrients.toFixed(2)+" a kilo of cells (amino acids, "+Math.round(TP.cloud.aa_intensity*1000)+" g at $"+(C.fx.aa/TP.cloud.aa_intensity).toFixed(2)+" a kilo, feed grade, GFI December 2025, $"+C.fx.aa.toFixed(2)+
    "; glucose, $"+(r0.nutrients-C.fx.aa-C.fx.other).toFixed(2)+", more for cells that burn more; salts, buffer and vitamins, $"+C.fx.other.toFixed(2)+"), "+
    "over the "+mlGrown.toFixed(1)+" litres a kilo of cells grown needs here: "+flT+" a litre. It moves with the cells' traits. Growth factors are on top of it.");
  set("pl_med_s",(hd.medium_price===undefined?'':'<button type="button" class="lnk" onclick="tpFreeHeld(\'medium_price\')">Let it vary again</button> ')+
    "The nutrient floor: the $"+r0.nutrients.toFixed(2)+" of nutrients a kilo of cells must eat, over the "+mlGrown.toFixed(0)+" litres it takes to grow here, is "+flT+" a litre; growth factors are on top of it. "+
    (r0.medium_floor?"Below it the medium costs the floor, so the floor sets it here.":""));
  // the plant protein in a steak or fillet (the shopper model's cut_cells, also under The shopper model in detail)
  const ct=document.getElementById("tp_cut"), cpp=Math.round((1-state.cut_cells)*100); if(ct&&document.activeElement!==ct) ct.value=cpp;
  set("tp_cut_v",cpp+"%");
  { const es=state.mk_supply===undefined?C.mk_supply:state.mk_supply, mk=document.getElementById("tp_mk");
    if(mk&&document.activeElement!==mk) mk.value=isFinite(es)?es:10;
    set("tp_mk_v",isFinite(es)?es.toFixed(1):"fixed price");
    const P=penetration(Object.assign({},state,{cost_override:f.cost,lmean:tpLmean(f.buyers)}));
    set("tp_mk_s",isFinite(es)?"At this cost conventional meat's prices here end "+((1-P.conv_f)*100).toFixed(1)+"% lower than the prices the model starts from, which holds the share back.":"Conventional meat's prices are held at the prices the model starts from.");
    const cl=closedShare(state), ce=document.getElementById("tp_cl"); if(ce&&document.activeElement!==ce) ce.value=(cl*100).toFixed(1);
    set("tp_cl_v",(cl*100).toFixed(1)+"%");
    const cls=C.closed[state.region]||[]; for(let lv=0;lv<cls.length;lv++) set("tp_clref_"+lv,(cls[lv]*100).toFixed(1)+"%");
    set("tp_cl_s","Every share of "+tpRegionMeat()+" on this screen is of the whole market, "+(cl*100).toFixed(1)+"% of which it cannot be sold into."); }
  const cc=cutCost(f.cost,state);
  set("tp_cut_s","A kilo of steak or fillet: "+(100-cpp)+"% cells at "+tpUSD(f.cost)+" a kilo"+(cpp?", "+cpp+"% plant protein at $"+C.matrix_price.toFixed(2)+" a kilo":"")+
    ", and "+scMoney(state.scaffold)+" to assemble it: "+scMoney(cc)+" before it reaches the shelf. Mince is all cells. Every figure on this screen follows it.");
  set("pl_design",SCS.base==="humbird"?"Humbird's design has no tank tricks: gas bubbled in at the base of an ordinary tall tank."
    :"The tank design: "+scSetting("tricks",SCS.choice.tricks).label.charAt(0).toLowerCase()+scSetting("tricks",SCS.choice.tricks).label.slice(1)+"; "+
     scSetting("shape",SCS.choice.shape).label.charAt(0).toLowerCase()+scSetting("shape",SCS.choice.shape).label.slice(1)+". "+
     (SCS.redesign?"Chosen again whenever the cells or the plant change: the cheapest design that passes the checks on the CO₂ loop.":"Kept as set: Published cells keep an ordinary tall tank with no tricks, and a design you pick under How the tank and the plant set the cost stays."));
  const by=document.getElementById("tp_buyers"); if(by&&document.activeElement!==by) by.value=(SCS.buyers*100).toFixed(1);
  set("tp_buyers_v",tpPctB(SCS.buyers));
  const lm=tpLmean(SCS.buyers), at=R=>shareCalc(R,KP,{ax:state.accept_x,tfM:state.theta_free_M,income:C.income_ref,nbx:state.neophobia_x,hx:state.health_x,lmean:lm,which:"x_meat"})*100;
  const free=at(0);
  set("tp_buyers_read","If it cost half as much as meat, "+at(0.5).toFixed(0)+"% of meat buyers would pick it; if it were free, "+free.toFixed(0)+"%, so "+(100-free).toFixed(0)+
    "% would not take it at any price. Nobody has measured this. Surveys run from about 5% to 60%. The page starts at "+tpPctB(tpRef(TP_START).buyers)+
    ", the model's reading of the one choice experiment with prices; 50% means no preference between it and conventional meat.");
  const sel=document.getElementById("regionsel"); if(sel) sel.value=state.region;
}

/* ---------- section 1's result: what the cells allow in the tank (the engine's own limits and litres) ---------- */
const TP_LIMW={"oxygen supply":"getting oxygen in","CO2 removal":"clearing CO₂","mixing":"mixing","thickness of the culture":"how thick a culture can be and still flow",
  "waste build-up":"ammonia and lactate building up (nothing washes them out)","other by-products":"other by-products building up","food in one fill":"the food in one fill of medium"};
const TP_TERMW={"ammonia":"washing out ammonia","lactate":"washing out lactate","least flow":"the least flow the cells need","harvest":"the liquid that leaves with the cells",
  "nutrients":"carrying the nutrients","salt":"keeping the salt strength down"};
function tpCellsRender(f){
  const host=document.getElementById("tp_cellres"); if(!host) return;
  const r=f.cloud.res, tr=tpTraitsShown(), lw=k=>TP_LIMW[k]||(typeof VM!=="undefined"&&VM.limit_plain[k])||k;
  const cells=r.density/(tr.mass_pg*1e-12)/1000, lims=Object.keys(r.limits).map(k=>[k,r.limits[k]]).filter(x=>isFinite(x[1])).sort((a,b)=>a[1]-b[1]);
  const terms=Object.keys(r.medium_terms||{}).map(k=>[k,r.medium_terms[k]]).sort((a,b)=>b[1]-a[1]);
  const qo2=r.o2_kg*Math.LN2/tr.doubling_h;     // mmol of oxygen a gram of cells an hour
  host.innerHTML='<div class="cellres"><div><span class="big">'+r.density.toFixed(0)+' g of cells a litre</span>'+
    'the densest this tank can run ('+(cells/1e6).toFixed(0)+' million cells a mL), limited by '+pgEsc(lw(r.limit))+'.'+
    '<ul>'+lims.slice(0,5).map(x=>'<li'+(x[0]===r.limit?' class="on"':'')+'>'+pgEsc(tpCap(lw(x[0])))+': '+x[1].toFixed(0)+' g a litre</li>').join("")+'</ul></div>'+
    '<div><span class="big">'+r.medium_l.toFixed(0)+' litres of medium a kilo of cells</span>'+
    (terms.length?'set by '+pgEsc(TP_TERMW[r.medium_set_by]||r.medium_set_by)+'.<ul>'+terms.map(x=>'<li'+(x[0]===r.medium_set_by?' class="on"':'')+'>'+pgEsc(tpCap(TP_TERMW[x[0]]||x[0]))+': '+x[1].toFixed(1)+' litres</li>').join("")+'</ul>':'as set.')+'</div>'+
    '<div><span class="big">'+(r.output).toFixed(1)+' tonnes a year from each m³ of tank</span>'+
    'The cells make '+r.nh3_kg.toFixed(3)+' mol of ammonia and '+r.lac_kg.toFixed(1)+' mol of lactate a kilo, and use '+qo2.toFixed(3)+' mmol of oxygen a gram an hour ('+
    (qo2*tr.mass_pg*1e-12*1e9*24).toFixed(1)+' pmol a cell a day). The tank is in use '+(r.uptime*100).toFixed(0)+'% of the time.</div></div>'+
    '<p class="small">Every figure here is calculated from your settings, with each estimate at its most likely value. The costs follow in the next sections.</p>';
}
/* ---------- section 2's comparisons: every vessel and mode, and every retention device, at the reader's settings ---------- */
function tpCompareRender(){
  const dv=document.getElementById("cmp_vm"), dr=document.getElementById("cmp_rt");
  if(dv&&dv.open){ const base=tpParamsFor(Object.assign({},SCS,{vessel:"stirred",vmode:null,choice:Object.assign({},SCS.choice,{mode:"perfusion"}),hb:Object.assign({},SCS.hb,{mode:"perfusion"})}));
    const vN=SCS.vessel||"stirred", mN=tpVMode();
    const head='<thead><tr><th>Vessel ↓ &nbsp; How it is run →</th>'+VM.morder.map(m=>'<th>'+VM.modes[m].name+'</th>').join("")+'</tr></thead>';
    const sN=SCS.held.tank_m3===undefined?null:SCS.held.tank_m3, big=VM.tag_order[2];
    const row=(v,size)=>{ const V=VM.vessels[v], b2=Object.assign({},base); if(v==="stirred") delete b2.vessel_m3;
      return '<tr><th>'+V.name+'<br><span class="alt">'+vmSize(size||V.size)+'</span></th>'+VM.morder.map(m=>{ const c=tpAtSize(size,()=>vmCell(v,m,b2));
        const on=(v===vN&&m===mN&&(v!=="stirred"||(size||20)===(sN||20)))?" on":"";
        if(!c.possible) return '<td class="vno'+on+'"><span class="alt">Not possible</span></td>';
        if(c.same_as) return '<td class="vsame'+on+'"><span class="alt">As batch</span></td>';
        return '<td class="pick'+on+'" onclick="tpPickVM(\''+v+'\',\''+m+'\','+(size||0)+')" title="'+pgEsc(size?"Animal cells have not been grown in a tank this large.":c.evidence)+'"><b>'+vmMoney(c.cost)+'</b><br><span class="alt">'+c.density.toFixed(0)+' g/L, limited by '+pgEsc(VM.limit_plain[c.limit]||c.limit)+'</span><br>'+vmTagChip(size?big:c.tag)+'</td>'; }).join("")+'</tr>'; };
    const rows=VM.vorder.map(v=>row(v,null)+(v==="stirred"?TP_SIZES.map(z=>row(v,z)).join(""):"")).join("");
    document.getElementById("tp_vmgrid").innerHTML='<div class="scrollx"><table class="sctab vmtab">'+head+'<tbody>'+rows+'</tbody></table></div>'+
      '<p class="small">The tag says whether animal cells have been grown this way at this size. The stirred tank is shown at 20, 50 and 100 m³; the lever “Size of a stirred tank” takes any size from 4 to 250 m³.</p>'; }
  if(dr&&dr.open&&MODEL.rt){ const p=tpParamsFor(Object.assign({},SCS,{vessel:"stirred",vmode:null,choice:Object.assign({},SCS.choice,{mode:"perfusion"}),hb:Object.assign({},SCS.hb,{mode:"perfusion"})}));
    const rows=MODEL.rt.order.map(d=>{ const D=MODEL.rt.devices[d], c=rtCost(d,p), on=(SCS.device||"tff")===d?' class="on"':'';
      return '<tr'+on+'><td class="pick" onclick="tpSetDevice(\''+d+'\')"><b>'+pgEsc(D.name.replace(" (the model's default)",""))+'</b><br><span class="alt">'+pgEsc(D.how)+'</span></td>'+
        '<td class="num"><b>'+(c.impossible?"not possible":vmMoney(c.total))+'</b>'+(c.beyond?'<br><span class="alt">denser than it has held</span>':'')+'</td>'+
        '<td class="num">$'+Math.round(c.capex_k_m3)+'k</td><td class="num">'+vmMoney(c.cons_kg)+'</td><td class="num">'+(c.loss*100).toFixed(1)+'%</td><td><span class="alt">'+pgEsc(D.shown)+'</span></td></tr>'; }).join("");
    const more=Object.keys(MODEL.rt.particles||{}).map(k=>'<li><b>'+pgEsc(MODEL.rt.particles[k].name)+'</b>: '+pgEsc(MODEL.rt.particles[k].how)+'. Priced in the Python model (retention.py), not on this page.</li>').join("")+
      Object.keys(MODEL.rt.not_costed||{}).map(k=>'<li><b>'+pgEsc(MODEL.rt.not_costed[k].name)+'</b>: not priced. '+pgEsc(MODEL.rt.not_costed[k].reason)+'</li>').join("");
    document.getElementById("tp_rtgrid").innerHTML='<div class="scrollx"><table class="sctab"><thead><tr><th>Device</th><th>Cost of a kilo of cells</th><th>Its capital, per m³ of tank</th><th>Its running cost, a kilo</th><th>Cells lost</th><th>Shown so far</th></tr></thead><tbody>'+rows+'</tbody></table></div>'+
      '<p class="small">In a stirred tank in perfusion, with your other settings.</p><ul class="small">'+more+'</ul>'; }
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
  const L=small?50:62, R=W-(small?10:18), T=small?64:70, B=H-(small?44:46);
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
  const meats=tpMeats().filter(m=>m.parity>TPM.x0&&m.parity<TPM.x1);
  meats.forEach(m=>{ g+='<line x1="'+lx(m.parity).toFixed(1)+'" x2="'+lx(m.parity).toFixed(1)+'" y1="'+T+'" y2="'+B+'" stroke="#fff" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.8"/>'; });
  // your point's range for 8 in 10 draws: a thin whisker across its cost, under everything else
  const yp=ly(f.buyers), cl=f.cloud, wa=lx(Math.min(TPM.x1,Math.max(TPM.x0,f.cb[0]))), wb=lx(Math.min(TPM.x1,Math.max(TPM.x0,f.cb[2]))), tip=pgEsc(tpVariedTip());
  if(wb-wa>1) g+='<g class="mwh"><title>'+tip+'</title><path d="M'+wa.toFixed(1)+' '+(yp-6).toFixed(1)+' V'+(yp+6).toFixed(1)+' M'+wa.toFixed(1)+' '+yp.toFixed(1)+' H'+wb.toFixed(1)+' M'+wb.toFixed(1)+' '+(yp-6).toFixed(1)+' V'+(yp+6).toFixed(1)+'" fill="none" stroke="#fff" stroke-width="4" stroke-opacity="0.7"/>'+
     '<path d="M'+wa.toFixed(1)+' '+(yp-6).toFixed(1)+' V'+(yp+6).toFixed(1)+' M'+wa.toFixed(1)+' '+yp.toFixed(1)+' H'+wb.toFixed(1)+' M'+wb.toFixed(1)+' '+(yp-6).toFixed(1)+' V'+(yp+6).toFixed(1)+'" fill="none" stroke="#1a1a19" stroke-width="1.6"/></g>';
  g+='</g>';
  // Labels that do not depend on your point are placed first, in a fixed order, so that moving your point (the meat-buyers slider
  // moves it up and down) never moves them: the zones, every reference point (the one loaded keeps its place, unlabelled, under your
  // point), the lines of equal share. Your point's label goes last, wherever it fits.
  const labs=[], fs=small?11:12, short=t=>small?t.replace(", all favourable","").replace("Humbird's optimistic design","Humbird's design").replace("Humbird's best estimate (2021)","Humbird's best estimate"):t;
  const zf=11;
  const zl=[[lx(fl)+zf+2,B-6,small?"floor: what cells eat":"$"+fl.toFixed(2)+" floor: what the cells must eat","start"],
            [lx(fr)+zf+2,T+6,small?"every lever at its limit":"$"+fr.toFixed(2)+": every lever at its limit","end"],
            ];
  zl.forEach(([x,y,t,a])=>{ const c=pl.tryPut([{x:x,y:y,t:t,fs:zf,anchor:a,rot:true}],[L,T,R,B]); if(c) labs.push(tpLabelSVG(c)); });
  const dots=[];        // no reference points here: a published cost says nothing about shoppers, so it has no height on this map
  dots.forEach(d=>{ pl.block(d.x-5,d.y-5,d.x+5,d.y+5); });
  dots.forEach(d=>{ const t=d.lab;
    const rf=Math.max(11,fs-1);
    const c=pl.tryPut([{x:d.x+8,y:d.y-7,t:t,fs:rf},{x:d.x-8,y:d.y-7,t:t,fs:rf,anchor:"end"},{x:d.x+8,y:d.y+15,t:t,fs:rf},{x:d.x-8,y:d.y+15,t:t,fs:rf,anchor:"end"},
                       {x:d.x+8,y:d.y-20,t:t,fs:rf},{x:d.x-8,y:d.y+28,t:t,fs:rf,anchor:"end"}],within);
    if(c&&d.key!==SCS.ref) labs.push(tpLabelSVG(c));
    if(d.key!==SCS.ref) g+='<circle class="rd" cx="'+d.x.toFixed(1)+'" cy="'+d.y.toFixed(1)+'" r="'+(small?3.4:4)+'"/>'; });
  if(G){ const ord=[1,10,0.1,30,0.01,50], fracs=[0.35,0.3,0.42,0.25,0.5,0.2,0.58,0.15,0.66,0.72,0.8];
    ord.forEach(Lv=>{ const pts=lines[Lv]; if(!pts||pts.length<2) return; if(small&&(Lv===0.01||Lv===50||Lv===30)) return;
      const t=(Lv<1?String(Lv):Lv)+"%", cands=[];
      (Lv>=30?[0.8,0.9,0.72,0.62]:fracs).forEach(fy=>{ const q=pts.reduce((a,b)=>Math.abs(b[1]-fy)<Math.abs(a[1]-fy)?b:a);
        cands.push({x:lx(q[0])+5,y:ly(q[1])+4,t:t,fs:fs}); cands.push({x:lx(q[0])-5,y:ly(q[1])+4,t:t,fs:fs,anchor:"end"}); });
      const c=pl.tryPut(cands,within); if(c) labs.push(tpLabelSVG(c)); }); }
  // your point and its label, last
  const px=lx(Math.min(TPM.x1,Math.max(TPM.x0,f.cost)));
  const meDot='<circle class="me" cx="'+px.toFixed(1)+'" cy="'+yp.toFixed(1)+'" r="'+(small?6:7)+'"><title>'+tip+'</title></circle>'; pl.block(px-8,yp-8,px+8,yp+8);
  const meLab=f.key==="own"?"Your settings":short(f.label);
  const meC=[]; [[-10,22],[-24,36],[-38,50],[-52,64],[-66,78],[-80,92]].forEach(([u,d])=>{ meC.push({x:px+11,y:yp+u,t:meLab,fs:fs+1,anchor:"start"},{x:px-11,y:yp+u,t:meLab,fs:fs+1,anchor:"end"},
    {x:px+11,y:yp+d,t:meLab,fs:fs+1,anchor:"start"},{x:px-11,y:yp+d,t:meLab,fs:fs+1,anchor:"end"},{x:px,y:yp+u,t:meLab,fs:fs+1,anchor:"middle"},{x:px,y:yp+d,t:meLab,fs:fs+1,anchor:"middle"}); });
  const me=pl.tryPut(meC,within)||pl.tryPut(meC.map(c=>Object.assign({},c,{fs:fs})),within)||pl.tryPut(meC.map(c=>Object.assign({},c,{fs:fs})),[2,T-30,W-2,B])||meC[0];
  if(me) labs.push(tpLabelSVG(me,"mb"));
  g+=labs.join("")+meDot;
  // axes
  const xt=small?[2,5,10,20,50,100,400]:[2,5,10,20,50,100,200,400];
  xt.forEach(v=>{ const tw=tpTextW("$"+v,11), xc=Math.min(W-2-tw/2,lx(v)); g+='<line x1="'+lx(v).toFixed(1)+'" x2="'+lx(v).toFixed(1)+'" y1="'+B+'" y2="'+(B+5)+'" '+mut+'/><text x="'+xc.toFixed(1)+'" y="'+(B+18)+'" text-anchor="middle" font-size="11">$'+v+'</text>'; });
  g+='<text x="'+((L+R)/2)+'" y="'+(B+36)+'" text-anchor="middle" font-size="12">Cost to grow a kilo of cells (log scale)</text>';
  // along the top: the cost of cells at which it sells at each kind of meat's own shop price (staggered so the names do not collide)
  let lastTop=-1e9, row=0; meats.forEach(m=>{ const x=lx(m.parity), t=(small?m.plain.replace(/ \(.*\)/,""):m.plain)+" $"+m.price.toFixed(m.price>=20?0:2), w=tpTextW(t,11);
    row=(x-w/2<lastTop+6)?(row+1)%3:0; const y=T-9-row*13, xc=Math.max(L+w/2,Math.min(R-w/2,x));
    g+='<line x1="'+x.toFixed(1)+'" x2="'+x.toFixed(1)+'" y1="'+(y+3)+'" y2="'+T+'" '+mut+'/><text x="'+xc.toFixed(1)+'" y="'+y+'" text-anchor="middle" font-size="11">'+pgEsc(t)+'</text>'; lastTop=xc+w/2; });
  g+='<text x="'+((L+R)/2)+'" y="'+(T-(small?46:48))+'" text-anchor="middle" font-size="'+(small?11:12)+'">'+(small?'Same shop price as (a kilo):':'The cost at which it would sell at the shop price of each kind of meat (a kilo, in '+pgRegionName()+')')+'</text>';
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
  return "Cells at "+tpUSD(cx)+" a kilo (shop price "+tpUSD(shop)+", "+(shop/tpMeats()[0].price).toFixed(1)+" times the price of "+tpMeats()[0].plain+"), "+tpPctB(cy)+
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
  set("tp_read_txt","<b>How to read the map.</b> Each orange line joins the points with the same share. To the right of the 1% line cultivated meat stays below 1% of the meat sold. To cross it with "+tpPctB(f.buyers)+
    " of meat buyers picking it at the same price, cells must cost under about "+(one===null?"(out of reach)":tpUSDk(one))+" a kilo; for 10%, under about "+(ten===null?"$0.5: out of reach":tpUSDk(ten))+
    ". Your point sits at "+tpUSD(f.cost)+". "+
    "Up the map, more shoppers like it; to the left, cells are cheaper. The lines of equal share do not move with the meat-buyers slider: it moves your point up and down. "+
    "<b>The dashed lines</b> mark the cost of cells at which it would sell at the shop price of each kind of meat named along the top. For one kind of meat at its own price, the share of its buyers who pick the cultivated one is your setting exactly (the chart above). This map adds up every kind of meat at one cost of cells, each at its own price, so its lines of equal share cross each dashed line below that setting for the dearer meats to its right and above it for the cheaper ones.");

  const rd=document.getElementById("tp_read"); if(rd) rd.style.display=PGS.readDismissed?"none":"";
  set("tp_map_region",pgRegionName());
  const mq=document.getElementById("tp_map_wq"); if(mq&&mq.setAttribute) mq.setAttribute("data-tip",tpVariedTip());
  tpHoverReset();
  const tb=document.getElementById("tp_table");
  if(tb&&G){ const cs=[3,5,10,20,40,80,150,300], bs=[0.05,0.145,0.25,0.5,0.75,0.95];
    tb.innerHTML='<table class="num"><thead><tr><th rowspan="2">Cost of cells, a kilo</th><th colspan="'+bs.length+'">Meat buyers who would pick it at the same price</th></tr><tr>'+bs.map(b=>'<th>'+tpPctB(b)+'</th>').join("")+'</tr></thead><tbody>'+
      cs.map(c=>'<tr><td>$'+c+'</td>'+bs.map(b=>'<td>'+pgPctS(tpInterp(c,b))+'</td>').join("")+'</tr>').join("")+'</tbody></table>'+
      '<p class="note">Long-run share of '+pgRegionOf()+' meat and seafood, read from the map\'s grid, at the shopper settings as set.</p>'; }
  set("tp_alt","Upright lines: the nutrient floor ($"+C.FEEDSTOCK_FLOOR.toFixed(2)+" a kilo of cells: cells grown on a medium cannot cost less), the cost at which it would sell at the shop price of each kind of meat ("+tpAnd(tpMeats().map(m=>m.plain+" "+tpUSD(m.parity)))+", dashed), and every lever at its limit ($"+TP.frontier.toFixed(2)+"). The map shades the long-run share of "+pgRegionOf()+" meat and seafood for every cost of cells (across) and every share of meat buyers who would pick it at the same price (up). "+
    "Your point: "+tpUSD(f.cost)+" and "+tpPctB(f.buyers)+", a share of "+pgPctS(f.share)+".");
}
// three figures that stay in view while any slider moves: the cost, the shop price against two named meats, the long-run share
function tpSummaryHTML(f){
  const ms=tpMeats(), a=ms[0], b=ms.find(m=>/steak/i.test(m.name))||ms[ms.length-1], r=f.cloud.res, x=m=>{ const q=m.shop(f.cost)/m.price; return (q>=9.5?q.toFixed(0):q.toFixed(1))+"×"; };
  const mince=shelfPrice(f.cost,state);
  return '<p class="sumlab">At your settings</p><div><b>'+tpUSD(f.cost)+'</b><span>to grow a kilo of cells ('+r.density.toFixed(0)+' g a litre, '+r.medium_l.toFixed(0)+' litres of medium a kilo)</span></div>'+
    '<div><b>'+tpUSD(mince)+'</b><span>a kilo in the shop as mince ('+x(a)+' '+pgEsc(a.plain)+'); <b class="in">'+tpUSD(b.shop(f.cost))+'</b> as a steak or fillet with '+Math.round((1-state.cut_cells)*100)+'% plant protein ('+x(b)+' '+pgEsc(b.plain)+')</span></div>'+
    '<div><b>'+(f.share<0.00095?"under 0.001%":tpPct2(f.share))+'</b><span>of '+tpRegionMeat()+' in the long run, if '+tpPctB(f.buyers)+' of meat buyers pick it at the same price</span></div>';
}
// "how uncertain is this cost": only when the reader opens it, the estimates nobody has measured are varied over the ranges listed
function tpUncRender(){
  const d=document.getElementById("unc"), host=document.getElementById("tp_unc"); if(!d||!host||!d.open) return;
  const cl=tpCloudFor(SCS), P=TP.cloud.priors, M=TP.cloud.mc, h=tpHeld(SCS), tr=SCS.traits, p=tpParams(), isScen=SCS.base!=="humbird";
  const perf=tpWashed(p)&&(SCS.device||"tff")==="tff"&&!(p.vm&&p.vm.own_retention), base=p.medium_price===undefined?0.15:p.medium_price;
  const n=(v,d)=>(+v).toLocaleString("en-US",{maximumFractionDigits:d});
  const rows=[];
  const add=(on,name,lo,mode,hi,unit,d)=>{ if(on) rows.push('<tr><td>'+name+'</td><td class="num">'+n(lo,d)+'</td><td class="num">'+n(mode,d)+'</td><td class="num">'+n(hi,d)+'</td><td>'+unit+'</td></tr>'); };
  add(h.capex_x===undefined,"What the plant costs to build",M.capex_x[0],M.capex_x[1],M.capex_x[2],"× the model's estimate",2);
  add(!tpFinHeld(h)&&!(SCS.base==="humbird"&&tpHb(SCS).finance),"The yearly charge on the plant",P.plant_charge_mature[0]*100,P.plant_charge_mature[1]*100,P.plant_charge_mature[2]*100,"% a year",1);
  add(h.medium_price===undefined&&base>0,"The price of the medium",M.medium_price[0]*base,M.medium_price[1]*base,M.medium_price[2]*base,"$ a litre",2);
  add(isScen&&(p.hazard||0)>0,"Runs lost to contamination",M.hazard[0]*p.hazard*100,M.hazard[1]*p.hazard*100,M.hazard[2]*p.hazard*100,"% of runs a day",2);
  add(perf&&h.mem_life===undefined,"Litres a m² of membrane filters",P.rt_membrane_life[0],P.rt_membrane_life[1],P.rt_membrane_life[2],"litres a m²",0);
  add(perf&&h.mem_price===undefined,"Price of the membranes",P.rt_membrane_price[0],P.rt_membrane_price[1],P.rt_membrane_price[2],"$ a m²",0);
  add(h.maint===undefined,"Share of a cell's oxygen spent on upkeep",P.pf_maintenance_share[0]*100,P.pf_maintenance_share[1]*100,P.pf_maintenance_share[2]*100,"%",0);
  const nl=P[isScen?"sc_nh3_limit":"pf_nh3_limit"];
  add(h.nh3_limit===undefined,"Ammonia the cells tolerate",nl[0],nl[1],nl[2],"mmol a litre",1);
  const ll=P[isScen?"sc_lac_limit":"pf_lac_limit"];
  add(h.lac_limit===undefined,"Lactate the cells tolerate",ll[0],ll[1],ll[2],"mmol a litre",0);
  add(h.killx===undefined&&tpSparged(p),"Cells killed by bursting bubbles",P.ge_kill_protected[0]/C.fx.kill,P.ge_kill_protected[1]/C.fx.kill,P.ge_kill_protected[2]/C.fx.kill,"× the model's estimate",1);
  add(h.protect_price===undefined,"Price of the bubble protectant",P.pf_protectant_price[0],P.pf_protectant_price[1],P.pf_protectant_price[2],"$ a kilo",0);
  add(h.protect_dose===undefined,"Bubble protectant in the medium",P.pf_protectant_dose[0],P.pf_protectant_dose[1],P.pf_protectant_dose[2],"grams a litre",1);
  add(h.min_perfusion===undefined,"Least medium flow the cells need",P.pf_min_perfusion[0],P.pf_min_perfusion[1],P.pf_min_perfusion[2],"mL a gram a day",1);
  add(p.antifoam_otr===undefined,"Oxygen transfer left once antifoam is added",P.pf_antifoam_otr[0]*100,P.pf_antifoam_otr[1]*100,P.pf_antifoam_otr[2]*100,"%",0);
  add(h.aa_price===undefined,"Price of amino acids",P.aa_bulk_price[0],P.aa_bulk_price[1],P.aa_bulk_price[2],"$ a kilo",2);
  add(isScen&&tr.mass_pg===undefined,"Weight of one cell",P.sc_mass_selected_pg[0]/1000,P.sc_mass_selected_pg[1]/1000,P.sc_mass_selected_pg[2]/1000,"ng",1);
  add(isScen&&tr.nh3_kg===undefined&&(SCS.choice.cells==="selected"||SCS.choice.cells==="measured"),"Ammonia the cells make",P.sc_nh3_selected[0],P.sc_nh3_selected[1],P.sc_nh3_selected[2],"mol a kilo of cells",3);
  host.innerHTML='<p>The cost above, <b>'+scMoney(cl.point)+'</b>, puts every setting at the value its slider shows. Some of those values are estimates that nobody has measured at this scale. '+
    'If each of them is drawn at random from the range below ('+cl.n+' draws; the value in the middle column is the most likely), half the draws cost less than <b>'+tpUSD(cl.q[1])+'</b> and 8 in 10 fall between <b>'+tpUSD(cl.q[0])+'</b> and <b>'+tpUSD(cl.q[2])+'</b>. '+
    'The middle draw is '+(cl.q[1]>cl.point*1.02?"above":(cl.q[1]<cl.point*0.98?"below":"close to"))+' the cost above because several ranges reach further on their costly side. A setting you move yourself leaves this list.</p>'+
    '<div class="scrollx"><table class="sctab"><thead><tr><th>Estimate varied</th><th>From</th><th>Most likely</th><th>To</th><th></th></tr></thead><tbody>'+rows.join("")+'</tbody></table></div>'+
    '<p class="small">The cells\' traits you set in section 1 and the shoppers are not varied here. The documents\' tables give the middle draw and this range for their examples.</p>';
}
// The arithmetic behind the three figures, with the reader's own numbers, one line a step (opened by the reader). Every number is
// the engine's own result or setting; the lines are checked to add up before a formula is shown.
function tpCalcRender(f){
  const d=document.getElementById("calc"), host=document.getElementById("tp_calc"); if(!d||!host||!d.open) return;
  f=f||pgFacts(); const r=f.cloud.res, p=tpParams(), tr=tpTraitsShown(), m2=v=>"$"+v.toFixed(2), m1=v=>"$"+v.toFixed(1), near=(a,b)=>Math.abs(a-b)<=0.01*Math.max(1,Math.abs(b));
  const lw=k=>TP_LIMW[k]||(typeof VM!=="undefined"&&VM.limit_plain[k])||k, lims=Object.keys(r.limits).map(k=>[k,r.limits[k]]).filter(x=>isFinite(x[1])).sort((a,b)=>a[1]-b[1]);
  const terms=Object.keys(r.medium_terms||{}).map(k=>[k,r.medium_terms[k]]).sort((a,b)=>b[1]-a[1]);
  const st=[];
  st.push("<b>How dense the tank can run.</b> The lowest of these limits: "+lims.slice(0,5).map(x=>pgEsc(lw(x[0]))+" "+x[1].toFixed(0)+" g a litre").join("; ")+". So <b>"+r.density.toFixed(0)+" g of cells a litre</b>.");
  st.push("<b>What a tank makes.</b> "+r.density.toFixed(0)+" g a litre, doubling every "+tr.doubling_h.toFixed(0)+" hours, with the tank in use "+(r.uptime*100).toFixed(0)+"% of the time: <b>"+r.output.toFixed(1)+" tonnes of cells a year from each m³ of tank</b>.");
  const cap=p.charge*r.capex/r.output;
  st.push("<b>The plant.</b> "+(near(cap,r.capital)?"It costs $"+Math.round(r.capex).toLocaleString("en-US")+"k to build per m³ of tank. A yearly charge of "+(p.charge*100).toFixed(1)+"% on that, divided by the "+r.output.toFixed(1)+" tonnes it makes: ":"Its yearly charge, divided by what it makes: ")+"<b>"+m1(r.capital)+" a kilo</b>.");
  const mp=p.medium_price===undefined?0.15:p.medium_price;
  st.push("<b>The litres of medium.</b> "+(terms.length?"The largest of these needs: "+terms.slice(0,4).map(x=>pgEsc(TP_TERMW[x[0]]||x[0])+" "+x[1].toFixed(0)+" litres").join("; ")+". So ":"")+"<b>"+r.medium_l.toFixed(0)+" litres a kilo</b>.");
  const wOn=p.wash_price!==undefined&&p.wash_price!==null&&!r.medium_floor, cOn=(r.clean_opex||0)+(r.clean_capital||0)>0.005, cfm=r.clean_filter_membranes||0;
  const liveS=r.harvested_share===undefined?1:r.harvested_share, carryL=Math.min(r.medium_l,C.fx.medium_l/liveS);
  st.push("<b>The medium.</b> "+(r.medium_floor?"The nutrients the cells must eat cost "+m2(r.nutrients)+" a kilo, more than "+r.medium_l.toFixed(0)+" litres at "+m2(mp)+", so the nutrients set it: "
    :(wOn?"The litres at their two prices":r.medium_l.toFixed(0)+" litres × "+m2(mp)+" a litre"+(near(r.medium_l*mp,r.feedstock)?"":", with the medium of lost runs"))+": ")+"<b>"+m1(r.feedstock)+" a kilo</b>."+
    (wOn?" The "+carryL.toFixed(0)+" litres that carry the nutrients are charged at "+m2(mp)+" and the other "+(r.medium_l-carryL).toFixed(0)+", which only wash waste out, at $"+p.wash_price.toFixed(3)+".":"")+
    (cOn?" Cleaning the medium: "+pgEsc(TP.clean.routes[SCS.clean.route].name.toLowerCase())+" cleans "+r.clean_loop.toFixed(0)+" litres a kilo and returns them, so the fresh medium is "+r.medium_l.toFixed(0)+" litres in place of "+r.medium_l_unclean.toFixed(0)+"; running it costs "+m2(r.clean_opex)+" a kilo, and its equipment "+m2(r.clean_capital)+", which is inside the plant's figure above.":"")+
    (r.membranes-cfm>0.005?" Filter membranes for those litres: "+m1(r.membranes-cfm)+".":"")+(r.device_running>0.005?" The retention device's running cost: "+m1(r.device_running)+".":"")+
    (r.protectant>0.005?" Bubble protectant: "+m1(r.protectant)+".":"")+(r.growth_factors>0.005?" Growth factors bought on top: "+m1(r.growth_factors)+".":""));
  const rest=r.total-r.capital-r.feedstock-(r.membranes-cfm)-(r.device_running||0)-r.protectant-r.growth_factors-(r.clean_opex||0);
  st.push("<b>Labour, energy and other supplies.</b> Labour "+m1(r.labour)+", and "+m1(rest-r.labour)+" for energy, gas and supplies. Everything added up: <b>"+m1(r.total)+" a kilo of cells</b>.");
  const shop=shelfPrice(f.cost,state);
  st.push("<b>In the shop.</b> ("+m1(f.cost)+" + "+m2(state.markup_add)+" to reach the shelf) ÷ (1 − the shop's "+(state.retail_margin*100).toFixed(0)+"% margin) = <b>"+m1(shop)+" a kilo as mince</b>.");
  const ms=tpMeats(), ty=f.animals.types;
  st.push("<b>Against each kind of meat.</b> With "+tpPctB(f.buyers)+" of meat buyers picking it at the same price, the dearer it is against a meat the fewer pick it: "+
    ms.map(m=>{ const t=ty.find(x=>x.name===m.name), q=m.shop(f.cost)/m.price; return pgEsc(m.plain)+" ($"+m.price.toFixed(2)+"): "+(q>=9.5?q.toFixed(0):q.toFixed(1))+" times its price, "+(t?pgPctS(t.sh*100):"")+" of it"; }).join("; ")+
    ". Every kind of meat added up by weight: <b>"+(f.share<0.00095?"under 0.001%":tpPct2(f.share))+" of "+tpRegionMeat()+"</b>.");
  host.innerHTML='<ol class="calcsteps">'+st.map(x=>"<li>"+x+"</li>").join("")+'</ol><p class="small">Each line is the model\'s own figure at your settings. Move a lever and the lines it changes show why the cost moved.</p>';
}
function tpRenderFirst(){
  if(typeof document==="undefined") return;
  const f=pgFacts(), set=(id,h)=>{ const e=document.getElementById(id); if(e) e.innerHTML=h; };
  set("deck",pgLead()); set("tp_yours",pgDeck(f)); set("sumbar",tpSummaryHTML(f)); tpUncRender(); tpCalcRender(f);
  tpLineDraw(f); tpLineText(f); tpGroupsDraw(f); tpGroupsText(f); tpAnimalsRender(f);
  tpRenderControls(f); tpOneDraw(f); tpMapDraw(f); if(typeof stRender==="function") stRender();
}
const pgRenderFirst=tpRenderFirst;
function pgWidth(id,dflt){ const e=document.getElementById(id); const w=e&&e.clientWidth?e.clientWidth:0; return w>0?w:(dflt||720); }
function pgInterp(xs,ys,x){ if(x<=xs[0]) return ys[0]; for(let i=1;i<xs.length;i++){ if(x<=xs[i]){ const t=(x-xs[i-1])/(xs[i]-xs[i-1]); return ys[i-1]+t*(ys[i]-ys[i-1]); } } return ys[ys.length-1]; }

/* ---------- what it would take: the table scenarios.what_it_would_take generates ---------- */
function tpWitRender(){
  const host=document.getElementById("tp_wit"); if(!host) return;
  const mode=m=>m==="perfusion"?"perfusion":"fed-batch, 20 m³";
  host.innerHTML='<table class="sctab stack wit"><thead><tr><th>Share of all meat</th><th>Buyers at the same price</th><th>Cells must cost</th>'+
    '<th>Cells that reach it</th><th>Beyond what is published</th></tr></thead><tbody>'+
    TP.wit.map((r,i)=>{ const p=r.pick;
      return '<tr><td data-label="Share"><b>'+r.target+'%</b></td><td data-label="Meat buyers">'+tpPctB(r.buyers)+'</td><td data-label="Cells must cost">'+(r.need===null?"out of reach, even at $0.5":tpUSD(r.need)+" a kilo or less")+'</td>'+
        '<td data-label="Cells">'+(p?TRAIT_KEYS.map(k=>tpFmtTrait(k,p.traits[k])).join(", ")+'<br><span class="alt">'+tpUSD(p.cost)+' a kilo in '+TP.plant_names[p.plant].charAt(0).toLowerCase()+TP.plant_names[p.plant].slice(1)+', '+mode(p.mode)+'.</span> '+
          '<button type="button" class="lnk" onclick="tpTryWit('+i+')">Try these cells</button>':"none of the "+TP.n_wit_sets+" sets tried")+'</td>'+
        '<td data-label="Beyond what is measured">'+(p?tpBeyondWords(p.traits):"")+'</td></tr>'; }).join("")+'</tbody></table>';
}
// "lactate 0.42 mol per mol, against 1.05 measured" for each trait beyond the best measured in meat cells (mirror of cell_traits.beyond_text)
function tpBeyondWords(tr){ const ks=tpBeyond(tr);
  return ks.length?ks.map(k=>TP_TRAIT_WORD[k]+" "+tpFmtTrait(k,tr[k])+", against "+tpFmtTrait(k,TP.traits[k].best)+" measured").join("; "):"none: each trait at or within the best measured in meat cells"; }
function tpTryWit(i){ const p=TP.wit[i].pick; if(!p) return;
  SCS.base="switches"; SCS.choice=Object.assign({},p.choice); SCS.traits=Object.assign({},p.traits); SCS.held={}; SCS.clean=tpCleanNone(); SCS.redesign=true;
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
    return '<div class="refcard'+(on?' on':'')+'"><h4>'+r.label+(on?' <span class="tag">loaded</span>':'')+'</h4><p>'+pgEsc(r.text)+'</p>'+
      '<p class="small">'+(r.kind==="company"?'Its own figure: '+scMoney(r.cost)+' a kilo of cells. ':'About '+tpUSD(q[1])+' a kilo of cells (8 in 10 draws '+tpRangeUSD(q[0],q[2])+'). ')+
      'With '+tpPctB(r.buyers)+' of meat buyers picking it at the same price: '+pgPctS(sh)+' of world meat and seafood in the long run.'+
      (r.traits?' Cells: '+TRAIT_KEYS.map(k=>tpFmtTrait(k,r.traits[k])).join(", ")+'. Beyond the best measured in meat cells: '+tpBeyondWords(r.traits)+'.':'')+'</p>'+
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
  h+='<div class="hb axis"><div class="hl"><span class="hv">Solid bar: the cost after the step. Pale bar: what the step saves. Dot and thin line: the median of the draws and the range that holds 8 in 10 of them (a draw is one run of the model with its unmeasured estimates picked at random from their ranges). '+
     'Dotted line: '+scMoney(par)+' a kilo of cells, the cost at which the shop price matches the world\'s meat and seafood at their price weighted by the tonnes eaten ($'+tpAvgPrice("global").toFixed(2)+' a kilo).</span></div><div class="ht">'+ticks.map(v=>'<span class="tk" style="left:'+pc(v)+'">$'+v+'</span>').join("")+'</div></div>';
  const ch=document.getElementById("l1chart"); if(ch) ch.innerHTML=h;
  const at=k=>L.find(s=>s.key===k).cost[1], first=L[0].cost[1], last=L[L.length-1].cost[1], eng=L.findIndex(s=>s.key==="engineered");
  const before=eng>0?L[eng-1].cost[1]:last;
  const alt=document.getElementById("l1alt");
  if(alt) alt.innerHTML="<b>What the chart shows.</b> The cost falls from about "+tpUSD(first)+" a kilo to about "+tpUSD(last)+". Of that fall, "+
    Math.round((first-before)/(first-last)*100)+"% comes before step 6, cells that make almost no ammonia or lactate: "+tpUSD(first-at("process"))+" from the process and cheaper inputs, "+
    tpUSD(at("process")-at("selected"))+" from cells that make less lactate and double every 36 hours, "+tpUSD(at("selected")-at("central"))+" from perfusion and "+tpUSD(at("central")-before)+" from a cheaper plant. "+
    (last>par?"No step reaches ":"The last step passes ")+scMoney(par)+". The steps are fixed examples, not a forecast: each adds one kind of change to the one before.";
  const tb=document.getElementById("l1table");
  if(tb) tb.innerHTML='<table class="num"><thead><tr><th rowspan="2">Step</th><th rowspan="2">What changes</th><th colspan="4">Cost of a kilo of cells, 2025 dollars</th></tr><tr><th>Median</th><th>8 in 10 draws</th><th>Most likely values</th><th>Saved</th></tr></thead><tbody>'+rowsT+'</tbody></table>'+
   '<p class="note">Median: the middle of the draws. Most likely values: every estimate at its single most likely value. Saved: the fall in the median from the step before.</p>';
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
  // the four traits, each from Published cells' level to that of the all-favourable example (a cell's weight over the range the draws take)
  const pub=tpRef("today").traits, eng=tpRef("best").traits, mq=TP.cloud.priors.sc_mass_selected_pg;
  TRAIT_KEYS.forEach(k=>{ const T=TP.traits[k], ends=k==="mass_pg"?[mq[0],mq[2]]:[pub[k],eng[k]];
    const c=ends.map(v=>floorExplore(Object.assign({},p0,{[k]:v})).total), lo=Math.min(c[0],c[1]), hi=Math.max(c[0],c[1]);
    const iLo=c[0]<=c[1]?0:1;
    rows.push({kind:"trait", id:"tr_"+k, name:T.name, what:T.help, now:tpFmtTrait(k,tpTraitsShown()[k]), lo:lo, hi:hi,
      loT:tpFmtTrait(k,ends[iLo]), hiT:tpFmtTrait(k,ends[1-iLo]),
      why:T.help+" "+tpBestText(k), tag:"a trait of the cells"}); });
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
  let h='<div class="hbh">What changes the cost of a kilo of cells. Start: '+scMoney(base)+' with every estimate at its most likely value.</div>';
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
  h+='<div class="hbh">What changes the long-run share at that cost. Start: '+pgPctS(R.bsh)+' of '+pgRegionOf()+' meat and seafood.</div>';
  R.dem.forEach(r=>{ const sel=PGS.l2sel===r.id;
    h+='<div class="hb click'+(sel?' sel':'')+'" role="button" tabindex="0" aria-expanded="'+sel+'" onclick="l2Pick(\''+r.id+'\')" onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();l2Pick(\''+r.id+'\')}">'+
       '<div class="hl"><b>'+r.name+'</b> '+pgTag(r.tag)+'<br><span class="hv">Now '+r.nowT+'. Share '+pgPctS(r.lo)+' at '+r.loT+', and '+pgPctS(r.hi)+' at '+r.hiT+'.</span></div>'+
       '<div class="ht"><span class="bar sh" style="left:'+ps(r.lo).toFixed(2)+'%;width:'+Math.max(0.6,ps(r.hi)-ps(r.lo)).toFixed(2)+'%"></span><span class="vbase" style="left:'+ps(R.bsh).toFixed(2)+'%"></span></div></div>'; });
  h+='<div class="hb axis"><div class="hl"><span class="hv">Each bar runs from the share at one end of the range to the share at the other. The line is the share now. Log scale.</span></div>'+
     '<div class="ht">'+[0.01,0.1,1,10].map(v=>'<span class="tk" style="left:'+ps(v).toFixed(2)+'%">'+v+'%</span>').join("")+'</div></div>';
  host.innerHTML=h;
  const sub=document.getElementById("l2sub");
  if(sub) sub.innerHTML="For "+pgCaseWords(f)+", "+pgRegionName()+". These are single estimates, so the starting cost is the most-likely-values figure ("+scMoney(base)+
    "), not the median of the draws ("+tpUSD(f.cb[1])+"). Each row moves one thing across its range, with everything else as set."+(SCS.base==="humbird"?" Humbird's design is not built from the plant's settings in How the tank and the plant set the cost, so they are not ranked here.":"");
  const all=R.cost.concat(R.dem), s=all.find(r=>r.id===PGS.l2sel), card=document.getElementById("l2card");
  if(card){ card.style.display=s?"":"none";
    if(s) card.innerHTML='<p><b>'+s.name+'.</b> '+pgTag(s.tag)+'</p>'+
      (s.kind==="trait"?'<p>Now: '+s.now+'. '+s.why+'</p><p>At '+s.loT+': '+scMoney(s.lo)+' a kilo and a long-run share of '+pgPctS(s.shLo)+'. At '+s.hiT+': '+scMoney(s.hi)+' and '+pgPctS(s.shHi)+'. Set it under <a href="#tp_cells">Change the cells</a>.</p>'
       :s.kind==="choice"?'<p>'+s.what+' Now: '+s.now+'. '+s.why+'</p><p>Cheapest setting: '+s.loT+', '+scMoney(s.lo)+' a kilo and a long-run share of '+pgPctS(s.shLo)+
          '. Dearest setting: '+s.hiT+', '+scMoney(s.hi)+' and '+pgPctS(s.shHi)+'. Change it under <a href="#engineering">How the tank and the plant set the cost</a>.</p>'
       :s.kind==="estimate"?'<p>Range: '+s.loT+' gives '+scMoney(s.lo)+' a kilo (share '+pgPctS(s.shLo)+'); '+s.hiT+' gives '+scMoney(s.hi)+' (share '+pgPctS(s.shHi)+').</p><p>Where the value comes from: '+s.why+'.</p>'
       :'<p>'+s.why+'</p><p>At '+s.loT+' the long-run share is '+pgPctS(s.lo)+'. At '+s.hiT+' it is '+pgPctS(s.hi)+'. Change it under <a href="#shoppers">How a shop price becomes a share</a>.</p>'); }
  const tb=document.getElementById("l2table");
  if(tb) tb.innerHTML='<table class="num"><thead><tr><th rowspan="2">What is moved</th><th rowspan="2">Kind</th><th colspan="3">Favourable end</th><th colspan="3">Unfavourable end</th></tr><tr><th>Value</th><th>Cost</th><th>Share</th><th>Value</th><th>Cost</th><th>Share</th></tr></thead><tbody>'+
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
  const basis="a cost of "+tpUSD(f.cost)+" a kilo of cells (every estimate at its most likely value), "+tpPctB(f.buyers)+" of meat buyers picking it at the same price, and the other shopper settings as set";
  set("l3_intro","Cultivated meat costs about the same whatever animal it copies, but conventional prices differ. So it competes where meat is dear and stays out where meat is cheap. "+
    "Everything in this level is at "+basis+". It adds up to "+pgPctS(total)+" of "+pgRegionOf()+" meat and seafood by weight ("+pgPctS(p.tval*100)+" by value).");
  set("l3asub",pgRegionName()+", "+pgCaseWords(f)+". A cut is "+Math.round(s.cut_cells*100)+"% cells bound with plant protein, so shoppers like it a little less than mince, and premium products less again.");
  const t3=rows.slice(0,3), dear=rows.filter(r=>/chicken|pork/i.test(r.name)&&!/organic|heritage/i.test(r.name));
  set("l3aalt","<b>What the chart shows.</b> The three types that add most to the total are "+t3.map(r=>r.name.toLowerCase()+" ("+pgPctS(r.sh)+" of the type)").join(", ")+
    ". "+(dear.length?"Ordinary chicken and pork stay at "+pgRange(Math.min.apply(null,dear.map(r=>r.R)),Math.max.apply(null,dear.map(r=>r.R)),v=>v.toFixed(1))+" times the conventional price.":""));
  set("l3atable",'<table class="num"><thead><tr><th rowspan="2">Type of meat</th><th rowspan="2">Kind</th><th colspan="2">Price in the shop</th><th colspan="3">Share, by weight</th></tr><tr><th>Conventional, a kilo</th><th>Cultivated, times</th><th>Of the type</th><th>Type in all meat</th><th>Adds to total</th></tr></thead><tbody>'+
    rows.map(r=>'<tr><td>'+r.name+'</td><td>'+r.kind+'</td><td>$'+r.price.toFixed(1)+'</td><td>'+r.R.toFixed(2)+'</td><td>'+pgPctS(r.sh)+'</td><td>'+r.w.toFixed(1)+'%</td><td>'+pgPctS(r.part)+'</td></tr>').join("")+'</tbody></table>');
  // regions: the same cloud of cost draws, at each region's own prices and incomes
  set("l3rsub","At "+tpUSD(f.cost)+" a kilo of cells and "+tpPctB(f.buyers)+" of meat buyers picking it at the same price, with the other shopper settings as set. Each region has its own meat prices and incomes. The two meats named are its cheapest large kind and its steak. The long-run share is of all the region's meat and seafood, by weight.");
  set("l3regions",'<table class="num"><thead><tr><th>Region</th><th>Two meats, shop price a kilo</th><th>Long-run share</th></tr></thead><tbody>'+
    PG.regions.map(r=>{ const ms=tpMeats(r[0]), a=ms[0], b=ms.find(m=>/steak/i.test(m.name))||ms[ms.length-1];
      return '<tr><td>'+r[1]+'</td><td>'+pgEsc(a.plain)+' $'+a.price.toFixed(2)+'; '+pgEsc(b.plain)+' $'+b.price.toFixed(2)+'</td><td><b>'+pgPctS(tpShare(f.cost,f.buyers,r[0]))+'</b></td></tr>'; }).join("")+'</tbody></table>');
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
  let h=(SCS.base==="humbird"?'<p class="callout">The page is on '+pgEsc(tpHb(SCS).label)+', which is not built from these settings. They show the settings of '+pgEsc(tpRef(scPresetOf(SCS.choice))?tpLabel(scPresetOf(SCS.choice)):"another set of cells")+'; moving one starts your own settings from them.</p>':'')+
    '<p><b>'+f.label+': '+scMoney(cost)+' a kilo of cells, with every setting at the value shown.</b> '+
    'The first screen\'s section “How uncertain is this cost” varies the estimates nobody has measured.'+
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
  const other=SCS.vmode||(SCS.device&&SCS.device!=="tff");
  host.innerHTML=(other?'<p class="callout">On the first screen you chose '+(SCS.vmode?pgEsc(VM.vessels[SCS.vessel].name.toLowerCase()+", run as "+VM.modes[SCS.vmode].name.toLowerCase()):"")+
    (SCS.vmode&&SCS.device!=="tff"?" and ":"")+(SCS.device&&SCS.device!=="tff"&&MODEL.rt?pgEsc(MODEL.rt.devices[SCS.device].name.toLowerCase())+" to hold the cells back":"")+
    '. The settings below describe a stirred tank with a membrane loop, so the cost in this section ('+scMoney(r.total)+') is that tank\'s, not the '+scMoney(pgPointCost())+' of your choice.</p>':"")+scResultHTML(ch,r);
  const gfIn=(p.gf_in_medium||0)>0&&r.growth_factors<0.005;
  const ph=document.getElementById("sc_parts");      // where the cost goes, against the low-lactate example (or the all-favourable example when that one is loaded)
  if(ph){ const refKey=SCS.ref==="central"?"best":"central"; ph.innerHTML=scPartsSVG(r,scWithExtra({},()=>scEval(SC.presets[refKey].choice)),tpLabel(refKey),gfIn); }
  const pn=document.getElementById("sc_parts_note");
  if(pn) pn.innerHTML=gfIn?"The medium's price is taken to include the growth factors, so they show as $0.00 here. The growth-factor setting then acts as a floor: the medium cannot cost less than its nutrients plus the growth factors bought. "+
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
    '<p class="small">No two settings interact strongly here: each saves about the same whatever the other is set to.</p>';
  drawCost(state); if(typeof fxRender==="function"&&fxDefaults) fxRender();
}
function l5Render(){
  const s=state, b=biomass(s), retail=shelfPrice(b,s), conv=C.p_conv_anchor*s.meat_tax;
  drawCalc(s,b,retail,conv,retail/conv); drawCurve(s); drawBreakdown(s); drawMilk(s); drawFoothold(s);
  // the 2,000-draw histogram takes about 0.3 s: while a slider is being dragged, draw it once the hand stops (150 ms), not on every step
  if(typeof setTimeout==="function"){ clearTimeout(PGS.mcTimer); PGS.mcTimer=setTimeout(()=>drawMC(state),150); } else drawMC(s);
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
  // labels are measured in the page's font: draw the charts again once the web font has arrived
  try{ if(typeof document!=="undefined"&&document.fonts&&document.fonts.ready) document.fonts.ready.then(()=>{ if(KP) tpRenderFirst(); }); }catch(e){}
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
    fxCarry={nh3_limit:p.nh3_limit, lac_limit:p.lac_limit, gf_in_medium:p.gf_in_medium||0, glc_balance:!!p.glc_balance, gk:document.getElementById("fx_gk").value};
  }
  fxRender();
}
