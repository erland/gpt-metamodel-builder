#!/usr/bin/env python3
"""CORE-015 subtype closure must be deterministic and opt-in."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mmp_effective_pairs import effective_pairs

def fixture():
    return {"elements":[
        {"id":"thing","abstract":True},
        {"id":"a","extends":["thing"]},
        {"id":"b","extends":["thing"]},
        {"id":"a_child","extends":["a"]},
        {"id":"target","abstract":True},
        {"id":"t1","extends":["target"]},
        {"id":"t2","extends":["target"]}],
        "relationships":[{"id":"link","source":{"types":["thing"]},"target":{"types":["target"]},
          "allowed_type_pairs":[{"source":"thing","target":"target"}]}]}
m=fixture()
expected=[{"source":s,"target":t} for s in ("a","a_child","b") for t in ("t1","t2")]
assert effective_pairs(m,"link")==expected
assert len(effective_pairs(m,"link"))==6
m["relationships"][0]["allowed_type_pairs"].append({"source":"thing","target":"target"})
assert effective_pairs(m,"link")==expected
m=fixture()
del m["relationships"][0]["allowed_type_pairs"]
try:effective_pairs(m,"link")
except ValueError as e:assert "not declared" in str(e)
else:raise AssertionError("Legacy relation was implicitly expanded")
m=fixture()
m["elements"][0]["extends"]=["a"]
try:effective_pairs(m,"link")
except ValueError as e:assert "cycle" in str(e)
else:raise AssertionError("Cycle accepted")
m=fixture()
m["relationships"][0]["allowed_type_pairs"]=[{"source":"missing","target":"target"}]
try:effective_pairs(m,"link")
except ValueError as e:assert "Unknown" in str(e)
else:raise AssertionError("Missing endpoint accepted")
print("CORE-015 effective pair closure PASS")
