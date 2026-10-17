"""Actual 3D C3D10 analysis, R3.2 and L2, explicit bounded fixture assumptions."""
from pathlib import Path
import importlib.util,sys,json,argparse,os,numpy as np
ROOT=Path(__file__).resolve().parents[2]; SUP=ROOT.parent/'_support'
spec=importlib.util.spec_from_file_location('fem_r2',ROOT/'cad/rebuild_r2/fem_check.py')
f=importlib.util.module_from_spec(spec);sys.modules[spec.name]=f;spec.loader.exec_module(f)
f.WORK=SUP/'work/l2/fem';f.REPORT=ROOT/'reports/l2_revision';f.low_priority()

def supports(mesh,centers,datum=5.2,anchor_swap=False):
    pads=[]
    for c in centers:
        ids=np.flatnonzero((abs(mesh.xyz[:,2]-datum)<.025)&(np.linalg.norm(mesh.xyz[:,:2]-c,axis=1)<4.03))
        if len(ids)<6:raise ValueError(('Too few datum nodes',c,len(ids)))
        pads.append(ids)
    aidx,bidx=(2,3) if anchor_swap else (0,1)
    a=int(pads[aidx][np.argmin(np.linalg.norm(mesh.xyz[pads[aidx],:2]-centers[aidx],axis=1))])
    b=int(pads[bidx][np.argmin(np.linalg.norm(mesh.xyz[pads[bidx],:2]-centers[bidx],axis=1))])
    constraints=[(int(i),3) for g in pads for i in g]+[(a,1),(a,2),(b,2)]
    return constraints,pads,dict(foot_datum_mm=datum,pad_nodes=[len(g) for g in pads],
       horizontal_anchor_xyz=[mesh.xyz[a].tolist(),mesh.xyz[b].tolist()],
       assumption='Five bilateral Z-only pad supports; minimum three in-plane rigid-body restraints. Negative normal reactions invalidate a free, unbonded, all-feet-down contact interpretation.')

def cases(mesh):
    x,y,z=mesh.centers.T; nx,ny,nz=mesh.normals.T
    top=f.selected_load(mesh,(y>44)&(y<71)&(abs(x)<24)&(z>23)&(nz>.3),[0,0,-1],5,'LC4_back_press_5N')
    sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
    from surfaces import half_width,roof_height
    p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text())
    w=np.array([half_width(q,p) for q in y]);h=np.array([roof_height(q,p) for q in y])
    ratio=np.clip((z-5)/(h-5),0,1);expected=w*np.maximum(0,1-ratio**3.4)**(1/3.4)
    skin=abs(abs(x)-expected)<.12
    left=f.selected_load(mesh,skin&(x>27)&(y>44)&(y<59)&(z>9)&(z<13)&(nx>.7),[-1,0,0],2,'LC3_left_outer_skin_2N')
    right=f.selected_load(mesh,skin&(x<-27)&(y>44)&(y<59)&(z>9)&(z<13)&(nx<-.7),[1,0,0],2,'LC3_right_outer_skin_2N')
    # Matching force centroids give a truly self-equilibrated pinch. The
    # positive linear traction adjustment avoids an accidental force couple
    # from different surface meshes/areas on the two sides.
    for loads,description in (left,right):
        sign=np.sign(loads[:,0].sum());weights=loads[:,0]*sign
        Q=np.c_[np.ones(len(weights)),mesh.xyz[:,1]-51.5,mesh.xyz[:,2]-11.]
        coefficients=np.linalg.solve(Q.T@(weights[:,None]*Q),[2.,0.,0.])
        factors=Q@coefficients;active=abs(weights)>1e-12
        assert factors[active].min()>0,'Traction adjustment changed force direction'
        loads[:,0]=sign*weights*factors
        description.update(centroid_target_yz_mm=[51.5,11.],linear_pressure_adjustment_coefficients=coefficients.tolist(),
                           adjustment_factor_range=[float(factors[active].min()),float(factors[active].max())],
                           actual_force_sum_N=loads.sum(axis=0).tolist())
    combined=left[0]+right[0];moment=np.cross(mesh.xyz,combined).sum(axis=0)
    assert np.linalg.norm(moment)<1e-8 and np.linalg.norm(combined.sum(axis=0))<1e-8
    return [top,(combined,dict(name='LC3_free_equilibrated_outer_grip_4N',components=[left[1],right[1]],support_mode='free_rigid_modes_only',
        actual_force_sum_N=combined.sum(axis=0).tolist(),actual_moment_sum_Nmm=moment.tolist(),
        physical_scope='Self-equilibrated opposed outer-skin normal grip in air; no desk-contact fixture and no claimed friction/weight dynamics.'))]

def free_supports(mesh,centers):
    targets=[[*centers[0],5.2],[*centers[1],5.2],[*centers[-1],5.2]]
    a,b,c=[int(np.argmin(np.linalg.norm(mesh.xyz-q,axis=1))) for q in targets]
    constraints=[(a,1),(a,2),(a,3),(b,2),(b,3),(c,3)]
    return constraints,None,dict(type='Minimum 3-2-1 constraints remove exactly six rigid modes from a self-equilibrated free body.',
        nodes_xyz=[mesh.xyz[i].tolist() for i in [a,b,c]],acceptance='Support reactions should be negligible; no finite-area clamp or bilateral pad support in this load case.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--version',default='R32');ap.add_argument('--sizes',nargs='+',type=float,default=[2.4,1.8,1.3]);ap.add_argument('--benchmark',action='store_true');ap.add_argument('--solver');args=ap.parse_args()
    if args.solver:os.environ['QM_FEM_LINEAR_SOLVER']=args.solver
    if args.benchmark:f.beam_benchmark();return
    step=ROOT/'exports/rebuild_r3_2/assembly/BODY.step' if args.version=='R32' else ROOT/f'exports/l2_revision/{args.version}/assembly/BODY.step'
    source=f.digest(step);d=json.loads((ROOT/'reports/rebuild_r3_2/design_metadata.json').read_text());centers=[q['center'] for q in d['mechanisms']['feet']]
    report=dict(version=args.version,source_step_sha256=source,analysis='Actual 3D isotropic linear elastic BODY fixture screening only',
                not_full_assembly_certification=True,material=dict(E_MPa=1700,nu=.37,density_for_mass_g_cm3=1.01,all_assumptions=True),levels=[])
    saved=f.REPORT/f'fem_{args.version}.json'
    if saved.exists():
        old=json.loads(saved.read_text())
        if old['source_step_sha256']==source:report['levels']=[q for q in old['levels'] if q['h_mm'] not in args.sizes]
    for h in args.sizes:
        work=f.WORK/args.version/f'h{h:g}_{source[:10]}';mesh=f.generate_mesh(work,h,step=step)
        level=dict(h_mm=h,mesh=mesh.stats,cases=[])
        for loads,description in cases(mesh):
            constraints,pads,boundary=free_supports(mesh,centers) if description.get('support_mode')=='free_rigid_modes_only' else supports(mesh,centers)
            result,u=f.solve(mesh,work/description['name'],1700,.37,constraints,loads,description,pads)
            result['material']['model']='Homogeneous isotropic linear elasticity; PA12 engineering assumption, not measured printed material.'
            F=sum(c['magnitude_N'] for c in description.get('components',[])) or description['magnitude_N']
            compliance=float((loads*u).sum()); delta=compliance/F
            result.update(observation='Work-conjugate surface displacement sum(F_i dot u_i)/sum(load magnitudes)',
                          effective_displacement_mm=delta,effective_stiffness_N_mm=F/delta,support=boundary)
            with np.load(work/description['name']/'result_arrays.npz') as arrays:
                vm=arrays['von_mises_MPa']; ss=arrays['stress_element_ids']; ii=arrays['stress_integration_points']-1
                weight=mesh.quadrature_volumes[np.searchsorted(mesh.eids,ss),ii];order=np.argsort(vm)
                result['volume_weighted_P99_vm_MPa']=float(np.interp(.99*weight.sum(),np.cumsum(weight[order]),vm[order]))
            level['cases'].append(result)
            print(args.version,h,description['name'],'k',result['effective_stiffness_N_mm'],'u',result['maximum_displacement_mm'],flush=True)
        report['levels'].append(level)
        report['levels'].sort(key=lambda q:q['h_mm'],reverse=True)
        f.write_json(f.REPORT/f'fem_{args.version}.json',report)
    report['convergence']=[]
    for a,b in zip(report['levels'],report['levels'][1:]):
        report['convergence'].append(dict(coarse_h=a['h_mm'],fine_h=b['h_mm'],cases=[dict(name=x['case']['name'],
            stiffness_relative_change=abs(x['effective_stiffness_N_mm']/y['effective_stiffness_N_mm']-1),
            P99_relative_change=abs(x['volume_weighted_P99_vm_MPa']/y['volume_weighted_P99_vm_MPa']-1)) for x,y in zip(a['cases'],b['cases'])]))
    report['limit']='These two BODY cases do not validate side-key friction, assembly contacts, main-key eccentric bending, fatigue, impacts, RF or optics. No COMMON_SHELL_REVIEWED assertion.'
    f.write_json(f.REPORT/f'fem_{args.version}.json',report)

if __name__=='__main__':main()
