"""Record measured digital gates separately from unproved product acceptance."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'reports/l2_revision'
def read(p):return json.loads(p.read_text())
def main():
 v=sys.argv[1];r=RP/v;f=read(RP/f'fem_{v}.json');ref=read(RP/'fem_R32.json');second=read(RP/f'body_second_review_{v}.json');geo=read(r/'geometry_second_review.json')
 geometry={n:read(r/(n+'.json'))['pass_check'] for n in ['mesh_and_volume','static_checks','motion_checks','insertion_checks','native_freecad_checks','slice_summary','toolpath_review']}
 geometry.update(five_feet=geo['five_feet_coplanar'],cap_normals=all(q['pass_check'] for q in geo['cap_normal_offsets']),direct_side_entry=all(q['pass_check'] for q in read(r/'side_direct_insertion.json')))
 comparison=[]
 for a,b in zip(ref['levels'][-1]['cases'],f['levels'][-1]['cases']):comparison.append(dict(case=a['case']['name'],R32_k=a['effective_stiffness_N_mm'],selected_k=b['effective_stiffness_N_mm'],ratio=b['effective_stiffness_N_mm']/a['effective_stiffness_N_mm'],R32_P99=a['volume_weighted_P99_vm_MPa'],selected_P99=b['volume_weighted_P99_vm_MPa']))
 checks=dict(three_mesh_levels=len(f['levels'])>=3,last_grid_k_change_below_2_percent=all(q['stiffness_relative_change']<.02 for q in f['convergence'][-1]['cases']),
  principal_daily_BODY_stiffness_not_lower=all(q['ratio']>=1 for q in comparison),independent_base_review=all(q['independent_review']['pass_check'] for q in second['cases']),independent_extra_review=all(q['independent_review']['pass_check'] for q in second['extra_cases']))
 extras=[];baseline={q['case']['name']:q for q in read(RP/'body_second_review_R32.json')['extra_cases']}
 for q in second['extra_cases']:
  n=q['case']['name']
  if n in baseline:extras.append(dict(case=n,R32_k=baseline[n]['effective_stiffness_N_mm'],selected_k=q['effective_stiffness_N_mm'],ratio=q['effective_stiffness_N_mm']/baseline[n]['effective_stiffness_N_mm']))
 mass=read(r/'mesh_and_volume.json')['total_PA12_g'];source=ROOT/f'exports/l2_revision/{v}/assembly/BODY.step'
 result=dict(variant=v,status='COMMON_SHELL_REVIEWED_FOR_LAYOUT_RESEARCH',digital_geometry_reviewed=all(geometry.values()),numerical_reviewed=all(checks.values()),
  geometry_checks=geometry,numerical_checks=checks,principal_comparison=comparison,secondary_fixture_comparison=extras,
  source_BODY_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),baseline_commit='f1b1090931d717117287ea2b79c2e14ddc234937',
  actual_PA12_g=mass,target_PA12_g=14.89,mass_target_met=mass<=14.89,full_master_spec_acceptance=False,
  physical_strength_certified=False,hardware_fit_certified=False,
  scope='Frozen geometry for explicitly estimated H/D layout and prototype documentation only. Principal BODY daily-load screens pass; secondary rigid-grip lift/service stiffness changes are reported, not suppressed. This is not an unrestricted production release or proof that every specification gate is satisfied.',
  remaining=['14.89 g target not achieved','Unknown printed material anisotropy, allowable stress, fatigue, friction and actual switch overtravel','Secondary LC5/LC7 fixture losses, if present, need physical comparison; no blanket non-degradation claim','Actual PCB/optical stack/retention and electrical functionality unverified','FDM tiny fits need test coupons, reaming and measured stop adjustment'])
 (r/'common_gate.json').write_text(json.dumps(result,indent=2)+'\n');assert result['digital_geometry_reviewed'] and result['numerical_reviewed'],result
 # Correct the generic exporter mass field for the nine printable parts.
 met=read(r/'cad_metrics.json')
 for q in read(r/'mesh_and_volume.json')['parts']:
  m=met[q['part']];m['legacy_default_Occ_volume_mm3']=m['volume_mm3'];m['volume_mm3']=q['adaptive_CAD_mm3'];m['volume_method']='adaptive native integration tolerance1e-7, authoritative for trimmed BRep'
 (r/'cad_metrics.json').write_text(json.dumps(met,indent=2)+'\n');print(result['status'],mass,'g; target not met; secondary',extras,flush=True)
 d=read(r/'design_metadata.json')
 d['mechanisms']['installation'][1]=dict(step=2,parts=['SWITCH_SIDE_FRONT','SWITCH_SIDE_REAR','SIDE_REAR_KEY_SWITCH_CLAMP','SIDE_FRONT_KEY_SWITCH_CLAMP'],action='Front switch first from underside, then rear switch; follow insertion_checks.json offsets. Install rear clamp before front clamp. The old nose-entry sequence failed and is superseded. Add fasteners afterward; tool-handle/threaded insertion not continuously certified.')
 d['mechanisms']['installation_source']='reports/l2_revision/'+v+'/insertion_checks.json; sampled actual retained meshes'
 (r/'design_metadata.json').write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
