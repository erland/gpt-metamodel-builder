import {readFileSync} from "node:fs";
import {requiredMinimumPolicy} from "./consumer.js";
const data=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const c of data.cases){
 const actual=requiredMinimumPolicy(c.required,c.cardinality);
 const {required,cardinality,...expected}=c;
 if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error("Required policy differs: "+JSON.stringify({c,actual}));
}
console.log("PASS: TypeScript opt-in required minimum policy");
