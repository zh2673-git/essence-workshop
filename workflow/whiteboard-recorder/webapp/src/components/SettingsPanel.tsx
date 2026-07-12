import { X, Video, MousePointer, FileText, Settings, Hand } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import type { WebcamSettings, CursorSettings, GestureSettings, TeleprompterSettings, RecordingSettings, WebcamCameraLayout } from '../types';

export function SettingsPanel() {
  const {
    showSettings,
    activeSettingsTab,
    toggleSettings,
    webcam,
    cursor,
    gesture,
    teleprompter,
    recording,
    updateWebcamSettings,
    updateCursorSettings,
    updateGestureSettings,
    updateTeleprompterSettings,
    updateRecordingSettings,
  } = useAppStore();

  if (!showSettings) return null;

  const tabs = [
    { id: 'recording' as const, label: '录制', icon: Settings },
    { id: 'webcam' as const, label: '摄像头', icon: Video },
    { id: 'cursor' as const, label: '光标', icon: MousePointer },
    { id: 'gesture' as const, label: '手势', icon: Hand },
    { id: 'teleprompter' as const, label: '提词器', icon: FileText },
  ];

  const currentTab = activeSettingsTab || 'recording';

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-50 flex flex-col border-l">
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-bold text-gray-800">设置</h2>
        <button
          onClick={() => toggleSettings(null)}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      <div className="flex border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => toggleSettings(tab.id)}
            className={`flex-1 flex flex-col items-center gap-1 py-3 text-sm transition-colors ${
              currentTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            <tab.icon className="w-5 h-5" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-auto p-4">
        {currentTab === 'recording' && (
          <RecordingSettingsPanel
            settings={recording}
            onChange={updateRecordingSettings}
          />
        )}
        {currentTab === 'webcam' && (
          <WebcamSettingsPanel
            settings={webcam}
            onChange={updateWebcamSettings}
          />
        )}
        {currentTab === 'cursor' && (
          <CursorSettingsPanel
            settings={cursor}
            onChange={updateCursorSettings}
          />
        )}
        {currentTab === 'gesture' && (
          <GestureSettingsPanel
            settings={gesture}
            onChange={updateGestureSettings}
          />
        )}
        {currentTab === 'teleprompter' && (
          <TeleprompterSettingsPanel
            settings={teleprompter}
            onChange={updateTeleprompterSettings}
          />
        )}
      </div>
    </div>
  );
}

interface SettingSectionProps {
  title: string;
  children: React.ReactNode;
}

function SettingSection({ title, children }: SettingSectionProps) {
  return (
    <div className="mb-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

interface ToggleProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

function Toggle({ label, checked, onChange }: ToggleProps) {
  return (
    <label className="flex items-center justify-between cursor-pointer">
      <span className="text-gray-700">{label}</span>
      <div
        onClick={() => onChange(!checked)}
        className={`w-12 h-6 rounded-full relative transition-colors cursor-pointer ${
          checked ? 'bg-blue-600' : 'bg-gray-300'
        }`}
      >
        <div
          className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
            checked ? 'translate-x-7' : 'translate-x-1'
          }`}
        />
      </div>
    </label>
  );
}

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (value: number) => void;
}

function Slider({ label, value, min, max, step = 1, unit = '', onChange }: SliderProps) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-gray-700">{label}</span>
        <span className="text-gray-500">
          {value}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
      />
    </div>
  );
}

interface SelectProps<T extends string> {
  label: string;
  value: T;
  options: { value: T; label: string }[];
  onChange: (value: T) => void;
}

function Select<T extends string>({ label, value, options, onChange }: SelectProps<T>) {
  return (
    <div>
      <label className="block text-sm text-gray-700 mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

interface ColorPickerProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function ColorPicker({ label, value, onChange }: ColorPickerProps) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-700">{label}</span>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-10 h-10 rounded cursor-pointer border-0"
        />
        <span className="text-sm text-gray-500 font-mono">{value}</span>
      </div>
    </div>
  );
}

interface TextInputProps {
  label: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
}

function TextInput({ label, value, placeholder, onChange }: TextInputProps) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-gray-700 whitespace-nowrap">{label}</span>
      <input
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="w-32 px-3 py-2 text-center border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-400"
      />
    </div>
  );
}

interface RecordingSettingsPanelProps {
  settings: RecordingSettings;
  onChange: (settings: Partial<RecordingSettings>) => void;
}

function RecordingSettingsPanel({ settings, onChange }: RecordingSettingsPanelProps) {
  return (
    <div>
      <SettingSection title="录制模式">
        <Select
          label="模式"
          value={settings.mode}
          options={[
            { value: 'whiteboard', label: '白板讲解' },
            { value: 'camera', label: '摄像头口播' },
            { value: 'screen', label: '屏幕演示' },
          ]}
          onChange={(mode) => onChange({ mode })}
        />
        <p className="text-xs text-gray-500 -mt-2">
          摄像头口播模式下，摄像头画面会占满整个录制区域，适合自拍式讲解。
          屏幕演示模式下会弹出窗口选择器，录制选中的屏幕或窗口，摄像头以小窗叠加。
        </p>
        <Toggle
          label="录制完整界面"
          checked={settings.recordFullInterface}
          onChange={(recordFullInterface) => onChange({ recordFullInterface })}
        />
        <p className="text-xs text-gray-500 -mt-2">
          白板讲解模式下开启后，会录制整个浏览器标签页，包括工具栏、设置面板等完整操作过程。
        </p>
        <Toggle
          label="连续滚动所有字幕"
          checked={settings.continuousTeleprompter}
          onChange={(continuousTeleprompter) => onChange({ continuousTeleprompter })}
        />
        <p className="text-xs text-gray-500 -mt-2">
          开启后，所有场景的提词器脚本会合并成一份完整文稿连续滚动播放。
        </p>
      </SettingSection>

      <SettingSection title="视频质量">
        <Select
          label="分辨率"
          value={settings.resolution}
          options={[
            { value: 'auto', label: '自动 (推荐)' },
            { value: '4k', label: '4K (3840×2160)' },
            { value: '2k', label: '2K (2560×1440)' },
            { value: '1080p', label: '1080p (1920×1080)' },
            { value: '720p', label: '720p (1280×720)' },
          ]}
          onChange={(resolution) => onChange({ resolution })}
        />
        <p className="text-xs text-gray-500 -mt-2">
          自动模式下以 1080p 录制，摄像头会根据硬件能力自动匹配最佳采集分辨率。
        </p>
        <Select
          label="帧率"
          value={String(settings.framerate) as '30' | '60'}
          options={[
            { value: '30', label: '30 fps' },
            { value: '60', label: '60 fps' },
          ]}
          onChange={(fps) => onChange({ framerate: Number(fps) as 30 | 60 })}
        />
        <Slider
          label="倒计时"
          value={settings.countdownSeconds}
          min={0}
          max={10}
          unit="秒"
          onChange={(countdownSeconds) => onChange({ countdownSeconds })}
        />
      </SettingSection>
      <SettingSection title="音频">
        <Toggle
          label="录制麦克风"
          checked={settings.audioEnabled}
          onChange={(audioEnabled) => onChange({ audioEnabled })}
        />
      </SettingSection>
    </div>
  );
}

interface WebcamSettingsPanelProps {
  settings: WebcamSettings;
  onChange: (settings: Partial<WebcamSettings>) => void;
}

function WebcamSettingsPanel({ settings, onChange }: WebcamSettingsPanelProps) {
  return (
    <div>
      <SettingSection title="摄像头">
        <Toggle
          label="启用摄像头"
          checked={settings.enabled}
          onChange={(enabled) => onChange({ enabled })}
        />
        <Toggle
          label="镜像画面"
          checked={settings.mirror}
          onChange={(mirror) => onChange({ mirror })}
        />
        <Select<WebcamCameraLayout>
          label="口播布局"
          value={settings.cameraLayout}
          options={[
            { value: 'fullscreen', label: '全屏填充' },
            { value: '16:9', label: '16:9 宽屏' },
            { value: '9:16', label: '9:16 竖屏（手机）' },
            { value: '4:3', label: '4:3 标准' },
            { value: '1:1', label: '1:1 方形' },
          ]}
          onChange={(cameraLayout) => onChange({ cameraLayout })}
        />
        <p className="text-xs text-gray-500 -mt-2">
          仅在“摄像头口播”模式下生效。选择非全屏比例时，录制输出尺寸会按目标比例从全屏画面中中心裁剪，不放大不缩小。
        </p>
      </SettingSection>
      <SettingSection title="画面效果">
        <Select
          label="滤镜"
          value={settings.filter}
          options={[
            { value: 'none', label: '无' },
            { value: 'soften', label: '柔化美颜' },
            { value: 'grayscale', label: '黑白' },
          ]}
          onChange={(filter) => onChange({ filter })}
        />
        <Slider
          label="圆角"
          value={settings.borderRadius}
          min={0}
          max={120}
          unit="px"
          onChange={(borderRadius) => onChange({ borderRadius })}
        />
      </SettingSection>
      <SettingSection title="摄像头框尺寸">
        <Slider
          label="宽度"
          value={settings.bounds.width}
          min={120}
          max={800}
          step={10}
          unit="px"
          onChange={(width) => onChange({ bounds: { ...settings.bounds, width } })}
        />
        <Slider
          label="高度"
          value={settings.bounds.height}
          min={90}
          max={600}
          step={10}
          unit="px"
          onChange={(height) => onChange({ bounds: { ...settings.bounds, height } })}
        />
        <p className="text-xs text-gray-500 -mt-2">
          也可以直接在白板上拖动摄像头框调整位置。
        </p>
      </SettingSection>
    </div>
  );
}

interface CursorSettingsPanelProps {
  settings: CursorSettings;
  onChange: (settings: Partial<CursorSettings>) => void;
}

function CursorSettingsPanel({ settings, onChange }: CursorSettingsPanelProps) {
  return (
    <div>
      <SettingSection title="光标效果">
        <Toggle
          label="启用光标高亮"
          checked={settings.enabled}
          onChange={(enabled) => onChange({ enabled })}
        />
        <Toggle
          label="点击涟漪效果"
          checked={settings.showClickEffect}
          onChange={(showClickEffect) => onChange({ showClickEffect })}
        />
        <Slider
          label="光环大小"
          value={settings.size}
          min={10}
          max={60}
          unit="px"
          onChange={(size) => onChange({ size })}
        />
      </SettingSection>
      <SettingSection title="颜色">
        <ColorPicker
          label="光环颜色"
          value={settings.color}
          onChange={(color) => onChange({ color })}
        />
        <ColorPicker
          label="点击效果颜色"
          value={settings.clickEffectColor}
          onChange={(clickEffectColor) => onChange({ clickEffectColor })}
        />
      </SettingSection>
    </div>
  );
}

interface GestureSettingsPanelProps {
  settings: GestureSettings;
  onChange: (settings: Partial<GestureSettings>) => void;
}

function GestureSettingsPanel({ settings, onChange }: GestureSettingsPanelProps) {
  return (
    <div>
      <SettingSection title="手势控制">
        <Toggle
          label="启用手势控制"
          checked={settings.enabled}
          onChange={(enabled) => onChange({ enabled })}
        />
        <p className="text-xs text-gray-500 -mt-2 mb-2">
          开启后会自动启用摄像头，用食指指尖控制光标位置。
        </p>
        <Toggle
          label="镜像X轴"
          checked={settings.mirror}
          onChange={(mirror) => onChange({ mirror })}
        />
      </SettingSection>
      <SettingSection title="光标外观">
        <TextInput
          label="光标图案"
          value={settings.icon}
          placeholder="🚀"
          onChange={(icon) => onChange({ icon })}
        />
        <div className="flex flex-wrap gap-2 -mt-1">
          {['🚀', '👆', '✨', '🔴', '🎯', '👁️', '🐦', '⚡'].map((emoji) => (
            <button
              key={emoji}
              onClick={() => onChange({ icon: emoji })}
              className={`w-9 h-9 text-lg rounded-lg border transition-colors ${
                settings.icon === emoji
                  ? 'border-cyan-400 bg-cyan-50'
                  : 'border-gray-200 hover:bg-gray-50'
              }`}
            >
              {emoji}
            </button>
          ))}
        </div>
        <Slider
          label="光标大小"
          value={settings.size}
          min={10}
          max={60}
          unit="px"
          onChange={(size) => onChange({ size })}
        />
        <ColorPicker
          label="光标颜色"
          value={settings.color}
          onChange={(color) => onChange({ color })}
        />
      </SettingSection>
    </div>
  );
}

interface TeleprompterSettingsPanelProps {
  settings: TeleprompterSettings;
  onChange: (settings: Partial<TeleprompterSettings>) => void;
}

function TeleprompterSettingsPanel({ settings, onChange }: TeleprompterSettingsPanelProps) {
  return (
    <div>
      <SettingSection title="提词器">
        <Toggle
          label="启用提词器"
          checked={settings.enabled}
          onChange={(enabled) => onChange({ enabled })}
        />
        <Select
          label="位置"
          value={settings.position}
          options={[
            { value: 'top', label: '顶部' },
            { value: 'bottom', label: '底部' },
            { value: 'left', label: '左侧' },
            { value: 'right', label: '右侧' },
            { value: 'center', label: '居中（适合口播）' },
          ]}
          onChange={(position) => onChange({ position })}
        />
        <Slider
          label="字体大小"
          value={settings.fontSize}
          min={16}
          max={48}
          unit="px"
          onChange={(fontSize) => onChange({ fontSize })}
        />
        <Slider
          label="滚动速度"
          value={settings.speed}
          min={20}
          max={200}
          unit="px/s"
          onChange={(speed) => onChange({ speed })}
        />
        <Slider
          label="透明度"
          value={Math.round(settings.opacity * 100)}
          min={30}
          max={90}
          unit="%"
          onChange={(value) => onChange({ opacity: value / 100 })}
        />
      </SettingSection>
      <SettingSection title="文稿">
        <textarea
          value={settings.text}
          onChange={(e) => onChange({ text: e.target.value })}
          placeholder="在此粘贴你的讲稿..."
          className="w-full h-40 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-gray-700"
        />
      </SettingSection>
    </div>
  );
}
