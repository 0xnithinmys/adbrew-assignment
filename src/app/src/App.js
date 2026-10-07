import './App.css';
import { ErrorBanner } from './components/ErrorBanner';
import { TodoForm } from './components/TodoForm';
import { TodoList } from './components/TodoList';
import { useTodos } from './hooks/useTodos';

export function App() {
  const { todos, isLoading, error, pendingIds, refresh, addTodo, toggleTodo, deleteTodo } = useTodos();
  const openCount = todos.filter((todo) => !todo.completed).length;
  const showList = !(error && todos.length === 0);

  return (
    <main className="app">
      <section className="card" aria-labelledby="todo-list-heading">
        <header className="card__header">
          <h1 id="todo-list-heading">List of TODOs</h1>
          {!isLoading && todos.length > 0 && (
            <span className="badge">{openCount} of {todos.length} open</span>
          )}
        </header>
        {error && <ErrorBanner message={error} onRetry={() => refresh()} />}
        {showList && (
          <TodoList
            todos={todos}
            isLoading={isLoading}
            pendingIds={pendingIds}
            onToggle={toggleTodo}
            onDelete={deleteTodo}
          />
        )}
      </section>

      <section className="card" aria-labelledby="todo-form-heading">
        <h2 id="todo-form-heading">Create a ToDo</h2>
        <TodoForm onCreate={addTodo} />
      </section>
    </main>
  );
}

export default App;
