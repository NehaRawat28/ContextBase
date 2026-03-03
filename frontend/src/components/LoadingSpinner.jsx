export default function LoadingSpinner({ size = 20 }) {
  return (
    <div 
      className="loading-spinner" 
      style={{ 
        width: size, 
        height: size,
        border: '2px solid var(--border-color)',
        borderTop: '2px solid var(--accent-primary)',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
      }}
    />
  );
}