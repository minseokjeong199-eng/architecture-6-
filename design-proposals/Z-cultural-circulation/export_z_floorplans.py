from pathlib import Path
import json,math,hashlib
import numpy as np
import ezdxf,rhino3dm as r
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely import set_precision
from ezdxf import bbox
OUT=Path('/workspace/design-studies/Z-floorplans');D=json.load(open('/workspace/design-studies/proposal-Z/internal_geometry.json'));REG=json.load(open('/workspace/design-studies/Y-floorplans/registration.json'))
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
model=r.File3dm.Read('/workspace/design-studies/proposal-Z/Z_circulation_platform_context.3dm');records=iter(D['records']);rs=[]
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
post_cores=[('P-PEV','공공 승강기',(10.8,50.5,13.6,53.3),'LIFT'),('P-FL','업무용 리프트',(-12.5,51,-9.5,54),'LIFT'),('P-S1','계단실',(-11,61.5,-4,65.7),'STAIR_H'),('P-S2','계단실',(4,67.5,11,71.7),'STAIR_H'),('P-EV','승강기',(-2.6,61.8,-.2,64.2),'LIFT'),('P-WM','남 WC',(-2.5,68,0,72),'WC'),('P-WF','여 WC',(0,68,2.5,72),'WC'),('P-WU','장애인 WC',(-2.5,65,0,67.5),'WC'),('P-EPS','EPS',(0,65,1.2,66.4),'SHAFT'),('P-PS','PS',(0,66.4,1.2,67.5),'SHAFT'),('P-TPS','TPS',(1.2,65,2.4,66.4),'SHAFT'),('P-JAN','청소',(1.2,66.4,2.4,67.5),'SERVICE')]
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
ref=ezdxf.readfile('/workspace/design-studies/Y-floorplans/Drawing1_reference.dxf');rot=np.array(REG['rotation_row']);trans=np.array(REG['translation']);context_lines=[];context_notes=[]
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
def program_specs(key,i):
 if key=='MARKET':
  if i==0:return [('반입·재료 분류',(-6,34,0,44)),('기계·공조실',(4,34,10,42)),('전기·통신실',(10,34,16,42)),('시설 관리',(-6,44,0,50)),('카페·행사 비품',(4,44,10,50)),('직원 탈의·지원',(10,44,16,50))]
  return [('수선 상담·재료 전시',(-6,36,-2,42)),('카페 바·준비',(-6,42,-2,48)),('반납·안내',(-6,48,-2,50)),('창작품 판매·순환마켓',(12,40,16,50))]
 if key=='LAB':
  if i==0:return [('재료 보관·등록',(-16,4,0,20)),('반입 검수',(2,4,20,12)),('세척·재료 가공',(2,12,20,22)),('공동 작업 준비',(-16,22,0,34)),('재료 리프트 대기',(2,22,20,34)),('재사용 포장재',(-16,34,-6,42)),('분리배출·회수 보관',(-16,42,-8,48))]
  if i==1:return [('리페어 스튜디오',(-16,4,0,20)),('오픈 메이킹',(2,4,20,22)),('체험·수선 교실',(-16,22,0,34)),('재료 라이브러리',(2,22,20,36)),('작품·완성품 전시',(-16,34,-6,48))]
  if i==2:return [('교육·워크숍',(-16,4,0,20)),('공개 제작실',(2,4,20,22)),('교육 갤러리',(-16,22,0,34)),('재료 실습실',(2,22,20,36)),('커뮤니티 교육',(-16,34,-6,48))]
  if i==3:return [('전문 작업실',(-16,4,0,22)),('공동 장비·작업',(2,4,20,24)),('교육·작품 갤러리',(-16,22,0,34)),('시제품·재료 실험',(2,24,20,36))]
  if i==4:return [('입주 작가 작업실',(-16,4,0,24)),('프로젝트 작업실',(0,4,20,28))]
  return [('개인 스튜디오',(-16,4,4,13)),('소규모 창작실',(-16,13,4,28)),('전문 스튜디오',(4,4,20,28))]
 if i==0:return [('공공 EV 전실 / 물류 분리',(8,50,14,56)),('다기능 작업장',(-14,50,-3,61.5)),('발착 검수',(0,56,4,61.5)),('발착·소포계 사무실',(4,50,8,56)),('하역 베이 1대',(4,57.5,14,61.5)),('집배 밴 준비 1대',(4,63,14,67.5)),('집배실·순로 구분',(-14,66,-3,70)),('특수계·보안 작업',(-14,70,-8,76)),('발송 대기',(-8,70,-3,76)),('직원 휴게·갱의',(-3,73.5,7.5,76)),('직원 샤워',(7.5,73.5,10,76)),('운영 지원',(10,73.5,14,76))]
 if i==1:return [('민원·우편 접수',(2,50,14,61)),('포장·발송 지원',(-14,50,2,60)),('금고·현금관리',(4,61,8,65)),('금융·개별 상담',(2,61,14,68)),('현업실·창구 후방',(-14,60,2,68)),('보안서고·운영',(-14,68,3,76)),('직원 지원',(3,68,14,76))]
 return [('회의·지역 연계',(2,50,14,61)),('우체국 업무',(-14,50,2,61)),('업무·교육',(2,61,14,68)),('문서·정보 지원',(-14,61,3,68)),('운영 관리',(-14,68,3,76)),('직원 회의·휴게',(3,68,14,76))]
def arrow(coords,lay,shift):
 lines(LineString(coords),lay,shift)
 a=np.array(coords[-2],float);b=np.array(coords[-1],float);t=b-a;t=t/np.linalg.norm(t);n=np.array([-t[1],t[0]])
 lines(LineString([b-t*.9+n*.35,b,b-t*.9-n*.35]),lay,shift)
def develop_sequence(i,z,ls,shift):
 if i==0:
  # Separate public road lobby, service receiving, and controlled material link.
  arrow([(19,52),(14,52),(12.2,52)],ls['PUBLIC_FLOW'],shift)
  arrow([(10,59.5),(3.5,59.5),(1.5,52),(1.5,43),(2,34),(10.5,32),(10.5,30)],ls['SERVICE_FLOW'],shift)
  text('검수 → 우편 / 재료 분기',2,54,ls['TEXT'],shift,320)
  lines(LineString([(-2,50),(4,50)]),ls['PROGRAM_EDGE'],shift);text('관리문',1,50,ls['TEXT'],shift,300)
  # Proposed service courtyard entirely on site; ring is space reservation, not a swept-path certification.
  apron=box(14,56,30,77).intersection(site)
  boundary(apron,ls['VEHICLE'],shift)
  turn=Point(22,65.5).buffer(6.0,quad_segs=24)
  assert turn.difference(site).area<.01
  boundary(turn,ls['VEHICLE'],shift)
  text('회차 여유 검토\P실차 궤적 미검증',22,65.5,ls['TEXT'],shift,350)
  for name,b in [('하역 6.5×2.5',(5.5,58,12,60.5)),('집배 5.2×2.0',(6.8,64,12,66)),('집배 대기',(21,72,26.2,74))]:
   g=box(*b);assert g.difference(site).area<.01,(name,g.difference(site).area)
   boundary(g,ls['VEHICLE'],shift);pt=g.centroid;text(name,pt.x,pt.y,ls['TEXT'],shift,280)
  for k in range(4):boundary(box(14.5+k,74,15.5+k,76.5),ls['VEHICLE'],shift)
  text('집배 이륜차 4대 / 가정',16.5,77,ls['TEXT'],shift,300)
  arrow([(27.8,60.7),(23.5,61),(19,61),(14,59.3),(12,59.3)],ls['SERVICE_FLOW'],shift)
  arrow([(20,71.5),(27,68),(28,63),(27.8,60.7)],ls['SERVICE_FLOW'],shift)
  text('도로측 서비스 출입\P보행 진입은 북측 전실로 분리',29,57,ls['TEXT'],shift,380)
  text('철도측 진입 없음',-27,47,ls['TEXT'],shift,380)
 elif i==1:
  # Exchange and cafe seating are open program edges, not independent shop boxes.
  for name,b in [('교환·반납',(-2,50,2,56)),('공유 포장·발송',(2,50,8,56)),('카페 좌석 / 관찰',(-2,42,1,48))]:
   boundary(box(*b),ls['PROGRAM_EDGE'],shift);p=box(*b).centroid;text(name,p.x,p.y,ls['TEXT'],shift,350)
  for y0 in (40.5,44,47):boundary(box(12.6,y0,15.2,y0+1.6),ls['PROGRAM_EDGE'],shift)
  arrow([(12.2,52),(8,54),(4,54),(4,49),(4,46),(4,42)],ls['PUBLIC_FLOW'],shift)
  arrow([(4,46),(1,46)],ls['PUBLIC_FLOW'],shift)
  lines(LineString([(0,50),(8,50)]),ls['PROGRAM_EDGE'],shift)
  text('우체국 운영시간 분리문',4,50,ls['TEXT'],shift,300)
  text('제작·수선이 보이는 순환 홀',5,37,ls['TEXT'],shift,400)
 elif i==2:
  for b in [(-6,34,2,36),(6,34,16,36),(-6,36,-2,42),(12,36,16,42)]:boundary(box(*b),ls['PROGRAM_EDGE'],shift)
  text('교육·제작 관찰 갤러리',11,35,ls['TEXT'],shift,350)
  arrow([(0,1),(0,20),(4,24),(4,33),(4,38)],ls['PUBLIC_FLOW'],shift)
  arrow([(4,33),(9,33),(13,36),(14,40)],ls['PUBLIC_FLOW'],shift)
  text('아래: 마켓·카페·교환',5,46,ls['TEXT'],shift,350)
 elif i==6:
  boundary(box(-2,40,1,42),ls['PROGRAM_EDGE'],shift)
  text('작품 전시 / 통행 유지',-.5,41,ls['TEXT'],shift,270)
  arrow([(4,47),(4,43),(4,41),(4,39),(4,34)],ls['PUBLIC_FLOW'],shift)
 if i in (3,4,5):text('창작소는 기존 계단·EV로 수직 연결',-1,39,ls['TEXT'],shift,400)
for idx,z in enumerate(levelz+[41.75]):
 mezz=idx==6;tag='M' if mezz else f'L{idx}';shift=shifts[idx]
 ls={k:layer(f'{tag}_{k}',c,w,d) for k,c,w,d in [('OUTLINE',7,35,False),('PARTITION',7,18,False),('CORE',7,25,False),('DOOR',7,13,False),('STAIR',7,13,False),('EPS_PS',7,18,False),('TEXT',7,13,False),('VOID_ROOF',8,13,True),('CORRIDOR',8,13,True),('SITE_3D',7,25,False),('PUBLIC_FLOW',3,18,True),('SERVICE_FLOW',1,18,True),('PROGRAM_EDGE',7,13,True),('VEHICLE',8,13,False),('SITE_DWG_REF',8,13,True),('CONTEXT',8,9,False)]}
 for g in context_lines:lines(g,ls['CONTEXT'],shift)
 boundary(site,ls['SITE_3D'],shift);boundary(refsite,ls['SITE_DWG_REF'],shift)
 for (xx,yy),t in context_notes:text(('원도 주석(진입 미채택): ' if '물류' in t else '원도 참고: ')+t.replace('\n',' / '),xx,yy,ls['CONTEXT'],shift,300)
 active={key:unary_union([o['p'] for o in rooms if o['key']==key and abs(o['z']-z)<.001]) for key in ['LAB','POST','MARKET']}
 if mezz:
  below=unary_union([o['p'] for o in rooms if abs(o['z']-39.75)<.001]);boundary(below,ls['VOID_ROOF'],shift)
 cores=[];circs=[];zones=[];doors=[]
 for key in ['LAB','POST','MARKET']:
  fp=active[key]
  if fp.is_empty:continue
  candidates=list(lab_cores if key=='LAB' else post_cores if key=='POST' else [])
  if key=='LAB' and z<=47.75:candidates+=lab_wc+[('L-FL','재료용 리프트',(9,27,12,30),'LIFT')]
  for code,name,b,kind in candidates:
   cg=box(*b);assert cg.difference(fp.buffer(.00001)).area<.001,(tag,code,'outside footprint')
   cores.append((code,name,cg,kind));doors.append(core_door(b,kind))
  cg=unary_union([q[2] for q in cores if q[0].startswith('L-' if key=='LAB' else 'P-')]) if key!='MARKET' else Polygon()
  if key=='LAB':
   circulation=unary_union([box(-1.2,4,1.2,34),box(-10,10.6,6,12.6),box(6,18.4,20,21),box(12.5,14.8,15.4,20),box(-14,20,8,22),box(-12,28.4,12,30),box(9,30,12,34)])
  elif key=='POST':
   circulation=unary_union([box(-3,56,3,74),box(-12,65.7,3 if idx==0 else 12,67.5),box(3,71.7,12,73.5),box(-12,55,4,56.5)])
  else:circulation=unary_union([box(0,34,4,52),box(4,42,16,44)]) if idx==0 else Polygon()
  specs=program_specs(key,idx)
  circulation=unary_union(parts(circulation.intersection(fp).difference(cg),'Polygon'));circs.append(circulation)
  free=fp.difference(cg.union(circulation));partition=[]
  remaining=free
  for j,(name,bounds) in enumerate(specs):
   zone=remaining.intersection(box(*bounds));remaining=remaining.difference(zone)
   for component in parts(zone,'Polygon'):
    if component.area<.00001:continue
    zones.append((key,name,component));partition.append(component)
  for component in parts(remaining,'Polygon'):
   if component.area>.00001:zones.append((key,'공용·운영 지원',component));partition.append(component)
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
  text('창작 순환 홀 / 공공 계단',4,44,ls['TEXT'],shift,450)
 if z==43.75:text('상부 도로 진입 Z43.75',0,1,ls['TEXT'],shift,460)
 if z==35.75:text('도로 → 공공 전실·EV',19,53,ls['TEXT'],shift,440)
 roof=unary_union([o['p'] for o in rooms if abs(o['z']+o['h']-z)<.001]).difference(unary_union(list(active.values())))
 boundary(roof,ls['VOID_ROOF'],shift)
 if not roof.is_empty:text('점선: 하층 지붕 / 테라스',-20,53,ls['TEXT'],shift,350)
 for key,g in active.items():
  for p in parts(g,'Polygon'):
   for hole in p.interiors:
    q=Polygon(hole).representative_point();text('VOID',q.x,q.y,ls['VOID_ROOF'],shift,350)
 # Model-change/program logic overlays and deliberately separate flow layers.
 develop_sequence(idx,z,ls,shift)
 title=('M  아트리움 중간참' if mezz else ['B1(가칭) 서비스·지원','1F(가칭) 공공서비스·교환','2F(가칭) 교육·제작·업무','3F(가칭) 창작·갤러리','4F(가칭) 입주 작업실','L5 상부 스튜디오'][idx])+f'  |  Z {z:.2f} m'
 left=cx-65000+shift[0];top=cy+72000+shift[1]
 rawtext(title,left,top,ls['TEXT'],1100)
 rawtext('Z안 변경 매스 외곽 + Drawing1 대지/출입 참조 | mm · 1:1 · 해치 없음 · 단선 구획',left,top-2400,ls['TEXT'],550)
 rawtext('Z안: B1 연결 / 우체국 소형 중정 삭제 / 공공·물류 분리. 계단·승강기·설비는 검토용 계획.',left,top-4200,ls['TEXT'],450)
 rawtext('D=실 출입 제안 / 녹색=공공 동선 / 적색=물류 동선 / 점선 구역=열린 전시·마켓·휴게 영역.',left,cy-65000+shift[1],ls['TEXT'],430)
 rawtext('SITE 실선=3D 4,445.64㎡ / 점선=첨부 DWG 4,593.91㎡. 일부 도로 접점 경계 차이 유지.',left,cy-66700+shift[1],ls['TEXT'],430)
 rawtext('참고: 2013 우정사업건축 PDF pp.10·18·24·30–31. 차량·하역은 가정 치수이며 실차 회차/높이 검토 전.',left,cy-68400+shift[1],ls['TEXT'],430)
 audit.append(dict(level=tag,z=z,cores=[dict(code=c,bounds=list(g.bounds),kind=k) for c,n,g,k in cores],zones=len(zones),shift=shift))
 preview.append(dict(level=tag,z=z,active=active,cores=cores,zones=zones,circulation=circs))
# Keep original full reference out of the plans, with registration metadata in a note.
rawtext('SOURCE REGISTRATION / Z + Drawing1',cx+shifts[7][0]-60000,cy+shifts[7][1]+50000,layer('SOURCE_NOTES'),1100)
rawtext(r'17 shared SITE vertices aligned by rigid rotation+translation; no scaling.\PReference DWG site differs at the road spur. Z revised perimeter used for plan.\PFirst plan remains in Rhino original XY; later plans use the stated sheet offsets.\PNo hatch, no fill. Original Drawing1 was not modified.',cx+shifts[7][0]-60000,cy+shifts[7][1]+46000,'SOURCE_NOTES',700)
notes=[
 '설계 판단: 중앙 공공 홀에 보이드 집중. 우체국 소형 중정과 상층 노치는 폐쇄.',
 'B1: 입고·검수 → 우편물 집하/발송 또는 재료 분류 → 창작소 재료 리프트. 공공 전실과 분리.',
 '1F: 우체국 민원 → 교환·포장 허브 → 마켓·수선·카페 → 넓은 계단으로 제작·교육을 관찰.',
 '2F: 상부 골목 진입 → 교육/공개 제작 → 아트리움 갤러리 → 교환·발송으로 되돌아오는 순환.',
 '에스컬레이터는 채택하지 않음. 넓은 공공 계단 + 별도 공공 EV로 머무름과 무단차 이동 병행.',
 '집배/하역: 도로측 진입 가정. 철도측 원도 물류 주석은 현 설계 진입으로 사용하지 않음.',
 '검토 차량: 하역 6.5×2.5m 1대 / 집배 밴 5.2×2.0m 2대 / 이륜차 4대 가정. 최종 대수·톤수 미확정.',
 '원형 선은 회차 여유 검토선이며 차량 궤적 검증 결과가 아님. 대형 트럭 정기 반입은 미계획.',
 '카페는 창작/수선 활동을 바라보는 휴게 접점. 판매점의 반복보다 제작과 물품 순환을 노출.',
 '우체국 폐점 시 공유 홀과 창작소를 별도 운영할 수 있도록 교환 허브 접점에 관리문 제안.',
 '중정 폐쇄 후 깊은 내부에는 서고·지원실 배치, 상주 작업/민원실은 외곽 입면 중심 배치.',
 '우정사업건축 pp.10·18·24·30–31 참고. 사례의 시설 규모를 그대로 복사하지 않고 동선 원칙과 필수 지원 기능 반영.'
]
for n,t in enumerate(notes):rawtext(t,cx+shifts[7][0]-60000,cy+shifts[7][1]+26000-n*2600,'SOURCE_NOTES',580)
# Duplicate identical line entities are unnecessary in single-line zoning.
seen=set();drop=[]
for e in ms.query('LWPOLYLINE'):
 co=tuple((round(x,4),round(y,4)) for x,y in e.get_points('xy'));key=(e.dxf.layer,min(co,co[::-1]))
 if key in seen:drop.append(e)
 else:seen.add(key)
for e in drop:ms.delete_entity(e)
assert not list(ms.query('HATCH'))
assert not doc.audit().has_errors
path=OUT/'Z_cultural_circulation_plans.dxf';doc.saveas(path)
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
