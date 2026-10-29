import manifold3d as mf
from shapely.geometry.polygon import orient
original_emit=emit
solid_meshes=[]
def mcube(a,b,c,d,z,h):
    return mf.Manifold.cube((c-a,d-b,h)).translate((a,b,z))
def manifold_polygon(p,z,h):
    p=orient(p,sign=1)
    return mf.CrossSection([list(p.exterior.coords)[:-1]]+[list(ring.coords)[:-1] for ring in p.interiors]).extrude(h).translate((0,0,z))
def emit(name,g,z,h,key,kind):
    g=set_precision(g,.000001)
    if kind!='room' or key not in ('LAB','POST','MARKET'):
        return original_emit(name,g,z,h,key,kind)
    polys=[g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon']
    for index,p in enumerate(polys):
        mass=manifold_polygon(p,z,h)
        if key=='LAB':
            # Recess only exterior faces; horizontal caps and end returns remain
            # part of the same storey solid. No duplicate slabs or ceilings.
            co=list(p.exterior.coords)
            for (ax,ay),(bx,by) in zip(co,co[1:]):
                if abs(ax-bx)<1e-5 and abs(by-ay)>5:
                    # Both u-facing facades; clipped cut cannot escape this solid.
                    length=abs(by-ay);y0=min(ay,by)+.85;y1=max(ay,by)-.85
                    depth=2.4 if length>8 else 1.5
                    if p.contains(__import__('shapely').geometry.Point(ax+.1,(ay+by)/2)):
                        cut=mcube(ax-.01,y0,ax+depth,y1,z+.4,h-1.05)
                    else:cut=mcube(ax-depth,y0,ax+.01,y1,z+.4,h-1.05)
                    mass=mass-cut
                elif abs(ay-by)<1e-5 and abs(bx-ax)>7:
                    x0=min(ax,bx)+.85;x1=max(ax,bx)-.85
                    if p.contains(__import__('shapely').geometry.Point((ax+bx)/2,ay+.1)):
                        cut=mcube(x0,ay-.01,x1,ay+1.8,z+.4,h-1.05)
                    else:cut=mcube(x0,ay-1.8,x1,ay+.01,z+.4,h-1.05)
                    mass=mass-cut
        elif key=='MARKET':
            x0,y0,x1,y1=p.bounds
            if y1-y0>6:
                mass=mass-mcube(x0-.01,y0+.6,x0+1.5,y1-.6,z+.3,h-.85)
        elif key=='POST' and z<36:
            # Connect the ground-floor portico piers with a thin integral cap.
            canopy=manifold_polygon(post_outer,z+h-.4,.4)
            mass=mass+canopy
            for yy in (54,62,70,74):
                for xx in (-14,12.8):
                    pier=B(xx,yy,xx+1.2,yy+1.2).intersection(post_outer)
                    if not pier.is_empty:mass=mass+manifold_polygon(pier,z,h)
        meshdata=mass.to_mesh()
        mesh=r.Mesh();mesh.Vertices.UseDoublePrecisionVertices=True;verts=[]
        for a,b,zz in meshdata.vert_properties[:,:3]:
            xx,yy=xy(float(a),float(b));vtx=pt(xx,yy,float(zz));mesh.Vertices.Add(vtx.X,vtx.Y,vtx.Z);verts.append((xx,yy,float(zz)))
        for face in meshdata.tri_verts:mesh.Faces.AddFace(*[int(i) for i in reversed(face)])
        mesh.Normals.ComputeNormals();mesh.Compact()
        assert mesh.IsClosed and mesh.IsValid,name
        solid=mesh
        objname=f'{name} part {index+1}'
        for model in [context,proposal]:model.Objects.AddMesh(solid,attrs(key,objname,model))
        world=orient(Polygon([xy(*q) for q in p.exterior.coords],[[xy(*q) for q in ring.coords] for ring in p.interiors]),sign=1)
        records.append(dict(name=objname,poly=list(world.exterior.coords)[:-1],holes=[list(r.coords)[:-1] for r in world.interiors],uv_poly=list(p.exterior.coords)[:-1],z=z,h=h,key=key,kind=kind,area=p.area))
        solid_meshes.append(dict(name=objname,key=key,vertices=verts,faces=meshdata.tri_verts.tolist()))
