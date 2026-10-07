export function ErrorBanner({ message, onRetry }) {
  return (
    <div className="error-banner" role="alert">
      <span>{message}</span>
      <button type="button" className="button button--ghost" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}
