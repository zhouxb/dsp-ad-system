<template>
  <div class="report-index">
    <a-row :gutter="16">
      <!-- 数据概览卡片 -->
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="今日消耗"
            :value="statistics.todaySpend"
            :precision="2"
            prefix="¥"
          >
            <template #suffix>
              <span class="trend" :class="{ up: statistics.spendTrend > 0 }">
                {{ statistics.spendTrend > 0 ? '+' : '' }}{{ statistics.spendTrend }}%
              </span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="今日展示"
            :value="statistics.todayImpressions"
            :precision="0"
          >
            <template #suffix>
              <span class="trend" :class="{ up: statistics.impressionsTrend > 0 }">
                {{ statistics.impressionsTrend > 0 ? '+' : '' }}{{ statistics.impressionsTrend }}%
              </span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="今日点击"
            :value="statistics.todayClicks"
            :precision="0"
          >
            <template #suffix>
              <span class="trend" :class="{ up: statistics.clicksTrend > 0 }">
                {{ statistics.clicksTrend > 0 ? '+' : '' }}{{ statistics.clicksTrend }}%
              </span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="今日转化"
            :value="statistics.todayConversions"
            :precision="0"
          >
            <template #suffix>
              <span class="trend" :class="{ up: statistics.conversionsTrend > 0 }">
                {{ statistics.conversionsTrend > 0 ? '+' : '' }}{{ statistics.conversionsTrend }}%
              </span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <!-- 趋势图表 -->
    <a-card class="trend-card">
      <template #title>
        <div class="card-title">
          <span>数据趋势</span>
          <a-radio-group v-model:value="trendTimeRange" button-style="solid">
            <a-radio-button value="7">近7天</a-radio-button>
            <a-radio-button value="30">近30天</a-radio-button>
            <a-radio-button value="90">近90天</a-radio-button>
          </a-radio-group>
        </div>
      </template>
      <div ref="trendChartRef" style="height: 400px"></div>
    </a-card>

    <!-- 数据分布 -->
    <a-row :gutter="16" class="distribution-row">
      <a-col :span="12">
        <a-card title="广告类型分布">
          <div ref="typeChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="投放渠道分布">
          <div ref="channelChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 数据表格 -->
    <a-card title="详细数据" class="data-table-card">
      <a-table
        :columns="columns"
        :data-source="tableData"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'ctr'">
            {{ record.ctr }}%
          </template>
          <template v-if="column.key === 'cvr'">
            {{ record.cvr }}%
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import * as echarts from 'echarts'

// 统计数据
const statistics = reactive({
  todaySpend: 12345.67,
  spendTrend: 5.2,
  todayImpressions: 123456,
  impressionsTrend: -2.1,
  todayClicks: 5678,
  clicksTrend: 3.4,
  todayConversions: 234,
  conversionsTrend: 1.5
})

// 趋势时间范围
const trendTimeRange = ref('7')

// 图表引用
const trendChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
const channelChartRef = ref<HTMLElement>()

// 表格列定义
const columns = [
  {
    title: '日期',
    dataIndex: 'date',
    key: 'date'
  },
  {
    title: '消耗',
    dataIndex: 'spend',
    key: 'spend'
  },
  {
    title: '展示量',
    dataIndex: 'impressions',
    key: 'impressions'
  },
  {
    title: '点击量',
    dataIndex: 'clicks',
    key: 'clicks'
  },
  {
    title: '点击率',
    dataIndex: 'ctr',
    key: 'ctr'
  },
  {
    title: '转化量',
    dataIndex: 'conversions',
    key: 'conversions'
  },
  {
    title: '转化率',
    dataIndex: 'cvr',
    key: 'cvr'
  }
]

// 表格数据
const tableData = ref([
  {
    key: '1',
    date: '2024-04-17',
    spend: '¥12,345.67',
    impressions: 123456,
    clicks: 5678,
    ctr: 4.6,
    conversions: 234,
    cvr: 4.1
  },
  {
    key: '2',
    date: '2024-04-16',
    spend: '¥11,234.56',
    impressions: 112345,
    clicks: 5123,
    ctr: 4.6,
    conversions: 212,
    cvr: 4.1
  }
])

const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 100
})

// 处理表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  // TODO: 重新加载数据
}

// 初始化趋势图表
const initTrendChart = () => {
  if (!trendChartRef.value) return

  const chart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['消耗', '展示量', '点击量', '转化量']
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
    yAxis: [
      {
        type: 'value',
        name: '金额',
        axisLabel: {
          formatter: '¥{value}'
        }
      },
      {
        type: 'value',
        name: '数量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '消耗',
        type: 'line',
        yAxisIndex: 0,
        data: [12000, 13200, 10100, 13400, 9000, 23000, 21000]
      },
      {
        name: '展示量',
        type: 'line',
        yAxisIndex: 1,
        data: [120000, 132000, 101000, 134000, 90000, 230000, 210000]
      },
      {
        name: '点击量',
        type: 'line',
        yAxisIndex: 1,
        data: [5000, 5200, 5100, 5400, 4900, 5300, 5100]
      },
      {
        name: '转化量',
        type: 'line',
        yAxisIndex: 1,
        data: [200, 220, 210, 240, 190, 230, 210]
      }
    ]
  }
  chart.setOption(option)
}

// 初始化类型分布图表
const initTypeChart = () => {
  if (!typeChartRef.value) return

  const chart = echarts.init(typeChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '广告类型',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 1048, name: '图片广告' },
          { value: 735, name: '视频广告' },
          { value: 580, name: 'HTML5广告' },
          { value: 484, name: '原生广告' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  chart.setOption(option)
}

// 初始化渠道分布图表
const initChannelChart = () => {
  if (!channelChartRef.value) return

  const chart = echarts.init(channelChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '投放渠道',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 1048, name: '移动端' },
          { value: 735, name: 'PC端' },
          { value: 580, name: '平板端' },
          { value: 484, name: '其他' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  chart.setOption(option)
}

onMounted(() => {
  initTrendChart()
  initTypeChart()
  initChannelChart()
})
</script>

<style lang="less" scoped>
.report-index {
  .trend {
    font-size: 14px;
    margin-left: 8px;
    color: #f5222d;

    &.up {
      color: #52c41a;
    }
  }

  .trend-card {
    margin-top: 16px;

    .card-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .distribution-row {
    margin-top: 16px;
  }

  .data-table-card {
    margin-top: 16px;
  }
}
</style> 