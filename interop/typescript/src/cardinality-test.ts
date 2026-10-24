import {readFileSync} from "node:fs";
import {parseCardinality,requiredProfile} from "./consumer.js";
const vectors=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const v of vectors.valid){const got=parseCardinality(v.text);if(got.min!==v.min||got.max!==v.max)throw Error("Unexpected bounds "+v.text);}
for(const value of vectors.invalid){let rejected=false;try{parseCardinality(value);}catch{rejected=true;}if(!rejected)throw Error("Invalid range accepted "+value);}
for(const v of vectors.required){if(requiredProfile(v.required,v.cardinality)!==v.strict)throw Error("Required semantics mismatch "+JSON.stringify(v));}
console.log("PASS: TypeScript cardinality vectors and undecided required semantics");
