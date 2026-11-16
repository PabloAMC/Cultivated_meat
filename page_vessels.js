/* ===== vessel types against operating modes =====
   A mirror of vessels.py (vm_for, explore_kwargs, cell); tests/run_parity.py checks the two agree. Each cell is
   floorExplore (the mirror of floor_physics.explore) with the vessel's and the mode's numbers in MODEL.vm.
   The table shows the scenario chosen in "What decides it" or the reference case, and is redrawn when a switch moves. */
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
  p.vessel_m3=V.size; p.mode=M.mode; p.vm=vm;
  if(V.fixed&&(m==="batch"||m==="fedbatch")) p.medium_l=1000/VM.batch_x;
  return p;
}
function vmLoopOk(r){ const c=r.column; return !c||(c.ph_vs_safe<=1+1e-9&&c.passes_tested); }
function vmCell(v,m,base){                      // mirror of vessels.cell
  const key=v+"|"+m, tag=VM.tags[key];
  const p=vmKwargs(v,m,base);
  if(p===null) return {possible:false, reason:VM.not_possible[key], tag:tag[0], evidence:tag[1]};
  let r=floorExplore(p), fallback="", unchecked=null;
  if(!vmLoopOk(r)){                             // the tricks' loop fails its checks here: the cheapest setting that passes
    unchecked=r.total; let best=null;
    scSwitch("tricks").settings.forEach(st=>{
      const b=Object.assign({},base); VM.trick_args.forEach(k=>{ delete b[k]; });
      const rr=floorExplore(vmKwargs(v,m,Object.assign(b,st.p)));
      if(vmLoopOk(rr)&&(best===null||rr.total<best[1].total-1e-12)) best=[st,rr];
    });
    r=best[1]; fallback=best[0].label;
  }
  let big="capital"; Object.keys(VM.biggest).forEach(k=>{ if(r[k]>r[big]) big=k; });
  return {possible:true, cost:r.total, limit:r.limit, density:r.density, output:r.output, medium_l:r.medium_l, uptime:r.uptime,
          biggest:VM.biggest[big], biggest_share:r[big]/r.total, tricks_fallback:fallback, unchecked_cost:unchecked,
          density_unshown:tag[0]===VM.tag_order[0]&&r.density>VM.x_meat_shown+1e-9,
          same_as:VM.same_as[key]?VM.same_as[key][0]:null, tag:tag[0], evidence:tag[1]};
}
function vmBase(){                              // the case the table holds fixed
  if(vmShow==="reference") return {doubling_h:24, mass_pg:3000, vessel_m3:20, plant:"sanitary", mode:"perfusion", charge:C.fx.charge_mature};
  return scParams(SCS.choice);
}
function vmMoney(x){ return "$"+(x>=1000?Math.round(x).toLocaleString("en-US"):x.toFixed(2)); }
function vmTagChip(t){ const cls=t===VM.tag_order[0]?"vt-today":t===VM.tag_order[1]?"vt-pilot":"vt-paper";
  return '<span class="vtag '+cls+'">'+t+'</span>'; }
function vmFallbackText(c){      // mirror of page_sections._vm_fallback_text
  return 'The scenario clears CO₂ with “tank tricks”: a column beside the tank that strips it without bubbles, and the options that go '+
    'with it. This vessel is taller, so the column would keep too much of the culture at a high pH, which slows cell growth. The cost '+
    'here uses the most that passes that check: “'+c.tricks_fallback+'”. With the scenario’s own tricks it would be '+vmMoney(c.unchecked_cost)+'.'; }
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
  if(lab) lab.textContent=vmShow==="reference"?"the reference case (a standard perfusion tank, no tricks)":scOwnName();
  document.querySelectorAll(".vmbtn").forEach(b=>b.classList.toggle("on",b.getAttribute("data-vm")===vmShow));
}
function vmSet(k){ vmShow=k; vmRender(); }
