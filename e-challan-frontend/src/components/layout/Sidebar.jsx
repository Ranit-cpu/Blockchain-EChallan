import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  BarChart3,
  Car,
  Users,
  FileWarning,
  CreditCard,
  Link,
  ScrollText,
  User,
  PlusCircle,
  Upload,
  ShieldCheck,
  X,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { NAV_ITEMS } from '@/lib/constants';
import { useAuthStore } from '@/store/authStore';
import { Separator } from '@/components/ui/separator';

const ICON_MAP = {
  LayoutDashboard,
  BarChart3,
  Car,
  Users,
  FileWarning,
  CreditCard,
  Link,
  ScrollText,
  User,
  PlusCircle,
  Upload,
  ShieldCheck,
};

export function Sidebar({ open, onClose }) {
  const { user } = useAuthStore();
  const items = NAV_ITEMS[user?.role] || [];

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={onClose} aria-hidden />
      )}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-card transition-transform duration-300 lg:static lg:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex h-16 items-center justify-between border-b px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-sm">
              eC
            </div>
            <span className="font-semibold">{import.meta.env.VITE_APP_NAME || 'e-Challan'}</span>
          </div>
          <button type="button" className="lg:hidden rounded-md p-1 hover:bg-muted" onClick={onClose}>
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {items.map((item, index) => {
            const Icon = ICON_MAP[item.icon] || LayoutDashboard;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path.split('/').length <= 2}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  )
                }
              >
                {({ isActive }) => (
                  <motion.div
                    className="flex items-center gap-3 w-full"
                    initial={false}
                    animate={{ x: isActive ? 2 : 0 }}
                  >
                    <Icon className="h-4 w-4 shrink-0" />
                    {item.label}
                  </motion.div>
                )}
              </NavLink>
            );
          })}
        </nav>
        <Separator />
        <div className="p-4">
          <p className="text-xs text-muted-foreground capitalize">{user?.role} portal</p>
          <p className="text-sm font-medium truncate">{user?.full_name || user?.email}</p>
        </div>
      </aside>
    </>
  );
}
