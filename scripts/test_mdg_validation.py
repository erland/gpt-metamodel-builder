#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys, tempfile, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]; CAN=ROOT/'examples/architecture-lite'; AD=CAN/'platforms/sparx-ea'
def run(args,expect=0):
    r=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if (r.returncode==0)!=(expect==0):
        print(r.stdout); print(r.stderr,file=sys.stderr); raise SystemExit('unexpected return code')
with tempfile.TemporaryDirectory() as td:
    good=Path(td)/'good.xml'
    run([sys.executable,'scripts/generate_sparx_mdg.py','--canonical',str(CAN),'--adapter',str(AD),'--output',str(good)])
    run([sys.executable,'scripts/validate_generated_mdg.py','--xml',str(good),'--canonical',str(CAN),'--adapter',str(AD)])
    tree=ET.parse(good); root=tree.getroot(); first=next(x for x in root.findall('UMLProfiles/UMLProfile/Content/Stereotypes/Stereotype') if x.get('_image'))
    first.attrib.pop('_image'); bad=Path(td)/'missing-shape.xml'; tree.write(bad,encoding='utf-8',xml_declaration=True)
    run([sys.executable,'scripts/validate_generated_mdg.py','--xml',str(bad),'--canonical',str(CAN),'--adapter',str(AD)],expect=1)
    tree=ET.parse(good); root=tree.getroot(); prop=root.find("DiagramProfile/UMLProfile/Content/Stereotypes/Stereotype/AppliesTo/Apply/Property[@name='toolbox']"); prop.set('value','does_not_exist'); bad2=Path(td)/'bad-toolbox.xml'; tree.write(bad2,encoding='utf-8',xml_declaration=True)
    run([sys.executable,'scripts/validate_generated_mdg.py','--xml',str(bad2),'--canonical',str(CAN),'--adapter',str(AD)],expect=1)
print('MDG validation regression tests: PASS')
