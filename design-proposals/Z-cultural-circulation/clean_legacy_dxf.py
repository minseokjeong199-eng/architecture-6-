import ezdxf
from pathlib import Path
out=Path('/workspace/design-studies/Z-floorplans');d=ezdxf.readfile(out/'Z_cultural_circulation_plans.dxf')
for name in ['ACAD_COLOR','ACAD_MATERIAL','ACAD_MLEADERSTYLE','ACAD_SCALELIST','ACAD_TABLESTYLE','ACAD_VISUALSTYLE','EZDXF_META']:
 if name in d.rootdict:del d.rootdict[name]
d.header['$DIMSTYLE']='Standard'
assert not d.audit().has_errors
d.saveas(out/'Z_cultural_circulation_plans.dxf')
