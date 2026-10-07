import { TodoItem } from './TodoItem';

export function TodoList({ todos, isLoading, pendingIds, onToggle, onDelete }) {
  if (isLoading) {
    return <p className="todo-status" role="status">Loading todos…</p>;
  }
  if (todos.length === 0) {
    return <p className="todo-status">Nothing here yet. Add your first todo below.</p>;
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          isPending={pendingIds.has(todo.id)}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
