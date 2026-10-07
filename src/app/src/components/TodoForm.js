import { useRef, useState } from 'react';
import { MAX_DESCRIPTION_LENGTH } from '../config';
import { validateDescription } from '../validation';

export function TodoForm({ onCreate }) {
  const [description, setDescription] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const inputRef = useRef(null);

  const handleChange = (event) => {
    setDescription(event.target.value);
    if (error) {
      setError(null);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (isSubmitting) {
      return;
    }
    const validationError = validateDescription(description);
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsSubmitting(true);
    try {
      await onCreate(description.trim());
      setDescription('');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
      inputRef.current.focus();
    }
  };

  return (
    <form className="todo-form" onSubmit={handleSubmit} noValidate>
      <label htmlFor="todo-description" className="todo-form__label">ToDo</label>
      <div className="todo-form__row">
        <input
          id="todo-description"
          ref={inputRef}
          className="todo-form__input"
          type="text"
          value={description}
          onChange={handleChange}
          placeholder="What needs to be done?"
          maxLength={MAX_DESCRIPTION_LENGTH}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? 'todo-description-error' : undefined}
          autoComplete="off"
        />
        <button type="submit" className="button button--primary" disabled={isSubmitting}>
          {isSubmitting ? 'Adding…' : 'Add ToDo!'}
        </button>
      </div>
      <div className="todo-form__meta">
        {error && <p id="todo-description-error" className="todo-form__error" role="alert">{error}</p>}
        <span className="todo-form__counter">{description.length}/{MAX_DESCRIPTION_LENGTH}</span>
      </div>
    </form>
  );
}
