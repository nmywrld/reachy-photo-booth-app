# Syncing `reachy_booth/` to Hugging Face

`reachy_booth/` is now a **plain folder** inside this parent repo (its own `.git` was
removed on 2026-11-10). The parent repo tracks the files, but it **cannot push to the
Hugging Face Space directly** — the Space still needs its own separate clone.

- Space: https://huggingface.co/spaces/nmywrld/reachy_booth
- Full backup of the old repo (including all history):
  `/home/dellaiih/drago/reachy_booth-backup.bundle`

## One-time setup: create the HF push clone

```bash
git clone https://huggingface.co/spaces/nmywrld/reachy_booth ~/drago/reachy_booth-hf
```

(If the Space is missing or out of date, restore from the backup instead and push it:

```bash
git clone /home/dellaiih/drago/reachy_booth-backup.bundle ~/drago/reachy_booth-hf
cd ~/drago/reachy_booth-hf
git push origin master:main   # HF Spaces serve from main
```
)

## Every time you make changes

### 1. Edit and commit in the parent repo (normal workflow)

```bash
cd ~/drago/reachy-photo-booth-app
# edit files under reachy_booth/ ...
git add reachy_booth/
git commit -m "describe the change"
```

This is your source of truth. The parent repo always has the latest code.

### 2. Copy the changes into the HF clone

```bash
rsync -av --exclude '.git' --exclude '__pycache__' \
    ~/drago/reachy-photo-booth-app/reachy_booth/ ~/drago/reachy_booth-hf/
```

Tips:
- Add `--delete` to the rsync **only if** you deleted files in the parent and want
  them removed from the Space too (it mirrors exactly).
- `-n` (dry-run) can be added first to preview what would be copied.

### 3. Commit and push from the HF clone

```bash
cd ~/drago/reachy_booth-hf
git add .
git commit -m "sync from parent repo"
git push
```

The Space rebuilds on every push to `main`.

## Quick reference

| Task | Where | Command |
|---|---|---|
| Daily work / commits | parent repo | edit `reachy_booth/`, `git commit` |
| Sync to Space | HF clone | rsync, then `git push` |
| Recover old history | anywhere | `git clone /home/dellaiih/drago/reachy_booth-backup.bundle` |
