function threeStageProgressInit(container) {
  const steps = container.querySelectorAll('.tsp-step');
  const panels = container.querySelectorAll('.tsp-panel');
  let current = 1;

  function showStep(n) {
    current = n;
    steps.forEach(s => {
      const step = parseInt(s.dataset.step);
      s.classList.toggle('active', step === n);
      s.classList.toggle('completed', step < n);
    });
    panels.forEach(p => p.classList.toggle('active', parseInt(p.dataset.step) === n));
  }

  steps.forEach(s => s.addEventListener('click', () => showStep(parseInt(s.dataset.step))));
}
