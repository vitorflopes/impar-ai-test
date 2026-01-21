import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faPaperclip, 
  faTerminal, 
  faPaperPlane, 
  faClone, 
  faFile, 
  faWandMagicSparkles, 
  faRobot,
  faChevronDown,
  faChevronRight,
  faWrench,
  faCheck
} from '@fortawesome/free-solid-svg-icons'
import { faFigma } from '@fortawesome/free-brands-svg-icons'

import App from './App.vue'
import router from './router'

library.add(
  faPaperclip, 
  faTerminal, 
  faPaperPlane, 
  faClone, 
  faFile, 
  faWandMagicSparkles, 
  faRobot,
  faFigma,
  faChevronDown,
  faChevronRight,
  faWrench,
  faCheck
)

const app = createApp(App)

app.component('font-awesome-icon', FontAwesomeIcon)

app.use(createPinia())
app.use(router)

app.mount('#app')
