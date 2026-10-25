import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {readArchive,consume} from "./consumer.js";
const kit=readArchive(new Uint8Array(readFileSync(process.argv[2])));
const manifest=JSON.parse(new TextDecoder().decode(kit["conformance/package-semantic-manifest.json"]));
if(manifest.suite_version!=="0.1.0")throw Error("Unexpected suite version");
for(const test of manifest.cases){
 const content=kit[test.package];
 if(!content||createHash("sha256").update(content).digest("hex")!==test.sha256)throw Error("Invalid fixture "+test.id);
 let result:any=null;
 try{result=consume(content);}catch{}
 const actual=result?"accept":"reject";
 if(actual!==test.expected)throw Error(test.id+": "+actual+" expected "+test.expected);
 if(test.effective_properties){
  for(const [type,expected] of Object.entries(test.effective_properties)){
   const got=result.effective_properties.elements[type].properties;
   if(JSON.stringify(got)!==JSON.stringify(expected))throw Error(test.id+" "+type+" properties differ");
  }
 }
 console.log("PASS",test.id);
}
console.log("PASS: package-level TypeScript Core subset (not full Core conformance)");
