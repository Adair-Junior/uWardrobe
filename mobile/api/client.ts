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

export type ClothingItem = {
  id: string;
  name: string;
  category: string;
  color: string;
  style: string;
  season: string;
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

export async function getWardrobe(
  accessToken: string
): Promise<ClothingItem[]> {
  const response = await fetch(`${API_BASE_URL}/wardrobe`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<ClothingItem[]>;
}

export async function createClothingItem(
  accessToken: string,
  item: Omit<ClothingItem, 'id'>
): Promise<ClothingItem> {
  const response = await fetch(`${API_BASE_URL}/wardrobe`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(item),
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<ClothingItem>;
}

export type DeleteClothingItemResponse = {
  message: string;
};

export async function deleteClothingItem(
  accessToken: string,
  itemId: string
): Promise<DeleteClothingItemResponse> {
  const response = await fetch(
    `${API_BASE_URL}/wardrobe/${itemId}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<DeleteClothingItemResponse>;
}

export async function updateClothingItem(
  accessToken: string,
  itemId: string,
  item: Omit<ClothingItem, 'id'>
): Promise<ClothingItem> {
  const response = await fetch(
    `${API_BASE_URL}/wardrobe/${itemId}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(item),
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  return response.json() as Promise<ClothingItem>;
}