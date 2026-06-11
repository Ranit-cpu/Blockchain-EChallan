import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { unwrapPaginated } from '@/lib/apiResponse';
import { FileWarning, CreditCard, ShieldCheck } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { StatCard } from '@/components/common/StatCard';
import { DashboardSkeleton } from '@/components/common/LoadingSkeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { challansApi } from '@/api';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

export default function OwnerDashboard() {
  // const { data: stats, isLoading } = useQuery({
  //   queryKey: ['owner-stats'],
  //   queryFn: async () => {
  //     const { data: res } = await challansApi.getStats();
  //     return res;
  //   },
  // });

  const { data: challans, isLoading } = useQuery({
    queryKey: ['owner-challans'],
    queryFn: async () => {
      const res = await challansApi.list({ page: 1, page_size: 5, status: 'pending' });
      return unwrapPaginated(res);
    },
  });

  if (isLoading) return <DashboardSkeleton />;

  const s = stats || { pending_challans: 0, total_due: 0, paid_challans: 0 };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Owner Dashboard"
        description="View and pay your traffic challans"
        actions={
          <Button asChild>
            <Link to="/owner/verify">
              <ShieldCheck className="mr-2 h-4 w-4" />
              Verify Challan
            </Link>
          </Button>
        }
      />
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Pending Challans" value={s.pending_challans} icon={FileWarning} index={0} />
        <StatCard title="Amount Due" value={formatCurrency(s.total_due)} icon={CreditCard} index={1} />
        <StatCard title="Paid" value={s.paid_challans} icon={FileWarning} index={2} />
      </div>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Pending Payments</CardTitle>
          <Link to="/owner/payments" className="text-sm text-primary hover:underline">Pay now</Link>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Challan #</TableHead>
                <TableHead>Violation</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Due Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(challans?.items || challans || []).map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <Link to={`/owner/challans/${c.id}`} className="text-primary hover:underline">
                      {c.challan_number}
                    </Link>
                  </TableCell>
                  <TableCell>{c.violation_type}</TableCell>
                  <TableCell>{formatCurrency(c.fine_amount)}</TableCell>
                  <TableCell><StatusBadge status={c.status} /></TableCell>
                  <TableCell>{formatDate(c.due_date)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
