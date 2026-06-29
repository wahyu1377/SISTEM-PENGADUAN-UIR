import axios from 'axios'

// API Base URL Configuration
const PRODUCTION_API_URL = 'https://uir-complaints-backend.onrender.com/api'

const getBaseURL = () => {
  // Always use hardcoded production URL
  return PRODUCTION_API_URL
}

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 15000
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - simple error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Just reject the error - don't try to redirect
    // Let the component that made the request handle the error
    return Promise.reject(error)
  }
)

export const authService = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
  changePassword: (data) => api.post('/auth/change-password', data)
}

export const complaintService = {
  getMyComplaints: (params) => api.get('/complaints', { params }),
  getComplaint: (id) => api.get(`/complaints/${id}`),
  createComplaint: (data) => api.post('/complaints', data),
  getAllComplaints: (params) => api.get('/admin/complaints', { params }),
  getAdminComplaint: (id) => api.get(`/admin/complaints/${id}`),
  updateComplaint: (id, data) => api.put(`/admin/complaints/${id}`, data),
  updateStatus: (id, status) => api.put(`/admin/complaints/${id}/status`, { status }),
  reanalyzeComplaint: (id) => api.post(`/admin/complaints/${id}/re-analyze`),
  deleteComplaint: (id) => api.delete(`/admin/complaints/${id}`),
  exportComplaints: (params) => api.get('/admin/complaints/export', { params, responseType: 'blob' })
}

export const documentService = {
  getDocuments: (params) => api.get('/admin/documents', { params }),
  getDocument: (id) => api.get(`/admin/documents/${id}`),
  createDocument: (data) => api.post('/admin/documents', data),
  updateDocument: (id, data) => api.put(`/admin/documents/${id}`, data),
  deleteDocument: (id) => api.delete(`/admin/documents/${id}`),
  uploadDocument: (formData) => api.post('/admin/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const analyticsService = {
  getOverview: () => api.get('/admin/analytics/overview'),
  getTrends: (days) => api.get('/admin/analytics/trends', { params: { days } }),
  getCategories: () => api.get('/admin/analytics/categories'),
  getUnits: () => api.get('/admin/analytics/units'),
  getFull: () => api.get('/admin/analytics/full')
}

export const attachmentService = {
  getAttachments: (complaintId) => api.get(`/attachments/complaint/${complaintId}`),
  uploadAttachment: (complaintId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/attachments/complaint/${complaintId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteAttachment: (attachmentId) => api.delete(`/attachments/${attachmentId}`)
}

export default api
