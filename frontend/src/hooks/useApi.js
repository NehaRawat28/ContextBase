import { useState, useCallback } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8000';

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const makeRequest = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const queryKnowledgeBase = useCallback(async (question, k = 3) => {
    return makeRequest('/query', {
      method: 'POST',
      body: JSON.stringify({ question, k }),
    });
  }, [makeRequest]);

  return {
    loading,
    error,
    queryKnowledgeBase,
    clearError: () => setError(null),
  };
}