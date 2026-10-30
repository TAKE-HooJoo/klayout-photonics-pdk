#!/usr/bin/env python3
"""Idempotently add AUTO_QUALITY GUI tool to existing v6.5 macro builder.

Never edits the installed v6.4 macro. Backups the generator before changes.
"""
from pathlib import Path
import argparse
import ast
import shutil

OLD = "# Three independent toolbar tools provide explicit, persistent mode selection."
NEW = "# Four independent toolbar tools provide explicit, persistent mode selection."
FACTORY = "    HybridRouterFactory('EULER', 'photonics_router_v6_5_euler', -1013),"
ADDED = "    HybridRouterFactory('AUTO_QUALITY', 'photonics_router_v6_5_auto_quality', -1014),"


def patch(path):
    original = path.read_text(encoding='utf-8')
    if ADDED in original:
        print('Already patched:', path)
        return False
    if original.count(OLD) != 1 or original.count(FACTORY) != 1:
        raise RuntimeError('Expected v6.5 GUI markers not found exactly once; no changes made')
    updated = original.replace(OLD, NEW, 1).replace(FACTORY, FACTORY + '\n' + ADDED, 1)
    # Ensure the builder is still syntactically valid.
    ast.parse(updated, filename=str(path))
    backup = path.with_suffix(path.suffix + '.before_quality.bak')
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_text(updated, encoding='utf-8')
    print('Patched:', path)
    print('Backup:', backup)
    return True


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--builder', default='tools/build_router_v65_gui.py')
    args = ap.parse_args()
    patch(Path(args.builder))
