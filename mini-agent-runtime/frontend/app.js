const form = document.getElementById("ticket-form");
const resultEl = document.getElementById("result");
const traceEl = document.getElementById("trace");

const pretty = (payload) => JSON.stringify(payload, null, 2);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultEl.textContent = "Running...";
  traceEl.textContent = "Loading trace...";

  const ticket = document.getElementById("ticket").value.trim();
  const correlationId = document.getElementById("correlationId").value.trim();
  const idempotencyKey = document.getElementById("idempotencyKey").value.trim();

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ticket,
        correlation_id: correlationId || undefined,
        idempotency_key: idempotencyKey || undefined,
      }),
    });
    const payload = await response.json();
    resultEl.textContent = pretty(payload);

    if (payload.run_id) {
      const traceResp = await fetch(`/api/trace?run_id=${payload.run_id}`);
      const tracePayload = await traceResp.json();
      traceEl.textContent = pretty(tracePayload);
    } else {
      traceEl.textContent = "No run_id returned.";
    }
  } catch (error) {
    resultEl.textContent = `Error: ${error.message}`;
    traceEl.textContent = "Trace unavailable.";
  }
});
