import { ref } from 'vue'
import { userService } from '@/services/users'

export function useUsers(){
  const usuarios = ref([])
  const cargarUsuarios = async () => {
    try{
      const response = await userService.getUsers({
        por_pagina: 100
      })
      console.log("Usuarios backend:", response)
      usuarios.value = response.usuarios || []
    
    }catch(error){
      console.error("Error cargando usuarios:", error)
    }
  }
  return {
    usuarios,
    cargarUsuarios
  }

}