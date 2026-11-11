// Client de l'API.
//
// La session vit dans un cookie HttpOnly : JavaScript ne voit jamais le jeton.
// Pour chaque écriture, on renvoie en en-tête le jeton CSRF que le serveur a
// posé dans un second cookie, lisible celui-là (« double soumission »).

const CSRF_COOKIE = "revisionna_csrf";
export const SESSION_EXPIRED = "revisionna:session-expiree";

function csrfToken() {
  const match = document.cookie.match(new RegExp(`(?:^|; )${CSRF_COOKIE}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

/** Indice (non fiable) qu'une session existe : évite un appel inutile au démarrage. */
export function hasSession() {
  return csrfToken() !== null;
}

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload ?? {};
  }

  /** Erreurs par champ renvoyées par le serveur, s'il y en a. */
  get fields() {
    return this.payload.errors ?? {};
  }
}

const FALLBACK = {
  401: "Connectez-vous pour continuer.",
  403: "Action refusée.",
  404: "Introuvable.",
  413: "Contenu trop volumineux.",
  429: "Trop de tentatives, patientez un instant.",
};

export async function api(path, { method = "GET", body } = {}) {
  const write = method !== "GET";
  const headers = { Accept: "application/json" };
  if (write) {
    headers["Content-Type"] = "application/json";
    const token = csrfToken();
    if (token) headers["X-CSRF-Token"] = token;
  }

  const hadSession = hasSession();
  let response;
  try {
    response = await fetch(`/api${path}`, {
      method,
      headers,
      credentials: "same-origin",
      body: write ? JSON.stringify(body ?? {}) : undefined,
    });
  } catch {
    throw new ApiError("Le serveur ne répond pas. Vérifiez votre connexion.", 0);
  }

  let data = {};
  try {
    data = await response.json();
  } catch {
    // Réponse non JSON : typiquement une page d'erreur du serveur frontal.
  }

  if (!response.ok) {
    if (response.status === 401 && hadSession && !path.startsWith("/auth/log")) {
      window.dispatchEvent(new Event(SESSION_EXPIRED));
    }
    const message = data.error || FALLBACK[response.status] || "Une erreur est survenue.";
    throw new ApiError(message, response.status, data);
  }
  return data;
}
