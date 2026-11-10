# ccdisk

`ccdisk` is a high-performance, deterministic disk analyzer and storage management utility written in Python 2.7. It provides precise disk allocation metrics, inode de-duplication, squarified treemap layouts, reclaimable build/cache detection, and safe, recoverable cleanup workflows.

## Features

- **Non-Recursive Traversal:** Iterative queue-based scanner designed to prevent stack overflow on deep directory structures.
- **Hard Link De-duplication:** Tracks underlying file inodes so that files sharing physical storage blocks are counted exactly once.
- **Sparse File Support:** Distinguishes apparent file size from actual allocated disk blocks.
- **Squarified Treemaps:** Organizes file sizes into aspect-ratio optimized visual layouts.
- **Reclaimable Intelligence:** Automatically identifies common build artifacts (`node_modules`, `target`, `__pycache__`) and cache folders (`.cache`).
- **Safe Cleanup:** Staged cleanup sets with duplicate protection, pre-execution safety review screens, protected system path barriers (`/usr`, `C:\Windows`), and OS Trash migration.

## Quick Start

Run the master application runner to execute the complete verification pipeline and generate execution telemetry:

```bash
python ccdisk_main.py
