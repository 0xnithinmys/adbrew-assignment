const dateFormatter = new Intl.DateTimeFormat(undefined, {
  day: 'numeric',
  month: 'short',
  hour: '2-digit',
  minute: '2-digit',
});

export function TodoItem({ todo, isPending, onToggle, onDelete }) {
  const className = ['todo-item', todo.completed && 'todo-item--done', isPending && 'todo-item--pending']
    .filter(Boolean)
    .join(' ');

  return (
    <li className={className}>
      <label className="todo-item__main">
        <input
          type="checkbox"
          className="todo-item__checkbox"
          checked={todo.completed}
          disabled={isPending}
          onChange={() => onToggle(todo)}
        />
        <span className="todo-item__text">{todo.description}</span>
      </label>
      <time className="todo-item__date" dateTime={todo.created_at}>
        {dateFormatter.format(new Date(todo.created_at))}
      </time>
      <button
        type="button"
        className="button button--ghost"
        disabled={isPending}
        onClick={() => onDelete(todo)}
        aria-label={`Delete "${todo.description}"`}
      >
        Delete
      </button>
    </li>
  );
}
