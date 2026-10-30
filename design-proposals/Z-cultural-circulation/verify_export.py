import ezdxf,json
from collections import Counter
from pathlib import Path
out=Path('/workspace/design-studies/Z-floorplans');a=ezdxf.readfile(out/'Z_cultural_circulation_plans.dxf');b=ezdxf.readfile(out/'Z_roundtrip.dxf')
assert a.units==b.units==4
assert not list(b.modelspace().query('HATCH'))
def signature(e):
 t=e.dxftype();base=(t,e.dxf.layer)
 if t=='LWPOLYLINE':return base+(e.closed,tuple(tuple(round(float(q),4) for q in p) for p in e.get_points('xyseb')))
 if t=='MTEXT':return base+(e.text,tuple(round(float(q),4) for q in e.dxf.insert),round(e.dxf.char_height,4),e.dxf.style)
 raise AssertionError(t)
assert Counter(map(signature,a.modelspace()))==Counter(map(signature,b.modelspace()))
assert len(list(a.layouts))==len(list(b.layouts))
assert not b.audit().has_errors
assert open(out/'Z_cultural_circulation_plans.dwg','rb').read(6).startswith(b'AC10')
# Vertical core consistency, and no overlaps within the scheduled core blocks.
audit=json.load(open(out/'plan_audit.json'));same={}
from shapely.geometry import box
for floor in audit['floors']:
 for core in floor['cores']:
  name=core['code'];bounds=core['bounds']
  if name in same:assert bounds==same[name]
  same[name]=bounds
 for i,x in enumerate(floor['cores']):
  for y in floor['cores'][i+1:]:assert box(*x['bounds']).intersection(box(*y['bounds'])).area<.00001,(floor['level'],x['code'],y['code'])
result=dict(modelspace_entities=len(b.modelspace()),types=dict(Counter(e.dxftype() for e in b.modelspace())),units='mm',layouts=list(b.layout_names()),hatches=0,roundtrip_geometry_and_korean_text='exact at 0.0001 mm numeric tolerance',core_alignment='passed',audit_errors=0,native_AutoCAD_test=False)
(out/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
