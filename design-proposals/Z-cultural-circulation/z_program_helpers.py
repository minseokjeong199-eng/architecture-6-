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
