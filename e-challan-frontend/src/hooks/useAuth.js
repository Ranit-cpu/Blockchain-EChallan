import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/hooks/useToast';

export function useAuth() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const {
    user,
    isAuthenticated,
    isLoading,
    authChecked,
    login,
    logout,
    fetchMe,
    hasRole,
  } = useAuthStore();

  const handleLogin = useCallback(
    async (credentials) => {
      try {
        const result = await login(credentials);
        toast({ title: 'Welcome back!', description: `Signed in as ${result.user.full_name || result.user.email}` });
        navigate(result.redirectTo, { replace: true });
        return result;
      } catch (error) {
        toast({
          title: 'Login failed',
          description: error.message || 'Invalid credentials',
          variant: 'destructive',
        });
        throw error;
      }
    },
    [login, navigate, toast]
  );

  const handleLogout = useCallback(async () => {
    await logout();
    toast({ title: 'Signed out', description: 'You have been logged out successfully.' });
    navigate('/login', { replace: true });
  }, [logout, navigate, toast]);

  return {
    user,
    isAuthenticated,
    isLoading,
    authChecked,
    login: handleLogin,
    logout: handleLogout,
    fetchMe,
    hasRole,
  };
}
