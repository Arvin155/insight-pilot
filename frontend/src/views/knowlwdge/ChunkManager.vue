<template>
  <div class="chunk-manager-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="header-card">
          <div class="header-content">
            <div class="title-section">
              <h2 class="highlight-title">分块管理</h2>
              <p class="subtitle">管理文档分块，支持查看分块内容和相关信息</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :span="24">
        <el-card class="main-content-card">
          <template #header>
            <div class="content-header">
              <div class="title-section">
                <h3><span class="kb-name-highlight">{{ documentName || '未知文档' }}</span> 分块列表</h3>
              </div>
              <div class="search-section">
                <el-input
                    v-model="searchKeyword"
                    placeholder="搜索分块内容"
                    clearable
                    class="search-input"
                    style="width: 300px"
                >
                  <template #prefix>
                    <el-icon>
                      <Search/>
                    </el-icon>
                  </template>
                </el-input>
              </div>
            </div>
          </template>

          <el-table
              :data="filteredChunks"
              v-loading="loading"
              style="width: 100%"
              stripe
          >
            <el-table-column prop="chunk_index" label="分块序号" width="100">
              <template #default="{ row }">
                {{ row.chunk_index }}
              </template>
            </el-table-column>

            <el-table-column prop="page_label" label="所在页码" width="100">
              <template #default="{ row }">
                {{ row.page_label }}
              </template>
            </el-table-column>

            <el-table-column prop="content" label="分块内容" min-width="300">
              <template #default="{ row }">
                <div class="chunk-content-preview">{{ truncateContent(row.content, 50) }}</div>
              </template>
            </el-table-column>


            <el-table-column prop="metadata" label="元数据" min-width="300">
              <template #default="{ row }">
                <div class="chunk-content-preview">{{ truncateContent(row.metadata, 50) }}</div>
              </template>
            </el-table-column>

            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>

            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewChunk(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalChunks"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分块详情对话框 -->
    <el-dialog
        v-model="detailDialogVisible"
        :title="`分块详情 - #${currentChunk.chunk_index}`"
        width="80%"
        top="5vh"
    >
      <div class="chunk-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分块序号">{{ currentChunk.chunk_index }}</el-descriptions-item>
          <el-descriptions-item label="所在页码">{{ currentChunk.page_label }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentChunk.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(currentChunk.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="分块ID">{{ currentChunk.chunk_id }}</el-descriptions-item>
          <el-descriptions-item label="文档ID">{{ currentChunk.doc_id }}</el-descriptions-item>
        </el-descriptions>

        <div class="chunk-content-section">
          <h4>分块内容</h4>
          <div class="chunk-content-detail">
            <pre>{{ currentChunk.content }}</pre>
          </div>
        </div>

        <div class="chunk-metadata-section">
          <h4>元数据信息</h4>
          <div class="chunk-metadata-detail">
            <pre>{{ formatMetadata(currentChunk.rawMetadata) }}</pre>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {useRoute} from 'vue-router'
import {Search} from '@element-plus/icons-vue'
import {toast} from "@/components/utils.js"
import {getDocumentChunks} from "@/services/docs.js"

const route = useRoute()

// 响应式数据
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const documentName = ref('')
const totalChunks = ref(0)

const chunks = ref([])
const currentChunk = ref({})

// 计算属性
const filteredChunks = computed(() => {
  let result = chunks.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(chunk =>
        chunk.content.toLowerCase().includes(keyword)
    )
  }

  // 分页处理
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// 方法
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

const truncateContent = (content, length) => {
  if (!content) return ''
  return content.length > length ? content.substring(0, length) + '...' : content
}

const formatMetadata = (metadata) => {
  if (!metadata) return '{}'
  try {
    return JSON.stringify(metadata, null, 2)
  } catch (e) {
    return metadata.toString()
  }
}

// 获取分块列表
const fetchChunks = async () => {
  try {
    // 尝试多种可能的参数名称
    const documentId = route.params.documentId || route.params.id;

    if (!documentId) {
      toast('未找到文档ID，请从文档列表进入', 'error');
      return;
    }

    loading.value = true;

    const response = await getDocumentChunks(documentId);

    if (response && response.code === 200) {
      documentName.value = response.data.document_name;
      chunks.value = response.data.chunks.map(chunk => {
        let metadata = {};
        try{
          metadata = JSON.parse(chunk.document_metadata);
        } catch(e) {
          console.warn('分块元数据解析失败:', e);
        }

        // 处理 tags 字段
        let processedTags = [];
        if (metadata.tags) {
          try {
            // 如果 tags 是字符串形式的数组，需要再次解析
            if (typeof metadata.tags === 'string') {
              processedTags = JSON.parse(metadata.tags);
            } else if (Array.isArray(metadata.tags)) {
              processedTags = metadata.tags;
            }
          } catch (e) {
            console.warn('tags解析失败:', e);
            processedTags = typeof metadata.tags === 'string' ? [metadata.tags] : [];
          }
        }

        // 确保 tags 字段正确设置
        const processedMetadata = {
          ...metadata,
          tags: processedTags
        };

        return{
          id: chunk.id,
          chunk_id: chunk.chunk_id,
          chunk_index: chunk.chunk_index,
          content: chunk.content,
          page_label: chunk.page_label,
          metadata: Object.keys(processedMetadata).length > 0 ?
              JSON.stringify(processedMetadata) : '{}',
          rawMetadata: processedMetadata,
          doc_id: metadata.doc_id,
          created_at: chunk.created_at || new Date().toISOString(),
          updated_at: chunk.updated_at || new Date().toISOString()
        }
      });
      totalChunks.value = chunks.value.length;
    } else {
      const errorMsg = response?.msg || '获取分块列表失败';
      toast(errorMsg, 'error');
    }
  } catch (error) {
    console.error('获取分块列表失败:', error);
    toast('获取分块列表失败，请检查网络连接或稍后重试', 'error');
  } finally {
    loading.value = false;
  }
};


const handleViewChunk = (chunk) => {
  currentChunk.value = chunk
  detailDialogVisible.value = true
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 页面加载时获取分块列表
onMounted(() => {
  fetchChunks()
})
</script>

<style scoped>
.chunk-manager-container {
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

.main-content-card {
  height: 100%;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chunk-content-preview {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chunk-detail {
  padding: 20px 0;
}

.chunk-content-section,
.chunk-metadata-section {
  margin-top: 20px;
}

.chunk-content-section h4,
.chunk-metadata-section h4 {
  margin-bottom: 10px;
  font-weight: 600;
  color: #303133;
}

.chunk-content-detail,
.chunk-metadata-detail {
  max-height: 400px;
  overflow-y: auto;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.chunk-content-detail pre,
.chunk-metadata-detail pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: 'Courier New', monospace;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.kb-name-highlight {
  color: #1890ff;
  font-weight: 800;
  font-size: large;
  position: relative;
  padding: 2px 4px;
}

.kb-name-highlight::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #1890ff, #00bfff);
  border-radius: 2px;
}
</style>
