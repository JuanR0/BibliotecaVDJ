import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useChatStore = defineStore('chat', () => {
    const clearChat = () => {
        messages.value = [
            { from: 'bot', text: 'Hola 👋 ¿En qué puedo ayudarte?' }
        ]

        localStorage.removeItem('chat_messages')
    }
    const safeParse = (key, fallback) => {
        try {
        const item = localStorage.getItem(key)
        return item ? JSON.parse(item) : fallback
        } catch (e) {
        return fallback
        }
    }

    const isOpen = ref(safeParse('chat_open', false))

    const messages = ref(
        safeParse('chat_messages', [
        { from: 'bot', text: 'Hola 👋 ¿En qué puedo ayudarte?' }
        ])
    )

    const toggle = () => {
        isOpen.value = !isOpen.value
    }

    const addMessage = (msg) => {
        messages.value.push(msg)
    }

    watch(messages, (val) => {
        localStorage.setItem('chat_messages', JSON.stringify(val))
    }, { deep: true })

    watch(isOpen, (val) => {
        localStorage.setItem('chat_open', JSON.stringify(val))
    })

    return {
        isOpen,
        messages,
        toggle,
        addMessage,
        clearChat
    }
})
