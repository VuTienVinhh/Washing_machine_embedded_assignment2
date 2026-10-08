#!/usr/bin/env python3
"""Build the report with XeLaTeX. Run from any directory."""
from pathlib import Path
import shutil
import subprocess
ROOT=Path(__file__).resolve().parent
tex=ROOT/'report'
out=ROOT/'output'
out.mkdir(exist_ok=True)
if not shutil.which('xelatex'):
    raise SystemExit('Install a TeX distribution with XeLaTeX, or use Overleaf with XeLaTeX.')
for _ in range(3):
    result=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',
                           '-output-directory='+str(out),'main.tex'],cwd=tex,
                          text=True,capture_output=True)
    (out/'build_console.txt').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
    if result.returncode:
        print(result.stdout[-6000:])
        raise SystemExit(result.returncode)
dest=out/'CO3053_Assignment2_Report.pdf'
shutil.copy2(out/'main.pdf',dest)
print('Built:',dest)
