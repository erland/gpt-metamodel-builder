#!/usr/bin/env python3
import hashlib,json,sys,tempfile,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import consume,strict_core_candidate
with zipfile.ZipFile(sys.argv[1]) as z:
  suite=json.loads(z.read("conformance/package-semantic-manifest.json"))
  with tempfile.TemporaryDirectory() as td:
    for case in suite["cases"]:
      data=z.read(case["package"])
      assert hashlib.sha256(data).hexdigest()==case["sha256"]
      path=Path(td)/(case["id"]+".zip");path.write_bytes(data)
      try: consume(path); legacy="accept"
      except ValueError: legacy="reject"
      assert legacy==case["expected"],case["id"]
      try: strict=strict_core_candidate(path)["status"]
      except ValueError: strict="reject"
      assert strict==case["strict_expected"],(case["id"],strict)
      print("PASS",case["id"],legacy,strict)
print("PASS opt-in strict Core package profile")
