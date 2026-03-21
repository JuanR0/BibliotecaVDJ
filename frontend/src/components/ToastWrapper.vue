<template>
  <Toast 
    ref="toastRef" 
    :position="position"
    :duration="duration"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Toast from './Toast.vue'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  position: {
    type: String,
    default: 'top-right'
  },
  duration: {
    type: Number,
    default: 4000
  }
})

const toastRef = ref(null)
const toastStore = useToastStore()

onMounted(() => {
  // Registrar el componente Toast en el store
  if (toastRef.value) {
    toastStore.setToastRef(toastRef.value)
    console.log('✅ Toast registrado en el store')
  }
})
</script>