import Icon from "./Icons";
import { VERDICT_LABELS, money, prettyDate } from "../i18n";

export default function CoverageStep({ analysis, loading, error, onRun, onBack, onNext }) {
  if (loading) {
    return (
      <section className="card">
        <div className="loading tall">
          <span className="spinner" />
          <h2>Matching every bill line to your policy</h2>
          <p className="subtle">Sarvam-105B is extracting facts, applying clauses, sub-limits, exclusions, waiting periods and co-pay.</p>
        </div>
      </section>
    );
  }

  if (!analysis) {
    return (
      <section className="card">
        <header className="card-header">
          <div>
            <p className="eyebrow">Step 3 of 5</p>
            <h2>Coverage check</h2>
            <p className="subtle">Match each bill line against the policy clauses, with a citation and confidence score.</p>
          </div>
        </header>
        {error && (
          <div className="notice warn">
            <Icon name="alert" size={18} />
            <p>{error}</p>
          </div>
        )}
        <div className="empty-state">
          <span className="empty-icon">
            <Icon name="spark" size={28} />
          </span>
          <p>The policy and bill are ready. Run the check to see what is covered and what needs fixing.</p>
          <button className="btn primary" onClick={onRun}>
            Run coverage check <Icon name="arrow" size={18} />
          </button>
        </div>
        <footer className="card-footer">
          <button className="btn ghost" onClick={onBack}>
            <Icon name="back" size={18} /> Back to documents
          </button>
          <div />
        </footer>
      </section>
    );
  }

  const coveredCount = analysis.verdicts.filter((v) => v.verdict === "covered").length;
  const partialCount = analysis.verdicts.filter((v) => v.verdict === "partially_covered").length;
  const unclearCount = analysis.verdicts.filter((v) => v.verdict === "unclear").length;

  return (
    <section className="stack">
      <div className="card">
        <header className="card-header">
          <div>
            <p className="eyebrow">Step 3 of 5</p>
            <h2>Coverage check</h2>
            <p className="subtle">
              {analysis.verdicts.length} bill lines · {coveredCount} fully covered · {partialCount} partly covered · {unclearCount} need review
            </p>
          </div>
          <span className="tag live">{analysis.mode === "mock" ? "Demo data" : "Sarvam-105B"}</span>
        </header>

        <div className="stats-grid">
          <Stat label="Total billed" value={money(analysis.totals.billed)} tone="neutral" />
          <Stat label="Likely covered" value={money(analysis.totals.covered)} tone="good" />
          <Stat label="You may pay" value={money(analysis.totals.patient_pay)} tone="warn" />
        </div>
        {analysis.totals.copay_percent > 0 && (
          <p className="tiny">
            Includes a {analysis.totals.copay_percent}% co-pay on {money(analysis.totals.admissible)} admissible amount
            ({money(analysis.totals.copay_amount)}). Confirm network-hospital status with the insurer.
          </p>
        )}

        <div className="facts-strip">
          <Fact label="Patient" value={analysis.facts.patient_name} />
          <Fact label="Hospital" value={analysis.facts.hospital_name} />
          <Fact label="Incident" value={prettyDate(analysis.facts.incident_date)} />
          <Fact label="Claim type" value={analysis.facts.claim_type} />
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
          <span>Line-by-line verdicts</span>
          <span className="tiny">clause cited for every line</span>
        </div>
        <div className="verdict-list">
          {analysis.verdicts.map((v) => (
            <article className={`verdict ${v.verdict}`} key={v.line_id}>
              <div className="verdict-top">
                <span className={`badge ${v.verdict}`}>{VERDICT_LABELS[v.verdict]}</span>
                <span className="verdict-amount">{money(v.amount)}</span>
              </div>
              <h3>{v.line_description}</h3>
              <div className="verdict-meta">
                <span>
                  Likely payable <strong>{money(v.covered_amount)}</strong>
                </span>
                <Confidence value={v.confidence} />
              </div>
              {v.reasoning && <p className="reason">{v.reasoning}</p>}
              <blockquote className="clause-quote">
                <span className="quote-label">
                  {v.clause_id ? `Clause ${v.clause_id}` : "Policy clause"} {v.clause_text ? "" : "· no match"}
                </span>
                <p>{v.clause_text || "No exact clause matched — flagged for manual review."}</p>
              </blockquote>
              <p className="bill-ref">
                <Icon name="file" size={14} /> Bill line {v.line_id}: {v.line_description} · {money(v.amount)}
              </p>
            </article>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="panel-title">
          <span>Document gaps & next steps</span>
          <span className="tag warn">{analysis.gaps.length} action items</span>
        </div>
        <div className="gap-list">
          {analysis.gaps.map((gap, i) => (
            <div className={`gap ${gap.severity}`} key={`${gap.id}-${i}`}>
              <span className="gap-icon">
                <Icon name={gap.severity === "high" ? "alert" : "info"} size={19} />
              </span>
              <div>
                <div className="gap-title">
                  <strong>{gap.title}</strong>
                  <span className={`badge severity ${gap.severity}`}>{gap.severity}</span>
                </div>
                <p>{gap.detail}</p>
                <p className="gap-action">
                  <Icon name="arrow" size={14} /> {gap.action}
                </p>
              </div>
            </div>
          ))}
        </div>
        <p className="disclaimer">
          <Icon name="lock" size={14} /> {analysis.disclaimer}
        </p>
        <footer className="card-footer">
          <button className="btn ghost" onClick={onBack}>
            <Icon name="back" size={18} /> Edit documents
          </button>
          <button className="btn primary" onClick={onNext}>
            Draft the claim <Icon name="arrow" size={18} />
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

function Fact({ label, value }) {
  return (
    <div className="fact">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function Confidence({ value }) {
  const pct = Math.round(Number(value || 0) * 100);
  const tone = pct >= 80 ? "high" : pct >= 60 ? "mid" : "low";
  return (
    <span className={`confidence ${tone}`} title={`${pct}% confidence`}>
      <span className="confidence-bar">
        <span style={{ width: `${pct}%` }} />
      </span>
      {pct}% confidence
    </span>
  );
}
