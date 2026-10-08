#!/usr/bin/env python3
"""Package the readable source, final outputs and real test evidence."""
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
dest=ROOT.parent/'output/CO3053_Assignment2_Full_Package.zip'
dest.parent.mkdir(exist_ok=True)
files=[]
for f in sorted(ROOT.rglob('*')):
    if not f.is_file(): continue
    rel=f.relative_to(ROOT)
    if '__pycache__' in rel.parts: continue
    if rel.parts[0]=='output':
        if rel.as_posix() not in ('output/CO3053_Assignment2_Report.pdf','output/Washing_Machine_Simulator.html') and not (len(rel.parts)>2 and rel.parts[1]=='uno_build' and f.suffix=='.hex'):
            continue
    files.append(f)
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in files: z.write(f,f.relative_to(ROOT.parent).as_posix())
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for name in ('README_VI.md','TEAM_PLAN_VI.md','report/main.tex','report/skeleton.tex',
                 'firmware/washing_controller/washing_controller.ino','firmware/washing_controller/controller.h',
                 'output/CO3053_Assignment2_Report.pdf','output/Washing_Machine_Simulator.html'):
        assert ROOT.name+'/'+name in z.namelist(),name
print(f'Package checked: {len(files)} files, {dest.stat().st_size} bytes. {dest}')
