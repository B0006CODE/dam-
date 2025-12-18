<template>
  <div class="agent-config-sidebar" :class="{ 'open': isOpen }">
    <!-- 侧边栏头部 -->
    <div class="sidebar-header">
      <div class="sidebar-title">
        <span>配置</span>
      </div>
      <a-button
        type="text"
        size="small"
        @click="closeSidebar"
        class="close-btn"
      >
        <CloseOutlined />
      </a-button>
    </div>

    <!-- 侧边栏内容 -->
    <div class="sidebar-content">
      <div class="agent-info" v-if="selectedAgent">
        <div class="agent-basic-info">
          <p class="agent-description">{{ selectedAgent.description }}</p>
        </div>

        <a-divider />

        <div v-if="selectedAgentId && configurableItems" class="config-form-content">
          <!-- 配置表单 -->
          <a-form :model="agentConfig" layout="vertical" class="config-form">
            <a-alert
              v-if="isEmptyConfig"
              type="warning"
              message="该智能体没有配置项"
              show-icon
              class="config-alert"
            />
            <a-alert
              v-if="!selectedAgent.has_checkpointer"
              type="error"
              message="该智能体没有配置 Checkpointer，功能无法正常使用"
              show-icon
              class="config-alert"
            />

            <!-- 统一显示所有配置项 -->
            <template v-for="(value, key) in configurableItems" :key="key">
              <a-form-item
                :label="getConfigLabel(key, value)"
                :name="key"
                class="config-item"
              >
                <p v-if="value.description" class="config-description">{{ value.description }}</p>

                <!-- <div>{{ value }}</div> -->
                <!-- 模型选择 -->
                <div v-if="value.template_metadata.kind === 'llm'" class="model-selector">
                  <ModelSelectorComponent
                    @select-model="handleModelChange"
                    :model_spec="agentConfig[key] || ''"
                  />
                </div>

                <!-- 系统提示词 -->
                <div v-else-if="key === 'system_prompt'" class="system-prompt-container">
                  <!-- 编辑模式 -->
                  <a-textarea
                    v-if="systemPromptEditMode"
                    :value="agentConfig[key]"
                    @update:value="(val) => agentStore.updateAgentConfig({ [key]: val })"
                    :rows="10"
                    :placeholder="getPlaceholder(key, value)"
                    class="system-prompt-input"
                    @blur="systemPromptEditMode = false"
                    ref="systemPromptTextarea"
                  />
                  <!-- 显示模式 -->
                  <div
                    v-else
                    class="system-prompt-display"
                    @click="enterEditMode"
                  >
                    <div
                      class="system-prompt-content"
                      :class="{ 'is-placeholder': !agentConfig[key] }"
                    >
                      {{ agentConfig[key] || getPlaceholder(key, value) }}
                    </div>
                    <div class="edit-hint">点击编辑</div>
                  </div>
                </div>

                <!-- 工具选择 -->
                <div v-else-if="value.template_metadata.kind === 'tools'" class="tools-selector">
                  <div class="tools-summary">
                    <div class="tools-summary-info">
                      <span class="tools-count">已选择 {{ getSelectedCount(key) }} 个工具</span>
                      <a-button
                        type="link"
                        size="small"
                        @click="clearSelection(key)"
                        v-if="getSelectedCount(key) > 0"
                        class="clear-btn"
                      >
                        清空
                      </a-button>
                    </div>
                    <a-button
                      type="primary"
                      @click="openToolsModal"
                      class="select-tools-btn"
                      size="small"
                    >
                      选择工具
                    </a-button>
                  </div>
                  <div v-if="getSelectedCount(key) > 0" class="selected-tools-preview">
                    <a-tag
                      v-for="toolId in agentConfig[key]"
                      :key="toolId"
                      closable
                      @close="removeSelectedTool(toolId)"
                      class="tool-tag"
                    >
                      {{ getToolNameById(toolId) }}
                    </a-tag>
                  </div>
                </div>

                <!-- 布尔类型 -->
                <a-switch
                  v-else-if="typeof agentConfig[key] === 'boolean'"
                  :checked="agentConfig[key]"
                  @update:checked="(val) => agentStore.updateAgentConfig({ [key]: val })"
                />

                <!-- 单选 -->
                <a-select
                  v-else-if="value?.options && (value?.type === 'str' || value?.type === 'select')"
                  :value="agentConfig[key]"
                  @update:value="(val) => agentStore.updateAgentConfig({ [key]: val })"
                  class="config-select"
                >
                  <a-select-option v-for="option in value.options" :key="option" :value="option">
                    {{ option.label || option }}
                  </a-select-option>
                </a-select>

                <!-- 多选 -->
                <div v-else-if="value?.options && value?.type === 'list'" class="multi-select-cards">
                  <div class="multi-select-label">
                    <span>已选择 {{ getSelectedCount(key) }} 项</span>
                    <a-button
                      type="link"
                      size="small"
                      @click="clearSelection(key)"
                      v-if="getSelectedCount(key) > 0"
                    >
                      清空
                    </a-button>
                  </div>
                  <div class="options-grid">
                    <div
                      v-for="option in value.options"
                      :key="option"
                      class="option-card"
                      :class="{
                        'selected': isOptionSelected(key, option),
                        'unselected': !isOptionSelected(key, option)
                      }"
                      @click="toggleOption(key, option)"
                    >
                      <div class="option-content">
                        <span class="option-text">{{ option }}</span>
                        <div class="option-indicator">
                          <CheckCircleOutlined v-if="isOptionSelected(key, option)" />
                          <PlusCircleOutlined v-else />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 数字 -->
                <a-input-number
                  v-else-if="value?.type === 'number'"
                  :value="agentConfig[key]"
                  @update:value="(val) => agentStore.updateAgentConfig({ [key]: val })"
                  :placeholder="getPlaceholder(key, value)"
                  class="config-input-number"
                />

                <!-- 滑块 -->
                <a-slider
                  v-else-if="value?.type === 'slider'"
                  :value="agentConfig[key]"
                  @update:value="(val) => agentStore.updateAgentConfig({ [key]: val })"
                  :min="value.min"
                  :max="value.max"
                  :step="value.step"
                  class="config-slider"
                />

                <!-- 其他类型 -->
                <a-input
                  v-else
                  :value="agentConfig[key]"
                  @update:value="(val) => agentStore.updateAgentConfig({ [key]: val })"
                  :placeholder="getPlaceholder(key, value)"
                  class="config-input"
                />
              </a-form-item>
            </template>

          </a-form>
        </div>
      </div>

      <!-- 固定在底部的操作按钮 -->
      <div class="sidebar-footer" v-if="!isEmptyConfig">
        <div class="form-actions">
          <a-button @click="saveConfig" class="save-btn" :class="{'changed': agentStore.hasConfigChanges}">
            保存配置
          </a-button>
          <!-- TODO：BUG 目前有 bug 暂时不展示 -->
          <!-- <a-button @click="resetConfig" class="reset-btn">
            重置
          </a-button> -->
        </div>
      </div>
    </div>

    <!-- 工具选择弹窗 -->
    <a-modal
      v-model:open="toolsModalOpen"
      title="选择工具"
      :width="800"
      :footer="null"
      :maskClosable="false"
      class="tools-modal"
    >
      <div class="tools-modal-content">
        <div class="tools-search">
          <a-input
            v-model:value="toolsSearchText"
            placeholder="搜索工具..."
            allow-clear
            class="search-input"
          >
            <template #prefix>
              <SearchOutlined class="search-icon" />
            </template>
          </a-input>
        </div>

        <div class="tools-list">
          <div
            v-for="tool in filteredTools"
            :key="tool.id"
            class="tool-item"
            :class="{ 'selected': selectedTools.includes(tool.id) }"
            @click="toggleToolSelection(tool.id)"
          >
            <div class="tool-content">
              <div class="tool-header">
                <span class="tool-name">{{ tool.name }}</span>
                <div class="tool-indicator">
                  <CheckCircleOutlined v-if="selectedTools.includes(tool.id)" />
                  <PlusCircleOutlined v-else />
                </div>
              </div>
              <div class="tool-description">{{ tool.description }}</div>
            </div>
          </div>
        </div>

        <div class="tools-modal-footer">
          <div class="selected-count">
            已选择 {{ selectedTools.length }} 个工具
          </div>
          <div class="modal-actions">
            <a-button @click="cancelToolsSelection">取消</a-button>
            <a-button type="primary" @click="confirmToolsSelection">确认</a-button>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import {
  SettingOutlined,
  CloseOutlined,
  CheckCircleOutlined,
  PlusCircleOutlined,
  SearchOutlined
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import ModelSelectorComponent from '@/components/ModelSelectorComponent.vue';
import { useAgentStore } from '@/stores/agent';
import { storeToRefs } from 'pinia';

// Props
const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
});

// Emits
const emit = defineEmits([
  'close'
]);

// Store 管理
const agentStore = useAgentStore();
const {
  availableTools,
  selectedAgent,
  selectedAgentId,
  agentConfig,
  configurableItems
} = storeToRefs(agentStore);

// console.log(availableTools.value)

// 本地状态
const toolsModalOpen = ref(false);
const selectedTools = ref([]);
const toolsSearchText = ref('');
const systemPromptEditMode = ref(false);


const isEmptyConfig = computed(() => {
  return !selectedAgentId.value || Object.keys(configurableItems.value).length === 0;
});

const filteredTools = computed(() => {
  const toolsList = filteredAvailableTools.value ? Object.values(filteredAvailableTools.value) : [];
  if (!toolsSearchText.value) {
    return toolsList;
  }
  const searchLower = toolsSearchText.value.toLowerCase();
  return toolsList.filter(tool =>
    tool.name.toLowerCase().includes(searchLower) ||
    tool.description.toLowerCase().includes(searchLower)
  );
});

// 方法
const closeSidebar = () => {
  emit('close');
};

const getConfigLabel = (key, value) => {
  // console.log(configurableItems)
  if (value.description && value.name !== key) {
    return `${value.name}（${key}）`;
  }
  return key;
};

const getPlaceholder = (key, value) => {
  return `（默认: ${value.default}）`;
};

const handleModelChange = (spec) => {
  if (typeof spec !== 'string' || !spec) return;
  agentStore.updateAgentConfig({
    model: spec
  });
};

// 多选相关方法
const ensureArray = (key) => {
  const config = agentConfig.value || {};
  if (!config[key] || !Array.isArray(config[key])) {
    return [];
  }
  return config[key];
};

const isOptionSelected = (key, option) => {
  const currentOptions = ensureArray(key);
  return currentOptions.includes(option);
};

const getSelectedCount = (key) => {
  const currentOptions = ensureArray(key);
  return currentOptions.length;
};

const toggleOption = (key, option) => {
  const currentOptions = [...ensureArray(key)];
  const index = currentOptions.indexOf(option);

  if (index > -1) {
    currentOptions.splice(index, 1);
  } else {
    currentOptions.push(option);
  }

  agentStore.updateAgentConfig({
    [key]: currentOptions
  });
};

const clearSelection = (key) => {
  agentStore.updateAgentConfig({
    [key]: []
  });
};

// 工具相关方法
const getToolNameById = (toolId) => {
  const toolsList = availableTools.value ? Object.values(availableTools.value) : [];
  const tool = toolsList.find(t => t.id === toolId);
  return tool ? tool.name : toolId;
};

const loadAvailableTools = async () => {
  try {
    await agentStore.fetchTools();
  } catch (error) {
    console.error('加载工具列表失败:', error);
  }
};

// 过滤掉不需要在前端显示的工具
const filteredAvailableTools = computed(() => {
  if (!availableTools.value) return {};

  const toolsToHide = [
    'calculator',
    'text_to_img_qwen',
    'mysql_list_tables',
    'mysql_describe_table',
    'mysql_query'
  ];

  const filtered = {};
  Object.keys(availableTools.value).forEach(key => {
    const tool = availableTools.value[key];
    if (!toolsToHide.includes(tool.id)) {
      filtered[key] = tool;
    }
  });

  return filtered;
});

const openToolsModal = async () => {
  try {
    await loadAvailableTools();
    selectedTools.value = [...(agentConfig.value?.tools || [])];
    toolsModalOpen.value = true;
  } catch (error) {
    console.error('打开工具选择弹窗失败:', error);
    message.error('打开工具选择弹窗失败');
  }
};

const toggleToolSelection = (toolId) => {
  const index = selectedTools.value.indexOf(toolId);
  if (index > -1) {
    selectedTools.value.splice(index, 1);
  } else {
    selectedTools.value.push(toolId);
  }
};

const removeSelectedTool = (toolId) => {
  const currentTools = [...(agentConfig.value?.tools || [])];
  const index = currentTools.indexOf(toolId);
  if (index > -1) {
    currentTools.splice(index, 1);
    agentStore.updateAgentConfig({
      tools: currentTools
    });
  }
};

const confirmToolsSelection = () => {
  agentStore.updateAgentConfig({
    tools: [...selectedTools.value]
  });
  toolsModalOpen.value = false;
  toolsSearchText.value = '';
};

const cancelToolsSelection = () => {
  toolsModalOpen.value = false;
  toolsSearchText.value = '';
  selectedTools.value = [];
};

// 系统提示词编辑相关方法
const enterEditMode = () => {
  systemPromptEditMode.value = true;
  // 使用 nextTick 确保 DOM 更新后再聚焦
  nextTick(() => {
    const textarea = document.querySelector('.system-prompt-input');
    if (textarea) {
      textarea.focus();
    }
  });
};

// 验证和过滤配置项
const validateAndFilterConfig = () => {
  const validatedConfig = { ...agentConfig.value };
  const configItems = configurableItems.value;

  // 遍历所有配置项
  Object.keys(configItems).forEach(key => {
    const configItem = configItems[key];
    const currentValue = validatedConfig[key];

    // 检查工具配置
    if (configItem.template_metadata?.kind === 'tools' && Array.isArray(currentValue)) {
      const availableToolIds = availableTools.value ? Object.values(availableTools.value).map(tool => tool.id) : [];
      validatedConfig[key] = currentValue.filter(toolId => availableToolIds.includes(toolId));

      if (validatedConfig[key].length !== currentValue.length) {
        console.warn(`工具配置 ${key} 中包含无效的工具ID，已自动过滤`);
      }
    }

    // 检查多选配置项 (type === 'list' 且有 options)
    else if (configItem.type === 'list' && configItem.options && Array.isArray(currentValue)) {
      const validOptions = configItem.options;
      validatedConfig[key] = currentValue.filter(value => validOptions.includes(value));

      if (validatedConfig[key].length !== currentValue.length) {
        console.warn(`配置项 ${key} 中包含无效的选项，已自动过滤`);
      }
    }
  });

  return validatedConfig;
};

// 配置保存和重置
const saveConfig = async () => {
  if (!selectedAgentId.value) {
    message.error('没有选择智能体');
    return;
  }

  try {
    // 验证和过滤配置
    const validatedConfig = validateAndFilterConfig();

    // 如果配置有变化，先更新到store
    if (JSON.stringify(validatedConfig) !== JSON.stringify(agentConfig.value)) {
      agentStore.updateAgentConfig(validatedConfig);
      message.info('检测到无效配置项，已自动过滤');
    }

    await agentStore.saveAgentConfig();
    message.success('配置已保存到服务器');
  } catch (error) {
    console.error('保存配置到服务器出错:', error);
    message.error('保存配置到服务器失败');
  }
};

const resetConfig = async () => {
  if (!selectedAgentId.value) {
    message.error('没有选择智能体');
    return;
  }

  try {
    agentStore.resetAgentConfig();
    message.info('配置已重置');
  } catch (error) {
    console.error('重置配置出错:', error);
    message.error('重置配置失败');
  }
};

// 监听器
watch(() => props.isOpen, (newVal) => {
  if (newVal && (!availableTools.value || Object.keys(availableTools.value).length === 0)) {
    loadAvailableTools();
  }
});
</script>

<style lang="less" scoped>

@padding-bottom: 0px;
.agent-config-sidebar {
  position: relative;
  width: 0;
  height: 100vh;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;

  &.open {
    width: 400px;
  }

  .sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(255, 255, 255, 0.02);
    flex-shrink: 0;
    min-width: 400px;

    .sidebar-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);

      .title-icon {
        color: #06b6d4;
        filter: drop-shadow(0 0 5px rgba(6, 182, 212, 0.5));
      }
    }

    .close-btn {
      color: var(--text-secondary);
      border: none;
      padding: 4px;

      &:hover {
        color: var(--text-primary);
        background: var(--bg-elevated);
      }
    }
  }

  .sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: 8px 12px;
    min-width: 400px;
    padding-bottom: @padding-bottom;

    .agent-info {
      .agent-basic-info {

        .agent-description {
          margin: 0 0 12px 0;
          font-size: 14px;
          color: var(--text-secondary);
          line-height: 1.5;
        }
      }
    }

    .sidebar-footer {
      position: sticky;
      bottom: 0px;
      padding: 12px 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(15, 23, 42, 0.8);
      backdrop-filter: blur(20px);
      z-index: 10;

      .form-actions {
        display: flex;
        gap: 12px;
        justify-content: space-between;

        .save-btn {
          flex: 1;
          background-color: var(--bg-elevated);
          border: none;
          border-radius: 6px;
          font-weight: 500;
          font-size: 14px;
          color: var(--text-primary);

          &.changed {
            background-color: var(--main-color);
            color: #fff;
          }

          &:hover {
            opacity: 0.9;
          }
        }

        .reset-btn {
          flex: 1;
          border: 1px solid var(--border-color-base);
          border-radius: 6px;
          color: var(--text-secondary);
          font-size: 14px;

          &:hover {
            border-color: var(--main-color);
            color: var(--main-color);
          }
        }
      }
    }

    .config-form-content {
      margin-bottom: 100px;
      .config-form {
        .config-alert {
          margin-bottom: 16px;
        }

        .config-item {
          margin-bottom: 20px;

          .config-description {
            margin: 4px 0 8px 0;
            font-size: 12px;
            color: var(--text-tertiary);
            line-height: 1.4;
          }

          .model-selector {
            width: 100%;
          }

          .system-prompt-input {
            resize: vertical;
            background: rgba(15, 23, 42, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 8px 12px;
            color: rgba(255, 255, 255, 0.9);

            &:focus {
              outline: none;
              border-color: #06b6d4;
              box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
            }
          }

          .system-prompt-container {
            width: 100%;
          }

          .system-prompt-display {
            min-height: 60px;
            background: rgba(15, 23, 42, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 8px 12px;
            cursor: pointer;
            position: relative;
            transition: all 0.2s ease;

            &:hover {
              border-color: rgba(6, 182, 212, 0.5);
              background: rgba(6, 182, 212, 0.05);

              .edit-hint {
                opacity: 1;
              }
            }

            .system-prompt-content {
               white-space: pre-wrap;
               word-break: break-word;
               line-height: 1.5;
               color: var(--text-primary);
               font-size: 14px;
              //  min-height: 100px;

               &.is-placeholder {
                 color: var(--text-tertiary);
                 font-style: italic;
               }

               &:empty::before {
                 content: attr(data-placeholder);
                 color: var(--text-tertiary);
               }
             }

            .edit-hint {
              position: absolute;
              top: 8px;
              right: 12px;
              font-size: 12px;
              color: var(--text-secondary);
              opacity: 0;
              transition: opacity 0.2s ease;
              background: var(--bg-elevated);
              padding: 2px 6px;
              border-radius: 4px;
            }
          }
        }
      }
    }
  }
}

// 多选卡片样式
.multi-select-cards {
  .multi-select-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .options-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 8px;
  }

  .option-card {
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    background: rgba(30, 41, 59, 0.3);
    user-select: none;

    &:hover {
      border-color: #06b6d4;
      background: rgba(6, 182, 212, 0.1);
      box-shadow: 0 0 10px rgba(6, 182, 212, 0.1);
    }

    &.selected {
      border-color: #06b6d4;
      background: rgba(6, 182, 212, 0.15);

      .option-indicator {
        color: #06b6d4;
        filter: drop-shadow(0 0 5px rgba(6, 182, 212, 0.5));
      }

      .option-text {
        color: #06b6d4;
        font-weight: 500;
      }
    }

    .option-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
    }

    .option-text {
      flex: 1;
      font-size: 14px;
      line-height: 1.4;
      word-break: break-word;
    }

    .option-indicator {
      flex-shrink: 0;
      font-size: 16px;
      transition: color 0.2s ease;
    }
  }
}

// 工具选择弹窗样式
.tools-modal {
  :deep(.ant-modal-content) {
    background: rgba(15, 23, 42, 0.9);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    overflow: hidden;
  }

  :deep(.ant-modal-header) {
    background: transparent;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding: 16px 20px;

    .ant-modal-title {
      font-size: 16px;
      font-weight: 600;
      color: #fff;
    }
  }

  :deep(.ant-modal-body) {
    padding: 20px;
    background: transparent;
  }

  .tools-modal-content {
    .tools-search {
      margin-bottom: 16px;

      .search-input {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #fff;

        &:focus {
          border-color: #06b6d4;
          box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
        }
      }
    }

    .tools-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 12px;
      max-height: 400px;
      overflow-y: auto;
      padding-right: 4px;

      .tool-item {
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px;
        cursor: pointer;
        transition: all 0.3s ease;
        background: rgba(30, 41, 59, 0.3);

        &:hover {
          border-color: #06b6d4;
          background: rgba(6, 182, 212, 0.1);
          box-shadow: 0 0 10px rgba(6, 182, 212, 0.1);
        }

        &.selected {
          border-color: #06b6d4;
          background: rgba(6, 182, 212, 0.15);

          .tool-name {
            color: #06b6d4;
          }

          .tool-indicator {
            color: #06b6d4;
            filter: drop-shadow(0 0 5px rgba(6, 182, 212, 0.5));
          }
        }

        .tool-content {
          .tool-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;

            .tool-name {
              font-weight: 600;
              color: #fff;
              font-size: 14px;
            }
          }

          .tool-description {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.5);
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }
      }
    }

    .tools-modal-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);

      .selected-count {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.6);
      }

      .modal-actions {
        display: flex;
        gap: 12px;
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .agent-config-sidebar.open {
    width: 100vw;
  }
}
</style>
