import {readFileSync} from "node:fs";
import {decideRequiredDefault} from "./required-default-presence.js";
const d=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const c of d.cases){
 const actual=decideRequiredDefault(c);
 if(actual!==c.expected)throw Error(JSON.stringify({id:c.id,actual,expected:c.expected}));
}
console.log("Required/default candidate contract parity PASS");
