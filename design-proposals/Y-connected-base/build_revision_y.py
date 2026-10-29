from pathlib import Path
code=Path('/workspace/design-studies/x_generated.py').read_text().replace('proposal-X','proposal-Y').replace('PROPOSAL_X_','PROPOSAL_Y_').replace('X_editable_boxes_context','Y_connected_lower_storeys_context').replace('X_EDITABLE_BOXES','Y_CONNECTED_BASE').replace('X_OPPOSITE','Y_OPPOSITE')
needle='labs=[unary_union([B(*b) for b in row]) for row in lab_rects]'
code=code.replace(needle,needle+'''
# Join the two workshop wings below the retained upper-road datum.
# Stop at V34 so the main stair descending into the atrium remains open.
labs[0]=labs[0].union(B(-14,4,20,34))
assert labs[0].geom_type=='Polygon' and len(labs[0].interiors)==0
emit('LAB added bottom storey',labs[0],35.75,4,'LAB','room')
''')
code=code.replace("emit('PUBLIC street lower level',entry.difference(labs[0]),39.5,.25,'MARKET','public_slab')",'')
# The retained upper approach stands on the connected lower storey roof;
# do not overlay a second coincident floor plate on that roof.
code=code.replace("emit('PUBLIC upper-road street Z43.75',entry,", "emit('PUBLIC upper-road street Z43.75',entry.difference(labs[0]),")
code=code.replace("emit('PUBLIC stair upper landing',B(2,32,6,34),", "emit('PUBLIC stair upper landing',B(2,32,6,34).difference(labs[0]),")
code=code.replace("'X: editable rectangular extrusion boxes; no mesh or window subtraction; separate facade window panels for POST and LAB'", "'Y: added 4m workshop bottom storey at Z35.75; connected workshop wings below Z43.75; removed lower duplicate road approach; retained upper road approach'")
code=code.replace("'Storeys 4m. Postal base Z35.75; upper road Z43.75; creative highest roof Z59.75. Cores omitted.'", "'Storeys 4m. Postal and added workshop base Z35.75. Upper road Z43.75 and workshop roof Z59.75 unchanged. No cores.'")
code=code.replace("print('X verified'", "print('Y verified'")
Path('/workspace/design-studies/y_generated.py').write_text(code)
exec(compile(code,'/workspace/design-studies/y_generated.py','exec'))
original=r.File3dm.Read('/workspace/architecture-6-/contour.3dm')
assert all(a.Geometry.Encode()==b.Geometry.Encode() for a,b in zip(original.Objects,list(check.Objects)[:227]))
assert not any(isinstance(ob.Geometry,r.Mesh) for ob in list(check.Objects)[227:])
assert not any('PUBLIC street lower level' in o['name'] for o in records)
assert labs[0].difference(unary_union([B(*b) for b in lab_rects[0]])).area>0
print('Y original contour, upper-road datum and connected lower footprint verified.')
# Model-based area audit. Rooms and roofed public floors, plan unions per level.
# Outdoor stairs/terraces, window markers and voids are excluded. Interior stair
# projections already lie within the counted public hall floor and are not added twice.
from collections import defaultdict
areas_by_z=defaultdict(list)
room_records=[o for o in records if o['kind']=='room']
roof_records=[o for o in records if o['kind']=='canopy']
def poly(o):return Polygon(o['poly'],o.get('holes',[]))
for o in room_records:areas_by_z[round(o['z'],3)].append(poly(o))
for o in records:
    if o['kind']!='public_slab':continue
    top=round(o['z']+o['h'],3)
    covers=unary_union([poly(q) for q in room_records+roof_records if q['z']>=top+2.1-.001])
    enclosed=poly(o).intersection(covers)
    if not enclosed.is_empty:areas_by_z[top].append(enclosed)
floors={z:unary_union(gs) for z,gs in areas_by_z.items()}
site_area=Polygon(boundary).area
footprint=unary_union([poly(o) for o in room_records+roof_records])
gross=sum(g.area for g in floors.values())
new_base=unary_union([poly(o) for o in room_records if o['key']=='LAB' and abs(o['z']-35.75)<.001])
audit=dict(site_area_m2=site_area,building_projection_m2=footprint.area,coverage_percent=100*footprint.area/site_area,
           modeled_floor_area_m2=gross,far_all_included_percent=100*gross/site_area,
           new_lab_bottom_m2=new_base.area,far_if_new_bottom_excluded_percent=100*(gross-new_base.area)/site_area,
           floor_area_by_z={str(z):g.area for z,g in sorted(floors.items())},
           basis='Model estimate: projected rooms+roofs; rooms+roofed public floor unions; outdoor floors/voids excluded. Interior stair plan counted within public hall floor. Not a legal ground-level/basement or FAR ruling.')
(OUT/'area_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
for key,value in audit.items():
    if not isinstance(value,dict):context.Strings['Area_'+key]=str(value)
assert context.Write(str(path),8)
print(json.dumps(audit,ensure_ascii=False,indent=2))
