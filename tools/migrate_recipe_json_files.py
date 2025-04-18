#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

JSON_BLOCK = re.compile(r"```json\s+(?P<body>.*?)\s+```", flags=re.DOTALL | re.IGNORECASE)


def transform_and_flatten(node: dict) -> bool:
    """
    - generate→llm_generate
    - rename artifact based on type:
        read_files    → contents_key
        generate*     → output_key
        write_files   → files_key
    - move ALL other keys (except 'type' & existing 'config') into node['config']
    """
    changed = False
    t = node.get("type")

    # 1) type=="generate" → "llm_generate"
    if t == "generate":
        node["type"] = "llm_generate"
        t = "llm_generate"
        changed = True

    # 2) rename the singular "artifact" based on type
    if t == "read_files" and "artifact" in node:
        node["contents_key"] = node.pop("artifact")
        changed = True
    if t in ("generate", "llm_generate") and "artifact" in node:
        node["output_key"] = node.pop("artifact")
        changed = True
    if t == "write_files" and "artifact" in node:
        node["files_key"] = node.pop("artifact")
        changed = True

    # 3) move every other key into config
    extras = [k for k in node if k not in ("type", "config")]
    if extras:
        if not isinstance(node.get("config"), dict):
            node["config"] = {}
        cfg = node["config"]
        for k in extras:
            cfg[k] = node.pop(k)
        node["config"] = cfg
        changed = True

    return changed


def normalize(obj) -> bool:
    modified = False

    def walk(x, parent_key=None):
        nonlocal modified
        # skip entire subtree under "output_format"
        if parent_key == "output_format":
            return
        if isinstance(x, dict):
            if "type" in x:
                if transform_and_flatten(x):
                    modified = True
            for k, v in x.items():
                walk(v, parent_key=k)
        elif isinstance(x, list):
            for item in x:
                walk(item, parent_key=None)

    walk(obj)
    return modified


def process_json_file(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    if normalize(data):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    return False


def process_md_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")

    def repl(m):
        body = m.group("body")
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return m.group(0)
        if normalize(data):
            return f"```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```"
        return m.group(0)

    new = JSON_BLOCK.sub(repl, text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    p = argparse.ArgumentParser(
        description="Normalize JSON in .json and ```json``` blocks in .md, skipping under 'output_format'."
    )
    p.add_argument("rootdir", help="directory to scan")
    args = p.parse_args()
    root = Path(args.rootdir)

    for pattern, handler in (("*.json", process_json_file), ("*.md", process_md_file)):
        for fn in root.rglob(pattern):
            try:
                if handler(fn):
                    print(f"Updated {fn}")
            except Exception as e:
                print(f"[!] Error in {fn}: {e}")


if __name__ == "__main__":
    main()
