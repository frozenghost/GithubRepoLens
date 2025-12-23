import type { AnalysisEvent } from "@/types/api";

export type AnalysisEventHandler = (event: AnalysisEvent) => void;

export async function parseSSEResponse(
  response: Response,
  onEvent: AnalysisEventHandler,
  signal?: AbortSignal
) {
  if (!response.body) {
    throw new Error("No response body");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      if (signal?.aborted) {
        break;
      }

      const { done, value } = await reader.read();
      
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (trimmedLine.startsWith("data: ")) {
          try {
            const jsonStr = trimmedLine.slice(6);
            const event: AnalysisEvent = JSON.parse(jsonStr);
            onEvent(event);
          } catch (e) {
            console.error("Failed to parse SSE event:", e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

