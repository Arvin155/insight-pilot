<!-- src/views/components/FHeader.vue -->
<script setup>
import {onMounted, ref} from 'vue'
import {useRouter} from 'vue-router'
import {clearAuthCookies, getCookie,} from '@/components/cookie'
import {Avatar, Bell, Message, SwitchButton} from '@element-plus/icons-vue'

const router = useRouter()
const username = ref('')
const activeIndex = ref('1')

// 菜单选项
const menuItems = ref([
  {index: '1', title: '首页', route: '/'},
  {index: '2', title: '知识库管理', route: '/knowledge_manager'},
  {index: '3', title: '智能问答', route: '/rag_chat'},
  {index: '4', title: '多模态问答', route: '/resume_manager'},
  {index: '5', title: '数据洞察Agent', route: '/resume_chat'},
  {index: '6', title: 'Text2SQL', route: '/recommendations'},
])

// 获取用户名
const fetchUserInfo = () => {
  username.value = getCookie('username') || ''
}

// 处理登出
const handleLogout = () => {
  // 删除所有相关的cookie
  clearAuthCookies()
  // 可以根据实际需要删除其他cookie
  router.push('/login')
}

// 处理个人信息
const handleProfile = () => {
  router.push('/user_profile')
}

// 处理消息
const handleMessage = () => {
  router.push('/messages')
}

// 处理菜单选择
const handleSelect = (key) => {
  // 查找一级菜单项
  let menuItem = menuItems.value.find(item => item.index === key)

  // 如果没找到，查找二级菜单项
  if (!menuItem) {
    for (const item of menuItems.value) {
      if (item.children) {
        const child = item.children.find(child => child.index === key)
        if (child) {
          menuItem = child
          break
        }
      }
    }
  }

  if (menuItem && menuItem.route) {
    router.push(menuItem.route)
  }
}

onMounted(() => {
  fetchUserInfo()
})

defineExpose({
  username
})
</script>

<template>
  <!-- 顶部导航栏 -->
  <el-header class="header">
    <div class="header-content">
      <!-- Logo区域 -->
      <div class="logo-section">
        <h2 class="logo">智慧数据洞察平台</h2>
      </div>

      <el-menu
          :default-active="activeIndex"
          class="nav-menu"
          mode="horizontal"
          @select="handleSelect"
      >
        <template v-for="item in menuItems" :key="item.index">
          <!-- 普通菜单项 -->
          <el-menu-item
              v-if="!item.children"
              :index="item.index"
          >
            {{ item.title }}
          </el-menu-item>

          <!-- 有子菜单的项 -->
          <el-sub-menu
              v-else
              :index="item.index"
          >
            <template #title>{{ item.title }}</template>
            <el-menu-item
                v-for="child in item.children"
                :key="child.index"
                :index="child.index"
            >
              {{ child.title }}
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>

      <!-- 用户信息区域 -->
      <div class="user-section">
        <el-dropdown>
          <div class="notification-icon">
            <el-icon :size="20">
              <Bell/>
            </el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>您有3条新消息</el-dropdown-item>
              <el-dropdown-item>面试提醒：下午2点</el-dropdown-item>
              <el-dropdown-item divided>
                <router-link to="/notifications">查看所有通知</router-link>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-dropdown>
          <div class="user-info">
            <el-icon class="user-avatar">
              <Avatar/>
            </el-icon>
            <span class="username">{{ username || '用户' }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleProfile">
                <el-icon>
                  <Avatar/>
                </el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item @click="handleMessage">
                <el-icon>
                  <Message/>
                </el-icon>
                我的消息
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon>
                  <SwitchButton/>
                </el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </el-header>
</template>

<style scoped>
.header {
  background-color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.logo-section {
  margin-right: 30px;
}

.logo {
  color: #1890ff;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.nav-menu {
  flex: 1;
  border: none;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-left: auto; /* 将用户信息推到最右侧 */
}

.notification-icon {
  cursor: pointer;
  color: #606266;
  padding: 5px;
  border-radius: 4px;
}

.notification-icon:hover {
  background-color: #f5f7fa;
  color: #1890ff;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  margin-right: 8px;
  font-size: 18px;
  color: #1890ff;
}

.username {
  font-size: 14px;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    padding: 10px;
  }

  .logo-section {
    margin-right: 10px;
  }

  .nav-menu {
    order: 3;
    width: 100%;
    margin-top: 10px;
  }

  .user-section {
    gap: 10px;
    margin-left: 0; /* 在小屏幕上重置margin */
  }
}
</style>
