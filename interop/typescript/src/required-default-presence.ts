/** Opt-in candidate: defaults do not satisfy explicit instance presence. */
export function decideRequiredDefault(c: {
 required:boolean; cardinality:string|null; present:boolean;
 default_defined:boolean; value?:unknown;
}):string {
 const raw=c.cardinality;
 let lo=0,hi:number|null=null;
 if(raw!==null && raw!=="*"){
  const parts=raw.split("..");
  if(parts.length>2)return "invalid_contract";
  if(parts.length===1){if(!/^[0-9]+$/.test(raw))return "invalid_contract";lo=hi=Number(raw);}
  else {if(!/^[0-9]+$/.test(parts[0]) || !(parts[1]==="*" || /^[0-9]+$/.test(parts[1])))return "invalid_contract";
   lo=Number(parts[0]); hi=parts[1]==="*"?null:Number(parts[1]);}
 }
 if(!Number.isSafeInteger(lo)||(hi!==null&&(!Number.isSafeInteger(hi)||lo>hi)))return "invalid_contract";
 const min=Math.max(lo,c.required?1:0);
 if(hi!==null&&min>hi)return "invalid_contract";
 if(!c.present){
  if(min>0)return c.required?"missing_required":"insufficient_values";
  return c.default_defined?"optional_default_available":"optional_absent";
 }
 if(c.value===null||c.value===undefined)return "invalid_null";
 const count=Array.isArray(c.value)?c.value.length:1;
 if(count<min)return "insufficient_values";
 if(hi!==null&&count>hi)return "too_many_values";
 return "satisfied";
}
