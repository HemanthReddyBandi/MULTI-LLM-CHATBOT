const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export async function registerUser(email, password) {
  const res = await fetch(`${API_BASE_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || 'Registration failed');
  }
  return data;
}

export async function loginUser(email, password, remember) {
  const form = new URLSearchParams();
  form.set('username', email);
  form.set('password', password);

  const res = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form.toString(),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || 'Login failed');
  }
  const token = data.access_token;
  if (remember) {
    localStorage.setItem('auth_token', token);
  } else {
    sessionStorage.setItem('auth_token', token);
  }
  return data;
}

export function getToken() {
  return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
}

export function logout() {
  localStorage.removeItem('auth_token');
  sessionStorage.removeItem('auth_token');
}

