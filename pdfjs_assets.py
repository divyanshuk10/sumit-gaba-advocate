"""Install the pinned PDF.js release for same-origin static hosting."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

VERSION = '6.5.438'
ARCHIVE_SHA256 = '55138aa33b5f1f6f68809895338b947f395f344eb6381d424b2420d6daa6a844'
RELEASE_URL = f'https://github.com/mozilla/pdf.js/releases/download/v{VERSION}/pdfjs-{VERSION}-legacy-dist.zip'


def prepare_pdfjs(root):
    destination = Path(root) / 'dist/assets/pdfjs' / VERSION
    marker = destination / '.release-sha256'
    if marker.is_file() and marker.read_text().strip() == ARCHIVE_SHA256:
        return
    print(f'Preparing PDF.js {VERSION} from the official Mozilla release...')
    with urlopen(RELEASE_URL, timeout=90) as response:
        archive = response.read()
    if sha256(archive).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('PDF.js release checksum mismatch; refusing to build.')
    with ZipFile(BytesIO(archive)) as files:
        for member in files.infolist():
            name = member.filename
            if name in ('LICENSE', 'build/pdf.mjs', 'build/pdf.worker.mjs') or (
                name.startswith(('web/cmaps/', 'web/standard_fonts/', 'web/wasm/'))
                and not member.is_dir() and not name.endswith('.map')
            ):
                path = Path(name)
                if path.is_absolute() or '..' in path.parts:
                    raise ValueError('Invalid PDF.js release path.')
                target = destination / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(files.read(member))
    marker.write_text(ARCHIVE_SHA256 + '\n')
