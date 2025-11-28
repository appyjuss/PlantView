const API_BASE = '/API';

type RefreshFn = () => Promise<boolean>;
type LogoutFn = () => void;

let refreshFn: RefreshFn | null = null;
let onLogout: LogoutFn | null = null;

export function registerAuthHandlers(handlers: { refresh?: RefreshFn; logout?: LogoutFn }) {
  if (handlers.refresh) refreshFn = handlers.refresh;
  if (handlers.logout) onLogout = handlers.logout;
}

function isJsonResponse(res: Response) {
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json');
}

export async function apiFetch(input: RequestInfo, init: RequestInit = {}) {
  const url = typeof input === 'string' ? input : (input as Request).url;
  const opts: RequestInit = { ...init, credentials: 'include' };

  // Don't set JSON headers for FormData
  if (opts.body && !(opts.body instanceof FormData) && typeof opts.body === 'object') {
    opts.headers = { ...(opts.headers || {}), 'Content-Type': 'application/json' };
    try {
      opts.body = JSON.stringify(opts.body as any);
    } catch (e) {
      // leave body as-is
    }
  }

  let response = await fetch(url, opts);

  if (response.status === 401 && refreshFn) {
    // attempt refresh
    let refreshed = false;
    try {
      refreshed = await refreshFn();
    } catch (e) {
      refreshed = false;
    }

    if (refreshed) {
      // retry original request once
      response = await fetch(url, opts);
    } else {
      // refresh failed — notify logout handler if available
      if (onLogout) onLogout();
      // return the 401 response
      return response;
    }
  }

  return response;
}

export { API_BASE };
