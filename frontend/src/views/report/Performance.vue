<template>
  <div class="performance-report">
    <!-- 筛选条件 -->
    <a-card class="filter-card">
      <a-form layout="inline" :model="filterForm">
        <a-form-item label="时间范围">
          <a-range-picker
            v-model:value="filterForm.dateRange"
            :ranges="dateRanges"
          />
        </a-form-item>
        <a-form-item label="广告主">
          <a-select
            v-model:value="filterForm.advertiser"
            style="width: 200px"
            placeholder="请选择广告主"
          >
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="1">ABC公司</a-select-option>
            <a-select-option value="2">XYZ品牌</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="广告活动">
          <a-select
            v-model:value="filterForm.campaign"
            style="width: 200px"
            placeholder="请选择广告活动"
          >
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="1">夏季促销活动</a-select-option>
            <a-select-option value="2">新品上市推广</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">
            <template #icon><search-outlined /></template>
            查询
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">
            <template #icon><reload-outlined /></template>
            重置
          </a-button>
          <a-button style="margin-left: 8px" @click="handleExport">
            <template #icon><download-outlined /></template>
            导出
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 数据概览 -->
    <a-row :gutter="16" class="overview-row">
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="总消耗"
            :value="overview.totalSpend"
            :precision="2"
            prefix="¥"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="总展示量"
            :value="overview.totalImpressions"
            :precision="0"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="总点击量"
            :value="overview.totalClicks"
            :precision="0"
          />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic
            title="总转化量"
            :value="overview.totalConversions"
            :precision="0"
          />
        </a-card>
      </a-col>
    </a-row>

    <!-- 趋势图表 -->
    <a-card class="trend-card">
      <template #title>
        <div class="card-title">
          <span>效果趋势</span>
          <a-radio-group v-model:value="trendType" button-style="solid">
            <a-radio-button value="day">按天</a-radio-button>
            <a-radio-button value="week">按周</a-radio-button>
            <a-radio-button value="month">按月</a-radio-button>
          </a-radio-group>
        </div>
      </template>
      <div ref="trendChartRef" style="height: 400px"></div>
    </a-card>

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
          <template v-if="column.key === 'cpa'">
            ¥{{ record.cpa }}
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  SearchOutlined,
  ReloadOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

// 筛选表单
const filterForm = reactive({
  dateRange: [dayjs().subtract(7, 'day'), dayjs()],
  advertiser: '',
  campaign: ''
})

// 日期范围快捷选项
const dateRanges = {
  '最近7天': [dayjs().subtract(7, 'day'), dayjs()],
  '最近30天': [dayjs().subtract(30, 'day'), dayjs()],
  '最近90天': [dayjs().subtract(90, 'day'), dayjs()]
}

// 趋势类型
const trendType = ref('day')

// 数据概览
const overview = reactive({
  totalSpend: 123456.78,
  totalImpressions: 1234567,
  totalClicks: 56789,
  totalConversions: 2345
})

// 图表引用
const trendChartRef = ref<HTMLElement>()

// 表格列定义
const columns = [
  {
    title: '日期',
    dataIndex: 'date',
    key: 'date'
  },
  {
    title: '广告主',
    dataIndex: 'advertiser',
    key: 'advertiser'
  },
  {
    title: '广告活动',
    dataIndex: 'campaign',
    key: 'campaign'
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
  },
  {
    title: 'CPA',
    dataIndex: 'cpa',
    key: 'cpa'
  }
]

// 表格数据
const tableData = ref([
  {
    key: '1',
    date: '2024-04-17',
    advertiser: 'ABC公司',
    campaign: '夏季促销活动',
    spend: '¥12,345.67',
    impressions: 123456,
    clicks: 5678,
    ctr: 4.6,
    conversions: 234,
    cvr: 4.1,
    cpa: 52.76
  },
  {
    key: '2',
    date: '2024-04-16',
    advertiser: 'XYZ品牌',
    campaign: '新品上市推广',
    spend: '¥11,234.56',
    impressions: 112345,
    clicks: 5123,
    ctr: 4.6,
    conversions: 212,
    cvr: 4.1,
    cpa: 53.00
  }
])

const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 100
})

// 处理搜索
const handleSearch = () => {
  console.log('搜索条件：', filterForm)
  // TODO: 实现搜索逻辑
}

// 处理重置
const handleReset = () => {
  filterForm.dateRange = [dayjs().subtract(7, 'day'), dayjs()]
  filterForm.advertiser = ''
  filterForm.campaign = ''
  handleSearch()
}

// 处理导出
const handleExport = () => {
  console.log('导出数据')
  // TODO: 实现导出逻辑
}

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
      data: ['消耗', '展示量', '点击量', '转化量', '点击率', '转化率']
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
      },
      {
        type: 'value',
        name: '比率',
        position: 'right',
        offset: 80,
        axisLabel: {
          formatter: '{value}%'
        }
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
      },
      {
        name: '点击率',
        type: 'line',
        yAxisIndex: 2,
        data: [4.2, 3.9, 5.0, 4.0, 5.4, 2.3, 2.4]
      },
      {
        name: '转化率',
        type: 'line',
        yAxisIndex: 2,
        data: [1.7, 1.7, 2.1, 1.8, 2.1, 1.0, 1.0]
      }
    ]
  }
  chart.setOption(option)
}

onMounted(() => {
  initTrendChart()
})
</script>

<style lang="less" scoped>
.performance-report {
  .filter-card {
    margin-bottom: 16px;
  }

  .overview-row {
    margin-bottom: 16px;
  }

  .trend-card {
    margin-bottom: 16px;

    .card-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .data-table-card {
    margin-bottom: 16px;
  }
}
</style> 