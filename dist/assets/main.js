const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
function closeMenu(returnFocus = false) {
  toggle.setAttribute('aria-expanded', 'false');
  nav.classList.remove('is-open');
  if (returnFocus) toggle.focus();
}
toggle.addEventListener('click', () => {
  const open = toggle.getAttribute('aria-expanded') !== 'true';
  toggle.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('is-open', open);
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') closeMenu(true);
});
document.addEventListener('click', e => {
  if (!e.target.closest('.header')) closeMenu();
});
nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => closeMenu()));
matchMedia('(min-width: 1100px)').addEventListener('change', e => { if (e.matches) closeMenu(); });
document.querySelector('[data-top]').addEventListener('click', e => {
  e.preventDefault();
  window.scrollTo({top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  document.querySelector('.brand').focus({preventScroll: true});
});
document.querySelector('#year').textContent = new Date().getFullYear();
