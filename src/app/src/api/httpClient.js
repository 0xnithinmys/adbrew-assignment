import { API_BASE_URL } from '../config';

const NETWORK_ERROR_MESSAGE = 'Cannot reach the server. Make sure the api container is running.';

/** Error thrown for every failed request, so callers handle a single type. */
export class ApiError extends Error {
  constructor(message, { status = 0, code = 'network_error', details = {} } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

/**
 * Thin wrapper around fetch: sends and parses JSON, and converts both network
 * failures and the API's {"error": {...}} responses into ApiError.
 */
export async function request(path, { method = 'GET', body, signal } = {}) {
  const hasBody = body !== undefined;
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      signal,
      headers: {
        Accept: 'application/json',
        ...(hasBody && { 'Content-Type': 'application/json' }),
      },
      body: hasBody ? JSON.stringify(body) : undefined,
    });
  } catch (error) {
    if (error.name === 'AbortError') {
      throw error;
    }
    throw new ApiError(NETWORK_ERROR_MESSAGE);
  }

  const data = await parseJson(response);
  if (!response.ok) {
    const apiError = (data && data.error) || {};
    throw new ApiError(apiError.message || `Request failed with status ${response.status}.`, {
      status: response.status,
      code: apiError.code || 'http_error',
      details: apiError.details || {},
    });
  }
  return data;
}

async function parseJson(response) {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    return null;
  }
}
