#!/usr/bin/env python3
"""CORE-016 full candidate ZIP -> independent consumers -> instance graph acceptance."""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
 return subprocess.run([str(a) for a in args],cwd=ROOT,capture_output=True,text=True)
def main():
 with tempfile.TemporaryDirectory() as td:
  work=Path(td);model=work/"model";shutil.copytree(ROOT/"examples/architecture-lite",model)
  path=model/"metamodel.yaml";doc=yaml.safe_load(path.read_text())
  fixture=json.loads((ROOT/"interop/core016-inherited-instance-graph-v1.json").read_text())
  original=fixture["model"]
  doc["metamodel"]["namespace"]="https://example.org/core016/inherited-pairs-package"
  doc["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[
   {"id":"mmp-typed-endpoints","version":"1.0.0"},
   {"id":"mmp-typed-pairs","version":"1.0.0"}]
  # The fixture is a reduced graph-analysis contract; preserve names required
  # by the canonical schema and use valid source/target type domains.
  # Keep the reference example intact: its viewpoints and styles use old types.
  # Extend rather than replace it.
  doc["elements"].extend({"id":e["id"],"name":e["id"].upper()} for e in original["elements"])
  doc.setdefault("junctions",[]).extend({"id":j["id"],"name":"Junction "+j["id"]} for j in original["junctions"])
  for rel in original["relationships"]:
   doc["relationships"].append({
    **rel,"name":rel["id"].upper(),
    "source":{**rel["source"],"types":["a","b"]},
    "target":{**rel["target"],"types":["b"]}})
  path.write_text(yaml.safe_dump(doc,sort_keys=False));before=path.read_bytes()
  package=work/"candidate.zip"
  result=run(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1","--model-dir",model,"--output",package)
  assert result.returncode==0,result.stderr
  verified=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)
  assert verified.returncode==0,verified.stderr
  sys.path.insert(0,str(ROOT/"interop"))
  from mmp_v1_consumer import consume
  assert consume(package)["package_format_version"]=="1.1.0"
  if "--typescript" in sys.argv:
   consumer=run("node",ROOT/"interop/typescript/dist/consumer.js",package)
   assert consumer.returncode==0,consumer.stderr
  output=work/"imported"
  restored=run(sys.executable,ROOT/"scripts/import_mmp.py","import",package,"--output",output)
  assert restored.returncode==0,restored.stderr
  assert (output/"metamodel.yaml").read_bytes()==before
  imported=yaml.safe_load((output/"metamodel.yaml").read_text())
  # The package includes legacy relationships without typed domains; the
  # opt-in typed graph adapter is only defined for the candidate relation subset.
  typed_ids={rel["id"] for rel in original["relationships"]}
  graph_model={**imported,"relationships":[r for r in imported["relationships"] if r["id"] in typed_ids]}
  graph_vectors={"suite_version":"1.0.0","model":graph_model,
                 "cases":fixture["cases"]}
  sys.path.insert(0,str(ROOT/"scripts"))
  from mmp_typed_instance_graph import validate_typed_graph
  for case in fixture["cases"]:
   candidate=case.get("model",graph_model)
   try:
    verdict="reject" if validate_typed_graph(candidate,case["graph"]) else "accept"
   except ValueError as exc:
    verdict="not_supported" if "not_supported" in str(exc) else "error"
   assert verdict==case["expected"],(case["id"],verdict,case["expected"])
  if "--typescript" in sys.argv:
   vectors=work/"vectors.json";vectors.write_text(json.dumps(graph_vectors))
   ts=run("node",ROOT/"interop/typescript/dist/typed-graph-test.js",vectors)
   assert ts.returncode==0,ts.stderr
  legacy=work/"legacy.zip"
  old=run(sys.executable,ROOT/"scripts/export_mmp.py","--model-dir",model,"--output",legacy)
  assert old.returncode!=0 and not legacy.exists()
  assert path.read_bytes()==before
 print("CORE-016 inherited typed pairs full candidate package PASS")
if __name__=="__main__":main()
