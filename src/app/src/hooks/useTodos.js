import { useCallback, useEffect, useState } from 'react';
import { todoApi } from '../api/todoApi';

/**
 * All todo state and server interaction, kept out of the components.
 *
 * After every change the list is fetched again from the API, so the screen
 * always shows exactly what is stored in MongoDB.
 */
export function useTodos() {
  const [todos, setTodos] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pendingIds, setPendingIds] = useState(() => new Set());

  const refresh = useCallback(async ({ signal } = {}) => {
    try {
      const latest = await todoApi.list({ signal });
      setTodos(latest);
      setError(null);
    } catch (err) {
      if (err.name === 'AbortError') {
        return;
      }
      setError(err.message);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    // Abort the first load if the component unmounts before it finishes.
    const controller = new AbortController();
    refresh({ signal: controller.signal });
    return () => controller.abort();
  }, [refresh]);

  // Errors are re-thrown so the form can show them next to the input.
  const addTodo = useCallback(async (description) => {
    await todoApi.create(description);
    await refresh();
  }, [refresh]);

  // Toggle and delete report errors in the shared banner and lock only the
  // affected row while the request is in flight.
  const runItemAction = useCallback(async (id, action) => {
    setPendingIds((ids) => new Set(ids).add(id));
    try {
      await action();
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setPendingIds((ids) => {
        const next = new Set(ids);
        next.delete(id);
        return next;
      });
    }
  }, [refresh]);

  const toggleTodo = useCallback(
    (todo) => runItemAction(todo.id, () => todoApi.update(todo.id, { completed: !todo.completed })),
    [runItemAction],
  );

  const deleteTodo = useCallback(
    (todo) => runItemAction(todo.id, () => todoApi.remove(todo.id)),
    [runItemAction],
  );

  return { todos, isLoading, error, pendingIds, refresh, addTodo, toggleTodo, deleteTodo };
}
