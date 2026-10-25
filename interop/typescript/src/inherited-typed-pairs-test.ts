import {readFileSync} from "node:fs";
type O=Record<string,any>;
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
const suite=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const item of suite.cases){
 let actual="accept",result:O[]=[];
 try{result=effective(item.model,item.relationship);}
 catch(e){actual=String(e).includes("not_supported")?"not_supported":"error";}
 if(actual!==item.expected)throw Error(item.id+" expected "+item.expected+" got "+actual);
 if(actual==="accept"&&JSON.stringify(result)!==JSON.stringify(item.pairs))
  throw Error(item.id+" mismatched effective pairs");
}
console.log("CORE-016 inherited typed pairs TypeScript PASS");
