import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { ApiError } from './api/httpClient';
import { todoApi } from './api/todoApi';

jest.mock('./api/todoApi');

const todo = (overrides) => ({
  id: '1',
  description: 'Learn Docker',
  completed: false,
  created_at: '2024-01-01T10:00:00+00:00',
  ...overrides,
});

const descriptionInput = () => screen.getByLabelText('ToDo');
const addButton = () => screen.getByRole('button', { name: 'Add ToDo!' });

test('shows the todos stored in the backend', async () => {
  todoApi.list.mockResolvedValue([todo(), todo({ id: '2', description: 'Learn React' })]);

  render(<App />);

  expect(await screen.findByText('Learn Docker')).toBeInTheDocument();
  expect(screen.getByText('Learn React')).toBeInTheDocument();
  expect(screen.getByText('2 of 2 open')).toBeInTheDocument();
});

test('creates a todo, then reloads the list from the backend', async () => {
  todoApi.list
    .mockResolvedValueOnce([])
    .mockResolvedValueOnce([todo({ description: 'Learn hooks' })]);
  todoApi.create.mockResolvedValue(todo({ description: 'Learn hooks' }));
  render(<App />);
  await screen.findByText(/nothing here yet/i);

  userEvent.type(descriptionInput(), '  Learn hooks  ');
  userEvent.click(addButton());

  expect(await screen.findByText('Learn hooks')).toBeInTheDocument();
  expect(todoApi.create).toHaveBeenCalledWith('Learn hooks');
  expect(todoApi.list).toHaveBeenCalledTimes(2);
  expect(descriptionInput()).toHaveValue('');
});

test('does not call the API for an empty description', async () => {
  todoApi.list.mockResolvedValue([]);
  render(<App />);
  await screen.findByText(/nothing here yet/i);

  userEvent.click(addButton());

  expect(await screen.findByRole('alert')).toHaveTextContent('Please enter a description.');
  expect(todoApi.create).not.toHaveBeenCalled();
});

test('shows the error returned by the backend when creating fails', async () => {
  todoApi.list.mockResolvedValue([]);
  todoApi.create.mockRejectedValue(new ApiError('The todo database is unavailable.', { status: 503 }));
  render(<App />);
  await screen.findByText(/nothing here yet/i);

  userEvent.type(descriptionInput(), 'Learn Mongo');
  userEvent.click(addButton());

  expect(await screen.findByRole('alert')).toHaveTextContent('The todo database is unavailable.');
  expect(descriptionInput()).toHaveValue('Learn Mongo');
});

test('shows a retry banner when loading fails, and recovers', async () => {
  todoApi.list
    .mockRejectedValueOnce(new ApiError('Cannot reach the server.'))
    .mockResolvedValueOnce([todo()]);
  render(<App />);

  userEvent.click(await screen.findByRole('button', { name: 'Retry' }));

  expect(await screen.findByText('Learn Docker')).toBeInTheDocument();
  expect(screen.queryByText('Cannot reach the server.')).not.toBeInTheDocument();
});

test('toggles and deletes a todo through the API', async () => {
  todoApi.list.mockResolvedValue([todo()]);
  todoApi.update.mockResolvedValue(todo({ completed: true }));
  todoApi.remove.mockResolvedValue(null);
  render(<App />);

  userEvent.click(await screen.findByRole('checkbox'));
  await waitFor(() => expect(todoApi.update).toHaveBeenCalledWith('1', { completed: true }));

  userEvent.click(screen.getByRole('button', { name: 'Delete "Learn Docker"' }));
  await waitFor(() => expect(todoApi.remove).toHaveBeenCalledWith('1'));
});
