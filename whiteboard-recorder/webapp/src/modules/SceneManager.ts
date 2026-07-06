import type { ExcalidrawImperativeAPI } from '@excalidraw/excalidraw/types/types';
import type { WhiteboardProject, WhiteboardScene } from '../types';

const normalizeElement = (el: any, _index: number): any => {
  return {
    ...el,
    version: el.version || 1,
    versionNonce: el.versionNonce || Math.floor(Math.random() * 1000000),
    isDeleted: el.isDeleted || false,
    boundElements: el.boundElements || null,
    updated: el.updated || Date.now(),
    link: el.link || null,
    locked: el.locked || false,
    seed: el.seed || Math.floor(Math.random() * 1000000),
    groupIds: el.groupIds || [],
    frameId: el.frameId || null,
    roundness: el.roundness || (el.type === 'rectangle' || el.type === 'ellipse' ? { type: 3 } : null),
  };
};

const calculateSceneViewport = (scene: WhiteboardScene, _sceneIndex: number): { x: number; y: number; zoom: number } => {
  if (scene.viewport) {
    return scene.viewport;
  }
  
  const elements = scene.elements;
  if (!elements || elements.length === 0) {
    return { x: scene.scene_x ?? 0, y: 400, zoom: 1 };
  }

  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  elements.forEach((el: any) => {
    minX = Math.min(minX, el.x);
    minY = Math.min(minY, el.y);
    maxX = Math.max(maxX, el.x + el.width);
    maxY = Math.max(maxY, el.y + el.height);
  });

  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;

  return {
    x: centerX,
    y: centerY,
    zoom: 0.9
  };
};

export class SceneManager {
  private excalidrawAPI: ExcalidrawImperativeAPI | null = null;
  private project: WhiteboardProject | null = null;
  private currentSceneIndex: number = 0;

  setExcalidrawAPI(api: ExcalidrawImperativeAPI | null) {
    this.excalidrawAPI = api;
  }

  loadProject(project: WhiteboardProject) {
    this.project = {
      ...project,
      total_scenes: project.scenes.length,
      scenes: project.scenes.map((scene, idx) => ({
        ...scene,
        elements: scene.elements.map((el, elIdx) => normalizeElement(el, elIdx)),
        viewport: calculateSceneViewport(scene, idx)
      }))
    };
    this.currentSceneIndex = 0;
    if (this.excalidrawAPI && this.project.scenes.length > 0) {
      const allElements = this.project.scenes.flatMap(s => s.elements) as any;
      this.excalidrawAPI.updateScene({ elements: allElements });
      setTimeout(() => this.goToScene(0, false), 100);
    }
  }

  getCurrentScene(): WhiteboardScene | null {
    if (!this.project) return null;
    return this.project.scenes[this.currentSceneIndex] || null;
  }

  getProject(): WhiteboardProject | null {
    return this.project;
  }

  getCurrentIndex(): number {
    return this.currentSceneIndex;
  }

  getTotalScenes(): number {
    return this.project?.total_scenes || 0;
  }

  getAllScenes(): WhiteboardScene[] {
    return this.project?.scenes || [];
  }

  goToScene(index: number, animate: boolean = true): boolean {
    if (!this.project || !this.excalidrawAPI) return false;
    if (index < 0 || index >= this.project.scenes.length) return false;

    const scene = this.project.scenes[index];
    this.currentSceneIndex = index;

    if (animate) {
      this.excalidrawAPI.scrollToContent(scene.elements as any, {
        fitToContent: true,
        animate: true,
        duration: 800
      });
    } else {
      this.excalidrawAPI.scrollToContent(scene.elements as any, {
        fitToContent: true,
        animate: false
      });
    }

    return true;
  }

  nextScene(animate: boolean = true): boolean {
    return this.goToScene(this.currentSceneIndex + 1, animate);
  }

  prevScene(animate: boolean = true): boolean {
    return this.goToScene(this.currentSceneIndex - 1, animate);
  }

  goToFirstScene(animate: boolean = true): boolean {
    return this.goToScene(0, animate);
  }

  goToLastScene(animate: boolean = true): boolean {
    if (!this.project) return false;
    return this.goToScene(this.project.scenes.length - 1, animate);
  }

  reset() {
    this.project = null;
    this.currentSceneIndex = 0;
    if (this.excalidrawAPI) {
      this.excalidrawAPI.updateScene({ elements: [] });
    }
  }
}

export const sceneManager = new SceneManager();
