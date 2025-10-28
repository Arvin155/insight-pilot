<script setup>
import { ref, onMounted } from 'vue'
import { Hide, Iphone, Key, Lock, User, View } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { toast } from '@/components/utils'
import { checkMobile, register } from '@/services/auth.js'

const router = useRouter()

const form = ref({
  username: '',
  mobile_phone: '',
  password: '',
  confirm_password: '',
  captcha: '', // 添加验证码字段
})

const rules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3位', trigger: 'blur' }
  ],
  mobile_phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
    {
      validator: async (rule, value, callback) => {
        if (!value) {
          callback(new Error('请输入手机号'))
        } else if (!/^1[3-9]\d{9}$/.test(value)) {
          callback(new Error('请输入正确的手机号'))
        } else {
          try {
            const response = await checkMobile(value)
            if (response.code === 200 && response.data.exists) {
              callback(new Error('该手机号已被注册'))
            } else {
              callback()
            }
          } catch (error) {
            callback(new Error('手机号校验失败'))
          }
        }
      },
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.value.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  captcha: [ // 添加验证码验证规则
    { required: true, message: '请输入验证码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value.toLowerCase() !== captchaCode.value.toLowerCase()) {
          callback(new Error('验证码错误'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
})

const formRef = ref(null)
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const captchaCode = ref('') // 验证码值

// 生成随机验证码
const generateCaptcha = () => {
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
  let result = ''
  for (let i = 0; i < 4; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaCode.value = result
}

const onSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 调用注册接口
        const registerData = {
          username: form.value.username,
          mobile_phone: form.value.mobile_phone,
          password: form.value.password
        }

        const response = await register(registerData)

        // 根据响应处理注册结果
        if (response.code === 200) {
          toast("注册成功")
          // 注册成功后跳转到登录页
          router.push('/login')
        } else {
          toast(response.msg || '注册失败', 'error')
          generateCaptcha() // 注册失败时刷新验证码
        }
      } catch (error) {
        toast(error.message || '注册失败', 'error')
        generateCaptcha() // 注册失败时刷新验证码
      } finally {
        loading.value = false
      }
    }
  })
}

const backToLogin = () => {
  router.push('/login')
}

// 在组件挂载时生成初始验证码
onMounted(() => {
  generateCaptcha()
})
</script>

<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="login-right">
        <div class="login-form-container">
          <h2 class="login-title">用户注册</h2>
          <el-form
              class="login-form"
              ref="formRef"
              :model="form"
              :rules="rules"
              @keyup.enter="onSubmit"
          >
            <el-form-item prop="username">
              <el-input
                  size="large"
                  placeholder="请输入用户名"
                  v-model="form.username"
              >
                <template #prefix>
                  <el-icon>
                    <User />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="mobile_phone">
              <el-input
                  size="large"
                  placeholder="请输入手机号"
                  v-model="form.mobile_phone"
              >
                <template #prefix>
                  <el-icon>
                    <Iphone />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                  size="large"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  v-model="form.password"
              >
                <template #prefix>
                  <el-icon>
                    <Lock />
                  </el-icon>
                </template>
                <template #suffix>
                  <el-icon
                      class="password-toggle"
                      @click="showPassword = !showPassword"
                  >
                    <View v-if="showPassword" />
                    <Hide v-else />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="confirm_password">
              <el-input
                  size="large"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="请确认密码"
                  v-model="form.confirm_password"
              >
                <template #prefix>
                  <el-icon>
                    <Lock />
                  </el-icon>
                </template>
                <template #suffix>
                  <el-icon
                      class="password-toggle"
                      @click="showConfirmPassword = !showConfirmPassword"
                  >
                    <View v-if="showConfirmPassword" />
                    <Hide v-else />
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <!-- 添加验证码输入项 -->
            <el-form-item prop="captcha">
              <div class="captcha-wrapper">
                <el-input
                    size="large"
                    placeholder="请输入验证码"
                    v-model="form.captcha"
                >
                  <template #prefix>
                    <el-icon>
                      <Key />
                    </el-icon>
                  </template>
                </el-input>
                <div
                    class="captcha-code"
                    @click="generateCaptcha"
                >
                  {{ captchaCode }}
                </div>
              </div>
            </el-form-item>

            <el-form-item>
              <div class="button-group">
                <el-button
                    size="large"
                    type="primary"
                    class="login-button"
                    @click="onSubmit"
                    :loading="loading"
                    round
                >
                  注册
                </el-button>
                <el-button
                    size="large"
                    class="register-button"
                    @click="backToLogin"
                    round
                >
                  返回登录
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 500px;
  height: auto;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.login-right {
  width: 100%;
  padding: 0;
}

.login-form-container {
  width: 100%;
  max-width: 350px;
  margin: 0 auto;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f1f1f;
  text-align: center;
  margin-bottom: 30px;
}

.login-form {
  width: 100%;
}

/* 添加验证码样式 */
.captcha-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-code {
  width: 100px;
  height: 40px;
  line-height: 40px;
  text-align: center;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #1890ff;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.captcha-code:hover {
  background: #e6f7ff;
  transform: scale(1.05);
}

.button-group {
  display: flex;
  gap: 12px;
  width: 100%;
}

.login-button,
.register-button {
  flex: 1;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
}

.register-button {
  background: #f0f5ff;
  border-color: #d9e6ff;
  color: #1890ff;
}

.register-button:hover {
  background: #e6f2ff;
  border-color: #1890ff;
}

.password-toggle {
  cursor: pointer;
  color: #909399;
}

.password-toggle:hover {
  color: #1890ff;
}

@media (max-width: 768px) {
  .login-container {
    padding: 30px;
  }

  .button-group {
    flex-direction: column;
  }

  .login-button,
  .register-button {
    flex: none;
    width: 100%;
  }
}
</style>
