# Contributing

Issues and focused pull requests are welcome. Before submitting a change:

1. Run `make build`.
2. Run `make test`.
3. If outlines, metrics, or rendering changed, run `make posters` and update the
   Playwright snapshots intentionally with `make test-update`.

Do not replace or remove upstream attribution or the SIL OFL license. Design
changes should include a specimen showing the affected glyphs at display and
small UI sizes.
