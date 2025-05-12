<template>
  <div class="campaign-detail">
    <a-card>
      <template #title>
        <div class="card-title">
          <span>广告活动详情</span>
          <a-space>
            <a-button @click="handleBack">返回</a-button>
            <a-button type="primary" @click="handleEdit">编辑</a-button>
          </a-space>
        </div>
      </template>

      <a-descriptions bordered>
        <a-descriptions-item label="活动名称" :span="3">
          {{ campaign.name }}
        </a-descriptions-item>
        <a-descriptions-item label="广告主" :span="3">
          {{ campaign.advertiser }}
        </a-descriptions-item>
        <a-descriptions-item label="预算">
          ¥{{ campaign.budget }}
        </a-descriptions-item>
        <a-descriptions-item label="消耗">
          ¥{{ campaign.spend }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="getStatusColor(campaign.status)">
            {{ getStatusText(campaign.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="开始时间">
          {{ campaign.startDate }}
        </a-descriptions-item>
        <a-descriptions-item label="结束时间">
          {{ campaign.endDate }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ campaign.createdAt }}
        </a-descriptions-item>
        <a-descriptions-item label="描述" :span="3">
          {{ campaign.description }}
        </a-descriptions-item>
      </a-descriptions>

      <!-- 数据概览 -->
      <div class="data-overview">
        <h3>数据概览</h3>
        <a-row :gutter="16">
          <a-col :span="6">
            <a-statistic
              title="展示量"
              :value="campaign.impressions"
              :precision="0"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="点击量"
              :value="campaign.clicks"
              :precision="0"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="点击率"
              :value="campaign.ctr"
              :precision="2"
              suffix="%"
            />
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="转化量"
              :value="campaign.conversions"
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
import * as echarts from 'echarts'

const router = useRouter()
const chartRef = ref<HTMLElement>()

// 模拟数据
const campaign = ref({
  id: 1,
  name: '夏季促销活动',
  advertiser: 'ABC公司',
  budget: 10000,
  spend: 5000,
  status: 'active',
  startDate: '2024-05-01',
  endDate: '2024-08-31',
  createdAt: '2024-04-15 10:00:00',
  description: '这是一个夏季促销活动，主要推广夏季新品和特价商品。',
  impressions: 100000,
  clicks: 5000,
  ctr: 5.0,
  conversions: 500
})

// 获取状态颜色
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    active: 'green',
    paused: 'orange',
    ended: 'red'
  }
  return colors[status] || 'default'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    active: '进行中',
    paused: '已暂停',
    ended: '已结束'
  }
  return texts[status] || status
}

// 处理返回
const handleBack = () => {
  router.back()
}

// 处理编辑
const handleEdit = () => {
  router.push(`/campaigns/${campaign.value.id}/edit`)
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
      data: ['展示量', '点击量', '转化量', '消耗']
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
      },
      {
        name: '消耗',
        type: 'line',
        data: [320, 332, 301, 334, 390, 330, 320]
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
.campaign-detail {
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .data-overview {
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