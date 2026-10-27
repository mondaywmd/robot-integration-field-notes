"""Read a local file and compare SHA-256. Never connects to or flashes a device."""
import argparse
import hashlib
import json
import re
from pathlib import Path

def check(path, expected):
    if not re.fullmatch(r"[a-fA-F0-9]{64}", expected):
        raise ValueError("Expected SHA-256 must have 64 hexadecimal characters")
    path=Path(path);digest=hashlib.sha256(path.read_bytes()).hexdigest()
    return {"file":path.name,"bytes":path.stat().st_size,"sha256":digest,"matches":digest==expected.lower(),"scope":"File integrity only; not board compatibility, firmware safety, or flash readback"}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("file");p.add_argument("--sha256",required=True);a=p.parse_args();r=check(a.file,a.sha256);print(json.dumps(r,indent=2));raise SystemExit(0 if r["matches"] else 1)
