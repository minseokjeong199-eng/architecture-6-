import ezdxf
from pathlib import Path
out=Path('/workspace/design-studies/Y-floorplans');d=ezdxf.readfile(out/'Y_floor_plans_partitioned.dxf')
for name in ['ACAD_COLOR','ACAD_MATERIAL','ACAD_MLEADERSTYLE','ACAD_SCALELIST','ACAD_TABLESTYLE','ACAD_VISUALSTYLE','EZDXF_META']:
 if name in d.rootdict:del d.rootdict[name]
d.header['$DIMSTYLE']='Standard'
assert not d.audit().has_errors
d.saveas(out/'Y_floor_plans_partitioned.dxf')
