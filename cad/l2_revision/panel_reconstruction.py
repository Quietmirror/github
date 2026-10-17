"""New, fully specified CST plane-stress proxy; NOT a 3D mouse strength test.

The historical numbers lack sufficient inputs for unique reproduction. This
independent proxy defines coordinates, triangulation, boundary and loading.
P0 uses the actual source R0.85 openings; P1 uses equal-area R1.30 openings.
"""
from pathlib import Path
import sys,json,ctypes,hashlib,subprocess,os
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from scipy.optimize import brentq
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
ROOT=Path(__file__).resolve().parents[2];RP=ROOT/'reports/l2_revision'
sys.path.insert(0,str(ROOT/'cad/rebuild_r2'))
import build

def contours():
    p=json.loads((ROOT/'cad/rebuild_r2/parameters.json').read_text());p0=[];p1=[]
    for _,xy,_ in build.window_layout(p):
        poly=Polygon(xy);q=poly.buffer(-.85,quad_segs=64).buffer(.85,quad_segs=64)
        def rounded(o):return poly.buffer(o,join_style='mitre').buffer(-1.3,quad_segs=64).buffer(1.3,quad_segs=64)
        o=brentq(lambda o:rounded(o).area-q.area,0,.5)
        p0.append(q);p1.append(rounded(o))
    return {'P0_R085':p0,'P1_R130_EQUAL_AREA':p1}

def conforming_mesh(domain,h):
    key=hashlib.sha1(domain.wkb+str(h).encode()).hexdigest()[:12]
    work=ROOT.parent/f'_support/work/l2/panel_conforming/{key}';work.mkdir(parents=True,exist_ok=True)
    model=domain.simplify(.002,preserve_topology=True);lines=[];point=1;edge=1;loops=[]
    for i,ring in enumerate([model.exterior,*model.interiors],1):
        xy=list(ring.coords)[:-1];start=point;ids=[]
        for x,y in xy:lines.append(f'Point({point})={{{x:.12g},{y:.12g},0,{h}}};');point+=1
        for k in range(len(xy)):
            lines.append(f'Line({edge})={{{start+k},{start+(k+1)%len(xy)}}};');ids.append(edge);edge+=1
        lines.append(f'Curve Loop({i})={{{",".join(map(str,ids))}}};');loops.append(i)
    lines+=['Plane Surface(1)={'+','.join(map(str,loops))+'};','Physical Surface(1)={1};',
            f'Mesh.MeshSizeMin={h*.7};',f'Mesh.MeshSizeMax={h};','Mesh.Algorithm=6;','Mesh.ElementOrder=1;','Mesh.MshFileVersion=2.2;']
    (work/'panel.geo').write_text('\n'.join(lines),encoding='ascii')
    if not (work/'mesh.msh').exists():
        exe=ROOT.parent/'_support/tools/Gmsh/gmsh-4.15.2-Windows64/gmsh.exe'
        with (work/'gmsh.log').open('w') as log:
            subprocess.run([str(exe),'panel.geo','-2','-nt','2','-format','msh2','-o','mesh.msh','-v','3'],cwd=work,stdout=log,stderr=log,check=True,timeout=180,creationflags=0x08000000 if os.name=='nt' else 0)
    data=(work/'mesh.msh').read_text().splitlines();a=data.index('$Nodes');n=int(data[a+1]);nodes={}
    for line in data[a+2:a+2+n]:
        q=line.split();nodes[int(q[0])]=[float(q[1]),float(q[2])]
    a=data.index('$Elements');n=int(data[a+1]);tri=[]
    for line in data[a+2:a+2+n]:
        q=list(map(int,line.split()))
        if q[1]==2:tri.append(q[3+q[2]:])
    keys=sorted(nodes);index={v:i for i,v in enumerate(keys)}
    return np.array([nodes[k] for k in keys]),np.array([[index[v] for v in row] for row in tri])

def mesh_and_k(domain,h,t=1.8):
    if '--conforming' in sys.argv:coords,tri=conforming_mesh(domain,h)
    else:
        xs=np.linspace(-31,31,round(62/h)+1);ys=np.linspace(42,83,round(41/h)+1)
        xx,yy=np.meshgrid(xs,ys);coords=np.c_[xx.ravel(),yy.ravel()];ny,nx=xx.shape
        a=(np.arange(ny-1)[:,None]*nx+np.arange(nx-1)).ravel()
        tri=np.vstack([np.c_[a,a+1,a+nx+1],np.c_[a,a+nx+1,a+nx]])
        poly=shapely.polygons(coords[tri]);tri=tri[shapely.covers(domain,poly)]
        unique,inverse=np.unique(tri,return_inverse=True);tri=inverse.reshape(-1,3);coords=coords[unique]
    d1=coords[tri[:,1]]-coords[tri[:,0]];d2=coords[tri[:,2]]-coords[tri[:,0]];flip=d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0]<0
    tri[flip]=tri[flip][:,[0,2,1]]
    xy=coords[tri];ab=xy[:,1]-xy[:,0];ac=xy[:,2]-xy[:,0];A=(ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0])/2
    b=np.stack([xy[:,1,1]-xy[:,2,1],xy[:,2,1]-xy[:,0,1],xy[:,0,1]-xy[:,1,1]],axis=1)/(2*A[:,None])
    c=np.stack([xy[:,2,0]-xy[:,1,0],xy[:,0,0]-xy[:,2,0],xy[:,1,0]-xy[:,0,0]],axis=1)/(2*A[:,None])
    B=np.zeros((len(tri),3,6));B[:,0,::2]=b;B[:,1,1::2]=c;B[:,2,::2]=c;B[:,2,1::2]=b
    E=1700;nu=.37;D=E/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]])
    ke=np.einsum('eji,jk,ekl,e->eil',B,D,B,A*t)
    dofs=np.stack((tri*2,tri*2+1),axis=2).reshape(-1,6)
    K=coo_matrix((ke.ravel(),(np.repeat(dofs,6,axis=1).ravel(),np.tile(dofs,(1,6)).ravel())),shape=(len(coords)*2,)*2).tocsr()
    return coords,tri,A,B,D,dofs,K

def evaluate(domain,h):
    coords,tri,A,B,D,dofs,K=mesh_and_k(domain,h);results=[]
    for name,axis,lo,hi in [('rear',1,42,83),('side',0,-31,31)]:
        fixed=np.flatnonzero(np.isclose(coords[:,axis],lo));loaded=np.flatnonzero(np.isclose(coords[:,axis],hi))
        along=1-axis;ordered=loaded[np.argsort(coords[loaded,along])];pos=coords[ordered,along]
        weights=np.zeros(len(ordered));weights[:-1]+=np.diff(pos)/2;weights[1:]+=np.diff(pos)/2;weights/=weights.sum()
        rhs=np.zeros(len(coords)*2);rhs[ordered*2+axis]=-weights
        constrained=np.ravel(np.c_[fixed*2,fixed*2+1]);free=np.setdiff1d(np.arange(len(rhs)),constrained)
        u=np.zeros_like(rhs);u[free]=spsolve(K[free][:,free],rhs[free]);residual=K@u-rhs
        stress=np.einsum('ij,ejk,ek->ei',D,B,u[dofs]);sx,sy,txy=stress.T;vm=np.sqrt(sx*sx-sx*sy+sy*sy+3*txy*txy)
        measured=abs(weights@u[ordered*2+axis]);order=np.argsort(vm)
        results.append(dict(case=name,stiffness_N_mm=1/measured,mean_loaded_displacement_mm=measured,
                            max_vm_MPa=float(vm.max()),area_weighted_P99_MPa=float(np.interp(.99*A.sum(),np.cumsum(A[order]),vm[order])),
                            free_residual_norm=float(np.linalg.norm(residual[free])),constrained_nodes=len(fixed),loaded_nodes=len(loaded)))
    return dict(target_h_mm=h,nodes=len(coords),CST_elements=len(tri),meshed_area_mm2=float(A.sum()),
                analytic_area_mm2=domain.area,area_discretisation_error=(A.sum()/domain.area-1),results=results)

def main():
    ctypes.windll.kernel32.SetPriorityClass(ctypes.c_void_p(-1),0x4000)
    out=dict(status='NEW_PROXY_NOT_REPRODUCTION_OF_UNSPECIFIED_HISTORICAL_MODEL',
             coordinates='X[-31,31], Y[42,83], units mm,N,MPa; front=smaller Y',
             method='CST plane stress E1700 nu.37 t1.8. Structured diagonal triangles retained only if their full polygon lies in material. Left/front edge fixed X,Y. Opposite full edge carries uniform line traction total 1N. k=1N/work-conjugate mean displacement.',
             limit='In-plane proxy only; does not test shell bending, whole mouse, contacts, fatigue or actual grips.',candidates={})
    for name,holes in contours().items():
        domain=box(-31,42,31,83).difference(unary_union(holes));levels=[]
        for h in [.75,.5,.35]:
            result=evaluate(domain,h);levels.append(result);print(name,h,[round(q['stiffness_N_mm'],4) for q in result['results']],flush=True)
        out['candidates'][name]=levels
    if '--conforming' in sys.argv:
        out['method']='Same CST formulation/loads; independent conforming Gmsh triangle mesh; contours simplified by at most .002 mm. Mesh and GEO retained. Not a reproduction of historical inputs.'
    name='conforming_2d_proxy.json' if '--conforming' in sys.argv else 'new_2d_proxy.json'
    (RP/name).write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
