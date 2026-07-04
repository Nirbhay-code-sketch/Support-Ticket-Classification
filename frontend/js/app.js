const els = {
  subject: document.getElementById("subject"),
  ticketText: document.getElementById("ticketText"),
  charCount: document.getElementById("charCount"),
  classifyBtn: document.getElementById("classifyBtn"),
  btnLabel: document.getElementById("btnLabel"),
  errorMsg: document.getElementById("errorMsg"),
  emptyState: document.getElementById("emptyState"),
  resultState: document.getElementById("resultState"),
  categoryValue: document.getElementById("categoryValue"),
  categoryConfidenceFill: document.getElementById("categoryConfidenceFill"),
  categoryConfidenceText: document.getElementById("categoryConfidenceText"),
  priorityValue: document.getElementById("priorityValue"),
  priorityConfidenceText: document.getElementById("priorityConfidenceText"),
  reasonsList: document.getElementById("reasonsList"),
  timestampText: document.getElementById("timestampText"),
  modelSuggestionText: document.getElementById("modelSuggestionText"),
  statusDot: document.getElementById("statusDot"),
  statusLabel: document.getElementById("statusLabel"),
  footApi: document.getElementById("footApi"),
};

const SAMPLES = {
  high: {
    subject: "Production API completely down",
    text: "URGENT - our checkout API has been returning 500 errors for the last 20 minutes and we are losing sales every minute this stays down. Please escalate immediately!!",
  },
  medium: {
    subject: "Duplicate charge on invoice",
    text: "I noticed I was billed twice for my March subscription. Could you please look into this and refund the extra charge when you get a chance?",
  },
  low: {
    subject: "Feature suggestion",
    text: "No rush at all, but it would be great if the dashboard supported a dark mode option in a future update.",
  },
};

els.footApi.textContent = API_BASE_URL;

els.ticketText.addEventListener("input", () => {
  els.charCount.textContent = els.ticketText.value.length;
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const sample = SAMPLES[chip.dataset.sample];
    els.subject.value = sample.subject;
    els.ticketText.value = sample.text;
    els.charCount.textContent = sample.text.length;
  });
});

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    const data = await res.json();
    if (data.models_loaded) {
      els.statusDot.classList.add("ok");
      els.statusLabel.textContent = "Engine ready";
    } else {
      els.statusDot.classList.add("down");
      els.statusLabel.textContent = "Models not trained yet";
    }
  } catch (e) {
    els.statusDot.classList.add("down");
    els.statusLabel.textContent = "Backend unreachable";
  }
}

function showError(message) {
  els.errorMsg.textContent = message;
  els.errorMsg.hidden = false;
}

function clearError() {
  els.errorMsg.hidden = true;
}

function renderResult(data) {
  els.emptyState.hidden = true;
  els.resultState.hidden = false;

  els.categoryValue.textContent = data.category;
  const catPct = Math.round(data.category_confidence * 100);
  els.categoryConfidenceFill.style.width = `${catPct}%`;
  els.categoryConfidenceText.textContent = `confidence ${catPct}%`;

  const priorityLower = data.priority.toLowerCase();
  els.priorityValue.textContent = data.priority;
  els.priorityValue.className = `result-value priority-value ${priorityLower}`;

  document.querySelectorAll(".priority-seg").forEach((seg) => {
    seg.className = "priority-seg";
  });
  const levels = ["low", "medium", "high"];
  const activeIndex = levels.indexOf(priorityLower);
  document.querySelectorAll(".priority-seg").forEach((seg, i) => {
    if (i <= activeIndex) seg.classList.add(`active-${priorityLower}`);
  });

  const priPct = Math.round(data.model_confidence * 100);
  els.priorityConfidenceText.textContent = `model confidence ${priPct}%`;

  els.reasonsList.innerHTML = "";
  data.reasons.forEach((reason) => {
    const li = document.createElement("li");
    li.textContent = reason;
    els.reasonsList.appendChild(li);
  });

  const ts = new Date(data.timestamp);
  els.timestampText.textContent = `classified ${ts.toLocaleTimeString()}`;
  els.modelSuggestionText.textContent = `model suggested: ${data.model_suggested_priority}`;
}

async function classifyTicket() {
  clearError();
  const text = els.ticketText.value.trim();
  if (text.length < 3) {
    showError("Please enter at least 3 characters describing the issue.");
    return;
  }

  els.classifyBtn.disabled = true;
  els.btnLabel.textContent = "Classifying…";

  try {
    const res = await fetch(`${API_BASE_URL}/classify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        subject: els.subject.value.trim() || null,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed with status ${res.status}`);
    }

    const data = await res.json();
    renderResult(data);
  } catch (e) {
    showError(e.message || "Something went wrong while classifying this ticket.");
  } finally {
    els.classifyBtn.disabled = false;
    els.btnLabel.textContent = "Classify ticket";
  }
}

els.classifyBtn.addEventListener("click", classifyTicket);

checkHealth();
