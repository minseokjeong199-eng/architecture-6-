from pathlib import Path
code=Path('/workspace/design-studies/y_generated.py').read_text().replace('proposal-Y','proposal-Z').replace('PROPOSAL_Y_','PROPOSAL_Z_').replace('Y_connected_lower_storeys_context','Z_circulation_platform_context').replace('Y_CONNECTED_BASE','Z_CIRCULATION_PLATFORM').replace('Y_OPPOSITE','Z_OPPOSITE')
code=code.replace('post_outer=B(-14,50,14,76).difference(B(-10,50,-5,54))','post_outer=B(-14,50,14,76)')
code=code.replace('post_courts=unary_union([B(-9,55,-3,61),B(-9,66,-3,72),B(3,59,10,67)])','post_courts=Polygon()')
a=code.index('posts=[');b=code.index('\nfor k,g in enumerate(posts)',a)
code=code[:a]+'''posts=[post_outer,post_outer.difference(B(-2,50,8,56)),post_outer]
# B1 becomes a continuous internal service / material-transfer base.
connector=B(-6,34,16,52).difference(labs[0]).difference(posts[0])
emit('MARKET B1 shared service connector',connector,35.75,4,'MARKET','room')
''' +code[b:]
# Piers are now inside the B1 volume, so no duplicate solids.
a=code.index('for yy in (54,62,70,74):');b=code.index("emit('POST courtyard ground'",a)
code=code[:a]+code[b:]
# No duplicate base floor at newly enclosed B1 public thresholds.
code=code.replace("emit('PUBLIC postal ground threshold',B(10,50,12,54)","emit('PUBLIC postal ground threshold',B(10,50,12,54).difference(posts[0])")
code=code.replace("emit('PUBLIC postal entry recess',B(8,52,12,57)","emit('PUBLIC postal entry recess',B(8,52,12,57).difference(posts[0])")
# 2F gallery within the high portion of the enclosed atrium; keep central stair void.
a=code.index('# Facade markers stand')
code=code[:a]+'''upper_gallery=unary_union([B(-6,34,2,36),B(6,34,16,36),B(-6,36,-2,42),B(12,36,16,42)]).difference(labs[1])
# Existing lower program roofs already form parts of the gallery floor.
lower_edge=hall_edges.difference(B(12,36,16,40))
emit('PUBLIC 2F atrium learning gallery',upper_gallery.difference(lower_edge),43.5,.25,'MARKET','public_slab')
''' +code[a:]
code=code.replace("'Y: added 4m workshop bottom storey at Z35.75; connected workshop wings below Z43.75; removed lower duplicate road approach; retained upper road approach'","'Z: connected B1 service floor; removed postal courts; central public atrium and learning gallery. 2D planning adds aligned cores and service rooms.'")
Path('/workspace/design-studies/z_generated.py').write_text(code)
exec(compile(code,'/workspace/design-studies/z_generated.py','exec'))
from collections import defaultdict
areas=defaultdict(list)
rooms=[o for o in records if o['kind']=='room'];roofs=[o for o in records if o['kind']=='canopy']
def pp(o):return Polygon(o['poly'],o.get('holes',[]))
for o in rooms:areas[o['z']].append(pp(o))
for o in records:
 if o['kind']=='public_slab':
  z=round(o['z']+o['h'],3);cover=unary_union([pp(q) for q in rooms+roofs if q['z']>=z+2.1-.001]);areas[z].append(pp(o).intersection(cover))
floors={z:unary_union(gs).area for z,gs in areas.items()}
sitearea=Polygon(boundary).area;coverage=unary_union([pp(q) for q in rooms+roofs if q['z']>=39.75]).area
summary=dict(site_area_m2=sitearea,above_B1_footprint_m2=coverage,BCR_model_percent=coverage/sitearea*100,
 model_floor_area_total_m2=sum(floors.values()),B1_floor_area_m2=floors.get(35.75,0),
 FAR_excluding_entire_B1_percent=sum(a for z,a in floors.items() if z>35.75)/sitearea*100,
 FAR_including_B1_percent=sum(floors.values())/sitearea*100,floor_areas=floors)
(OUT/'area_audit.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
