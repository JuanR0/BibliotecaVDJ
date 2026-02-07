import { api } from './api'

export const bookService = {
  // Obtener todos los libros
  async getBooks(params = {}) {
    try {
      const response = await api.get('/libros', { params })
      return response.data
    } catch (error) {
      console.error('Error obteniendo libros:', error)
      throw error
    }
  },

  // OBTENER LIBRO POR ID
  async getBookById(id) {
    try {
      const response = await api.get(`/libros/${id}`)
      return response.data
    } catch (error) {
      console.error(`Error obteniendo libro ${id}:`, error)
      throw error
    }
  },

  // BUSCAR LIBROS
  async searchBooks(query, params = {}) {
    const cleanParams = {};
    
    Object.entries(params).forEach(([key, value]) => {
      // Solo incluir si tiene valor y no es string vacío
      if (value !== undefined && value !== null && value !== '') {
        // Convertir tipos según el campo
        if (key.endsWith('_id') && !isNaN(value)) {
          cleanParams[key] = parseInt(value);
        } else if (key === 'es_prestable' || key === 'incluir_retirados') {
          cleanParams[key] = Boolean(value);
        } else if (key === 'pagina' || key === 'por_pagina') {
          cleanParams[key] = parseInt(value);
        } else {
          cleanParams[key] = value;
        }
      }
    });
    
    console.log('📤 Llamando GET /api/libros con:', cleanParams);
    
    const response = await api.get('/libros', { params: cleanParams });
    return response.data;
  },

  // CREAR LIBRO
  async createBook(bookData) {
    try {
      const response = await api.post('/libros', bookData)
      return response.data
    } catch (error) {
      console.error('Error creando libro:', error)
      throw error
    }
  },

  // ACTUALIZAR LIBRO
  async updateBook(id, bookData) {
    try {
      const response = await api.put(`/libros/${id}`, bookData)
      return response.data
    } catch (error) {
      console.error(`Error actualizando libro ${id}:`, error)
      throw error
    }
  },

  // ELIMINAR LIBRO
  async deleteBook(id) {
    try {
      const response = await api.delete(`/libros/${id}`)
      return response.data
    } catch (error) {
      console.error(`Error eliminando libro ${id}:`, error)
      throw error
    }
  },

  // REACTIVAR LIBRO
  async reactivateBook(bookId) {
    try {
      const response = await api.patch(`/api/libros/${bookId}/reactivar`)
      return response.data
    } catch (error) {
      console.error('Error reactivating book:', error)
      throw error
    }
  },

  // Obtener préstamos de un libro
  async getBookLoans(bookId) {
    try {
      const response = await api.get(`/libros/${bookId}/prestamos`)
      return response.data
    } catch (error) {
      console.error(`Error obteniendo préstamos del libro ${bookId}:`, error)
      throw error
    }
  }
}