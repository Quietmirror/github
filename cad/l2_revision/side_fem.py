"""Actual side-cap C3D10 press screening; guide contact is a stated fixture."""
import argparse,json,numpy as np
from part_fem import f,ROOT,SUP
from solid_review import review
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--variant',default='F1E');ap.add_argument('--sizes',nargs='+',type=float,default=[.9,.65,.5]);args=ap.parse_args()
    base=ROOT/'exports/rebuild_r3_2' if args.variant=='R32' else ROOT/f'exports/l2_revision/{args.variant}'
    rp=ROOT/'reports/rebuild_r3_2' if args.variant=='R32' else ROOT/f'reports/l2_revision/{args.variant}'
    design=json.loads((rp/'design_metadata.json').read_text());allparts=[]
    for motion in design['mechanisms']['side_motions']:
        name=motion['part'];tip=np.array(motion['actuation_point']);cx,cy,cz=tip
        touch=next(q for q in design['side_touch_geometry'] if q.get('name',q.get('part'))==name)
        touch_y=touch.get('new_touch_center_y',touch.get('cap_center',[0,cy,cz])[1]);length=touch.get('length_y_mm',touch.get('touch_length_y_mm',10.4))
        step=base/f'assembly/{name}.step';source=f.digest(step);levels=[]
        for h in args.sizes:
            work=SUP/f'work/l2/side_fem/{args.variant}/{name}_h{h:g}_{source[:10]}';mesh=f.generate_mesh(work,h,step=step)
            xyz=mesh.xyz;fc=mesh.centers;nx,ny,nz=mesh.normals.T
            guide=motion.get('guide_length_mm',3.8)
            # Full-stroke guide mapped back to the undeformed key frame:
            # fixed guide +0.6 X, then clipped to the actual slider end.
            xinner=cx+6.4-guide;xouter=cx+6.1
            yfaces=(abs(abs(fc[:,1]-cy)-2.6)<.02)&(abs(ny)>.95)&(fc[:,0]>xinner)&(fc[:,0]<xouter)
            zfaces=(abs(abs(fc[:,2]-cz)-1.7)<.02)&(abs(nz)>.95)&(fc[:,0]>xinner)&(fc[:,0]<xouter)
            seatfaces=(abs(fc[:,0]-cx)<.02)&((fc[:,1]-cy)**2+(fc[:,2]-cz)**2<1.02**2)&(nx<-.95)
            groups=[np.unique(mesh.faces[np.flatnonzero(mask)].reshape(-1)) for mask in [seatfaces,yfaces,zfaces]]
            assert all(len(g)>=4 for g in groups),(name,h,[len(g) for g in groups])
            constraints=[(int(i),d) for d,g in zip([1,2,3],groups) for i in g]
            level=dict(h_mm=h,mesh=mesh.stats,guide_nodes=[len(g) for g in groups],cases=[])
            for label,dy in [('front',-.32*length),('center',0.),('rear',.32*length)]:
                mask=(nx>.65)&(fc[:,0]>cx+5.9)&((fc[:,1]-touch_y-dy)**2+(fc[:,2]-cz)**2<1.25**2)
                loads,description=f.selected_load(mesh,mask,[-1,0,0],1.5,'LC2_'+label+'_1p5N')
                result,u=f.solve(mesh,work/description['name'],1700,.37,constraints,loads,description)
                with np.load(work/description['name']/'result_arrays.npz') as arrays:check=review(mesh,arrays,loads,1700,.37,[i for i,d in constraints])
                result.update(independent_review=check,effective_displacement_mm=float(np.sum(loads*u)/1.5))
                result['effective_stiffness_N_mm']=1.5/result['effective_displacement_mm'];level['cases'].append(result)
                print(args.variant,name,h,label,result['effective_stiffness_N_mm'],check['pass_check'],flush=True)
            levels.append(level)
        allparts.append(dict(part=name,levels=levels,source_sha256=source))
        f.write_json(ROOT/f'reports/l2_revision/side_fem_{args.variant}.json',dict(variant=args.variant,parts=allparts,
            boundary='Bilateral frictionless slider bearing planes and rigid actuator seat. No real clearance take-up, friction, switch spring, wear or physical jamming certification.',
            material=dict(E_MPa=1700,nu=.37,assumptions=True)))
if __name__=='__main__':main()
