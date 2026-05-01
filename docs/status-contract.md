<h1>Status contract (Age Decision API)</h1>

Stable operator-facing endpoints for lifecycle metadata and downstream readiness signals. Responses exclude inference outputs, biometric scores unrelated to aggregated decisions successful path, undocumented upstream dumps, timings as diagnostics, and stack traces.

<hr>

<h2>GET /health</h2>

Contract keys (privacy-first assertions block extra fields such as biometric scores mirrored from downstream):

<ul>
  <li><strong>status</strong> — process liveness,</li>
  <li><strong>service</strong> — gateway service slug,</li>
  <li><strong>version</strong> — deployment semver,</li>
  <li><strong>contract_version</strong> — public contract line echoed from metadata.</li>
</ul>

<hr>

<h2>GET /ready</h2>

Keys include aggregates plus downstream stubs:

<ul>
  <li><strong>status</strong> — <code>ready</code> only when modeled downstream checks report readiness; otherwise <code>degraded</code>,</li>
  <li><strong>service</strong>, <strong>version</strong>, <strong>contract_version</strong> — mirrored from project metadata,</li>
  <li><strong>core</strong> — object with at least <strong>status</strong> and <strong>url</strong> for coordinating core reachability,</li>
  <li><strong>antispoof</strong> — same shape for AntiSpoof.</li>
</ul>

<hr>

<h2>GET /version</h2>

Returns <code>project.json</code> metadata fields surfaced through <code>ProjectMetadata</code>, including:

<ul>
  <li><strong>service_name</strong>, <strong>app_name</strong>, <strong>version</strong>, <strong>contract_version</strong>,</li>
  <li><strong>repository</strong>, <strong>image</strong>.</li>
</ul>

<hr>

<h2><code>contract_version</code> behavior</h2>

The string matches the gateway’s advertised semantic contract lane; consumers correlate it against published compatibility matrices instead of probing undocumented fields across environments.
