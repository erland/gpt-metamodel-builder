import {readFileSync} from "node:fs";
import {effectiveProperties} from "./consumer.js";
const f=JSON.parse(readFileSync(process.argv[2],"utf8"));
const result=effectiveProperties(f.elements,f.relationships,f.property_sets,f.property_definitions);
const canonical=(value:any):string=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
if(canonical(result)!==canonical(f.expected)){
  console.error(JSON.stringify({expected:f.expected,actual:result},null,2));process.exit(1);
}
console.log("PASS: TypeScript diamond-inheritance effective properties match golden semantics");
