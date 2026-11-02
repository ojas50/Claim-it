import { useState } from "react";
import Icon from "./Icons";
import { LANGUAGES, SAMPLE_NARRATION } from "../i18n";
import { transcribe } from "../api";

function formatTime(seconds) {
  if (!Number.isFinite(seconds)) return "00:00";
  const s = Math.max(0, Math.floor(seconds));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${String(m).padStart(2, "0")}:${String(r).padStart(2, "0")}`;
}

export default function VoiceStep({ language, setLanguage, transcript, setTranscript, onNext }) {
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [seconds, setSeconds] = useState(0);
  const [timer, setTimer] = useState(null);

  const startRecording = async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType: mime });
      const pieces = [];
      recorder.ondataavailable = (e) => e.data.size > 0 && pieces.push(e.data);
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(pieces, { type: mime });
        setLoading(true);
        try {
          const res = await transcribe(blob, language);
          setTranscript(res.transcript || "");
          if (res.warning) setError(res.warning);
        } catch (e) {
          setError(e.message || "Transcription failed. Use the sample narration instead.");
        } finally {
          setLoading(false);
        }
      };
      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
      setSeconds(0);
      const id = setInterval(() => setSeconds((s) => s + 1), 1000);
      setTimer(id);
    } catch (e) {
      setError(e.message || "Microphone access was denied. Paste or use the sample narration.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
    if (timer) clearInterval(timer);
    setTimer(null);
    setRecording(false);
  };

  const useSample = () => {
    setTranscript(SAMPLE_NARRATION[language] || SAMPLE_NARRATION["en-IN"]);
    setError("");
  };

  return (
    <section className="card">
      <header className="card-header">
        <div>
          <p className="eyebrow">Step 1 of 5</p>
          <h2>Voice intake</h2>
          <p className="subtle">Narrate the hospitalisation or accident in your language. Saaras will transcribe it.</p>
        </div>
        <div className="row">
          <label className="field small">
            <span>Language</span>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label} · {l.english}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>

      <div className="mic-panel">
        <button
          className={`mic ${recording ? "recording" : ""}`}
          onClick={recording ? stopRecording : startRecording}
          disabled={loading}
          aria-label={recording ? "Stop recording" : "Start recording"}
        >
          <Icon name={recording ? "stop" : "mic"} size={32} />
        </button>
        <p className="mic-text">{loading ? "Transcribing with Saaras..." : recording ? "Recording..." : "Tap the mic and narrate your claim"}</p>
        <p className="time">{formatTime(seconds)}</p>
      </div>

      <div className="row wrap">
        <button className="btn ghost" onClick={useSample}>
          <Icon name="spark" size={18} /> Use sample narration
        </button>
      </div>

      <label className="field">
        <span>Transcript (editable)</span>
        <textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} placeholder="Your narration will appear here. You can edit it before continuing." />
      </label>

      {error && (
        <div className="notice warn">
          <Icon name="alert" size={18} />
          <p>{error}</p>
        </div>
      )}

      <footer className="card-footer">
        <div />
        <button className="btn primary" onClick={onNext} disabled={!transcript.trim()}>
          Next: Upload documents <Icon name="arrow" size={18} />
        </button>
      </footer>
    </section>
  );
}
