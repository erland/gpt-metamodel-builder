import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {readArchive,consume,strictCoreCandidate} from "./consumer.js";
const kit=readArchive(new Uint8Array(readFileSync(process.argv[2])));
const suite=JSON.parse(new TextDecoder().decode(kit["conformance/package-semantic-manifest.json"]));
for(const c of suite.cases){
 const bytes=kit[c.package];
 if(!bytes||createHash("sha256").update(bytes).digest("hex")!==c.sha256)throw Error("Hash mismatch: "+c.id);
 let legacy="reject",strict="reject";
 try{consume(bytes);legacy="accept";}catch{}
 try{strict=strictCoreCandidate(bytes).status;}catch{}
 if(legacy!==c.expected||strict!==c.strict_expected)throw Error(c.id+": "+legacy+"/"+strict);
 console.log("PASS",c.id,legacy,strict);
}
console.log("PASS TypeScript strict package profile");
