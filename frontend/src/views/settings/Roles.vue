<template>
  <div class="roles-manage">
    <!-- 搜索和操作栏 -->
    <div class="table-operations">
      <a-space>
        <a-input-search
          v-model:value="searchForm.keyword"
          placeholder="搜索角色名称"
          style="width: 200px"
          @search="handleSearch"
        />
        <a-select
          v-model:value="searchForm.status"
          style="width: 120px"
          placeholder="状态"
          @change="handleSearch"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="active">启用</a-select-option>
          <a-select-option value="inactive">禁用</a-select-option>
        </a-select>
        <a-button type="primary" @click="handleAdd">
          <template #icon><plus-outlined /></template>
          新增角色
        </a-button>
      </a-space>
    </div>

    <!-- 角色列表 -->
    <a-table
      :columns="columns"
      :data-source="tableData"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="record.status === 'active' ? 'success' : 'error'">
            {{ record.status === 'active' ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a @click="handlePermission(record)">权限设置</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="确定要删除该角色吗？"
              @confirm="handleDelete(record)"
            >
              <a class="danger-link">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 角色表单对话框 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form
        ref="formRef"
        :model="form"
        :rules="rules"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="角色名称" name="name">
          <a-input v-model:value="form.name" placeholder="请输入角色名称" />
        </a-form-item>
        <a-form-item label="角色编码" name="code">
          <a-input v-model:value="form.code" placeholder="请输入角色编码" />
        </a-form-item>
        <a-form-item label="角色描述" name="description">
          <a-textarea
            v-model:value="form.description"
            placeholder="请输入角色描述"
            :rows="4"
          />
        </a-form-item>
        <a-form-item label="状态" name="status">
          <a-radio-group v-model:value="form.status">
            <a-radio value="active">启用</a-radio>
            <a-radio value="inactive">禁用</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 权限设置对话框 -->
    <a-modal
      v-model:visible="permissionVisible"
      title="权限设置"
      width="800px"
      @ok="handlePermissionOk"
      @cancel="handlePermissionCancel"
    >
      <a-tree
        v-model:checkedKeys="permissionForm.checkedKeys"
        :tree-data="permissionTree"
        checkable
        :defaultExpandAll="true"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import type { FormInstance } from 'ant-design-vue'

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

// 表格列定义
const columns = [
  {
    title: '角色名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '角色编码',
    dataIndex: 'code',
    key: 'code'
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description'
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
    key: 'action'
  }
]

// 表格数据
const tableData = ref([
  {
    id: '1',
    name: '超级管理员',
    code: 'admin',
    description: '系统最高权限',
    status: 'active',
    createdAt: '2024-04-17 10:00:00'
  },
  {
    id: '2',
    name: '运营人员',
    code: 'operator',
    description: '负责日常运营',
    status: 'active',
    createdAt: '2024-04-17 11:00:00'
  }
])

const loading = ref(false)
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 100
})

// 表单对话框
const modalVisible = ref(false)
const modalTitle = computed(() => (form.id ? '编辑角色' : '新增角色'))
const formRef = ref<FormInstance>()
const form = reactive({
  id: '',
  name: '',
  code: '',
  description: '',
  status: 'active'
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 20, message: '角色名称长度在2-20个字符之间', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/, message: '角色编码只能包含字母、数字和下划线，且必须以字母开头', trigger: 'blur' }
  ]
}

// 权限树数据
const permissionTree = [
  {
    title: '系统管理',
    key: 'system',
    children: [
      {
        title: '用户管理',
        key: 'system:user',
        children: [
          { title: '查看用户', key: 'system:user:view' },
          { title: '创建用户', key: 'system:user:create' },
          { title: '编辑用户', key: 'system:user:edit' },
          { title: '删除用户', key: 'system:user:delete' }
        ]
      },
      {
        title: '角色管理',
        key: 'system:role',
        children: [
          { title: '查看角色', key: 'system:role:view' },
          { title: '创建角色', key: 'system:role:create' },
          { title: '编辑角色', key: 'system:role:edit' },
          { title: '删除角色', key: 'system:role:delete' }
        ]
      }
    ]
  },
  {
    title: '广告管理',
    key: 'ad',
    children: [
      {
        title: '广告主管理',
        key: 'ad:advertiser',
        children: [
          { title: '查看广告主', key: 'ad:advertiser:view' },
          { title: '创建广告主', key: 'ad:advertiser:create' },
          { title: '编辑广告主', key: 'ad:advertiser:edit' },
          { title: '删除广告主', key: 'ad:advertiser:delete' }
        ]
      },
      {
        title: '广告计划管理',
        key: 'ad:campaign',
        children: [
          { title: '查看计划', key: 'ad:campaign:view' },
          { title: '创建计划', key: 'ad:campaign:create' },
          { title: '编辑计划', key: 'ad:campaign:edit' },
          { title: '删除计划', key: 'ad:campaign:delete' }
        ]
      }
    ]
  }
]

// 权限设置对话框
const permissionVisible = ref(false)
const permissionForm = reactive({
  roleId: '',
  checkedKeys: [] as string[]
})

// 处理搜索
const handleSearch = () => {
  console.log('搜索条件：', searchForm)
  // TODO: 实现搜索逻辑
}

// 处理新增
const handleAdd = () => {
  form.id = ''
  form.name = ''
  form.code = ''
  form.description = ''
  form.status = 'active'
  modalVisible.value = true
}

// 处理编辑
const handleEdit = (record: any) => {
  form.id = record.id
  form.name = record.name
  form.code = record.code
  form.description = record.description
  form.status = record.status
  modalVisible.value = true
}

// 处理删除
const handleDelete = (record: any) => {
  console.log('删除角色：', record)
  message.success('删除成功')
}

// 处理权限设置
const handlePermission = (record: any) => {
  permissionForm.roleId = record.id
  // TODO: 获取角色已有权限
  permissionForm.checkedKeys = ['system:user:view', 'ad:campaign:view']
  permissionVisible.value = true
}

// 处理表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  // TODO: 重新加载数据
}

// 处理表单提交
const handleModalOk = async () => {
  try {
    await formRef.value?.validate()
    console.log('表单数据：', form)
    message.success(form.id ? '编辑成功' : '新增成功')
    modalVisible.value = false
  } catch (error) {
    console.error('表单验证失败：', error)
  }
}

// 处理表单取消
const handleModalCancel = () => {
  modalVisible.value = false
}

// 处理权限设置确认
const handlePermissionOk = () => {
  console.log('权限设置：', permissionForm)
  message.success('权限设置成功')
  permissionVisible.value = false
}

// 处理权限设置取消
const handlePermissionCancel = () => {
  permissionVisible.value = false
}
</script>

<style lang="less" scoped>
.roles-manage {
  .table-operations {
    margin-bottom: 16px;
  }

  .danger-link {
    color: #ff4d4f;
  }
}
</style> 