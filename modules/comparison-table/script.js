function comparisonTableInit(container) {
  const btns = container.querySelectorAll('.ct-btn');
  const views = container.querySelectorAll('.ct-view');

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      const view = btn.dataset.view;
      btns.forEach(b => b.classList.toggle('active', b.dataset.view === view));
      views.forEach(v => v.classList.toggle('active', v.classList.contains('ct-view-' + view)));
    });
  });
}
