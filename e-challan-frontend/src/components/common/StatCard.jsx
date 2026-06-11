import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

export function StatCard({ title, value, description, icon: Icon, trend, className, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className={cn('overflow-hidden', className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          {Icon && (
            <div className="rounded-lg bg-primary/10 p-2 text-primary">
              <Icon className="h-4 w-4" />
            </div>
          )}
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          {(description || trend) && (
            <p className="mt-1 text-xs text-muted-foreground">
              {trend && (
                <span className={cn('mr-1 font-medium', trend > 0 ? 'text-green-600' : 'text-red-600')}>
                  {trend > 0 ? '+' : ''}
                  {trend}%
                </span>
              )}
              {description}
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
