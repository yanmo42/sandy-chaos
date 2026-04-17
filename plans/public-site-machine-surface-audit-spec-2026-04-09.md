# Sandy Chaos public-site machine-surface audit/spec (2026-04-09)

## Status
Drafted from direct repo inspection of `/home/ian/projects/sandy-chaos`.

## Current audit snapshot

### Confirmed present
- `robots.txt` now exists at repo root (minimal baseline added today)
- `llms.txt` now exists at repo root (minimal baseline added today)
- Canonical docs are clearly present under `docs/`
- Internal embedding-aware retrieval code exists in repo:
  - `nfem_suite/intelligence/ygg/topological_memory.py`
  - related tests/docs/plans for optional embedding baselines

### Confirmed missing
- no `sitemap.xml`
- no `llms-full.txt`
- no detectable public-site structured metadata source in this repo:
  - no obvious Open Graph tags
  - no obvious Twitter card tags
  - no obvious JSON-LD / `schema.org`
- no obvious static-site framework/deploy config found in this repo root:
  - no `package.json`
  - no `astro.config.*`
  - no `next.config.*`
  - no `mkdocs.yml`
  - no obvious VitePress/Docusaurus/Hugo/Jekyll config

### Important uncertainty
This repo contains the content and docs, but **does not clearly expose the actual public-site build/deploy surface**.
Therefore, some specs below are implementation-ready in concept but not yet wired to a detected renderer/deployer.

---

## 1. `robots.txt` audit/spec

### Current state
Current repo-root `robots.txt` is intentionally minimal:

```txt
User-agent: *
Allow: /

# Add a confirmed absolute Sitemap URL once the live site domain/path is pinned down.
```

### Risk
- crawlers have no sitemap hint
- no explicit disallow rules for private or low-value surfaces
- no distinction between public doctrine and local/internal artifacts

### Spec
Target `robots.txt` should:
1. allow canonical public docs
2. disallow clearly non-public/internal/build/admin surfaces if they are ever exposed
3. advertise absolute sitemap URL
4. remain conservative, simple, and legible

### Proposed target shape
```txt
User-agent: *
Allow: /

# Keep non-public/internal surfaces out of crawl paths if exposed by deploy.
Disallow: /memory/
Disallow: /plans/
Disallow: /state/
Disallow: /.git/
Disallow: /venv/
Disallow: /node_modules/
Disallow: /.openclaw/

Sitemap: https://<confirmed-domain>/sitemap.xml
```

### Notes
- Only disallow paths that are actually reachable on the public deploy.
- If docs are served under `/docs/`, keep that explicitly crawlable.
- Do **not** use `robots.txt` as a security boundary.

### Immediate action
- Confirm live domain and deploy path.
- Replace placeholder comment with real sitemap URL.
- Add disallow rules only for surfaces that could actually leak publicly.

---

## 2. `llms.txt` / `llms-full.txt` audit/spec

### Current state
- `llms.txt` now exists, minimal but usable
- `llms-full.txt` missing

### Purpose
These files should act as the machine-readable front door for model/crawler/agent access to the site corpus.

### `llms.txt` spec (short front door)
Should include:
- one-sentence project identity
- preferred canonical docs
- project claim-discipline rules
- preference ordering: canonical docs over archive drafts
- optionally a link to `llms-full.txt`

### `llms-full.txt` spec (expanded machine map)
Should include:
1. project identity
2. canonical reading order
3. glossary / ontology anchors
4. claim-tier rules
5. archive policy
6. implementation surfaces
7. non-goals / caution zones
8. preferred citation style for machine summarizers

### Proposed `llms-full.txt` outline
```txt
# Sandy Chaos

## Identity
Short description of the project and its scope.

## Canonical reading path
1. /docs/README.md
2. /docs/00_sandy_chaos_blueprint.md
3. /docs/01_foundations.md
4. /docs/02_tempo_tracer_protocol.md
5. /docs/13_nested_temporal_domains.md
6. /docs/14_cognitive_tempo_orchestration.md
7. /docs/19_surface_authority_architecture.md

## Claim discipline
- Defensible now
- Plausible but unproven
- Speculative

Do not collapse these categories.

## Interpretation rules
- Prefer canonical docs over `docs/archive/`
- Preserve causal-boundary discipline
- Do not upgrade metaphor into mechanism
- Distinguish research notes from validated implementation artifacts

## Important supporting surfaces
- /docs/glossary.md
- /docs/assumptions_register.md
- /docs/theory-implementation-matrix.md
- /spine/README.md

## Implementation/evidence surfaces
- /nfem_suite/
- /scripts/
- /tests/
- /schemas/

## Citation preference
Cite exact doc paths when summarizing claims.
```

### Immediate action
- Author `llms-full.txt`
- Add a pointer from `llms.txt` to `llms-full.txt`
- Ensure only public-safe surfaces are referenced

---

## 3. Sitemap / canonical / structured-data audit/spec

### Current state
Missing or not detectable in this repo:
- `sitemap.xml`
- canonical URL declarations
- Open Graph tags
- Twitter card tags
- JSON-LD structured data

### Risk
- weak crawler/site comprehension
- poor canonicalization
- weak previews/shares
- low machine-legibility for page type, authorship, hierarchy, and update time

### Target spec

#### 3a. Sitemap
Minimum requirements:
- absolute URLs only
- include homepage + core docs + key indexes
- exclude drafts/private/internal surfaces
- include `lastmod`

Minimum pages to include:
- homepage
- start/docs index
- canonical docs
- glossary
- assumptions register
- theory-implementation matrix

If site has a real “Start Here” page, include it near top priority.

#### 3b. Canonical URLs
Each public page should emit:
```html
<link rel="canonical" href="https://<confirmed-domain>/<path>" />
```

#### 3c. Open Graph / Twitter
Each page should emit at minimum:
- `og:title`
- `og:description`
- `og:type`
- `og:url`
- `og:image` (shared fallback OK)
- `twitter:card=summary_large_image`

#### 3d. JSON-LD structured data
At minimum:
- homepage: `WebSite`
- docs/article pages: `TechArticle` or `Article`
- optionally breadcrumbs: `BreadcrumbList`

Homepage example:
```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Sandy Chaos",
  "url": "https://<confirmed-domain>/",
  "description": "Research and implementation work on Tempo Tracer, nested temporal domains, observer coupling, and continuity architecture."
}
```

Doc page example:
```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Nested Temporal Domains",
  "url": "https://<confirmed-domain>/docs/13_nested_temporal_domains/",
  "about": ["nested temporal domains", "causality", "continuity architecture"],
  "isPartOf": {
    "@type": "WebSite",
    "name": "Sandy Chaos",
    "url": "https://<confirmed-domain>/"
  }
}
```

### Immediate action
- identify actual page-rendering stack
- inject metadata at layout/template layer, not by hand per page if avoidable
- generate sitemap from canonical route list

---

## 4. Internal embedding / retrieval surfaces worth exposing safely

### Current state
Internal embedding-aware retrieval exists in code, but no public machine surface in this repo clearly exposes it as a site feature.

### Principle
Do **not** expose raw internal memory or unstable experimental retrieval surfaces just because they exist.
Public exposure should follow SC discipline:
- canonical first
- bounded interfaces
- no hidden/private state leakage
- no speculative claims disguised as operational capability

### Safe exposure candidates

#### 4a. Public corpus manifest
A machine-readable manifest of crawl-approved public documents.
Example format: JSON

```json
{
  "site": "Sandy Chaos",
  "version": "v1",
  "documents": [
    {
      "path": "/docs/01_foundations.md",
      "title": "Foundations",
      "tier": "canonical",
      "topics": ["foundations", "causality", "assumptions"]
    }
  ]
}
```

#### 4b. Public concept graph export
Derived from glossary/canonical docs only, not private memory.
Could expose:
- concept id
- title
- parent/related concepts
- canonical doc path
- status (`canonical`, `supporting`, `archive`)

#### 4c. Read-only retrieval API or static index
Only if the site stack supports it cleanly.
Potential outputs:
- lexical search index
- public embedding index over canonical docs only
- query -> top canonical docs + snippets

#### 4d. Crawler-facing reading-order map
This may be simpler and safer than a full API.
Could be exposed via:
- `llms-full.txt`
- `public-corpus.json`
- `reading-order.json`

### Unsafe exposure candidates for now
- private memory files
- prompt packets not meant for public consumption
- raw pressure/promotions unless intentionally published
- unreviewed archive drafts being treated as authoritative

### Immediate action
Recommended order:
1. publish `llms-full.txt`
2. publish `public-corpus.json`
3. add sitemap + canonical metadata
4. only then consider public retrieval/index APIs

---

## Concrete implementation order

### Phase 0, done today
- repo-root `robots.txt` created
- repo-root `llms.txt` created

### Phase 1, next 30 minutes
- confirm live domain + deployment path
- author `llms-full.txt`
- author `public-corpus.json`
- update `robots.txt` with real sitemap URL

### Phase 2, next 60-90 minutes
- generate `sitemap.xml`
- define canonical URL policy
- define page metadata defaults (title/description/OG/Twitter)
- define JSON-LD templates for homepage + article pages

### Phase 3, after deploy surface is identified
- wire templates into real site generator
- validate published files via live fetch
- optionally add public lexical/embedding retrieval layer

---

## Blockers
1. **Live domain not yet confirmed in this repo scan**
2. **Actual public site build/deploy stack not yet detected in this repo**
3. **Unclear which repo/path is the true website renderer**

Until those are resolved, this document is a correct architecture/spec, but not yet fully attached to the live public surface.

---

## Recommendation
Highest-value immediate move:
- find the actual site deploy source,
- then wire these machine surfaces at the layout/build layer rather than as isolated files in content repo root.

That is the clean path to truly claw oneself.
