"""Independent force/work check and explicitly bounded extra BODY fixtures."""
from pathlib import Path
import argparse,json,numpy as np
from fem import f,ROOT,SUP,cases,supports,free_supports
from solid_review import review
import inspect
from scipy.spatial import cKDTree
# Keep memory bounded for finite-area grip restraints.
source=inspect.getsource(f.solve).replace('np.linalg.norm(integration_element_centers[:,None,:]-mesh.xyz[horizontal_anchors][None,:,:],axis=2).min(axis=1)',
    'cKDTree(mesh.xyz[horizontal_anchors]).query(integration_element_centers)[0]')
f.cKDTree=cKDTree
exec(compile(source,'l2_body_review_tree','exec'),f.__dict__)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('variant');ap.add_argument('--h',type=float,default=1.8);ap.add_argument('--extra',action='store_true');ap.add_argument('--targeted',action='store_true');a=ap.parse_args()
    step=ROOT/('exports/rebuild_r3_2/assembly/BODY.step' if a.variant=='R32' else f'exports/l2_revision/{a.variant}/assembly/BODY.step')
    digest=f.digest(step);work=f.WORK/a.variant/f'h{a.h:g}_{digest[:10]}';mesh=f.generate_mesh(work,a.h,step=step)
    d=json.loads((ROOT/'reports/rebuild_r3_2/design_metadata.json').read_text());feet=[q['center'] for q in d['mechanisms']['feet']]
    output=dict(variant=a.variant,source_sha256=digest,h_mm=a.h,cases=[],extra_cases=[])
    for loads,desc in cases(mesh):
        constraints,pads,boundary=free_supports(mesh,feet) if desc.get('support_mode') else supports(mesh,feet)
        result_dir=work/desc['name']
        with np.load(result_dir/'result_arrays.npz') as arrays:
            check=review(mesh,arrays,loads,1700,.37,[i for i,dof in constraints])
        output['cases'].append(dict(name=desc['name'],independent_review=check))
    if a.extra:
        # Fixture sensitivity and load/material scaling use the same mesh,
        # geometry and loaded facets, avoiding geometry changes masquerading
        # as a material or boundary comparison.
        loads,desc=cases(mesh)[0]
        sensitivity=[('anchor_swap',1700,.37,1.,True),('half_load',1700,.37,.5,False),('high_load',1700,.37,1.5,False),('low_modulus',1200,.37,1.,False),('high_modulus',2200,.37,1.,False),('low_poisson',1700,.30,1.,False)]
        if a.targeted:sensitivity=[q for q in sensitivity if q[0] in ['anchor_swap','low_poisson']]
        for label,E,nu,scale,swap in sensitivity:
            constraints,pads,boundary=supports(mesh,feet,anchor_swap=swap)
            applied=loads*scale;description=dict(desc,name='LC4_sensitivity_'+label,load_scale=scale)
            result,u=f.solve(mesh,work/description['name'],E,nu,constraints,applied,description,pads)
            F=5*scale;result['effective_stiffness_N_mm']=F*F/float(np.sum(applied*u))
            with np.load(work/description['name']/'result_arrays.npz') as arrays:check=review(mesh,arrays,applied,E,nu,[i for i,dof in constraints])
            result.update(independent_review=check,boundary=boundary)
            output['extra_cases'].append(result);print(a.variant,label,result['effective_stiffness_N_mm'],check['pass_check'],flush=True)
        # LC5: a pair of explicitly rigid hand-contact patches, bounded by
        # a simple fixture rather than an invented skin friction coefficient.
        x,y,z=mesh.centers.T;nx,ny,nz=mesh.normals.T
        grip=(abs(x)>29)&(y>48)&(y<55)&(z>9)&(z<13)&(abs(nx)>.7)
        nodes=np.unique(mesh.faces[np.flatnonzero(grip)].reshape(-1));assert len(nodes)>12
        constraints=[(int(i),dof) for i in nodes for dof in [1,2,3]]
        load,desc=f.selected_load(mesh,(x<-12)&(y>73)&(y<81)&(nz>.35),[0,0,1],2.,'LC5_rear_corner_lift_2N_rigid_grip_fixture')
        result,u=f.solve(mesh,work/desc['name'],1700,.37,constraints,load,desc)
        result['effective_stiffness_N_mm']=4/float(np.sum(load*u));result['scope']='Local twist/lift screening with two rigid hand patches. No measured finger friction, body acceleration or complete assembly contact.'
        with np.load(work/desc['name']/'result_arrays.npz') as arrays:result['independent_review']=review(mesh,arrays,load,1700,.37,nodes)
        output['extra_cases'].append(result)
        # LC7: one real upper PCB-ear land, without using a PCB as a brace.
        cx,cy,cz=d['mechanisms']['pcb_mounting_ears'][0]['center'] if 'pcb_mounting_ears' in d['mechanisms'] else [27.331,43.,9.5]
        patch=(abs(x-cx)<3.7)&(abs(y-cy)<3.7)&(abs(z-10.75)<.03)&(nz>.9)
        load,desc=f.selected_load(mesh,patch,[0,0,-1],2.,'LC7_one_PCB_ear_service_2N')
        constraints,pads,boundary=supports(mesh,feet);result,u=f.solve(mesh,work/desc['name'],1700,.37,constraints,load,desc,pads)
        result['effective_stiffness_N_mm']=4/float(np.sum(load*u));result['scope']='2 N downward maintenance load on an existing ear face; no screw preload, plastic creep or thread stripping calculation.'
        with np.load(work/desc['name']/'result_arrays.npz') as arrays:result['independent_review']=review(mesh,arrays,load,1700,.37,[i for i,dof in constraints])
        output['extra_cases'].append(result)
    output['scope']='Independent second numerical method on stated fixtures; not independent hardware tests or printed-material certification.'
    f.write_json(ROOT/f'reports/l2_revision/body_second_review_{a.variant}.json',output)
if __name__=='__main__':main()
