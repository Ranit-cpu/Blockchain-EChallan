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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { vehicleSchema } from '@/schemas/vehicle.schema';
import { vehiclesApi } from '@/api';
import { unwrapData } from '@/lib/apiResponse';
import { useToast } from '@/hooks/useToast';

export default function VehicleFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const isEdit = Boolean(id);

  const { data: vehicle } = useQuery({
    queryKey: ['vehicle', id],
    queryFn: async () => {
      const res = await vehiclesApi.getById(id);
      return unwrapData(res);
    },
    enabled: isEdit,
  });

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    resolver: zodResolver(vehicleSchema),
    defaultValues: {
      registration_number: '',
      make: '',
      model: '',
      year: new Date().getFullYear(),
      vehicle_type: 'four_wheeler',
    },
  });

  useEffect(() => {
    if (vehicle) {
      Object.keys(vehicle).forEach((key) => setValue(key, vehicle[key]));
    }
  }, [vehicle, setValue]);

  const mutation = useMutation({
    mutationFn: (data) => (isEdit ? vehiclesApi.update(id, data) : vehiclesApi.create(data)),
    onSuccess: () => {
      toast({ title: isEdit ? 'Vehicle updated' : 'Vehicle created' });
      navigate('/admin/vehicles');
    },
    onError: (err) => toast({ title: 'Error', description: err.message, variant: 'destructive' }),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title={isEdit ? 'Edit Vehicle' : 'Add Vehicle'} />
      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Registration Number</Label>
                <Input {...register('registration_number')} />
                {errors.registration_number && <p className="text-sm text-destructive">{errors.registration_number.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Vehicle Type</Label>
                <Select value={watch('vehicle_type')} onValueChange={(v) => setValue('vehicle_type', v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="two_wheeler">Two Wheeler</SelectItem>
                    <SelectItem value="four_wheeler">Four Wheeler</SelectItem>
                    <SelectItem value="commercial">Commercial</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Make</Label>
                <Input {...register('make')} />
                {errors.make && <p className="text-sm text-destructive">{errors.make.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Model</Label>
                <Input {...register('model')} />
                {errors.model && <p className="text-sm text-destructive">{errors.model.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Year</Label>
                <Input type="number" {...register('year')} />
              </div>
              <div className="space-y-2">
                <Label>Color</Label>
                <Input {...register('color')} />
              </div>
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isEdit ? 'Update' : 'Create'}
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate('/admin/vehicles')}>Cancel</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
