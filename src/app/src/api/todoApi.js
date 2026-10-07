import { request } from './httpClient';

const TODOS_PATH = '/todos/';
const todoPath = (id) => `${TODOS_PATH}${encodeURIComponent(id)}/`;

/** Every call the frontend makes to the todos API lives here. */
export const todoApi = {
  list: ({ signal } = {}) => request(TODOS_PATH, { signal }),
  create: (description) => request(TODOS_PATH, { method: 'POST', body: { description } }),
  update: (id, changes) => request(todoPath(id), { method: 'PATCH', body: changes }),
  remove: (id) => request(todoPath(id), { method: 'DELETE' }),
};
