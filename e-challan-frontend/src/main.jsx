import { StrictMode, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { AppProviders } from '@/providers/AppProviders';
import { router } from '@/routes';
import { useAuthStore } from '@/store/authStore';
import { useThemeStore } from '@/store/themeStore';
import './index.css';

function AppBootstrap() {
  const fetchMe = useAuthStore((s) => s.fetchMe);
  const initTheme = useThemeStore((s) => s.initTheme);

  useEffect(() => {
    initTheme();
    fetchMe();
  }, [fetchMe, initTheme]);

  return <RouterProvider router={router} />;
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AppProviders>
      <AppBootstrap />
    </AppProviders>
  </StrictMode>
);
