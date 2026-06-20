export interface VideoGenerationSpec {
  title: string;
  aspectRatio: '9:16' | '16:9' | '1:1';
  durationSeconds: number;
  fps: number;
  style?: string;
  sections: VideoSection[];
  assets?: {
    bgm?: string;
    images?: string[];
    videos?: string[];
  };
}

export interface VideoSection {
  type: 'title' | 'scene' | 'summary' | 'stat' | 'compare' | 'timeline';
  heading?: string;
  subheading?: string;
  content?: string;
  visualHint?: string;
  durationFrames: number;
  narration?: string;
  data?: Record<string, unknown>;
}

export interface GenerationResult {
  videoProgramPath: string;
  manifestPath: string;
  specPath: string;
  assets: string[];
}

export interface ValidationReport {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

export interface AgentClient {
  generateCode: (prompt: string) => Promise<string>;
}

export interface GenerateOptions {
  spec: VideoGenerationSpec;
  outputDir: string;
  agentClient: AgentClient;
  promptTemplate?: string;
  maxRetries?: number;
}
