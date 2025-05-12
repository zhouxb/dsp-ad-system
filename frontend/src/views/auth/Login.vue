<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <img src="@/assets/images/logo.svg" alt="Logo" class="logo" />
        <h1>DSP广告管理系统</h1>
      </div>
      
      <a-form
        :model="loginForm"
        :rules="rules"
        ref="formRef"
        class="login-form"
        @finish="handleSubmit"
      >
        <a-form-item name="username">
          <a-input
            v-model:value="loginForm.username"
            placeholder="用户名"
            size="large"
          >
            <template #prefix>
              <user-outlined class="site-form-item-icon" />
            </template>
          </a-input>
        </a-form-item>
        
        <a-form-item name="password">
          <a-input-password
            v-model:value="loginForm.password"
            placeholder="密码"
            size="large"
          >
            <template #prefix>
              <lock-outlined class="site-form-item-icon" />
            </template>
          </a-input-password>
        </a-form-item>
        
        <a-form-item>
          <a-row>
            <a-col :span="12">
              <a-checkbox v-model:checked="loginForm.remember">
                记住我
              </a-checkbox>
            </a-col>
            <a-col :span="12" class="text-right">
              <a href="javascript:;">忘记密码？</a>
            </a-col>
          </a-row>
        </a-form-item>
        
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            class="login-form-button"
            block
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>
      
      <div class="login-footer">
        <p>欢迎使用DSP广告管理系统</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/store/user'

export default defineComponent({
  name: 'Login',
  components: {
    UserOutlined,
    LockOutlined
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userStore = useUserStore()
    const formRef = ref()
    const loading = ref(false)
    
    // 登录表单数据
    const loginForm = reactive({
      username: '',
      password: '',
      remember: true
    })
    
    // 表单验证规则
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度必须在3-20个字符之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 5, message: '密码长度不能少于5个字符', trigger: 'blur' }
      ]
    }
    
    // 提交表单
    const handleSubmit = async (values: any) => {
      loading.value = true
      
      try {
        await userStore.login(values.username, values.password)
        
        message.success('登录成功')
        
        // 如果有重定向URL，跳转到该URL，否则跳转到仪表盘
        const redirectUrl = route.query.redirect as string
        router.push(redirectUrl || '/dashboard')
      } catch (error) {
        // 错误处理已在store中完成
        console.error('Login failed:', error)
      } finally {
        loading.value = false
      }
    }
    
    return {
      loginForm,
      rules,
      formRef,
      loading,
      handleSubmit
    }
  }
})
</script>

<style lang="less" scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1890ff 0%, #0050b3 100%);
}

.login-content {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  
  .logo {
    width: 80px;
    margin-bottom: 16px;
  }
  
  h1 {
    font-size: 24px;
    color: rgba(0, 0, 0, 0.85);
    margin-bottom: 0;
  }
}

.login-form {
  .login-form-button {
    height: 40px;
  }
}

.login-footer {
  margin-top: 24px;
  text-align: center;
  color: rgba(0, 0, 0, 0.45);
}

.text-right {
  text-align: right;
}
</style> 