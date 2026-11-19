// Render the original PDF without relying on a browser's native PDF plug-in.
const viewer = document.querySelector('#calendar-document');
const sourceLink = document.querySelector('.calendar-actions a[download]');

if (viewer && sourceLink) {
  const status = viewer.querySelector('[data-pdf-status]');
  const scroll = viewer.querySelector('.calendar-scroll');
  const canvas = viewer.querySelector('canvas');
  const pageLabel = viewer.querySelector('[data-pdf-page]');
  const zoomLabel = viewer.querySelector('[data-pdf-zoom]');
  const previous = viewer.querySelector('[data-pdf-previous]');
  const next = viewer.querySelector('[data-pdf-next]');
  const zoomIn = viewer.querySelector('[data-pdf-in]');
  const zoomOut = viewer.querySelector('[data-pdf-out]');
  const fit = viewer.querySelector('[data-pdf-fit]');
  let pdf;
  let pageNumber = 1;
  let zoom = 1;
  let renderTask;
  let generation = 0;
  let queue = Promise.resolve();
  let resizeTimer;

  function controls(enabled) {
    previous.disabled = !enabled || pageNumber <= 1;
    next.disabled = !enabled || pageNumber >= pdf.numPages;
    zoomIn.disabled = !enabled || zoom >= 3;
    zoomOut.disabled = !enabled || zoom <= 0.5;
    fit.disabled = !enabled;
  }

  function showError(error) {
    if (error?.name === 'RenderingCancelledException') return;
    status.hidden = false;
    status.textContent = 'The preview could not load. Please use Open PDF or Download PDF above.';
    canvas.hidden = true;
    controls(false);
    console.error('Calendar PDF preview:', error);
  }

  function draw(resetScroll = false) {
    const current = ++generation;
    renderTask?.cancel();
    controls(false);
    status.hidden = false;
    status.textContent = 'Loading calendar…';
    viewer.setAttribute('aria-busy', 'true');
    queue = queue.catch(() => {}).then(async () => {
      if (current !== generation) return;
      const page = await pdf.getPage(pageNumber);
      if (current !== generation) return;
      const natural = page.getViewport({ scale: 1 });
      const available = Math.max(1, scroll.clientWidth - 24);
      const viewport = page.getViewport({ scale: available / natural.width * zoom });
      // Bound canvas memory on phones, including large scanned PDFs.
      const density = Math.min(window.devicePixelRatio || 1, 2,
        4096 / viewport.width, 4096 / viewport.height,
        Math.sqrt(8_000_000 / (viewport.width * viewport.height)));
      canvas.width = Math.max(1, Math.floor(viewport.width * density));
      canvas.height = Math.max(1, Math.floor(viewport.height * density));
      canvas.style.width = `${Math.floor(viewport.width)}px`;
      canvas.style.height = `${Math.floor(viewport.height)}px`;
      canvas.setAttribute('aria-label', `Original court calendar, page ${pageNumber} of ${pdf.numPages}`);
      renderTask = page.render({
        canvasContext: canvas.getContext('2d'), viewport,
        transform: density === 1 ? null : [density, 0, 0, density, 0, 0],
      });
      await renderTask.promise;
      renderTask = null;
      if (current !== generation) return;
      canvas.hidden = false;
      status.hidden = true;
      pageLabel.textContent = `Page ${pageNumber} of ${pdf.numPages}`;
      zoomLabel.textContent = zoom === 1 ? 'Fit width' : `${Math.round(zoom * 100)}%`;
      viewer.setAttribute('aria-busy', 'false');
      controls(true);
      if (resetScroll) scroll.scrollTo({ top: 0, left: 0 });
    }).catch(error => {
      if (current === generation) {
        viewer.setAttribute('aria-busy', 'false');
        showError(error);
      }
    });
  }

  async function start() {
    const source = new URL(sourceLink.href);
    if (source.origin !== window.location.origin) throw new Error('Only local calendar PDFs are allowed.');
    const pdfjs = await import('./pdfjs/6.5.438/build/pdf.mjs');
    const library = new URL('./pdfjs/6.5.438/', import.meta.url);
    pdfjs.GlobalWorkerOptions.workerSrc = new URL('build/pdf.worker.mjs', library).href;
    const loading = pdfjs.getDocument({
      url: source.href,
      cMapUrl: new URL('web/cmaps/', library).href,
      standardFontDataUrl: new URL('web/standard_fonts/', library).href,
      wasmUrl: new URL('web/wasm/', library).href,
      useWasm: false,
      disableFontFace: true,
      enableXfa: false,
    });
    pdf = await loading.promise;
    previous.addEventListener('click', () => { if (pageNumber > 1) { pageNumber--; draw(true); } });
    next.addEventListener('click', () => { if (pageNumber < pdf.numPages) { pageNumber++; draw(true); } });
    zoomIn.addEventListener('click', () => { zoom = Math.min(3, zoom + 0.25); draw(); });
    zoomOut.addEventListener('click', () => { zoom = Math.max(0.5, zoom - 0.25); draw(); });
    fit.addEventListener('click', () => { zoom = 1; draw(true); });
    let width = scroll.clientWidth;
    new ResizeObserver(() => {
      if (scroll.clientWidth === width) return;
      width = scroll.clientWidth;
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => draw(), 120);
    }).observe(scroll);
    draw();
  }
  start().catch(showError);
}
