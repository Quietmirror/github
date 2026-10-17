"""FreeCADCmd native save/reopen; imported BReps and source, not solved joints."""
from pathlib import Path
import os,json,traceback
import FreeCAD as App
import Part
ROOT=Path(os.environ['QUIETMIRROR_ROOT']);variant=os.environ['QM_L2_VARIANT']
OUT=ROOT/f'exports/l2_revision/{variant}';RP=ROOT/f'reports/l2_revision/{variant}'
def main():
    met=json.loads((RP/'cad_metrics.json').read_text());doc=App.newDocument('Quietmirror_'+variant)
    printed=doc.addObject('App::DocumentObjectGroup','PrintedParts');hardware=doc.addObject('App::DocumentObjectGroup','HardwareReferences')
    info=doc.addObject('App::FeaturePython','DesignInfo')
    for key,val in dict(Revision=variant,Units='mm',Source='cad/l2_revision; MASTER_SPEC.md and per-variant source_parameters.json',
        Editing='Editable imported BReps. Parameterised Python source accompanies this document; no reconstructed sketch tree or solved assembly joints.',
        Evidence='Research geometry. See reports/l2_revision/'+variant+'. Electronics, optical stack, physical click/friction and fatigue are not certified.',
        Mass='PA12 density1.01g/cm3 assumption; 14.89g is a target, not a result. PLA slicing is reported separately.').items():
        info.addProperty('App::PropertyString',key,'Design');setattr(info,key,val)
    expected={}
    for name,m in met.items():
        shape=Part.Shape();shape.read(str(OUT/f'assembly/{name}.step'));assert shape.isValid() and len(shape.Solids)==1,name
        obj=doc.addObject('Part::Feature',name);obj.Label=name;obj.Shape=shape
        obj.addProperty('App::PropertyBool','PrintInPLA','Manufacture');obj.PrintInPLA=m['printable']
        obj.addProperty('App::PropertyString','SourceSTEP','Manufacture');obj.SourceSTEP=f'assembly/{name}.step'
        (printed if m['printable'] else hardware).addObject(obj);expected[name]=shape.Volume
    doc.recompute();path=OUT/(variant+'_FULL_ASSEMBLY.FCStd');doc.saveAs(str(path));App.closeDocument(doc.Name)
    check=App.openDocument(str(path));rows=[]
    for name,volume in expected.items():
        obj=check.getObject(name);s=obj.Shape;diff=abs(s.Volume-volume);rows.append(dict(part=name,valid=s.isValid(),solids=len(s.Solids),save_reopen_volume_difference_mm3=diff,pass_check=s.isValid() and len(s.Solids)==1 and diff<1e-4))
    App.closeDocument(check.Name)
    result=dict(application='FreeCAD '+'.'.join(App.Version()[:3]),variant=variant,file=str(path.relative_to(ROOT)).replace('\\','/'),parts=rows,pass_check=all(q['pass_check'] for q in rows),
        scope='Actual native save/reopen and same BRep volume check. Imported parts, not sketch feature history or kinematic assembly joints. Default FreeCAD volume is used only for same-file persistence equality, never for trimmed-body mass.')
    (RP/'native_freecad_checks.json').write_text(json.dumps(result,indent=2)+'\n');assert result['pass_check'];print('Native',variant,len(rows),'parts saved/reopened',flush=True)
try:main()
except Exception:
    (RP/'native_ERROR.txt').write_text(traceback.format_exc());raise
