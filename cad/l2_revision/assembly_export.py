"""Named, unfused assembly STEP and auditable per-component manifest."""
from pathlib import Path
import sys,json,ctypes,cadquery as cq
from audit_baseline import volume
ROOT=Path(__file__).resolve().parents[2]
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    v=sys.argv[1];base=ROOT/f'exports/l2_revision/{v}';rp=ROOT/f'reports/l2_revision/{v}'
    met=json.loads((rp/'cad_metrics.json').read_text());assembly=cq.Assembly(name='Quietmirror_'+v);rows=[]
    for name,m in met.items():
        path=base/f'assembly/{name}.step';s=cq.importers.importStep(str(path)).val();assert s.isValid() and len(s.Solids())==1,name
        printed=m['printable'];color=(.18,.38,.43) if printed else (.72,.48,.2)
        if name in ['LEFT_KEY','RIGHT_KEY']:color=(.72,.81,.77)
        if name in ['SIDE_FRONT_KEY','SIDE_REAR_KEY']:color=(.84,.59,.25)
        if name=='WHEEL':color=(.17,.21,.23)
        assembly.add(s,name=name,color=cq.Color(*color));vol=volume(s)[0]
        rows.append(dict(part=name,printable=printed,adaptive_CAD_mm3=vol,PA12_g=vol*.00101 if printed else None,PLA_solid_g=vol*.00124 if printed else None,
            measured_mass_g=None,source_step=str(path.relative_to(ROOT)).replace('\\','/'),status='Original printable geometry' if printed else 'Purchased hardware mechanical reference; supplier and measured fit unverified'))
    path=base/(v+'_FULL_ASSEMBLY.step');assembly.save(str(path),exportType='STEP')
    back=cq.importers.importStep(str(path)).val();assert back.isValid() and len(back.Solids())==len(rows)
    result=dict(variant=v,parts=rows,assembly_step=str(path.relative_to(ROOT)).replace('\\','/'),named_unfused_components=len(rows),step_reimport_valid=back.isValid(),
        printable_count=sum(q['printable'] for q in rows),PA12_total_g=sum(q['PA12_g'] or 0 for q in rows),PLA_solid_total_g=sum(q['PLA_solid_g'] or 0 for q in rows),
        electronics_fit_certified=False,fatigue_or_click_tested=False)
    (rp/'assembly_manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(v,'named STEP',len(rows),flush=True)
if __name__=='__main__':main()
