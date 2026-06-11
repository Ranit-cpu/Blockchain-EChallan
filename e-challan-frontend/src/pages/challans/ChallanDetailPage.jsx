import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Shield, Upload } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { StatusBadge } from '@/components/common/StatusBadge';
import { BlockchainHash } from '@/components/common/BlockchainHash';
import { PageSkeleton } from '@/components/common/LoadingSkeleton';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { challansApi, evidenceApi } from '@/api';
import { formatCurrency, formatDate } from '@/lib/utils';
import { useAuthStore } from '@/store/authStore';
import { ROLES } from '@/lib/constants';
import { challansApi } from '@/api';
import { unwrapData } from '@/lib/apiResponse';

export default function ChallanDetailPage() {
  const { id } = useParams();
  const { user } = useAuthStore();

  const { data: challan, isLoading } = useQuery({
    queryKey: ['challan', id],
    queryFn: async () => {
      const { data } = await challansApi.getById(id);
      return data;
    },
  });

  // const { data: evidence } = useQuery({
  //   queryKey: ['challan-evidence', id],
  //   queryFn: async () => {
  //     const { data } = await evidenceApi.getByChallan(id);
  //     return data;
  //   },
  //   enabled: Boolean(id),
  // });

  if (isLoading) return <PageSkeleton />;
  if (!challan) return <p>Challan not found</p>;

  const evidenceList = evidence?.items || evidence || [];
  const canPay = user?.role === ROLES.OWNER && ['pending', 'issued', 'overdue'].includes(challan.status);

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Challan ${challan.challan_number}`}
        description={challan.violation_type}
        actions={
          canPay && (
            <Button asChild>
              <Link to={`/owner/payments?challan=${challan.id}`}>Pay Now</Link>
            </Button>
          )
        }
      />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Violation Details</CardTitle>
              <StatusBadge status={challan.status} />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <dl className="grid gap-3 sm:grid-cols-2 text-sm">
              <div><dt className="text-muted-foreground">Vehicle</dt><dd className="font-medium">{challan.vehicle_registration}</dd></div>
              <div><dt className="text-muted-foreground">Fine Amount</dt><dd className="font-medium">{formatCurrency(challan.fine_amount)}</dd></div>
              <div><dt className="text-muted-foreground">Location</dt><dd>{challan.location}</dd></div>
              <div><dt className="text-muted-foreground">Violation Date</dt><dd>{formatDate(challan.violation_date)}</dd></div>
              <div><dt className="text-muted-foreground">Issued</dt><dd>{formatDate(challan.created_at, { time: true })}</dd></div>
              <div><dt className="text-muted-foreground">Officer</dt><dd>{challan.officer_name || '—'}</dd></div>
            </dl>
            <Separator />
            <div>
              <p className="text-sm text-muted-foreground mb-1">Description</p>
              <p>{challan.violation_description}</p>
            </div>
            {challan.officer_notes && (
              <div>
                <p className="text-sm text-muted-foreground mb-1">Officer Notes</p>
                <p>{challan.officer_notes}</p>
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Blockchain
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div>
              <p className="text-muted-foreground mb-1">Transaction Hash</p>
              <BlockchainHash hash={challan.tx_hash} />
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Block Number</p>
              <p className="font-mono">{challan.block_number || '—'}</p>
            </div>
            <div>
              <p className="text-muted-foreground mb-1">Anchored At</p>
              <p>{formatDate(challan.anchored_at, { time: true })}</p>
            </div>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-4 w-4" />
            Evidence ({evidenceList.length})
          </CardTitle>
          {user?.role === ROLES.OFFICER && (
            <Button variant="outline" size="sm" asChild>
              <Link to="/officer/evidence">Upload</Link>
            </Button>
          )}
        </CardHeader>
        <CardContent>
          {evidenceList.length === 0 ? (
            <p className="text-sm text-muted-foreground">No evidence uploaded</p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {evidenceList.map((e) => (
                <a
                  key={e.id}
                  href={e.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-lg border p-3 hover:bg-muted transition-colors"
                >
                  <p className="text-sm font-medium truncate">{e.file_name}</p>
                  <p className="text-xs text-muted-foreground">{formatDate(e.created_at)}</p>
                </a>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
