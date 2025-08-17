from pathlib import Path
import os, shutil

def ensure_dir(p: Path): p.parent.mkdir(parents=True, exist_ok=True)

def apply_action(src: Path, dst: Path, action='move', dry_run=True):
    ensure_dir(dst)
    if dry_run: return
    if action=='move': shutil.move(str(src), str(dst))
    elif action=='copy': shutil.copy2(src, dst)
    elif action=='hardlink': os.link(src, dst)
    elif action=='symlink':
        if dst.exists(): dst.unlink()
        dst.symlink_to(src)
    else: raise ValueError(action)
