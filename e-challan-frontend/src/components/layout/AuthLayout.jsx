import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';

export function AuthLayout() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:flex flex-col justify-between bg-primary p-10 text-primary-foreground">
        <div>
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/20 font-bold">eC</div>
          <h1 className="mt-8 text-3xl font-bold">{import.meta.env.VITE_APP_NAME || 'e-Challan'}</h1>
          <p className="mt-2 text-primary-foreground/80 max-w-md">
            Blockchain-powered electronic challan management system for transparent, verifiable traffic enforcement.
          </p>
        </div>
        <div className="space-y-4 text-sm text-primary-foreground/70">
          <p>✓ Immutable blockchain records</p>
          <p>✓ Real-time notifications</p>
          <p>✓ Secure cookie-based sessions</p>
        </div>
      </div>
      <div className="flex items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <Outlet />
        </motion.div>
      </div>
    </div>
  );
}
