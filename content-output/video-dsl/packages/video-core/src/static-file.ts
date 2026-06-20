import type { AssetRegistry } from './types.js';

const assetRegistry: AssetRegistry = {
  images: new Set(),
  audio: new Set(),
  video: new Set(),
};

export function staticFile(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase();
  if (['png', 'jpg', 'jpeg', 'svg', 'gif', 'webp'].includes(ext ?? '')) {
    assetRegistry.images.add(path);
  } else if (['mp3', 'wav', 'aac', 'ogg'].includes(ext ?? '')) {
    assetRegistry.audio.add(path);
  } else if (['mp4', 'mov', 'webm'].includes(ext ?? '')) {
    assetRegistry.video.add(path);
  }
  return path;
}

export function getAssetRegistry(): AssetRegistry {
  return {
    images: new Set(assetRegistry.images),
    audio: new Set(assetRegistry.audio),
    video: new Set(assetRegistry.video),
  };
}

export function clearAssetRegistry(): void {
  assetRegistry.images.clear();
  assetRegistry.audio.clear();
  assetRegistry.video.clear();
}
