"""LC6 carrier and wheel fixtures on real BReps, not a click/friction model."""
import argparse,json,numpy as np
from part_fem import f,ROOT,SUP,TRANSFORMS
from solid_review import review
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sizes',nargs='+',type=float,default=[1.0,.75,.55]);a=ap.parse_args()
    d=json.loads((ROOT/'reports/rebuild_r3_2/design_metadata.json').read_text());motion=next(q for q in d['mechanisms']['motions'] if q['part']=='WHEEL_CARRIER');pivot=np.array(motion['origin']);contact=np.array(motion['actuation_point']);result=[]
    for part in ['WHEEL_CARRIER','WHEEL']:
        step=ROOT/f'exports/rebuild_r3_2/assembly/{part}.step';source=f.digest(step);levels=[]
        for h in a.sizes:
            work=SUP/f'work/l2/wheel_fem/{part}_h{h:g}_{source[:10]}';mesh=f.generate_mesh(work,h,step=step);xyz=mesh.xyz;fc=mesh.centers;nx,ny,nz=mesh.normals.T
            if part=='WHEEL_CARRIER':
                bore=np.flatnonzero((abs(np.linalg.norm(xyz[:,1:]-pivot[1:],axis=1)-1.175)<.025)&(abs(xyz[:,0])<3.1))
                seatfaces=(abs(fc[:,2]-contact[2])<.035)&((fc[:,0]-contact[0])**2+(fc[:,1]-contact[1])**2<1.15**2)&(nz<-.9)
                seat=np.unique(mesh.faces[np.flatnonzero(seatfaces)].reshape(-1));assert len(bore)>10 and len(seat)>3,(len(bore),len(seat))
                TRANSFORMS[:]=[('PIN','C',bore,[0,*pivot[1:],1,*pivot[1:]])]
                axial=int(bore[np.argmin(abs(xyz[bore,0]))]);constraints=[(int(i),1) for i in bore]+[(axial,3)]+[(int(i),3) for i in seat]
                radius=np.linalg.norm(fc[:,1:]-[28.,19.],axis=1)
                bearing=(fc[:,0]<-4)&(fc[:,0]>-7)&(abs(radius-1.175)<.06)&(nz>.35)
                platform=(fc[:,0]>2.8)&(fc[:,0]<8.7)&(fc[:,1]>23)&(fc[:,1]<33)&(abs(fc[:,2]-12)<.05)&(nz>.9)
                q1,d1=f.selected_load(mesh,bearing,[0,0,-1],.75,'wheel_round_journal_share')
                q2,d2=f.selected_load(mesh,platform,[0,0,-1],.75,'encoder_foot_share')
                loads=q1+q2;desc=dict(name='LC6_middle_press_1p5N_carrier',components=[d1,d2],magnitude_N=1.5)
            else:
                TRANSFORMS[:]=[]
                # Purchased encoder hub and opposite radial journal are rigid
                # fixture surfaces. No claim of encoder shaft stiffness.
                end=np.flatnonzero((xyz[:,0]>8.80)|(xyz[:,0]<-7.20))
                assert len(end)>8;constraints=[(int(i),q) for i in end for q in [1,2,3]]
                loads,desc=f.selected_load(mesh,(abs(fc[:,0])<2.5)&(abs(fc[:,1]-28)<2)&(nz>.65),[0,0,-1],1.5,'LC6_middle_press_1p5N_wheel')
            out,u=f.solve(mesh,work/desc['name'],1700,.37,constraints,loads,desc)
            with np.load(work/desc['name']/'result_arrays.npz') as arrays:check=review(mesh,arrays,loads,1700,.37,[i for i,q in constraints])
            out.update(h_mm=h,independent_review=check,effective_stiffness_N_mm=2.25/float(np.sum(loads*u)));levels.append(out)
            print(part,h,out['effective_stiffness_N_mm'],check['pass_check'],flush=True)
        result.append(dict(part=part,source_sha256=source,levels=levels))
        f.write_json(ROOT/'reports/l2_revision/wheel_fem.json',dict(parts=result,material_assumption='E1700 MPa, nu0.37 isotropic PA12 assumption',
            boundary='Carrier: radial rear hinge and rigid middle-switch seat, half load on wheel journal and half on encoder cradle. Wheel: rigid end supports. Actual encoder/PCB/steel compliance, wheel torque/friction, switch spring and fatigue are unverified.',
            applicability='Selected L2 variants retain the exact R3.2 wheel/carrier files; equality checked in delivery manifest.'))
if __name__=='__main__':main()
