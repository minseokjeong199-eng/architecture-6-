from pathlib import Path
code=Path('/workspace/design-studies/v_generated.py').read_text().replace('proposal-V','proposal-W').replace('PROPOSAL_V_','PROPOSAL_W_').replace('V_reference_terraces_context','W_recessed_terraces_context').replace('V_REFERENCE_TERRACES','W_REFERENCE_MASS').replace('V_OPPOSITE','W_OPPOSITE')
code=code.replace('POST=(177,90,57,255),LAB=(59,110,154,255),MARKET=(223,175,68,255)', 'POST=(124,153,173,255),LAB=(224,157,119,255),MARKET=(208,201,186,255)')
code=code.replace('ROOF=(172,203,210,255)','ROOF=(209,212,210,255)')
code=code.replace('01_우체국_RED','01_우체국_BLUE').replace('02_창작소_BLUE','02_창작소_PEACH')
a=code.index('lab_rects=[');b=code.index('\nlabs=',a)
code=code[:a]+'''lab_rects=[
 [(-14,4,-2,20),(6,4,20,24),(-16,20,2,32),(6,24,20,36),(-16,32,-6,42),(-16,42,-8,48)],
 [(-14,4,-2,18),(6,4,20,22),(-14,20,0,30),(8,24,20,34),(-14,32,-6,40)],
 [(-12,6,-2,20),(6,6,20,24),(-12,22,0,30),(8,24,18,30),(-2,10,6,14)],
 [(-12,6,-2,18),(4,8,20,24),(-2,10,4,14)],
 [(-10,6,2,12),(-12,14,-4,22),(8,12,18,20)],
]''' +code[b:]
# A fourth court is an open notch on the atrium side, as in the new reference.
code=code.replace('post_outer=B(-14,50,14,76)', 'post_outer=B(-14,50,14,76).difference(B(-10,50,-5,54))')
# Lower entrance remains at the original site datum.
code=code.replace('hall_edges=unary_union([B(-10,36,-6,50),B(12,36,16,50)])','hall_edges=unary_union([B(-6,36,-2,50),B(12,36,16,50)])')
# Atrium west line is adjusted to avoid the new cascading workshop edge.
code=code.replace('B(-10,34,20,50)', 'B(-6,34,20,50)')
code=code.replace('gallery=B(-10,32,16,36)', 'gallery=B(-6,32,16,36)')
code=code.replace('B(-6,40,12,42)','B(-2,40,12,42)')
code=code.replace('[(-6,2),(6,12)]','[(-2,2),(6,12)]')
code=code.replace('[(-10,-6),(12,16)]','[(-6,-2),(12,16)]')
code=code.replace('[(-10,-9.84),(15.84,16)]','[(-6,-5.84),(15.84,16)]')
code=code.replace('B(-10,y0,16,y1)','B(-6,y0,16,y1)').replace('B(-10,41.84,16,42)','B(-6,41.84,16,42)')
code=code.replace('[(-6,0),(8,12)]','[(-2,0),(8,12)]')
# The upper terraces no longer share the V geometry: discard those stairs/rails.
a=code.index('# Exposed workshop roof terraces');b=code.index('\nnames=',a)
code=code[:a]+'''# The descending front workshop sequence is expressed by occupied masses,
# not an expansive landscaped plaza. No invented cores or furniture.
''' +code[b:]
# Construct a SINGLE closed solid for each storey with real recessed openings.
a=code.index('original_emit=emit');b=code.index('\n# Left/high end:',a)
code=code[:a]+Path('/workspace/design-studies/w_solid_helper.py').read_text()+code[b:]
code=code.replace("'Red POST, blue CREATIVE LAB; shared street and terrace plates; single translucent atrium cover'", "'Blue-grey POST and peach LAB, matching the latest reference; neutral public hall'")
code=code.replace("'Reference-form study, not an 8200 sqm programme reconciliation. No certified BCR, FAR, legal height or basement classification.'", "'Form prioritised per user instruction; FAR is not a shaping target. No certified BCR, FAR or legal height assessment.'")
code=code.replace("'V: close reference silhouette: staggered workshop terraces, twin roof pavilions, stepped glass atrium, continuous postal upper bar with three courts'", "'W: deep facade recesses within closed storey solids; cascading front workshops; three roof pavilions; recessed postal base and four court/notch openings'")
# Additional records for mesh validation remain on floor layers.
code=code.replace("if isinstance(ob.Geometry,r.Extrusion):assert ob.Geometry.IsSolid", "if isinstance(ob.Geometry,(r.Extrusion,r.Brep)):assert ob.Geometry.IsSolid")
code=code.replace("print('S verified'", "print('W verified'")
Path('/workspace/design-studies/w_generated.py').write_text(code)
exec(compile(code,'/workspace/design-studies/w_generated.py','exec'))
original=r.File3dm.Read('/workspace/architecture-6-/contour.3dm')
assert all(a.Geometry.Encode()==b.Geometry.Encode() for a,b in zip(original.Objects,list(check.Objects)[:227]))
for ob in list(check.Objects)[227:]:
    if isinstance(ob.Geometry,r.Mesh):assert ob.Geometry.IsClosed and ob.Geometry.IsValid
for stair in [o for o in records if o['kind']=='stair']:
    top=stair['z']+stair['h'];p=Polygon(stair['poly'])
    for ob in [o for o in records if o['kind'] in ('enclosure','canopy')]:
        if min(top+2.1,ob['z']+ob['h'])-max(top+.001,ob['z'])<=.001:continue
        assert p.intersection(Polygon(ob['poly'],ob.get('holes',[]))).area<.001,(stair['name'],ob['name'])
(OUT/'solid_mesh.json').write_text(json.dumps(solid_meshes))
print('Original contour retained. Recessed floor masses are valid closed meshes.')
