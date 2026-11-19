"""Check generated links, metadata, public/private mode and contact destinations."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument('directory')
parser.add_argument('--public', action='store_true')
parser.add_argument('--demo', action='store_true')
parser.add_argument('--base-path', default='')
args = parser.parse_args()
root = Path(args.directory).resolve()

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

files = list(root.rglob('*.html'))
assert len(files) == 10, f'Expected 10 HTML files, found {len(files)}'
for file in files:
    page = Page()
    page.feed(file.read_text())
    tags = page.tags
    policies = [a['content'] for t, a in tags if t == 'meta' and a.get('http-equiv', '').lower() == 'content-security-policy']
    assert len(policies) == 1, f'{file}: missing Content Security Policy'
    for directive in ("script-src 'self'", "object-src 'none'", "base-uri 'none'", "form-action 'none'", "frame-src 'self'"):
        assert directive in policies[0], f'{file}: missing {directive}'
    assert "'unsafe-inline'" not in policies[0] and "'unsafe-eval'" not in policies[0], file
    assert any(t == 'meta' and a.get('name') == 'referrer' and a.get('content') == 'no-referrer' for t, a in tags), file
    assert all(not key.lower().startswith('on') for _, attrs in tags for key in attrs), f'{file}: inline event handler'
    assert all(attrs.get('src', '').startswith('/') for tag, attrs in tags if tag == 'script'), f'{file}: inline or external script'
    assert sum(tag == 'h1' for tag, _ in tags) == 1, file
    robots = next(a['content'] for t, a in tags if t == 'meta' and a.get('name') == 'robots')
    is_error = file == root/'404.html' or file == root/'404/index.html'
    expected_robots = ('noindex,follow' if is_error or args.demo else 'index,follow') if args.public else 'noindex,nofollow'
    assert robots == expected_robots, file
    canonicals = [a['href'] for t, a in tags if t == 'link' and a.get('rel') == 'canonical']
    assert len(canonicals) == int(args.public and not is_error), file
    for tag, attrs in tags:
        if tag == 'img':
            assert attrs.get('alt'), file
        if attrs.get('target') == '_blank':
            assert 'noopener' in attrs.get('rel', '').split(), file
        for attr in ('href', 'src'):
            url = urlsplit(attrs.get(attr, ''))
            if url.scheme or url.netloc or not url.path:
                continue
            path = unquote(url.path)
            if path.startswith('/') and args.base_path:
                assert path.startswith(args.base_path.rstrip('/')+'/'), f'{file}: missing base path: {path}'
                path = path[len(args.base_path.rstrip('/')):]
            target = root/path.lstrip('/') if path.startswith('/') else file.parent/path
            if target.is_dir():
                target = target/'index.html'
            assert target.is_file(), f'{file}: missing {attrs[attr]}'
for file in (root/'index.html', root/'contact/index.html'):
    page = Page(); page.feed(file.read_text())
    links = [a.get('href') for t, a in page.tags if t == 'a']
    assert links.count('https://wa.me/917011546631') == 1
    assert all('tel:+91'+number in links for number in ('9310377771', '7011546631'))
assert (root/'.nojekyll').is_file()
if args.public and not args.demo:
    sitemap = ET.parse(root/'sitemap.xml')
    assert len(sitemap.getroot()) == 8
    assert 'Disallow: /' not in (root/'robots.txt').read_text()
    assert 'Access and sign-in' not in (root/'privacy/index.html').read_text()
else:
    assert not (root/'sitemap.xml').exists()
    assert 'Disallow: /' in (root/'robots.txt').read_text()
for path in ('marcellus.ttf', 'source-sans.ttf'):
    assert (root/'assets'/path).is_file()
print(f'Passed: {len(files)} pages, internal destinations, metadata, contacts and build mode.')
