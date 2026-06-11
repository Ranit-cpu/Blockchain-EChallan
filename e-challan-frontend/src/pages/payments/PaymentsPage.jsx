import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CreditCard, Loader2 } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { SearchFilter } from '@/components/common/SearchFilter';
import { Pagination } from '@/components/common/Pagination';
import { StatusBadge } from '@/components/common/StatusBadge';
import { TableSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { paymentsApi, challansApi } from '@/api';
import { usePagination } from '@/hooks/usePagination';
import { useDebounce } from '@/hooks/useDebounce';
import { useToast } from '@/hooks/useToast';
import { formatCurrency, formatDate } from '@/lib/utils';
import { ROLES } from '@/lib/constants';
import { unwrapData, unwrapPaginated } from '@/lib/apiResponse';

export default function PaymentsPage({ role }) {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({});
  const [payDialog, setPayDialog] = useState(null);
  const [method, setMethod] = useState('upi');
  const [searchParams] = useSearchParams();
  const challanId = searchParams.get('challan');
  const debouncedSearch = useDebounce(search);
  const { page, pageSize, setPage, setPageSize, queryParams, getPaginationMeta } = usePagination();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const isOwner = role === ROLES.OWNER;

  const { data, isLoading } = useQuery({
    queryKey: ['payment-challans', role, page, pageSize, debouncedSearch, filters],
    queryFn: async () => {
      const res = await challansApi.list({
        ...queryParams,
        status: filters.status || 'pending',
        ...(debouncedSearch ? { vehicle_registration: debouncedSearch } : {}),
      });
      return unwrapPaginated(res);
    },
  });

  const { data: pendingChallan } = useQuery({
    queryKey: ['challan-pay', challanId],
    queryFn: async () => {
      const res = await challansApi.getById(challanId);
      return unwrapData(res);
    },
    enabled: Boolean(challanId),
  });

  const payMutation = useMutation({
    mutationFn: () =>
      paymentsApi.process({
        challan_id: payDialog?.id || challanId,
        payment_method: method,
      }),
    onSuccess: () => {
      toast({ title: 'Payment successful' });
      setPayDialog(null);
      queryClient.invalidateQueries({ queryKey: ['payment-challans'] });
    },
    onError: (err) => toast({ title: 'Payment failed', description: err.message, variant: 'destructive' }),
  });

  const items = data?.items ?? [];
  const total = data?.total ?? items.length;
  const meta = getPaginationMeta(total);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payments"
        description={isOwner ? 'View and pay your challans' : 'Challans awaiting payment'}
        actions={
          isOwner && pendingChallan && (
            <Button onClick={() => setPayDialog(pendingChallan)}>
              Pay {pendingChallan.challan_number}
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
            key: 'status',
            label: 'Status',
            options: [
              { value: 'pending', label: 'pending' },
              { value: 'issued', label: 'issued' },
              { value: 'paid', label: 'paid' },
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
            <EmptyState title="No challans found" icon={CreditCard} />
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Challan #</TableHead>
                    <TableHead>Vehicle</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Due</TableHead>
                    {isOwner && <TableHead>Action</TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell className="font-medium">{c.challan_number}</TableCell>
                      <TableCell>{c.vehicle?.registration_number ?? '—'}</TableCell>
                      <TableCell>{formatCurrency(c.fine_amount)}</TableCell>
                      <TableCell><StatusBadge status={c.status} /></TableCell>
                      <TableCell>{formatDate(c.due_date)}</TableCell>
                      {isOwner && ['pending', 'issued', 'overdue'].includes(c.status) && (
                        <TableCell>
                          <Button size="sm" onClick={() => setPayDialog(c)}>Pay</Button>
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
      <Dialog open={Boolean(payDialog)} onOpenChange={() => setPayDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Process Payment</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm">
              Amount: <strong>{formatCurrency(payDialog?.fine_amount)}</strong>
            </p>
            <Select value={method} onValueChange={setMethod}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="upi">UPI</SelectItem>
                <SelectItem value="card">Card</SelectItem>
                <SelectItem value="netbanking">Net Banking</SelectItem>
                <SelectItem value="wallet">Wallet</SelectItem>
              </SelectContent>
            </Select>
            <Button className="w-full" onClick={() => payMutation.mutate()} disabled={payMutation.isPending}>
              {payMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Confirm Payment
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}