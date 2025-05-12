<template>
  <div class="settings-index">
    <a-row :gutter="16">
      <!-- 系统信息卡片 -->
      <a-col :span="8">
        <a-card title="系统信息" class="info-card">
          <a-descriptions :column="1">
            <a-descriptions-item label="系统名称">
              DSP广告投放系统
            </a-descriptions-item>
            <a-descriptions-item label="系统版本">
              v1.0.0
            </a-descriptions-item>
            <a-descriptions-item label="最后更新">
              2024-04-17
            </a-descriptions-item>
            <a-descriptions-item label="系统状态">
              <a-tag color="success">运行中</a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-col>

      <!-- 系统资源卡片 -->
      <a-col :span="8">
        <a-card title="系统资源" class="resource-card">
          <a-progress
            :percent="80"
            :format="percent => `CPU: ${percent}%`"
            status="active"
          />
          <a-progress
            :percent="60"
            :format="percent => `内存: ${percent}%`"
            status="active"
            style="margin-top: 16px"
          />
          <a-progress
            :percent="40"
            :format="percent => `磁盘: ${percent}%`"
            status="active"
            style="margin-top: 16px"
          />
        </a-card>
      </a-col>

      <!-- 快捷操作卡片 -->
      <a-col :span="8">
        <a-card title="快捷操作" class="action-card">
          <a-space direction="vertical" style="width: 100%">
            <a-button type="primary" block @click="handleClearCache">
              <template #icon><clear-outlined /></template>
              清除缓存
            </a-button>
            <a-button block @click="handleBackup">
              <template #icon><cloud-upload-outlined /></template>
              备份数据
            </a-button>
            <a-button block @click="handleRestore">
              <template #icon><cloud-download-outlined /></template>
              恢复数据
            </a-button>
          </a-space>
        </a-card>
      </a-col>
    </a-row>

    <!-- 系统配置表单 -->
    <a-card title="系统配置" class="config-card">
      <a-form
        :model="configForm"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="系统名称">
          <a-input v-model:value="configForm.systemName" />
        </a-form-item>
        <a-form-item label="系统Logo">
          <a-upload
            v-model:file-list="fileList"
            action="/api/upload"
            list-type="picture-card"
          >
            <div>
              <plus-outlined />
              <div style="margin-top: 8px">上传</div>
            </div>
          </a-upload>
        </a-form-item>
        <a-form-item label="系统主题">
          <a-radio-group v-model:value="configForm.theme">
            <a-radio value="light">浅色</a-radio>
            <a-radio value="dark">深色</a-radio>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="系统语言">
          <a-select v-model:value="configForm.language">
            <a-select-option value="zh_CN">简体中文</a-select-option>
            <a-select-option value="en_US">English</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="时区设置">
          <a-select v-model:value="configForm.timezone">
            <a-select-option value="Asia/Shanghai">(GMT+8) 北京</a-select-option>
            <a-select-option value="America/New_York">(GMT-5) 纽约</a-select-option>
            <a-select-option value="Europe/London">(GMT+0) 伦敦</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="数据备份">
          <a-switch
            v-model:checked="configForm.autoBackup"
            checked-children="开启"
            un-checked-children="关闭"
          />
        </a-form-item>
        <a-form-item label="备份周期">
          <a-select
            v-model:value="configForm.backupCycle"
            :disabled="!configForm.autoBackup"
          >
            <a-select-option value="daily">每天</a-select-option>
            <a-select-option value="weekly">每周</a-select-option>
            <a-select-option value="monthly">每月</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :wrapper-col="{ offset: 4 }">
          <a-button type="primary" @click="handleSaveConfig">
            保存配置
          </a-button>
          <a-button style="margin-left: 8px" @click="handleResetConfig">
            重置
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  ClearOutlined,
  CloudUploadOutlined,
  CloudDownloadOutlined,
  PlusOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

// 系统配置表单
const configForm = reactive({
  systemName: 'DSP广告投放系统',
  theme: 'light',
  language: 'zh_CN',
  timezone: 'Asia/Shanghai',
  autoBackup: true,
  backupCycle: 'daily'
})

// 文件列表
const fileList = ref([])

// 处理清除缓存
const handleClearCache = () => {
  message.success('缓存清除成功')
}

// 处理备份数据
const handleBackup = () => {
  message.success('数据备份成功')
}

// 处理恢复数据
const handleRestore = () => {
  message.success('数据恢复成功')
}

// 处理保存配置
const handleSaveConfig = () => {
  console.log('保存配置：', configForm)
  message.success('配置保存成功')
}

// 处理重置配置
const handleResetConfig = () => {
  configForm.systemName = 'DSP广告投放系统'
  configForm.theme = 'light'
  configForm.language = 'zh_CN'
  configForm.timezone = 'Asia/Shanghai'
  configForm.autoBackup = true
  configForm.backupCycle = 'daily'
  message.success('配置已重置')
}
</script>

<style lang="less" scoped>
.settings-index {
  .info-card,
  .resource-card,
  .action-card {
    margin-bottom: 16px;
  }

  .config-card {
    margin-bottom: 16px;
  }
}
</style> 