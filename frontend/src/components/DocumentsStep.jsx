import { useMemo, useRef, useState } from "react";
import Icon from "./Icons";
import { money } from "../i18n";
import { parseDocs } from "../api";

const ACCEPT = ".pdf,.png,.jpg,.jpeg,.webp,.tif,.tiff";

export default function DocumentsStep({ language, files, setFiles, parsed, setParsed, onNext, onBack }) {
  const [error, setError] = useState("");
  const [loading, setLoading] = useState("");
  const [active, setActive] = useState(0);
  const policyInput = useRef(null);
  const billInput = useRef(null);

  const policyFile = files.find((f) => f.kind === "policy");
  const billFiles = files.filter((f) => f.kind === "bill");
  const previews = useMemo(
    () => [
      ...(policyFile ? [{ ...policyFile, label: "Policy" }] : []),
      ...billFiles.map((f, i) => ({ ...f, label: `Bill ${i + 1}` })),
    ],
    [policyFile, billFiles]
  );
  const activeDoc = previews[Math.min(active, Math.max(0, previews.length - 1))];

  const addFiles = (list, kind) => {
    const incoming = Array.from(list || []);
    if (!incoming.length) return;
    setError("");
    const valid = [];
    for (const file of incoming) {
      const ext = `.${file.name.split(".").pop().toLowerCase()}`;
      if (!ACCEPT.split(",").includes(ext)) {
        setError(`"${file.name}" is not a supported type. Use PDF, PNG, JPG, WEBP, or TIFF.`);
        continue;
      }
      if (file.size > 20 * 1024 * 1024) {
        setError(`"${file.name}" is larger than 20 MB.`);
        continue;
      }
      valid.push({ file, kind, url: URL.createObjectURL(file) });
    }
    if (!valid.length) return;
    setParsed(null);
    setFiles((prev) => {
      const next = kind === "policy" ? prev.filter((f) => f.kind !== "policy") : prev;
      return [...next, ...valid];
    });
    setActive(0);
  };

  const removeFile = (target) => {
    URL.revokeObjectURL(target.url);
    setFiles((prev) => prev.filter((f) => f !== target));
    setParsed(null);
  };

  const loadSamples = async () => {
    setError("");
    setLoading("Loading sample policy and bills...");
    try {
      const names = [
        ["policy.pdf", "policy", "application/pdf"],
        ["bill_printed.png", "bill", "image/png"],
        ["bill_handwritten.png", "bill", "image/png"],
      ];
      const loaded = [];
      for (const [name, kind, type] of names) {
        const res = await fetch(`/samples/${name}`);
        if (!res.ok) throw new Error(`Could not load samples/${name}`);
        const blob = await res.blob();
        const file = new File([blob], name, { type });
        loaded.push({ file, kind, url: URL.createObjectURL(file) });
      }
      setFiles(loaded);
      setParsed(null);
      setActive(0);
      setLoading("");
      await runParse(loaded);
    } catch (e) {
      setLoading("");
      setError(e.message || "Could not load the sample set. Upload the files manually.");
    }
  };

  const runParse = async (selected = files) => {
    if (!selected.some((f) => f.kind === "policy")) {
      setError("Add the insurance policy first.");
      return;
    }
    if (!selected.some((f) => f.kind === "bill")) {
      setError("Add at least one hospital or pharmacy bill.");
      return;
    }
    setError("");
    setLoading("Reading the policy and bills. Handwritten pages can take a moment...");
    try {
      const result = await parseDocs(selected, language);
      setParsed(result);
      setActive(0);
    } catch (e) {
      setError(e.message || "Document reading failed. Try a clearer photo, or enable MOCK_MODE.");
    } finally {
      setLoading("");
    }
  };

  const updatePolicy = (patch) => setParsed((p) => (p ? { ...p, policy: { ...p.policy, ...patch } } : p));
  const updateBill = (patch) => setParsed((p) => (p ? { ...p, bill: { ...p.bill, ...patch } } : p));
  const updateClause = (index, patch) =>
    setParsed((p) => {
      if (!p) return p;
      const clauses = p.policy.clauses.map((c, i) => (i === index ? { ...c, ...patch } : c));
      return { ...p, policy: { ...p.policy, clauses } };
    });
  const addClause = () =>
    setParsed((p) =>
      p
        ? {
            ...p,
            policy: {
              ...p.policy,
              clauses: [...p.policy.clauses, { id: `C${p.policy.clauses.length + 1}`, title: "New clause", text: "" }],
            },
          }
        : p
    );
  const removeClause = (index) =>
    setParsed((p) =>
      p ? { ...p, policy: { ...p.policy, clauses: p.policy.clauses.filter((_, i) => i !== index) } } : p
    );
  const updateLine = (index, patch) =>
    setParsed((p) => {
      if (!p) return p;
      const line_items = p.bill.line_items.map((l, i) => (i === index ? { ...l, ...patch } : l));
      return { ...p, bill: { ...p.bill, line_items } };
    });
  const addLine = () =>
    setParsed((p) =>
      p
        ? {
            ...p,
            bill: {
              ...p.bill,
              line_items: [
                ...p.bill.line_items,
                { id: `B${p.bill.line_items.length + 1}`, description: "New bill item", amount: 0 },
              ],
            },
          }
        : p
    );
  const removeLine = (index) =>
    setParsed((p) => (p ? { ...p, bill: { ...p.bill, line_items: p.bill.line_items.filter((_, i) => i !== index) } } : p));

  const total = parsed ? parsed.bill.line_items.reduce((sum, l) => sum + Number(l.amount || 0), 0) : 0;
  const lowConfidence =
    parsed && (Number(parsed.policy.confidence) < 0.7 || Number(parsed.bill.confidence) < 0.7);

  return (
    <section className="card">
      <header className="card-header">
        <div>
          <p className="eyebrow">Step 2 of 5</p>
          <h2>Documents</h2>
          <p className="subtle">Upload the policy and bills. Sarvam Vision reads printed and handwritten pages.</p>
        </div>
        <button className="btn ghost" onClick={loadSamples} disabled={!!loading}>
          <Icon name="spark" size={18} /> Load sample set
        </button>
      </header>

      {!parsed && (
        <>
          <div className="drop-grid">
            <DropZone
              title="Insurance policy"
              hint="PDF or clear photo · 1 file"
              icon="file"
              onClick={() => policyInput.current?.click()}
              onDrop={(e) => {
                e.preventDefault();
                addFiles(e.dataTransfer.files, "policy");
              }}
              active={!!policyFile}
            />
            <DropZone
              title="Hospital & pharmacy bills"
              hint="Printed, handwritten or crumpled · multiple files"
              icon="camera"
              onClick={() => billInput.current?.click()}
              onDrop={(e) => {
                e.preventDefault();
                addFiles(e.dataTransfer.files, "bill");
              }}
              active={billFiles.length > 0}
            />
          </div>
          <input ref={policyInput} type="file" accept={ACCEPT} hidden onChange={(e) => addFiles(e.target.files, "policy")} />
          <input ref={billInput} type="file" accept={ACCEPT} multiple hidden onChange={(e) => addFiles(e.target.files, "bill")} />

          <div className="file-list">
            {files.map((item) => (
              <div className="file-chip" key={item.url}>
                <span className={`tag ${item.kind}`}>{item.kind === "policy" ? "Policy" : "Bill"}</span>
                <Icon name={item.file.name.endsWith(".pdf") ? "file" : "camera"} size={16} />
                <span className="file-name">{item.file.name}</span>
                <button className="icon-btn" onClick={() => removeFile(item)} aria-label={`Remove ${item.file.name}`}>
                  <Icon name="x" size={15} />
                </button>
              </div>
            ))}
          </div>

          <footer className="card-footer">
            <button className="btn ghost" onClick={onBack}>
              <Icon name="back" size={18} /> Back
            </button>
            <button className="btn primary" onClick={() => runParse(files)} disabled={!!loading || !files.length}>
              {loading ? "Reading..." : "Read documents"} <Icon name="arrow" size={18} />
            </button>
          </footer>
        </>
      )}

      {loading && (
        <div className="loading">
          <span className="spinner" />
          <p>{loading}</p>
        </div>
      )}

      {error && (
        <div className="notice warn">
          <Icon name="alert" size={18} />
          <p>{error}</p>
        </div>
      )}

      {parsed && (
        <>
          {lowConfidence && (
            <div className="notice warn">
              <Icon name="alert" size={18} />
              <p>Low-confidence read on at least one document. Check every field against the original before continuing.</p>
            </div>
          )}
          {parsed.warnings?.length > 0 && (
            <div className="notice info">
              <Icon name="info" size={18} />
              <p>{parsed.warnings.join(" ")}</p>
            </div>
          )}

          <div className="review-grid">
            <div className="source-panel">
              <div className="panel-title">
                <span>Original document</span>
                <span className="tiny">side-by-side check</span>
              </div>
              {previews.length > 1 && (
                <div className="tabs">
                  {previews.map((doc, i) => (
                    <button key={doc.url} className={i === active ? "active" : ""} onClick={() => setActive(i)}>
                      {doc.label}
                    </button>
                  ))}
                </div>
              )}
              <div className="preview-frame">
                {activeDoc ? (
                  activeDoc.file.name.toLowerCase().endsWith(".pdf") ? (
                    <iframe title="Policy PDF preview" src={`${activeDoc.url}#toolbar=0&navpanes=0`} />
                  ) : (
                    <img src={activeDoc.url} alt={`${activeDoc.label} preview`} />
                  )
                ) : (
                  <p className="subtle">No document preview.</p>
                )}
              </div>
              <p className="tiny">Zoom with your browser. Fields on the right are fully editable.</p>
            </div>

            <div className="fields-panel">
              <div className="panel-title">
                <span>Extracted policy</span>
                <span className="tag policy">editable</span>
              </div>
              <div className="form-grid">
                <Field label="Policy number" value={parsed.policy.policy_number} onChange={(v) => updatePolicy({ policy_number: v })} />
                <Field label="Insurer" value={parsed.policy.insurer} onChange={(v) => updatePolicy({ insurer: v })} />
                <Field label="Insured name" value={parsed.policy.insured_name} onChange={(v) => updatePolicy({ insured_name: v })} />
                <Field label="Sum insured (₹)" type="number" value={parsed.policy.sum_insured} onChange={(v) => updatePolicy({ sum_insured: Number(v) })} />
                <Field label="Start date" value={parsed.policy.policy_start_date} onChange={(v) => updatePolicy({ policy_start_date: v })} />
                <Field label="End date" value={parsed.policy.policy_end_date} onChange={(v) => updatePolicy({ policy_end_date: v })} />
              </div>

              <div className="subhead">
                <span>Policy clauses</span>
                <button className="btn tiny-btn" onClick={addClause}>
                  <Icon name="plus" size={14} /> Add clause
                </button>
              </div>
              <div className="clause-list">
                {parsed.policy.clauses.map((clause, index) => (
                  <div className="clause-edit" key={index}>
                    <div className="row">
                      <input className="clause-id" value={clause.id} onChange={(e) => updateClause(index, { id: e.target.value })} aria-label="Clause id" />
                      <input className="clause-title" value={clause.title} onChange={(e) => updateClause(index, { title: e.target.value })} aria-label="Clause title" />
                      <button className="icon-btn" onClick={() => removeClause(index)} aria-label="Remove clause">
                        <Icon name="trash" size={15} />
                      </button>
                    </div>
                    <textarea value={clause.text} onChange={(e) => updateClause(index, { text: e.target.value })} aria-label="Clause text" />
                  </div>
                ))}
              </div>

              <div className="subhead">
                <span>Extracted bill</span>
                <span className="tag bill">editable</span>
              </div>
              <div className="form-grid">
                <Field label="Patient name" value={parsed.bill.patient_name} onChange={(v) => updateBill({ patient_name: v })} />
                <Field label="Hospital" value={parsed.bill.hospital_name} onChange={(v) => updateBill({ hospital_name: v })} />
                <Field label="Admission" value={parsed.bill.admission_date} onChange={(v) => updateBill({ admission_date: v })} />
                <Field label="Discharge" value={parsed.bill.discharge_date} onChange={(v) => updateBill({ discharge_date: v })} />
                <Field label="Bill number" value={parsed.bill.bill_number} onChange={(v) => updateBill({ bill_number: v })} />
              </div>

              <div className="line-table">
                <div className="line-head">
                  <span>Bill line</span>
                  <span>Amount</span>
                  <span />
                </div>
                {parsed.bill.line_items.map((line, index) => (
                  <div className="line-row" key={index}>
                    <input value={line.description} onChange={(e) => updateLine(index, { description: e.target.value })} aria-label="Bill line description" />
                    <input
                      type="number"
                      value={line.amount}
                      onChange={(e) => updateLine(index, { amount: Number(e.target.value) })}
                      aria-label="Bill line amount"
                    />
                    <button className="icon-btn" onClick={() => removeLine(index)} aria-label="Remove bill line">
                      <Icon name="trash" size={15} />
                    </button>
                  </div>
                ))}
                <div className="line-total">
                  <button className="btn tiny-btn" onClick={addLine}>
                    <Icon name="plus" size={14} /> Add line
                  </button>
                  <strong>Total: {money(total)}</strong>
                </div>
              </div>
            </div>
          </div>

          <footer className="card-footer">
            <button className="btn ghost" onClick={() => setParsed(null)}>
              <Icon name="refresh" size={18} /> Re-read documents
            </button>
            <button className="btn primary" onClick={onNext}>
              Check coverage <Icon name="arrow" size={18} />
            </button>
          </footer>
        </>
      )}
    </section>
  );
}

function DropZone({ title, hint, icon, onClick, onDrop, active }) {
  return (
    <div
      className={`drop ${active ? "active" : ""}`}
      onClick={onClick}
      onDragOver={(e) => e.preventDefault()}
      onDrop={onDrop}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onClick()}
    >
      <span className="drop-icon">
        <Icon name={icon} size={26} />
      </span>
      <h3>{title}</h3>
      <p>{hint}</p>
      <span className="btn tiny-btn">Choose files</span>
    </div>
  );
}

function Field({ label, value, onChange, type = "text" }) {
  return (
    <label className="field small">
      <span>{label}</span>
      <input type={type} value={value ?? ""} onChange={(e) => onChange(e.target.value)} />
    </label>
  );
}
