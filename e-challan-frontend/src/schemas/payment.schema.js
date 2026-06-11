import { z } from 'zod';

export const paymentSchema = z.object({
  challan_id: z.string().min(1, 'Challan is required'),
  payment_method: z.enum(['upi', 'card', 'netbanking', 'wallet']),
  amount: z.coerce.number().positive('Amount must be positive'),
});
