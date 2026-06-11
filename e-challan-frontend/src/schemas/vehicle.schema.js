import { z } from 'zod';

export const vehicleSchema = z.object({
  registration_number: z
    .string()
    .min(4, 'Registration number is required')
    .max(15, 'Registration number too long'),
  make: z.string().min(1, 'Make is required'),
  model: z.string().min(1, 'Model is required'),
  year: z.coerce.number().min(1990).max(new Date().getFullYear() + 1),
  color: z.string().optional(),
  vehicle_type: z.enum(['two_wheeler', 'four_wheeler', 'commercial', 'other']),
  owner_id: z.string().optional(),
  chassis_number: z.string().optional(),
  engine_number: z.string().optional(),
});
