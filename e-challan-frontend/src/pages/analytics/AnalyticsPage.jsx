import { useQuery } from '@tanstack/react-query';
import { PageHeader } from '@/components/common/PageHeader';
import { DashboardSkeleton } from '@/components/common/LoadingSkeleton';
import { StatCard } from '@/components/common/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChallanTrendChart } from '@/components/charts/ChallanTrendChart';
import { RevenueChart } from '@/components/charts/RevenueChart';
import { ViolationPieChart } from '@/components/charts/ViolationPieChart';
import { challansApi } from '@/api';
import { formatCurrency } from '@/lib/utils';
import { unwrapData, unwrapPaginated } from '@/lib/apiResponse';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  AlertTriangle,
} from 'lucide-react';

const demoAnalytics = {
  dashboard: {
    total_challans: 2847,
    pending_challans: 186,
    paid_challans: 2600,
    total_revenue: 1254800,
    collection_rate: 93.4,
    disputes: 42,
    revenue_growth: 18.5,
    challan_growth: 12.8,
    challan_trends: [
      { month: 'Jan', count: 180 },
      { month: 'Feb', count: 245 },
      { month: 'Mar', count: 320 },
    ],
  },
  revenue: [
    { month: 'Jan', revenue: 85000 },
    { month: 'Feb', revenue: 120000 },
    { month: 'Mar', revenue: 145000 },
  ],
  violations: [
    { name: 'Overspeeding', value: 820 },
    { name: 'Signal Jump', value: 540 },
  ],
};

function aggregateByMonth(challans) {
  const buckets = new Map();

  for (const c of challans) {
    if (!c.created_at) continue;
    const month = new Date(c.created_at).toLocaleString('en-IN', { month: 'short' });
    const row = buckets.get(month) ?? { month, count: 0, revenue: 0 };
    row.count += 1;
    if (c.status === 'paid') {
      row.revenue += Number(c.fine_amount ?? 0);
    }
    buckets.set(month, row);
  }

  return [...buckets.values()];
}

function aggregateViolationCounts(challans) {
  const counts = new Map();

  for (const c of challans) {
    const name = c.violation?.name ?? c.violation?.code ?? 'Unknown';
    counts.set(name, (counts.get(name) ?? 0) + 1);
  }

  return [...counts.entries()].map(([name, value]) => ({ name, value }));
}

function buildAnalyticsFromApi(stats, challans) {
  const total = stats.total_challans ?? 0;
  const paid = stats.paid_challans ?? 0;
  const monthly = aggregateByMonth(challans);

  return {
    dashboard: {
      ...stats,
      collection_rate: total > 0 ? Math.round((paid / total) * 1000) / 10 : 0,
      disputes: challans.filter((c) => c.is_disputed).length,
      revenue_growth: 0,
      challan_growth: 0,
      challan_trends: monthly.map(({ month, count }) => ({ month, count })),
    },
    revenue: monthly.map(({ month, revenue }) => ({ month, revenue })),
    violations: aggregateViolationCounts(challans),
  };
}

export default function AnalyticsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: async () => {
      const [statsRes, listRes] = await Promise.all([
        challansApi.getStats(),
        challansApi.list({ page: 1, page_size: 100 }),
      ]);

      const stats = unwrapData(statsRes) ?? {};
      const challans = unwrapPaginated(listRes)?.items ?? [];

      return buildAnalyticsFromApi(stats, challans);
    },
  });

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  const hasRealData =
    !isError &&
    data &&
    ((data.dashboard?.total_challans ?? 0) > 0 ||
      (data.dashboard?.challan_trends?.length ?? 0) > 0 ||
      (data.violations?.length ?? 0) > 0);

  const analyticsData = hasRealData ? data : demoAnalytics;
  const stats = analyticsData.dashboard;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics"
        description="Comprehensive system analytics and insights"
      />

      {!hasRealData && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
          Showing demo analytics data (backend empty or stats require admin).
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Revenue"
          value={formatCurrency(stats.total_revenue)}
          icon={DollarSign}
          trend={stats.revenue_growth}
          index={0}
        />
        <StatCard
          title="Challans Issued"
          value={stats.total_challans}
          icon={BarChart3}
          trend={stats.challan_growth}
          index={1}
        />
        <StatCard
          title="Collection Rate"
          value={`${stats.collection_rate ?? 0}%`}
          icon={TrendingUp}
          index={2}
        />
        <StatCard
          title="Disputes"
          value={stats.disputes ?? 0}
          icon={AlertTriangle}
          index={3}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-0 shadow-xl bg-gradient-to-br from-background via-background to-blue-500/5">
          <CardHeader>
            <CardTitle>Challan Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ChallanTrendChart data={stats.challan_trends ?? []} />
          </CardContent>
        </Card>

        <Card className="border-0 shadow-xl bg-gradient-to-br from-background via-background to-emerald-500/5">
          <CardHeader>
            <CardTitle>Revenue Collection</CardTitle>
          </CardHeader>
          <CardContent>
            <RevenueChart data={analyticsData.revenue ?? []} />
          </CardContent>
        </Card>
      </div>

      <Card className="border-0 shadow-xl bg-gradient-to-br from-background via-background to-violet-500/5">
        <CardHeader>
          <CardTitle>Violation Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <ViolationPieChart data={analyticsData.violations ?? []} />
        </CardContent>
      </Card>
    </div>
  );
}