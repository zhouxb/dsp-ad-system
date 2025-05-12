<template>
  <div class="custom-report">
    <!-- 筛选条件 -->
    <a-card class="filter-card">
      <a-form layout="inline" :model="filterForm">
        <a-form-item label="时间范围">
          <a-range-picker
            v-model:value="filterForm.dateRange"
            :ranges="dateRanges"
          />
        </a-form-item>
        <a-form-item label="维度">
          <a-select
            v-model:value="filterForm.dimensions"
            mode="multiple"
            style="width: 300px"
            placeholder="请选择维度"
          >
            <a-select-option value="date">日期</a-select-option>
            <a-select-option value="advertiser">广告主</a-select-option>
            <a-select-option value="campaign">广告活动</a-select-option>
            <a-select-option value="creative">创意</a-select-option>
            <a-select-option value="channel">渠道</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="指标">
          <a-select
            v-model:value="filterForm.metrics"
            mode="multiple"
            style="width: 300px"
            placeholder="请选择指标"
          >
            <a-select-option value="spend">消耗</a-select-option>
            <a-select-option value="impressions">展示量</a-select-option>
            <a-select-option value="clicks">点击量</a-select-option>
            <a-select-option value="ctr">点击率</a-select-option>
            <a-select-option value="conversions">转化量</a-select-option>
            <a-select-option value="cvr">转化率</a-select-option>
            <a-select-option value="cpa">CPA</a-select-option>
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
          <a-button style="margin-left: 8px" @click="handleSave">
            <template #icon><save-outlined /></template>
            保存报表
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 数据表格 -->
    <a-card title="报表数据" class="data-table-card">
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
          <template v-if="column.key === 'spend'">
            ¥{{ record.spend }}
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 保存报表对话框 -->
    <a-modal
      v-model:visible="saveModalVisible"
      title="保存报表"
      @ok="handleSaveConfirm"
      @cancel="handleSaveCancel"
    >
      <a-form :model="saveForm" layout="vertical">
        <a-form-item label="报表名称" required>
          <a-input v-model:value="saveForm.name" placeholder="请输入报表名称" />
        </a-form-item>
        <a-form-item label="报表描述">
          <a-textarea
            v-model:value="saveForm.description"
            placeholder="请输入报表描述"
            :rows="4"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  SearchOutlined,
  ReloadOutlined,
  DownloadOutlined,
  SaveOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'

// 筛选表单
const filterForm = reactive({
  dateRange: [dayjs().subtract(7, 'day'), dayjs()],
  dimensions: ['date', 'advertiser'],
  metrics: ['spend', 'impressions', 'clicks', 'ctr']
})

// 日期范围快捷选项
const dateRanges = {
  '最近7天': [dayjs().subtract(7, 'day'), dayjs()],
  '最近30天': [dayjs().subtract(30, 'day'), dayjs()],
  '最近90天': [dayjs().subtract(90, 'day'), dayjs()]
}

// 保存报表对话框
const saveModalVisible = ref(false)
const saveForm = reactive({
  name: '',
  description: ''
})

// 表格列定义
const columns = computed(() => {
  const cols = []
  
  // 添加维度列
  if (filterForm.dimensions.includes('date')) {
    cols.push({
      title: '日期',
      dataIndex: 'date',
      key: 'date'
    })
  }
  if (filterForm.dimensions.includes('advertiser')) {
    cols.push({
      title: '广告主',
      dataIndex: 'advertiser',
      key: 'advertiser'
    })
  }
  if (filterForm.dimensions.includes('campaign')) {
    cols.push({
      title: '广告活动',
      dataIndex: 'campaign',
      key: 'campaign'
    })
  }
  if (filterForm.dimensions.includes('creative')) {
    cols.push({
      title: '创意',
      dataIndex: 'creative',
      key: 'creative'
    })
  }
  if (filterForm.dimensions.includes('channel')) {
    cols.push({
      title: '渠道',
      dataIndex: 'channel',
      key: 'channel'
    })
  }

  // 添加指标列
  if (filterForm.metrics.includes('spend')) {
    cols.push({
      title: '消耗',
      dataIndex: 'spend',
      key: 'spend'
    })
  }
  if (filterForm.metrics.includes('impressions')) {
    cols.push({
      title: '展示量',
      dataIndex: 'impressions',
      key: 'impressions'
    })
  }
  if (filterForm.metrics.includes('clicks')) {
    cols.push({
      title: '点击量',
      dataIndex: 'clicks',
      key: 'clicks'
    })
  }
  if (filterForm.metrics.includes('ctr')) {
    cols.push({
      title: '点击率',
      dataIndex: 'ctr',
      key: 'ctr'
    })
  }
  if (filterForm.metrics.includes('conversions')) {
    cols.push({
      title: '转化量',
      dataIndex: 'conversions',
      key: 'conversions'
    })
  }
  if (filterForm.metrics.includes('cvr')) {
    cols.push({
      title: '转化率',
      dataIndex: 'cvr',
      key: 'cvr'
    })
  }
  if (filterForm.metrics.includes('cpa')) {
    cols.push({
      title: 'CPA',
      dataIndex: 'cpa',
      key: 'cpa'
    })
  }

  return cols
})

// 表格数据
const tableData = ref([
  {
    key: '1',
    date: '2024-04-17',
    advertiser: 'ABC公司',
    campaign: '夏季促销活动',
    creative: '创意A',
    channel: '移动端',
    spend: '12,345.67',
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
    creative: '创意B',
    channel: 'PC端',
    spend: '11,234.56',
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
  filterForm.dimensions = ['date', 'advertiser']
  filterForm.metrics = ['spend', 'impressions', 'clicks', 'ctr']
  handleSearch()
}

// 处理导出
const handleExport = () => {
  console.log('导出数据')
  // TODO: 实现导出逻辑
}

// 处理保存报表
const handleSave = () => {
  saveModalVisible.value = true
}

// 处理保存确认
const handleSaveConfirm = () => {
  console.log('保存报表：', saveForm)
  // TODO: 实现保存逻辑
  saveModalVisible.value = false
}

// 处理保存取消
const handleSaveCancel = () => {
  saveModalVisible.value = false
}

// 处理表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  // TODO: 重新加载数据
}

onMounted(() => {
  handleSearch()
})
</script>

<style lang="less" scoped>
.custom-report {
  .filter-card {
    margin-bottom: 16px;
  }

  .data-table-card {
    margin-bottom: 16px;
  }
}
</style> 