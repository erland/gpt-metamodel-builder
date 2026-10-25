import {readFileSync} from "node:fs";
type Obj=Record<string,any>;
function evaluate(model:Obj,graph:Obj):string{
 if(graph.complete!==true)return "not_supported";
 if(!Array.isArray(graph.junctions)||!Array.isArray(graph.edges))return "error";
 const defs=new Map<string,Obj>(model.junctions.map((j:Obj)=>[j.id,j]));
 const types=new Map<string,string>();
 for(const j of graph.junctions){
  if(typeof j.id!=="string"||!j.id||types.has(j.id)||!defs.has(j.type))return "error";
  types.set(j.id,j.type);
 }
 const degrees=new Map<string,{in:number;out:number}>([...types.keys()].map(id=>[id,{in:0,out:0}]));
 for(const edge of graph.edges){
  for(const [side,dir] of [["source","out"],["target","in"]] as const){
   const endpoint=edge[side];if(!endpoint||typeof endpoint!=="object")return "error";
   if(endpoint.kind!=="junction")continue;
   const count=degrees.get(endpoint.id);if(!count)return "error";
   count[dir]++;
  }
 }
 let issues=0;
 for(const [id,typ] of types){
  const operator=defs.get(typ)?.operator;
  if(operator!=="and"&&operator!=="or")return "not_supported";
  const d=degrees.get(id)!;
  if(d.in+d.out<2||d.in===0||d.out===0)issues++;
 }
 return issues?"reject":"accept";
}
const suite=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const c of suite.cases){
 const actual=evaluate(suite.model,c.graph);
 if(actual!==c.expected)throw Error(c.id+": expected "+c.expected+", got "+actual);
}
console.log("CORE-016 TypeScript junction structure PASS");
