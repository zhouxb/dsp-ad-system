<template>
  <div class="creative-detail">
    <a-card>
      <template #title>
        <div class="card-title">
          <span>创意详情</span>
          <a-space>
            <a-button @click="handleBack">返回</a-button>
            <a-button type="primary" @click="handleEdit">编辑</a-button>
          </a-space>
        </div>
      </template>

      <a-descriptions bordered>
        <a-descriptions-item label="创意名称" :span="3">
          {{ creative.name }}
        </a-descriptions-item>
        <a-descriptions-item label="类型">
          {{ getTypeText(creative.type) }}
        </a-descriptions-item>
        <a-descriptions-item label="尺寸">
          {{ creative.size }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(creative.status)">
            {{ getStatusText(creative.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ creative.createdAt }}
        </a-descriptions-item>
        <a-descriptions-item label="更新时间">
          {{ creative.updatedAt }}
        </a-descriptions-item>
        <a-descriptions-item label="创建人">
          {{ creative.creator }}
        </a-descriptions-item>
        <a-descriptions-item label="描述" :span="3">
          {{ creative.description }}
        </a-descriptions-item>
      </a-descriptions>

      <!-- 创意预览 -->
      <div class="preview-section">
        <h3>创意预览</h3>
        <div class="preview-container">
          <img
            v-if="creative.type === 'image'"
            :src="creative.previewUrl"
            :alt="creative.name"
            class="preview-image"
          />
          <video
            v-else-if="creative.type === 'video'"
            :src="creative.previewUrl"
            class="preview-video"
            controls
          ></video>
          <div v-else class="preview-html">
            <html-outlined />
            <span>HTML5</span>
            <a-button type="link" @click="handlePreviewHtml">预览</a-button>
          </div>
        </div>
      </div>

      <!-- 投放数据 -->
      <div class="performance-section">
        <h3>投放数据</h3>
        <a-row :gutter="16">
          <a-col :span="6">
            <a-statistic
              title="展示量"
              :value="creative.impressions"
              :precision="0"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="点击量"
              :value="creative.clicks"
              :precision="0"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="点击率"
              :value="creative.ctr"
              :precision="2"
              suffix="%"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="转化量"
              :value="creative.conversions"
              :precision="0"
            />
          </a-col>
        </a-row>
      </div>

      <!-- 趋势图表 -->
      <div class="trend-chart">
        <h3>数据趋势</h3>
        <div ref="chartRef" style="height: 400px"></div>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { HtmlOutlined } from '@ant-design/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const chartRef = ref<HTMLElement>()

// 模拟数据
const creative = ref({
  id: 1,
  name: '夏季促销banner',
  type: 'image',
  size: '300x250',
  status: 'active',
  createdAt: '2024-04-15 10:00:00',
  updatedAt: '2024-04-16 15:30:00',
  creator: '张三',
  description: '这是一个夏季促销活动的banner广告，主要展示夏季特价商品。',
  previewUrl: 'https://example.com/preview1.jpg',
  impressions: 100000,
  clicks: 5000,
  ctr: 5.0,
  conversions: 500
})

// 获取类型文本
const getTypeText = (type: string) => {
  const texts: Record<string, string> = {
    image: '图片',
    video: '视频',
    html: 'HTML5'
  }
  return texts[type] || type
}

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    active: 'green',
    inactive: 'orange',
    pending: 'blue',
    rejected: 'red'
  }
  return colors[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    active: '已启用',
    inactive: '已禁用',
    pending: '待审核',
    rejected: '已拒绝'
  }
  return texts[status] || status
}

// 处理返回
const handleBack = () => {
  router.back()
}

// 处理编辑
const handleEdit = () => {
  router.push(`/creatives/${creative.value.id}/edit`)
}

// 处理HTML5预览
const handlePreviewHtml = () => {
  // TODO: 实现HTML5预览逻辑
  console.log('预览HTML5创意')
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return

  const chart = echarts.init(chartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['展示量', '点击量', '转化量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '展示量',
        type: 'line',
        data: [120, 132, 101, 134, 90, 230, 210]
      },
      {
        name: '点击量',
        type: 'line',
        data: [220, 182, 191, 234, 290, 330, 310]
      },
      {
        name: '转化量',
        type: 'line',
        data: [150, 232, 201, 154, 190, 330, 410]
      }
    ]
  }
  chart.setOption(option)
}

onMounted(() => {
  initChart()
})
</script>

<style lang="less" scoped>
.creative-detail {
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .preview-section {
    margin-top: 24px;

    h3 {
      margin-bottom: 16px;
    }

    .preview-container {
      width: 100%;
      max-width: 800px;
      height: 400px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      border-radius: 4px;
      overflow: hidden;

      .preview-image {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
      }

      .preview-video {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
      }

      .preview-html {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #1890ff;
      }
    }
  }

  .performance-section {
    margin-top: 24px;
    padding: 24px;
    background: #fafafa;
    border-radius: 4px;

    h3 {
      margin-bottom: 16px;
    }
  }

  .trend-chart {
    margin-top: 24px;

    h3 {
      margin-bottom: 16px;
    }
  }
}
</style> 