<template>
  <div class="creative-list">
    <a-card>
      <template #title>
        <div class="card-title">
          <span>创意列表</span>
          <a-button type="primary" @click="handleCreate">
            <template #icon><plus-outlined /></template>
            新建创意
          </a-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <a-form layout="inline" :model="searchForm" class="search-form">
        <a-form-item label="创意名称">
          <a-input v-model:value="searchForm.name" placeholder="请输入创意名称" />
        </a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="searchForm.type" style="width: 120px">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="image">图片</a-select-option>
            <a-select-option value="video">视频</a-select-option>
            <a-select-option value="html">HTML5</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="searchForm.status" style="width: 120px">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="active">已启用</a-select-option>
            <a-select-option value="inactive">已禁用</a-select-option>
            <a-select-option value="pending">待审核</a-select-option>
            <a-select-option value="rejected">已拒绝</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">
            <template #icon><search-outlined /></template>
            搜索
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">
            <template #icon><reload-outlined /></template>
            重置
          </a-button>
        </a-form-item>
      </a-form>

      <!-- 数据表格 -->
      <a-table
        :columns="columns"
        :data-source="creatives"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'preview'">
            <div class="preview-container">
              <img
                v-if="record.type === 'image'"
                :src="record.previewUrl"
                :alt="record.name"
                class="preview-image"
              />
              <video
                v-else-if="record.type === 'video'"
                :src="record.previewUrl"
                class="preview-video"
                controls
              ></video>
              <div v-else class="preview-html">
                <html-outlined />
                <span>HTML5</span>
              </div>
            </div>
          </template>
          <template v-if="column.key === 'status'">
            <a-tag :color="getStatusColor(record.status)">
              {{ getStatusText(record.status) }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a @click="handleEdit(record)">编辑</a>
              <a-divider type="vertical" />
              <a @click="handleView(record)">查看</a>
              <a-divider type="vertical" />
              <a-popconfirm
                title="确定要删除这个创意吗？"
                @confirm="handleDelete(record)"
              >
                <a class="danger-link">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  HtmlOutlined
} from '@ant-design/icons-vue'

const router = useRouter()

// 搜索表单数据
const searchForm = reactive({
  name: '',
  type: '',
  status: ''
})

// 表格列定义
const columns = [
  {
    title: '预览',
    dataIndex: 'preview',
    key: 'preview',
    width: 120
  },
  {
    title: '创意名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '类型',
    dataIndex: 'type',
    key: 'type'
  },
  {
    title: '尺寸',
    dataIndex: 'size',
    key: 'size'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status'
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt'
  },
  {
    title: '操作',
    key: 'action',
    width: 200
  }
]

// 模拟数据
const creatives = ref([
  {
    id: 1,
    name: '夏季促销banner',
    type: 'image',
    size: '300x250',
    status: 'active',
    createdAt: '2024-04-15 10:00:00',
    previewUrl: 'https://example.com/preview1.jpg'
  },
  {
    id: 2,
    name: '新品视频广告',
    type: 'video',
    size: '640x360',
    status: 'pending',
    createdAt: '2024-04-16 14:30:00',
    previewUrl: 'https://example.com/preview2.mp4'
  },
  {
    id: 3,
    name: '互动游戏广告',
    type: 'html',
    size: '728x90',
    status: 'active',
    createdAt: '2024-04-17 09:15:00',
    previewUrl: ''
  }
])

const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 100
})

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

// 处理搜索
const handleSearch = () => {
  console.log('搜索条件：', searchForm)
  // TODO: 实现搜索逻辑
}

// 处理重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.type = ''
  searchForm.status = ''
  handleSearch()
}

// 处理表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  // TODO: 重新加载数据
}

// 处理新建
const handleCreate = () => {
  router.push('/creatives/create')
}

// 处理编辑
const handleEdit = (record: any) => {
  router.push(`/creatives/${record.id}/edit`)
}

// 处理查看
const handleView = (record: any) => {
  router.push(`/creatives/${record.id}`)
}

// 处理删除
const handleDelete = (record: any) => {
  console.log('删除创意：', record)
  // TODO: 实现删除逻辑
}
</script>

<style lang="less" scoped>
.creative-list {
  .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .search-form {
    margin-bottom: 24px;
  }

  .preview-container {
    width: 100px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    border-radius: 4px;
    overflow: hidden;

    .preview-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .preview-video {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }

    .preview-html {
      display: flex;
      flex-direction: column;
      align-items: center;
      color: #1890ff;
    }
  }

  .danger-link {
    color: #ff4d4f;
  }
}
</style> 