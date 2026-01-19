export const config = {
  apiUrl: import.meta.env.PROD
    ? 'https://flight-search-engine-206655984617.europe-west1.run.app'
    : (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8080'),

  isProd: import.meta.env.PROD
};