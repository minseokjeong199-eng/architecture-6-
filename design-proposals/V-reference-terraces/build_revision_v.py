from pathlib import Path
code=Path('/workspace/design-studies/u_generated.py').read_text().replace('proposal-U','proposal-V').replace('PROPOSAL_U_','PROPOSAL_V_').replace('U_enclosed_atrium_context','V_reference_terraces_context').replace('U_ARCHITECTURAL_MASS','V_REFERENCE_TERRACES').replace('U_OPPOSITE','V_OPPOSITE')
a=code.index('lab_rects=[');b=code.index('\nlabs=',a)
code=code[:a]+'''# Offset four-storey workshop clusters and TWO small roof pavilions.
lab_rects=[
 [(-14,4,-2,20),(6,4,20,24),(-14,20,2,32),(6,24,20,36)],
 [(-14,4,-2,18),(6,4,20,22),(-12,20,0,30),(8,24,20,34)],
 [(-12,6,-2,20),(6,6,18,24),(-10,22,0,28),(8,24,16,30),(-2,10,6,14)],
 [(-12,6,-2,18),(6,8,18,22)],
 [(-10,8,-2,16),(8,10,16,18)],
]''' +code[b:]
a=code.index('post_outer=');b=code.index('\nfor k,g in enumerate(posts)',a)
code=code[:a]+'''post_outer=B(-14,50,14,76)
# One unbroken upper postal bar, with three square roof courts.
post_courts=unary_union([B(-9,55,-3,61),B(-9,66,-3,72),B(3,59,10,67)])
posts=[B(-12,52,12,74).difference(post_courts),post_outer.difference(post_courts),post_outer.difference(post_courts)]
posts[0]=posts[0].difference(B(8,52,12,57))
posts[1]=posts[1].difference(B(-2,50,8,56))
''' +code[b:]
# replace hall construction completely: glazed stepped enclosure over lower occupied edges.
a=code.index('# Occupied edges define');b=code.index('\nnames=',a)
code=code[:a]+'''edge=hall_edges.difference(B(12,36,16,40))
emit('MARKET lower hall-edge storey',edge,39.75,4,'MARKET','room')
emit('PUBLIC road entrance passage',B(12,36,16,40),39.5,.25,'MARKET','public_slab')
emit('PUBLIC Exchange lobby',B(-2,50,8,56),39.5,.25,'MARKET','public_slab')
emit('PUBLIC postal entry recess',B(8,52,12,57),35.5,.25,'MARKET','public_slab')
# North enclosure: portal follows the upper stair, all remaining faces closed.
for lo,hi in [(-6,2),(6,12)]:
    emit('GLASS north wall',B(lo,36,hi,36.16),39.75,7.8,'ROOF','enclosure')
emit('GLASS north portal head',B(2,36,6,36.16),46.15,1.4,'ROOF','enclosure')
for lo,hi in [(-10,-6),(12,16)]:
    emit('GLASS north clerestory',B(lo,36,hi,36.16),43.75,3.8,'ROOF','enclosure')
# Lower east road entry has a deliberate 3m-wide opening.
emit('GLASS east entry side',B(15.84,36,16,37),39.75,4,'ROOF','enclosure')
emit('GLASS east entry head',B(15.84,37,16,40),42.55,1.2,'ROOF','enclosure')
# Roof step makes the public centre lower and lighter than either main building.
for y0,y1,roofz in [(36,42,47.75),(42,50,45.75)]:
    for x0,x1 in [(-10,-9.84),(15.84,16)]:
        emit('GLASS atrium side clerestory',B(x0,y0,x1,y1),43.75,roofz-43.95,'ROOF','enclosure')
    emit('GLASS atrium roof',B(-10,y0,16,y1),roofz-.2,.2,'ROOF','canopy')
emit('GLASS roof step clerestory',B(-10,41.84,16,42),45.75,1.8,'ROOF','enclosure')
for lo,hi in [(-6,0),(8,12)]:
    emit('GLASS south wall',B(lo,49.84,hi,50),39.75,5.8,'ROOF','enclosure')
emit('GLASS postal doorway head',B(0,49.84,8,50),42.55,3,'ROOF','enclosure')
# Side bars below the roof leave a full-width glazed upper frontage.
for lo,hi in [(-10,-6),(12,16)]:
    emit('GLASS south clerestory',B(lo,49.84,hi,50),43.75,1.8,'ROOF','enclosure')
# Exposed workshop roof terraces have low edge returns, not duplicate floor slabs.
for k in range(1,5):
    terrace=labs[k-1].difference(labs[k])
    # only the outside edges, preserving the inner public route and terraces.
    outside=terrace.intersection(unary_union([B(-14,4,-13.8,32),B(19.8,4,20,36)]))
    emit(f'LAB terrace edge return {k}',outside,39.75+4*k,.8,'LAB','parapet')
# Two roof pavilion terrace stairs, embedded in existing setbacks.
steps('workshop terrace stair west',(-14,10,-12,18),47.75,51.75,28)
steps('workshop terrace stair east',(18,14,20,22),47.75,51.75,28)
emit('PUBLIC west workshop stair landing',B(-14,18,-12,20),51.5,.25,'MARKET','public_slab')
emit('PUBLIC east workshop stair landing',B(18,22,20,24),51.5,.25,'MARKET','public_slab')
''' +code[b:]
code=code.replace("model.Strings['Revision']=", "model.Strings['Previous_revision']=")
code=code.replace("model.Strings['Scope']=", "model.Strings['Revision']='V: close reference silhouette: staggered workshop terraces, twin roof pavilions, stepped glass atrium, continuous postal upper bar with three courts'\n    model.Strings['Scope']=")
code='\n'.join(line for line in code.split('\n') if not any(q in line for q in ["model.Strings['Previous_revision']","model.Strings['Refinement_previous_T']"]))
Path('/workspace/design-studies/v_generated.py').write_text(code)
exec(compile(code,'/workspace/design-studies/v_generated.py','exec'))
original=r.File3dm.Read('/workspace/architecture-6-/contour.3dm')
assert all(a.Geometry.Encode()==b.Geometry.Encode() for a,b in zip(original.Objects,list(check.Objects)[:227]))
for s in [o for o in records if o['kind']=='stair']:
 top=s['z']+s['h'];p=Polygon(s['poly'])
 for ob in [o for o in records if o['kind'] in ('enclosure','canopy')]:
  if min(top+2.1,ob['z']+ob['h'])-max(top+.001,ob['z'])<=.001:continue
  assert p.intersection(Polygon(ob['poly'],ob.get('holes',[]))).area<.001,(s['name'],ob['name'])
print('V original contour / solid / boundary / stair headroom checks passed')
