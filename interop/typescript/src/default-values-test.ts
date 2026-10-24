import {readFileSync} from "node:fs";
import {validateDefaultValue} from "./consumer.js";
const cases=JSON.parse(readFileSync(process.argv[2],"utf8")).cases;
for(const c of cases){
  const got=validateDefaultValue(c.type,c.value,{values:c.values,cardinality:c.cardinality});
  if(got!==c.valid)throw new Error("Mismatch: "+JSON.stringify({case:c,got}));
}
console.log("PASS: TypeScript default semantics "+cases.length+" vectors");
