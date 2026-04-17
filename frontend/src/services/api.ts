export async function enrollFace(user_id: string, image_sequence_base64: string[]): Promise<void> {
  const res = await fetch("http://localhost:8000/auth/enroll-face", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, image_sequence_base64 })
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const j = await res.json();
      detail = j?.detail || j?.message || detail;
    } catch {
      // ignore - non-JSON error
    }
    throw new Error(detail);
  }
}

export async function verifyFace(user_id: string, image_sequence_base64: string[], challenge_response: string): Promise<string> {
  const res = await fetch("http://localhost:8000/auth/verify-face", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id, image_sequence_base64, challenge_response })
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const j = await res.json();
      detail = j?.detail || j?.message || detail;
    } catch {
      // ignore - non-JSON error
    }
    throw new Error(detail);
  }
  const data = await res.json();
  return data.token;
}

export async function chatQuery(token: string, user_id: string, query: string, session_id?: number) {
  const res = await fetch("http://localhost:8000/chat/query", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ user_id, query, session_id })
  });
  if (!res.ok) throw new Error("Chat request failed");
  return res.json();
}

export async function chatQueryStream(token: string, user_id: string, query: string, session_id?: number) {
  const res = await fetch("http://localhost:8000/chat/query-stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ user_id, query, session_id })
  });
  if (!res.ok) throw new Error("Streaming request failed");
  return res;
}
