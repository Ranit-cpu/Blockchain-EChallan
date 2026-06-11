import { useState, useCallback, useMemo } from 'react';
import { DEFAULT_PAGE_SIZE } from '@/lib/constants';

export function usePagination(initialPage = 1, initialPageSize = DEFAULT_PAGE_SIZE) {
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);

  const resetPage = useCallback(() => setPage(1), []);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: pageSize,
      skip: (page - 1) * pageSize,
      limit: pageSize,
    }),
    [page, pageSize]
  );

  const getPaginationMeta = useCallback(
    (total) => ({
      page,
      pageSize,
      total: total ?? 0,
      totalPages: Math.max(1, Math.ceil((total ?? 0) / pageSize)),
      hasNext: page * pageSize < (total ?? 0),
      hasPrev: page > 1,
    }),
    [page, pageSize]
  );

  return {
    page,
    pageSize,
    setPage,
    setPageSize,
    resetPage,
    queryParams,
    getPaginationMeta,
  };
}
