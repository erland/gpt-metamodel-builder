import {readFileSync} from "node:fs";
import {negotiateExtensions} from "./consumer.js";
const cases=JSON.parse(readFileSync(process.argv[2],"utf8")).cases;
for(const c of cases){
 const result=negotiateExtensions(c.requirement,c.consumer);
 if(JSON.stringify(result)!==JSON.stringify(c.expected))throw Error(c.name+": "+JSON.stringify(result));
}
console.log("PASS: TypeScript versioned extension capability negotiation");
