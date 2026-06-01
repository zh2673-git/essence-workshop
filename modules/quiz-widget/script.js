function selectQuizOption(option) {
  var options = option.parentElement.querySelectorAll('.quiz-widget-option');
  options.forEach(function(opt) {
    opt.classList.remove('selected-correct', 'selected-wrong');
  });

  var isCorrect = option.getAttribute('data-correct') === 'true';
  var feedback = document.getElementById('quizFeedback');

  if (isCorrect) {
    option.classList.add('selected-correct');
    feedback.className = 'quiz-widget-feedback correct';
    feedback.textContent = '正确！三层架构（元素层→管线层→平台层）是本质工坊的核心设计原则。';
  } else {
    option.classList.add('selected-wrong');
    feedback.className = 'quiz-widget-feedback wrong';
    feedback.textContent = '不对哦，再想想看。提示：本质工坊的设计思路是分层解耦。';
  }
}
