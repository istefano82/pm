import { getAuthToken } from "./session";
import { boardFromApi, type BoardData } from "./kanban";

const API_BASE = "/api";

function getHeaders(): HeadersInit {
  const token = getAuthToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  } else {
    console.warn("No auth token found");
  }

  return headers;
}

export async function fetchBoard(): Promise<BoardData> {
  const response = await fetch(`${API_BASE}/board`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch board: ${response.statusText}`);
  }

  const data = await response.json();
  return boardFromApi(data);
}

export async function createCard(
  columnId: number,
  title: string,
  details: string
): Promise<void> {
  const response = await fetch(`${API_BASE}/cards`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({
      column_id: columnId,
      title,
      details,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create card: ${response.statusText}`);
  }
}

export async function updateCard(
  id: number,
  title?: string,
  details?: string
): Promise<void> {
  const response = await fetch(`${API_BASE}/cards/${id}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify({
      ...(title !== undefined && { title }),
      ...(details !== undefined && { details }),
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update card: ${response.statusText}`);
  }
}

export async function deleteCard(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/cards/${id}`, {
    method: "DELETE",
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to delete card: ${response.statusText}`);
  }
}

export async function moveCard(
  id: number,
  columnId: number,
  position: number
): Promise<void> {
  const response = await fetch(`${API_BASE}/cards/${id}/move`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify({
      column_id: columnId,
      position,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to move card: ${response.statusText}`);
  }
}

export async function renameColumn(id: number, title: string): Promise<void> {
  const response = await fetch(`${API_BASE}/columns/${id}`, {
    method: "PUT",
    headers: getHeaders(),
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    throw new Error(`Failed to rename column: ${response.statusText}`);
  }
}

export async function queryAI(question: string): Promise<{
  response: string;
  updates: Array<{
    action: string;
    columnId?: number;
    cardId?: number;
    title?: string;
    details?: string;
    position?: number;
  }>;
  board?: BoardData;
}> {
  const response = await fetch(`${API_BASE}/ai/query`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`AI query failed: ${response.statusText}`);
  }

  const data = await response.json();
  return {
    response: data.response,
    updates: data.updates,
    board: data.board ? boardFromApi(data.board) : undefined,
  };
}
