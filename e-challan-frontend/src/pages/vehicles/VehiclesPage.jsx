import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Plus, Car } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { SearchFilter } from '@/components/common/SearchFilter';
import { Pagination } from '@/components/common/Pagination';
import { TableSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { vehiclesApi } from '@/api';
import { unwrapPaginated } from '@/lib/apiResponse';
import { usePagination } from '@/hooks/usePagination';
import { useDebounce } from '@/hooks/useDebounce';
import { formatDate } from '@/lib/utils';

export default function VehiclesPage({ readOnly = false }) {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({});
  const debouncedSearch = useDebounce(search);
  const { page, pageSize, setPage, setPageSize, queryParams, getPaginationMeta } = usePagination();

  const { data, isLoading } = useQuery({
    queryKey: ['vehicles', page, pageSize, debouncedSearch, filters],
    queryFn: async () => {
      const res = await vehiclesApi.list({
        ...queryParams,
        ...filters,
        ...(debouncedSearch ? { q: debouncedSearch } : {}),
      });
      return unwrapPaginated(res);
    },
  });

  const items = data?.items || data || [];
  const total = data?.total ?? items.length;
  const meta = getPaginationMeta(total);
  const basePath = readOnly ? '/officer/vehicles' : '/admin/vehicles';

  return (
    <div className="space-y-6">
      <PageHeader
        title="Vehicles"
        description="Manage registered vehicles"
        actions={
          !readOnly && (
            <Button asChild>
              <Link to="/admin/vehicles/new">
                <Plus className="mr-2 h-4 w-4" />
                Add Vehicle
              </Link>
            </Button>
          )
        }
      />
      <SearchFilter
        search={search}
        onSearchChange={setSearch}
        placeholder="Search by registration..."
        filters={[
          {
            key: 'vehicle_type',
            label: 'Type',
            options: [
              { value: 'two_wheeler', label: 'Two Wheeler' },
              { value: 'four_wheeler', label: 'Four Wheeler' },
              { value: 'commercial', label: 'Commercial' },
            ],
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
            <EmptyState title="No vehicles found" icon={Car} />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Registration</TableHead>
                    <TableHead>Make / Model</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead>Registered</TableHead>
                    {!readOnly && <TableHead>Actions</TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((v) => (
                    <TableRow key={v.id}>
                      <TableCell className="font-medium">{v.registration_number}</TableCell>
                      <TableCell>{v.make} {v.model}</TableCell>
                      <TableCell className="capitalize">{v.vehicle_type?.replace('_', ' ')}</TableCell>
                      <TableCell>{v.owner_name || '—'}</TableCell>
                      <TableCell>{formatDate(v.created_at)}</TableCell>
                      {!readOnly && (
                        <TableCell>
                          <Button variant="ghost" size="sm" asChild>
                            <Link to={`/admin/vehicles/${v.id}/edit`}>Edit</Link>
                          </Button>
                        </TableCell>
                      )}
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
