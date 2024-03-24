import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import "bootstrap/dist/css/bootstrap.css"
import "./assets/css/global.css"


const app = createApp(App)

const backend_path = "http://localhost:5001"
app.config.globalProperties.BACKENDPATH = backend_path

app.use(router)

app.mount('#app')
