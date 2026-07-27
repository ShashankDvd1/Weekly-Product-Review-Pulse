/**
 * Pulse Intelligence — Frontend Configuration
 *
 * Dynamically resolves the backend API URL based on the current hostname
 * so the app works seamlessly when accessed from other devices (like phones)
 * on the same local network.
 */
export const getBackendUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  const hostname = window.location.hostname;
  if (hostname && hostname !== 'localhost' && hostname !== '127.0.0.1') {
    return `http://${hostname}:8000`;
  }
  return 'http://127.0.0.1:8000';
};
