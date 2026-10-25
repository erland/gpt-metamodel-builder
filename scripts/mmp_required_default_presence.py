"""Opt-in candidate rule: defaults never satisfy instance presence constraints."""
from __future__ import annotations

def decide(case):
    cardinality=case.get("cardinality")
    try:
        if cardinality is None or cardinality=="*":
            lo,hi=0,None
        elif ".." in cardinality:
            left,right=cardinality.split("..",1)
            lo=int(left);hi=None if right=="*" else int(right)
        else:lo=hi=int(cardinality)
        if lo<0 or (hi is not None and (hi<0 or lo>hi)):
            return "invalid_contract"
    except (ValueError,TypeError,AttributeError):
        return "invalid_contract"
    required=case["required"]
    effective=max(lo,1 if required else 0)
    if hi is not None and effective>hi:return "invalid_contract"
    if not case["present"]:
        if effective>0:return "missing_required" if required else "insufficient_values"
        return "optional_default_available" if case["default_defined"] else "optional_absent"
    value=case.get("value")
    if value is None:return "invalid_null"
    count=len(value) if isinstance(value,list) else 1
    if count<effective:return "insufficient_values"
    if hi is not None and count>hi:return "too_many_values"
    return "satisfied"
