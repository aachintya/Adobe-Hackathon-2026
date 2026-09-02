#!/usr/bin/env python3
"""Dependency-free Adobe marketplace and Agent Skills structure checks."""
import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def frontmatter(path):
    text=path.read_text(encoding="utf-8")
    match=re.match(r"^---\s*\n(.*?)\n---\s*\n",text,re.S)
    assert match,f"missing frontmatter: {path}"
    fields={}
    for line in match.group(1).splitlines():
        if ":" in line:
            key,value=line.split(":",1); fields[key.strip()]=value.strip()
    return fields,text

def main():
    manifest=json.loads((ROOT/"marketplace.json").read_text(encoding="utf-8")); skills=manifest.get("skills",[])
    assert manifest.get("version")=="1.4.0" and skills and sum(bool(item.get("entrypoint")) for item in skills)==1
    checked=[]
    for item in skills:
        folder=ROOT/item["path"]; document=folder/"SKILL.md"; assert folder.parent==ROOT/"skills" and document.is_file()
        fields,text=frontmatter(document); name=fields.get("name",""); description=fields.get("description","")
        assert name==folder.name and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",name) and len(name)<=64
        assert 0<len(description)<=1024 and fields.get("license") and fields.get("allowed-tools")
        assert len(text.splitlines())<500
        for reference in re.findall(r"\[[^]]+\]\(([^)]+)\)",text): assert (folder/reference).resolve().is_file(),f"broken reference {reference} in {document}"
        checked.append(name)
    print(json.dumps({"result":"PASS","marketplace_version":manifest["version"],"skills":checked,"entrypoints":1},indent=2))

if __name__=="__main__": main()
