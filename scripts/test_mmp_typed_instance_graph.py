#!/usr/bin/env python3
"""Typed edge endpoints, recursive references and conservative CORE-016 semantics."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mmp_typed_instance_graph import validate_typed_graph

model={"elements":[{"id":"actor"},{"id":"service"}],
"relationships":[
 {"id":"serving","source":{"types":["actor"],"typed_refs":[{"kind":"element","id":"actor"}],"cardinality":"0..*"},
               "target":{"types":["service"],"typed_refs":[{"kind":"element","id":"service"}],"cardinality":"0..*"}},
 {"id":"annotation","source":{"types":[],"typed_refs":[{"kind":"relationship","id":"serving"}],"cardinality":"0..*"},
                  "target":{"types":["service"],"typed_refs":[{"kind":"element","id":"service"}],"cardinality":"0..*"},
  "allowed_typed_pairs":[{"source":{"kind":"relationship","id":"serving"},"target":{"kind":"element","id":"service"}}]}
]}
graph={"complete":True,"instances":[{"id":"a","type":"actor"},{"id":"b","type":"service"}],
"edges":[{"id":"e1","relationship":"serving","source":{"kind":"element","id":"a"},"target":{"kind":"element","id":"b"}},
         {"id":"e2","relationship":"annotation","source":{"kind":"relationship","id":"e1"},"target":{"kind":"element","id":"b"}}]}
assert validate_typed_graph(model,graph)==[]
def invalid(g,part):
 try:validate_typed_graph(model,g)
 except ValueError as e:assert part in str(e),str(e)
 else:raise AssertionError("Invalid typed graph accepted")
invalid({**graph,"complete":False},"complete=true")
invalid({**graph,"edges":[graph["edges"][0],{**graph["edges"][1],"source":{"kind":"relationship","id":"missing"}}]},"dangling")
invalid({**graph,"edges":[graph["edges"][0],{**graph["edges"][1],"source":{"kind":"element","id":"a"}}]},"outside")
invalid({**graph,"edges":[graph["edges"][0],{**graph["edges"][1],"id":"e1"}]},"invalid relationship instance")
invalid({**graph,"junctions":[{"id":"j","type":"unknown"}]},"invalid or duplicate junction instance")
print("CORE-007 relationship instance endpoints PASS")
