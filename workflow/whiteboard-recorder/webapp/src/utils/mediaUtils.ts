export function getSupportedMimeType(): string {
  const types = [
    'video/mp4;codecs=h264,aac',
    'video/mp4',
    'video/webm;codecs=vp9,opus',
    'video/webm;codecs=vp8,opus',
    'video/webm',
  ];
  
  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  
  return '';
}

export function getFileExtension(mimeType: string): string {
  if (mimeType.includes('mp4')) return 'mp4';
  if (mimeType.includes('webm')) return 'webm';
  return 'webm';
}

export function generateFilename(mimeType: string): string {
  const now = new Date();
  const timestamp = now.getFullYear().toString() +
    (now.getMonth() + 1).toString().padStart(2, '0') +
    now.getDate().toString().padStart(2, '0') + '-' +
    now.getHours().toString().padStart(2, '0') +
    now.getMinutes().toString().padStart(2, '0') +
    now.getSeconds().toString().padStart(2, '0');
  const ext = getFileExtension(mimeType);
  return `whiteboard-capture-${timestamp}.${ext}`;
}

export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}

export function createRecordingStream(
  canvas: HTMLCanvasElement,
  audioStream: MediaStream | null,
  fps: number
): MediaStream {
  const videoStream = canvas.captureStream(fps);
  const combinedStream = new MediaStream();
  
  videoStream.getVideoTracks().forEach(track => {
    combinedStream.addTrack(track);
  });
  
  if (audioStream) {
    audioStream.getAudioTracks().forEach(track => {
      combinedStream.addTrack(track);
    });
  }
  
  return combinedStream;
}
