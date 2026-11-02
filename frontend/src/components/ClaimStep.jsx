import { useEffect, useState } from "react";
import Icon from "./Icons";
import { LANGUAGES, money } from "../i18n";
import { draft } from "../api";

export default function ClaimStep({
  language,
  form,
  setForm,
  letter,
  setLetter,
  letterLanguage,
  setLetterLanguage,
  analysis,
  onBack,
  onNext,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const langLabel = LANGUAGES.find((l) => l.code === language)?.english || "English";

  const generate = async () => {
    if (!form.patient_name.trim()) {
      setError("Patient name is required before the letter can be written.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await draft(language, form);
      setLetter(res.letter);
      setLetterLanguage(res.language);
    } catch (e) {
      setError(e.message || "Could not generate the claim letter. Retry in a moment.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!form.patient_name.trim()) return;
    if (letter && letterLanguage === language) return;
    generate();
    // Generate once when the step opens, or when the language changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language]);

  const set = (patch) => setForm((current) => ({ ...current, ...patch }));

  return (
    <section className="stack">
      <div className="card">
        <header className="card-header">
          <div>
            <p className="eyebrow">Step 4 of 5</p>
            <h2>Claim form &amp; letter</h2>
            <p className="subtle">
              Check every field, edit anything that is wrong, then save the plain-language letter as a PDF.
            </p>
          </div>
          <div className="row wrap">
            <button className="btn ghost" onClick={generate} disabled={loading}>
              <Icon name="refresh" size={18} /> {loading ? "Writing..." : "Regenerate"}
            </button>
            <button className="btn primary" onClick={() => window.print()} disabled={!letter}>
              <Icon name="print" size={18} /> Save as PDF
            </button>
          </div>
        </header>

        {error && (
          <div className="notice warn">
            <Icon name="alert" size={18} />
            <p>{error}</p>
          </div>
        )}

        <div className="claim-grid">
          <div className="claim-form">
            <div className="panel-title">
              <span>Claim details</span>
              <span className="tag policy">editable</span>
            </div>
            <div className="form-grid">
              <Field label="Policy number" value={form.policy_number} onChange={(v) => set({ policy_number: v })} />
              <Field label="Insurer" value={form.insurer} onChange={(v) => set({ insurer: v })} />
              <Field label="Patient name" value={form.patient_name} onChange={(v) => set({ patient_name: v })} />
              <Field label="Hospital" value={form.hospital_name} onChange={(v) => set({ hospital_name: v })} />
              <Field label="Admission date" value={form.admission_date} onChange={(v) => set({ admission_date: v })} />
              <Field label="Discharge date" value={form.discharge_date} onChange={(v) => set({ discharge_date: v })} />
              <Field
                label="Claim amount (₹)"
                type="number"
                value={form.claim_amount}
                onChange={(v) => set({ claim_amount: Number(v) })}
              />
              <Field label="Phone" value={form.phone} onChange={(v) => set({ phone: v })} placeholder="+91 ..." />
              <Field
                label="Address"
                value={form.address}
                onChange={(v) => set({ address: v })}
                placeholder="City, state"
                wide
              />
            </div>

            <div className="claim-hint">
              <Icon name="info" size={18} />
              <p>
                Claim amount defaults to the billed total ({money(analysis?.totals?.billed || 0)}). Most insurers expect
                the full billed amount; attach the itemised bill and receipts.
              </p>
            </div>
          </div>

          <div className="letter-panel">
            <div className="panel-title">
              <span>Claim letter · {langLabel}</span>
              <span className={`tag ${letterLanguage === language ? "ok" : "warn"}`}>
                {letterLanguage === language ? "ready" : "regenerating"}
              </span>
            </div>
            {loading && !letter ? (
              <div className="loading compact">
                <span className="spinner" />
                <p>Writing the letter in {langLabel}...</p>
              </div>
            ) : (
              <textarea
                className="letter-edit"
                value={letter}
                onChange={(e) => setLetter(e.target.value)}
                placeholder="The claim letter will appear here."
                aria-label="Claim letter text"
              />
            )}
            <p className="tiny">
              Edit the letter freely. “Save as PDF” prints the letter with your device’s PDF printer, so Hindi, Tamil,
              Telugu and Bengali render correctly.
            </p>
          </div>
        </div>

        <p className="disclaimer">
          <Icon name="lock" size={14} /> This is an assistive draft, not legal or financial advice. Verify the policy
          number, dates, amounts and clause citations with your insurer before submitting.
        </p>

        <footer className="card-footer">
          <button className="btn ghost" onClick={onBack}>
            <Icon name="back" size={18} /> Back to coverage
          </button>
          <button className="btn primary" onClick={onNext} disabled={!letter}>
            Hear the summary <Icon name="arrow" size={18} />
          </button>
        </footer>
      </div>
    </section>
  );
}

function Field({ label, value, onChange, type = "text", placeholder = "", wide = false }) {
  return (
    <label className={`field small ${wide ? "wide" : ""}`}>
      <span>{label}</span>
      <input
        type={type}
        value={value ?? ""}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
