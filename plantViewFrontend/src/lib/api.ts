const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) {
    clearTokens();
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      clearTokens();
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    const newAccessToken = data.access_token;
    setToken(newAccessToken);
    return newAccessToken;
  } catch (error) {
    clearTokens();
    throw error;
  }
}

export async function apiCall(
  endpoint: string,
  options: RequestInit & { requiresAuth?: boolean } = {}
): Promise<Response> {
  const { requiresAuth = true, ...fetchOptions } = options;

  const headers = new Headers(fetchOptions.headers);
  headers.set('Content-Type', 'application/json');

  // Add JWT token to headers if required
  if (requiresAuth) {
    let token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('No authentication token found');
    }
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  // Handle token expiration with refresh attempt
  if (response.status === 401 && requiresAuth && !isRefreshing) {
    isRefreshing = true;

    try {
      const newAccessToken = await refreshAccessToken();
      
      if (newAccessToken) {
        // Retry original request with new token
        const retryHeaders = new Headers(fetchOptions.headers);
        retryHeaders.set('Content-Type', 'application/json');
        retryHeaders.set('Authorization', `Bearer ${newAccessToken}`);

        response = await fetch(`${API_URL}${endpoint}`, {
          ...fetchOptions,
          headers: retryHeaders,
        });

        isRefreshing = false;
        onRefreshed(newAccessToken);
      }
    } catch (error) {
      isRefreshing = false;
      throw error;
    }
  } else if (response.status === 401 && requiresAuth && isRefreshing) {
    // Queue request to retry after refresh completes
    return new Promise((resolve) => {
      addRefreshSubscriber((token: string) => {
        const retryHeaders = new Headers(fetchOptions.headers);
        retryHeaders.set('Content-Type', 'application/json');
        retryHeaders.set('Authorization', `Bearer ${token}`);

        resolve(
          fetch(`${API_URL}${endpoint}`, {
            ...fetchOptions,
            headers: retryHeaders,
          })
        );
      });
    });
  }

  return response;
}

export async function signup(
  email: string,
  password: string
): Promise<{ access_token: string; refresh_token: string; user: { id: string; email: string } }> {
  const response = await apiCall('/api/auth/signup', {
    method: 'POST',
    requiresAuth: false,
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Signup failed');
  }

  return response.json();
}

export async function login(
  email: string,
  password: string
): Promise<{ access_token: string; refresh_token: string; user: { id: string; email: string } }> {
  const response = await apiCall('/api/auth/login', {
    method: 'POST',
    requiresAuth: false,
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Login failed');
  }

  return response.json();
}

export async function verifyToken(): Promise<{
  user: { id: string; email: string };
}> {
  const response = await apiCall('/api/auth/verify', {
    method: 'GET',
    requiresAuth: true,
  });

  if (!response.ok) {
    throw new Error('Token verification failed');
  }

  return response.json();
}

export async function logout(): Promise<void> {
  try {
    await apiCall('/api/auth/logout', {
      method: 'POST',
      requiresAuth: true,
    });
  } catch (error) {
    console.error('Logout error (non-critical):', error);
  } finally {
    clearTokens();
  }
}

export function getToken(): string | null {
  return localStorage.getItem('authToken');
}

export function setToken(token: string): void {
  localStorage.setItem('authToken', token);
}

export function setRefreshToken(token: string): void {
  localStorage.setItem('refreshToken', token);
}

export function clearTokens(): void {
  localStorage.removeItem('authToken');
  localStorage.removeItem('refreshToken');
}

export function clearToken(): void {
  clearTokens();
}
