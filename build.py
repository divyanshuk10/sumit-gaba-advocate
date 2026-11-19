from pathlib import Path
from html import escape
import json
import argparse
import shutil
from hashlib import sha256
from urllib.parse import urlsplit
from calendar_page import render_calendar, available_calendars
from pdfjs_assets import prepare_pdfjs

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description='Build the Sumit Gaba static website.')
parser.add_argument('--public', action='store_true', help='Enable public metadata and search indexing.')
parser.add_argument('--demo', action='store_true', help='Keep a public demo excluded from search indexing.')
parser.add_argument('--site-url', default='https://sumitgabaadvocate.github.io', help='Canonical public URL, including any project subdirectory.')
parser.add_argument('--output', default='dist', help='Output directory (assets are copied from dist/assets).')
ARGS = parser.parse_args()
SITE_URL = ARGS.site_url.rstrip('/')
origin = urlsplit(SITE_URL)
if origin.scheme != 'https' or not origin.netloc or origin.query or origin.fragment or '..' in origin.path:
 parser.error('--site-url must be an HTTPS URL without a query or fragment.')
if ARGS.demo and not ARGS.public:
 parser.error('--demo requires --public.')
BASE_PATH = origin.path.rstrip('/') if ARGS.public else ''
OUT = (ROOT / ARGS.output).resolve()
OUT.mkdir(parents=True, exist_ok=True)
prepare_pdfjs(ROOT)
if OUT != ROOT / 'dist':
 shutil.copytree(ROOT / 'dist/assets', OUT / 'assets', dirs_exist_ok=True)
DATA = json.loads((ROOT / 'content.json').read_text())
CALENDAR_YEAR = available_calendars(ROOT)[0][0]
CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; frame-src 'self'; object-src 'none'; connect-src 'none'; base-uri 'none'; form-action 'none'; upgrade-insecure-requests"
nav = [('/', 'Home'),('/profile/', 'Profile'),('/practice-areas/', 'Areas of Practice'),('/resources/', 'Court Resources'),('/holiday-calendar/', 'Holiday Calendar'),('/contact/', 'Contact & Chambers')]
DESCRIPTIONS = {
 '/': 'Sumit Gaba, Advocate in Delhi. Professional profile, areas of practice, office and court chamber details, and court resources.',
 '/profile/': 'Professional profile of Sumit Gaba, Advocate, ONS Gaba & Associates. Enrolment D/2355/06, with office and court chambers in Delhi.',
 '/practice-areas/': 'An overview of civil, property, family and criminal proceedings handled by the practice of Sumit Gaba, Advocate in Delhi.',
 '/resources/': 'Official court links for the Supreme Court of India, Delhi High Court, Delhi District Courts and eCourts Services.',
 '/holiday-calendar/': f'View or download the original Delhi High Court calendar for {CALENDAR_YEAR}.',
 '/contact/': 'Contact Sumit Gaba, Advocate. Office in Shubhash Nagar and court chambers at Tis Hazari and Dwarka, with phone and WhatsApp enquiries.',
 '/disclaimer/': 'Information-use notice, external-link terms and professional engagement information for the Sumit Gaba, Advocate website.',
 '/privacy/': 'How this website handles visitor information, contact enquiries and links to external services.',
 '/404/': 'This page could not be found. Browse the professional profile, practice information and chamber contact details.'
}

def asset_url(path):
 return path + '?v=' + sha256((ROOT/'dist'/path.lstrip('/')).read_bytes()).hexdigest()[:12]

def links(active, footer=False):
 return ''.join(f'<a href="{url}"'+(' aria-current="page"' if active==url else '')+f'>{label}</a>' for url,label in nav)

def shell(title, body, route='/'):
 description = escape(DESCRIPTIONS[route], quote=True)
 public_page = ARGS.public and route != '/404/'
 robots = 'index,follow' if public_page and not ARGS.demo else 'noindex,follow' if ARGS.public else 'noindex,nofollow'
 page_title = 'Sumit Gaba — Advocate in Delhi' if route == '/' else escape(title) + ' — Sumit Gaba, Advocate'
 metadata = ''
 if public_page:
  canonical = escape(SITE_URL + route, quote=True)
  metadata = f'''<link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:locale" content="en_IN"><meta property="og:site_name" content="Sumit Gaba — Advocate"><meta property="og:title" content="{page_title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE_URL}/assets/chamber.webp"><meta property="og:image:alt" content="Illustrative law library"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{page_title}"><meta name="twitter:description" content="{description}"><meta name="twitter:image" content="{SITE_URL}/assets/chamber.webp">'''
 if route == '/holiday-calendar/':
  metadata += f'<link rel="stylesheet" href="{asset_url("/assets/calendar.css")}"><script type="module" src="{asset_url("/assets/calendar-viewer.mjs")}"></script>'
 page_csp = CSP.replace("connect-src 'none'", "connect-src 'self'; worker-src 'self'") if route == '/holiday-calendar/' else CSP
 html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="{escape(page_csp, quote=True)}"><meta name="referrer" content="no-referrer"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}</title><meta name="description" content="{description}">
<meta name="robots" content="{robots}"><meta name="theme-color" content="#3A1018">{metadata}
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{asset_url('/assets/style.css')}"><script src="/assets/main.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<div class="utility"><div class="wrap utility-inner"><span>Chamber practice <span class="utility-detail">/ Delhi</span></span><span>Enrolment: {DATA['enrolment']} <span class="utility-location">New Delhi</span></span></div></div>
<header class="header"><div class="wrap header-inner"><a class="brand" href="/" aria-label="Sumit Gaba, Advocate — Home"><span class="monogram" aria-hidden="true">SG</span><span><span class="brand-name">Sumit Gaba <small>Advocate</small></span><span class="brand-sub">ONS Gaba & Associates</span></span></a>
<button class="menu-toggle" type="button" aria-controls="navigation" aria-expanded="false"><span class="menu-icon" aria-hidden="true"></span><span>Menu</span></button><nav id="navigation" aria-label="Main navigation">{links(route)}</nav></div></header>
<main id="main">{external_profiles() if route == "/profile/" else ""}{body}</main>
<footer><div class="wrap footer-grid"><div><a class="brand footer-brand" href="/"><span class="monogram" aria-hidden="true">SG</span><span class="brand-name">Sumit Gaba <small>Advocate</small></span></a><p>Professional profile and chamber information.<br>New Delhi, India.</p><span class="footer-enrolment">Enrolment: {DATA['enrolment']}</span></div><div><h2 class="eyebrow">Explore</h2><nav aria-label="Footer navigation">{links(route,True)}</nav></div><div><h2 class="eyebrow">Information notice</h2><p>Information about the practice, chamber locations and court resources. The content is for general reference and does not constitute legal advice.</p><a class="footer-notice-link" href="/disclaimer/">Read the information-use notice</a></div></div><div class="wrap footer-bottom"><span>© <span id="year">2026</span> Sumit Gaba, Advocate</span><div><a href="/disclaimer/">Disclaimer & Terms</a><a href="/privacy/">Privacy</a><a href="#top" data-top>Back to top</a></div></div></footer>

</body></html>'''
 return html.replace('href="/', f'href="{BASE_PATH}/').replace('src="/', f'src="{BASE_PATH}/')

def heading(kicker, title, text=''):
 return f'<div class="section-heading"><span class="eyebrow">{kicker}</span><h2>{title}</h2><span class="short-rule"></span>'+ (f'<p>{text}</p>' if text else '')+'</div>'

def pagehead(label,title,text):
 return f'<section class="page-heading"><div class="wrap"><div class="breadcrumb"><a href="/">Home</a><span>/</span>{label}</div><span class="eyebrow">Chamber information</span><h1>{title}</h1><p>{text}</p></div></section>'

def facts():
 return f'''<div class="identity-card"><div class="identity-title"><span class="square-monogram" aria-hidden="true">SG</span><div><span class="eyebrow">Professional particulars</span><strong>Sumit Gaba, Advocate</strong></div></div><dl><div><dt>Enrolment number</dt><dd>{DATA['enrolment']}</dd></div><div><dt>Practice name</dt><dd>{DATA['practice']}</dd></div><div><dt>Court chambers</dt><dd>Tis Hazari & Dwarka</dd></div></dl></div>'''

def external_profiles():
 profiles = [p for p in DATA.get('external_profiles', []) if p.get('enabled')]
 if not profiles:
  return ''
 cards = ''.join(f'<div class="spotlight-action"><a class="button primary" href="{escape(p["url"], quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="View Sumit Gaba on eCourtsIndia (opens in a new tab)">View eCourtsIndia Profile</a><span class="external-link-note">Opens in a new tab</span></div>' for p in profiles)
 return f'''<aside class="profile-spotlight" aria-label="External advocate profile"><div class="wrap spotlight-card"><div class="spotlight-main"><span class="directory-symbol" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M7 5h18v23H7zM11 10h10M11 22h10M12 17c0-2 8-2 8 0v1h-8z"/><circle cx="16" cy="12.5" r="2" fill="#3a1018"/></svg></span><div class="spotlight-copy"><span class="eyebrow">Independent directory</span><p class="spotlight-title">Sumit Gaba on eCourtsIndia</p><p class="spotlight-description">Explore the third-party advocate listing and case records.</p><span class="spotlight-provider">Private platform · Independent of courts and government</span></div>{cards}</div><p class="spotlight-note">Listings may be incomplete or out of date. Verify case information with the relevant court.</p></div></aside>'''

def profile(full=False):
 return f'''<section class="section white"><div class="wrap profile-grid"><div>{heading('The practice','Professional Profile','Enrolment details, practice information and professional locations in Delhi.')}{facts()}</div><div class="profile-copy"><span class="eyebrow">Sumit Gaba · Advocate</span><h3>Legal practice in Delhi</h3><p>Sumit Gaba is an advocate practising in Delhi under the name ONS Gaba & Associates.</p><p>The office is located in Shubhash Nagar, with court chambers at Tis Hazari and Dwarka. The practice includes civil litigation, property matters, and family and matrimonial proceedings.</p><p>For enquiries about a matter or a chamber visit, please contact the office using the telephone details provided. Official court links are also available for case information, cause lists and published orders.</p><a class="text-link" href="{'/contact/' if full else '/profile/'}">{'View chamber details' if full else 'View professional profile'}</a><div class="profile-features"><div><span class="feature-icon" aria-hidden="true">§</span><h4>Areas of practice</h4><p>Civil, criminal, property and family-related proceedings.</p></div><div><span class="feature-icon" aria-hidden="true">⌂</span><h4>Office & chambers</h4><p>Professional locations in Shubhash Nagar, Tis Hazari and Dwarka.</p></div><div><span class="feature-icon" aria-hidden="true">≡</span><h4>Court resources</h4><p>Official portals for case information and published orders.</p></div></div></div></div></section>'''

practices=[('Civil Litigation','Civil proceedings and related applications before the appropriate courts.',['Civil suits and applications','Interim relief and related proceedings','Execution and appellate proceedings']),('Property Matters','Matters concerning property, possession and documentation.',['Property and possession disputes','Title and partition matters','Tenancy and documentation']),('Family & Matrimonial Matters','Family-related proceedings and dispute-resolution processes.',['Matrimonial proceedings','Maintenance and custody matters','Mediation and conciliation'])]

def practice_cards():
 return '<div class="practice-grid">'+''.join(f'''<article class="practice-card"><span class="eyebrow">Area of practice</span><h3>{name}</h3><p>{desc}</p><ul>{''.join(f'<li>{x}</li>' for x in topics)}</ul><div class="card-foot"><span>Contact & enquiries</span><a href="/contact/">Chamber details</a></div></article>''' for name,desc,topics in practices)+'</div>'

PROCEEDING_ICONS = {
 'Civil Miscellaneous Application': '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 15h8M12 11v8"/>',
 'Criminal Complaint Case': '<rect x="5" y="4" width="14" height="18" rx="2"/><rect x="9" y="2" width="6" height="4" rx="1" fill="var(--ivory)"/><path d="M12 10v5M12 18h.01"/>',
 'Criminal Miscellaneous': '<path d="M12 2 3 6v6c0 5 5 9 9 10 4-1 9-5 9-10V6zM8 12h8M12 8v8"/>',
 'Civil Suit': '<path d="M12 3v18M7 21h10M4 7h16M5 7l-3 7h6L5 7Zm14 0-3 7h6l-3-7ZM2 14a3 3 0 0 0 6 0M16 14a3 3 0 0 0 6 0"/>',
 'Criminal Revision': '<path d="M13 2H5a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h7M13 2v6h6V8l-6-6ZM7 12h3M7 16h2"/><circle cx="16" cy="15" r="4"/><path d="m19 18 3 3"/>',
 'First Appeal': '<path d="m12 3 9 5-9 5-9-5 9-5ZM3 12l9 5 9-5M3 16l9 5 9-5"/>',
 'Execution Application (Civil)': '<path d="M4 16h16v5H4zM7 16v-3c0-2 2-3 3-4V5a2 2 0 0 1 4 0v4c1 1 3 2 3 4v3M7 19h10"/>',
 'Civil Appeal': '<path d="M3 7V5a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7ZM3 9h18m-12 7 3-3 3 3"/>',
 'Motor Accident Claims Appeal': '<path d="m5 9 2-5h10l2 5M3 11l2-2h14l2 2v7H3v-7ZM6 18v3M18 18v3M7 13h.01M17 13h.01M10 15h4"/>',
 'Contempt Petition': '<path d="m3 7 9-5 9 5H3ZM5 10v7M9 10v7M3 21h11M3 18h10M13 10h2M19 11v5M19 19h.01"/><rect x="15" y="9" width="8" height="13" rx="1"/>',
 'Death Reference': '<path d="M12 5C9 3 5 3 2 4v16c4-1 7-1 10 1 3-2 6-2 10-1V4c-3-1-7-1-10 1v16M5 8h4M5 12h4M15 8h4M15 12h4"/>',
 'Bail Application': '<rect x="4" y="10" width="16" height="12" rx="2"/><path d="M8 10V6a4 4 0 0 1 7.6-1.7M12 15v3"/>',
}

def proceeding_icon(label):
 return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{PROCEEDING_ICONS[label]}</svg>'

def proceeding_types():
 items = ''.join(f'<li><span class="proceeding-icon" aria-hidden="true">{proceeding_icon(label)}</span><span>{escape(label)}</span></li>' for label in DATA.get('practice_proceeding_types', []))
 return f'''<div class="proceedings"><div class="proceedings-heading"><div><span class="eyebrow">Proceedings & applications</span><h3>Additional Areas of Practice</h3><p>Civil and criminal applications, appeals and related proceedings.</p></div><a class="text-link" href="https://ecourtsindia.com/advocate/sumit-gaba-3598" target="_blank" rel="noopener noreferrer">View directory profile<span class="proceeding-link-note">Opens in a new tab</span></a></div><ul class="proceeding-grid">{items}</ul></div>'''

def practice_section():
 return f'''<section class="section"><div class="wrap"><div class="heading-row">{heading('Areas of practice','Legal Practice','Civil, criminal, property and family-related matters, including applications, appeals and execution proceedings.')}</div>{practice_cards()}{proceeding_types()}</div></section>'''

resources=[('Apex court','Supreme Court of India','https://www.sci.gov.in/','sci.gov.in','Court information, cause lists, judgments and orders.'),('High court','Delhi High Court','https://delhihighcourt.nic.in/','delhihighcourt.nic.in','Court notices, cause lists, case information and judgments.'),('District judiciary','Delhi District Courts','https://delhidistrictcourts.nic.in/','delhidistrictcourts.nic.in','Information and services for Delhi’s district court complexes.'),('Case information','eCourts Services','https://services.ecourts.gov.in/','services.ecourts.gov.in','Official case-status and court-order services.')]

def court_service_tiles():
 services = [
  ('Video Conference', 'https://delhidistrictcourts.nic.in/lockdownfiling', 'Delhi District Courts', 'Find your district and court’s official video hearing link.', 'Open hearing links', '<rect x="2" y="5" width="14" height="14" rx="2"/><path d="m16 10 6-4v12l-6-4z"/>'),
  ('e-Filing Portal', 'https://filing.ecourts.gov.in/pdedev/', 'Online filing', 'Access the official portal for online case and document filing.', 'Open e-Filing', '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M12 18v-7m-3 3 3-3 3 3"/>'),
  ('Virtual Court', 'https://vcourts.gov.in/virtualcourt/', 'Online court services', 'Access online services for cases handled by Virtual Courts.', 'Open Virtual Court', '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4M6 9l6-3 6 3H6Zm2 2v3m4-3v3m4-3v3"/>'),
  ('ePay Portal', 'https://pay.ecourts.gov.in/epay/', 'eCourts digital payments', 'Access the official eCourts digital payment portal.', 'Open ePay', '<rect x="2" y="5" width="20" height="15" rx="2"/><path d="M2 10h20M6 15h4M16 3v4"/>')
 ]
 return '<div class="court-service-grid" aria-label="Useful court services">' + ''.join(f'''<a class="court-service-tile" href="{url}" target="_blank" rel="noopener noreferrer"><span class="court-service-heading"><span class="court-service-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{icon}</svg></span><span class="eyebrow">{category}</span></span><h3>{title}</h3><p>{description}</p><span class="court-service-action">{action}</span><span class="court-service-external">Official portal · Opens in a new tab</span></a>''' for title,url,category,description,action,icon in services) + '</div>'

def resource_section():
 return f'''<section class="section white"><div class="wrap"><div class="heading-row">{heading('Public judicial utilities','Official Court Resources','Direct links to official judicial portals for court information, case services and published orders.')}<span class="subtle-label">External official services</span></div>{court_service_tiles()}<div class="resource-grid">'''+''.join(f'''<a class="resource-card" href="{url}" target="_blank" rel="noopener noreferrer"><span class="resource-top"><span class="eyebrow">{tag}</span><svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M9 5H5v14h14v-4M13 5h6v6M10 14l9-9"/></svg></span><h3>{name}</h3><span class="domain">{domain}</span><p>{desc}</p><span class="small">Opens in a new tab</span></a>''' for tag,name,url,domain,desc in resources)+'''</div><p class="small resource-note">These services are operated by their respective courts and government authorities. This chamber website is independent of them.</p></div></section>'''

def phone_card(number):
 whatsapp = ''
 if number == DATA.get('whatsapp_number'):
  whatsapp = f'''<a class="whatsapp-link" href="https://wa.me/91{number}" target="_blank" rel="noopener noreferrer" aria-label="Message +91 {number} on WhatsApp (opens in a new tab)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 21l1.9-5.5A8.5 8.5 0 1 1 21 11.5Z"/><path d="m8.2 7.2 1.4 2.6-1 1a8.5 8.5 0 0 0 4.4 4.4l1-1 2.7 1.4c-.5 2-2.5 2-4.7.9a12.7 12.7 0 0 1-5.2-5.2c-1.1-2.2-1.1-4.1 1.4-4.1Z"/></svg><span>Message on WhatsApp</span></a>'''
 return f'<div class="phone-card"><span class="phone-icon" aria-hidden="true">☎</span><div><span class="eyebrow">Telephone</span><a class="phone-number" href="tel:+91{number}" aria-label="Call +91 {number}">+91 {number[:5]} {number[5:]}</a><span class="small">Office & chamber enquiries</span>{whatsapp}</div></div>'

def contact_section():
 cards=''.join(f'''<article class="location-card"><div class="location-meta"><span>{item['tag']}</span><span>{item['area']}</span></div><h3>{item['name']}</h3><address>{escape(item['address'])}</address><div class="card-foot">{item['area']}</div></article>''' for item in DATA['locations'])
 phones=''.join(phone_card(number) for number in DATA['phones'])
 email = escape(DATA['email'], quote=True)
 email_card = f'<div class="phone-card email-card"><span class="phone-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/></svg></span><div><span class="eyebrow">Email</span><a class="contact-email" href="mailto:{email}">{email}</a><span class="small">Office &amp; chamber enquiries</span></div></div>' 
 return f'''<section class="section contact-section"><div class="wrap"><div class="heading-row">{heading('Office & court chambers','Locations & Contact','Find the office and court chambers in Delhi. Please call to arrange a visit and confirm availability.')}</div><div class="location-grid">{cards}</div><div class="telephone"><div><span class="eyebrow">Get in touch</span><h3>Call, Message or Email</h3><p class="small">Contact the office by phone, WhatsApp or email about a matter, chamber location or visit.</p></div><div class="phone-grid">{phones}{email_card}</div></div><p class="small contact-note">Please confirm the meeting location before travelling to the office or a court chamber.</p></div></section>'''

hero=f'''<section class="hero" id="top"><div class="wrap hero-grid"><div class="hero-copy"><span class="credential">Enrolment · {DATA['enrolment']}</span><h1>Sumit Gaba</h1><p class="hero-role">Advocate</p><p class="hero-subtitle">Professional profile, areas of practice,<br class="desktop-break"> and chamber information.</p><p class="hero-description">Office and court chamber details in Delhi, with an overview of civil, criminal, property and family-related matters.</p><div class="hero-actions"><a class="button primary" href="/profile/">View Professional Profile</a><a class="button secondary" href="/contact/">Contact Details</a></div><div class="hero-facts"><div><span class="eyebrow">Court chambers</span><strong>Tis Hazari & Dwarka</strong></div><div><span class="eyebrow">Office</span><strong>Shubhash Nagar, Delhi</strong></div></div></div><figure class="hero-image"><div class="image-frame"><img src="/assets/chamber.webp" width="1376" height="768" alt="Illustrative law library with bookshelves and a wooden desk" fetchpriority="high"><div class="image-caption"><span class="eyebrow">Law & legal research</span><p>Law, learning & considered practice.</p></div></div><figcaption><span>Illustrative law library</span><span>New Delhi</span></figcaption></figure></div></section>'''

pages={
 '/':('Professional Profile & Chambers',hero+external_profiles()+profile()+practice_section()+resource_section()+contact_section()),
 '/profile/':('Professional Profile',pagehead('Profile','Professional Profile','Identity, professional particulars and chamber information.')+profile(True)),
 '/practice-areas/':('Areas of Practice',pagehead('Areas of Practice','Areas of Practice','An overview of civil, criminal, property and family-related proceedings.')+practice_section()+f'<div class="wrap end-note"><a class="text-link" href="/resources/">Explore official court resources</a></div>'),
 '/resources/':('Court Resources',pagehead('Court Resources','Official Court Resources','A concise directory of independently operated judicial information services.')+resource_section()),
 '/holiday-calendar/':(f'Court Holiday Calendar {CALENDAR_YEAR}',pagehead('Holiday Calendar','Court Holiday Calendar',f'Delhi High Court · {CALENDAR_YEAR}')+render_calendar(ROOT)),
 '/contact/':('Contact & Chambers',pagehead('Contact & Chambers','Contact & Chambers','Office and court chamber locations in Delhi, with phone, WhatsApp and email contacts for enquiries.')+contact_section()),
 '/disclaimer/':('Disclaimer & Terms',pagehead('Disclaimer','Information-use Notice','Please read this notice when using the information and links on this website.')+'''<section class="section white"><div class="wrap reading"><h2>About this website</h2><p>This website provides professional and chamber information about Sumit Gaba, Advocate, together with links to court services and an independent advocate directory. It is intended for general information.</p><h2>Legal advice and engagement</h2><p>The information here does not constitute legal advice or an opinion on any individual matter. Advice depends on the facts, documents and circumstances of the case.</p><p>Viewing this website or making an enquiry does not by itself establish an advocate-client relationship. Representation is subject to the advocate accepting the matter and agreeing the terms of engagement.</p><h2>External websites</h2><p>Court-resource links lead to websites operated by the relevant courts or authorities. eCourtsIndia is a separate private platform. These external websites are responsible for their own content, services and availability.</p><h2>Case information</h2><p>Case status, hearing dates and orders should be checked with the relevant court records. Directory entries and third-party summaries may be incomplete or out of date.</p><h2>Contact details</h2><p>Please contact the office to confirm availability and the appropriate meeting location before travelling.</p></div></section>'''),
 '/privacy/':('Privacy',pagehead('Privacy','Privacy Notice','How information is handled when you visit this website or follow its links.')+'''<section class="section white"><div class="wrap reading"><h2>Information you share</h2><p>This website does not have an enquiry form or accept document uploads. Telephone, WhatsApp and email enquiries take place outside the website. Please avoid sending sensitive documents until you have agreed an appropriate way to share them with the advocate.</p><h2>Website activity</h2><p>The website does not use advertising scripts, marketing cookies or analytics trackers. The hosting provider may process technical information, such as an IP address and requested page, to deliver the site and maintain security.</p><h2>Access and sign-in</h2><p>If you are asked to sign in to access this website, the authentication provider handles that process under its own privacy policy.</p><h2>External links</h2><p>Following a court-resource, directory or WhatsApp link takes you to a separately operated service. Its own privacy policy and terms apply to your activity there.</p><h2>Questions</h2><p>For questions about information on this website, please use the contact options on the Contact & Chambers page.</p></div></section>'''),
 '/404/':('Page Not Found',pagehead('Page not found','This page could not be found.','The address may have changed. Use the links below to continue.')+'''<section class="section white"><div class="wrap hero-actions"><a class="button primary" href="/">Return Home</a><a class="button secondary" href="/contact/">Chamber Details</a></div></section>''')
}
if ARGS.public:
 title, body = pages['/privacy/']
 body = body.replace('<h2>Access and sign-in</h2><p>If you are asked to sign in to access this website, the authentication provider handles that process under its own privacy policy.</p>', '<h2>Hosting</h2><p>This public website is hosted on GitHub Pages and does not require a visitor account. GitHub processes technical information under its <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" target="_blank" rel="noopener noreferrer">privacy statement</a>.</p>')
 pages['/privacy/'] = (title, body)
for route,(title,body) in pages.items():
 dest = OUT / route.lstrip('/') / 'index.html' if route!='/' else OUT/'index.html'
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(shell(title,body,route))
(OUT/'404.html').write_text(shell(*pages['/404/'],route='/404/'))
(OUT/'.nojekyll').write_text('')
if ARGS.public and not ARGS.demo:
 (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
 (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{escape(SITE_URL + route)}</loc></url>\n' for route in pages if route != '/404/') + '</urlset>\n')
else:
 (OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
 if (OUT/'sitemap.xml').exists():
  (OUT/'sitemap.xml').unlink()
print(f'Generated {len(pages)} routes and 404.html')
