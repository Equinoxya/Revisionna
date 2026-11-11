const TOKEN_KEY = "revisionna.token";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* mode navigation privee : on continue sans persistance */
  }
}

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.status = status;
    this.payload = payload ?? {};
  }
}

/** Appel JSON unique, avec le jeton si present. */
export async function api(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`/api${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const texte = await response.text();
  const data = texte ? JSON.parse(texte) : {};

  if (!response.ok) {
    throw new ApiError(data.error || "Une erreur est survenue.", response.status, data);
  }
  return data;
}
