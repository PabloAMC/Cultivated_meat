/* ===== vessel types against operating modes =====
   A mirror of vessels.py (vm_for, explore_kwargs, cell); tests/run_parity.py checks the two agree. Each cell is
   floorExplore (the mirror of floor_physics.explore) with the vessel's and the mode's numbers in MODEL.vm.
   The table shows the selected case or Humbird's optimistic design, and is redrawn when a switch moves. */
const VM=MODEL.vm;
let vmShow="scenario";                          // "scenario" | "reference"
function vmFor(v,m){                            // mirror of vessels.vm_for (null if the combination is not possible)
  const key=v+"|"+m;
  if(VM.not_possible[key]) return null;
  if(VM.same_as[key]) return vmFor(v,VM.same_as[key][0]);
  const V=VM.vessels[v], M=VM.modes[m];
  const out=Object.assign({},V.vm,M.vm), caps=Object.assign({},V.vm.caps||{},M.vm.caps||{});
  if(Object.keys(caps).length) out.caps=caps;
  if(V.fixed){ Object.assign(out,{kind:"cyclic",restart_days:VM.restart},V.cycle);
    if(m==="batch"){ out.washed=true; out.caps=Object.assign({},V.vm.caps); } }
  if(V.size<VM.str_m3) out.labour_mult=Math.pow(VM.str_m3/V.size,VM.labour_exp);
  return out;
}
function vmKwargs(v,m,base){                    // mirror of vessels.explore_kwargs (JS argument names)
  const vm=vmFor(v,m); if(vm===null) return null;
  const V=VM.vessels[v], M=VM.modes[m], p=Object.assign({},base);
  if(!V.tricks) VM.trick_args.forEach(k=>{ delete p[k]; });
  if(!V.shape) delete p.aspect;
  if(V.aspect!==null&&V.aspect!==undefined){ p.aspect=V.aspect; p.shape_cost=false; }
  let vm2=vm;
  if(V.gas_add!==null&&V.gas_add!==undefined){ p.gas_v=(p.gas_v===undefined?C.fx.gas_v:p.gas_v)+V.gas_add;   // the cage's gas adds to the ring's
    vm2=Object.assign({},vm,{gas_away:V.gas_add}); }           // and meets no cells: no bubble deaths on it (vessels.explore_kwargs)
  p.vessel_m3=V.size; p.mode=M.mode; p.vm=vm2;
  if(V.fixed&&(m==="batch"||m==="fedbatch")) p.medium_l=1000/VM.batch_x;
  return p;
}
function vmLoopOk(r){ const c=r.column; return !c||(c.ph_vs_safe<=1+1e-9&&c.passes_tested); }
function vmThinned(kw,xHi){                     // mirror of vessels._thinned: the densest culture whose loop passes its checks
  let lo=0, hi=xHi, ok=null;
  for(let i=0;i<24;i++){ const mid=0.5*(lo+hi), caps=Object.assign({},kw.vm.caps||{}); caps[VM.loop_limit]=mid;
    const r=floorExplore(Object.assign({},kw,{vm:Object.assign({},kw.vm,{caps:caps})}));
    if(vmLoopOk(r)){ lo=mid; ok=r; } else hi=mid; }
  return ok;
}
function vmCell(v,m,base){                      // mirror of vessels.cell
  const key=v+"|"+m, tag=VM.tags[key];
  const p=vmKwargs(v,m,base);
  if(p===null) return {possible:false, reason:VM.not_possible[key], tag:tag[0], evidence:tag[1]};
  let r=floorExplore(p), fallback="", unchecked=null;
  if(!vmLoopOk(r)){                             // the tricks' loop fails its checks here: the cheapest setting that passes
    unchecked=r.total; let best=null;
    scSwitch("tricks").settings.forEach(st=>{
      const b=Object.assign({},base); VM.trick_args.forEach(k=>{ delete b[k]; });
      const kw2=vmKwargs(v,m,Object.assign(b,st.p));
      let rr=floorExplore(kw2), thin=false;
      if(!vmLoopOk(rr)){ rr=vmThinned(kw2,rr.density); thin=true; }      // the same tricks with the culture run thinner
      if(rr!==null&&(best===null||rr.total<best[1].total-1e-12)) best=[st,rr,thin];
    });
    r=best[1]; fallback=best[0].label+(best[2]?VM.thin_note:"");
  }
  let big="capital"; Object.keys(VM.biggest).forEach(k=>{ if(r[k]>r[big]) big=k; });
  return {possible:true, cost:r.total, limit:r.limit, density:r.density, output:r.output, medium_l:r.medium_l, uptime:r.uptime,
          biggest:VM.biggest[big], biggest_share:r[big]/r.total, tricks_fallback:fallback, unchecked_cost:unchecked,
          density_unshown:tag[0]===VM.tag_order[0]&&r.density>VM.x_meat_shown+1e-9,
          same_as:VM.same_as[key]?VM.same_as[key][0]:null, tag:tag[0], evidence:tag[1]};
}
// Is the combination one the model can price (not "not possible")?
function vmPossible(v,m){ return !VM.not_possible[v+"|"+m]; }
// The floorExplore arguments of a vessel and a way of running it on top of a case, after the same fallback as vmCell: if the case's
// added equipment for oxygen and CO₂ fail the column's checks in this vessel, the cheapest trick setting that passes, run thinner if it must be.
function vmResolve(v,m,base){
  const p=vmKwargs(v,m,base); if(p===null) return null;
  if(vmLoopOk(floorExplore(p))) return {kw:p, fallback:""};
  let best=null;
  scSwitch("tricks").settings.forEach(st=>{
    const b=Object.assign({},base); VM.trick_args.forEach(k=>{ delete b[k]; });
    let kw2=vmKwargs(v,m,Object.assign(b,st.p)), rr=floorExplore(kw2), thin=false;
    if(!vmLoopOk(rr)){ let lo=0, hi=rr.density, ok=null;
      for(let i=0;i<24;i++){ const mid=0.5*(lo+hi), caps=Object.assign({},kw2.vm.caps||{}); caps[VM.loop_limit]=mid;
        const kw3=Object.assign({},kw2,{vm:Object.assign({},kw2.vm,{caps:caps})}), r3=floorExplore(kw3);
        if(vmLoopOk(r3)){ lo=mid; ok=[kw3,r3]; } else hi=mid; }
      if(ok===null) return; kw2=ok[0]; rr=ok[1]; thin=true; }
    if(best===null||rr.total<best[1].total-1e-12) best=[kw2,rr,st.label+(thin?VM.thin_note:"")];
  });
  return best?{kw:best[0], fallback:best[2]}:{kw:p, fallback:""};
}
function vmBase(){                              // the case the table holds fixed
  if(vmShow==="reference") return {doubling_h:24, mass_pg:3000, vessel_m3:20, plant:"sanitary", mode:"perfusion", charge:C.fx.charge_mature};
  // the side bar's case in a stirred tank in perfusion (as the first screen's own table of vessels), so the table follows every lever
  return tpParamsFor(Object.assign({},SCS,{vessel:"stirred",vmode:null,choice:Object.assign({},SCS.choice,{mode:"perfusion"}),hb:Object.assign({},SCS.hb,{mode:"perfusion"})}));
}
function vmMoney(x){ return "$"+(x>=1000?Math.round(x).toLocaleString("en-US"):x.toFixed(2)); }
function vmTagChip(t){ const cls=t===VM.tag_order[0]?"vt-today":t===VM.tag_order[1]?"vt-pilot":"vt-paper";
  return '<span class="vtag '+cls+'">'+t+'</span>'; }
function vmFallbackText(c){      // mirror of page_sections._vm_fallback_text
  return 'The case clears CO₂ with “added equipment for oxygen and CO₂”: a column beside the tank that strips it without bubbles, and the options that go '+
    'with it. This vessel is taller, so the column would keep too much of the culture at a high pH, which slows cell growth. The cost '+
    'here uses what passes that check: “'+c.tricks_fallback+'”. With the case’s own added equipment at full density it would be '+vmMoney(c.unchecked_cost)+'.'; }
function vmCellHTML(c,v,m){
  if(!c.possible) return '<td class="vno"><b>Not possible</b><br><span class="alt">'+c.reason+'</span></td>';
  if(c.same_as) return '<td class="vsame"><b>As batch</b><br><span class="alt">'+VM.same_as[v+"|"+m][1]+'</span></td>';
  const lim=VM.limit_plain[c.limit]||c.limit;
  let extra="";
  if(c.tricks_fallback) extra='<br><span class="alt">'+vmFallbackText(c)+'</span>';
  return '<td title="'+c.evidence.replace(/"/g,"&quot;")+'"><b>'+vmMoney(c.cost)+'</b><br><span class="alt">'+c.density.toFixed(0)+
    ' g/L, limited by '+lim+'. Biggest cost: '+c.biggest+'.</span><br>'+vmTagChip(c.tag)+
    (c.density_unshown?'<br><span class="alt vunshown">'+VM.unshown_note+'</span>':'')+extra+'</td>';
}
function vmGridHTML(base){
  const head='<thead><tr><th>Vessel ↓ &nbsp; How it is run →</th>'+VM.morder.map(m=>'<th>'+VM.modes[m].name+
    '<br><span class="alt">'+VM.modes[m].what+'</span></th>').join("")+'</tr></thead>';
  const rows=VM.vorder.map(v=>{ const V=VM.vessels[v];
    return '<tr><th>'+V.name+'<br><span class="alt">'+vmSize(V.size)+'. '+V.what+'</span></th>'+
      VM.morder.map(m=>vmCellHTML(vmCell(v,m,base),v,m)).join("")+'</tr>'; }).join("");
  return '<div class="scrollx"><table class="sctab vmtab">'+head+'<tbody>'+rows+'</tbody></table></div>';
}
function vmSize(m3){ return m3>=1?(m3.toFixed(0)+" m³ a unit"):(m3*1000>=1?(m3*1000).toFixed(0)+" litres a unit":(m3*1e6).toFixed(0)+" mL a unit"); }
function vmRender(){
  const host=document.getElementById("vm_grid"); if(!host) return;
  host.innerHTML=vmGridHTML(vmBase());
  const lab=document.getElementById("vm_case");
  if(lab) lab.textContent=vmShow==="reference"?"Humbird's optimistic design (a standard perfusion tank, no added equipment for oxygen and CO₂)":pgCaseWords(pgFacts());
  document.querySelectorAll(".vmbtn").forEach(b=>b.classList.toggle("on",b.getAttribute("data-vm")===vmShow));
}
function vmSet(k){ vmShow=k; vmRender(); }
