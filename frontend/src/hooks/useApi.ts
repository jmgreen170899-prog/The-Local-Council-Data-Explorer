/**
 * useApi hook for managing API state with loading, error, and retry logic.
 */

import { useState, useCallback, useEffect } from "react";

export interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export interface UseApiResult<T> extends ApiState<T> {
  refetch: () => Promise<void>;
  reset: () => void;
}

/**
 * Custom hook for managing async API calls with loading, error states and retry.
 * @param fetcher - Async function that returns the data
 * @param deps - Dependencies that trigger a refetch when changed
 * @param immediate - Whether to fetch immediately on mount (default: true)
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: readonly unknown[] = [],
  immediate: boolean = true
): UseApiResult<T> {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const result = await fetcher();
      setState({ data: result, loading: false, error: null });
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : (err as { message?: string }).message ?? "An error occurred";
      setState((prev) => ({ ...prev, loading: false, error: message }));
    }
    // Spread deps is intentional for dynamic dependency support
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetcher, ...deps]);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
    // Spread deps is intentional for dynamic dependency support
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate, execute, ...deps]);

  return {
    ...state,
    refetch: execute,
    reset,
  };
}

export default useApi;
