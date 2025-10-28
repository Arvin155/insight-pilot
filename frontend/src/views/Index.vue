<!-- src/views/Index.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCookie } from '@/components/cookie'
import { Document, Briefcase, VideoCamera, Search } from '@element-plus/icons-vue'

const router = useRouter()
const username = ref('')
const headerRef = ref(null)

// 数据概览指标
const overviewData = ref({
  totalQueries: 1248,
  documentCount: 865,
  insightReports: 234,
  sqlConversionRate: 87.3,
  activeUsers: 42,
  ragAccuracy: 92.5
})

// 获取用户名
const fetchUserInfo = () => {
  username.value = getCookie('username') || ''
}

// 处理菜单选择
const handleSelect = (index) => {
  // 根据路由配置跳转到相应页面
  switch(index) {
    case '2':
      router.push('/resumes')
      break
    case '3':
      router.push('/positions')
      break
    case '4':
      router.push('/interview')
      break
    case '5':
      router.push('/matching')
      break
  }
}

// 查看所有通知
const viewAllNotices = () => {
  console.log('查看所有通知')
}

// 查看通知详情
const viewNoticeDetail = (id) => {
  console.log('查看通知详情', id)
}

onMounted(() => {
  fetchUserInfo()
})
</script>

<template>
  <div class="main-layout">
    <!-- 主内容区域 -->
    <el-main class="main-content">
      <!-- 欢迎信息 -->
      <el-card class="welcome-card">
        <div class="welcome-header">
          <h2>欢迎使用智慧数据洞察平台</h2>
          <p>您好，{{ headerRef?.username || username || '用户' }}！今天是 {{ new Date().toLocaleDateString() }}</p>
        </div>
      </el-card>

      <!-- 数据概览区域 -->
      <el-card class="overview-section">
        <template #header>
          <div class="overview-header">
            <span>数据概览</span>
          </div>
        </template>

        <div class="overview-content">
          <el-row :gutter="20">
            <el-col :xs="12" :sm="12" :md="8" :lg="8">
              <div class="overview-item highlight-primary">
                <div class="item-title">总查询次数</div>
                <div class="item-value">{{ overviewData.totalQueries }}</div>
                <div class="item-desc">今日增长: <span class="positive">+12%</span></div>
              </div>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8" :lg="8">
              <div class="overview-item highlight-success">
                <div class="item-title">文档数</div>
                <div class="item-value">{{ overviewData.documentCount }}</div>
                <div class="item-desc">新增文档: <span class="positive">+5%</span></div>
              </div>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8" :lg="8">
              <div class="overview-item highlight-warning">
                <div class="item-title">洞察报告生成份数</div>
                <div class="item-value">{{ overviewData.insightReports }}</div>
                <div class="item-desc">今日生成: <span class="info">12份</span></div>
              </div>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8" :lg="8">
              <div class="overview-item highlight-info">
                <div class="item-title">SQL转换率</div>
                <div class="item-value">{{ overviewData.sqlConversionRate }}%</div>
                <div class="item-desc">较上周: <span class="positive">+2.1%</span></div>
              </div>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8" :lg="8">
              <div class="overview-item highlight-purple">
                <div class="item-title">活跃用户数</div>
                <div class="item-value">{{ overviewData.activeUsers }}</div>
                <div class="item-desc">在线用户: <span class="info">8</span></div>
              </div>
            </el-col>

            <el-col :xs="12" :sm="12" :md="8" :lg="8">
              <div class="overview-item highlight-orange">
                <div class="item-title">RAG准确率</div>
                <div class="item-value">{{ overviewData.ragAccuracy }}%</div>
                <div class="item-desc">较昨日: <span class="positive">+0.8%</span></div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 功能介绍卡片 -->
      <el-card class="features-section">
        <template #header>
          <div class="features-header">
            <span>核心功能</span>
          </div>
        </template>

        <div class="features-content">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="12" :lg="6">
              <div class="feature-card">
                <div class="feature-icon bg-blue">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="feature-info">
                  <h3>智能RAG问答</h3>
                  <p>基于检索增强生成技术，提供精准的知识问答服务</p>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :sm="12" :md="12" :lg="6">
              <div class="feature-card">
                <div class="feature-icon bg-green">
                  <el-icon><VideoCamera /></el-icon>
                </div>
                <div class="feature-info">
                  <h3>多模态问答</h3>
                  <p>支持文本、图像等多种媒体类型的智能问答</p>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :sm="12" :md="12" :lg="6">
              <div class="feature-card">
                <div class="feature-icon bg-purple">
                  <el-icon><Search /></el-icon>
                </div>
                <div class="feature-info">
                  <h3>自然语言转SQL</h3>
                  <p>将自然语言自动转换为结构化查询语句</p>
                </div>
              </div>
            </el-col>

            <el-col :xs="24" :sm="12" :md="12" :lg="6">
              <div class="feature-card">
                <div class="feature-icon bg-orange">
                  <el-icon><Briefcase /></el-icon>
                </div>
                <div class="feature-info">
                  <h3>数据洞察Agent</h3>
                  <p>自动化数据分析与洞察生成，辅助决策制定</p>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <router-view/>
    </el-main>
  </div>
</template>

<style scoped>
.main-layout {
  min-height: 85vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  width: 100%;
  margin: 20px auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-header h2 {
  margin-bottom: 10px;
  color: #1890ff;
}

.overview-section {
  margin-bottom: 20px;
}

.overview-header {
  font-weight: 500;
}

.overview-content {
  padding: 10px 0;
}

.overview-item {
  padding: 20px;
  text-align: center;
  border-radius: 8px;
  background-color: #f8f9fa;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-left: 4px solid #dcdfe6;
}

.overview-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.highlight-primary {
  border-left-color: #409eff;
}

.highlight-success {
  border-left-color: #67c23a;
}

.highlight-warning {
  border-left-color: #e6a23c;
}

.highlight-info {
  border-left-color: #909399;
}

.highlight-purple {
  border-left-color: #9254de;
}

.highlight-orange {
  border-left-color: #ffa500;
}

.item-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.item-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.item-desc {
  font-size: 12px;
  color: #999;
}

.positive {
  color: #67c23a;
  font-weight: bold;
}

.success {
  color: #67c23a;
  font-weight: bold;
}

.info {
  color: #409eff;
  font-weight: bold;
}

.features-section {
  margin-bottom: 20px;
}

.features-header {
  font-weight: 500;
}

.feature-card {
  display: flex;
  padding: 20px;
  border-radius: 8px;
  background-color: #f8f9fa;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.feature-icon.el-icon {
  font-size: 24px;
  color: white;
}

.bg-blue {
  background-color: #409eff;
}

.bg-green {
  background-color: #67c23a;
}

.bg-purple {
  background-color: #9254de;
}

.bg-orange {
  background-color: #ffa500;
}

.feature-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.feature-info p {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin: 10px;
    padding: 15px;
  }

  .feature-card {
    flex-direction: column;
    text-align: center;
  }

  .feature-icon {
    margin-right: 0;
    margin-bottom: 15px;
  }
}
</style>
