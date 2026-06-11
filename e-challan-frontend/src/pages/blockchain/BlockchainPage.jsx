import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link2, Loader2, CheckCircle2, XCircle, Activity } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BlockchainHash } from '@/components/common/BlockchainHash';
import { StatusBadge } from '@/components/common/StatusBadge';
import { blockchainApi } from '@/api';
import { verifyChallanSchema } from '@/schemas/challan.schema';
import { formatDate } from '@/lib/utils';
import { z } from 'zod';
import { challansApi } from '@/api';
import { unwrapData } from '@/lib/apiResponse';

const txSchema = z.object({
  tx_hash: z.string().min(10, 'Enter a valid transaction hash'),
});

export default function BlockchainPage() {
  const [verifyResult, setVerifyResult] = useState(null);
  const [txResult, setTxResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const { data: networkStatus } = useQuery({
    queryKey: ['blockchain-status'],
    queryFn: async () => {
      const { data } = await blockchainApi.getNetworkStatus();
      return data;
    },
    refetchInterval: 30000,
  });

  const challanForm = useForm({ resolver: zodResolver(verifyChallanSchema) });
  const txForm = useForm({ resolver: zodResolver(txSchema) });

  const verifyChallan = async (formData) => {
    setLoading(true);
    setVerifyResult(null);
    try {
      const res = await challansApi.verify(formData.challan_number);
      setVerifyResult(unwrapData(res));
    } catch (err) {
      setVerifyResult({ verified: false, error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const verifyTx = async (data) => {
    setLoading(true);
    setTxResult(null);
    try {
      const { data: res } = await blockchainApi.verify(data.tx_hash);
      setTxResult(res);
    } catch (err) {
      setTxResult({ verified: false, error: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Blockchain Verification" description="Verify challan authenticity on the blockchain" />
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6 flex items-center gap-3">
            <Activity className={`h-8 w-8 ${networkStatus?.connected ? 'text-green-500' : 'text-red-500'}`} />
            <div>
              <p className="text-sm text-muted-foreground">Network</p>
              <p className="font-semibold">{networkStatus?.connected ? 'Connected' : 'Disconnected'}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Block Height</p>
            <p className="text-2xl font-bold">{networkStatus?.block_height ?? '—'}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Anchored Challans</p>
            <p className="text-2xl font-bold">{networkStatus?.anchored_count ?? '—'}</p>
          </CardContent>
        </Card>
      </div>
      <Tabs defaultValue="challan">
        <TabsList>
          <TabsTrigger value="challan">Verify Challan</TabsTrigger>
          <TabsTrigger value="transaction">Verify Transaction</TabsTrigger>
        </TabsList>
        <TabsContent value="challan">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Link2 className="h-5 w-5" />Challan Verification</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={challanForm.handleSubmit(verifyChallan)} className="flex gap-2 max-w-md">
                <div className="flex-1 space-y-2">
                  <Label>Challan Number</Label>
                  <Input placeholder="ECH-2024-00001" {...challanForm.register('challan_number')} />
                </div>
                <div className="flex items-end">
                  <Button type="submit" disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Verify'}
                  </Button>
                </div>
              </form>
              {verifyResult && (
                <VerificationResult result={verifyResult} type="challan" />
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="transaction">
          <Card>
            <CardHeader>
              <CardTitle>Transaction Verification</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={txForm.handleSubmit(verifyTx)} className="flex gap-2 max-w-lg">
                <div className="flex-1 space-y-2">
                  <Label>Transaction Hash</Label>
                  <Input placeholder="0x..." {...txForm.register('tx_hash')} />
                </div>
                <div className="flex items-end">
                  <Button type="submit" disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Verify'}
                  </Button>
                </div>
              </form>
              {txResult && <VerificationResult result={txResult} type="tx" />}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function VerificationResult({ result, type }) {
  const verified = result.verified !== false && !result.error;
  return (
    <div className={`rounded-lg border p-4 ${verified ? 'border-green-500/30 bg-green-500/5' : 'border-destructive/30 bg-destructive/5'}`}>
      <div className="flex items-center gap-2 mb-3">
        {verified ? <CheckCircle2 className="h-5 w-5 text-green-500" /> : <XCircle className="h-5 w-5 text-destructive" />}
        <span className="font-semibold">{verified ? 'Verified' : result.error || 'Not Verified'}</span>
      </div>
      <dl className="grid gap-2 text-sm">
        {type === 'challan' && (
          <>
            <div className="flex justify-between"><dt className="text-muted-foreground">Challan</dt><dd>{result.challan_number}</dd></div>
            <div className="flex justify-between"><dt className="text-muted-foreground">Status</dt><dd><StatusBadge status={result.status} /></dd></div>
          </>
        )}
        <div className="flex justify-between items-center"><dt className="text-muted-foreground">TX Hash</dt><dd><BlockchainHash hash={result.tx_hash} /></dd></div>
        <div className="flex justify-between"><dt className="text-muted-foreground">Block</dt><dd>{result.block_number || '—'}</dd></div>
        <div className="flex justify-between"><dt className="text-muted-foreground">Timestamp</dt><dd>{formatDate(result.timestamp || result.anchored_at, { time: true })}</dd></div>
      </dl>
    </div>
  );
}
