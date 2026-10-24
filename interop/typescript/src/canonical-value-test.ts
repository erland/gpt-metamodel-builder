import {readFileSync} from "node:fs";
import {canonicalValue} from "./consumer.js";
const vectors=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const [kind,cases] of Object.entries(vectors)){
 if(kind==="version")continue;
 for(const c of cases as any[]){
  const actual=canonicalValue(kind,c.input);
  const {input,...expected}=c;
  if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error(JSON.stringify({kind,c,actual}));
 }
}
console.log("PASS: TypeScript canonical value profile");
