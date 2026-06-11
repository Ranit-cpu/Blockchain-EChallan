import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { challanCreateSchema } from '@/schemas/challan.schema';
import { challansApi } from '@/api';
import { useToast } from '@/hooks/useToast';
import { VIOLATION_TYPES } from '@/lib/constants';

export default function ChallanCreatePage() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    resolver: zodResolver(challanCreateSchema),
    defaultValues: {
      violation_date: new Date().toISOString().split('T')[0],
      fine_amount: 500,
    },
  });

  const mutation = useMutation({
    mutationFn: (data) => challansApi.create(data),
    onSuccess: (res) => {
      const challan = res.data;
      toast({ title: 'Challan created', description: `Challan ${challan.challan_number} issued successfully` });
      navigate(`/officer/challans/${challan.id}`);
    },
    onError: (err) => toast({ title: 'Error', description: err.message, variant: 'destructive' }),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="Create Challan" description="Issue a new traffic violation challan" />
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Vehicle Registration</Label>
                <Input placeholder="MH12AB1234" {...register('vehicle_registration')} />
                {errors.vehicle_registration && <p className="text-sm text-destructive">{errors.vehicle_registration.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Violation Type</Label>
                <Select value={watch('violation_type') || ''} onValueChange={(v) => setValue('violation_type', v)}>
                  <SelectTrigger><SelectValue placeholder="Select violation" /></SelectTrigger>
                  <SelectContent>
                    {VIOLATION_TYPES.map((v) => (
                      <SelectItem key={v} value={v}>{v}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.violation_type && <p className="text-sm text-destructive">{errors.violation_type.message}</p>}
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Description</Label>
                <Textarea {...register('violation_description')} />
                {errors.violation_description && <p className="text-sm text-destructive">{errors.violation_description.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Location</Label>
                <Input {...register('location')} />
                {errors.location && <p className="text-sm text-destructive">{errors.location.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Fine Amount (₹)</Label>
                <Input type="number" {...register('fine_amount')} />
                {errors.fine_amount && <p className="text-sm text-destructive">{errors.fine_amount.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Violation Date</Label>
                <Input type="date" {...register('violation_date')} />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Officer Notes</Label>
                <Textarea {...register('officer_notes')} />
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Issue Challan
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate('/officer/challans')}>Cancel</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
