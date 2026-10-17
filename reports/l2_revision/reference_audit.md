# L2 references and evidence boundaries

Checked on 2026-10-17. The current user adopted the new master specification; A1 Pro is now the requested donor identity, but its commercial identity and PCB remain unverified. No A1 Plus geometry has been relabelled as an A1 Pro board.

## Actual source reads

- [badjeff/paw3395-pcb](https://github.com/badjeff/paw3395-pcb): read README and downloaded/read `paw3395.kicad_pcb` from the main branch. The published board thickness is 1.6 mm and nominal outline 15.5 × 28 mm. Actual top-level Edge.Cuts in that file bound X138.875–154.325 / Y76.15–104.15 mm, i.e. 15.45 × 28 mm with rounded corners. The footprint also contains internal Edge.Cuts; its external PMW3360 STEP reference is not a verified PAW3950/lens solid. This is a sensor breakout board, not a complete wireless mouse controller. The old 18 × 18 × 1.2 placeholder is not this board.
- Its author documents a PAW3950 option and lens choices, but that does not verify the proposed wireless controller, receiver, macros, LOD, no-sync operation, power consumption or 12-hour runtime. Upstream hardware license: CERN-OHL-P-2.0; existing license/attribution retained under `references/licenses/`.
- [G-Wolves Fenrir Pro official page](https://shop.g-wolves.com/products/g-wolves-fenrir-pro-8k-wireless-mouse) and retained [reference notes](../../references/FENRIR_REFERENCE.md): visual/proportion reference only. New F1/F2 geometry is built from Quietmirror's existing mother surface and independent mechanisms. No commercial CAD or manufacturer hole locations are available or copied. No numerical shape-similarity claim is made.
- [ATK official collection](https://www.atk.store/collections/mice): the retrieved listing does not establish an A1 Pro model or board. An absent listing is not proof the product does not exist. Keep `DONOR_ID_UNVERIFIED`, `PCB_GEOMETRY_UNVERIFIED`, `FIT_NOT_CERTIFIED` until the exact physical donor is identified.
- [Puppy v3Air video](https://www.bilibili.com/video/BV1BJd1BaExM/), [Puppy V4 video](https://www.bilibili.com/video/BV1Nhj96zE24), and [Puppy v3 model](https://makerworld.com.cn/zh/models/2312877): retrieval failed or returned HTTP 412 in this run. The master specification's 18 g title is not independently established as battery-inclusive measured mass. No geometry from those pages was used. No inference that v3/v3Air/V4 are interchangeable.
- [Omron D2LS datasheet](https://components.omron.com/us-en/datasheet_pdf/B122-E1.pdf): confirms a compact 8.6 × 4.8 × 3.0 mm switch family. Considered as an optional future socket-reduction route only; current F1/F2 still use the explicit D2F reference, not an invented drop-in D2LS socket.
- [CalculiX project](https://www.calculix.de/): actual local executable identifies version 2.22. Local Gmsh is 4.15.2. Real solver logs/decks are in the D-drive support tree; analytical beam examples and the new CST proxy are distinguished from solid C3D10 analysis.
- [EOS material data](https://www.eos.info/polymer-solutions/data-sheets/all-processes-and-materials?id=pa-2200): PA12 data is process/product dependent. The task's density 1.01 g/cm³, E1700 MPa and ν0.37 are explicitly retained analysis assumptions, not measured properties of the eventual PLA print or one universally defined PA12 material.

## Numerical corrections

The source hole profiles already have R0.85 mm fillets. The task's 1301.27 mm² projection matches the *sharp* polygons; the rounded 2D contours total approximately 1292.284 mm² before contact-band masks. P1 therefore preserves the actual rounded projection and reports exact CAD area separately. Same projection area does not imply exactly equal curved-shell volume.

The historical 2D study lacks exact supports, panel position, load distribution and mesh/rounding implementation. Its stiffness and stress figures cannot be uniquely reproduced. `new_2d_proxy.json` is a new explicitly defined reconstruction, not verification of those old figures; discretisation sensitivity must be checked before drawing conclusions. Real body 3D cases are recorded separately.

No sources here establish actual optical working distance, physical printing tolerance, fatigue life or electrical operation. These remain distinct from geometric clearance and linear static fixture screening.
