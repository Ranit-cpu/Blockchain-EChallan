import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '@/api/auth.api';
import { ROLE_DASHBOARD_PATH } from '@/lib/constants';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      authChecked: false,
      notifications: [],

      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
        }),

      setAuthChecked: (checked) => set({ authChecked: checked }),

      setLoading: (isLoading) => set({ isLoading }),

      addNotification: (notification) =>
        set((state) => ({
          notifications: [
            {
              id: crypto.randomUUID(),
              timestamp: new Date().toISOString(),
              read: false,
              ...notification,
            },
            ...state.notifications,
          ].slice(0, 50),
        })),

      markNotificationRead: (id) =>
        set((state) => ({
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
        })),

      markAllNotificationsRead: () =>
        set((state) => ({
          notifications: state.notifications.map((n) => ({ ...n, read: true })),
        })),

      clearNotifications: () => set({ notifications: [] }),

      login: async (credentials) => {
        set({ isLoading: true });

        try {
          const { data: body } = await authApi.login(credentials);

          const rawUser = body.data ?? body.user ?? body;

          const user = {
            ...rawUser,
            role:
              typeof rawUser.role === 'object'
                ? String(rawUser.role.name).toLowerCase()
                : String(rawUser.role ?? '').toLowerCase(),
          };

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            authChecked: true,
          });

          return {
            user,
            redirectTo:
              ROLE_DASHBOARD_PATH[user.role] || '/login',
          };
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch {
          /* session may already be invalid */
        } finally {
          get().clearAuth();
        }
      },

      fetchMe: async () => {
        set({ isLoading: true });

        try {
          const { data } = await authApi.me();

          const rawUser = data.data ?? data.user ?? data;

          const user = {
            ...rawUser,
            role:
              typeof rawUser.role === 'object'
                ? String(rawUser.role.name).toLowerCase()
                : String(rawUser.role ?? '').toLowerCase(),
          };

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            authChecked: true,
          });

          return user;
        } catch {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            authChecked: true,
          });

          return null;
        }
      },

      clearAuth: () =>
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        }),

      hasRole: (...roles) => {
        const { user } = get();

        return user && roles.includes(user.role);
      },
    }),
    {
      name: 'echallan-auth',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
