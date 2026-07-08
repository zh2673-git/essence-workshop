import { useEffect, useState } from 'react';

interface WorkItem {
  id: string;
  title: string;
  folder: string;
  updatedAt: string;
}

interface WorkSelectorProps {
  onSelect: (workId: string) => void;
}

export function WorkSelector({ onSelect }: WorkSelectorProps) {
  const [works, setWorks] = useState<WorkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/works/list')
      .then(res => res.json())
      .then(data => {
        setWorks(data.works || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err instanceof Error ? err.message : '加载作品列表失败');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-white/90 z-50 flex items-center justify-center">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <span className="text-gray-700 font-medium">正在扫描作品...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-white/90 z-50 flex items-center justify-center">
        <div className="bg-white rounded-xl shadow-xl p-8 max-w-md">
          <h2 className="text-xl font-bold text-red-600 mb-2">加载失败</h2>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-gray-100 z-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-2xl mx-4">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">🎨</span>
          <h1 className="text-2xl font-bold text-gray-800">WhiteboardCaster</h1>
        </div>
        <p className="text-gray-500 mb-6">请选择一个作品加载到白板</p>

        {works.length === 0 ? (
          <div className="bg-gray-50 rounded-xl p-8 text-center">
            <p className="text-gray-600 mb-2">暂无作品</p>
            <p className="text-sm text-gray-400">
              在 whiteboard-recorder/output/ 下创建作品文件夹并放入 .whiteboard.json 文件后即可选择
            </p>
          </div>
        ) : (
          <div className="grid gap-3">
            {works.map(work => (
              <button
                key={work.id}
                onClick={() => onSelect(work.id)}
                className="text-left bg-white border border-gray-200 rounded-xl p-4 hover:border-blue-400 hover:shadow-md transition-all group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">
                      {work.title}
                    </h3>
                    <p className="text-sm text-gray-400 mt-1">{work.folder}</p>
                  </div>
                  <span className="text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
                    加载 →
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}

        <div className="mt-6 pt-4 border-t border-gray-100 text-xs text-gray-400">
          作品目录：whiteboard-recorder/output/作品名/作品名.whiteboard.json
        </div>
      </div>
    </div>
  );
}
