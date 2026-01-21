<script setup>
import { computed, ref } from 'vue'
import { useNotificationStore } from '../stores/notification'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  hasStarted: {
    type: Boolean,
    default: false
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'send', 'files-selected'])
const notificationStore = useNotificationStore()
const fileInput = ref(null)
const selectedFiles = ref([])

const message = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const suggestions = [
  { icon: ['fas', 'robot'], label: 'O que é o Teste de Turing?' },
  { icon: ['fas', 'terminal'], label: 'Quem criou o termo IA?' },
  { icon: ['fas', 'wand-magic-sparkles'], label: 'O que foi o Deep Blue?' },
  { icon: ['fas', 'clone'], label: 'O que é IA Forte?' }
]

const handleSuggestion = (label) => {
  message.value = label
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  
  if (selectedFiles.value.length + files.length > 3) {
    notificationStore.addNotification({
      message: 'Você só pode anexar no máximo 3 arquivos.',
      type: 'warning'
    })
    return
  }

  const allowedTypes = [
    'application/pdf',
    'text/csv', 
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
    'application/vnd.openxmlformats-officedocument.presentationml.presentation', 
    'text/html',
    'application/json',
    'text/plain',
    'text/markdown',
    'image/png',
    'image/jpeg',
    'image/tiff',
    'image/bmp'
  ]

  const allowedExtensions = ['.pdf', '.csv', '.xls', '.xlsx', '.docx', '.pptx', '.html', '.json', '.txt', '.text', '.md', '.markdown', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']

  for (const file of files) {
    const hasValidType = allowedTypes.includes(file.type)
    const hasValidExtension = allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))
    
    if (!hasValidType && !hasValidExtension) {
      notificationStore.addNotification({
        message: `Formato inválido: ${file.name}. Formatos aceitos: PDF, Excel, CSV, Word, PowerPoint, HTML, JSON, TXT, Markdown e Imagens.`,
        type: 'error'
      })
      continue
    }
    
    if (!selectedFiles.value.some(f => f.name === file.name && f.size === file.size)) {
      selectedFiles.value.push(file)
    }
  }

  event.target.value = ''
  emit('files-selected', selectedFiles.value)
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  emit('files-selected', selectedFiles.value)
}

const handleSend = () => {
  if (props.isLoading) return
  if (message.value.trim() || selectedFiles.value.length > 0) {
    emit('send', selectedFiles.value)
    selectedFiles.value = []
  }
}

const handlePaste = (event) => {
  const items = event.clipboardData?.items
  if (!items) return

  for (const item of items) {
    if (item.type.startsWith('image/')) {
      event.preventDefault()
      
      const file = item.getAsFile()
      if (!file) continue

      if (selectedFiles.value.length >= 3) {
        notificationStore.addNotification({
          message: 'Você só pode anexar no máximo 3 arquivos.',
          type: 'warning'
        })
        return
      }

      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')
      const extension = file.type.split('/')[1] || 'png'
      const namedFile = new File([file], `imagem-colada-${timestamp}.${extension}`, { type: file.type })

      selectedFiles.value.push(namedFile)
      emit('files-selected', selectedFiles.value)
      
      notificationStore.addNotification({
        message: 'Imagem colada com sucesso!',
        type: 'success',
        duration: 2000
      })
      break
    }
  }
}
</script>

<template>
  <div class="input-section">
    <div class="input-card">
      <div v-if="selectedFiles.length > 0" class="files-preview">
        <div v-for="(file, index) in selectedFiles" :key="index" class="file-tag">
          <span class="file-icon">
            <font-awesome-icon :icon="['fas', 'file']" />
          </span>
          <span class="file-name">{{ file.name }}</span>
          <button class="remove-btn" @click="removeFile(index)">×</button>
        </div>
      </div>

      <textarea
        v-model="message"
        placeholder="Digite sua mensagem..."
        @keydown.enter.prevent="handleSend"
        @paste="handlePaste"
        rows="1"
      ></textarea>
      
      <input 
        type="file" 
        ref="fileInput"
        multiple 
        accept=".pdf,.csv,.xls,.xlsx,.docx,.pptx,.html,.json,.txt,.text,.md,.markdown,.png,.jpg,.jpeg,.tiff,.bmp" 
        style="display: none"
        @change="handleFileSelect"
      >

      <div class="action-bar">
        <div class="left-actions">
          <button class="icon-btn" title="Anexar" @click="triggerFileInput">
            <font-awesome-icon :icon="['fas', 'paperclip']" />
          </button>
        </div>
        
        <button class="send-btn" @click="handleSend" :disabled="isLoading || (!message && selectedFiles.length === 0)">
          <font-awesome-icon :icon="['fas', 'paper-plane']" />
          <span>Send</span>
        </button>
      </div>
    </div>

    <div v-if="!hasStarted" class="suggestions-list">
      <button 
        v-for="item in suggestions" 
        :key="item.label" 
        class="suggestion-btn"
        @click="handleSuggestion(item.label)"
      >
        <font-awesome-icon :icon="item.icon" />
        {{ item.label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.input-section {
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-card {
  background-color: rgba(10, 10, 10, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: border-color 0.2s;
  min-height: 120px;
}

.input-card:focus-within {
  border-color: #333;
}

textarea {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 1rem;
  padding: 12px;
  resize: none;
  font-family: inherit;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  flex-grow: 1;
}

textarea::placeholder {
  color: #4B4B4B;
  font-weight: 400;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
  margin-top: auto;
}

.left-actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  background: #1A1A1A;
  border: 1px solid #1F1F1F;
  color: #888;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background: #252525;
  color: #ccc;
}

.send-btn {
  background: #1F1F1F;
  border: 1px solid #1F1F1F;
  color: #E5E5E5;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
  height: 36px;
}

.send-btn:hover:not(:disabled) {
  background: #2A2A2A;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  color: #666;
}

.suggestions-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 0.5rem;
}

.suggestion-btn {
  background: #0A0A0A;
  border: 1px solid #1F1F1F;
  color: #888;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.suggestion-btn:hover {
  background: #1A1A1A;
  border-color: #333;
  color: #E5E5E5;
}

@media (max-width: 640px) {
  .input-section { width: 100%; }
}

.files-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 4px 12px 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 8px;
}

.file-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px 8px 4px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #E5E5E5;
}

.file-icon {
  color: #888;
  font-size: 0.9em;
}

.file-name {
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.remove-btn {
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 1.2em;
  line-height: 1;
  padding: 0 2px;
  margin-left: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.remove-btn:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}
</style>
