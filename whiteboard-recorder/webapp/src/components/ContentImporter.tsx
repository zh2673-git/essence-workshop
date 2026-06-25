import React, { useRef, useState } from 'react';
import { Upload, Link2, X, Loader2 } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { sceneManager } from '../modules/SceneManager';
import type { WhiteboardProject } from '../types';

export const ContentImporter: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [url, setUrl] = useState('');
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { loadWhiteboardProject, whiteboardProject, clearWhiteboardProject } = useAppStore();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    setError(null);

    try {
      const text = await file.text();
      const project: WhiteboardProject = JSON.parse(text);
      
      if (!project.version || !project.scenes || !Array.isArray(project.scenes)) {
        throw new Error('无效的白板项目文件格式');
      }

      loadWhiteboardProject(project);
      sceneManager.loadProject(project);
      
      if (project.scenes.length > 0) {
        useAppStore.getState().setSceneTeleprompter(project.scenes[0]);
        useAppStore.getState().setCurrentSceneIndex(0);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '导入失败，请检查文件格式');
      console.error('Import error:', err);
    } finally {
      setIsImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleUrlImport = async () => {
    if (!url.trim()) {
      setError('请输入有效的URL');
      return;
    }
    setError('请先运行Python脚本生成白板项目文件，再导入生成的JSON文件');
    setUrl('');
    setShowUrlInput(false);
  };

  return (
    <div className="relative">
      {whiteboardProject ? (
        <button
          onClick={clearWhiteboardProject}
          className="flex items-center gap-2 px-3 py-2 bg-gray-800/80 hover:bg-red-600/80 text-white rounded-lg transition-colors text-sm backdrop-blur-sm border border-gray-700"
          title="清除已加载项目"
        >
          <X size={16} />
          <span>清除</span>
        </button>
      ) : (
        <>
          <input
            ref={fileInputRef}
            type="file"
            accept=".whiteboard.json,.json"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {showUrlInput ? (
            <div className="flex items-center gap-2 bg-gray-800/90 rounded-lg p-2 backdrop-blur-sm border border-gray-700">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="输入公众号文章URL..."
                className="bg-transparent text-white text-sm px-2 py-1 outline-none w-64 placeholder:text-gray-500"
                onKeyDown={(e) => e.key === 'Enter' && handleUrlImport()}
              />
              <button
                onClick={handleUrlImport}
                disabled={isImporting}
                className="p-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded transition-colors disabled:opacity-50"
              >
                {isImporting ? <Loader2 size={14} className="animate-spin" /> : <Link2 size={14} />}
              </button>
              <button
                onClick={() => setShowUrlInput(false)}
                className="p-1.5 text-gray-400 hover:text-white transition-colors"
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-1">
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isImporting}
                className="flex items-center gap-2 px-3 py-2 bg-gray-800/80 hover:bg-gray-700/80 text-white rounded-lg transition-colors text-sm backdrop-blur-sm border border-gray-700 disabled:opacity-50"
                title="导入白板项目文件"
              >
                {isImporting ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <Upload size={16} />
                )}
                <span>导入</span>
              </button>
            </div>
          )}
        </>
      )}

      {error && (
        <div className="absolute top-full mt-2 left-0 bg-red-900/90 text-red-200 text-xs px-3 py-2 rounded-lg backdrop-blur-sm max-w-xs z-50">
          {error}
        </div>
      )}
    </div>
  );
};
