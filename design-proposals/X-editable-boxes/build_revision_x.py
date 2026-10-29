from pathlib import Path
code=Path('/workspace/design-studies/w_generated.py').read_text().replace('proposal-W','proposal-X').replace('PROPOSAL_W_','PROPOSAL_X_').replace('W_recessed_terraces_context','X_editable_boxes_context').replace('W_REFERENCE_MASS','X_EDITABLE_BOXES').replace('W_OPPOSITE','X_OPPOSITE')
code=code.replace('POST=(124,153,173,255),LAB=(224,157,119,255)','POST=(224,157,119,255),LAB=(124,153,173,255)')
code=code.replace('01_우체국_BLUE','01_우체국_PEACH').replace('02_창작소_PEACH','02_창작소_BLUE')
code=code.replace('Blue-grey POST and peach LAB, matching the latest reference; neutral public hall','Peach POST and blue-grey LAB per latest colour swap; neutral public hall')
a=code.index('import manifold3d');b=code.index('\n# Left/high end:',a)
helper='''from shapely.geometry import Point, LineString
from shapely.geometry.polygon import orient
original_emit=emit
room_footprints=[]
def rectangles(g):
    # Exact rectilinear partition. Merge occupied grid cells into large boxes.
    polygons=[g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon']
    xs=sorted({round(x,6) for p in polygons for ring in [p.exterior,*p.interiors] for x,y in ring.coords})
    ys=sorted({round(y,6) for p in polygons for ring in [p.exterior,*p.interiors] for x,y in ring.coords})
    cells={(i,j) for i in range(len(xs)-1) for j in range(len(ys)-1) if g.covers(Point((xs[i]+xs[i+1])/2,(ys[j]+ys[j+1])/2))}
    result=[]
    while cells:
        i,j=min(cells,key=lambda q:(q[1],q[0]));right=i+1
        while (right,j) in cells:right+=1
        top=j+1
        while all((k,top) in cells for k in range(i,right)):top+=1
        for k in range(i,right):
            for n in range(j,top):cells.remove((k,n))
        result.append(B(xs[i],ys[j],xs[right],ys[top]))
    assert unary_union(result).symmetric_difference(g).area<.00001
    return result

def emit(name,g,z,h,key,kind):
    g=set_precision(g,.000001)
    if kind!='room':return original_emit(name,g,z,h,key,kind)
    room_footprints.append((name,g,z,h,key))
    for i,rect in enumerate(rectangles(g)):
        original_emit(f'{name} BOX {i+1:02}',rect,z,h,key,kind)
'''
code=code[:a]+helper+code[b:]
# Ground portico piers retained as independent editable boxes; no merged cap/slab.
a=code.index("emit('POST courtyard ground'")
code=code[:a]+'''for yy in (54,62,70,74):
    for xx in (-14,12.8):
        g=B(xx,yy,xx+1.2,yy+1.2).intersection(post_outer)
        if not g.is_empty:emit('POST portico pier',g,35.75,4,'POST','support')
''' +code[a:]
# Add light, separately selectable window panels after all rooms have been built.
a=code.index('\nnames=')
windows='''
# Facade markers stand 20mm proud of the mass, 40mm thick. They are NOT holes.
window_layers={};window_mats={}
for model in [context,proposal]:
    window_layers[id(model)]={}
    mat=r.Material();mat.Name='Window indication';mat.DiffuseColor=(67,91,102,255);mat.Transparency=.1
    window_mats[id(model)]=model.Materials.Add(mat)
    for key,title in [('POST','우체국'),('LAB','창작소')]:
        layer=r.Layer();layer.Name=f'{title}_창표현_별도패널';layer.Color=(67,91,102,255)
        window_layers[id(model)][key]=model.Layers.Add(layer)
for name,g,z,h,key in room_footprints:
    if key not in ('POST','LAB'):continue
    neighbours=unary_union([q for n,q,zz,hh,kk in room_footprints if n!=name and min(z+h,zz+hh)>max(z,zz)+.01])
    polys=[g] if g.geom_type=='Polygon' else list(g.geoms)
    counter=0
    for p in polys:
        p=orient(p,sign=1)
        for ring in [p.exterior,*p.interiors]:
            coords=list(ring.coords)
            for (ax,ay),(bx,by) in zip(coords,coords[1:]):
                length=((bx-ax)**2+(by-ay)**2)**.5
                if length<3:continue
                dx=(bx-ax)/length;dy=(by-ay)/length;nx=dy;ny=-dx
                modules=max(1,int((length-1.2)/(3.5 if key=='POST' else 6)))
                pitch=(length-1.2)/modules
                for k in range(modules):
                    start=.6+k*pitch+.12;end=.6+(k+1)*pitch-.12
                    points=[(ax+dx*t+nx*d,ay+dy*t+ny*d) for t,d in [(start,.02),(end,.02),(end,.06),(start,.06)]]
                    panel=Polygon(points)
                    if not neighbours.is_empty and panel.intersection(neighbours).area>.000001:continue
                    counter+=1;title=f'{key} window Z{z:.2f} panel {counter:03}'
                    original_emit(title,panel,z+.8,2.55,key,'window')
                    for model in [context,proposal]:
                        ob=list(model.Objects)[-1]
                        ob.Attributes.LayerIndex=window_layers[id(model)][key]
                        ob.Attributes.MaterialIndex=window_mats[id(model)]
                        ob.Attributes.ObjectColor=(67,91,102,255)
                        ob.Attributes.SetUserString('Window','Separate symbolic facade panel, not a cut opening')
'''
code=code[:a]+windows+code[a:]
code=code.replace("'W: deep facade recesses within closed storey solids; cascading front workshops; three roof pavilions; recessed postal base and four court/notch openings'", "'X: editable rectangular extrusion boxes; no mesh or window subtraction; separate facade window panels for POST and LAB'")
code=code.replace("'Floor masses with conceptual atrium envelope and entry voids; no detailed structural, facade, egress or accessibility design.'", "'Program masses are rectangular extrusion solids. Window panels are separate symbolic solids, not holes. Site contour unchanged. Cores omitted.'")
code=code.replace("print('W verified'", "print('X verified'")
Path('/workspace/design-studies/x_generated.py').write_text(code)
exec(compile(code,'/workspace/design-studies/x_generated.py','exec'))
original=r.File3dm.Read('/workspace/architecture-6-/contour.3dm')
assert all(a.Geometry.Encode()==b.Geometry.Encode() for a,b in zip(original.Objects,list(check.Objects)[:227]))
new_objects=list(check.Objects)[227:]
assert not any(isinstance(ob.Geometry,r.Mesh) for ob in new_objects)
for ob in new_objects:
    if isinstance(ob.Geometry,r.Extrusion):assert ob.Geometry.IsSolid and ob.Geometry.IsValid
for key in ('POST','LAB'):
    assert any(o['kind']=='window' and o['key']==key for o in records)
print('X verified: original site preserved; all new masses non-mesh; windows on separate layers.')
