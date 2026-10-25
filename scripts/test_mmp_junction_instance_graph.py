#!/usr/bin/env python3
"""CORE-007: explicit junction instances, typed pair constraints and incidence."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mmp_typed_instance_graph import validate_typed_graph

model={
 "elements":[{"id":"actor"},{"id":"service"}],
 "junctions":[{"id":"and_junction"}],
 "relationships":[
  {"id":"link","source":{"types":["actor"],"typed_refs":[{"kind":"element","id":"actor"}],"cardinality":"0..*"},
   "target":{"types":[],"typed_refs":[{"kind":"junction","id":"and_junction"}],"cardinality":"1..2"},
   "allowed_typed_pairs":[{"source":{"kind":"element","id":"actor"},"target":{"kind":"junction","id":"and_junction"}}]},
  {"id":"out","source":{"types":[],"typed_refs":[{"kind":"junction","id":"and_junction"}],"cardinality":"0..*"},
   "target":{"types":["service"],"typed_refs":[{"kind":"element","id":"service"}],"cardinality":"0..*"},
   "allowed_typed_pairs":[{"source":{"kind":"junction","id":"and_junction"},"target":{"kind":"element","id":"service"}}]}
 ]}
graph={"complete":True,"instances":[{"id":"a","type":"actor"},{"id":"b","type":"service"}],
 "junctions":[{"id":"j","type":"and_junction"}],
 "edges":[
  {"id":"e1","relationship":"link","source":{"kind":"element","id":"a"},"target":{"kind":"junction","id":"j"}},
  {"id":"e2","relationship":"out","source":{"kind":"junction","id":"j"},"target":{"kind":"element","id":"b"}}]}
assert validate_typed_graph(model,graph)==[]
empty={**graph,"edges":[graph["edges"][1]]}
issues=validate_typed_graph(model,empty)
assert len(issues)==1 and issues[0]["relationship"]=="link" and issues[0]["count"]==0,issues
def failure(graph, fragment):
 try:validate_typed_graph(model,graph)
 except ValueError as exc:assert fragment in str(exc),str(exc)
 else:raise AssertionError("Invalid junction graph accepted")
failure({**graph,"junctions":[{"id":"j","type":"unknown"}]},"invalid or duplicate junction")
failure({**graph,"junctions":[graph["junctions"][0],graph["junctions"][0]]},"invalid or duplicate junction")
failure({**graph,"edges":[{**graph["edges"][0],"target":{"kind":"junction","id":"missing"}},graph["edges"][1]]},"dangling")
failure({**graph,"complete":False},"complete=true")
failure({**graph,"edges":[{**graph["edges"][0],"source":{"kind":"junction","id":"j"}},graph["edges"][1]]},"outside declared domain")
print("CORE-007 junction instance topology PASS")
