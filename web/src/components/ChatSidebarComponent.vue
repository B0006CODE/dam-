<template>
  <div class="chat-sidebar" :class="{'sidebar-open': isSidebarOpen, 'no-transition': isInitialRender}">
    <div class="sidebar-content">
      <div class="sidebar-header">
        <div class="header-title" v-if="singleMode">{{ selectedAgentName }}</div>
        <div
          v-else
          class="agent-selector"
          @click="openAgentModal"
        >
          <span class="agent-name">{{ selectedAgentName || '选择智能体' }}</span>
          <ChevronDown size="16" class="switch-icon" />
        </div>
        <div class="header-actions">
          <div class="toggle-sidebar nav-btn" v-if="isSidebarOpen" @click="toggleCollapse">
            <PanelLeftClose size="20" color="var(--gray-800)"/>
          </div>
        </div>
      </div>

      <!-- 批量操作工具栏 -->
      <div v-if="isBatchMode" class="batch-toolbar">
        <div class="batch-info">
          <a-checkbox
            v-model:checked="isAllSelected"
            @change="toggleSelectAll"
            class="select-all-checkbox"
          >
            <span>已选择 {{ selectedChats.size }} 个对话</span>
          </a-checkbox>
          <a-button size="small" @click="exitBatchMode" class="cancel-btn">取消</a-button>
        </div>
        <div class="batch-actions">
          <a-button size="small" type="primary" danger @click="batchDeleteSelected" :disabled="selectedChats.size === 0" class="delete-btn">
            删除选中
          </a-button>
          <a-dropdown :trigger="['click']">
            <a-button size="small" class="more-actions-btn">
              更多操作 <DownOutlined />
            </a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item key="select-all" @click="selectAllChats">
                  <CheckSquareOutlined /> 全选
                </a-menu-item>
                <a-menu-item key="clear-selection" @click="clearSelection">
                  <ClearOutlined /> 清空选择
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="delete-today" @click="deleteChatsByDays(1)">
                  <CalendarOutlined /> 删除今天对话
                </a-menu-item>
                <a-menu-item key="delete-week" @click="deleteChatsByDays(7)">
                  <CalendarOutlined /> 删除本周对话
                </a-menu-item>
                <a-menu-item key="delete-month" @click="deleteChatsByDays(30)">
                  <CalendarOutlined /> 删除本月对话
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="clear-all" @click="clearAllConversations" danger>
                  <DeleteOutlined /> 清空所有对话
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </div>

      <div class="conversation-list-top">
        <button type="text" @click="createNewChat" class="new-chat-btn" v-if="!isBatchMode">
          <MessageSquarePlus size="20" /> 创建新对话
        </button>
        <div class="batch-mode-header" v-else>
          <a-button size="small" @click="exitBatchMode">
            <LeftOutlined /> 返回正常模式
          </a-button>
        </div>
        <div class="conversation-actions-header">
          <a-button
            size="small"
            @click="enterBatchMode"
            v-if="!isBatchMode && Object.keys(groupedChats).length > 0"
            class="batch-mode-btn"
          >
            <CheckSquareOutlined /> 批量操作
          </a-button>
        </div>
      </div>
      <div class="conversation-list">
        <template v-if="Object.keys(groupedChats).length > 0">
          <div v-for="(group, groupName) in groupedChats" :key="groupName" class="chat-group">
            <div class="chat-group-title">{{ groupName }}</div>
            <div
              v-for="chat in group"
              :key="chat.id"
              class="conversation-item"
              :class="{
                'active': currentChatId === chat.id,
                'batch-mode': isBatchMode,
                'selected': selectedChats.has(chat.id)
              }"
              @click="handleItemClick(chat)"
            >
              <!-- 批量选择模式的复选框 -->
              <a-checkbox
                v-if="isBatchMode"
                :checked="selectedChats.has(chat.id)"
                @change="toggleChatSelection(chat.id)"
                class="chat-checkbox"
                @click.stop
              />
              <div class="conversation-title">{{ chat.title || '新的对话' }}</div>
              <div class="actions-mask"></div>
              <div class="conversation-actions" v-if="!isBatchMode">
                <a-dropdown :trigger="['click']" @click.stop>
                  <template #overlay>
                    <a-menu>
                      <a-menu-item key="rename" @click.stop="renameChat(chat.id)">
                        <EditOutlined /> 重命名
                      </a-menu-item>
                      <a-menu-item key="delete" @click.stop="deleteChat(chat.id)" v-if="chat.id !== currentChatId">
                        <DeleteOutlined /> 删除
                      </a-menu-item>
                    </a-menu>
                  </template>
                  <a-button type="text" class="more-btn" @click.stop>
                    <MoreOutlined />
                  </a-button>
                </a-dropdown>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="empty-list">
          暂无对话历史
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, h, ref, watch } from 'vue';
import {
  DeleteOutlined,
  EditOutlined,
  MoreOutlined,
  CheckSquareOutlined,
  ClearOutlined,
  CalendarOutlined,
  DownOutlined,
  LeftOutlined
} from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { PanelLeftClose, MessageSquarePlus, ChevronDown } from 'lucide-vue-next';
import { threadApi } from '@/apis/agent_api';
import dayjs, { parseToShanghai } from '@/utils/time';

const props = defineProps({
  currentAgentId: {
    type: String,
    default: null
  },
  currentChatId: {
    type: String,
    default: null
  },
  chatsList: {
    type: Array,
    default: () => []
  },
  isSidebarOpen: {
    type: Boolean,
    default: false
  },
  isInitialRender: {
    type: Boolean,
    default: false
  },
  singleMode: {
    type: Boolean,
    default: true
  },
  agents: {
    type: Object,
    default: () => ({})
  },
  selectedAgentId: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['create-chat', 'select-chat', 'delete-chat', 'rename-chat', 'toggle-sidebar', 'open-agent-modal']);

// 批量操作状态
const isBatchMode = ref(false);
const selectedChats = ref(new Set());
const isAllSelected = ref(false);

const selectedAgentName = computed(() => {
  if (props.selectedAgentId && props.agents && props.agents[props.selectedAgentId]) {
    return props.agents[props.selectedAgentId].name;
  }
  return '';
});

const groupedChats = computed(() => {
  const groups = {
    '今天': [],
    '七天内': [],
    '三十天内': [],
  };

  // 确保使用北京时间进行比较
  const now = dayjs().tz('Asia/Shanghai');
  const today = now.startOf('day');
  const sevenDaysAgo = now.subtract(7, 'day').startOf('day');
  const thirtyDaysAgo = now.subtract(30, 'day').startOf('day');

  // Sort chats by creation date, newest first
  const sortedChats = [...props.chatsList].sort((a, b) => {
    const dateA = parseToShanghai(b.created_at);
    const dateB = parseToShanghai(a.created_at);
    if (!dateA || !dateB) return 0;
    return dateA.diff(dateB);
  });

  sortedChats.forEach(chat => {
    // 将后端时间当作UTC时间处理，然后转换为北京时间
    const chatDate = parseToShanghai(chat.created_at);
    if (!chatDate) {
      return;
    }
    if (chatDate.isAfter(today)) {
      groups['今天'].push(chat);
    } else if (chatDate.isAfter(sevenDaysAgo)) {
      groups['七天内'].push(chat);
    } else if (chatDate.isAfter(thirtyDaysAgo)) {
      groups['三十天内'].push(chat);
    } else {
      const monthKey = chatDate.format('YYYY-MM');
      if (!groups[monthKey]) {
        groups[monthKey] = [];
      }
      groups[monthKey].push(chat);
    }
  });

  // Remove empty groups
  for (const key in groups) {
    if (groups[key].length === 0) {
      delete groups[key];
    }
  }

  return groups;
});

// 监听选中的聊天变化，更新全选状态
watch(selectedChats, (newSelected) => {
  const totalChats = props.chatsList.length;
  isAllSelected.value = totalChats > 0 && newSelected.size === totalChats;
});

// 监听对话列表变化，更新全选状态
watch(() => props.chatsList, () => {
  const totalChats = props.chatsList.length;
  isAllSelected.value = totalChats > 0 && selectedChats.value.size === totalChats;
});

// 批量操作方法
const enterBatchMode = () => {
  isBatchMode.value = true;
  clearSelection();
};

const exitBatchMode = () => {
  isBatchMode.value = false;
  clearSelection();
};

const handleItemClick = (chat) => {
  if (isBatchMode.value) {
    // 批量模式下，点击切换选择状态
    toggleChatSelection(chat.id);
  } else {
    // 正常模式下，选择聊天
    selectChat(chat);
  }
};

const selectAllChats = () => {
  const allChatIds = props.chatsList.map(chat => chat.id);
  selectedChats.value = new Set(allChatIds);
  isAllSelected.value = true;
  // 确保响应式更新
  selectedChats.value = new Set(selectedChats.value);
};

const clearSelection = () => {
  selectedChats.value.clear();
  isAllSelected.value = false;
  // 确保响应式更新
  selectedChats.value = new Set(selectedChats.value);
};

const toggleChatSelection = (chatId) => {
  if (selectedChats.value.has(chatId)) {
    selectedChats.value.delete(chatId);
  } else {
    selectedChats.value.add(chatId);
  }
  // 确保响应式更新
  selectedChats.value = new Set(selectedChats.value);
};

const toggleSelectAll = (checked) => {
  isAllSelected.value = checked;
  if (checked) {
    selectAllChats();
  } else {
    clearSelection();
  }
};

const batchDeleteSelected = async () => {
  if (selectedChats.value.size === 0) {
    message.warning('请先选择要删除的对话');
    return;
  }

  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedChats.value.size} 个对话吗？此操作不可恢复。`,
    okText: '确认删除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        const results = await threadApi.batchDeleteThreads(Array.from(selectedChats.value));

        if (results.deleted_count > 0) {
          message.success(`成功删除 ${results.deleted_count} 个对话`);
        }

        if (results.failed_count > 0) {
          message.warning(`有 ${results.failed_count} 个对话删除失败`);
        }

        emit('delete-chat', null); // 通知父组件重新加载
        // 不立即退出批量模式，让用户看到操作结果
        setTimeout(() => {
          exitBatchMode();
        }, 1000);
      } catch (error) {
        message.error('批量删除失败');
        console.error('批量删除失败:', error);
      }
    },
    onCancel: () => {
      // 用户取消删除，不做任何操作
    }
  });
};

const deleteChatsByDays = async (days) => {
  const dayText = days === 1 ? '今天' : days === 7 ? '本周' : '本月';

  Modal.confirm({
    title: `删除${dayText}对话确认`,
    content: `确定要删除${dayText}的所有对话吗？此操作不可恢复。`,
    okText: '确认删除',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        const results = await threadApi.deleteThreadsByCondition({ days });

        if (results.deleted_count > 0) {
          message.success(`成功删除 ${results.deleted_count} 个${dayText}对话`);
        } else {
          message.info(`${dayText}没有对话需要删除`);
        }

        emit('delete-chat', null);
      } catch (error) {
        message.error(`删除${dayText}对话失败`);
        console.error(`删除${dayText}对话失败:`, error);
      }
    },
    onCancel: () => {
      // 用户取消删除，不做任何操作
    }
  });
};

const clearAllConversations = async () => {
  Modal.confirm({
    title: '清空所有对话确认',
    content: '确定要清空所有对话吗？此操作不可恢复，请谨慎操作。',
    okText: '确认清空',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      try {
        const results = await threadApi.clearAllConversations();

        if (results.deleted_count > 0) {
          message.success(`成功清空 ${results.deleted_count} 个对话`);
        } else {
          message.info('没有对话需要清空');
        }

        emit('delete-chat', null);
      } catch (error) {
        message.error('清空对话失败');
        console.error('清空对话失败:', error);
      }
    },
    onCancel: () => {
      // 用户取消删除，不做任何操作
    }
  });
};

const createNewChat = () => {
  emit('create-chat');
};

const selectChat = (chat) => {
  emit('select-chat', chat.id);
};

const deleteChat = (chatId) => {
  emit('delete-chat', chatId);
};

const renameChat = async (chatId) => {
  try {
    const chat = props.chatsList.find(c => c.id === chatId);
    if (!chat) return;

    let newTitle = chat.title;
    Modal.confirm({
      title: '重命名对话',
      content: h('div', { style: { marginTop: '12px' } }, [
        h('input', {
          value: newTitle,
          style: { width: '100%', padding: '4px 8px', border: '1px solid #d9d9d9', borderRadius: '4px' },
          onInput: (e) => { newTitle = e.target.value; }
        })
      ]),
      okText: '确认',
      cancelText: '取消',
      onOk: () => {
        if (!newTitle.trim()) {
          message.warning('标题不能为空');
          return Promise.reject();
        }
        emit('rename-chat', { chatId, title: newTitle });
      },
      onCancel: () => {}
    });
  } catch (error) {
    console.error('重命名对话失败:', error);
  }
};

const toggleCollapse = () => {
  emit('toggle-sidebar');
};

const openAgentModal = () => {
  emit('open-agent-modal');
};
</script>

<style lang="less" scoped>
.chat-sidebar {
  width: 0;
  height: 100%;
  background-color: var(--bg-sider);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border: none;
  overflow: hidden;

  .sidebar-content {
    // 保持内部宽度，避免折叠时压缩
    width: 280px;
    min-width: 280px;
    height: 100%;
    display: flex;
    flex-direction: column;
    opacity: 1;
    transform: translateX(0);
    transition: opacity 0.2s ease, transform 0.3s ease;
  }

  &:not(.sidebar-open) .sidebar-content {
    opacity: 0;
    transform: translateX(-12px);
  }

  &.floating-sidebar .sidebar-content {
    width: 100%;
    min-width: 0;
    max-width: 300px;
  }

  &.no-transition {
    transition: none !important;
  }

  &.sidebar-open {
    width: 280px;
    max-width: 300px;
    border-right: 1px solid var(--gray-200);
  }

  .sidebar-header {
    height: var(--header-height);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    border-bottom: 1px solid var(--gray-50);
    flex-shrink: 0;

    .header-title {
      font-weight: 500;
      font-size: 16px;
      color: var(--gray-900);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      // color: var(--gray-600);
    }
  }

  .conversation-list-top {
    padding: 8px 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;

    .new-chat-btn {
      width: 100%;
      padding: 8px 12px;
      border-radius: 6px;
      background-color: var(--gray-50);
      color: var(--main-color);
      border: none;
      transition: all 0.2s ease;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;

      &:hover {
        background-color: var(--gray-100);
      }
    }

    .batch-mode-header {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .conversation-actions-header {
      display: flex;
      align-items: center;
      justify-content: center;

      .batch-mode-btn {
        width: 100%;
        padding: 6px 12px;
        border-radius: 6px;
        background-color: var(--main-color);
        color: white;
        border: none;
        transition: all 0.2s ease;
        font-weight: 500;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        font-size: 13px;

        &:hover {
          background-color: var(--main-600);
        }
      }
    }
  }

  // 批量操作工具栏样式
  .batch-toolbar {
    padding: 12px;
    background-color: var(--gray-25);
    border-bottom: 1px solid var(--gray-200);
    border-radius: 8px;
    margin: 8px 12px;

    .batch-info {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;

      .select-all-checkbox {
        flex: 1;

        span {
          font-size: 13px;
          color: var(--gray-700);
        }
      }

      .cancel-btn {
        font-size: 12px;
        padding: 4px 8px;
      }
    }

    .batch-actions {
      display: flex;
      gap: 8px;
      align-items: center;

      .delete-btn {
        background-color: #ff4d4f;
        border-color: #ff4d4f;
        font-size: 12px;
        padding: 4px 12px;

        &:hover {
          background-color: #ff7875;
          border-color: #ff7875;
        }
      }

      .more-actions-btn {
        font-size: 12px;
        padding: 4px 8px;
      }
    }
  }

  .conversation-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;

    .chat-group {
      margin-bottom: 16px;
    }

    .chat-group-title {
      padding: 4px 8px;
      font-size: 12px;
      color: var(--gray-500);
      font-weight: 500;
      text-transform: uppercase;
    }

    .conversation-item {
      display: flex;
      align-items: center;
      padding: 8px 12px;
      border-radius: 6px;
      margin: 4px 0;
      cursor: pointer;
      transition: background-color 0.2s ease;
      position: relative;
      overflow: hidden;

      // 批量选择模式样式
      &.batch-mode {
        padding-left: 8px;

        .chat-checkbox {
          margin-right: 8px;
          flex-shrink: 0;

          :deep(.ant-checkbox) {
            .ant-checkbox-inner {
              border-color: var(--gray-400);

              &:hover {
                border-color: var(--main-color);
              }
            }

            &.ant-checkbox-checked .ant-checkbox-inner {
              background-color: var(--main-color);
              border-color: var(--main-color);
            }
          }
        }
      }

      // 选中状态样式
      &.selected {
        background-color: var(--main-50);
        border: 1px solid var(--main-200);

        .conversation-title {
          color: var(--main-700);
          font-weight: 500;
        }
      }

      .conversation-title {
        flex: 1;
        font-size: 14px;
        color: var(--gray-800);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        transition: color 0.2s ease;
      }

      .actions-mask {
        position: absolute;
        right: 0;
        top: 0;
        bottom: 0;
        width: 60px;
        background: linear-gradient(to right, transparent, var(--bg-sider) 20px);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
      }

      .conversation-actions {
        display: flex;
        align-items: center;
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        opacity: 0;
        transition: opacity 0.3s ease;

        .more-btn {
          color: var(--gray-600);
          background-color: transparent !important;
          &:hover {
            color: var(--main-500);
            background-color: transparent !important;
          }
        }
      }

      &:hover {
        background-color: var(--gray-25);

        .actions-mask {
            background: linear-gradient(to right, transparent, var(--gray-25) 20px);
        }

        .actions-mask, .conversation-actions {
          opacity: 1;
        }
      }

      &.active {
        background-color: var(--gray-50);

        .conversation-title {
          color: var(--main-600);
          font-weight: 500;
        }
        .actions-mask {
          background: linear-gradient(to right, transparent, var(--gray-50) 20px);
        }
      }
    }

    .empty-list {
      text-align: center;
      margin-top: 20px;
      color: var(--gray-500);
      font-size: 14px;
    }
  }
}

// Scrollbar styling
.conversation-list::-webkit-scrollbar {
  width: 5px;
}
.conversation-list::-webkit-scrollbar-track {
  background: transparent;
}
.conversation-list::-webkit-scrollbar-thumb {
  background: var(--gray-300);
  border-radius: 5px;
}
.conversation-list::-webkit-scrollbar-thumb:hover {
  background: var(--gray-400);
}

.toggle-sidebar.nav-btn {
  cursor: pointer;
  height: 2.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  // padding: 0.5rem;
  transition: background-color 0.3s;

  svg {
    stroke: var(--gray-600);
  }

  &:hover svg {
    stroke: var(--main-color);
  }
}

// 智能体选择器样式
.agent-selector {
  cursor: pointer;
  font-size: 15px;
  color: var(--gray-900);
  transition: color 0.2s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;

  .agent-name {
    transition: color 0.2s ease;
  }

  .switch-icon {
    color: var(--gray-500);
    transition: all 0.2s ease;
  }

  &:hover {
    .agent-name {
      color: var(--main-500);
    }
    .switch-icon {
      color: var(--main-500);
      transform: translateY(1px);
    }
  }
}
</style>
