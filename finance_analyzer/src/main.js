import { createApp } from 'vue'
import App from './App.vue'
import './index.css'
import router from './router' // ← c’est ce qui manque probablement

const app = createApp(App)
app.use(router) // ← indispensable
app.mount('#app')