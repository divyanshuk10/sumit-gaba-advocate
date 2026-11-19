# Sumit Gaba — Advocate

Responsive professional website with profile, areas of practice, court resources and chamber contact details.

Demo: https://divyanshuk10.github.io/sumit-gaba-advocate/

## Development

Python 3 is the only build requirement. Professional particulars are in `content.json`, page templates are in `build.py`, and assets are in `dist/assets/`.

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
