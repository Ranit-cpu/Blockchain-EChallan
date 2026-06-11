import { cn } from '@/lib/utils';
import { STATUS_COLORS } from '@/lib/constants';

export function StatusBadge({ status, className }) {
  const normalized = (status || 'pending').toLowerCase();
  const colorClass = STATUS_COLORS[normalized] || STATUS_COLORS.pending;

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize',
        colorClass,
        className
      )}
    >
      {normalized.replace(/_/g, ' ')}
    </span>
  );
}
