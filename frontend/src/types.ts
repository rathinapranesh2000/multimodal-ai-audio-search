export type StageMap = Record<string, string>;

export type IngestStatus = {
  file_id: string;
  filename: string;
  status: string;
  stage: string;
  progress: StageMap;
  timings: Record<string, number>;
  error: string | null;
  duration_seconds: number | null;
  chunk_count: number;
};

export type Conversation = {
  file_id: string;
  filename: string;
  status: string;
  stage: string;
  duration_seconds: number | null;
  chunk_count: number;
  created_at: string;
};

export type SearchHit = {
  file_id: string;
  file: string;
  speaker: string;
  start_ts: number;
  end_ts: number;
  snippet: string;
  cited: boolean;
  why: string;
};

export type Citation = {
  file_id: string;
  file: string;
  speaker: string;
  start_ts: number;
  end_ts: number;
};

export type SearchResponse = {
  query: string;
  answer: string;
  citations: Citation[];
  results: SearchHit[];
  fallback: string | null;
  query_truncated: boolean;
  injection_stripped: boolean;
  speaker_filter: string | null;
  mode: string;
  trace_id: string;
  elapsed_ms: number;
};

export type SearchMode = "hybrid" | "hybrid_rrf" | "lexical" | "semantic";
