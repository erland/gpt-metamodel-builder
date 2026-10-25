import {readFileSync} from "node:fs";
type Obj=Record<string,any>;
function evaluate(model:Obj,graph:Obj,profile:Obj):string {
 const expected=(model.junctions??[]).map((j:Obj)=>j.id).sort();
 const op=profile?.junction_operators;
 if(profile?.profile!=="mmp-junction-structure@0.1.0"||!op||typeof op!=="object"||Array.isArray(op)||
  Object.keys(profile).sort().join(",")!=="junction_operators,profile"||
  JSON.stringify(Object.keys(op).sort())!==JSON.stringify(expected)||
  !Object.values(op).every(x=>x==="and"||x==="or"))return "not_supported";
 if(graph.complete!==true)return "not_supported";
 if(!Array.isArray(graph.junctions)||!Array.isArray(graph.edges))return "error";
 const defs=new Set<string>(expected);
 const types=new Map<string,string>();
 for(const j of graph.junctions){
  if(typeof j.id!=="string"||!j.id||types.has(j.id)||!defs.has(j.type))return "error";
  types.set(j.id,j.type);
 }
 const degrees=new Map<string,{incoming:number;outgoing:number}>([...types.keys()].map(id=>[id,{incoming:0,outgoing:0}]));
 for(const edge of graph.edges){
  for(const [role,direction] of [["source","outgoing"],["target","incoming"]] as const){
   const endpoint=edge[role];
   if(!endpoint||typeof endpoint!=="object")return "error";
   if(endpoint.kind!=="junction")continue;
   const count=degrees.get(endpoint.id);
   if(!count)return "error";
   count[direction]++;
  }
 }
 for(const d of degrees.values())if(d.incoming+d.outgoing<2||!d.incoming||!d.outgoing)return "reject";
 return "accept";
}
const suite=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const item of suite.cases){
 const actual=evaluate(suite.model,item.graph,item.profile??suite.profile);
 if(actual!==item.expected)throw Error("Expected "+item.expected+", got "+actual);
}
console.log("CORE-016 TypeScript package-bound junction graph PASS");
