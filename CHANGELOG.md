## [0.3.6] - 2025-01-23
### Added
- Introduced **local caching** in various modules to reduce redundant computations and improve performance. 
  - Caching has been applied where repeated lookups occur, particularly in fertilisation-related calculations.
  - *Contributed by: Colm Duffy*

### Changed
- Performed **source code optimizations** in the fertilisation modules and other areas where caching provided significant value.
- Updated logic to ensure correct reference years are used in calculations, enhancing result accuracy and consistency.
    - *Contributed by: Colm Duffy*

### Fixed
- Resolved a **bug** where the default calibration year was always being applied, even when not required.
  - This fix may cause slight differences in outputs such as spared area calculations.

### Testing
- Conducted basic **compatibility tests** to verify the stability and correctness of changes.
    - *Contributed by: Colm Duffy*

---