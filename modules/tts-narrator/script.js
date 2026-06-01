var ttsPlaying = false;
var ttsProgress = 0;
var ttsTimer = null;

function toggleTTS() {
  ttsPlaying = !ttsPlaying;
  var btn = document.getElementById('ttsPlayBtn');
  if (ttsPlaying) {
    btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>';
    ttsTimer = setInterval(function() {
      ttsProgress += 0.5;
      if (ttsProgress >= 100) {
        ttsProgress = 0;
        toggleTTS();
        return;
      }
      document.getElementById('ttsProgressFill').style.width = ttsProgress + '%';
      var totalSec = Math.round(ttsProgress * 1.8);
      var min = Math.floor(totalSec / 60);
      var sec = totalSec % 60;
      document.getElementById('ttsTimeDisplay').textContent = min + ':' + (sec < 10 ? '0' : '') + sec;
    }, 300);
  } else {
    btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>';
    clearInterval(ttsTimer);
  }
}

function updateTTSSpeed() {
  var val = document.getElementById('ttsSpeedRange').value;
  document.getElementById('ttsSpeedValue').textContent = parseFloat(val).toFixed(1) + 'x';
}
