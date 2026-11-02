import { useEffect, useRef, useState } from "react";
import Icon from "./Icons";
import { LANGUAGES, SPEECH_FALLBACK, money } from "../i18n";
import { speak } from "../api";

export default function FinalStep({ analysis, language, onBack, onRestart }) {
  const [playing, setPlaying] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const audioRef = useRef(null);
  const utterRef = useRef(null);

  const langLabel = LANGUAGES.find((l) => l.code === language)?.english || "English";

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    };
  }, []);

  const stop = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setPlaying(false);
    setStatus("");
  };

  const fallback = (text) => {
    if (!window.speechSynthesis) {
      setPlaying(false);
      setError("This browser cannot play audio. The full summary is written below.");
      return;
    }
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = language;
    utter.rate = 0.95;
    const voices = window.speechSynthesis.getVoices?.() || [];
    const exact = voices.find((v) => v.lang?.toLowerCase() === language.toLowerCase());
    const loose = voices.find((v) => v.lang?.toLowerCase().startsWith(language.slice(0, 2).toLowerCase()));
    if (exact || loose) utter.voice = exact || loose;
    utter.onend = () => {
      setPlaying(false);
      setStatus("");
    };
    utter.onerror = () => {
      setPlaying(false);
      setStatus("");
    };
    utterRef.current = utter;
    window.speechSynthesis.speak(utter);
    setPlaying(true);
    setStatus("Playing with your device voice (demo mode).");
  };

  const play = async () => {
    if (playing) {
      stop();
      return;
    }
    setError("");
    setStatus("Preparing the spoken summary...");
    setPlaying(true);
    const fallbackText = SPEECH_FALLBACK[language] || analysis.summary;
    const speechText = [
      analysis.summary,
      ...analysis.gaps.slice(0, 3).map((gap) => gap.action),
    ]
      .filter(Boolean)
      .join(" ");
    try {
      const { blob, mock } = await speak(speechText, language);
      if (mock || !blob.size) {
        fallback(fallbackText);
        return;
      }
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => {
        setPlaying(false);
        setStatus("");
        URL.revokeObjectURL(url);
      };
      audio.onerror = () => {
        setError("The audio could not play here. Using the device voice instead.");
        fallback(fallbackText);
      };
      await audio.play();
      setStatus("Playing with Sarvam Bulbul.");
    } catch (e) {
      setError(e.message || "Spoken reply failed. Using the device voice instead.");
      fallback(fallbackText);
    }
  };

  const severityOrder = { high: 0, medium: 1, low: 2 };
  const nextSteps = [...analysis.gaps]
    .sort((a, b) => (severityOrder[a.severity] ?? 3) - (severityOrder[b.severity] ?? 3))
    .slice(0, 5);

  return (
    <section className="stack">
      <div className="card speak-card">
        <header className="card-header">
          <div>
            <p className="eyebrow">Step 5 of 5</p>
            <h2>Spoken summary</h2>
            <p className="subtle">Hear the outcome and next steps in {langLabel}, powered by Sarvam Bulbul.</p>
          </div>
          <span className={`tag ${analysis.mode === "mock" ? "demo" : "live"}`}>
            {analysis.mode === "mock" ? "Demo voice" : "Bulbul v4 Flash"}
          </span>
        </header>

        <div className="speak-hero">
          <button className={`speak-btn ${playing ? "playing" : ""}`} onClick={play} aria-label={playing ? "Stop summary" : "Play summary"}>
            <Icon name={playing ? "pause" : "volume"} size={30} />
          </button>
          <div>
            <strong>{playing ? "Playing summary..." : "Play the summary & next steps"}</strong>
            <p className="tiny">
              {status ||
                (analysis.mode === "mock"
                  ? "Demo mode: the browser voice reads the localised summary."
                  : "Sarvam Bulbul will read the summary in your language.")}
            </p>
          </div>
        </div>

        {error && (
          <div className="notice warn">
            <Icon name="alert" size={18} />
            <p>{error}</p>
          </div>
        )}

        <div className="stats-grid compact-stats">
          <Stat label="Billed" value={money(analysis.totals.billed)} tone="neutral" />
          <Stat label="Likely covered" value={money(analysis.totals.covered)} tone="good" />
          <Stat label="You may pay" value={money(analysis.totals.patient_pay)} tone="warn" />
        </div>

        <div className="summary-box">
          <div className="summary-icon">
            <Icon name="info" size={20} />
          </div>
          <p>{analysis.summary}</p>
        </div>
      </div>

      <div className="card">
        <div className="panel-title">
          <span>What to do next</span>
          <span className="tag warn">{analysis.gaps.length} items</span>
        </div>
        {nextSteps.length === 0 ? (
          <div className="empty-state small">
            <Icon name="check" size={26} />
            <p>No document gaps were detected. Submit the claim and keep the originals safe.</p>
          </div>
        ) : (
          <ol className="next-steps">
            {nextSteps.map((gap, index) => (
              <li key={`${gap.id}-${index}`} className={`next-step ${gap.severity}`}>
                <span className="step-num">{index + 1}</span>
                <div>
                  <strong>{gap.title}</strong>
                  <p>{gap.action || gap.detail}</p>
                </div>
              </li>
            ))}
          </ol>
        )}
        <p className="disclaimer">
          <Icon name="lock" size={14} /> {analysis.disclaimer}
        </p>
        <footer className="card-footer">
          <button className="btn ghost" onClick={onBack}>
            <Icon name="back" size={18} /> Back to the letter
          </button>
          <button className="btn primary" onClick={onRestart}>
            <Icon name="refresh" size={18} /> Start a new claim
          </button>
        </footer>
      </div>
    </section>
  );
}

function Stat({ label, value, tone }) {
  return (
    <div className={`stat ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
