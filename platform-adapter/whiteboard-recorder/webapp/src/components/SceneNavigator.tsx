import React from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, List } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { sceneManager } from '../modules/SceneManager';

export const SceneNavigator: React.FC = () => {
  const {
    whiteboardProject,
    currentSceneIndex,
    setCurrentSceneIndex,
    setSceneTeleprompter,
    showSceneNavigator,
    toggleSceneNavigator,
  } = useAppStore();

  if (!whiteboardProject) {
    return null;
  }

  const totalScenes = whiteboardProject.scenes.length;

  const goToScene = (index: number) => {
    if (sceneManager.goToScene(index)) {
      setCurrentSceneIndex(index);
      const scene = whiteboardProject.scenes[index];
      if (scene) {
        setSceneTeleprompter(scene);
      }
    }
  };

  const goPrev = () => {
    if (currentSceneIndex > 0) {
      goToScene(currentSceneIndex - 1);
    }
  };

  const goNext = () => {
    if (currentSceneIndex < totalScenes - 1) {
      goToScene(currentSceneIndex + 1);
    }
  };

  const goFirst = () => goToScene(0);
  const goLast = () => goToScene(totalScenes - 1);

  return (
    <>
      {showSceneNavigator && (
        <div className="fixed left-4 top-1/2 -translate-y-1/2 z-40 flex flex-col gap-2">
          <div className="bg-gray-900/90 backdrop-blur-md rounded-xl p-3 border border-gray-700 shadow-2xl w-48">
            <div className="text-white text-xs font-medium mb-3 flex items-center justify-between">
              <span>场景导航</span>
              <span className="text-gray-400">
                {currentSceneIndex + 1}/{totalScenes}
              </span>
            </div>

            <div className="flex gap-1 mb-3">
              <button
                onClick={goFirst}
                disabled={currentSceneIndex === 0}
                className="flex-1 p-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="第一页"
              >
                <ChevronsLeft size={14} className="mx-auto" />
              </button>
              <button
                onClick={goPrev}
                disabled={currentSceneIndex === 0}
                className="flex-1 p-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="上一页"
              >
                <ChevronLeft size={14} className="mx-auto" />
              </button>
              <button
                onClick={goNext}
                disabled={currentSceneIndex === totalScenes - 1}
                className="flex-1 p-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="下一页"
              >
                <ChevronRight size={14} className="mx-auto" />
              </button>
              <button
                onClick={goLast}
                disabled={currentSceneIndex === totalScenes - 1}
                className="flex-1 p-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                title="最后一页"
              >
                <ChevronsRight size={14} className="mx-auto" />
              </button>
            </div>

            <div className="space-y-1.5 max-h-96 overflow-y-auto pr-1 custom-scrollbar">
              {whiteboardProject.scenes.map((scene, index) => (
                <button
                  key={index}
                  onClick={() => goToScene(index)}
                  className={`w-full text-left p-2 rounded-lg text-xs transition-all ${
                    index === currentSceneIndex
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'bg-gray-800/50 text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <div className="font-medium truncate">
                    {index + 1}. {scene.title}
                  </div>
                  <div className={`text-xs mt-0.5 ${
                    index === currentSceneIndex ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    ~{scene.duration_estimate ? Math.round(scene.duration_estimate / 60 * 10) / 10 : '内容'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <button
        onClick={toggleSceneNavigator}
        className={`fixed left-4 top-20 z-40 p-2 rounded-lg backdrop-blur-sm border transition-colors ${
          showSceneNavigator
            ? 'bg-blue-600 border-blue-500 text-white'
            : 'bg-gray-800/80 border-gray-700 text-gray-300 hover:bg-gray-700 hover:text-white'
        }`}
        title="场景列表"
      >
        <List size={18} />
      </button>
    </>
  );
};
