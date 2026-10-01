import { API_BASE_URL } from './config';

export type HealthResponse = {
  status: string;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}

export type AuthCredentials = {
  email: string;
  password: string;
};

export type UserResponse = {
  id: string;
  email: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};

export async function registerUser(
  credentials: AuthCredentials
): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/user/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<UserResponse>;
}

export async function loginUser(
  credentials: AuthCredentials
): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/user/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<LoginResponse>;
}

export async function getCurrentUser(
  accessToken: string
): Promise<UserResponse> {
  const response = await fetch(`${API_BASE_URL}/user/me`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<UserResponse>;
}