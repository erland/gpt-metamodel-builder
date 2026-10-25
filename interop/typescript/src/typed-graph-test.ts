import {readFileSync} from "node:fs";
type Obj=Record<string,any>;
function graphResult(model:Obj,graph:Obj):string{
  if(graph.complete!==true)return "not_supported";
  const elements=new Set<string>(model.elements.map((e:Obj)=>e.id));
  const junctionDefs=new Set<string>(model.junctions.map((e:Obj)=>e.id));
  const rels=new Map<string,Obj>(model.relationships.map((r:Obj)=>[r.id,r]));
  if(!Array.isArray(graph.instances)||!Array.isArray(graph.edges)||!Array.isArray(graph.junctions))return "error";
  const maps:Record<string,Map<string,string>>={element:new Map(),relationship:new Map(),junction:new Map()};
  for(const node of graph.instances){
    if(typeof node.id!=="string"||!node.id||maps.element.has(node.id)||!elements.has(node.type))return "error";
    maps.element.set(node.id,node.type);
  }
  for(const edge of graph.edges){
    if(typeof edge.id!=="string"||!edge.id||maps.relationship.has(edge.id)||maps.element.has(edge.id)||!rels.has(edge.relationship))return "error";
    maps.relationship.set(edge.id,edge.relationship);
  }
  for(const j of graph.junctions){
    if(typeof j.id!=="string"||!j.id||Object.values(maps).some(m=>m.has(j.id))||!junctionDefs.has(j.type))return "error";
    maps.junction.set(j.id,j.type);
  }
  const counts=new Map<string,number>();
  const key=(r:string,role:string,kind:string,id:string)=>JSON.stringify([r,role,kind,id]);
  for(const edge of graph.edges){
    const rel=rels.get(edge.relationship)!;
    for(const role of ["source","target"]){
      const endpoint=edge[role];
      if(!endpoint||typeof endpoint!=="object"||Object.keys(endpoint).sort().join(",")!=="id,kind")return "error";
      const kind=endpoint.kind,id=endpoint.id;
      if(!maps[kind]?.has(id))return "error";
      const actual=maps[kind].get(id);
      const refs=rel[role].typed_refs;
      if(!Array.isArray(refs))return "not_supported";
      if(!refs.some((ref:Obj)=>ref.kind===kind&&ref.id===actual))return "error";
      const k=key(rel.id,role,kind,id);counts.set(k,(counts.get(k)??0)+1);
    }
    if(rel.allowed_typed_pairs!==undefined){
      const pair=rel.allowed_typed_pairs.some((p:Obj)=>["source","target"].every(role=>
        p[role].kind===edge[role].kind&&p[role].id===maps[edge[role].kind].get(edge[role].id)));
      if(!pair)return "error";
    }
  }
  let violations=0;
  for(const rel of model.relationships){
    for(const role of ["source","target"]){
      const endpoint=rel[role];
      if(!Array.isArray(endpoint.typed_refs))return "not_supported";
      for(const ref of endpoint.typed_refs){
        if(!maps[ref.kind])return "error";
        for(const [id,type] of maps[ref.kind]){
          if(type!==ref.id)continue;
          const card=endpoint.cardinality;
          if(typeof card!=="string")return "not_supported";
          const m=/^(0|[1-9][0-9]*)(?:\\.\\.(0|[1-9][0-9]*|\\*))?$|^(\\*)$/.exec(card);
          if(!m)return "error";
          const min=m[3]?0:Number(m[1]);
          const max=m[3]||m[2]==="*"?null:Number(m[2]??m[1]);
          if(max!==null&&max<min)return "error";
          const value=counts.get(key(rel.id,role,ref.kind,id))??0;
          if(value<min||(max!==null&&value>max))violations++;
        }
      }
    }
  }
  return violations?"reject":"accept";
}
const path=process.argv[2];
if(!path)throw Error("Missing vectors path");
const suite=JSON.parse(readFileSync(path,"utf8"));
for(const c of suite.cases){
 const actual=graphResult(suite.model,c.graph);
 if(actual!==c.expected)throw Error(c.id+": expected "+c.expected+" got "+actual);
}
console.log("CORE-007/016 TypeScript typed graph vectors PASS");
