import { createRouter, createWebHistory } from 'vue-router'
import PDF_warper from '../components/PDF_warper.vue'
import Resizer from '../components/Resizer.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'pdf',
      // component: Resizer,
      component: PDF_warper,
    },
    // {
    //   path: '/books',
    //   name: 'books',
    //   component: Books,
    // },
    // {
    //   path: '/ping',
    //   name: 'ping',
    //   component: Ping
    // },
  ]
})

export default router