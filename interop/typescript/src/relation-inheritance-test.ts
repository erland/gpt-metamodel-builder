import {readFileSync} from "node:fs";
import {relationInheritanceProfile} from "./consumer.js";
const f=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const c of f.cases){
 const actual=relationInheritanceProfile(f.elements,c.relations);
 if(actual!==c.expected)throw Error(c.id+": "+actual+" != "+c.expected);
}
console.log("PASS: TypeScript relation inheritance profile vectors");
