from pathlib import Path
code=Path('/workspace/design-studies/t_generated.py').read_text().replace('proposal-T','proposal-U').replace('PROPOSAL_T_','PROPOSAL_U_').replace('T_composed_massing_context','U_enclosed_atrium_context').replace('T_COMPOSED_MASS','U_ARCHITECTURAL_MASS').replace('T_OPPOSITE','U_OPPOSITE')
a=code.index('lab_rects=[');b=code.index('\nlabs=',a)
code=code[:a]+'''lab_rects=[
 [(-14,4,-2,32),(6,4,20,36)],
 [(-14,4,-2,32),(6,4,20,36)],
 [(-14,6,-2,30),(6,6,18,32),(-2,8,6,14)],
 [(-14,8,-2,26),(6,8,18,28),(-2,8,6,14)],
 [(-14,8,18,14)],
]'''+code[b:]
code=code.replace('for k,g in enumerate(posts):',"posts[0]=posts[0].difference(B(8,51,13,56))\nposts[1]=posts[1].difference(B(-2,50,8,56))\nfor k,g in enumerate(posts):")
code=code.replace("court=B(-10,34,20,50).difference(labs[0]).difference(road_stair)","hall_edges=unary_union([B(-10,36,-6,50),B(12,36,16,50)])\ncourt=B(-10,34,20,50).difference(labs[0]).difference(road_stair).difference(hall_edges)")
a=code.index('atrium_cover=');b=code.index('\nnames=',a)
code=code[:a]+'''# Occupied edges define an interior hall; the road stair stays outside.
for k in range(2):
    edge=hall_edges.difference(B(12,36,16,40)) if k==0 else hall_edges
    emit(f'MARKET enclosed hall-edge storey {k+1}',edge,39.75+4*k,4,'MARKET','room')
emit('PUBLIC road stair entrance passage',B(12,36,16,40),39.5,.25,'MARKET','public_slab')
emit('ENCLOSURE road entrance side panel',B(15.82,36,16,37),39.75,4,'ROOF','enclosure')
emit('ENCLOSURE road entrance portal head',B(15.82,37,16,40),42.55,1.2,'ROOF','enclosure')
emit('PUBLIC Exchange lobby inside postal mass',B(-2,50,8,56),39.5,.25,'MARKET','public_slab')
emit('PUBLIC recessed postal street lobby',B(8,51,13,56),35.5,.25,'MARKET','public_slab')
# End glazing is modelled as solid panels with actual doorway voids.
# North stair portal: 4m wide, no panel across the walking route.
for lo,hi in [(-6,2),(6,12)]:
    emit('ENCLOSURE north glazed wall',B(lo,36,hi,36.18),39.75,7.8,'ROOF','enclosure')
emit('ENCLOSURE north stair portal head',B(2,36,6,36.18),46.15,1.4,'ROOF','enclosure')
# Postal entry is 8m wide and 2.8m clear, directly into the carved lobby.
for lo,hi in [(-6,0),(8,12)]:
    emit('ENCLOSURE postal glazed wall',B(lo,49.82,hi,50),39.75,7.8,'ROOF','enclosure')
emit('ENCLOSURE postal portal head',B(0,49.82,8,50),42.55,5,'ROOF','enclosure')
# The exterior road stair meets the lower hall through the south-east porch.
# Cover is continuous weather enclosure, with opaque edges and a glass lantern.
cover=B(-6,36,12,50)
lantern=B(-4,37,10,49)
emit('ATRIUM opaque perimeter roof',cover.difference(lantern),47.55,.2,'MARKET','canopy')
emit('ATRIUM continuous glazed lantern',lantern,47.55,.2,'ROOF','canopy')
# A glazed threshold distinguishes the external upper entry from the internal street.
for lo,hi in [(-2,-1.5),(1.5,6)]:
    emit('ENCLOSURE upper-road vestibule screen',B(lo,4,hi,4.18),43.75,3.8,'ROOF','enclosure')
emit('ENCLOSURE upper entry portal head',B(-1.5,4,1.5,4.18),46.55,1,'ROOF','enclosure')
''' +code[b:]
code=code.replace("'04_아트리움_연결지붕'","'04_아트리움_유리외피'")
code=code.replace("model.Strings['Scope']=", "model.Strings['Enclosure']='Central hall enclosed by occupied side bars, north/south glazing and continuous roof. Deliberate entry portals only. Road stair and upper terraces remain outdoors; no cores.'\n    model.Strings['Scope']=")
code=code.replace("'Editable concept masses interpreted from a single image; no designed walls/doors/windows or structural members.'","'Floor masses with conceptual atrium envelope and entry voids; no detailed structural, facade, egress or accessibility design.'")
code=code.replace("'T: refined S1 / aligned creative volumes, a single crown bar, recessed postal upper storey, paired light courts, slotted atrium roof'","'U: continuous workshop wings, inhabited atrium edges, enclosed public hall, carved Exchange lobby'")
code=code.replace("model.Strings['Refinement']=", "model.Strings['Refinement_previous_T']=")
Path('/workspace/design-studies/u_generated.py').write_text(code)
exec(compile(code,'/workspace/design-studies/u_generated.py','exec'))
# Preserve source context exactly and verify new walls do not obstruct stair headroom.
original=r.File3dm.Read('/workspace/architecture-6-/contour.3dm')
assert all(a.Geometry.Encode()==b.Geometry.Encode() for a,b in zip(original.Objects,list(check.Objects)[:227]))
for s in [o for o in records if o['kind']=='stair']:
    top=s['z']+s['h'];p=Polygon(s['poly'])
    for ob in [o for o in records if o['kind'] in ('enclosure','canopy')]:
        if min(top+2.1,ob['z']+ob['h'])-max(top+.001,ob['z'])<=.001:continue
        assert p.intersection(Polygon(ob['poly'],ob.get('holes',[]))).area<.001,(s['name'],ob['name'])
print('U original contour and stair-envelope clearances verified')
