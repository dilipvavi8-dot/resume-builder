// Keep the browser client on the exact loopback interface the local FastAPI
// server uses. `localhost` may resolve to IPv6 (`::1`) on some machines while
// the backend deliberately listens on IPv4 only (`127.0.0.1`).
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function parseJsonBody<T>(text: string, fallback: T): T {
  const trimmed = text.trim();
  if (!trimmed) return fallback;
  try {
    return JSON.parse(trimmed) as T;
  } catch {
    throw new Error(trimmed || "Request returned an unreadable response.");
  }
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.text();
    const parsed = parseJsonBody<{ detail?: string }>(body, {});
    throw new Error(parsed.detail || body.trim() || "Request failed.");
  }
  const text = await response.text();
  return parseJsonBody<T>(text, {} as T);
}

export function downloadUrl(path: string) {
  return `${API_URL}${path}`;
}
