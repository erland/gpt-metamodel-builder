import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {readArchive,consume} from "./consumer.js";
type Test={id:string;expected:"accept"|"reject";package:string;sha256:string};
const args=process.argv.slice(2);
const file=args[0];
if(!file){console.error("Usage: node dist/conformance.js specification-kit.zip");process.exit(2);}
try{
 const kit=readArchive(new Uint8Array(readFileSync(file)));
 const manifest=JSON.parse(new TextDecoder().decode(kit["conformance/test-manifest.json"]));
 if(manifest.suite_version!=="1.0.0")throw Error("Unsupported test suite version");
 let passes=0;
 for(const test of manifest.cases as Test[]){
   const bytes=kit[test.package];if(!bytes)throw Error("Missing fixture: "+test.id);
   if(createHash("sha256").update(bytes).digest("hex")!==test.sha256)throw Error("Tampered fixture: "+test.id);
   let actual:"accept"|"reject"="accept";
   try{consume(bytes);}catch{actual="reject";}
   const pass=actual===test.expected;if(pass)passes++;
   console.log(`${pass?"PASS":"FAIL"} ${test.id}: expected ${test.expected}, got ${actual}`);
 }
 console.log(`MMP TypeScript conformance: ${passes}/${manifest.cases.length} PASS`);
 if(passes!==manifest.cases.length)process.exitCode=1;
}catch(e){console.error(e);process.exitCode=1;}
