import {readFileSync} from "node:fs";
import {effectiveProperties} from "./consumer.js";
const f=JSON.parse(readFileSync(process.argv[2],"utf8"));
const result=effectiveProperties(f.elements,f.relationships,f.property_sets,f.property_definitions);
if(JSON.stringify(result)!==JSON.stringify(f.expected)){
  console.error(JSON.stringify({expected:f.expected,actual:result},null,2));process.exit(1);
}
console.log("PASS: TypeScript diamond-inheritance effective properties match golden semantics");
