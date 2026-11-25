/* ===== the device that holds the cells back in a perfusion tank =====
   A mirror of retention.py (duty, sizing, scenario_cost) for every device but the hoped-for one and the two particle
   routes (MODEL.rt.particles, python_only); tests/run_parity.py checks the two agree. The numbers are in MODEL.rt
   (retention.js_model) and C.fx. `p` is a set of floorExplore arguments (JS names), as scParams gives. No UI here. */
const RT=MODEL.rt;
function rtDuty(p,res){                         // mirror of retention.duty: flows in m3/h for the case p (res: its result, if run)
  const F=C.fx, r=res||floorExplore(p), v=p.vessel_m3===undefined?20:p.vessel_m3;
  const liquid=F.wv*v;                                        // m3
  const tonnes=r.output*v;                                    // t of wet cells per tank-year
  const harvest=tonnes*1000/(RT.hours*r.uptime);              // kg/h while the tank runs
  const medium=r.medium_l*harvest/1000;                       // m3/h
  const hs=r.harvested_share===undefined?1:r.harvested_share; // kilos harvested per kilo grown
  const bleed=harvest/hs/r.density;                           // m3/h of whole culture: the cells grown leave in it (kg grown an hour over kg/m3)
  let permeate=Math.max(0,medium-bleed);
  if(permeate<1e-9*medium) permeate=0;                        // the bleed carries out all the liquid (rounding apart)
  permeate+=(r.filter_extra_l||0)*harvest/1000;               // what a device on the permeate cleans passes the filter again (2026-11-21)
  const phi=r.density/(F.cell_density*1000);                  // volume fraction of cells
  return {vessel_m3:v, liquid_m3:liquid, density:r.density, phi:phi, kg_h:harvest, kg_year:tonnes*1000, medium_m3_h:medium,
          bleed_m3_h:bleed, permeate_m3_h:permeate, outflow_m3_h:medium, vvd_medium:medium*24/liquid, vvd_permeate:permeate*24/liquid,
          uptime:r.uptime, run_frac:r.run_frac===undefined?1:r.run_frac, result:r};
}
function rtStokes(dUm,drho){                    // mirror of floor_physics._stokes: cm/h
  const d=dUm*1e-6, v=d*d*drho*9.81/(18*C.fx.medium_viscosity*1e-3);
  return v*100*3600;
}
function rtSizing(device,p,d){                  // mirror of retention.sizing (not the particle routes)
  const F=C.fx, D=RT.devices[device];
  if(!D) throw new Error("retention device not on the page: "+device);
  const I=D.inputs;
  if(d===undefined||d===null) d=rtDuty(p);
  const v=d.vessel_m3, liq=d.liquid_m3, P=d.permeate_m3_h, B=d.bleed_m3_h, phi=d.phi, kg=d.kg_year;
  const out={device:device, units:0, area_m2:0, capex_k_m3:0, cons_kg:0, loss:0, holdup_m3:0};
  const permLkg=P*1000/d.kg_h;                                // litres of permeate per kg harvested
  const runFrac=d.run_frac===undefined?1:d.run_frac;          // a lost run throws its membranes away early
  if(device==="atf"){
    const n=Math.ceil(P*1000/(I.flux*I.area));
    Object.assign(out,{units:n, area_m2:n*I.area, cons_kg:permLkg*I.mem_price/(I.mem_life*runFrac), capex_k_m3:n*I.price*I.factor/v});   // I.factor: retention.atf_factor
  } else if(device==="tff"){
    // the engine's own loop: the case's own flux, membrane life, price and hardware where it sets them (floorExplore's arguments)
    const own=(a,dflt)=>(p&&p[a]!==undefined&&p[a]!==null)?p[a]:dflt;
    const area=P*1000/own("flux",I.flux);
    Object.assign(out,{area_m2:area, cons_kg:permLkg*own("membrane_price",I.mem_price)/(own("membrane_life",I.mem_life)*runFrac), capex_k_m3:area*own("membrane_hw",I.hw)*I.install/v});
  } else if(RT.memb.indexOf(device)>=0){
    const area=P*1000/I.flux; let life=I.life;
    if(device!=="ceramic") life*=runFrac;                     // ceramics are cleaned and kept
    Object.assign(out,{area_m2:area, cons_kg:permLkg*I.price/life, capex_k_m3:area*I.hw*I.install/v});
  } else if(device==="settler"){
    const mass=p.mass_pg===undefined?3000:p.mass_pg;
    const dUm=Math.pow(6*mass*1e-15/(Math.PI*F.cell_density*1000),1/3)*1e6;
    const v1=rtStokes(dUm,(F.cell_density-F.medium_density)*1000);        // cm/h
    const vd=v1*Math.pow(1-phi,4.65)*I.v_frac;                            // design overflow, cm/h
    const area=P/(vd/100);
    Object.assign(out,{area_m2:area, holdup_m3:area*I.holdup/1000, settle_cm_h:vd, capex_k_m3:area*I.price/v});
  } else if(device==="acoustic"){
    const n=Math.ceil(P*24/I.cap);
    Object.assign(out,{units:n, capex_k_m3:n*I.price*I.install/v});
  } else if(device==="discstack"){
    const c=I.conc, feed=P*(1+phi/(c-phi));                   // permeate plus the concentrate sent back
    const run=Math.ceil(feed/I.cap), n=run+I.spares, capex=n*I.price;     // $k per tank, installed
    const passes=feed*24/liq, bleed=B*24/liq;                 // share of the culture through the bowl a day
    const f=I.lysis*passes;
    const power=run*I.power*RT.hours*d.uptime*I.power_price/kg;
    Object.assign(out,{units:n, feed_m3_h:feed, passes_day:passes, loss:f/(bleed+f), capex_k_m3:capex/v,
                       cons_kg:power+I.maint*capex*1000/kg});
  } else if(device==="hydrocyclone"){
    const feed=P/I.split, esc=(1-I.eff)*feed;                 // culture-equivalent flow of cells lost
    Object.assign(out,{feed_m3_h:feed, loss:esc/(B+esc), capex_k_m3:feed*I.price/v});
  } else throw new Error("retention device not mirrored: "+device);
  out.cons_kg_grown=out.cons_kg*(d.result.harvested_share===undefined?1:d.result.harvested_share);   // per kilo grown: what floorExplore's extra_opex takes
  out.phi_max=D.phi_max;
  out.beyond=D.phi_max!==null&&phi>D.phi_max+1e-9;
  // not possible: a settler that would hold too much of the culture outside the tank, with no oxygen
  out.impossible=out.holdup_m3>RT.holdup_max*liq?"It would hold "+(out.holdup_m3/liq*100).toFixed(0)+"% of the culture outside the tank, with no oxygen supply.":"";
  return out;
}
const RT_PER_KG=["capital","labour","utilities","consumables","feedstock","growth_factors","extra_opex","membranes","protectant","total"];
function rtCost(device,p){                      // mirror of retention.scenario_cost
  const d=rtDuty(p); let sz=rtSizing(device,p,d);
  let r=device==="tff"?floorExplore(p)
    :floorExplore(Object.assign({},p,{retention:sz.capex_k_m3, extra_opex:(p.extra_opex||0)+sz.cons_kg_grown}));
  if(device!=="tff"&&!(device in (RT.particles||{}))){   // size the device from the design it runs (retention.scenario_cost)
    for(let i=0;i<RT.resize_passes;i++){ sz=rtSizing(device,p,rtDuty(p,r));
      r=floorExplore(Object.assign({},p,{retention:sz.capex_k_m3, extra_opex:(p.extra_opex||0)+sz.cons_kg_grown})); } }
  const keep=1-sz.loss, total=r.total/keep;     // the share of grown cells that survive the device
  // the case's own result with every cost per kilo over that share, for a cost breakdown. The device's running cost sits in
  // res.extra_opex (with any bought oxygen) and its capital in res.capital; for the TFF loop they are res.membranes
  // (inside res.consumables) and res.retention_capex, as floorExplore gives them
  const res=Object.assign({},r), cs=p.cell_share===undefined?1:p.cell_share;
  RT_PER_KG.forEach(k=>{ res[k]=r[k]/keep; });
  res.product=cs*res.total+(1-cs)*C.fx.filler;
  const tff=device==="tff", vm=p.vm||{};
  const held=(vm.washed!==undefined?vm.washed:p.mode==="perfusion")&&!vm.own_retention;   // floorExplore charges a device's capital only then
  return Object.assign({},sz,{total:total, base:d.result.total, delta:total-d.result.total, res:res,
    device_capital_kg:(tff?p.charge*r.retention_capex/r.output:(held?p.charge*sz.capex_k_m3/r.output:0))/keep,
    device_running_kg:(tff?r.membranes:sz.cons_kg)/keep});
}
