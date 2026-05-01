<h1>Deprecation policy (public gateway contract)</h1>

This document applies to the Age Decision API HTTP surface: documented routes, stable JSON responses, and schemas published for this repository. It omits roadmap-level release planning tracked in the central project.

<hr>

<h2>Semantic versioning</h2>

Breaking changes to documented URLs, documented request payloads, or stable response field sets follow semver aligned with gateway <code>version</code> and <code>contract_version</code> metadata.

<hr>

<h2>Deprecated behaviors before removal</h2>

If a documented public route, payload field, or response field will be removed, it remains referenced in changelog and repository docs—with replacement guidance—until removal ships alongside compatibility metadata updates.

<hr>

<h2>Majors, minors, internals</h2>

Removing or renaming advertised public JSON contracts typically requires coordinated **minor** bumps when backward compatible, or ecosystem **major** alignment when callers must change. Purely operational or internal orchestration helpers that never appeared in documented contracts may evolve under tighter versioning only when undocumented.

<hr>

<h2>Privacy leaks</h2>

Leakage pathways—estimated age payloads, granular confidence blobs, undocumented score fields mirrored from downstream internals, verbatim upstream traces, raw stack content in HTTP bodies—must be corrected urgently; they are **not** carried through deprecation windows.
