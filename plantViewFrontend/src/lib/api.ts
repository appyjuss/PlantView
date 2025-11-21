const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export async function apiCall(
  endpoint: string,
  options: RequestInit & { requiresAuth?: boolean } = {}
): Promise<Response> {
  const { requiresAuth = true, ...fetchOptions } = options;
  
  const headers = new Headers(fetchOptions.headers);
  headers.set('Content-Type', 'application/json');

  // Add JWT token to headers if required
  if (requiresAuth) {
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('No authentication token found');
    }
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  return response;
}

export async function signup(
  email: string,
  password: string
): Promise<{ token: string; user: { id: string; email: string } }> {
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
): Promise<{ token: string; user: { id: string; email: string } }> {
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

export function getToken(): string | null {
  return localStorage.getItem('authToken');
}

export function setToken(token: string): void {
  localStorage.setItem('authToken', token);
}

export function clearToken(): void {
  localStorage.removeItem('authToken');
}
