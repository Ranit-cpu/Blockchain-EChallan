import { lazy, Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { PageSkeleton } from '@/components/common/LoadingSkeleton';
import { ROLES } from '@/lib/constants';

const LoginPage = lazy(() => import('@/pages/auth/LoginPage'));
const AdminDashboard = lazy(() => import('@/pages/admin/AdminDashboard'));
const OfficerDashboard = lazy(() => import('@/pages/officer/OfficerDashboard'));
const OwnerDashboard = lazy(() => import('@/pages/owner/OwnerDashboard'));
const VehiclesPage = lazy(() => import('@/pages/vehicles/VehiclesPage'));
const VehicleFormPage = lazy(() => import('@/pages/vehicles/VehicleFormPage'));
const OwnersPage = lazy(() => import('@/pages/owners/OwnersPage'));
const OwnerFormPage = lazy(() => import('@/pages/owners/OwnerFormPage'));
const ChallansPage = lazy(() => import('@/pages/challans/ChallansPage'));
const ChallanCreatePage = lazy(() => import('@/pages/challans/ChallanCreatePage'));
const ChallanDetailPage = lazy(() => import('@/pages/challans/ChallanDetailPage'));
const PaymentsPage = lazy(() => import('@/pages/payments/PaymentsPage'));
const EvidencePage = lazy(() => import('@/pages/evidence/EvidencePage'));
const BlockchainPage = lazy(() => import('@/pages/blockchain/BlockchainPage'));
const AuditLogsPage = lazy(() => import('@/pages/audit/AuditLogsPage'));
const ProfilePage = lazy(() => import('@/pages/profile/ProfilePage'));
const AnalyticsPage = lazy(() => import('@/pages/analytics/AnalyticsPage'));
const VerifyPage = lazy(() => import('@/pages/owner/VerifyPage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));

function LazyPage({ children }) {
  return <Suspense fallback={<PageSkeleton />}>{children}</Suspense>;
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <AuthLayout />,
    children: [
      {
        index: true,
        element: (
          <LazyPage>
            <LoginPage />
          </LazyPage>
        ),
      },
    ],
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate to="/login" replace /> },
      {
        path: 'admin',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <AdminDashboard />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/analytics',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <AnalyticsPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/vehicles',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <VehiclesPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/vehicles/new',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <VehicleFormPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/vehicles/:id/edit',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <VehicleFormPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/owners',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <OwnersPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/owners/new',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <OwnerFormPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/owners/:id/edit',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <OwnerFormPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/challans',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <ChallansPage role={ROLES.ADMIN} />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/challans/:id',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <ChallanDetailPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/payments',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <PaymentsPage role={ROLES.ADMIN} />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/blockchain',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <BlockchainPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'admin/audit',
        element: (
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <LazyPage>
              <AuditLogsPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'officer',
        element: (
          <ProtectedRoute roles={[ROLES.OFFICER]}>
            <LazyPage>
              <OfficerDashboard />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'officer/challans',
        element: (
          <ProtectedRoute roles={[ROLES.OFFICER]}>
            <LazyPage>
              <ChallansPage role={ROLES.OFFICER} />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'officer/challans/create',
        element: (
          <ProtectedRoute roles={[ROLES.OFFICER]}>
            <LazyPage>
              <ChallanCreatePage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'officer/challans/:id',
        element: (
          <ProtectedRoute roles={[ROLES.OFFICER]}>
            <LazyPage>
              <ChallanDetailPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'officer/vehicles',
        element: (
          <ProtectedRoute roles={[ROLES.OFFICER]}>
            <LazyPage>
              <VehiclesPage readOnly />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'officer/evidence',
        element: (
          <ProtectedRoute roles={[ROLES.OFFICER]}>
            <LazyPage>
              <EvidencePage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'officer/blockchain',
        element: (
          <ProtectedRoute roles={[ROLES.OFFICER]}>
            <LazyPage>
              <BlockchainPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'owner',
        element: (
          <ProtectedRoute roles={[ROLES.OWNER]}>
            <LazyPage>
              <OwnerDashboard />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'owner/challans',
        element: (
          <ProtectedRoute roles={[ROLES.OWNER]}>
            <LazyPage>
              <ChallansPage role={ROLES.OWNER} />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'owner/challans/:id',
        element: (
          <ProtectedRoute roles={[ROLES.OWNER]}>
            <LazyPage>
              <ChallanDetailPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'owner/payments',
        element: (
          <ProtectedRoute roles={[ROLES.OWNER]}>
            <LazyPage>
              <PaymentsPage role={ROLES.OWNER} />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'owner/verify',
        element: (
          <ProtectedRoute roles={[ROLES.OWNER]}>
            <LazyPage>
              <VerifyPage />
            </LazyPage>
          </ProtectedRoute>
        ),
      },
      {
        path: 'profile',
        element: (
          <LazyPage>
            <ProfilePage />
          </LazyPage>
        ),
      },
    ],
  },
  {
    path: '*',
    element: (
      <LazyPage>
        <NotFoundPage />
      </LazyPage>
    ),
  },
]);
