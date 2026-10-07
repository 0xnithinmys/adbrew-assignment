// The browser runs on the host machine, so the API is reached through the
// port Docker publishes (8000), not the container name.
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Must match MAX_DESCRIPTION_LENGTH in src/rest/todos/validators.py.
export const MAX_DESCRIPTION_LENGTH = 200;
