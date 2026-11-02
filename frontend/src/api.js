const BASE = import.meta.env.VITE_API_BASE || "";

async function handle(res) {
  if (res.ok) return res;
  let message = `Request failed (${res.status})`;
  try {
    const data = await res.json();
    if (typeof data.detail === "string") message = data.detail;
    else if (Array.isArray(data.detail)) message = data.detail.map((d) => d.msg).join(", ");
  } catch {
    /* keep generic message */
  }
  throw new Error(message);
}

export async function getHealth() {
  const res = await fetch(`${BASE}/api/health`);
  return (await handle(res)).json();
}

export async function transcribe(blob, language) {
  const form = new FormData();
  const name = blob.type.includes("mp4") ? "narration.m4a" : "narration.webm";
  form.append("file", blob, name);
  form.append("language", language);
  const res = await fetch(`${BASE}/api/transcribe`, { method: "POST", body: form });
  return (await handle(res)).json();
}

export async function parseDocs(files, language) {
  const form = new FormData();
  for (const item of files) form.append("files", item.file, item.file.name);
  form.append("kinds", files.map((item) => item.kind).join(","));
  form.append("language", language);
  const res = await fetch(`${BASE}/api/parse`, { method: "POST", body: form });
  return (await handle(res)).json();
}

export async function analyze(payload) {
  const res = await fetch(`${BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return (await handle(res)).json();
}

export async function draft(language, form) {
  const res = await fetch(`${BASE}/api/draft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, form }),
  });
  return (await handle(res)).json();
}

export async function speak(text, language) {
  const res = await fetch(`${BASE}/api/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
  });
  await handle(res);
  return { blob: await res.blob(), mock: res.headers.get("X-Claimit-Mock") === "true" };
}
