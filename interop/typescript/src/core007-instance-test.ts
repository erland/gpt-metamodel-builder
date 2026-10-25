import {readFileSync} from "node:fs";

type Endpoint={cardinality?:string};
type Relation={id:string;source:Endpoint;target:Endpoint};
type Count={relationship:string;role:string;instance:string;count:number};
type Test={id:string;expected:string;model:{relationships:Relation[]};counts:Count[]};

function parseRange(value:string):[number,number|null]{
  if(!/^(?:0|[1-9][0-9]*)(?:\.\.(?:0|[1-9][0-9]*|\*))?$|^\*$/.test(value))throw Error("invalid range");
  if(value==="*")return [0,null];
  const parts=value.split("..");
  const lower=Number(parts[0]);
  const upper=parts.length===2&&parts[1]==="*"?null:Number(parts[parts.length-1]);
  if(upper!==null&&upper<lower)throw Error("inverted range");
  return [lower,upper];
}
function evaluate(model:{relationships:Relation[]},counts:Count[]):string{
  const byId=new Map(model.relationships.map(x=>[x.id,x]));
  const seen=new Set<string>();
  let violations=0;
  for(const c of counts){
    const key=JSON.stringify([c.relationship,c.role,c.instance]);
    if(seen.has(key))throw Error("duplicate key");
    seen.add(key);
    const rel=byId.get(c.relationship);
    if(!rel||(c.role!=="source"&&c.role!=="target")||typeof c.instance!=="string"||!c.instance||!Number.isSafeInteger(c.count)||c.count<0)throw Error("invalid incidence");
    const card=rel[c.role].cardinality;
    if(card===undefined)return "not_supported";
    const [min,max]=parseRange(card);
    if(c.count<min||(max!==null&&c.count>max))violations++;
  }
  return violations?"reject":"accept";
}
const path=process.argv[2];
if(!path)throw Error("Usage: core007-instance-test <vectors.json>");
const data=JSON.parse(readFileSync(path,"utf8"));
for(const test of data.cases as Test[]){
  const actual=evaluate(test.model,test.counts);
  if(actual!==test.expected)throw Error(test.id+": expected "+test.expected+", got "+actual);
}
console.log("CORE-007 TypeScript instance cardinality candidate PASS");
