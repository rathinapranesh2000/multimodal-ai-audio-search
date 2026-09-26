import type { Conversation, IngestStatus, SearchMode, SearchResponse } from "./types";

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string };
    return body.detail || response.statusText;
  } catch {
    return response.statusText;
  }
}

export async function uploadAudio(file: File): Promise<{ file_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch("/api/ingest", { method: "POST", body: form });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json() as Promise<{ file_id: string }>;
}

export async function ingestStatus(fileId: string): Promise<IngestStatus> {
  const response = await fetch(`/api/ingest/${fileId}/status`);
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json() as Promise<IngestStatus>;
}

export async function deleteConversation(fileId: string): Promise<void> {
  const response = await fetch(`/api/conversations/${fileId}`, { method: "DELETE" });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
}

export async function listConversations(): Promise<Conversation[]> {
  const response = await fetch("/api/conversations");
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json() as Promise<Conversation[]>;
}

export async function searchAudio(query: string, mode: SearchMode): Promise<SearchResponse> {
  const response = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, mode }),
  });
  if (!response.ok) {
    throw new Error(await readError(response));
  }
  return response.json() as Promise<SearchResponse>;
}

export function audioUrl(fileId: string): string {
  return `/api/audio/${fileId}`;
}
