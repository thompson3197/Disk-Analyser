---
title: 'ccdisk: A High-Performance, Deterministic Python 2.7 Disk Analyzer and Storage Management Utility'
tags:
  - Python
  - Systems Programming
  - Disk Space Analysis
  - Hard Link De-duplication
  - Squarified Treemaps
authors:
  - name: Dr. Travis Lee Thompson
    orcid: 0009-0001-7917-0306
    affiliation: 1
affiliations:
  - name: Independent Systems Researcher & Software Author
    index: 1
date: 10 November 2026
bibliography: paper.bib
---

# Summary

`ccdisk` is a deterministic, high-performance disk usage analyzer and storage management utility built specifically for systems engineers and administrators. Designed around strict memory-safety, non-recursive directory traversal, and inode-level hard link de-duplication, `ccdisk` provides accurate disk utilization metrics, apparent size comparisons, sparse file block calculations, and interactive squarified treemap visualizations. Furthermore, `ccdisk` incorporates automated detection of build artifacts and cache directories, staged cleanup sets with containment de-duplication, and safe migration to the operating system's recoverable Trash backed by rigorous path protection barriers.

# Statement of Need

Existing disk visualization tools often rely on recursive directory scanners that risk stack overflow exceptions on deep directory hierarchies, fail to correctly account for hard-linked inodes (leading to inflated storage metrics), or lack safety barriers when staging files for deletion. In resource-constrained or specialized environments (such as embedded diagnostics, offline legacy systems, and strict deterministic runtime environments), administrators require a lightweight, transparent utility that adheres to strict safety ground rules [@vesely2004python]:
- **Zero Recursion:** Fully iterative queue-based traversal preventing stack exhaustion.
- **Accurate Inode De-duplication:** Tracks file system device and inode keys to ensure hard links share storage costs correctly.
- **Deterministic Safety Barriers:** Hardcoded checks that prohibit tampering with critical system paths (e.g., `/`, `/usr`, `C:\Windows`) or traversing outside active scan roots.
- **Recoverable Cleanup:** Moves candidates to the OS Trash rather than executing destructive permanent removals.

# Core Architecture & Features

`ccdisk` is structured into twelve modular subsystems mirroring systems engineering best practices:
1. **Iterative Scanner (`Step 1`):** Non-recursive queue walker handling permission exceptions gracefully.
2. **Storage Metrics (`Step 2`):** Distinguishes apparent size from actual allocated disk blocks.
3. **De-duplication & Safety (`Step 3`):** Inode tracking and symlink loop protection.
4. **Squarified Treemaps (`Step 4`):** Aspect-ratio optimized 2D layout engine for hierarchical files [@johnson1991treemaps].
5. **Interactive Navigation (`Step 5`):** Breadcrumb state management and dynamic resizing.
6. **Inspector & Rankings (`Step 6-8`):** Deep metadata inspection, largest-children drill-downs, and size/age filtering.
7. **Reclaimable Detection (`Step 9-10`):** Automatic identification of build directories (`node_modules`, `target`, `__pycache__`) and user caches with staged cleanup savings prediction.
8. **Safety & Trash (`Step 11-12`):** Pre-execution review barriers and safe OS Trash migration.

# Mathematics of Squarified Treemaps

Following the squarified layout approach [@bruls2000squarified], given a set of rectangular areas proportional to file disk usage $s_i$, the aspect ratio $r$ for a row of items with width $w$ and total area $s$ is minimized by evaluating:

$$\max\left(\frac{w^2 \cdot \max(s_i)}{s^2}, \frac{s^2}{w^2 \cdot \min(s_i)}\right)$$

This prevents unreadable, elongated slivers when visualizing directories containing thousands of small files.
