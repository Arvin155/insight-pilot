<template>
  <div class="docs-manager-container">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="header-card">
          <div class="header-content">
            <div class="title-section">
              <h2 class="highlight-title">文档管理</h2>
              <p class="subtitle">管理知识库中的文档，支持上传、删除和查看文档详情</p>
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
                <h3><span class="kb-name-highlight">{{ knowledgeBaseName }}</span> 文档列表</h3>
              </div>
              <div class="search-section">
                <el-input
                    v-model="searchKeyword"
                    placeholder="搜索文档"
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
                <el-button type="primary" @click="handleUploadDocument">
                  <el-icon>
                    <Upload/>
                  </el-icon>
                  上传文档
                </el-button>
              </div>
            </div>
          </template>

          <el-table
              :data="filteredDocuments"
              v-loading="loading"
              style="width: 100%"
              stripe
          >
            <el-table-column prop="name" label="文档名称" min-width="200">
              <template #default="{ row }">
                <span class="document-name">{{ row.name }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getFileTypeTagType(row.type)">
                  {{ row.type.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column prop="size" label="大小" width="120">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>

            <el-table-column prop="created_at" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>

            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag
                    :type="row.status === 'processed' ? 'success' : row.status === 'processing' ? 'warning' : 'info'">
                  {{ getDocumentStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleViewChunks(row)">查看分块</el-button>
                <el-button link type="primary" @click="handleDownloadDocument(row)">下载</el-button>
                <el-button link type="danger" @click="handleDeleteDocument(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalDocuments"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 上传文档对话框 -->
    <el-dialog
        v-model="uploadDialogVisible"
        title="上传文档"
        width="650px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        class="upload-dialog"
    >
      <el-form
          ref="uploadFormRef"
          :model="uploadForm"
          :rules="uploadRules"
          label-width="100px"
          class="upload-form"
      >
        <el-form-item label="选择文件" prop="file">
          <div class="upload-area">
            <el-upload
                v-model:file-list="uploadForm.fileList"
                class="upload-demo"
                drag
                :auto-upload="false"
                :multiple="true"
                :limit="5"
                :on-exceed="handleExceed"
                :on-change="handleFileChange"
                :show-file-list="false"
            >
              <div class="upload-content">
                <el-icon class="upload-icon">
                  <UploadFilled/>
                </el-icon>
                <div class="upload-text">
                  <div class="upload-title">点击上传或拖拽文件到这里</div>
                  <div class="upload-desc">支持 PDF, DOC, DOCX, TXT, MD 格式，单个文件最大 50MB</div>
                </div>
              </div>
            </el-upload>
          </div>
        </el-form-item>

        <!-- 已选择文件列表 -->
        <div v-if="uploadForm.fileList.length > 0" class="selected-files">
          <h4 class="files-title">已选择的文件 ({{ uploadForm.fileList.length }}/5)</h4>
          <div class="file-list">
            <div
                v-for="(file, index) in uploadForm.fileList"
                :key="index"
                class="file-item"
            >
              <div class="file-info">
                <el-icon class="file-icon">
                  <Document/>
                </el-icon>
                <div class="file-details">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-meta">
                    <span class="file-size">{{ formatFileSize(file.size) }}</span>
                    <span class="file-status">待上传</span>
                  </div>
                </div>
              </div>
              <el-button
                  type="danger"
                  plain
                  size="small"
                  @click="removeFile(file)"
                  class="remove-btn"
              >
                <el-icon>
                  <Delete/>
                </el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 上传说明 -->
        <div class="upload-instructions">
          <h4>上传说明</h4>
          <ul>
            <li>支持的文件格式：PDF, DOC, DOCX, TXT, MD</li>
            <li>单个文件最大支持 50MB</li>
            <li>一次最多可选择 5 个文件</li>
            <li>文档将自动进行解析和索引处理</li>
          </ul>
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeUploadDialog" size="large">取消</el-button>
          <el-button
              type="primary"
              @click="submitUpload"
              :disabled="uploadForm.fileList.length === 0"
              :loading="uploading"
              size="large"
          >
            <el-icon v-if="uploading">
              <Loading/>
            </el-icon>
            {{ uploading ? '上传中...' : `上传 (${uploadForm.fileList.length} 个文件)` }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 文档预览对话框 -->
    <el-dialog
        v-model="previewDialogVisible"
        :title="previewDocument.name"
        width="80%"
        top="5vh"
    >
      <div class="document-preview">
        <div v-if="isPreviewable(previewDocument)" class="preview-content">
          <iframe
              v-if="previewDocument.type === 'pdf'"
              :src="previewDocument.url"
              width="100%"
              height="600px"
              frameborder="0"
          ></iframe>
          <div v-else class="text-preview">
            <pre>{{ previewContent }}</pre>
          </div>
        </div>
        <div v-else class="no-preview">
          <el-empty description="该文件类型不支持预览">
            <el-button type="primary" @click="handleDownloadDocument(previewDocument)">下载文件</el-button>
          </el-empty>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import {computed, onMounted, reactive, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {ElMessage, ElMessageBox} from 'element-plus'
import {Delete, Document, Loading, Search, Upload, UploadFilled} from '@element-plus/icons-vue'
import {toast} from "@/components/utils.js"
import {deleteDocument, downloadDocument, getDocumentList, uploadDocuments} from "@/services/docs.js"


const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const uploadFormRef = ref()
const knowledgeBaseName = ref('默认知识库')
const totalDocuments = ref(0)
const uploading = ref(false)

const documents = ref([])

const previewDocument = ref({})
const previewContent = ref('')

const uploadForm = reactive({
  fileList: []
})

const uploadRules = {
  file: [
    {required: true, message: '请选择至少一个文件', trigger: 'change'}
  ]
}

// 计算属性
const filteredDocuments = computed(() => {
  let result = documents.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(doc =>
        doc.name.toLowerCase().includes(keyword) ||
        doc.type.toLowerCase().includes(keyword)
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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 新增：解析文件大小字符串为字节数
const parseFileSize = (sizeStr) => {
  if (!sizeStr) return 0

  const units = {
    'Bytes': 1,
    'KB': 1024,
    'MB': 1024 * 1024,
    'GB': 1024 * 1024 * 1024
  }

  const matches = sizeStr.match(/^([\d.]+)\s*(Bytes|KB|MB|GB)$/)
  if (!matches) return 0

  const value = parseFloat(matches[1])
  const unit = matches[2]

  return value * units[unit]
}

const getFileTypeTagType = (type) => {
  const typeMap = {
    pdf: 'danger',
    doc: 'primary',
    docx: 'primary',
    txt: 'success',
    md: 'warning'
  }
  return typeMap[type] || 'info'
}

const getDocumentStatusText = (status) => {
  const statusMap = {
    processed: '已处理',
    processing: '处理中',
    failed: '处理失败'
  }
  return statusMap[status] || '未知'
}

const isPreviewable = (document) => {
  const previewableTypes = ['pdf', 'txt', 'md']
  return previewableTypes.includes(document.type)
}

// 获取文档列表 - 修改后的函数
const fetchDocuments = async () => {
  try {
    // 从路由参数中提取知识库ID
    const knowledgeBaseId = route.params.id || route.params.knowledgeBaseId

    // 检查知识库ID是否存在
    if (!knowledgeBaseId) {
      toast('未找到知识库ID，请返回知识库列表选择一个知识库', 'error')
      return
    }

    loading.value = true

    // 发起API请求获取文档列表
    const response = await getDocumentList(knowledgeBaseId)

    if (response && response.code === 200) {
      // 更新知识库名称
      knowledgeBaseName.value = response.data.knowledge_name

      // 处理文档数据 - 根据新数据结构调整
      const docs = response.data.documents.map(doc => ({
        id: doc.id,
        name: doc.name,
        type: doc.file_type || '',
        size: parseFileSize(doc.file_size) || 0,
        created_at: doc.created_at || new Date().toISOString(),
        status: 'processed', // 接口未返回状态，默认设为已处理
        url: '' // 可根据需要添加实际URL
      }))

      // 更新文档列表和总数
      documents.value = docs
      totalDocuments.value = docs.length
    } else {
      const errorMsg = response?.msg || '获取文档列表失败'
      toast(errorMsg, 'error')
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
    toast('获取文档列表失败，请检查网络连接或稍后重试', 'error')
  } finally {
    loading.value = false
  }
}

// 上传相关方法
const handleExceed = () => {
  ElMessage.warning('最多只能上传 5 个文件')
}

const handleFileChange = (file, fileList) => {
  // 检查文件大小
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error(`文件 ${file.name} 超过 50MB 限制`)
    // 移除超大文件
    const index = fileList.findIndex(item => item.uid === file.uid)
    if (index !== -1) {
      fileList.splice(index, 1)
    }
  }
  // 更新表单中的文件列表
  uploadForm.fileList = fileList;
}

const removeFile = (file) => {
  const index = uploadForm.fileList.findIndex(item => item.uid === file.uid)
  if (index !== -1) {
    uploadForm.fileList.splice(index, 1)
  }
}

const handleUploadDocument = () => {
  uploadForm.fileList = []
  uploadDialogVisible.value = true
}

const closeUploadDialog = () => {
  uploadDialogVisible.value = false
  uploadForm.fileList = []
}

const submitUpload = async () => {
  try {
    if (uploadForm.fileList.length === 0) {
      ElMessage.error('请选择至少一个文件')
      return
    }

    uploading.value = true

    // 获取知识库ID
    const knowledgeBaseId = route.params.id || route.params.knowledgeBaseId

    // 提取文件对象
    const files = uploadForm.fileList.map(fileObj => fileObj.raw);

    // 调用上传API
    const response = await uploadDocuments(knowledgeBaseId, files);

    if (response && response.code === 200) {
      toast(`成功上传 ${uploadForm.fileList.length} 个文档`)
      closeUploadDialog()
      // 重新获取文档列表
      await fetchDocuments()
    } else {
      const errorMsg = response?.msg || '上传失败'
      ElMessage.error(errorMsg)
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败: ' + error.message)
  } finally {
    uploading.value = false
  }
}

const handleViewChunks = (document) => {
  router.push(`/chunk_manager/${document.id}`)
}

const handleDownloadDocument = async (document) => {
  try {
    toast(`正在准备下载 ${document.name}...`)

    // 调用下载API
    const response = await downloadDocument(document.id);

    // 创建一个隐藏的a标签用于下载
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = window.document.createElement('a'); // 使用 window.document
    link.href = url;
    link.download = document.name; // 使用原始文件名
    window.document.body.appendChild(link); // 使用 window.document
    link.click();

    // 清理
    window.document.body.removeChild(link); // 使用 window.document
    window.URL.revokeObjectURL(url);

    toast(`开始下载 ${document.name}`, 'success');
  } catch (error) {
    console.error('下载失败:', error);
    toast('下载失败: ' + error.message, 'error');
  }
}


// 修改：完善删除文档逻辑
const handleDeleteDocument = (document) => {
  ElMessageBox.confirm(
      `确定要删除文档 "${document.name}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
  ).then(async () => {
    try {
      // 调用删除API
      const response = await deleteDocument(document.id);

      if (response && response.code === 200) {
        // 从前端列表中移除该文档
        const index = documents.value.findIndex(d => d.id === document.id)
        if (index > -1) {
          documents.value.splice(index, 1)
          totalDocuments.value = documents.value.length
          toast(`已删除文档 "${document.name}"`, 'success')

          // 如果当前页为空且不是第一页，则回到上一页
          const totalPages = Math.ceil(totalDocuments.value / pageSize.value)
          if (currentPage.value > 1 && filteredDocuments.value.length === 0) {
            currentPage.value = totalPages || 1
          }
        }
      } else {
        const errorMsg = response?.msg || '删除失败'
        toast(errorMsg, 'error')
      }
    } catch (error) {
      console.error('删除失败:', error)
      toast('删除失败: ' + error.message, 'error')
    }
  }).catch(() => {
    toast('已取消删除')
  })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val) => {
  currentPage.value = val
}

// 页面加载时获取文档列表
onMounted(() => {
  fetchDocuments()
})
</script>


<style scoped>
.docs-manager-container {
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

.document-name {
  font-weight: 500;
  color: #409eff;
}

.upload-demo {
  width: 100%;
}

.document-preview {
  min-height: 600px;
}

.text-preview {
  max-height: 600px;
  overflow-y: auto;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.no-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

/* 上传组件样式 */
.upload-dialog :deep(.el-dialog__body) {
  padding: 20px 30px;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  transition: all 0.3s;
  background-color: #fafafa;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
}

.upload-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-title {
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.upload-desc {
  font-size: 14px;
  color: #909399;
}

.selected-files {
  margin-top: 20px;
}

.files-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 15px;
}

.file-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.file-item:last-child {
  border-bottom: none;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.file-icon {
  font-size: 20px;
  color: #409eff;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.file-status {
  color: #67c23a;
}

.remove-btn {
  margin-left: 10px;
}

.upload-instructions {
  margin-top: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.upload-instructions h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #303133;
}

.upload-instructions ul {
  margin: 0;
  padding-left: 20px;
}

.upload-instructions li {
  margin: 5px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
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
}
</style>
