import {readFileSync} from "node:fs";
type Obj=Record<string,any>;
type O=Obj;
function effective(model:O,id:string):O[]{
 const rels=new Map<string,O>(model.relationships.map((r:O)=>[r.id,r]));
 const known:Record<string,Set<string>>={
  element:new Set((model.elements??[]).map((r:O)=>r.id)),
  relationship:new Set(rels.keys()),
  junction:new Set((model.junctions??[]).map((r:O)=>r.id))
 };
 const ref=(x:O):string=>{
  if(!x||typeof x!=="object"||Object.keys(x).sort().join(",")!=="id,kind"||
      !known[x.kind]?.has(x.id))throw Error("invalid typed ref");
  return JSON.stringify([x.kind,x.id]);
 };
 const pair=(p:O):string=>{
  if(!p||Object.keys(p).sort().join(",")!=="source,target")throw Error("invalid pair");
  return JSON.stringify([ref(p.source),ref(p.target)]);
 };
 const walk=(rid:string,visiting:Set<string>):Set<string>[]=>{
  const rel=rels.get(rid);
  if(!rel)throw Error("unknown relationship");
  if(visiting.has(rid))throw Error("inheritance cycle");
  const next=new Set([...visiting,rid]);
  const constraints:Set<string>[]=[];
  for(const parent of rel.extends??[]){
   const values=walk(parent,next);
   if(!values.length)throw Error("not_supported parent undeclared");
   constraints.push(...values);
  }
  if(rel.allowed_typed_pairs!==undefined)
   constraints.push(new Set(rel.allowed_typed_pairs.map(pair)));
  return constraints;
 };
 const constraints=walk(id,new Set());
 if(!constraints.length)throw Error("not_supported no contract");
 let keys=new Set(constraints[0]);
 for(const restriction of constraints.slice(1))keys=new Set([...keys].filter(v=>restriction.has(v)));
 if(!keys.size)throw Error("empty intersection");
 const child=rels.get(id)!;
 const domains=["source","target"].map(side=>{
  const domain=child[side]?.typed_refs;
  if(!Array.isArray(domain))throw Error("not_supported missing typed domain");
  return new Set<string>(domain.map(ref));
 });
 keys=new Set([...keys].filter(value=>{
  const [left,right]=JSON.parse(value) as string[];
  return domains[0].has(left)&&domains[1].has(right);
 }));
 if(!keys.size)throw Error("no pairs in domains");
 return [...keys].map(value=>{
  const [s,t]=JSON.parse(value) as string[];
  const [sk,si]=JSON.parse(s),[tk,ti]=JSON.parse(t);
  return {source:{kind:sk,id:si},target:{kind:tk,id:ti}};
 }).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)));
}

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
  // Relationship-instance dependency cycles have no supported meaning yet.
  const dependencies=new Map<string,string[]>();
  for(const edge of graph.edges){
    dependencies.set(edge.id,["source","target"]
      .map(role=>edge[role])
      .filter((endpoint:Obj)=>endpoint?.kind==="relationship"&&maps.relationship.has(endpoint.id))
      .map((endpoint:Obj)=>endpoint.id));
  }
  const states=new Map<string,number>();
  const visit=(id:string):boolean=>{
    if(states.get(id)===1)return false;
    if(states.get(id)===2)return true;
    states.set(id,1);
    for(const dependency of dependencies.get(id)??[])if(!visit(dependency))return false;
    states.set(id,2);return true;
  };
  for(const id of dependencies.keys())if(!visit(id))return "not_supported";
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
    if(rel.allowed_typed_pairs!==undefined||(rel.extends??[]).length>0){
      let allowed:Obj[];
      try{allowed=effective(model,rel.id);}
      catch(error){return String(error).includes("not_supported")?"not_supported":"error";}
      const pair=allowed.some((p:Obj)=>["source","target"].every(role=>
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
          const m=/^(0|[1-9][0-9]*)(?:\.\.(0|[1-9][0-9]*|\*))?$|^(\*)$/.exec(card);
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
