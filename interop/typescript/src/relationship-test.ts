import {readFileSync} from "node:fs";
import {relationshipSemantics} from "./consumer.js";
const f=JSON.parse(readFileSync(process.argv[2],"utf8"));
const {summary,allowed}=relationshipSemantics(f.elements,f.relationships);
const norm=(v:any):string=>JSON.stringify(v,(_,x)=>x&&typeof x==="object"&&!Array.isArray(x)?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a.localeCompare(b))):x);
if(norm(summary)!==norm(f.expected))throw Error("Relationship summary differs");
for(const c of f.cases)if(allowed(c.relationship,c.source,c.target)!==c.allowed)throw Error("Endpoint eligibility differs: "+JSON.stringify(c));
console.log("PASS: TypeScript relationship role and subtype semantics");
