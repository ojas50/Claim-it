import { useCallback, useEffect, useState } from "react";
import Stepper from "./components/Stepper";
import VoiceStep from "./components/VoiceStep";
import DocumentsStep from "./components/DocumentsStep";
import CoverageStep from "./components/CoverageStep";
import ClaimStep from "./components/ClaimStep";
import FinalStep from "./components/FinalStep";
import Icon from "./components/Icons";
import { analyze, getHealth } from "./api";
import { LANGUAGES } from "./i18n";

const EMPTY_FORM = {
  policy_number: "",
  insurer: "",
  patient_name: "",
  hospital_name: "",
  admission_date: "",
  discharge_date: "",
  claim_amount: 0,
  phone: "",
  address: "",
};

function buildForm(parsed, analysis) {
  return {
    ...EMPTY_FORM,
    policy_number: parsed?.policy?.policy_number || "",
    insurer: parsed?.policy?.insurer || "",
    patient_name: analysis?.facts?.patient_name || parsed?.bill?.patient_name || "",
    hospital_name: analysis?.facts?.hospital_name || parsed?.bill?.hospital_name || "",
    admission_date: parsed?.bill?.admission_date || analysis?.facts?.incident_date || "",
    discharge_date: parsed?.bill?.discharge_date || "",
    claim_amount: analysis?.totals?.billed || parsed?.bill?.total_amount || 0,
  };
}

export default function App() {
  const [health, setHealth] = useState(null);
  const [healthError, setHealthError] = useState("");

  const [step, setStep] = useState(0);
  const [maxStep, setMaxStep] = useState(0);
  const [language, setLanguage] = useState("hi-IN");

  const [transcript, setTranscript] = useState("");
  const [files, setFiles] = useState([]);
  const [parsed, setParsedState] = useState(null);

  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  const [form, setForm] = useState(EMPTY_FORM);
  const [letter, setLetter] = useState("");
  const [letterLanguage, setLetterLanguage] = useState("");

  useEffect(() => {
    let alive = true;
    getHealth()
      .then((data) => {
        if (alive) setHealth(data);
      })
      .catch((e) => {
        if (alive) setHealthError(e.message || "Backend unreachable.");
      });
    return () => {
      alive = false;
    };
  }, []);

  const setParsed = useCallback((next) => {
    setParsedState(next);
    setAnalysis(null);
    setAnalysisError("");
    setLetter("");
    setLetterLanguage("");
  }, []);

  const chooseLanguage = (code) => {
    setLanguage(code);
    setAnalysis(null);
    setAnalysisError("");
    setLetter("");
    setLetterLanguage("");
  };

  const runAnalysis = useCallback(async () => {
    if (!parsed) {
      setAnalysisError("Upload and read the documents first.");
      return null;
    }
    if (!transcript.trim()) {
      setAnalysisError("Record or paste the narration first.");
      return null;
    }
    setAnalysisLoading(true);
    setAnalysisError("");
    try {
      const result = await analyze({
        narration: transcript,
        language,
        policy: parsed.policy,
        bill: parsed.bill,
      });
      setAnalysis(result);
      return result;
    } catch (e) {
      setAnalysisError(e.message || "Coverage check failed. Retry in a moment.");
      return null;
    } finally {
      setAnalysisLoading(false);
    }
  }, [parsed, transcript, language]);

  const goTo = (next) => {
    setStep(next);
    setMaxStep((current) => Math.max(current, next));
  };

  const openCoverage = () => {
    goTo(2);
    if (!analysis && !analysisLoading) runAnalysis();
  };

  const openClaim = () => {
    setForm((current) => (current.patient_name ? current : buildForm(parsed, analysis)));
    goTo(3);
  };

  const openFinal = () => goTo(4);

  const handleStepSelect = (index) => {
    if (index === 2 && !analysis && !analysisLoading) runAnalysis();
    if (index === 3) {
      setForm((current) => (current.patient_name ? current : buildForm(parsed, analysis)));
    }
    setStep(index);
  };

  const restart = () => {
    files.forEach((item) => URL.revokeObjectURL(item.url));
    setFiles([]);
    setParsedState(null);
    setTranscript("");
    setAnalysis(null);
    setAnalysisError("");
    setAnalysisLoading(false);
    setForm(EMPTY_FORM);
    setLetter("");
    setLetterLanguage("");
    setStep(0);
    setMaxStep(0);
  };

  const langLabel = LANGUAGES.find((l) => l.code === language);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">
            <Icon name="shield" size={24} />
          </span>
          <div>
            <h1>Claim-It</h1>
            <p>Insurance claim copilot for India</p>
          </div>
        </div>
        <div className="topbar-right">
          <span className="lang-chip" title="Narration and letter language">
            {langLabel?.label || "हिन्दी"}
          </span>
          <span
            className={`mode-pill ${health?.mode === "live" ? "live" : "demo"}`}
            title={
              health?.mode === "live"
                ? "Live Sarvam API"
                : "Mock mode: canned responses, no API calls"
            }
          >
            <span className="dot" />
            {health ? (health.mode === "live" ? "Live Sarvam" : "Demo mode") : "Connecting..."}
          </span>
        </div>
      </header>

      {healthError && (
        <div className="notice warn global">
          <Icon name="alert" size={18} />
          <p>
            Backend not reachable ({healthError}). Start FastAPI on port 8000, then refresh. Demo mode still works once
            it is running.
          </p>
        </div>
      )}

      {health?.mode === "mock" && (
        <div className="notice info global">
          <Icon name="info" size={18} />
          <p>
            Demo mode is on: transcription, document reading, coverage reasoning and voice use canned data. Set{" "}
            <code>MOCK_MODE=false</code> to call Sarvam live.
          </p>
        </div>
      )}

      <Stepper step={step} maxStep={maxStep} onSelect={handleStepSelect} />

      <main className="main">
        {step === 0 && (
          <VoiceStep
            language={language}
            setLanguage={chooseLanguage}
            transcript={transcript}
            setTranscript={setTranscript}
            onNext={() => goTo(1)}
          />
        )}

        {step === 1 && (
          <DocumentsStep
            language={language}
            files={files}
            setFiles={setFiles}
            parsed={parsed}
            setParsed={setParsed}
            onNext={openCoverage}
            onBack={() => setStep(0)}
          />
        )}

        {step === 2 && (
          <CoverageStep
            analysis={analysis}
            loading={analysisLoading}
            error={analysisError}
            onRun={runAnalysis}
            onBack={() => setStep(1)}
            onNext={openClaim}
          />
        )}

        {step === 3 && (
          <ClaimStep
            language={language}
            form={form}
            setForm={setForm}
            letter={letter}
            setLetter={setLetter}
            letterLanguage={letterLanguage}
            setLetterLanguage={setLetterLanguage}
            analysis={analysis}
            onBack={() => setStep(2)}
            onNext={openFinal}
          />
        )}

        {step === 4 && analysis && (
          <FinalStep
            analysis={analysis}
            language={language}
            onBack={() => setStep(3)}
            onRestart={restart}
          />
        )}
      </main>

      <footer className="site-footer">
        <p>
          <Icon name="lock" size={13} /> Claim-It is a hackathon demo. It is not legal, medical, or financial advice.
          Coverage outcomes are estimates; verify every clause and document with your insurer.
        </p>
        <p className="tiny">
          Built with Sarvam Saaras (speech), Sarvam Vision (documents), Sarvam-105B (reasoning) and Bulbul (voice).
        </p>
      </footer>

      {step === 3 && (
        <div className="print-area" aria-hidden="true">
          <div className="print-head">
            <h1>Claim-It</h1>
            <p>Assistive claim letter · not legal or financial advice</p>
          </div>
          <pre>{letter || "The letter is being generated..."}</pre>
        </div>
      )}
    </div>
  );
}
