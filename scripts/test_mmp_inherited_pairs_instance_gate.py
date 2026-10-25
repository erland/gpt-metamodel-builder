#!/usr/bin/env python3
"""CORE-016: inherited exact typed pairs enforced in a complete instance graph."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_typed_instance_graph import validate_typed_graph

def reference(kind,ident):return {"kind":kind,"id":ident}
a=reference("element","a")
b=reference("element","b")
j=reference("junction","j")
def pair(source,target):return {"source":source,"target":target}
def endpoint(refs):return {"types":[],"typed_refs":refs,"cardinality":"0..*"}
def relation(ident,pairs=None,parents=None):
 result={"id":ident,"source":endpoint([a,b]),"target":endpoint([j,b])}
 if parents:result["extends"]=parents
 if pairs is not None:result["allowed_typed_pairs"]=pairs
 return result
model={"elements":[{"id":"a"},{"id":"b"}],"junctions":[{"id":"j"}],
 "relationships":[relation("p1",[pair(a,j),pair(b,j)]),
                  relation("p2",[pair(a,j),pair(a,b)]),
                  relation("child",parents=["p1","p2"])]}
def graph(source="a",target="j"):
 return {"complete":True,"instances":[{"id":"one","type":"a"},{"id":"two","type":"b"}],
         "junctions":[{"id":"junction1","type":"j"}],
         "edges":[{"id":"edge1","relationship":"child",
                   "source":{"kind":"element","id":"one" if source=="a" else "two"},
                   "target":{"kind":"junction" if target=="j" else "element",
                             "id":"junction1" if target=="j" else "two"}}]}
assert validate_typed_graph(model,graph())==[]
try:validate_typed_graph(model,graph("b"))
except ValueError as e:assert "typed pair disallowed" in str(e)
else:raise AssertionError("Inherited restriction not enforced")
try:validate_typed_graph(model,graph("a","b"))
except ValueError as e:assert "typed pair disallowed" in str(e)
else:raise AssertionError("Inherited pair intersection not enforced")
model["relationships"][1].pop("allowed_typed_pairs")
try:validate_typed_graph(model,graph())
except ValueError as e:assert "not_supported" in str(e)
else:raise AssertionError("Undeclared parent contract accepted")
print("CORE-016 inherited instance pair gate PASS")
