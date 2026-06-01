function cardFlipInit(container) {
  const card = container.querySelector('.cf-card');
  card.addEventListener('click', () => card.classList.toggle('flipped'));
}
