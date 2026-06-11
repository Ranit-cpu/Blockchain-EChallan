import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FileWarning, PlusCircle, Upload } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { StatCard } from '@/components/common/StatCard';
import { DashboardSkeleton } from '@/components/common/LoadingSkeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { challansApi } from '@/api';
import { StatusBadge } from '@/components/common/StatusBadge';
import { unwrapData, unwrapPaginated } from '@/lib/apiResponse';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

export default function OfficerDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['officer-dashboard'],
    queryFn: async () => {
      const res = await challansApi.getStats();
      return unwrapData(res) ?? {};
    },
  });

  const { data: recent } = useQuery({
    queryKey: ['officer-recent-challans'],
    queryFn: async () => {
      const res = await challansApi.list({ page: 1, page_size: 5 });
      return unwrapPaginated(res);
    },
  });

  if (isLoading) return <DashboardSkeleton />;

  const stats = data || { issued_today: 0, total_issued: 0, pending_collection: 0 };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Officer Dashboard"
        description="Issue and manage traffic challans"
        actions={
          <>
            <Button asChild>
              <Link to="/officer/challans/create">
                <PlusCircle className="mr-2 h-4 w-4" />
                New Challan
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/officer/evidence">
                <Upload className="mr-2 h-4 w-4" />
                Upload Evidence
              </Link>
            </Button>
          </>
        }
      />
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard title="Issued Today" value={stats.issued_today} icon={FileWarning} index={0} />
        <StatCard title="Total Issued" value={stats.total_issued} icon={FileWarning} index={1} />
        <StatCard title="Pending Collection" value={formatCurrency(stats.pending_collection)} icon={FileWarning} index={2} />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>My Recent Challans</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Challan #</TableHead>
                <TableHead>Vehicle</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(recent?.items || recent || []).slice(0, 5).map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <Link to={`/officer/challans/${c.id}`} className="text-primary hover:underline">
                      {c.challan_number}
                    </Link>
                  </TableCell>
                  <TableCell>{c.vehicle_registration}</TableCell>
                  <TableCell>{formatCurrency(c.fine_amount)}</TableCell>
                  <TableCell><StatusBadge status={c.status} /></TableCell>
                  <TableCell>{formatDate(c.created_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
