function knowledgeGraphInit(container) {
  const svg = container.querySelector('.kg-svg');
  const nodesGroup = svg.querySelector('.kg-nodes');
  const edgesGroup = svg.querySelector('.kg-edges');
  const detail = container.querySelector('.kg-detail');
  const detailName = container.querySelector('.kg-detail-name');
  const detailBody = container.querySelector('.kg-detail-body');
  const detailClose = container.querySelector('.kg-detail-close');
  let scale = 1;

  container.querySelector('.kg-zoom-in').addEventListener('click', () => {
    scale = Math.min(3, scale * 1.2);
    svg.querySelector('g').setAttribute('transform', 'scale(' + scale + ')');
  });
  container.querySelector('.kg-zoom-out').addEventListener('click', () => {
    scale = Math.max(0.3, scale / 1.2);
    svg.querySelector('g').setAttribute('transform', 'scale(' + scale + ')');
  });
  container.querySelector('.kg-reset').addEventListener('click', () => {
    scale = 1;
    svg.querySelector('g').setAttribute('transform', 'scale(1)');
  });
  detailClose.addEventListener('click', () => { detail.style.display = 'none'; });

  function showNodeDetail(name, description) {
    detailName.textContent = name;
    detailBody.textContent = description || '';
    detail.style.display = 'block';
  }

  nodesGroup.addEventListener('click', (e) => {
    const node = e.target.closest('.kg-node');
    if (node) showNodeDetail(node.dataset.name, node.dataset.desc);
  });
}
