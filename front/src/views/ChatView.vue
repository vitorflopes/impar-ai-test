<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import ChatInput from '../components/ChatInput.vue'
import ChatMessages from '../components/ChatMessages.vue'
import { streamMessageFromApi, uploadFilesToApi, triggerScrapeApi } from '../api/chat'
import { useNotificationStore } from '../stores/notification'

const message = ref('')
const messages = ref([])
const isLoading = ref(false)
const hasStarted = computed(() => messages.value.length > 0)
const notificationStore = useNotificationStore()
const threadId = ref(Math.random().toString(36).substring(7))

const orb1 = ref({ top: '50%', left: '50%', opacity: 0, scale: 1 })
const orb2 = ref({ top: '50%', left: '50%', opacity: 0, scale: 1 })
let intervalId = null

const getRandomPos = () => ({
  top: `${Math.random() * 80 + 10}%`,
  left: `${Math.random() * 80 + 10}%`,
  scale: 0.8 + Math.random() * 0.6
})

const animateOrb = (orbRef, delay = 0) => {
  setTimeout(() => {
    const newPos = getRandomPos()
    orbRef.value = { ...newPos, opacity: 0 }
    
    setTimeout(() => {
      orbRef.value.opacity = 0.5
    }, 100)

    setTimeout(() => {
      orbRef.value.opacity = 0
    }, 6000)
  }, delay)
}

const startOrbAnimation = () => {
  animateOrb(orb1, 0)
  animateOrb(orb2, 6000)

  intervalId = setInterval(() => {
    animateOrb(orb1, 0)
    animateOrb(orb2, 6000)
  }, 12000)
}

const triggerInitialScrape = async () => {
  notificationStore.addNotification({
    message: 'Iniciando scraping da página da Wikipedia...',
    type: 'info',
    duration: 3000
  })

  try {
    const data = await triggerScrapeApi()
    notificationStore.addNotification({
      message: data.message,
      type: data.status === 'success' ? 'success' : 'warning'
    })
  } catch (error) {
    notificationStore.addNotification({
      message: 'Falha ao realizar scraping inicial.',
      type: 'error'
    })
  }
}

onMounted(() => {
  startOrbAnimation()
  triggerInitialScrape()
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})

watch(hasStarted, (val) => {
  if (val && intervalId) {
    clearInterval(intervalId)
    intervalId = null
  }
})

const sendMessage = async (attachedFiles = []) => {
  if (!message.value.trim() && attachedFiles.length === 0) return

  const userContent = message.value
  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userContent
  })

  message.value = ''
  isLoading.value = true

  try {
    if (attachedFiles.length > 0) {
      notificationStore.addNotification({
        message: 'Enviando arquivos...',
        type: 'info',
        duration: 2000
      })
      
      const uploadData = await uploadFilesToApi(attachedFiles)
      
      notificationStore.addNotification({
        message: `Arquivos processados: ${uploadData.chunks_generated} chunks gerados.`,
        type: 'success'
      })
    }

    if (userContent) {
      const assistantMessage = reactive({
        id: Date.now() + 1,
        role: 'assistant',
        thinking: '',
        content: '',
        toolCalls: []
      })
      messages.value.push(assistantMessage)
      
      isLoading.value = false

      for await (const chunk of streamMessageFromApi(userContent, threadId.value)) {
        if (chunk.type === 'thinking') {
          assistantMessage.thinking += chunk.text
        } else if (chunk.type === 'content') {
          assistantMessage.content += chunk.text
        } else if (chunk.type === 'tool_call') {
          assistantMessage.toolCalls.push({
            tool: chunk.tool,
            input: chunk.input,
            output: null
          })
        } else if (chunk.type === 'tool_response') {
          const toolCall = assistantMessage.toolCalls.find(
            tc => tc.tool === chunk.tool && tc.output === null
          )
          if (toolCall) {
            toolCall.output = chunk.output
          }
        }
      }
    }
  } catch (error) {
    notificationStore.addNotification({
      message: 'Erro ao processar sua solicitação. Tente novamente.',
      type: 'error',
      duration: 5000
    })
    console.error(error)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="chat-container">
    <div class="background-effects">
      <div class="orb fixed-orb"></div>
      <template v-if="!hasStarted">
        <div 
          class="orb" 
          :style="{ 
            top: orb1.top, 
            left: orb1.left, 
            opacity: orb1.opacity,
            transform: `translate(-50%, -50%) scale(${orb1.scale})`
          }"
        ></div>
        <div 
          class="orb" 
          :style="{ 
            top: orb2.top, 
            left: orb2.left, 
            opacity: orb2.opacity,
            transform: `translate(-50%, -50%) scale(${orb2.scale})`
          }"
        ></div>
      </template>
    </div>

    <div class="content-wrapper" :class="{ 'started': hasStarted }">
      
      <div v-if="!hasStarted" class="welcome-header">
        <h1>Como posso ajudar hoje?</h1>
        <p>Digite um comando ou faça uma pergunta</p>
      </div>

      <ChatMessages 
        v-else 
        :messages="messages" 
        :is-loading="isLoading" 
      />

      <div class="input-area-wrapper">
        <ChatInput 
          v-model="message" 
          :has-started="hasStarted"
          :is-loading="isLoading"
          @send="sendMessage" 
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  height: 100vh;
  background-color: #050505;
  color: #ffffff;
  font-family: 'Inter', -apple-system, sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.background-effects {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.orb {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(76, 29, 149, 0.4) 0%, rgba(76, 29, 149, 0) 70%);
  filter: blur(60px);
  transition: opacity 3s ease-in-out, top 0s, left 0s, transform 3s ease-in-out;
  pointer-events: none;
}

.fixed-orb {
  top: 0;
  left: 50%;
  width: 1800px;
  height: 1800px;
  transform: translate(-50%, -50%);
  opacity: 0.25;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.4) 0%, rgba(76, 29, 149, 0) 100%);
  animation: none;
  transition: none;
}

.content-wrapper {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  transition: all 0.5s ease;
  position: relative;
  z-index: 1;
}

.content-wrapper.started {
  justify-content: flex-start;
  height: 100vh;
  padding-top: 2rem;
}

.welcome-header {
  text-align: center;
  margin-bottom: 2.5rem;
  animation: fadeIn 0.8s ease-out;
}

.welcome-header h1 {
  font-size: 2.5rem;
  font-weight: 500;
  background: linear-gradient(135deg, #ffffff 0%, #6a6a6a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.02em;
}

.welcome-header p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

.input-area-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.started .input-area-wrapper {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 4rem);
  max-width: 800px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .content-wrapper { padding: 1rem; }
  .welcome-header h1 { font-size: 2rem; }
}
</style>
