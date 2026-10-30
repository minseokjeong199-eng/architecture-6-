from pathlib import Path
s=Path('/workspace/design-studies/export_y_floorplans.py').read_text()
s=s.replace("OUT=Path('/workspace/design-studies/Y-floorplans')","OUT=Path('/workspace/design-studies/Z-floorplans')")
s=s.replace('proposal-Y','proposal-Z').replace('Y_connected_lower_storeys_context','Z_circulation_platform_context')
s=s.replace("open(OUT/'registration.json')","open('/workspace/design-studies/Y-floorplans/registration.json')")
s=s.replace("str(OUT/'Drawing1_reference.dxf')","'/workspace/design-studies/Y-floorplans/Drawing1_reference.dxf'")
s=s.replace('Y_floor_plans_partitioned','Z_cultural_circulation_plans').replace('Y안 3D','Z안 변경 매스').replace('Y + Drawing1','Z + Drawing1').replace('Y 3D perimeter','Z revised perimeter')
s=s.replace("post_cores=[", "post_cores=[('P-PEV','공공 승강기',(10.8,50.5,13.6,53.3),'LIFT'),('P-FL','업무용 리프트',(-12.5,51,-9.5,54),'LIFT'),")
s=s.replace("if key=='LAB' and z<=47.75:candidates+=lab_wc", "if key=='LAB' and z<=47.75:candidates+=lab_wc+[('L-FL','재료용 리프트',(9,27,12,30),'LIFT')]")
s=s.replace("for key in ['LAB','POST']:","for key in ['LAB','POST','MARKET']:")
s=s.replace("candidates=list(lab_cores if key=='LAB' else post_cores)","candidates=list(lab_cores if key=='LAB' else post_cores if key=='POST' else [])")
s=s.replace("cg=unary_union([q[2] for q in cores if q[0].startswith('L-' if key=='LAB' else 'P-')])", "cg=unary_union([q[2] for q in cores if q[0].startswith('L-' if key=='LAB' else 'P-')]) if key!='MARKET' else Polygon()")
a=s.index("  if key=='LAB':\n   circulation=");b=s.index("  circulation=unary_union(parts",a)
s=s[:a]+'''  if key=='LAB':
   circulation=unary_union([box(-1.2,4,1.2,34),box(-10,10.6,6,12.6),box(6,18.4,20,21),box(12.5,14.8,15.4,20),box(-14,20,8,22),box(-12,28.4,12,30),box(9,30,12,34)])
  elif key=='POST':
   circulation=unary_union([box(-3,56,3,74),box(-12,65.7,3 if idx==0 else 12,67.5),box(3,71.7,12,73.5),box(-12,55,4,56.5)])
  else:circulation=unary_union([box(0,34,4,52),box(4,42,16,44)]) if idx==0 else Polygon()
  specs=program_specs(key,idx)
''' +s[b:]
a=s.index('  for j,mask in enumerate(masks):');b=s.index('  assert free.difference',a)
s=s[:a]+'''  remaining=free
  for j,(name,bounds) in enumerate(specs):
   zone=remaining.intersection(box(*bounds));remaining=remaining.difference(zone)
   for component in parts(zone,'Polygon'):
    if component.area<.00001:continue
    zones.append((key,name,component));partition.append(component)
  for component in parts(remaining,'Polygon'):
   if component.area>.00001:zones.append((key,'공용·운영 지원',component));partition.append(component)
''' +s[b:]
s=s.replace("'SITE_3D',7,25,False),", "'SITE_3D',7,25,False),('PUBLIC_FLOW',3,18,True),('SERVICE_FLOW',1,18,True),('PROGRAM_EDGE',7,13,True),('VEHICLE',8,13,False),")
s=s.replace("text('참고: '+t.replace('\\n',' / '),xx,yy,ls['CONTEXT'],shift,330)", "text(('원도 주석(진입 미채택): ' if '물류' in t else '원도 참고: ')+t.replace('\\n',' / '),xx,yy,ls['CONTEXT'],shift,300)")
# insert detailed program and movement helpers before floor loop
pos=s.index('for idx,z in enumerate(levelz+[41.75]):')
s=s[:pos]+Path('/workspace/design-studies/z_program_helpers.py').read_text()+s[pos:]
pos=s.index(' title=(',s.index('for idx,z in enumerate(levelz+[41.75]):'))
s=s[:pos]+''' # Model-change/program logic overlays and deliberately separate flow layers.
 develop_sequence(idx,z,ls,shift)
''' +s[pos:]
s=s.replace("'아트리움 / 공공 계단'","'창작 순환 홀 / 공공 계단'")
s=s.replace("'하부 도로 진입 Z35.75'","'도로 → 공공 전실·EV'")
s=s.replace("'Y안 4,445.64㎡", "'Z안 4,445.64㎡")
s=s.replace("SITE 실선=Y안", "SITE 실선=3D")
s=s.replace("코어·화장실·EPS/PS 위치는 신규 계획 제안. 계단 4m층고/24단 개념. 법규·피난·구조 검토 전.","Z안: B1 연결 / 우체국 소형 중정 삭제 / 공공·물류 분리. 계단·승강기·설비는 검토용 계획.")
s=s.replace("실 내부 선은 구획선. D: 실 출입 위치 제안. 문호: 코어 출입. 점선: 하층 지붕/참고 경계.","D=실 출입 제안 / 녹색=공공 동선 / 적색=물류 동선 / 점선 구역=열린 전시·마켓·휴게 영역.")
s=s.replace("L0 Z35.75부터 4m 간격, L5 Z55.75까지 실제 모델 반영. 지상/지하 법정 층수 미확정.","참고: 2013 우정사업건축 PDF pp.10·18·24·30–31. 차량·하역은 가정 치수이며 실차 회차/높이 검토 전.")
# add review-note sheet focused on decisions and operating sequence.
s=s.replace("rawtext('SOURCE REGISTRATION / Y + Drawing1'", "rawtext('Z DESIGN / SOURCE REGISTRATION'")
pos=s.index('# Duplicate identical line entities')
s=s[:pos]+'''notes=[
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
''' +s[pos:]
Path('/workspace/design-studies/export_z_floorplans.py').write_text(s)
exec(compile(s,'/workspace/design-studies/export_z_floorplans.py','exec'))
