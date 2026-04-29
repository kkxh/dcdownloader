# DCDownloader Continuation Roadmap

This repository is a continuation of `dev-techmoe/python-dcdownloader`, which was archived by its owner on 2022-11-09. The original project is MIT licensed, so continuation is allowed as long as the license and copyright notice are preserved.

## Project Positioning

DCDownloader is being repositioned as a pluggable image-site crawler framework. The continuation should prioritize maintainability, testability, respectful crawling behavior, and fast Parser adaptation for user-specified sites before adding broad built-in site support.

## Phase 0: Project Takeover

- Preserve upstream git history.
- Keep the original `LICENSE` file and author attribution.
- Rename the original remote to `upstream`.
- Add a new `origin` only after the replacement GitHub repository exists.
- Document the continuation status in `README.md`.

## Phase 1: Reproducible Development

- Add a modern `pyproject.toml` while keeping `setup.py` compatibility until packaging is verified.
- Separate runtime dependencies from development tools.
- Replace the old Travis configuration with GitHub Actions.
- Establish supported Python versions, likely Python 3.10+ or 3.11+.
- Make the existing tests runnable without depending on import-time network/session side effects.

## Phase 2: Async Compatibility Fixes

- Replace deprecated `aiohttp.ClientSession(read_timeout=...)` usage.
- Remove `with (await self.sema)` patterns and use `async with self.sema`.
- Avoid constructing `ClientSession` at import or object construction time without a running event loop.
- Ensure sessions are always closed, including early-return and error paths.
- Add focused tests for fetch-only mode, retry behavior, and output path generation.

## Phase 3: Parser Health

- Treat `SimpleParser` as the stable contract test parser.
- Keep built-in Parser examples minimal and site-neutral where possible.
- Recheck legacy site-specific parsers against current site behavior before claiming support.
- Mark broken or unverified parsers clearly rather than silently failing.
- Document the expected Parser adaptation workflow for extracting images and organizing them into collections. (Started in `docs/parser-adapter-guide.md`.)

## Phase 4: Release

- Choose a maintained distribution name before publishing to PyPI.
- Use semantic versioning for the continuation line.
- Add changelog entries that distinguish upstream history from continuation releases.
- Publish a first release only after tests and at least one real parser path are verified.

## Immediate Risks

- Pinned dependencies are from 2018 and may not install cleanly on current Python.
- The async code uses APIs and idioms that changed in modern `aiohttp`.
- Parser behavior likely drifted because target sites have changed over years.
- The CLI reports inconsistent versions (`setup.py`, `arg_parse.py`, and `version.py` disagree).
