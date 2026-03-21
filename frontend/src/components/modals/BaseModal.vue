<template>
    <transition name="modal">
    <div v-if="modelValue" class="modal-overlay" @click.self="close">
    <div class="modal-container">
        <div class="modal-header">
            <h3>{{ title }}</h3>
            <button class="modal-close" @click="close">✖</button>
        </div>

        <div class="modal-body">
            <slot />
        </div>
        
        <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
        </div>

    </div>

    </div>

    </transition>
</template>

<script setup>

const props = defineProps({
  modelValue: Boolean,
  title: String
})

const emit = defineEmits(["update:modelValue"])

function close(){
  emit("update:modelValue", false)
}

</script>

<style scoped>
@keyframes fadeIn{
  from{
    opacity:0;
  }
  to{
    opacity:1;
  }
}

@keyframes scaleIn{
  from{
    transform:scale(.9);
    opacity:0;
  }
  to{
    transform:scale(1);
    opacity:1;
  }
}

.modal-overlay{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display:flex;
  justify-content:center;
  align-items:center;
  z-index:1000;
  animation: fadeIn .18 ease;
}

.modal-container{
  background:white;
  border-radius:10px;
  width:500px;
  max-width:90%;
  box-shadow:0 10px 30px rgba(0,0,0,0.2);

  animation: scaleIn .18 ease;
}

.modal-header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:16px;
  border-bottom:1px solid #eee;
}

.modal-body{
  padding:20px;
}

.modal-footer{
  padding:16px;
  border-top:1px solid #eee;
  display:flex;
  justify-content:flex-end;
  gap:10px;
}

.modal-close{
  background:none;
  border:none;
  cursor:pointer;
  font-size:16px;
}

.modal-enter-active,
.modal-leave-active{
  transition: all .2s ease;
}

.modal-enter-from{
  opacity:0;
  transform:scale(.9);
}

.modal-enter-to{
  opacity:1;
  transform:scale(1);
}

.modal-leave-from{
  opacity:1;
}

.modal-leave-to{
  opacity:0;
}

</style>

