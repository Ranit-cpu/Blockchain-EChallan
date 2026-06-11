import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ShieldCheck, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { verifyChallanSchema } from '@/schemas/challan.schema';
import { blockchainApi } from '@/api';
import { StatusBadge } from '@/components/common/StatusBadge';
import { BlockchainHash } from '@/components/common/BlockchainHash';
import { formatCurrency, formatDate } from '@/lib/utils';
import { challansApi } from '@/api';
import { unwrapData } from '@/lib/apiResponse';

export default function VerifyPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(verifyChallanSchema),
  });

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const { data: res } = await blockchainApi.verifyChallan(data.challan_number);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="Verify Challan" description="Verify authenticity using blockchain records" />
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5" />
            Challan Verification
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="challan_number">Challan Number</Label>
              <Input id="challan_number" placeholder="ECH-2024-00001" {...register('challan_number')} />
              {errors.challan_number && <p className="text-sm text-destructive">{errors.challan_number.message}</p>}
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ShieldCheck className="mr-2 h-4 w-4" />}
              Verify on Blockchain
            </Button>
          </form>
        </CardContent>
      </Card>
      {error && (
        <Card className="border-destructive">
          <CardContent className="flex items-center gap-2 pt-6 text-destructive">
            <XCircle className="h-5 w-5" />
            {error}
          </CardContent>
        </Card>
      )}
      {result && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="flex items-center gap-2">
              {result.verified ? (
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              ) : (
                <XCircle className="h-6 w-6 text-destructive" />
              )}
              <span className="font-semibold">{result.verified ? 'Verified Authentic' : 'Not Verified'}</span>
            </div>
            <dl className="grid gap-2 text-sm">
              <div className="flex justify-between"><dt className="text-muted-foreground">Challan</dt><dd>{result.challan_number}</dd></div>
              <div className="flex justify-between"><dt className="text-muted-foreground">Status</dt><dd><StatusBadge status={result.status} /></dd></div>
              <div className="flex justify-between"><dt className="text-muted-foreground">Amount</dt><dd>{formatCurrency(result.fine_amount)}</dd></div>
              <div className="flex justify-between"><dt className="text-muted-foreground">Date</dt><dd>{formatDate(result.created_at)}</dd></div>
              <div className="flex justify-between items-center"><dt className="text-muted-foreground">TX Hash</dt><dd><BlockchainHash hash={result.tx_hash} /></dd></div>
            </dl>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
