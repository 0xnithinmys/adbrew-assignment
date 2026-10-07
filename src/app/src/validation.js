import { MAX_DESCRIPTION_LENGTH } from './config';

/**
 * Mirrors the backend rules for instant feedback. The backend still validates
 * every request, since the browser can always be bypassed.
 * Returns an error message, or null when the description is valid.
 */
export function validateDescription(description) {
  if (!description.trim()) {
    return 'Please enter a description.';
  }
  if (description.trim().length > MAX_DESCRIPTION_LENGTH) {
    return `Keep it under ${MAX_DESCRIPTION_LENGTH} characters.`;
  }
  return null;
}
