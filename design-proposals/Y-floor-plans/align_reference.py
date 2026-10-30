import ezdxf,numpy as np,json,math,rhino3dm as r
from pathlib import Path
out=Path('/workspace/design-studies/Y-floorplans')
d=ezdxf.readfile(str(out/'Drawing1_reference.dxf'));e=next(e for e in d.modelspace() if e.dxf.layer=='SITE');src=np.array(list(e.get_points('xy')))
m=r.File3dm.Read('/workspace/architecture-6-/contour.3dm');segs=[]
for e in m.Objects[226].Geometry.Edges:
 if abs(e.PointAtStart.Z-34500)<.01 and abs(e.PointAtEnd.Z-34500)<.01:segs.append([(p.X,p.Y) for p in e.TryGetPolyline()])
b=segs.pop(0)
while segs:
 for i,s in enumerate(segs):
  if math.dist(b[-1],s[0])<.01:b+=s[1:];segs.pop(i);break
  if math.dist(b[-1],s[-1])<.01:b+=s[::-1][1:];segs.pop(i);break
 else:raise ValueError()
tgt=np.array(b);a=src[list(range(26,9,-1))];c=tgt[1:18]
U,S,Vt=np.linalg.svd((a-a.mean(0)).T@(c-c.mean(0)));rot=U@Vt;trans=c.mean(0)-a.mean(0)@rot
err=np.linalg.norm(a@rot+trans-c,axis=1)
print('det',np.linalg.det(rot),'rigid errors mm',err)
assert max(err)<.01
(out/'registration.json').write_text(json.dumps(dict(rotation_row=rot.tolist(),translation=trans.tolist(),max_matched_error_mm=float(max(err)),matched_vertices=17,rhino_boundary=tgt.tolist(),drawing_site=(src@rot+trans).tolist()),indent=2))
