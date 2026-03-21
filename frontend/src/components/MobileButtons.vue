<template>
  <button class="mobile-menu-btn" @click="$emit('toggle')">
    <span v-if="!open">☰</span>
    <span v-else>✕</span>
  </button>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])
</script>

<style scoped>
.mobile-menu-btn {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1001;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  border: none;
  font-size: 24px;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.mobile-menu-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }
}
</style>