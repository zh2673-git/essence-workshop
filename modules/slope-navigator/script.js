function slopeNavigatorInit(container) {
  const levels = container.querySelectorAll('.slope-level');
  const btns = container.querySelectorAll('.slope-btn');
  const prevBtn = container.querySelector('.slope-prev');
  const nextBtn = container.querySelector('.slope-next');
  const progress = container.querySelector('.slope-progress');
  let current = 1;
  const total = levels.length;

  function showLevel(n) {
    current = Math.max(1, Math.min(total, n));
    levels.forEach(l => l.classList.toggle('active', parseInt(l.dataset.level) === current));
    btns.forEach(b => b.classList.toggle('active', parseInt(b.dataset.level) === current));
    prevBtn.disabled = current === 1;
    nextBtn.disabled = current === total;
    progress.textContent = current + ' / ' + total;
  }

  btns.forEach(btn => btn.addEventListener('click', () => showLevel(parseInt(btn.dataset.level))));
  prevBtn.addEventListener('click', () => showLevel(current - 1));
  nextBtn.addEventListener('click', () => showLevel(current + 1));
}
