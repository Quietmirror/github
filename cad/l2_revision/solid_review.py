"""Independent C3D10 stress integration: nodal forces and strain energy.

This is separate from CalculiX RF extraction, especially important for
transformed constraints whose MPC reactions are absent from NODE PRINT RF.
Straight midside tetrahedra use four-point exact quadratic integration.
"""
import numpy as np
def review(mesh,arrays,loads,young,poisson,support_nodes):
    sig=arrays['stress_tensor_MPa'];eid=arrays['stress_element_ids'];ip=arrays['stress_integration_points']
    order=np.lexsort((ip,eid));sig=sig[order].reshape(len(mesh.eids),4,6)
    coords=mesh.xyz[mesh.conn];force=np.zeros_like(mesh.xyz);energy=0.
    a,b=.5854101966249685,.1381966011250105
    tensor=np.zeros((len(mesh.eids),4,3,3))
    tensor[:,:,0,0]=sig[:,:,0];tensor[:,:,1,1]=sig[:,:,1];tensor[:,:,2,2]=sig[:,:,2]
    tensor[:,:,0,1]=tensor[:,:,1,0]=sig[:,:,3]
    tensor[:,:,0,2]=tensor[:,:,2,0]=sig[:,:,4]
    tensor[:,:,1,2]=tensor[:,:,2,1]=sig[:,:,5]
    # CalculiX C3D10 integration-point order: dominant barycentric L1,
    # then L2, L3, L4. This is not the mesher's Jacobian-check point order.
    for j,(u,v,w) in enumerate(((b,b,b),(a,b,b),(b,a,b),(b,b,a))):
        l=1-u-v-w
        d=np.array([[1-4*l,4*u-1,0,0,4*(l-u),4*v,-4*v,-4*w,4*w,0],
            [1-4*l,0,4*v-1,0,-4*u,4*u,4*(l-v),-4*w,0,4*w],
            [1-4*l,0,0,4*w-1,-4*u,0,-4*v,4*(l-w),4*u,4*v]]).T
        jac=coords.transpose(0,2,1)@d;dv=np.linalg.det(jac)/24
        grad=d[None,:,:]@np.linalg.inv(jac)
        nodal=(grad@tensor[:,j,:,:])*dv[:,None,None]
        np.add.at(force,mesh.conn.reshape(-1),nodal.reshape(-1,3))
        t=tensor[:,j,:,:];tr=np.trace(t,axis1=1,axis2=2)
        eps=(1+poisson)/young*t-poisson/young*tr[:,None,None]*np.eye(3)
        energy+=float((.5*np.sum(t*eps,axis=(1,2))*dv).sum())
    residual=force-loads;support=np.array(sorted(set(support_nodes)),int)
    free=np.ones(len(force),bool);free[support]=False
    reactions=residual[support];applied=loads.sum(axis=0);rforce=reactions.sum(axis=0)
    moment=np.cross(mesh.xyz[support],reactions).sum(axis=0)+np.cross(mesh.xyz,loads).sum(axis=0)
    work=float(np.sum(loads*arrays['displacement_mm']))
    scale=max(1.,float(np.linalg.norm(applied)))
    force_error=float(np.linalg.norm(applied+rforce)/scale)
    moment_error=float(np.linalg.norm(moment)/(scale*np.ptp(mesh.xyz,axis=0).max()))
    energy_error=abs(2*energy/work-1)
    return dict(method='Independent NumPy integration of B^T sigma over all C3D10 elements, and stress compliance strain energy',
        reaction_sum_N=rforce.tolist(),applied_force_N=applied.tolist(),force_balance_relative_error=force_error,
        moment_balance_relative_error=moment_error,free_nodal_residual_max_N=float(np.linalg.norm(residual[free],axis=1).max()),
        strain_energy_Nmm=energy,external_work_Nmm=work,energy_relative_error=energy_error,
        pass_check=bool(force_error<.002 and moment_error<.002 and energy_error<.002))
