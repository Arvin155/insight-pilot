<template>
  <div class="rag-manager-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="header-card">
          <div class="header-content">
            <div class="title-section">
              <h2 class="highlight-title">知识库管理</h2>
              <p class="subtitle">集中管理您的知识资产，提升团队协作效率</p>
            </div>
            <el-button type="primary" @click="handleAddKnowledgeBase">
              <el-icon>
                <Plus/>
              </el-icon>
              新建知识库
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :span="6">
        <el-card class="sidebar-card">
          <template #header>
            <div class="sidebar-header">
              <span>知识库列表</span>
              <el-input
                  v-model="searchKeyword"
                  placeholder="搜索知识库"
                  clearable
                  class="search-input"
              >
                <template #prefix>
                  <el-icon>
                    <Search/>
                  </el-icon>
                </template>
              </el-input>
            </div>
          </template>
          <div class="knowledge-base-list">
            <div v-if="loading" class="loading-container">
              <el-skeleton animated>
                <template #template>
                  <el-skeleton-item variant="text" style="width: 50%"/>
                  <el-skeleton-item variant="text" style="width: 70%"/>
                  <el-skeleton-item variant="text" style="width: 60%"/>
                </template>
              </el-skeleton>
            </div>

            <el-menu
                v-else
                :default-active="activeKnowledgeBaseId"
                @select="handleSelectKnowledgeBase"
                class="knowledge-base-menu"
            >
              <el-menu-item
                  v-for="kb in filteredKnowledgeBases"
                  :key="kb.id"
                  :index="kb.id.toString()"
              >
                <el-icon>
                  <Document/>
                </el-icon>
                <span>{{ kb.name }}</span>
                <el-tag
                    size="small"
                    :type="kb.status === 'active' ? 'success' : 'info'"
                    class="status-tag"
                >
                  {{ kb.status === 'active' ? '启用' : '停用' }}
                </el-tag>
              </el-menu-item>
            </el-menu>
          </div>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card v-if="activeKnowledgeBase" class="main-content-card">
          <template #header>
            <div class="content-header">
              <div class="title-section">
                <h3>{{ activeKnowledgeBase.name }}</h3>
              </div>
              <div class="action-buttons">
                <el-button @click="handleEditKnowledgeBase">编辑</el-button>
                <el-button
                    :type="activeKnowledgeBase.status === 'active' ? 'danger' : 'success'"
                    @click="handleChangeStatus"
                >
                  {{ activeKnowledgeBase.status === 'active' ? '停用' : '启用' }}
                </el-button>
                <el-button type="primary" @click="handleManageDocuments">管理文档</el-button>
              </div>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="创建时间">
              {{ formatDate(activeKnowledgeBase.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDate(activeKnowledgeBase.updated_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="文档数量">
              {{ activeKnowledgeBase.documentCount || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="文档分块大小">
              {{ activeKnowledgeBase.chunk_size }}
            </el-descriptions-item>
            <el-descriptions-item label="重叠大小">
              {{ activeKnowledgeBase.chunk_overlap }}
            </el-descriptions-item>
            <el-descriptions-item label="向量数据库">
              {{ activeKnowledgeBase.vector_db_type }}
            </el-descriptions-item>
            <el-descriptions-item label="标签" :span="2">
              <el-tag
                  v-for="tag in activeKnowledgeBase.tags"
                  :key="tag"
                  style="margin-right: 8px;"
              >
                {{ tag }}
              </el-tag>
              <span v-if="!activeKnowledgeBase.tags || activeKnowledgeBase.tags.length === 0">无标签</span>
            </el-descriptions-item>
            <el-descriptions-item label="描述" :span="2">
              {{ activeKnowledgeBase.description || '暂无描述' }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="statistics-section">
            <h4>统计信息</h4>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-number">{{ activeKnowledgeBase.documentCount || 0 }}</div>
                    <div class="stat-label">文档数量</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-number">{{ activeKnowledgeBase.chunkCount || 0 }}</div>
                    <div class="stat-label">文本块数量</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-number">{{ activeKnowledgeBase.queryCount || 0 }}</div>
                    <div class="stat-label">查询次数</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <el-card v-else class="empty-content-card">
          <el-empty description="请选择一个知识库或创建新的知识库"/>
        </el-card>
      </el-col>
    </el-row>

    <!-- 知识库编辑/创建对话框 -->
    <el-dialog
        v-model="knowledgeBaseDialogVisible"
        :title="editingKnowledgeBase ? '编辑知识库' : '新建知识库'"
        width="500px"
    >
      <el-form
          ref="knowledgeBaseFormRef"
          :model="knowledgeBaseForm"
          :rules="knowledgeBaseRules"
          label-width="100px"
      >
        <el-form-item label="知识库名称" prop="name">
          <el-input
              v-model="knowledgeBaseForm.name"
              placeholder="请输入知识库名称"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
              v-model="knowledgeBaseForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入知识库描述"
          />
        </el-form-item>

        <el-form-item label="标签">
          <div class="tags-container">
            <el-tag
                v-for="tag in knowledgeBaseForm.tags"
                :key="tag"
                closable
                @close="removeTag(tag)"
                style="margin-right: 10px; margin-bottom: 10px;"
            >
              {{ tag }}
            </el-tag>

            <el-input
                v-model="newTag"
                placeholder="请输入标签"
                size="small"
                style="width: 150px; margin-bottom: 10px;"
                @keyup.enter="addTag"
            >
              <template #append>
                <el-button @click="addTag">添加</el-button>
              </template>
            </el-input>
          </div>
        </el-form-item>

        <el-form-item label="Chunk大小">
          <el-select
              v-model="knowledgeBaseForm.chunk_size"
              placeholder="请选择Chunk大小">
            <el-option
                v-for="size in chunkSizeOptions"
                :key="size"
                :label="size"
                :value="size">
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="重叠大小">
          <el-input-number
              v-model="knowledgeBaseForm.chunk_overlap"
              :min="0"
              :max="knowledgeBaseForm.chunk_size / 2"
              :step="10"
              controls-position="right"/>
        </el-form-item>

        <el-form-item label="向量数据库">
          <el-select v-model="knowledgeBaseForm.vector_db_type" placeholder="请选择向量数据库">
            <el-option label="Milvus" value="milvus"></el-option>
            <el-option label="Chroma" value="chroma"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="knowledgeBaseForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="knowledgeBaseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveKnowledgeBase">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {computed, onMounted, reactive, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {toast} from "@/components/utils.js";
import {Document, Plus, Search} from '@element-plus/icons-vue'
import {getKnowledgeList, updateKnowledge,updateKnowledgeStatus} from '@/services/knowledge'
import {getCookie} from '@/components/cookie'

export default {
  name: 'KnowledgeManager',
  components: {
    Plus,
    Search,
    Document
  },
  setup() {
    const router = useRouter()

    const knowledgeBases = ref([])
    const loading = ref(false)

    const searchKeyword = ref('')
    const activeKnowledgeBaseId = ref('')
    const knowledgeBaseDialogVisible = ref(false)
    const editingKnowledgeBase = ref(null)
    const knowledgeBaseFormRef = ref()
    const newTag = ref('')

    // 预定义的chunk大小选项
    const chunkSizeOptions = [128, 256, 512, 1024, 2048]

    const knowledgeBaseForm = reactive({
      id: null,
      name: '',
      description: '',
      tags: [],
      chunk_size: 1024,
      chunk_overlap: 20,
      vector_db_type: 'milvus',
      status: 'active'
    })

    const knowledgeBaseRules = {
      name: [
        {required: true, message: '请输入知识库名称', trigger: 'blur'}
      ]
    }

    // 计算属性
    const filteredKnowledgeBases = computed(() => {
      if (!searchKeyword.value) {
        return knowledgeBases.value
      }
      return knowledgeBases.value.filter(kb =>
          kb.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
          (kb.description && kb.description.toLowerCase().includes(searchKeyword.value.toLowerCase()))
      )
    })

    const activeKnowledgeBase = computed(() => {
      return knowledgeBases.value.find(kb => kb.id.toString() === activeKnowledgeBaseId.value)
    })

    // 监听chunk_size变化，更新chunk_overlap最大值并调整为10的倍数
    watch(() => knowledgeBaseForm.chunk_size, (newVal) => {
      const maxOverlap = Math.floor(newVal / 2);
      // 调整重叠大小为最接近的10的倍数
      const adjustedOverlap = Math.floor(maxOverlap / 10) * 10;
      if (knowledgeBaseForm.chunk_overlap > maxOverlap) {
        knowledgeBaseForm.chunk_overlap = adjustedOverlap;
      }
    });

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
    }

    // 获取知识库列表
    const fetchKnowledgeBases = async () => {
      try {
        loading.value = true
        // 从cookie中获取user_id
        const userId = getCookie('user_id')
        if (!userId) {
          toast('未找到用户信息，请重新登录', 'error')
          return
        }

        const response = await getKnowledgeList(userId)
        // 根据API返回的数据格式进行处理
        knowledgeBases.value = response.data.map(item => ({
          id: item.id,
          name: item.name,
          description: item.description,
          tags: item.tags || [],
          chunk_size: item.chunk_size,
          chunk_overlap: item.chunk_overlap,
          vector_db_type: item.vector_db_type,
          status: item.status || 'inactive', // 默认为inactive
          created_at: item.created_at,
          updated_at: item.updated_at,
          documentCount: item.document_count || 0,
          chunkCount: item.chunk_total || 0,
          queryCount: item.query_count || 0
        }))

        // 默认选中第一个知识库
        if (knowledgeBases.value.length > 0 && !activeKnowledgeBaseId.value) {
          activeKnowledgeBaseId.value = knowledgeBases.value[0].id.toString()
        }
      } catch (error) {
        console.error('获取知识库列表失败:', error)
        toast('获取知识库列表失败', 'error')
      } finally {
        loading.value = false
      }
    }

    // 添加标签
    const addTag = () => {
      if (newTag.value && !knowledgeBaseForm.tags.includes(newTag.value)) {
        knowledgeBaseForm.tags.push(newTag.value)
        newTag.value = ''
      }
    }

    // 删除标签
    const removeTag = (tag) => {
      knowledgeBaseForm.tags = knowledgeBaseForm.tags.filter(t => t !== tag)
    }

    // 方法
    const handleSelectKnowledgeBase = (index) => {
      activeKnowledgeBaseId.value = index
    }

    const handleAddKnowledgeBase = () => {
      router.push({name: 'CreateKnowledge'})
    }

    const handleEditKnowledgeBase = () => {
      if (!activeKnowledgeBase.value) return

      editingKnowledgeBase.value = activeKnowledgeBase.value
      // 设置表单数据
      knowledgeBaseForm.id = activeKnowledgeBase.value.id
      knowledgeBaseForm.name = activeKnowledgeBase.value.name
      knowledgeBaseForm.description = activeKnowledgeBase.value.description
      knowledgeBaseForm.tags = [...(activeKnowledgeBase.value.tags || [])]
      knowledgeBaseForm.chunk_size = activeKnowledgeBase.value.chunk_size
      knowledgeBaseForm.chunk_overlap = activeKnowledgeBase.value.chunk_overlap
      knowledgeBaseForm.vector_db_type = activeKnowledgeBase.value.vector_db_type
      knowledgeBaseForm.status = activeKnowledgeBase.value.status
      knowledgeBaseDialogVisible.value = true
    }

    const handleChangeStatus = async () => {
      if (!activeKnowledgeBase.value) return

      try {
        const kb = knowledgeBases.value.find(k => k.id.toString() === activeKnowledgeBaseId.value)
        if (kb) {
          const newStatus = kb.status === 'active' ? 'inactive' : 'active'

          // 使用专用的状态更新接口
          await updateKnowledgeStatus({
            id: kb.id,
            status: newStatus
          })

          kb.status = newStatus
          toast(`知识库已${newStatus === 'active' ? '启用' : '停用'}`)
        }
      } catch (error) {
        console.error('更新知识库状态失败:', error)
        toast('更新知识库状态失败', 'error')
      }
    }


    const handleManageDocuments = () => {
      if (activeKnowledgeBase.value) {
        router.push({
          name: 'DocsManager',
          params: { id: activeKnowledgeBase.value.id }
        })
      }
    }

    const saveKnowledgeBase = async () => {
      try {
        const valid = await knowledgeBaseFormRef.value.validate();
        if (!valid) return;

        // 获取用户ID
        const userId = getCookie('user_id');
        if (!userId) {
          toast('未找到用户信息，请重新登录', 'error');
          return;
        }

        if (editingKnowledgeBase.value) {
          // 准备更新数据
          const updateData = {
            id: editingKnowledgeBase.value.id,
            name: knowledgeBaseForm.name,
            description: knowledgeBaseForm.description,
            tags: [...knowledgeBaseForm.tags],
            chunk_size: knowledgeBaseForm.chunk_size,
            chunk_overlap: knowledgeBaseForm.chunk_overlap,
            vector_db_type: knowledgeBaseForm.vector_db_type,
            status: knowledgeBaseForm.status,
          };

          // 调用更新API
          await updateKnowledge(updateData);

          // 更新本地数据
          const index = knowledgeBases.value.findIndex(kb => kb.id === editingKnowledgeBase.value.id)
          if (index !== -1) {
            knowledgeBases.value[index] = {
              ...knowledgeBases.value[index],
              name: knowledgeBaseForm.name,
              description: knowledgeBaseForm.description,
              tags: [...knowledgeBaseForm.tags],
              chunk_size: knowledgeBaseForm.chunk_size,
              chunk_overlap: knowledgeBaseForm.chunk_overlap,
              vector_db_type: knowledgeBaseForm.vector_db_type,
              status: knowledgeBaseForm.status,
              updated_at: new Date().toISOString()
            }
            toast('知识库已更新')
          }
        } else {
          // 创建逻辑保持不变
          const newKnowledgeBase = {
            id: Math.max(0, ...knowledgeBases.value.map(kb => kb.id)) + 1,
            name: knowledgeBaseForm.name,
            description: knowledgeBaseForm.description,
            tags: [...knowledgeBaseForm.tags],
            chunk_size: knowledgeBaseForm.chunk_size,
            chunk_overlap: knowledgeBaseForm.chunk_overlap,
            vector_db_type: knowledgeBaseForm.vector_db_type,
            status: knowledgeBaseForm.status,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            documentCount: 0,
            chunkCount: 0,
            queryCount: 0
          }
          knowledgeBases.value.push(newKnowledgeBase)
          toast('知识库已创建')
        }

        knowledgeBaseDialogVisible.value = false
      } catch (error) {
        console.error('保存知识库失败:', error)
        toast('保存知识库失败', 'error')
      }
    }


    onMounted(() => {
      fetchKnowledgeBases()
    })

    return {
      searchKeyword,
      activeKnowledgeBaseId,
      knowledgeBaseDialogVisible,
      editingKnowledgeBase,
      knowledgeBaseFormRef,
      knowledgeBaseForm,
      knowledgeBaseRules,
      filteredKnowledgeBases,
      activeKnowledgeBase,
      loading,
      newTag,
      formatDate,
      handleSelectKnowledgeBase,
      handleAddKnowledgeBase,
      handleEditKnowledgeBase,
      handleChangeStatus,
      handleManageDocuments,
      saveKnowledgeBase,
      addTag,
      removeTag,
      chunkSizeOptions
    }
  }
}
</script>


<style scoped>
.rag-manager-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 84px);
}

.header-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.highlight-title {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
  margin: 0;
  position: relative;
}

.highlight-title::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(90deg, #1890ff, #00bfff);
  border-radius: 2px;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.content-row {
  margin-bottom: 20px;
}

.sidebar-card,
.main-content-card,
.empty-content-card {
  height: 100%;
}

.sidebar-header {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.search-input {
  width: 100%;
}

.knowledge-base-menu {
  border-right: none;
}

.knowledge-base-menu .el-menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-tag {
  margin-left: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-tag-large {
  font-size: 14px;
}

.statistics-section {
  margin-top: 30px;
}

.statistics-section h4 {
  margin-bottom: 15px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 20px 0;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.loading-container {
  padding: 20px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
</style>
