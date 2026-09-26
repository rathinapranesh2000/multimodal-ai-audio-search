import { useEffect, useRef, useState, type FormEvent } from "react";
import { audioUrl, deleteConversation, ingestStatus, listConversations, searchAudio, uploadAudio } from "./api";
import { createPlayerController } from "./playback";
import type { Conversation, IngestStatus, SearchHit, SearchMode, SearchResponse } from "./types";

const STAGES = ["normalizing", "diarizing", "transcribing", "aligning", "chunking", "indexing", "done"];

function clock(seconds: number): string {
  const whole = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(whole / 60);
  const remain = whole % 60;
  return `${minutes}:${remain.toString().padStart(2, "0")}`;
}

export function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [status, setStatus] = useState<IngestStatus | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<SearchMode>("hybrid");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const playerRef = useRef<ReturnType<typeof createPlayerController> | null>(null);
  const [activeFile, setActiveFile] = useState("");

  async function refreshLibrary() {
    try {
      setConversations(await listConversations());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load recordings");
    }
  }

  useEffect(() => {
    void refreshLibrary();
  }, []);

  useEffect(() => {
    if (!status || status.status !== "processing") {
      return;
    }
    const timer = window.setInterval(async () => {
      try {
        const next = await ingestStatus(status.file_id);
        setStatus(next);
        if (next.status !== "processing") {
          window.clearInterval(timer);
          await refreshLibrary();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Status check failed");
      }
    }, 1500);
    return () => window.clearInterval(timer);
  }, [status?.file_id, status?.status]);

  async function onUpload(file: File | undefined) {
    if (!file) {
      return;
    }
    setError("");
    setNotice("");
    try {
      const accepted = await uploadAudio(file);
      const next = await ingestStatus(accepted.file_id);
      setStatus(next);
      setNotice(`${file.name} is processing.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    }
  }

  async function onRemove(item: Conversation) {
    if (!window.confirm(`Remove ${item.filename}?`)) {
      return;
    }
    setError("");
    try {
      await deleteConversation(item.file_id);
      if (status?.file_id === item.file_id) {
        setStatus(null);
      }
      if (activeFile === item.file_id && audioRef.current) {
        audioRef.current.pause();
        audioRef.current.removeAttribute("src");
        playerRef.current = null;
        setActiveFile("");
      }
      await refreshLibrary();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not remove the recording");
    }
  }

  async function onSearch(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      setResult(await searchAudio(query, mode));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setBusy(false);
    }
  }

  function play(hit: SearchHit) {
    const element = audioRef.current;
    if (!element) {
      return;
    }
    if (!playerRef.current) {
      playerRef.current = createPlayerController(element);
    }
    setActiveFile(hit.file_id);
    setError("");
    void playerRef.current
      .play({ fileId: hit.file_id, startTs: hit.start_ts, url: audioUrl(hit.file_id) })
      .catch((err: unknown) => {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setError(err instanceof Error ? err.message : "Could not play this recording");
      });
  }

  return (
    <div className="page">
      <header className="top">
        <div>
          <p className="eyebrow">Hybrid audio search</p>
          <h1>AudioRAG</h1>
        </div>
        <p className="lede">
          Keyword and meaning search over two-speaker recordings, with the file, speaker, and timestamp attached to every hit.
        </p>
      </header>

      <section className="panel">
        <h2>Recordings</h2>
        <label className="upload">
          <input
            type="file"
            accept="audio/*,.wav,.mp3,.m4a,.flac,.ogg"
            onChange={(event) => void onUpload(event.target.files?.[0])}
          />
          <span>Upload a two-speaker recording</span>
        </label>
        {status ? <StageList status={status} /> : null}
        <ul className="library">
          {conversations.map((item) => (
            <li key={item.file_id}>
              <div>
                <strong>{item.filename}</strong>
                <span>
                  {item.status}
                  {item.chunk_count ? ` · ${item.chunk_count} chunks` : ""}
                  {item.duration_seconds ? ` · ${clock(item.duration_seconds)}` : ""}
                </span>
              </div>
              <button type="button" className="remove" onClick={() => void onRemove(item)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section className="panel">
        <h2>Search</h2>
        <form onSubmit={(event) => void onSearch(event)} className="search">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="What did Speaker 01 say about the cutover?"
            aria-label="Search query"
          />
          <select value={mode} onChange={(event) => setMode(event.target.value as SearchMode)} aria-label="Retrieval mode">
            <option value="hybrid">Hybrid + rerank</option>
            <option value="hybrid_rrf">Hybrid / RRF</option>
            <option value="lexical">Lexical only</option>
            <option value="semantic">Semantic only</option>
          </select>
          <button type="submit" disabled={busy}>
            {busy ? "Searching" : "Search"}
          </button>
        </form>
        {notice ? <p className="notice">{notice}</p> : null}
        {error ? <p className="error">{error}</p> : null}
        {result ? (
          <article className="answer">
            <h3>Answer</h3>
            <p>{result.answer}</p>
            <p className="meta">
              {result.mode}
              {result.speaker_filter ? ` · ${result.speaker_filter}` : ""}
              {result.fallback ? ` · fallback ${result.fallback}` : ""}
              {` · ${result.elapsed_ms} ms · ${result.trace_id}`}
            </p>
            <h3>Evidence</h3>
            <ul className="hits">
              {result.results.map((hit) => (
                <li key={`${hit.file_id}-${hit.start_ts}-${hit.snippet.slice(0, 24)}`}>
                  <div className="hit-head">
                    <strong>{hit.file}</strong>
                    <span>
                      {hit.speaker} · {clock(hit.start_ts)}–{clock(hit.end_ts)}
                      {hit.cited ? " · cited" : ""}
                    </span>
                  </div>
                  <p>{hit.snippet}</p>
                  <p className="why">{hit.why}</p>
                  <button type="button" onClick={() => play(hit)}>
                    Play from {clock(hit.start_ts)}
                  </button>
                </li>
              ))}
            </ul>
          </article>
        ) : null}
        <audio id="recording-player" ref={audioRef} controls preload="metadata" className="player" />
      </section>
    </div>
  );
}

function StageList({ status }: { status: IngestStatus }) {
  return (
    <div className="stages">
      <p>
        {status.filename}: {status.status === "failed" ? status.error : status.stage}
      </p>
      <ol>
        {STAGES.map((stage) => (
          <li key={stage} data-state={status.progress[stage] || "pending"}>
            {stage}
          </li>
        ))}
      </ol>
    </div>
  );
}
