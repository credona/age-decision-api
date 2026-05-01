<h1>Error model (Age Decision API gateway)</h1>

This repository normalizes failures for its public orchestration endpoints. Detailed downstream semantics remain owned by core and anti-spoof; the gateway emits a constrained envelope documented here.

<hr>

<h2>ErrorResponse shape</h2>

```json
{
  "request_id": "...",
  "correlation_id": "...",
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

Headers <strong>X-Request-ID</strong> and <strong>X-Correlation-ID</strong>, when omitted, synthesize identifiers (correlation mirrors request unless provided).

<hr>

<h2>HTTP semantics</h2>

<ul>
  <li><strong>POST /verify</strong> advertises <strong>400</strong> and <strong>502</strong> standardized failures using the envelope above.</li>
</ul>

Other endpoints may rely on FastAPI defaults when validation failures fall outside normalized <code>/verify</code> body checks (see normalization rules below)—those payloads are intentionally not asserted by the same standardized contract suite.

<hr>

<h2>Known gateway error codes</h2>

Emitted by this gateway for paths covered above:

<ul>
  <li><strong>missing_image_base64</strong> — JSON body validates but <code>image_base64</code> absent.</li>
  <li><strong>invalid_request</strong> — other field-level rejection on <code>/verify</code> under normalized validation paths.</li>
  <li><strong>invalid_base64_image</strong> — decoding or payload validation surfaced as rejection before downstream calls.</li>
  <li><strong>downstream_service_error</strong> — aggregated upstream orchestration failures; HTTP <strong>502</strong> with canonical external wording (<code>An upstream service error has occurred.</code>) without attaching raw downstream bodies.</li>
</ul>

<hr>

<h2>Normalization scope</h2>

Structured normalization applies when the inbound request targets <strong><code>/verify</code></strong>, the payload decodes as JSON, and validation errors originate from modeled body fields (<code>VerifyRequest</code>). Other validation surfaces keep framework defaults.

<hr>

<h2>Forbidden fields</h2>

Normalized error payloads expose only <strong>request_id</strong>, <strong>correlation_id</strong>, nested <strong>error.code</strong>, and <strong>error.message</strong>. Forbidden additions include traceback strings, downstream raw JSON embedded as helper fields, array-style validation dumps mirroring internals, biometric scores, heuristic dumps, granular threshold metadata, inferred ages, undisclosed spoof metrics, or environment diagnostics.
