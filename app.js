// Respect "reduce motion"
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* Toggle contact (sans inline) */
(function(){
  const bubble = document.getElementById('contact-bubble');
  const form = document.getElementById('contact-form');
  const closeBtn = document.getElementById('close-form');
  if(!bubble || !form || !closeBtn) return;

  const open = ()=>{ form.hidden = false; bubble.setAttribute('aria-expanded','true'); };
  const close = ()=>{ form.hidden = true; bubble.setAttribute('aria-expanded','false'); };

  bubble.addEventListener('click', open, {passive:true});
  closeBtn.addEventListener('click', close, {passive:true});
  document.addEventListener('click', (e)=>{
    if(!form.hidden && !form.contains(e.target) && e.target !== bubble) close();
  }, {passive:true});
})();

/* Reveal au scroll (léger) */
(function(){
  if(reduceMotion || !('IntersectionObserver' in window)){
    document.querySelectorAll('section').forEach(s=> s.classList.add('is-visible'));
    return;
  }
  const io = new IntersectionObserver((entries, obs)=>{
    for(const entry of entries){
      if(entry.isIntersecting){
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    }
  }, { rootMargin: '0px 0px -10% 0px', threshold: 0.12 });
  document.querySelectorAll('#services, #presentation, #tarifs, #contact').forEach(sec=> io.observe(sec));
})();

/* Smooth scroll uniquement sur clic d’ancres (pas la molette) */
(function(){
  document.addEventListener('click', function(e){
    const a = e.target.closest('a[href^="#"]');
    if(!a) return;
    const id = a.getAttribute('href').slice(1);
    const el = document.getElementById(id);
    if(!el) return;
    e.preventDefault();
    const headerH = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--header-h')) || 100;
    const top = el.getBoundingClientRect().top + window.pageYOffset - (headerH + 12);
    window.scrollTo({ top: Math.max(0, top), behavior: reduceMotion ? 'auto' : 'smooth' });
    history.pushState(null, '', '#' + id);
  }, {passive:false});
})();
