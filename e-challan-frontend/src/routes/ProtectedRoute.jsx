import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { DashboardSkeleton } from '@/components/common/LoadingSkeleton';

export function ProtectedRoute({
  children,
  roles = [],
}) {
  const {
    isAuthenticated,
    user,
    authChecked,
    isLoading,
  } = useAuthStore();

  const location = useLocation();

  if (!authChecked || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <div className="w-full max-w-4xl">
          <DashboardSkeleton />
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <Navigate
        to="/login"
        state={{ from: location }}
        replace
      />
    );
  }

  if (
    roles.length > 0 &&
    !roles.includes(user.role)
  ) {
    const redirectMap = {
      admin: '/admin',
      officer: '/officer',
      owner: '/owner',
    };

    return (
      <Navigate
        to={redirectMap[user.role] || '/login'}
        replace
      />
    );
  }

  return children;
}