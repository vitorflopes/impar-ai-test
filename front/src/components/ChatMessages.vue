<script setup>
import { ref, watch, nextTick } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  messages: {
    type: Array,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const collapsedThinking = ref({})

const toggleThinking = (msgId) => {
  collapsedThinking.value[msgId] = !collapsedThinking.value[msgId]
}

const isThinkingExpanded = (msgId) => {
  return collapsedThinking.value[msgId] !== true
}

const parseMarkdown = (content) => {
  return marked.parse(content || '')
}

const thinkingRefs = ref({})

const setThinkingRef = (el, id) => {
  if (el) thinkingRefs.value[id] = el
}

watch(() => props.messages, () => {
  nextTick(() => {
    props.messages.forEach(msg => {
      if (msg.thinking && isThinkingExpanded(msg.id)) {
        const el = thinkingRefs.value[msg.id]
        if (el) {
          el.scrollTop = el.scrollHeight
        }
      }
    })
  })
}, { deep: true })
</script>

<template>
  <div class="messages-area">
    <div
      v-for="msg in messages"
      :key="msg.id"
      class="message-wrapper"
      :class="msg.role"
    >
      <div class="avatar" v-if="msg.role === 'assistant'">
        <font-awesome-icon :icon="['fas', 'robot']" />
      </div>
      <div class="message-bubble">
        <template v-if="msg.role === 'assistant'">
          <!-- Thinking Block (collapsible) -->
          <div v-if="msg.thinking" class="thinking-block">
            <button 
              class="thinking-toggle" 
              @click="toggleThinking(msg.id)"
            >
              <font-awesome-icon 
                :icon="['fas', isThinkingExpanded(msg.id) ? 'chevron-down' : 'chevron-right']" 
                class="toggle-icon"
              />
              <span>Pensando...</span>
            </button>
            <div 
              v-show="isThinkingExpanded(msg.id)" 
              class="thinking-content"
              :ref="(el) => setThinkingRef(el, msg.id)"
            >
              {{ msg.thinking }}
            </div>
          </div>
          
          <!-- Tool Calls Block -->
          <div v-if="msg.toolCalls && msg.toolCalls.length > 0" class="tool-calls-block">
            <div v-for="(tc, idx) in msg.toolCalls" :key="idx" class="tool-call-item">
              <div class="tool-call-header">
                <font-awesome-icon :icon="['fas', 'wrench']" class="tool-icon" />
                <span class="tool-name">{{ tc.tool }}</span>
                <span v-if="tc.output === null" class="tool-loading">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                </span>
                <font-awesome-icon v-else :icon="['fas', 'check']" class="tool-done" />
              </div>
              <div class="tool-call-input">
                <code>{{ JSON.stringify(tc.input, null, 2) }}</code>
              </div>
              <div v-if="tc.output" class="tool-call-output">
                <span class="output-label">Resultado:</span>
                <pre>{{ tc.output }}</pre>
              </div>
            </div>
          </div>
          
          <!-- Main Content -->
          <div class="markdown-content" v-html="parseMarkdown(msg.content)"></div>
        </template>
        <template v-else>
          {{ msg.content }}
        </template>
      </div>
    </div>
    
    <div v-if="isLoading" class="message-wrapper assistant">
       <div class="avatar">
        <font-awesome-icon :icon="['fas', 'robot']" />
      </div>
      <div class="message-bubble loading">
        <span class="dot"></span><span class="dot"></span><span class="dot"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.messages-area {
  flex: 1;
  width: 100%;
  overflow-y: auto;
  padding-bottom: 120px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.messages-area::-webkit-scrollbar {
  width: 6px;
}

.messages-area::-webkit-scrollbar-track {
  background: transparent;
}

.messages-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.messages-area::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.message-wrapper {
  display: flex;
  gap: 16px;
  max-width: 80%;
}

.message-wrapper.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-wrapper.assistant {
  margin-right: auto;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
}

.user .message-bubble {
  background: #3B82F6;
  color: #fff;
  border-radius: 20px;
  padding: 10px 20px;
  font-weight: 400;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.assistant .message-bubble {
  background: transparent;
  padding-left: 0;
}

.markdown-content {
  line-height: 1.6;
}

.markdown-content p {
  margin: 0 0 0.75em 0;
}

.markdown-content p:last-child {
  margin-bottom: 0;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3 {
  margin: 1em 0 0.5em 0;
  font-weight: 600;
}

.markdown-content ul,
.markdown-content ol {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

.markdown-content li {
  margin: 0.25em 0;
}

.markdown-content code {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
}

.markdown-content pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.75em 0;
}

.markdown-content pre code {
  background: transparent;
  padding: 0;
}

.markdown-content a {
  color: #60a5fa;
  text-decoration: underline;
}

.markdown-content blockquote {
  border-left: 3px solid rgba(255, 255, 255, 0.2);
  padding-left: 1em;
  margin: 0.75em 0;
  color: rgba(255, 255, 255, 0.7);
}

.loading {
  display: flex;
  gap: 4px;
  padding-left: 0;
}

.dot {
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  animation: pulse 1.5s infinite ease-in-out;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.thinking-block {
  margin-bottom: 12px;
  border-left: 2px solid rgba(255, 255, 255, 0.15);
  padding-left: 12px;
}

.thinking-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.4);
  font-size: 0.8rem;
  cursor: pointer;
  padding: 4px 0;
  transition: color 0.2s ease;
}

.thinking-toggle:hover {
  color: rgba(255, 255, 255, 0.6);
}

.toggle-icon {
  font-size: 0.65rem;
  width: 10px;
}

.thinking-content {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.35);
  line-height: 1.5;
  white-space: pre-wrap;
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 8px;
}

.thinking-content::-webkit-scrollbar {
  width: 4px;
}

.thinking-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.tool-calls-block {
  margin: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-call-item {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.85rem;
}

.tool-call-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.tool-icon {
  color: #3b82f6;
  font-size: 0.9rem;
}

.tool-name {
  font-weight: 600;
  color: #60a5fa;
}

.tool-done {
  color: #22c55e;
  font-size: 0.8rem;
}

.tool-loading {
  display: flex;
  gap: 3px;
}

.tool-loading .dot {
  width: 5px;
  height: 5px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out;
}

.tool-loading .dot:nth-child(1) { animation-delay: 0s; }
.tool-loading .dot:nth-child(2) { animation-delay: 0.2s; }
.tool-loading .dot:nth-child(3) { animation-delay: 0.4s; }

.tool-call-input {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 8px;
}

.tool-call-input code {
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  white-space: pre-wrap;
  word-break: break-all;
}

.tool-call-output {
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  padding-top: 8px;
}

.output-label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tool-call-output pre {
  font-family: 'Fira Code', 'Monaco', monospace;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  white-space: pre-wrap;
  word-break: break-word;
  margin: 4px 0 0 0;
  max-height: 150px;
  overflow-y: auto;
}
</style>
