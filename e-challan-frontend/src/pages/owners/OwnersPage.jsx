import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Plus, Users } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { SearchFilter } from '@/components/common/SearchFilter';
import { Pagination } from '@/components/common/Pagination';
import { TableSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { unwrapPaginated } from '@/lib/apiResponse';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ownersApi } from '@/api';
import { usePagination } from '@/hooks/usePagination';
import { useDebounce } from '@/hooks/useDebounce';

export default function OwnersPage() {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search);
  const { page, pageSize, setPage, setPageSize, queryParams, getPaginationMeta } = usePagination();

  const { data, isLoading } = useQuery({
    queryKey: ['owners', page, pageSize, debouncedSearch],
    queryFn: async () => {
      const res = await ownersApi.list({
        ...queryParams,
        ...(debouncedSearch ? { q: debouncedSearch } : {}),
      });
      return unwrapPaginated(res);
    },
  });

  const items = data?.items || data || [];
  const total = data?.total ?? items.length;
  const meta = getPaginationMeta(total);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Owners"
        description="Manage vehicle owners"
        actions={
          <Button asChild>
            <Link to="/admin/owners/new">
              <Plus className="mr-2 h-4 w-4" />
              Add Owner
            </Link>
          </Button>
        }
      />
      <SearchFilter search={search} onSearchChange={setSearch} placeholder="Search owners..." onClear={() => setSearch('')} />
      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <TableSkeleton />
          ) : items.length === 0 ? (
            <EmptyState title="No owners found" icon={Users} />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Phone</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>City</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((o) => (
                    <TableRow key={o.id}>
                      <TableCell className="font-medium">{o.full_name}</TableCell>
                      <TableCell>{o.phone}</TableCell>
                      <TableCell>{o.email || '—'}</TableCell>
                      <TableCell>{o.city}</TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/admin/owners/${o.id}/edit`}>Edit</Link>
                        </Button>
                      </TableCell>
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
