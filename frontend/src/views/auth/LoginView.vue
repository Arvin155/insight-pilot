<!-- src/views/user/Login.vue -->
<script setup>
import {onMounted, ref} from 'vue'
import {Hide, Iphone, Key, Lock, View} from '@element-plus/icons-vue'
import {useRouter} from 'vue-router'
import {login} from '@/services/auth.js'
import {toast} from '@/components/utils'
import {setCookie} from '@/components/cookie'

const router = useRouter()

const form = ref({
  mobile_phone: '',
  password: '',
  captcha: '',
})

const rules = ref({
  mobile_phone: [
    {required: true, message: '请输入手机号', trigger: 'blur'}
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {min: 6, message: '密码长度不能少于6位', trigger: 'blur'}
  ],
  captcha: [
    {required: true, message: '请输入验证码', trigger: 'blur'},
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
const captchaCode = ref('')

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
        // 调用真实的登录接口
        const loginData = {
          mobile_phone: form.value.mobile_phone,
          password: form.value.password
        }

        const response = await login(loginData)

        // 根据响应模板处理登录成功逻辑
        if (response.code === 200) {
          // 存储access_token到cookie
          setCookie('access_token', response.data.access_token, 7)

          // 存储用户信息到cookie
          setCookie('username', response.data.user.username, 7)
          setCookie('user_id', response.data.user.id, 7)

          // 登录成功提示
          toast("登录成功")

          // 跳转到首页
          router.push('/')
        } else {
          toast(response.msg || '登录失败', 'error')
        }
      } catch (error) {
        // 登录失败处理
        toast(error.message || '登录失败', 'error')
      } finally {
        loading.value = false
      }
    }
  })
}

const register = () => {
  router.push('/register')
}

// 添加跳转到忘记密码页面的方法
const goToForgotPassword = () => {
  router.push('/forgot_password')
}

onMounted(() => {
  generateCaptcha()
})
</script>

<template>
  <div class="login-wrapper">
    <div class="login-container">
      <div class="login-right">
        <div class="login-form-container">
          <h2 class="login-title">智慧数据洞察平台</h2>
          <el-form
              class="login-form"
              ref="formRef"
              :model="form"
              :rules="rules"
              @keyup.enter="onSubmit"
          >
            <el-form-item prop="mobile_phone">
              <el-input
                  size="large"
                  placeholder="请输入手机号"
                  v-model="form.mobile_phone"
              >
                <template #prefix>
                  <el-icon>
                    <Iphone/>
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
                    <Lock/>
                  </el-icon>
                </template>
                <template #suffix>
                  <el-icon
                      class="password-toggle"
                      @click="showPassword = !showPassword"
                  >
                    <View v-if="showPassword"/>
                    <Hide v-else/>
                  </el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="captcha">
              <div class="captcha-wrapper">
                <el-input
                    size="large"
                    placeholder="请输入验证码"
                    v-model="form.captcha"
                >
                  <template #prefix>
                    <el-icon>
                      <Key/>
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
                  登录
                </el-button>
                <el-button
                    size="large"
                    class="register-button"
                    @click="register"
                    round
                >
                  注册
                </el-button>
              </div>
            </el-form-item>

            <el-form-item>
              <div class="forgot-password">
                <span class="forgot-password-link" @click="goToForgotPassword">忘记密码？</span>
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
  background-color: #ebf8ff;
}

.login-container {
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  background: white;
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

.forgot-password {
  text-align: right;
  margin-top: 10px;
}

/* 修改忘记密码链接样式 */
.forgot-password-link {
  color: #1890ff;
  text-decoration: none;
  cursor: pointer;
  display: inline-block;
}

.forgot-password-link:hover {
  text-decoration: underline;
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
