"""L2 alternate BRep construction, derived from retained R3.2 builder.
Preserve Boolean face partitions; do not globally unify trimmed NURBS faces.
"""
import cadquery as cq

def rebuild_body(r,p,design,apertures):
    """Apply changed apertures before the original surface is heavily trimmed.

    OCC fails Boolean classification on the already trimmed exported BSpline
    BODY. Regenerate its documented source operations instead of accepting an
    empty or partial Boolean. The unchanged R3/R3.1 corrections are reapplied.
    """
    outer,inner,_=r.make_surfaces(p);mech=r.build_mechanics(p,outer,inner)
    interface=r.build_interfaces(p,outer,mech['parts'])
    mech['body_cuts'].extend(interface['body_cuts']);mech['body_additions'].extend(interface['body_additions'])
    body=outer.cut(inner)
    for sign in (-1,1):body=body.cut(r.box(25,25,50,(sign*40.8,12.5,32.5)))
    for i,c in enumerate(mech['body_cuts']):
        bb=c.BoundingBox()
        if abs(bb.xlen-22)<1e-5 and abs(bb.ylen-10.7)<1e-5 and abs(bb.zlen-5.7)<1e-5:
            cy=round(c.Center().y)
            for tool in apertures[cy]['skin']:body=body.cut(tool.mirror('YZ'))
        else:body=body.cut(c)
        assert body.isValid(),('source cut',i)
    for name,points,tool in r.exporter.window_layout(p):body=body.cut(tool)
    relief=[]
    for m in mech['metadata']['side_motions']:
        cx=m['actuation_point'][0]-7.1;cy=m['actuation_point'][1];cz=m['actuation_point'][2]
        relief.append(r.box(3.3,10.7,5.7,(cx+.5,cy,cz)))
    for i,support in enumerate(mech['body_additions']):
        for tool in relief:
            if r.possible(support,tool):support=support.cut(tool,tol=1e-5)
        for ap in apertures.values():
            for tool in ap['supports']:
                tool=tool.mirror('YZ')
                if r.possible(support,tool):support=support.cut(tool,tol=1e-5)
        body=body.fuse(support,tol=1e-5)
        assert body.isValid(),('source support',i)
    for tool in interface['final_cuts']+mech['terminal_cuts']:body=body.cut(tool,tol=1e-5)
    body=body.mirror('YZ');print('Regenerated source BODY',len(body.Solids()),body.Volume(),flush=True)
    for m in design['mechanisms']['motions']:
        if m['part'] in ('LEFT_KEY','RIGHT_KEY','WHEEL_CARRIER'):
            actor=cq.importers.importStep(str(r.BASE/f"assembly/{m['part']}.step")).val()
            ori=m['origin'];axis=[ori[0]+1,*ori[1:]]
            if m['part']=='WHEEL_CARRIER':
                cut=actor.rotate(ori,axis,m['end_deg']).translate((0,0,-.03)).intersect(r.box(2,5,8,(-4.35,41.5,14)))
            else:
                stop=r.box(7,11,7,(m['actuation_point'][0]/18.3*23,11.5,10.5))
                cut=actor.rotate(ori,axis,m['end_deg']).translate((0,0,-.04)).intersect(stop)
            body=body.cut(cut)
    for x in (7.8,-7.8):
        post=r.cylinder(2.8,2.4,(x,13.,5.6));bridge=r.beam((x,13.,6.8),(x,17.5,6.8),1.35)
        body=r.join(body,post,bridge).cut(r.cylinder(.85,3.2,(x,13.,5.4)))
    body=body.cut(r.box(20.4,10.4,20,(0,15,18)))
    feet=design['mechanisms']['feet'];z=5.2
    local=r.join(*[r.cylinder(4.01,z+6,(*f['center'],-5)) for f in feet])
    body=body.cut(r.box(150,150,z+5,(0,44,(z-5)/2)).intersect(local))
    for f in feet:body=body.fuse(r.cylinder(4,1.6,(*f['center'],z)))
    return body
