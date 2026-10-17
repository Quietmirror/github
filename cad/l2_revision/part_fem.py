"""Main-key C3D10 comparative screening with a radial pin and contact seat.

Rigid frictionless bilateral pin/seat reference constraints are comparative
fixtures, not nonlinear contact, click force or fatigue qualification.
"""
from pathlib import Path
import sys,argparse,json,numpy as np
from fem import f,ROOT,SUP
from solid_review import review
import inspect
from scipy.spatial import cKDTree
# The inherited BODY postprocessor had only three horizontal anchor nodes.
# Thousands of radial pin constraints require a tree, not an N x M array.
source=inspect.getsource(f.solve)
source=source.replace('np.linalg.norm(integration_element_centers[:,None,:]-mesh.xyz[horizontal_anchors][None,:,:],axis=2).min(axis=1)',
                      'cKDTree(mesh.xyz[horizontal_anchors]).query(integration_element_centers)[0]')
f.cKDTree=cKDTree
exec(compile(source,'l2_part_solve_with_tree','exec'),f.__dict__)
ORIGINAL_WRITER=f.write_deck
TRANSFORMS=[]
def writer(mesh,directory,young,poisson,constraints,loads):
    path=ORIGINAL_WRITER(mesh,directory,young,poisson,constraints,loads)
    text=path.read_text();extra=[]
    for name,kind,nodes,data in TRANSFORMS:
        extra.append(f'*NSET,NSET={name}')
        for offset in range(0,len(nodes),16):extra.append(','.join(str(mesh.ids[i]) for i in nodes[offset:offset+16]))
        extra.extend([f'*TRANSFORM,NSET={name},TYPE={kind}',','.join(str(float(q)) for q in data)])
    text=text.replace('*MATERIAL,NAME=PLA_IDEAL','\n'.join(extra)+'\n*MATERIAL,NAME=PLA_IDEAL')
    text=text.replace('*NODE PRINT,NSET=NALL','*NODE PRINT,NSET=NALL,GLOBAL=YES').replace('*NODE PRINT,NSET=SUPPORT','*NODE PRINT,NSET=SUPPORT,GLOBAL=YES')
    path.write_text(text,encoding='ascii');return path
f.write_deck=writer
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--variants',nargs='+',default=['R32','K16','K14','K12']);ap.add_argument('--sizes',nargs='+',type=float,default=[1.2,.9,.65]);args=ap.parse_args()
    meta=json.loads((ROOT/'reports/rebuild_r3_2/design_metadata.json').read_text())
    motion=next(m for m in meta['mechanisms']['motions'] if m['part']=='LEFT_KEY');pivot=np.array(motion['origin']);contact=np.array(motion['actuation_point'])
    normal=np.array([0.,-np.sin(np.deg2rad(18)),np.cos(np.deg2rad(18))])
    for variant in args.variants:
        base=ROOT/'exports/rebuild_r3_2' if variant=='R32' else ROOT/f'exports/l2_revision/{variant}'
        step=base/'assembly/LEFT_KEY.step';source=f.digest(step);levels=[]
        for h in args.sizes:
            work=SUP/f'work/l2/part_fem/{variant}/LEFT_KEY_h{h:g}_{source[:10]}';mesh=f.generate_mesh(work,h,step=step)
            radial=np.linalg.norm(mesh.xyz[:,1:]-pivot[1:],axis=1)
            bore=np.flatnonzero((abs(radial-1.175)<.025)&(abs(mesh.xyz[:,0]-18.3)<6.7))
            centers=mesh.centers;from_contact=centers-contact
            faceids=np.flatnonzero((abs(from_contact@normal)<.035)&(np.linalg.norm(from_contact,axis=1)<1.36)&(mesh.normals@normal<-.95))
            seat=np.unique(mesh.faces[faceids].reshape(-1))
            if len(bore)<10 or len(seat)<5:raise ValueError(('Missing pin or seat',variant,h,len(bore),len(seat)))
            assert not set(bore)&set(seat)
            TRANSFORMS[:]=[('PIN','C',bore,[0,*pivot[1:],1,*pivot[1:]]),('SEAT','R',seat,[*normal,1,0,0])]
            axial=int(bore[np.argmin(abs(mesh.xyz[bore,0]-18.3))])
            constraints=[(int(i),1) for i in bore]+[(axial,3)]+[(int(i),1) for i in seat]
            level=dict(h_mm=h,mesh=mesh.stats,bore_nodes=len(bore),seat_nodes=len(seat),cases=[])
            for label,x,y in [('center',18.3,18.),('outer',24.,18.),('inner',12.5,18.),('front',18.3,9.)]:
                mask=((centers[:,0]-x)**2+(centers[:,1]-y)**2<2.2**2)&(mesh.normals[:,2]>.4)
                loads,description=f.selected_load(mesh,mask,[0,0,-1],1.5,'LC1_'+label+'_1p5N')
                r,u=f.solve(mesh,work/description['name'],1700,.37,constraints,loads,description)
                with np.load(work/description['name']/'result_arrays.npz') as arrays:second=review(mesh,arrays,loads,1700,.37,[i for i,d in constraints])
                r.update(independent_review=second,RF_print_reactions_not_used='Transformed support constraints become MPCs; reactions independently integrated from element stresses.',
                    effective_displacement_mm=float(np.sum(loads*u)/1.5),material=dict(E_MPa=1700,nu=.37,assumption=True))
                r['effective_stiffness_N_mm']=1.5/r['effective_displacement_mm'];level['cases'].append(r)
                print(variant,h,label,'k',r['effective_stiffness_N_mm'],'independent balance',second['pass_check'],flush=True)
            levels.append(level)
            f.write_json(ROOT/f'reports/l2_revision/key_fem_{variant}.json',dict(variant=variant,part='LEFT_KEY',source_sha256=source,levels=levels,
                boundary='Rigid radial pin support on bore; axial mode removed at one bore node; bilateral frictionless seat normal to tilted switch. Reference fixture only; actual pin clearance/contact/slip and switch spring are not solved.',
                not_click_force_or_fatigue_certification=True))
if __name__=='__main__':main()
