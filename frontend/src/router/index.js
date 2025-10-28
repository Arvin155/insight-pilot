import {createRouter, createWebHistory} from 'vue-router'
import Admin from "@/views/Admin.vue";
import Index from "@/views/Index.vue";
import Login from "@/views/auth/LoginView.vue"
import Register from "@/views/auth/RegisterView.vue"
import KnowledgeManager from "@/views/knowlwdge/KnowledgeManager.vue";
import CreateKnowledge from "@/views/knowlwdge/CreateKnowledge.vue";
import DocsManager from "@/views/knowlwdge/DocsManager.vue";
import ChunkManager from "@/views/knowlwdge/ChunkManager.vue";

const routes = [
    {
        path: '/',
        component: Admin,
        children: [
            {
                path: '/',
                name: 'Index',
                component: Index,
            },
            {
                path: '/knowledge_manager',
                name: 'KnowledgeManager',
                component: KnowledgeManager
            },
            {
                path: '/create_knowledge',
                name: 'CreateKnowledge',
                component: CreateKnowledge
            },
            {
                path: '/docs_manager/:id',
                name: 'DocsManager',
                component: DocsManager
            },
            {
                path: '/chunk_manager/:id',
                name: 'ChunkManager',
                component: ChunkManager
            }
        ]
    },
    {
        path: '/login',
        name: 'login',
        component: Login,
    },
    {
        path: '/register',
        name: 'register',
        component: Register
    }
]
const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
