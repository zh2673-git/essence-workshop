function toggleMentorCard(card) {
  card.classList.toggle('active');
  var detail = card.nextElementSibling;
  detail.classList.toggle('open');
}
