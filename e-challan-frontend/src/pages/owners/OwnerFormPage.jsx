import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ownerSchema } from '@/schemas/owner.schema';
import { ownersApi } from '@/api';
import { unwrapData } from '@/lib/apiResponse';
import { useToast } from '@/hooks/useToast';

export default function OwnerFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const isEdit = Boolean(id);

  const { data: owner } = useQuery({
    queryKey: ['owner', id],
    queryFn: async () => {
      const res = await ownersApi.getById(id);
      return unwrapData(res);
    },
    enabled: isEdit,
  });

  const { register, handleSubmit, setValue, formState: { errors } } = useForm({
    resolver: zodResolver(ownerSchema),
  });

  useEffect(() => {
    if (owner) Object.keys(owner).forEach((key) => setValue(key, owner[key] ?? ''));
  }, [owner, setValue]);

  const mutation = useMutation({
    mutationFn: (data) => (isEdit ? ownersApi.update(id, data) : ownersApi.create(data)),
    onSuccess: () => {
      toast({ title: isEdit ? 'Owner updated' : 'Owner created' });
      navigate('/admin/owners');
    },
    onError: (err) => toast({ title: 'Error', description: err.message, variant: 'destructive' }),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title={isEdit ? 'Edit Owner' : 'Add Owner'} />
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2 sm:col-span-2">
                <Label>Full Name</Label>
                <Input {...register('full_name')} />
                {errors.full_name && <p className="text-sm text-destructive">{errors.full_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input {...register('phone')} />
                {errors.phone && <p className="text-sm text-destructive">{errors.phone.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input type="email" {...register('email')} />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Address</Label>
                <Textarea {...register('address')} />
              </div>
              <div className="space-y-2">
                <Label>City</Label>
                <Input {...register('city')} />
              </div>
              <div className="space-y-2">
                <Label>State</Label>
                <Input {...register('state')} />
              </div>
              <div className="space-y-2">
                <Label>Pincode</Label>
                <Input {...register('pincode')} />
                {errors.pincode && <p className="text-sm text-destructive">{errors.pincode.message}</p>}
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isEdit ? 'Update' : 'Create'}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate('/admin/owners')}>Cancel</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
