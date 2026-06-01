function toggleAICompanion() {
  var panel = document.getElementById('aiCompanionPanel');
  panel.classList.toggle('open');
}

function sendAICompanionMsg() {
  var input = document.getElementById('aiCompanionInput');
  var msg = input.value.trim();
  if (!msg) return;

  var messages = document.getElementById('aiCompanionMessages');
  var userDiv = document.createElement('div');
  userDiv.className = 'ai-msg ai-msg-user';
  userDiv.textContent = msg;
  messages.appendChild(userDiv);

  input.value = '';

  setTimeout(function() {
    var sysDiv = document.createElement('div');
    sysDiv.className = 'ai-msg ai-msg-system';
    sysDiv.textContent = '这是一个前端演示模块。在实际使用中，这里会连接AI后端来回答你的问题。';
    messages.appendChild(sysDiv);
    messages.scrollTop = messages.scrollHeight;
  }, 500);

  messages.scrollTop = messages.scrollHeight;
}
