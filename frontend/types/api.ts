export type EventType = "start" | "token" | "tool_call" | "tool_result" | "complete" | "error";

export interface AnalysisEvent {
  type: EventType;
  data: AnalysisEventData;
  timestamp: string;
}

export interface AnalysisEventData {
  content?: string;
  message?: string;
  tool?: string;
  repo_url?: string;
  status?: string;
  error?: string;
}

export interface ToolCallEvent {
  message: string;
  tool: string;
  timestamp: string;
}

export interface AnalyzeRequest {
  repo_url: string;
  language: string;
  llm_provider?: "openai" | "gemini" | "openrouter";
  llm_model?: string;
}

export interface AnalysisState {
  output: string;
  toolCalls: ToolCallEvent[];
  isAnalyzing: boolean;
  error: string | null;
}

