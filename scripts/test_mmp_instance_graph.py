#!/usr/bin/env python3
"""CORE-007: complete instance graph counts, zero incidence and fail-closed inputs."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mmp_instance_graph import validate_graph

model={"elements":[{"id":"a"},{"id":"b"}],"relationships":[
 {"id":"r","source":{"types":["a"],"cardinality":"1..2"},
  "target":{"types":["b"],"cardinality":"0..*"}}]}
complete={"complete":True,"instances":[{"id":"a1","type":"a"},{"id":"b1","type":"b"}],
          "edges":[{"id":"e1","relationship":"r","source":"a1","target":"b1"}]}
assert validate_graph(model,complete)==[]
zero={**complete,"edges":[]}
assert validate_graph(model,zero)==[{"relationship":"r","role":"source","instance":"a1","count":0,"minimum":1,"maximum":2}]
two={**complete,"edges":[{"id":"e1","relationship":"r","source":"a1","target":"b1"},
                         {"id":"e2","relationship":"r","source":"a1","target":"b1"}]}
assert validate_graph(model,two)==[]
three={**two,"edges":two["edges"]+[{"id":"e3","relationship":"r","source":"a1","target":"b1"}]}
assert len(validate_graph(model,three))==1 and validate_graph(model,three)[0]["count"]==3
cases=[
 ({**complete,"complete":False},"complete=true"),
 ({**complete,"edges":[{"id":"e1","relationship":"r","source":"missing","target":"b1"}]},"dangling"),
 ({**complete,"edges":[complete["edges"][0],complete["edges"][0]]},"duplicate"),
 ({**complete,"instances":complete["instances"]+[complete["instances"][0]]},"duplicate"),
]
for bad, fragment in cases:
 try:validate_graph(model,bad)
 except ValueError as exc:assert fragment in str(exc),(fragment,str(exc))
 else:raise AssertionError("Invalid graph accepted")
typed={"elements":model["elements"],"junctions":[{"id":"junction"}],"relationships":model["relationships"]}
try:validate_graph(typed,complete)
except ValueError as exc:assert "not_supported" in str(exc)
else:raise AssertionError("Unsupported junction graph accepted")
print("CORE-007 complete graph adapter PASS")
