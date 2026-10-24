import {readFileSync} from "node:fs";
import {classifyModelChange,extensionSupport} from "./consumer.js";
const vectors=JSON.parse(readFileSync(process.argv[2],"utf8"));
for(const c of vectors.cases)if(classifyModelChange(c.before,c.after)!==c.expected)throw Error("Diff mismatch "+c.name);
for(const c of vectors.extensions)if(extensionSupport(c.extensions,c.recognized,c.critical)!==c.expected)throw Error("Extension mismatch");
console.log("PASS: TypeScript conservative version compatibility and extension policy");
