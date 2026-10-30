from pathlib import Path
import json,math,hashlib
import numpy as np
import ezdxf,rhino3dm as r
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely import set_precision
from ezdxf import bbox
OUT=Path('/workspace/design-studies/Y-floorplans');D=json.load(open('/workspace/design-studies/proposal-Y/internal_geometry.json'));REG=json.load(open(OUT/'registration.json'))
origin=D['origin'];u=D['u'];v=D['v']
def local(x,y):
 x=x/1000-origin[0];y=(y-1500000)/1000-origin[1]
 return (x*u[0]+y*u[1],x*v[0]+y*v[1])
def world(x,y):return ((origin[0]+x*u[0]+y*v[0])*1000,(origin[1]+x*u[1]+y*v[1])*1000+1500000)
def parts(g,kind):
 if g is None or g.is_empty:return []
 if g.geom_type==kind:return [g]
 return [a for q in getattr(g,'geoms',[]) for a in parts(q,kind)]
# Extract actual closed extrusion profiles from the delivered Y 3DM.
model=r.File3dm.Read('/workspace/design-studies/proposal-Y/Y_connected_lower_storeys_context.3dm');records=iter(D['records']);rs=[]
for ob in list(model.Objects)[227:]:
 if not isinstance(ob.Geometry,r.Extrusion):continue
 meta=next(records);assert meta['name']==ob.Attributes.Name
 g=ob.Geometry
 rings=[[(p.X,p.Y) for p in g.Profile3d(i,0).TryGetPolyline()] for i in range(g.ProfileCount)]
 p=Polygon([local(*q) for q in rings[0]],[[local(*q) for q in a] for a in rings[1:]])
 p=set_precision(p,1e-6);assert p.is_valid
 assert abs(p.area-meta['area'])<.001,(ob.Attributes.Name,p.area,meta['area'])
 rs.append(dict(meta,p=p))
site=Polygon([local(*q) for q in REG['rhino_boundary']]);refsite=Polygon([local(*q) for q in REG['drawing_site']])
rooms=[o for o in rs if o['kind']=='room'];levelz=[35.75,39.75,43.75,47.75,51.75,55.75]
# Same shaft/stair location vertically wherever program is present.
lab_cores=[('L-S1','계단실',(-9.5,6.4,-2.5,10.6),'STAIR_H'),('L-S2','계단실',(8.5,12.4,12.5,18.4),'STAIR_V'),('L-EV','승강기',(13,12.4,15.4,14.8),'LIFT'),('L-WU','공용/장애인 WC',(15.4,16,17.9,19),'WC'),('L-EPS','EPS',(16,14,16.9,15.6),'SHAFT'),('L-PS','PS',(16.9,14,17.8,15.6),'SHAFT')]
post_cores=[('P-S1','계단실',(-11,61.5,-4,65.7),'STAIR_H'),('P-S2','계단실',(4,67.5,11,71.7),'STAIR_H'),('P-EV','승강기',(-2.6,61.8,-.2,64.2),'LIFT'),('P-WM','남 WC',(-2.5,68,0,72),'WC'),('P-WF','여 WC',(0,68,2.5,72),'WC'),('P-WU','장애인 WC',(-2.5,65,0,67.5),'WC'),('P-EPS','EPS',(0,65,1.2,66.4),'SHAFT'),('P-PS','PS',(0,66.4,1.2,67.5),'SHAFT'),('P-TPS','TPS',(1.2,65,2.4,66.4),'SHAFT'),('P-JAN','청소',(1.2,66.4,2.4,67.5),'SERVICE')]
lab_wc=[('L-WM','남 WC',(-11.5,23,-8.5,28),'WC'),('L-WF','여 WC',(-8.5,23,-5.5,28),'WC'),('L-TPS','TPS',(-5.5,26,-4.3,27.2),'SHAFT'),('L-PS2','PS',(-5.5,27.2,-4.3,28.4),'SHAFT')]
doc=ezdxf.new('R2000');doc.units=4;doc.header['$MEASUREMENT']=1;doc.styles.new('KOREAN',dxfattribs={'font':'malgun.ttf'})
doc.linetypes.new('PLAN_DASH',dxfattribs={'pattern':[800,500,-300]});doc.linetypes.new('PLAN_DOT',dxfattribs={'pattern':[300,70,-230]})
ms=doc.modelspace();layercache=set();audit=[];preview=[]
def layer(name,color=7,width=18,dash=False):
 if name not in layercache:
  doc.layers.new(name,dxfattribs={'color':color,'lineweight':width,'linetype':'PLAN_DASH' if dash else 'Continuous'});layercache.add(name)
 return name
shifts=[(i%3*150000,-(i//3)*170000) for i in range(8)]
def lines(g,lay,shift):
 for a in parts(g,'LineString'):
  coords=[world(x,y) for x,y in a.coords]
  if len(coords)>1:ms.add_lwpolyline([(x+shift[0],y+shift[1]) for x,y in coords],dxfattribs={'layer':lay})
def boundary(g,lay,shift):
 for p in parts(g,'Polygon'):
  for ring in [p.exterior,*p.interiors]:lines(LineString(ring.coords),lay,shift)
def text(s,x,y,lay,shift,h=430):
 px,py=world(x,y);ms.add_mtext(s,dxfattribs={'insert':(px+shift[0],py+shift[1]),'char_height':h,'width':6000,'attachment_point':5,'layer':lay,'style':'KOREAN'})
def rawtext(s,x,y,lay,h=600):ms.add_mtext(s,dxfattribs={'insert':(x,y),'char_height':h,'width':110000,'layer':lay,'style':'KOREAN'})
def stair_detail(g,kind,lay,shift):
 x0,y0,x1,y1=g.bounds
 # Two conceptual flights, 24 risers for 4m (166.7mm); detail remains schematic.
 if kind=='STAIR_H':
  for t in np.linspace(x0+1.3,x1-1.3,12):lines(LineString([(t,y0+.2),(t,y1-.2)]),lay,shift)
  lines(LineString([(x0+.2,(y0+y1)/2),(x1-.2,(y0+y1)/2)]),lay,shift)
 else:
  for t in np.linspace(y0+1.3,y1-1.3,12):lines(LineString([(x0+.2,t),(x1-.2,t)]),lay,shift)
  lines(LineString([((x0+x1)/2,y0+.2),((x0+x1)/2,y1-.2)]),lay,shift)
def core_door(bounds,kind):
 x0,y0,x1,y1=bounds
 if kind=='WC' and x0>10: # east core WC opens west onto lift lobby
  y=(y0+y1)/2;return LineString([(x0,y-.5),(x0,y+.5)])
 x=(x0+x1)/2
 return LineString([(x-.5,y1),(x+.5,y1)])
ref=ezdxf.readfile(str(OUT/'Drawing1_reference.dxf'));rot=np.array(REG['rotation_row']);trans=np.array(REG['translation']);context_lines=[];context_notes=[]
clip=site.buffer(12)
for e in ref.modelspace():
 if e.dxftype()=='LWPOLYLINE' and (e.dxf.layer.startswith('건물') or e.dxf.layer=='지적도'):
  co=np.array(list(e.get_points('xy')))@rot+trans
  if e.closed:co=np.vstack([co,co[0]])
  ll=LineString([local(x,y) for x,y in co]).intersection(clip).difference(site.buffer(.2))
  if not ll.is_empty:context_lines.append(ll)
 if e.dxftype()=='MTEXT' and e.dxf.layer=='text' and 'North' not in e.plain_text():
  pt=np.array([e.dxf.insert.x,e.dxf.insert.y])@rot+trans;context_notes.append((local(*pt),e.plain_text()))
basecenter=Polygon(REG['rhino_boundary']).centroid;cx,cy=basecenter.x,basecenter.y
zone_names_lab=[['재료 보관·분류','공동 작업 준비','수선·재료 이동'],['리페어 스튜디오','공개 제작·체험','Maker shop'],['교육·워크숍','공개 제작실','교육 지원'],['전문 작업실','공동 장비실','교육 갤러리'],['개인 작업실','프로젝트 작업실','작업 지원'],['개인 스튜디오','전문 스튜디오','소규모 창작실']]
zone_names_post=[['발송·포장 지원','우편물 집하','직원·운영 지원'],['민원·우편 접수','금융·상담','직원 지원'],['우체국 업무','회의·교육','운영 관리']]
for idx,z in enumerate(levelz+[41.75]):
 mezz=idx==6;tag='M' if mezz else f'L{idx}';shift=shifts[idx]
 ls={k:layer(f'{tag}_{k}',c,w,d) for k,c,w,d in [('OUTLINE',7,35,False),('PARTITION',7,18,False),('CORE',7,25,False),('DOOR',7,13,False),('STAIR',7,13,False),('EPS_PS',7,18,False),('TEXT',7,13,False),('VOID_ROOF',8,13,True),('CORRIDOR',8,13,True),('SITE_3D',7,25,False),('SITE_DWG_REF',8,13,True),('CONTEXT',8,9,False)]}
 for g in context_lines:lines(g,ls['CONTEXT'],shift)
 boundary(site,ls['SITE_3D'],shift);boundary(refsite,ls['SITE_DWG_REF'],shift)
 for (xx,yy),t in context_notes:text('참고: '+t.replace('\n',' / '),xx,yy,ls['CONTEXT'],shift,330)
 active={key:unary_union([o['p'] for o in rooms if o['key']==key and abs(o['z']-z)<.001]) for key in ['LAB','POST','MARKET']}
 if mezz:
  below=unary_union([o['p'] for o in rooms if abs(o['z']-39.75)<.001]);boundary(below,ls['VOID_ROOF'],shift)
 cores=[];circs=[];zones=[];doors=[]
 for key in ['LAB','POST']:
  fp=active[key]
  if fp.is_empty:continue
  candidates=list(lab_cores if key=='LAB' else post_cores)
  if key=='LAB' and z<=47.75:candidates+=lab_wc
  for code,name,b,kind in candidates:
   cg=box(*b);assert cg.difference(fp.buffer(.00001)).area<.001,(tag,code,'outside footprint')
   cores.append((code,name,cg,kind));doors.append(core_door(b,kind))
  cg=unary_union([q[2] for q in cores if q[0].startswith('L-' if key=='LAB' else 'P-')])
  if key=='LAB':
   circulation=unary_union([box(-1.2,4,1.2,34),box(-10,10.6,6,12.6),box(6,18.4,20,21),box(12.5,14.8,15.4,20),box(-14,20,8,22),box(-12,28.4,0,30)])
   masks=[box(-30,0,30,20),box(-30,20,30,34),box(-30,34,30,60)]
   names=zone_names_lab[idx]
  else:
   circulation=unary_union([box(-3,56,3,74),box(-12,65.7,12,67.5),box(3,71.7,12,73.5)])
   masks=[box(-30,48,30,60),box(-30,60,30,68),box(-30,68,30,80)]
   names=zone_names_post[idx]
  circulation=unary_union(parts(circulation.intersection(fp).difference(cg),'Polygon'));circs.append(circulation)
  free=fp.difference(cg.union(circulation));partition=[]
  for j,mask in enumerate(masks):
   zone=free.intersection(mask)
   for component in parts(zone,'Polygon'):
    if component.area<.00001:continue
    zones.append((key,names[j],component));partition.append(component)
  assert free.difference(unary_union(partition)).area<1.0
  boundary(fp,ls['OUTLINE'],shift)
 # Internal partition lines are merged and door gaps subtracted once.
 csum=unary_union(circs);door_cut=unary_union([g.buffer(.006) for g in doors])
 allwalls=unary_union([g.boundary for _,_,g,_ in cores]+[g.boundary for _,_,g in zones]+[g.boundary for g in circs])
 exterior=unary_union([g.boundary for g in active.values() if not g.is_empty])
 allwalls=allwalls.difference(exterior.buffer(.002)).difference(door_cut)
 lines(allwalls,ls['PARTITION'],shift)
 for code,name,g,kind in cores:
  boundary(g,ls['EPS_PS'] if kind=='SHAFT' else ls['CORE'],shift) if kind=='SHAFT' else lines(g.boundary.difference(door_cut),ls['CORE'],shift)
  pt=g.representative_point();text(code+r'\P'+name,pt.x,pt.y,ls['TEXT'],shift,230 if kind=='SHAFT' else 320)
  if kind.startswith('STAIR'):stair_detail(g,kind,ls['STAIR'],shift)
  elif kind=='LIFT':
   x0,y0,x1,y1=g.bounds;lines(LineString([(x0+.2,y0+.2),(x1-.2,y1-.2)]),ls['CORE'],shift);lines(LineString([(x1-.2,y0+.2),(x0+.2,y1-.2)]),ls['CORE'],shift)
  # Door leaf and swing indicate an opening, not a double-line wall thickness.
  if kind not in ('SHAFT',):
   dl=core_door(g.bounds,kind);a,b=list(dl.coords);dx=b[0]-a[0];dy=b[1]-a[1]
   leaf=(a[0]-dy,a[1]+dx);lines(LineString([a,leaf]),ls['DOOR'],shift)
   ang=math.atan2(dy,dx);arc=[(a[0]+math.cos(ang+t),a[1]+math.sin(ang+t)) for t in np.linspace(0,math.pi/2,13)];lines(LineString(arc),ls['DOOR'],shift)
 for key,name,g in zones:
  if g.area<9:continue
  pt=g.representative_point();text(name,pt.x,pt.y,ls['TEXT'],shift,420 if g.area>35 else 300)
 # Openings from proposed program zones to the shared circulation.
 for key,name,g in zones:
  shared=g.boundary.intersection(csum.boundary)
  candidates=[a for a in parts(shared,'LineString') if a.length>=1.4]
  if candidates:
   a=max(candidates,key=lambda a:a.length);p=a.interpolate(.5,normalized=True)
   # Short paired ticks identify a proposed door position on single-line zoning.
   text('D',p.x,p.y,ls['DOOR'],shift,230)
 for o in rs:
  if o['kind']=='public_slab' and abs(o['z']+o['h']-z)<.001:boundary(o['p'],ls['OUTLINE'],shift)
 if z in [39.75,43.75,41.75]:
  for b in [(2,34,6,40),(2,42,6,48)]:boundary(box(*b),ls['STAIR'],shift);stair_detail(box(*b),'STAIR_V',ls['STAIR'],shift)
  text('아트리움 / 공공 계단',4,44,ls['TEXT'],shift,450)
 if z==43.75:text('상부 도로 진입 Z43.75',0,1,ls['TEXT'],shift,460)
 if z==35.75:text('하부 도로 진입 Z35.75',19,53,ls['TEXT'],shift,440)
 roof=unary_union([o['p'] for o in rooms if abs(o['z']+o['h']-z)<.001]).difference(unary_union(list(active.values())))
 boundary(roof,ls['VOID_ROOF'],shift)
 if not roof.is_empty:text('점선: 하층 지붕 / 테라스',-20,53,ls['TEXT'],shift,350)
 for key,g in active.items():
  for p in parts(g,'Polygon'):
   for hole in p.interiors:
    q=Polygon(hole).representative_point();text('VOID',q.x,q.y,ls['VOID_ROOF'],shift,350)
 title=('M  아트리움 중간참' if mezz else ['B1(가칭) 서비스·지원','1F(가칭) 공공서비스·교환','2F(가칭) 교육·제작·업무','3F(가칭) 창작·갤러리','4F(가칭) 입주 작업실','L5 상부 스튜디오'][idx])+f'  |  Z {z:.2f} m'
 left=cx-65000+shift[0];top=cy+72000+shift[1]
 rawtext(title,left,top,ls['TEXT'],1100)
 rawtext('Y안 3D 외곽 + Drawing1 대지/출입 참조 | mm · 1:1 · 해치 없음 · 단선 구획',left,top-2400,ls['TEXT'],550)
 rawtext('코어·화장실·EPS/PS 위치는 신규 계획 제안. 계단 4m층고/24단 개념. 법규·피난·구조 검토 전.',left,top-4200,ls['TEXT'],450)
 rawtext('실 내부 선은 구획선. D: 실 출입 위치 제안. 문호: 코어 출입. 점선: 하층 지붕/참고 경계.',left,cy-65000+shift[1],ls['TEXT'],430)
 rawtext('SITE 실선=Y안 4,445.64㎡ / 점선=첨부 DWG 4,593.91㎡. 일부 도로 접점 경계 차이 유지.',left,cy-66700+shift[1],ls['TEXT'],430)
 rawtext('L0 Z35.75부터 4m 간격, L5 Z55.75까지 실제 모델 반영. 지상/지하 법정 층수 미확정.',left,cy-68400+shift[1],ls['TEXT'],430)
 audit.append(dict(level=tag,z=z,cores=[dict(code=c,bounds=list(g.bounds),kind=k) for c,n,g,k in cores],zones=len(zones),shift=shift))
 preview.append(dict(level=tag,z=z,active=active,cores=cores,zones=zones,circulation=circs))
# Keep original full reference out of the plans, with registration metadata in a note.
rawtext('SOURCE REGISTRATION / Y + Drawing1',cx+shifts[7][0]-60000,cy+shifts[7][1]+50000,layer('SOURCE_NOTES'),1100)
rawtext(r'17 shared SITE vertices aligned by rigid rotation+translation; no scaling.\PReference DWG site differs at the road spur. Y 3D perimeter used for plan.\PFirst plan remains in Rhino original XY; later plans use the stated sheet offsets.\PNo hatch, no fill. Original Drawing1 was not modified.',cx+shifts[7][0]-60000,cy+shifts[7][1]+46000,'SOURCE_NOTES',700)
# Duplicate identical line entities are unnecessary in single-line zoning.
seen=set();drop=[]
for e in ms.query('LWPOLYLINE'):
 co=tuple((round(x,4),round(y,4)) for x,y in e.get_points('xy'));key=(e.dxf.layer,min(co,co[::-1]))
 if key in seen:drop.append(e)
 else:seen.add(key)
for e in drop:ms.delete_entity(e)
assert not list(ms.query('HATCH'))
assert not doc.audit().has_errors
path=OUT/'Y_floor_plans_partitioned.dxf';doc.saveas(path)
(OUT/'plan_audit.json').write_text(json.dumps(dict(extracted_3d_objects=len(rs),floors=audit,reference_registration=REG['max_matched_error_mm'],entity_count=len(ms),hatch_count=0),ensure_ascii=False,indent=2))
# Internal quality-control plots, not extra user deliverables.
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');plt.rcParams['font.family']='Noto Sans CJK JP'
fig,axes=plt.subplots(2,3,figsize=(15,18))
for ax,pl in zip(axes.flat,preview):
 for g in pl['active'].values():
  for p in parts(g,'Polygon'):
   xx,yy=p.exterior.xy;ax.plot(xx,yy,color='black',lw=1)
   for ring in p.interiors:ax.plot(*ring.xy,color='gray',lw=.8)
 for key,name,g in pl['zones']:
  for p in parts(g,'Polygon'):ax.plot(*p.exterior.xy,color='#999',lw=.4)
 for code,name,g,kind in pl['cores']:
  ax.plot(*g.exterior.xy,color='red',lw=.7);pt=g.centroid;ax.text(pt.x,pt.y,code,fontsize=5,ha='center')
 ax.set_xlim(-20,23);ax.set_ylim(79,0);ax.set_aspect('equal');ax.set_title(pl['level']+' Z'+str(pl['z']));ax.axis('off')
fig.savefig(OUT/'internal_plan_check.png',dpi=120);plt.close(fig)
print('Created',path,'entities',len(ms),'core counts',[len(p['cores']) for p in preview])
