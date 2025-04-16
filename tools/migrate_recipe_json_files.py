#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def cleanup_data(node) -> bool:
    """
    Recursively walk `node` (which may be a dict or list),
    normalize any dict in a "steps" or "substeps" list by
    moving all keys except "type", "config", "steps", "substeps"
    under the nested "config" dict.
    Returns True if any modification was made.
    """
    modified = False

    def recurse(n):
        nonlocal modified
        if isinstance(n, dict):
            for container in ("steps", "substeps"):
                if container in n and isinstance(n[container], list):
                    for step in n[container]:
                        if isinstance(step, dict) and "type" in step:
                            # collect keys to move into config
                            extras = [k for k in step if k not in ("type", "config", "steps", "substeps")]
                            if extras:
                                cfg = step.get("config")
                                if not isinstance(cfg, dict):
                                    cfg = {}
                                for k in extras:
                                    cfg[k] = step.pop(k)
                                step["config"] = cfg
                                modified = True
                        # recurse into nested steps/substeps
                        recurse(step)
        elif isinstance(n, list):
            for item in n:
                recurse(item)

    recurse(node)
    return modified


def cleanup_file(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return False

    if cleanup_data(data):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    return False


def main():
    p = argparse.ArgumentParser(description="Recursively normalize 'steps' and 'substeps' in JSON files.")
    p.add_argument("root_dir", help="directory to scan")
    args = p.parse_args()

    root = Path(args.root_dir)
    for fn in root.rglob("*.json"):
        try:
            if cleanup_file(fn):
                print(f"Updated {fn}")
        except Exception as e:
            print(f"[!] Error processing {fn}: {e}")


if __name__ == "__main__":
    main()
