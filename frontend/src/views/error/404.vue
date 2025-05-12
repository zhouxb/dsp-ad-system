<template>
  <div class="error-container">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">页面不存在</h2>
      <p class="error-description">抱歉，您访问的页面不存在或已被移除</p>
      <a-button type="primary" size="large" @click="goHome">
        返回首页
      </a-button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'NotFound',
  setup() {
    const router = useRouter()

    const goHome = () => {
      router.push('/')
    }

    return {
      goHome
    }
  }
})
</script>

<style lang="less" scoped>
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.error-content {
  text-align: center;
  padding: 48px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #1890ff;
  margin: 0 0 16px;
  line-height: 1.1;
}

.error-title {
  font-size: 24px;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 16px;
}

.error-description {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 32px;
}
</style> 