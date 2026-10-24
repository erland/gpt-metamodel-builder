import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { unzipSync } from "fflate";
import YAML from "yaml";
import Ajv from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

type Obj = Record<string, any>;
const required = ["metamodel","properties","constraints","viewpoints","notation","provenance","version"];
function ensure(ok: unknown, message: string): asserts ok { if (!ok) throw new Error(message); }
function validPath(p:string): boolean {
  return p.length>0 && !p.startsWith("/") && !p.includes("\\") && !/^[a-zA-Z]:/.test(p)
    && p.split("/").every(x=>x!==""&&x!=="."&&x!=="..");
}
export function readArchive(bytes:Uint8Array): Record<string,Uint8Array> {
  const files=unzipSync(bytes);
  const names=Object.keys(files);
  ensure(names.length<=300,"Too many files");
  ensure(names.every(validPath),"Unsafe ZIP member path");
  ensure(names.every(x=>!x.endsWith("/")),"Directory member not supported");
  ensure(names.reduce((s,n)=>s+files[n].byteLength,0)<=33554432,"Archive too large");
  // ZIP readers may overwrite duplicates when materializing maps. Reject them from central directory.
  const view=new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  let end=-1;
  for(let i=bytes.length-22;i>=Math.max(0,bytes.length-65557);i--){
    if(view.getUint32(i,true)===0x06054b50){end=i;break;}
  }
  ensure(end>=0,"ZIP central directory missing");
  const count=view.getUint16(end+10,true);
  let offset=view.getUint32(end+16,true);
  const seen=new Set<string>();
  const decoder=new TextDecoder();
  for(let i=0;i<count;i++){
    ensure(view.getUint32(offset,true)===0x02014b50,"Malformed central directory");
    const len=view.getUint16(offset+28,true),extra=view.getUint16(offset+30,true),comment=view.getUint16(offset+32,true);
    const name=decoder.decode(bytes.subarray(offset+46,offset+46+len));
    ensure(!seen.has(name),"Duplicate ZIP entry");
    seen.add(name);
    const external=view.getUint32(offset+38,true);
    ensure(((external>>>16)&0xf000)!==0xa000,"ZIP symlink forbidden");
    const rawSize=view.getUint32(offset+24,true),zipSize=view.getUint32(offset+20,true);
    ensure(rawSize<=8388608 && (rawSize===0 || (zipSize>0&&rawSize/zipSize<=200)),"Oversized compressed member");
    offset+=46+len+extra+comment;
  }
  ensure(seen.size===names.length,"ZIP inventory mismatch");
  return files;
}
const decoder = new TextDecoder();
function parseYaml(bytes:Uint8Array):Obj { const value=YAML.parse(decoder.decode(bytes),{uniqueKeys:true});ensure(value&&typeof value==="object"&&!Array.isArray(value),"Invalid YAML object");return value; }
function ids(items:Obj[],label:string):Set<string> {const found=new Set<string>();for(const item of items){ensure(typeof item.id==="string"&&!found.has(item.id),"Duplicate/invalid ID: "+label);found.add(item.id);}return found;}
function graph(items:Obj[],available:Set<string>):void {
  const lookup=new Map(items.map((x:Obj)=>[x.id,x]));
  const visiting=new Set<string>(),visited=new Set<string>();
  function visit(id:string){ensure(!visiting.has(id),"Inheritance cycle");if(visited.has(id))return;
    visiting.add(id);for(const parent of lookup.get(id)?.extends??[]){ensure(available.has(parent),"Unknown inherited type");visit(parent);}
    visiting.delete(id);visited.add(id);
  }
  for(const id of available)visit(id);
}
function sha(bytes:Uint8Array):string{return createHash("sha256").update(bytes).digest("hex");}

export function parseCardinality(value:string):{min:number;max:number|null} {
  if(value==="*")return {min:0,max:null};
  const number="(?:0|[1-9][0-9]*)";
  if(new RegExp("^"+number+"$").test(value)){
    const n=Number(value);ensure(Number.isSafeInteger(n),"Cardinality exceeds safe integer");return {min:n,max:n};
  }
  const match=new RegExp("^("+number+")[.][.]("+number+"|[*])$").exec(value);
  ensure(match,"Invalid cardinality syntax");
  const min=Number(match[1]),max=match[2]==="*"?null:Number(match[2]);
  ensure(Number.isSafeInteger(min)&&(max===null||Number.isSafeInteger(max)),"Cardinality exceeds safe integer");
  ensure(max===null||min<=max,"Inverted cardinality interval");
  return {min,max};
}
export function requiredProfile(required:boolean,cardinality:string|null):"accept"|"undecided" {
  if(cardinality===null)return "accept";
  const b=parseCardinality(cardinality);
  return required===true&&b.min===0?"undecided":"accept";
}


export function validateDefaultValue(typeName:string,value:any,opts:{values?:string[];cardinality?:string}={}):boolean {
  if(opts.cardinality!==undefined){
    const b=parseCardinality(opts.cardinality);
    const count=Array.isArray(value)?value.length:1;
    if(count<b.min||(b.max!==null&&count>b.max))return false;
  }else if(Array.isArray(value))return false;
  const items=Array.isArray(value)?value:[value];
  return items.every(item=>{
    switch(typeName){
      case "string":return typeof item==="string";
      case "identifier":return typeof item==="string"&&item.length>0;
      case "integer":return typeof item==="number"&&Number.isSafeInteger(item);
      case "decimal":return typeof item==="number"&&Number.isFinite(item);
      case "boolean":return typeof item==="boolean";
      case "date":{
        if(typeof item!=="string"||!/^\d{4}-\d{2}-\d{2}$/.test(item))return false;
        const [y,m,d]=item.split("-").map(Number);
        const dt=new Date(Date.UTC(y,m-1,d));
        return dt.getUTCFullYear()===y&&dt.getUTCMonth()+1===m&&dt.getUTCDate()===d;
      }
      case "datetime":{
        if(typeof item!=="string"||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})$/.test(item))return false;
        return !Number.isNaN(Date.parse(item));
      }
      case "uri":return typeof item==="string"&&/^[A-Za-z][A-Za-z0-9+.-]*:/.test(item)&&!/[\s]/.test(item);
      case "enumeration":return typeof item==="string"&&Array.isArray(opts.values)&&opts.values.includes(item);
      default:return false;
    }
  });
}


export function relationshipSemantics(elements:Obj[],relationships:Obj[]){
  const byElement=new Map<string,Obj>(elements.map(x=>[x.id,x]));
  const byRelation=new Map<string,Obj>(relationships.map(x=>[x.id,x]));
  const descendants=(id:string,ancestor:string):boolean=>{
    const seen=new Set<string>(),todo=[id];
    while(todo.length){const current=todo.pop()!;
      if(current===ancestor)return true;
      if(seen.has(current)||!byElement.has(current))continue;
      seen.add(current);todo.push(...(byElement.get(current)!.extends??[]));
    }
    return false;
  };
  const summary:Obj={};
  for(const id of [...byRelation.keys()].sort()){
    const r=byRelation.get(id)!;
    summary[id]={directed:r.directed??true,source_types:[...r.source.types].sort(),
      target_types:[...r.target.types].sort(),source_navigable:r.source.navigable??null,
      target_navigable:r.target.navigable??null};
  }
  const allowed=(rel:string,source:string,target:string):boolean=>{
    const r=byRelation.get(rel);
    if(!r||!byElement.has(source)||!byElement.has(target))return false;
    return r.source.types.some((t:string)=>descendants(source,t))
      && r.target.types.some((t:string)=>descendants(target,t));
  };
  return {summary,allowed};
}


export function classifyModelChange(before:Obj,after:Obj):"breaking"|"compatible"|"needs_review" {
  if(before.namespace!==after.namespace)return "breaking";
  let uncertain=false;
  for(const group of ["elements","relationships"]){
    const old=new Map<string,Obj>((before[group]??[]).map((x:Obj)=>[x.id,x]));
    const next=new Map<string,Obj>((after[group]??[]).map((x:Obj)=>[x.id,x]));
    for(const [id,item] of old){
      if(!next.has(id))return "breaking";
      const normalize=(v:Obj)=>JSON.stringify(Object.fromEntries(Object.entries(v).filter(([k])=>!["name","description"].includes(k)).sort(([a],[b])=>a.localeCompare(b))));
      if(normalize(item)!==normalize(next.get(id)!))uncertain=true;
    }
  }
  return uncertain?"needs_review":"compatible";
}
export function extensionSupport(extensions:Obj,recognized:string[],critical:string[]):"not_supported"|"preserved_uninterpreted"|"supported"{
  const unknown=Object.keys(extensions).filter(x=>!recognized.includes(x));
  if(unknown.some(x=>critical.includes(x)))return "not_supported";
  return unknown.length?"preserved_uninterpreted":"supported";
}

export function effectiveProperties(elements:Obj[],relationships:Obj[],propertySets:Obj[],propertyDefinitions:Obj[]):Obj {
  const sets=new Map<string,string[]>(propertySets.map(x=>[x.id,x.properties]));
  const known=new Set<string>(propertyDefinitions.map(x=>x.id));
  const result:Obj={};
  for(const [label,types] of [["elements",elements],["relationships",relationships]] as const){
    const byId=new Map<string,Obj>(types.map(x=>[x.id,x]));
    const cache=new Map<string,Obj>(),visiting=new Set<string>();
    const resolve=(id:string):Obj=>{
      if(cache.has(id))return cache.get(id)!;
      ensure(!visiting.has(id),"Inheritance cycle");
      const item=byId.get(id);ensure(item,"Unknown inherited type");
      visiting.add(id);
      const union=new Set<string>(item.property_sets??[]);
      for(const parent of item.extends??[])for(const p of resolve(parent).property_sets)union.add(p);
      visiting.delete(id);
      const props=new Set<string>();
      for(const setId of union){
        const refs=sets.get(setId);ensure(refs,"Unknown property set");
        for(const ref of refs){ensure(known.has(ref),"Unknown property definition");props.add(ref);}
      }
      const value={property_sets:[...union].sort(),properties:[...props].sort()};
      cache.set(id,value);return value;
    };
    result[label]=Object.fromEntries([...byId.keys()].sort().map(id=>[id,resolve(id)]));
  }
  return result;
}

export function consume(bytes:Uint8Array):Obj {
  const files=readArchive(bytes);
  ensure(files["manifest.yaml"],"Missing manifest");
  const manifest=parseYaml(files["manifest.yaml"]);
  ensure(manifest.package_format==="mmp" && manifest.package_format_version==="1.0.0","Unsupported MMP format");
  ensure(Array.isArray(manifest.files)&&manifest.entrypoints&&manifest.metamodel,"Malformed manifest");
  const listed=new Set<string>();
  for(const entry of manifest.files){ensure(typeof entry.path==="string"&&validPath(entry.path)&&!listed.has(entry.path),"Invalid/duplicate manifest path");
    listed.add(entry.path);ensure(files[entry.path] && sha(files[entry.path])===entry.sha256,"Missing file or SHA mismatch: "+entry.path);
  }
  ensure(listed.size===Object.keys(files).length-1 && Object.keys(files).every(x=>x==="manifest.yaml"||listed.has(x)),"Undeclared ZIP file");
  const schemas=new Map<string,Obj>();
  for(const [name,raw] of Object.entries(files)){if(name.startsWith("schemas/")&&name.endsWith(".schema.json")){
    const schema=JSON.parse(decoder.decode(raw));ensure(typeof schema.$id==="string","Missing schema ID");
    schemas.set(schema.$id,schema);
  }}
  // Offline-only schema references. No fetch or network resolver.
  const ajv=new (Ajv as any)({strict:false,allErrors:true,validateFormats:true});
  (addFormats as any)(ajv);
  for(const schema of schemas.values())ajv.addSchema(schema);
  const docs:Obj={};
  for(const key of required){const path=manifest.entrypoints[key];ensure(typeof path==="string"&&validPath(path)&&files[path],"Missing entrypoint: "+key);
    const schemaPath="schemas/"+key+".schema.json";ensure(files[schemaPath],"Missing schema: "+key);
    const schema=JSON.parse(decoder.decode(files[schemaPath]));
    const value=parseYaml(files[path]);const validate=ajv.getSchema(schema.$id);
    ensure(validate && validate(value),"Invalid canonical "+key+": "+JSON.stringify(validate?.errors));
    docs[key]=value;
  }
  const meta=docs.metamodel.metamodel;
  ensure(meta.id===manifest.metamodel.id && meta.version===manifest.metamodel.version && meta.namespace===manifest.metamodel.namespace
    && docs.version.version.current===meta.version,"Metamodel identity mismatch");
  const elements=docs.metamodel.elements,relations=docs.metamodel.relationships,props=docs.properties;
  const elemIds=ids(elements,"elements"),relIds=ids(relations,"relationships");
  ensure([...elemIds].every(id=>!relIds.has(id)),"Element / relationship ID collision");
  graph(elements,elemIds);graph(relations,relIds);
  const sets=ids(props.property_sets,"property sets"),properties=ids(props.property_definitions,"property definitions");
  const dataTypes=ids(props.data_types,"data types"),enumerations=ids(props.enumerations,"enumerations");
  for(const item of [...elements,...relations])for(const ref of item.property_sets??[])ensure(sets.has(ref),"Unknown property set");
  for(const item of props.property_sets)for(const ref of item.properties)ensure(properties.has(ref),"Unknown property");
  for(const item of props.property_definitions){const type=item.type;
    if(type.data_type)ensure(dataTypes.has(type.data_type),"Unknown data type");
    if(type.enumeration)ensure(enumerations.has(type.enumeration),"Unknown enum");
  }
  for(const item of props.enumerations)ids(item.values,"enum values");
  for(const r of relations)for(const end of ["source","target"])for(const ref of r[end].types)ensure(elemIds.has(ref),"Unknown endpoint");
  return {effective_properties:effectiveProperties(elements,relations,props.property_sets,props.property_definitions),package_format_version:manifest.package_format_version,metamodel:manifest.metamodel,
    elements:elements.map((x:Obj)=>({id:x.id,name:x.name})),relationships:relations.map((x:Obj)=>({id:x.id,name:x.name})),
    property_count:props.property_definitions.length};
}
if(process.argv[1]?.endsWith("consumer.js")){
  try{console.log(JSON.stringify(consume(new Uint8Array(readFileSync(process.argv[2]))),null,2));}
  catch(e){console.error(String(e));process.exitCode=1;}
}
