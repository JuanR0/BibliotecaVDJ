<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal">
      <h2>Solicitar Préstamo</h2>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Fecha de devolución</label>
          <input 
            type="date" 
            v-model="fechaDevolucion"
            required
          />
        </div>

        <div class="form-group">
          <label>Observaciones</label>
          <textarea 
            v-model="observaciones"
            placeholder="Opcional..."
          ></textarea>
        </div>

        <div class="actions">
          <button type="button" @click="cerrar">Cancelar</button>
          <button type="submit" :disabled="loading">
            {{ loading ? "Procesando..." : "Confirmar Préstamo" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue"
import { crearPrestamoLibro } from "@/services/prestamoLibroService"
import { useUsuarioStore } from "@/stores/usuario"

const props = defineProps({
  visible: Boolean,
  libroId: Number
})

const emit = defineEmits(["close", "success"])

const usuarioStore = useUsuarioStore()

const fechaDevolucion = ref("")
const observaciones = ref("")
const loading = ref(false)

watch(() => props.visible, (newVal) => {
  if (newVal) {
    fechaDevolucion.value = ""
    observaciones.value = ""
  }
})

const cerrar = () => {
  emit("close")
}

const handleSubmit = async () => {
  try {
    loading.value = true

    const payload = {
      libro_id: props.libroId,
      usuario_prestado_id: usuarioStore.usuario_id,
      fecha_devolucion_esperada: new Date(fechaDevolucion.value).toISOString(),
      observaciones: observaciones.value
    }

    await crearPrestamoLibro(payload)

    emit("success")
    cerrar()

  } catch (error) {
    console.error(error)
    alert(error.response?.data?.detail || "Error al crear préstamo")
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 400px;
}

.form-group {
  margin-bottom: 1rem;
}

.actions {
  display: flex;
  justify-content: space-between;
}
</style>
