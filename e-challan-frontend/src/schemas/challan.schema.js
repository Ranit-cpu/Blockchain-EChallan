import { z } from 'zod';

export const challanCreateSchema = z.object({
  vehicle_registration: z.string().min(4, 'Registration number is required'),
  violation_code: z.string().min(1, 'Violation is required'),
  location: z.string().min(5, 'Location is required'),
  violation_date: z.string().min(1, 'Violation date is required'),
  notes: z.string().optional(),
  evidenceFile: z.any().optional(),
});

export const challanFilterSchema = z.object({
  status: z.string().optional(),
  violation_code: z.string().optional(),
  from_date: z.string().optional(),
  to_date: z.string().optional(),
  vehicle_registration: z.string().optional(),
});

export const verifyChallanSchema = z.object({
  challan_number: z.string().min(5, 'Enter a valid challan number'),
});

export const disputeSchema = z.object({
  reason: z.string().min(20, 'Please provide a detailed reason (min 20 characters)'),
});