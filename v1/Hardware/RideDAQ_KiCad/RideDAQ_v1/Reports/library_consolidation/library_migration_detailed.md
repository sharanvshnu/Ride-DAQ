# RideDAQ V1 library consolidation

## Result

Staging migration completed. KiCad CLI version 10.0.1 loaded and exported the board and hierarchical schematic. Validation: **PASS (8/8 merged-project checks)**.

## Migrated dependencies

- 75 PCB footprint instances; 27 active footprint IDs now resolve from project-local `.pretty` libraries.
- Both embedded logo graphics retained as separate library definitions and board objects.
- All 22 referenced 3D models resolve project-locally: 20 copied into `Libraries/3dmodels`, and 2 existing local models reused in `Libraries/3dmodel`; no duplicate model copies are needed in the merged project.
- 29 placed schematic symbol IDs across 16 local symbol namespaces; standard libraries copied and custom definitions extracted from hierarchical sheet embedded libraries.
- `sym-lib-table` and `fp-lib-table` added.

## Structural validation

- Footprint UUIDs, references, coordinates and layers match the pre-migration snapshot.
- PCB text comparison permits only the footprint library identifiers for the two logos and the 22 model path substitutions; model offsets, rotations and scales are unchanged.
- Root and child schematic files match the pre-migration backup byte-for-byte.
- KiCad CLI board SVG, schematic netlist and three custom symbol SVG exports succeeded.
- Rollback source: `Backups/pre-library-consolidation`.

See `validation_report.json`, `migration_report.json`, `post_migration/` (inventory), and `cli/` (all final KiCad exports) for machine-readable details.

