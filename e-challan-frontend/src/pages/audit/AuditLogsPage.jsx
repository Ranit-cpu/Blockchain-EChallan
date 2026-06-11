import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ScrollText, Download } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { SearchFilter } from '@/components/common/SearchFilter';
import { Pagination } from '@/components/common/Pagination';
import { TableSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { auditApi } from '@/api';
import { usePagination } from '@/hooks/usePagination';
import { useDebounce } from '@/hooks/useDebounce';
import { formatDate } from '@/lib/utils';
import { useToast } from '@/hooks/useToast';

export default function AuditLogsPage() {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({});
  const debouncedSearch = useDebounce(search);
  const { page, pageSize, setPage, setPageSize, queryParams, getPaginationMeta } = usePagination();
  const { toast } = useToast();

  const { data, isLoading } = useQuery({
    queryKey: ['audit-logs', page, pageSize, debouncedSearch, filters],
    queryFn: async () => {
      const res = await auditApi.list({
        ...queryParams,
        ...(filters.action ? { action: filters.action } : {}),
      });
      return unwrapPaginated(res);
    },
  });

  const handleExport = async () => {
    try {
      const { data: blob } = await auditApi.export({ search: debouncedSearch, ...filters });
      const url = window.URL.createObjectURL(new Blob([blob]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast({ title: 'Export started' });
    } catch (err) {
      toast({ title: 'Export failed', description: err.message, variant: 'destructive' });
    }
  };

  const items = data?.items || data || [];
  const total = data?.total ?? items.length;
  const meta = getPaginationMeta(total);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Logs"
        description="System activity and security audit trail"
        actions={
          <Button variant="outline" onClick={handleExport}>
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
        }
      />
      <SearchFilter
        search={search}
        onSearchChange={setSearch}
        placeholder="Search logs..."
        filters={[
          {
            key: 'action',
            label: 'Action',
            options: [
              { value: 'login', label: 'Login' },
              { value: 'logout', label: 'Logout' },
              { value: 'create', label: 'Create' },
              { value: 'update', label: 'Update' },
              { value: 'delete', label: 'Delete' },
              { value: 'payment', label: 'Payment' },
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
            <EmptyState title="No audit logs" icon={ScrollText} />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Action</TableHead>
                    <TableHead>Resource</TableHead>
                    <TableHead>IP</TableHead>
                    <TableHead>Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="whitespace-nowrap">{formatDate(log.created_at, { time: true })}</TableCell>
                      <TableCell>{log.user_email || log.user_id}</TableCell>
                      <TableCell className="capitalize font-medium">{log.action}</TableCell>
                      <TableCell>{log.resource_type} {log.resource_id && `#${log.resource_id.slice(0, 8)}`}</TableCell>
                      <TableCell className="font-mono text-xs">{log.ip_address}</TableCell>
                      <TableCell className="max-w-[200px] truncate text-muted-foreground">{log.details}</TableCell>
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
