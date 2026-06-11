import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FileWarning } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { SearchFilter } from '@/components/common/SearchFilter';
import { Pagination } from '@/components/common/Pagination';
import { StatusBadge } from '@/components/common/StatusBadge';
import { TableSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { challansApi } from '@/api';
import { usePagination } from '@/hooks/usePagination';
import { useDebounce } from '@/hooks/useDebounce';
import { formatCurrency, formatDate } from '@/lib/utils';
import { CHALLAN_STATUS, ROLES } from '@/lib/constants';
import { unwrapPaginated } from '@/lib/apiResponse';

const PATH_MAP = {
  [ROLES.ADMIN]: '/admin/challans',
  [ROLES.OFFICER]: '/officer/challans',
  [ROLES.OWNER]: '/owner/challans',
};

function getReg(c) {
  return c.vehicle?.registration_number ?? c.vehicle_registration ?? '—';
}

function getViolationLabel(c) {
  return c.violation?.name ?? c.violation?.code ?? c.violation_type ?? '—';
}

export default function ChallansPage({ role }) {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({});
  const debouncedSearch = useDebounce(search);
  const { page, pageSize, setPage, setPageSize, queryParams, getPaginationMeta } = usePagination();
  const basePath = PATH_MAP[role] || '/admin/challans';

  const { data, isLoading } = useQuery({
    queryKey: ['challans', role, page, pageSize, debouncedSearch, filters],
    queryFn: async () => {
      const res = await challansApi.list({
        ...queryParams,
        ...filters,
        ...(debouncedSearch ? { vehicle_registration: debouncedSearch } : {}),
        ...(filters.violation_type ? { violation_code: filters.violation_type } : {}),
      });
      return unwrapPaginated(res);
    },
  });

  const items = data?.items ?? [];
  const total = data?.total ?? items.length;
  const meta = getPaginationMeta(total);

  return (
    <div className="space-y-6">
      <PageHeader title="Challans" description="View and manage traffic challans" />
      <SearchFilter
        search={search}
        onSearchChange={setSearch}
        placeholder="Search by registration..."
        filters={[
          {
            key: 'status',
            label: 'Status',
            options: Object.values(CHALLAN_STATUS).map((s) => ({ value: s, label: s })),
          },
        ]}
        filterValues={filters}
        onFilterChange={(k, v) => setFilters((f) => ({ ...f, [k]: v }))}
        onClear={() => { setSearch(''); setFilters({}); }}
      />
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <TableSkeleton />
          ) : items.length === 0 ? (
            <EmptyState title="No challans found" icon={FileWarning} />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Challan #</TableHead>
                    <TableHead>Vehicle</TableHead>
                    <TableHead>Violation</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>
                        <Link to={`${basePath}/${c.id}`} className="font-medium text-primary hover:underline">
                          {c.challan_number}
                        </Link>
                      </TableCell>
                      <TableCell>{getReg(c)}</TableCell>
                      <TableCell>{getViolationLabel(c)}</TableCell>
                      <TableCell>{formatCurrency(c.fine_amount)}</TableCell>
                      <TableCell><StatusBadge status={c.status} /></TableCell>
                      <TableCell>{formatDate(c.created_at)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="mt-4">
                <Pagination {...meta} onPageChange={setPage} onPageSizeChange={setPageSize} />
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}