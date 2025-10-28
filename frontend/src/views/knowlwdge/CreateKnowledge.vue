<script setup>
import {ref, watch} from 'vue'
import {createKnowledge} from '@/services/knowledge'
import {toast} from "@/components/utils.js";
import {getCookie} from '@/components/cookie'
import {useRouter} from 'vue-router'

const router = useRouter()
// 预定义的chunk大小选项
const chunkSizeOptions = [128, 256, 512, 1024, 2048]

// 表单数据
const form = ref({
  name: '',
  description: '',
  tags: [],
  user_id: parseInt(getCookie('user_id')) || 1, // 从cookie获取user_id，如果获取不到则默认为1
  chunk_size: 1024,
  chunk_overlap: 20,
  vector_db_type: 'faiss',
  is_public: true
})

// 标签输入相关
const newTag = ref('')

// 监听chunk_size变化，更新chunk_overlap最大值并调整为10的倍数
watch(() => form.value.chunk_size, (newVal) => {
  const maxOverlap = Math.floor(newVal / 2);
  // 调整重叠大小为最接近的10的倍数
  const adjustedOverlap = Math.floor(maxOverlap / 10) * 10;
  if (form.value.chunk_overlap > maxOverlap) {
    form.value.chunk_overlap = adjustedOverlap;
  }
});

// 添加标签
const addTag = () => {
  if (newTag.value && !form.value.tags.includes(newTag.value)) {
    form.value.tags.push(newTag.value)
    newTag.value = ''
  }
}

// 删除标签
const removeTag = (tag) => {
  form.value.tags = form.value.tags.filter(t => t !== tag)
}

// 提交表单
const handleSubmit = async () => {
  try {
    // 在提交前再次确保使用最新的cookie中的user_id
    form.value.user_id = parseInt(getCookie('user_id')) || form.value.user_id

    const response = await createKnowledge(form.value)

    // 根据状态码判断是否成功（200表示成功）
    if (response.code === 200) {
      toast('知识库创建成功', 'success')
      // 这里可以跳转到知识库列表页面
      router.push('/knowledge_manager')
    } else {
      toast('创建知识库失败', 'error')
    }
  } catch (error) {
    console.error('创建知识库失败:', error)
    toast('创建知识库失败', 'error')
  }
}
</script>


<template>
  <div class="create-knowledge-wrapper">
    <el-card class="create-knowledge-card">
      <div class="create-knowledge">
        <h2>创建知识库</h2>
        <el-form
            :model="form"
            label-width="120px"
            style="max-width: 600px"
        >
          <el-form-item label="知识库名称" required>
            <el-input
                v-model="form.name"
                placeholder="请输入知识库名称"
            />
          </el-form-item>

          <el-form-item label="描述">
            <el-input
                v-model="form.description"
                type="textarea"
                placeholder="请输入知识库描述"
            />
          </el-form-item>

          <el-form-item label="标签">
            <div class="tags-container">
              <el-tag
                  v-for="tag in form.tags"
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

          <el-form-item label="分块块大小">
            <el-select
                v-model="form.chunk_size"
                placeholder="请选择Chunk大小"
                style="width: 30%"
            >
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
                v-model="form.chunk_overlap"
                :min="0"
                :step="10"
                controls-position="right"
                style="width: 30%"
            />
          </el-form-item>

          <el-form-item label="向量数据库">
            <el-select v-model="form.vector_db_type" placeholder="请选择向量数据库" style="width: 30%">
              <el-option label="Milvus" value="milvus"/>
              <el-option label="chroma" value="chroma"/>
            </el-select>
          </el-form-item>

          <el-form-item label="是否公开">
            <el-switch v-model="form.is_public"/>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSubmit">创建知识库</el-button>
            <el-button @click="() => form = {
              name: '',
              description: '',
              tags: [],
              user_id: parseInt(getCookie('user_id')) || 1,
              chunk_size: 1024,
              chunk_overlap: 20,
              vector_db_type: 'faiss',
              is_public: true
            }">重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>


<style scoped>
.create-knowledge-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px); /* 减去头部等高度 */
  padding: 20px;
}

.create-knowledge-card {
  width: 100%;
  max-width: 800px;
}

.create-knowledge {
  padding: 20px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
</style>
