import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export const libraryAPI = {
  getHealth: () => api.get('/api/health'),
  getBooks: () => api.get('/api/books'),
  // We'll add more methods as we build the API
};