# Quality assurance

Zutat Sans 0.6 has no FontBakery failures, fatals, or errors.

| Format | PASS | WARN | SKIP | INFO |
| --- | ---: | ---: | ---: | ---: |
| TTF | 294 | 24 | 142 | 12 |
| OTF | 266 | 16 | 178 | 12 |

The remaining warnings are documented upstream/design-review items rather than
release blockers. Combining marks retain zero advance width in every style and
are protected by the production regression suite.
