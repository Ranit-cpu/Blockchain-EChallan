export const ROLES = {
  ADMIN: 'admin',
  OFFICER: 'officer',
  OWNER: 'owner',
};

export const CHALLAN_STATUS = {
  PENDING: 'pending',
  ISSUED: 'issued',
  PAID: 'paid',
  DISPUTED: 'disputed',
  CANCELLED: 'cancelled',
  OVERDUE: 'overdue',
};

export const PAYMENT_STATUS = {
  PENDING: 'pending',
  COMPLETED: 'completed',
  FAILED: 'failed',
  REFUNDED: 'refunded',
};

export const STATUS_COLORS = {
  pending: 'bg-yellow-500/15 text-yellow-700 dark:text-yellow-400 border-yellow-500/30',
  issued: 'bg-blue-500/15 text-blue-700 dark:text-blue-400 border-blue-500/30',
  paid: 'bg-green-500/15 text-green-700 dark:text-green-400 border-green-500/30',
  disputed: 'bg-orange-500/15 text-orange-700 dark:text-orange-400 border-orange-500/30',
  cancelled: 'bg-gray-500/15 text-gray-700 dark:text-gray-400 border-gray-500/30',
  overdue: 'bg-red-500/15 text-red-700 dark:text-red-400 border-red-500/30',
  completed: 'bg-green-500/15 text-green-700 dark:text-green-400 border-green-500/30',
  failed: 'bg-red-500/15 text-red-700 dark:text-red-400 border-red-500/30',
  refunded: 'bg-purple-500/15 text-purple-700 dark:text-purple-400 border-purple-500/30',
};

export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

export const DEFAULT_PAGE_SIZE = 10;

export const VIOLATION_TYPES = [
  'Speeding',
  'Red Light Violation',
  'Illegal Parking',
  'No Helmet',
  'No Seat Belt',
  'Wrong Lane',
  'Drunk Driving',
  'Expired Documents',
  'Other',
];

export const NAV_ITEMS = {
  admin: [
    { label: 'Dashboard', path: '/admin', icon: 'LayoutDashboard' },
    { label: 'Analytics', path: '/admin/analytics', icon: 'BarChart3' },
    { label: 'Vehicles', path: '/admin/vehicles', icon: 'Car' },
    { label: 'Owners', path: '/admin/owners', icon: 'Users' },
    { label: 'Challans', path: '/admin/challans', icon: 'FileWarning' },
    { label: 'Payments', path: '/admin/payments', icon: 'CreditCard' },
    { label: 'Blockchain', path: '/admin/blockchain', icon: 'Link' },
    { label: 'Audit Logs', path: '/admin/audit', icon: 'ScrollText' },
    { label: 'Profile', path: '/profile', icon: 'User' },
  ],
  officer: [
    { label: 'Dashboard', path: '/officer', icon: 'LayoutDashboard' },
    { label: 'Create Challan', path: '/officer/challans/create', icon: 'PlusCircle' },
    { label: 'Challans', path: '/officer/challans', icon: 'FileWarning' },
    { label: 'Vehicles', path: '/officer/vehicles', icon: 'Car' },
    { label: 'Evidence', path: '/officer/evidence', icon: 'Upload' },
    { label: 'Blockchain', path: '/officer/blockchain', icon: 'Link' },
    { label: 'Profile', path: '/profile', icon: 'User' },
  ],
  owner: [
    { label: 'Dashboard', path: '/owner', icon: 'LayoutDashboard' },
    { label: 'My Challans', path: '/owner/challans', icon: 'FileWarning' },
    { label: 'Payments', path: '/owner/payments', icon: 'CreditCard' },
    { label: 'Verify', path: '/owner/verify', icon: 'ShieldCheck' },
    { label: 'Profile', path: '/profile', icon: 'User' },
  ],
};

export const ROLE_DASHBOARD_PATH = {
  admin: '/admin',
  officer: '/officer',
  owner: '/owner',
};
