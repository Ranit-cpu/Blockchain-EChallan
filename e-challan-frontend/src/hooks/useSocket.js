import { useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import { useAuthStore } from '@/store/authStore';

const WS_URL = import.meta.env.VITE_WS_URL || '';

export function useSocket() {
  const socketRef = useRef(null);
  const { user, addNotification } = useAuthStore();

  useEffect(() => {
    if (!user?.id || !WS_URL) return undefined;

    const socket = io(WS_URL, {
      withCredentials: true,
      transports: ['websocket', 'polling'],
      query: { userId: user.id, role: user.role },
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      socket.emit('join', { userId: user.id, role: user.role });
    });

    socket.on('notification', (payload) => {
      addNotification({
        title: payload.title || 'New notification',
        description: payload.message || payload.description,
        type: payload.type || 'info',
      });
    });

    socket.on('challan:created', (payload) => {
      addNotification({
        title: 'New Challan',
        description: `Challan ${payload.challan_number} has been created`,
        type: 'info',
      });
    });

    socket.on('payment:completed', (payload) => {
      addNotification({
        title: 'Payment Received',
        description: `Payment of ₹${payload.amount} completed`,
        type: 'success',
      });
    });

    socket.on('blockchain:anchored', (payload) => {
      addNotification({
        title: 'Blockchain Anchored',
        description: `Challan anchored with tx ${payload.tx_hash?.slice(0, 10)}...`,
        type: 'success',
      });
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [user?.id, user?.role, addNotification]);

  return socketRef;
}
