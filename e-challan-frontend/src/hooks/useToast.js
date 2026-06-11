import { useToast as useToastContext } from '@/providers/ToastProvider';

export function useToast() {
  return useToastContext();
}
