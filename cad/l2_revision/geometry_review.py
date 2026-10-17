"""Exact foot-datum checks, bounded BRep wall rays and cap normal offsets."""
from pathlib import Path
import sys,json,math,ctypes,importlib.util,numpy as np,cadquery as cq,trimesh
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
from mechanics import cylinder
from audit_baseline import volume
def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    v=sys.argv[1];rp=ROOT/f'reports/l2_revision/{v}';base=ROOT/f'exports/l2_revision/{v}'
    d=json.loads((rp/'design_metadata.json').read_text());body=cq.importers.importStep(str(base/'assembly/BODY.step')).val();mesh=trimesh.load_mesh(base/'assembly/BODY.stl')
    feet=[]
    for q in d['mechanisms']['feet']:
        x,y=q['center'];disk=cylinder(4.,1.6,(x,y,5.2));missing=volume(disk.cut(body))[0];under=volume(body.intersect(cylinder(3.999,10.2,(x,y,-5))))[0]
        faces=[f for f in body.Faces() if f.BoundingBox().zlen<1e-6 and abs(f.BoundingBox().zmin-5.2)<1e-6 and math.hypot(f.Center().x-x,f.Center().y-y)<4]
        area=sum(f.Area() for f in faces)
        feet.append(dict(center_xy_mm=[x,y],z_mm=5.2,diameter_mm=8.,land_thickness_mm=1.6,missing_mm3=missing,under_mm3=under,area_mm2=area,pass_check=abs(missing)<1e-5 and abs(under)<1e-5 and abs(area-16*math.pi)<.5))
    reserve=cq.importers.importStep(str(base/'gauges/SENSOR_RESERVED_VOLUME.step')).val()
    mother=trimesh.load_mesh(base/'gauges/MOTHER_OUTER_REFERENCE.stl');caps=[]
    for n in ['SIDE_FRONT_KEY','SIDE_REAR_KEY']:
        m=trimesh.load_mesh(base/f'assembly/{n}.stl');points,ids=trimesh.sample.sample_surface(m,1600,seed=73)
        touch=points[(m.face_normals[ids,0]>.7)&(points[:,0]>27)]
        near,distance,face=trimesh.proximity.closest_point(mother,touch);signed=np.einsum('ij,ij->i',touch-near,mother.face_normals[face])
        internal=int(np.sum(signed<-.75));signed=signed[signed>=-.75]
        caps.append(dict(part=n,samples=len(signed),excluded_deep_internal_slider_face_samples=internal,normal_offset_min_mm=float(signed.min()),normal_offset_max_mm=float(signed.max()),normal_offset_P95_mm=float(np.percentile(signed,95)),max_normal_target_mm=.35,pass_check=bool(signed.max()<.35+.035),scope='Finite samples on outward cap faces; samples more than0.75mm inward are hidden slider faces, recorded separately. No positive protrusion sample discarded. Normal comes from independent mother-skin mesh; not exhaustive curvature certification.'))
    points,ids=trimesh.sample.sample_surface(mesh,10000,seed=317);norm=mesh.face_normals[ids]
    grip=(abs(points[:,0])>27)&(points[:,1]>43)&(points[:,1]<61)&(points[:,2]>9)&(points[:,2]<13)&(abs(norm[:,0])>.7)
    chosen=np.flatnonzero(grip)[::max(1,int(grip.sum()/50))][:50];rays=[]
    for j in chosen:
        p=points[j];n=norm[j];line=cq.Edge.makeLine(cq.Vector(*(p+n*.12)),cq.Vector(*(p-n*12.)))
        edges=body.intersect(line).Edges();edges.sort(key=lambda e:float((np.array(e.Center().toTuple())-p)@(-n)))
        lengths=[e.Length() for e in edges if e.Length()>.001]
        rays.append(dict(point=p.tolist(),normal=n.tolist(),solid_intervals_mm=lengths,first_interval_mm=lengths[0] if lengths else None))
    # Exact BRep interval lengths; no declaration of exhaustive minimum wall.
    report=dict(variant=v,feet=feet,five_feet_coplanar=all(q['pass_check'] for q in feet),sensor_reserve_bottom_mm=reserve.BoundingBox().zmin,
        foot_to_reserve_datum_difference_mm=abs(5.2-reserve.BoundingBox().zmin),cap_normal_offsets=caps,grip_BRep_rays=rays,
        body_bounds_mm=[[mesh.bounds[0,i],mesh.bounds[1,i]] for i in range(3)],
        example_skate_mm=.5,example_ground_z_mm=4.7,body_ground_clearance_mm=float(mesh.bounds[0,2]-4.7),
        global_minimum_wall_certified=False,scope='Exact native foot surfaces and BRep line intersections at a bounded set of grip samples. Ray direction comes from delivered mesh. No global thickness or material strength claim.')
    (rp/'geometry_second_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('GEOMETRY',v,'feet',report['five_feet_coplanar'],'caps',[q['normal_offset_max_mm'] for q in caps],flush=True)
    spec=importlib.util.spec_from_file_location('thickness_base',ROOT/'cad/rebuild_r3_2/thickness_check.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    old.RP=rp;old.OUT=base/'assembly';old.main()
if __name__=='__main__':main()
