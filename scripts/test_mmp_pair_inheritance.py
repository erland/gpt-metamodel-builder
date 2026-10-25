#!/usr/bin/env python3
"""CORE-015 relation inheritance: intersection, narrowing, legacy and failure cases."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mmp_effective_pairs import effective_pairs

model={"elements":[
 {"id":"root","abstract":True},{"id":"a","extends":["root"]},{"id":"b","extends":["root"]},
 {"id":"target","abstract":True},{"id":"x","extends":["target"]},{"id":"y","extends":["target"]}],
 "relationships":[
  {"id":"wide","source":{"types":["root"]},"target":{"types":["target"]},
   "allowed_type_pairs":[{"source":"root","target":"target"}]},
  {"id":"narrow","source":{"types":["a"]},"target":{"types":["target"]},
   "allowed_type_pairs":[{"source":"a","target":"target"}]},
  {"id":"child","extends":["wide","narrow"],"source":{"types":["a"]},"target":{"types":["target"]}}
 ]}
expected=[{"source":"a","target":"x"},{"source":"a","target":"y"}]
assert effective_pairs(model,"child")==expected
assert len(effective_pairs(model,"wide"))==4
model["relationships"][2]["allowed_type_pairs"]=[{"source":"a","target":"x"}]
assert effective_pairs(model,"child")==[{"source":"a","target":"x"}]
del model["relationships"][2]["allowed_type_pairs"]
model["relationships"][1].pop("allowed_type_pairs")
try:effective_pairs(model,"child")
except ValueError as e: assert "not_supported" in str(e)
else: raise AssertionError("Inherited legacy parent was accepted as pairwise")
model["relationships"][1]["allowed_type_pairs"]=[{"source":"a","target":"target"}]
model["relationships"][0]["extends"]=["child"]
try:effective_pairs(model,"child")
except ValueError as e: assert "cycle" in str(e)
else: raise AssertionError("Relation inheritance cycle accepted")
print("CORE-015 relationship inheritance PASS")
