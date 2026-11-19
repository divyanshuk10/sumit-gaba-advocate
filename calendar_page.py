"""Show the newest uploaded calendar PDF, with links to previous years."""
from html import escape
from pathlib import Path
import re


def available_calendars(root):
    folder = Path(root) / 'dist/assets/calendars'
    files = [(int(file.stem), '/assets/calendars/' + file.name)
             for file in folder.glob('*.pdf')
             if re.fullmatch(r'[0-9]{4}', file.stem)]
    if not files:
        raise ValueError('Add a calendar PDF named YYYY.pdf to dist/assets/calendars/.')
    return sorted(files, reverse=True)


def render_calendar(root):
    calendars = available_calendars(root)
    year, url = calendars[0]
    archive = ''
    if len(calendars) > 1:
        links = ''.join(f'<li><a href="{escape(path, quote=True)}" target="_blank" rel="noopener noreferrer">{old_year} calendar <span>PDF · Opens in a new tab</span></a></li>' for old_year, path in calendars[1:])
        archive = f'<section class="calendar-archive"><h2>Previous years</h2><ul>{links}</ul></section>'
    return f'''<section class="section calendar-section"><div class="wrap">
<div class="calendar-document-head"><div><span class="eyebrow">Original court publication</span><h2>{year} Calendar</h2><p>View the calendar as published by the Delhi High Court, or save a copy for reference.</p></div><div class="calendar-actions"><a class="button primary" href="{url}" download="Delhi-Court-Calendar-{year}.pdf">Download PDF</a><a class="button secondary" href="{url}" target="_blank" rel="noopener noreferrer">Open PDF in a new tab</a></div></div>
<div class="calendar-viewer"><iframe src="{url}#toolbar=1&amp;navpanes=0&amp;view=FitH" title="Delhi High Court calendar {year} — original PDF"></iframe></div>
<p class="calendar-preview-note">If the preview does not load on your device, use “Open PDF in a new tab” above.</p>
<div class="calendar-source-note"><p>The original annual calendar is shown unchanged. For subsequent holiday changes and sitting arrangements, please check the court’s latest notices.</p><a class="text-link" href="https://delhihighcourt.nic.in/web/public-notice" target="_blank" rel="noopener noreferrer">Latest official court notices</a></div>
{archive}
</div></section>'''
