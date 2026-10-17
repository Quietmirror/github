# L2 continuation status

The user explicitly adopted the new master specification on 2026-10-17.
Baseline: Quietmirror/github R3.2 commit f1b1090931d717117287ea2b79c2e14ddc234937.
Work branch: codex/l2-balanced. Historical revision folders are immutable inputs.

- Gate 0 done: branch now based on correct R3.2 commit, working files and historical branches retained. Only new L2 folders should be staged; old CRLF/V0.9 differences are pre-existing.
- Gate 1 arithmetic/CAD audit done: 18.6917428605 g PA12 baseline; target requires 3764.101842 mm3 net removal. Reference audit records missing supplier/old-proxy inputs explicitly.
- Actual R3.2 C3D10 BODY runs complete at h2.4, 2.0, 1.8 for 5 N upper-back and 2 N + 2 N self-equilibrated outer-skin grips. The corrected grip case removes only rigid modes, without holding feet to a desk. Last-grid stiffness change: back 3.76%, grip 0.36%. The old held-foot fixture remains in a separate first-review report. h1.3 CalculiX access-violation twice; failed logs retained.
- P1_R13: full CAD equal-area six-hole rounding, nine valid closed non-self-intersecting meshes, 72-part static and five sampled motions passed. The inherited rear-key straight insertion still fails. Actual coarse 3D fixture comparison is available; not a new production release.
- F1/F2: caps and internal D2F switches/guides/pins moved together to Y49/62 Z17.5, cap length 10.4, gap 2.6. F1 height3.6/offset.18; F2 height4.0/offset.30 and 3-degree YZ outline slope. Both initial BODY exports have 4 intersecting faces/non-manifold mesh at rear-hole upper edge X15.5..17.4 Y67.3..67.8 Z27.8..28.3. Not printable releases. Finer CAD tessellation .015/.01/.005 and split-fuse Y67.5 failed; all failures retained, no mesh repair used.
- F1S and isolated F1_P0/F2_P0 also had the same OCC tessellation defect. Independent Gmsh surface meshing of F1_P0 solved it: 1 closed connected component, 0 self-intersections, 0.0201% CAD volume difference, 500 boundary samples maximum 0.00534 mm. No holes filled or pieces discarded.
- F1_P0 full static check then found 4 genuine clamp/bolt-to-cross-tie collisions. Both direct side-key insertion paths passed. Coarse back stiffness dropped from 97.49 to 43.86 N/mm. Rejected. F1B moves the complete aligned mechanism from Z17.5 down to Z15.5 to restore the upper load band and cross-tie clearance; checks pending.
- K16/K14/K12: paired PA12 savings .21139/.31794/.42491 g. Three-level C3D10 analysis at h1.2/.9/.65 completed, four 1.5 N press positions each. All stiffnesses fall below R3.2, so rejected by comparative stiffness gate. Independent stress/energy integration passes after correcting integration-point ordering. K14R adds two deeper longitudinal ribs; new actual geometry and FEA are in progress.
- New structured-grid 2D proxy is diagnostic only. A separate conforming Gmsh/CST proxy completed three levels (.75/.5/.35 mm); final stiffness changes <1%. Its boundary conditions differ from the incomplete old study, which remains unreproducible. No 2D result is claimed as mouse 3D stiffness.
- Strict BRep functional partition completed for R3.2: A6532.023, B1875.718, C_BODY4393.981 mm3. BODY closure error -0.0062 mm3; classification gives footprint-land material not covered by old brace masks to C installation regions. Detailed ledger and colored STEP partitions are saved.
- P2 full CAD generated. P1_R10/P1_R15/P3-P6 and B1-B4 single-variable CAD study is running. These are research candidates, not accepted releases.
- Pending: full P2-P6 / B1-B4 exploration, mount mass partition/optimisation, side-key repair and full installation checks, structural comparison and independent second review.
- Pending: common-shell freeze, H/D adapters, native assemblies and actual separated-parts slicing.
- Hardware status: A1 Pro identity and all real PCB dimensions remain unverified.
- Default controls: no added external DPI button or separate external power slider; retain charging/protection and the selected electronics' required power control.
- Inherited functional targets: 400-6400 DPI, five buttons/wheel, wireless 1 kHz, macros, adjustable LOD, no optional sync, at least 12 h full-power continuous use. These require real PCB/firmware/receiver/battery evidence.
- The 14.89 g target assumes PA12 density 1.01 g/cm3, not PLA sliced mass.

No strength, fit, fatigue, electrical-function or mass-target completion is implied by this file.
