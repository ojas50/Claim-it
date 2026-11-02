import Icon from "./Icons";
import { STEPS } from "../i18n";

export default function Stepper({ step, maxStep, onSelect }) {
  return (
    <nav className="stepper" aria-label="Claim progress">
      {STEPS.map((label, index) => {
        const done = index < step;
        const active = index === step;
        const enabled = index <= maxStep;
        return (
          <button
            key={label}
            type="button"
            className={`step ${active ? "active" : ""} ${done ? "done" : ""}`}
            onClick={() => enabled && onSelect(index)}
            disabled={!enabled}
            aria-current={active ? "step" : undefined}
          >
            <span className="step-dot">{done ? <Icon name="check" size={14} /> : index + 1}</span>
            <span className="step-label">{label}</span>
          </button>
        );
      })}
    </nav>
  );
}
