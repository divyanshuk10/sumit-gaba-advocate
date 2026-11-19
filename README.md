# Sumit Gaba — Advocate

Responsive professional website with profile, areas of practice, court resources and chamber contact details.

Demo: https://divyanshuk10.github.io/sumit-gaba-advocate/

## Development

Python 3 is the only build requirement. Professional particulars are in `content.json`, page templates are in `build.py`, and assets are in `dist/assets/`. The first build downloads the pinned official Mozilla PDF.js release and verifies its SHA-256 checksum. Subsequent local builds reuse it; GitHub Actions installs it automatically.

```bash
python3 build.py --public --demo --site-url https://divyanshuk10.github.io/sumit-gaba-advocate
python3 scripts/check_site.py dist --public --demo --base-path /sumit-gaba-advocate
```

Keep `dist/assets/` tracked. The build copies those assets when `--output` selects another directory.

## Deployment

Settings → Pages → Source: GitHub Actions. The workflow builds, validates and deploys `dist/` after each push to `main`. The demo uses noindex and disallows crawling. This does not restrict public access.

## Moving to the final account

Create `sumitgabaadvocate/sumitgabaadvocate.github.io`, copy the repository contents, and enable GitHub Actions as the Pages source. The workflow reads its URL and base path from GitHub Pages, so links adapt automatically. Remove `--demo` from both workflow commands when ready for search indexing; this enables the sitemap and indexable public metadata.

## Website features

Phone links and WhatsApp contact, a clearly labelled independent eCourtsIndia profile link, official court resources, custom 404 page, privacy and information-use notices. No API credentials or backend are required. No case feed or performance statistics are imported.

The law-library image is illustrative. Marcellus and Source Sans 3 are self-hosted under the SIL Open Font License; notices are in `dist/assets/licenses/`. No open-source licence is granted for the website code or other assets by this repository.

## Court Holiday Calendar

The `/holiday-calendar/` page renders the original PDF with self-hosted PDF.js, with fit-to-width, zoom and page controls, plus direct Open and Download links. This avoids relying on a mobile browser's native PDF iframe support. It does not extract, interpret or filter holiday dates. If JavaScript or the renderer fails, the original PDF links remain available.

`pdfjs_assets.py` pins PDF.js 6.5.438 (legacy distribution for broader browser compatibility), its official release URL and GitHub-published archive checksum. The generated library assets under `dist/assets/pdfjs/` are ignored by Git and included in every built deployment, including the Apache 2.0 licence and font/CMap notices. Updates require deliberately changing the version/checksum and matching import paths in `calendar-viewer.mjs`. PDF forms and document scripts are not executed by this canvas-only viewer. Canvas size is bounded for phone memory; the PDF itself is unchanged.

### Add a future year

Upload a PDF named for its year to `dist/assets/calendars/`, for example `2027.pdf`, and commit it to `main`. The build automatically embeds the highest-numbered year and lists older PDFs as downloads. No code or calendar-data edits are needed. Upload only calendar PDFs intended for publication. The original 2026 PDF is retained unchanged.

## Security baseline

Pages use a restrictive, meta-delivered Content Security Policy: local scripts/styles/fonts only, no inline/evaluated JavaScript, no object embeds, no form submissions, and no base-URL overrides. Only the calendar page permits same-origin fetches and workers to load the local PDF and its self-hosted renderer. Other pages retain `connect-src 'none'`. PDF.js WebAssembly and dynamic font-face loading are disabled. No external viewer or CDN is contacted by visitors. A no-referrer policy limits outbound referrer disclosure. New-tab links use `noopener noreferrer`.

The deployment workflow uses verified full commit SHAs for its four official actions, disables persisted checkout credentials, limits runtime, and grants only the permissions each job needs. Update action pins deliberately when updating the workflow. The site has no visitor authentication, enquiry form, database or visitor document uploads. Only approved public documents belong in the repository.

GitHub Pages serves HTTPS and HSTS. Other response headers are controlled by GitHub Pages: meta CSP does not provide `frame-ancestors` protection, and meta `X-Frame-Options`/`X-Content-Type-Options` would be ineffective. Stronger server-header control would require a hosting/proxy change. Repository administrators should protect their GitHub account with 2FA/passkeys; account and branch-protection settings are separate from this source configuration. This baseline is not a penetration-test certification.
