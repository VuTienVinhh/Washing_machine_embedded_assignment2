#!/usr/bin/env python3
from pathlib import Path
root=Path(__file__).resolve().parents[1]
html=(root/'simulator/index.html').read_text(encoding='utf-8')
js=(root/'simulator/controller.js').read_text(encoding='utf-8')
assert '<script src="controller.js"></script>' in html
html=html.replace('<script src="controller.js"></script>','<script>\n'+js+'\n</script>')
dest=root/'output/Washing_Machine_Simulator.html'
dest.parent.mkdir(exist_ok=True)
dest.write_text(html,encoding='utf-8')
print('Created standalone offline simulator:',dest)
