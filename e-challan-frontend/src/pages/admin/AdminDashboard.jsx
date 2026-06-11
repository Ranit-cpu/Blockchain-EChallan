import { useQuery } from '@tanstack/react-query';
import { FileWarning, CreditCard, Car } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { StatCard } from '@/components/common/StatCard';
import { DashboardSkeleton } from '@/components/common/LoadingSkeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChallanTrendChart } from '@/components/charts/ChallanTrendChart';
import { RevenueChart } from '@/components/charts/RevenueChart';
import { analyticsApi } from '@/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Link } from 'react-router-dom';
import { challansApi } from '@/api';
import { unwrapData, unwrapPaginated } from '@/lib/apiResponse';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const demoDashboardData = {
  stats: {
    total_challans: 2847,
    pending_challans: 186,
    total_revenue: 1254800,
    total_vehicles: 9421,
    total_owners: 7318,
  },

  challan_trends: [
    { month: 'Jan', count: 180 },
    { month: 'Feb', count: 245 },
    { month: 'Mar', count: 320 },
    { month: 'Apr', count: 410 },
    { month: 'May', count: 380 },
    { month: 'Jun', count: 520 },
    { month: 'Jul', count: 610 },
    { month: 'Aug', count: 720 },
    { month: 'Sep', count: 650 },
    { month: 'Oct', count: 790 },
    { month: 'Nov', count: 860 },
    { month: 'Dec', count: 940 },
  ],

  revenue_trends: [
    { month: 'Jan', revenue: 85000 },
    { month: 'Feb', revenue: 120000 },
    { month: 'Mar', revenue: 145000 },
    { month: 'Apr', revenue: 185000 },
    { month: 'May', revenue: 220000 },
    { month: 'Jun', revenue: 270000 },
    { month: 'Jul', revenue: 310000 },
    { month: 'Aug', revenue: 355000 },
    { month: 'Sep', revenue: 390000 },
    { month: 'Oct', revenue: 445000 },
    { month: 'Nov', revenue: 510000 },
    { month: 'Dec', revenue: 580000 },
  ],

  recent_challans: [
    {
      id: 1,
      challan_number: 'ECH-2026-1001',
      vehicle_registration: 'WB02AB1234',
      violation_type: 'Overspeeding',
      fine_amount: 1000,
      status: 'paid',
      created_at: '2026-05-28T10:00:00',
    },
    {
      id: 2,
      challan_number: 'ECH-2026-1002',
      vehicle_registration: 'WB20CD5678',
      violation_type: 'Signal Jump',
      fine_amount: 1500,
      status: 'pending',
      created_at: '2026-05-29T12:30:00',
    },
    {
      id: 3,
      challan_number: 'ECH-2026-1003',
      vehicle_registration: 'WB10EF9988',
      violation_type: 'No Helmet',
      fine_amount: 500,
      status: 'paid',
      created_at: '2026-05-29T15:45:00',
    },
    {
      id: 4,
      challan_number: 'ECH-2026-1004',
      vehicle_registration: 'WB04GH4567',
      violation_type: 'Wrong Parking',
      fine_amount: 750,
      status: 'disputed',
      created_at: '2026-05-30T09:15:00',
    },
    {
      id: 5,
      challan_number: 'ECH-2026-1005',
      vehicle_registration: 'WB12XY9876',
      violation_type: 'Red Light Violation',
      fine_amount: 2000,
      status: 'paid',
      created_at: '2026-05-30T11:20:00',
    },
  ],
};

export default function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: async () => {
      const [statsRes, listRes] = await Promise.all([
        challansApi.getStats(),
        challansApi.list({ page: 1, page_size: 5 }),
      ]);
      const stats = unwrapData(statsRes) ?? {};
      const { items: recent_challans = [] } = unwrapPaginated(listRes) ?? {};
      return { stats, recent_challans, challan_trends: [], revenue_trends: [] };
    },
  });

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  const hasRealData =
    data &&
    (
      (data?.stats?.total_challans ?? 0) > 0 ||
      (data?.challan_trends?.length ?? 0) > 0 ||
      (data?.revenue_trends?.length ?? 0) > 0 ||
      (data?.recent_challans?.length ?? 0) > 0
    );

  const dashboardData = hasRealData ? data : demoDashboardData;
  const stats = dashboardData.stats;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Admin Dashboard"
        description="Overview of the e-Challan system"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Challans"
          value={stats.total_challans}
          icon={FileWarning}
          index={0}
        />

        <StatCard
          title="Pending"
          value={stats.pending_challans}
          icon={FileWarning}
          index={1}
        />

        <StatCard
          title="Revenue"
          value={formatCurrency(stats.total_revenue)}
          icon={CreditCard}
          index={2}
        />

        <StatCard
          title="Vehicles"
          value={stats.total_vehicles}
          icon={Car}
          description={`${stats.total_owners} owners`}
          index={3}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Challan Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ChallanTrendChart
              data={dashboardData.challan_trends}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Revenue Collection</CardTitle>
          </CardHeader>
          <CardContent>
            <RevenueChart
              data={dashboardData.revenue_trends}
            />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Challans</CardTitle>

          <Link
            to="/admin/challans"
            className="text-sm text-primary hover:underline"
          >
            View all
          </Link>
        </CardHeader>

        <CardContent>
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
              {dashboardData.recent_challans.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>
                    <Link
                      to={`/admin/challans/${c.id}`}
                      className="font-medium text-primary hover:underline"
                    >
                      {c.challan_number}
                    </Link>
                  </TableCell>

                  <TableCell>
                    {c.vehicle_registration}
                  </TableCell>

                  <TableCell>
                    {c.violation_type}
                  </TableCell>

                  <TableCell>
                    {formatCurrency(c.fine_amount)}
                  </TableCell>

                  <TableCell>
                    <StatusBadge status={c.status} />
                  </TableCell>

                  <TableCell>
                    {formatDate(c.created_at)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}