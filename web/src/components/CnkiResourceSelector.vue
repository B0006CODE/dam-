<template>
  <div class="cnki-resource-selector">
    <!-- 知识库筛选组 -->
    <div class="cnki-filter-group">
      <div class="filter-header" @click="kbCollapsed = !kbCollapsed">
        <span class="filter-title">知识库</span>
        <div class="filter-header-right">
          <BarChartOutlined class="filter-stats-icon" />
          <UpOutlined v-if="!kbCollapsed" class="collapse-icon" />
          <DownOutlined v-else class="collapse-icon" />
        </div>
      </div>
      <div class="filter-body" v-show="!kbCollapsed">
        <div class="filter-disabled-hint" v-if="!allowKbSelect">
          <InfoCircleOutlined /> 切换到"混合检索"或"知识库检索"以选择
        </div>
        <div 
          v-for="option in kbOptionsWithStats" 
          :key="option.value"
          class="filter-item"
          :class="{ 
            'disabled': !allowKbSelect, 
            'selected': selectedKbIds.includes(option.value) 
          }"
          @click="toggleKbSelection(option.value)"
        >
          <a-checkbox 
            :checked="selectedKbIds.includes(option.value)"
            :disabled="!allowKbSelect"
            @click.stop
            @change="(e) => handleKbCheckChange(option.value, e.target.checked)"
          />
          <span class="filter-label">{{ option.name }}</span>
          <span class="filter-count">({{ option.fileCount }})</span>
        </div>
        <div class="filter-empty" v-if="kbOptionsWithStats.length === 0">
          暂无可用知识库
        </div>
      </div>
    </div>

    <!-- 知识图谱筛选组 -->
    <div class="cnki-filter-group">
      <div class="filter-header" @click="graphCollapsed = !graphCollapsed">
        <span class="filter-title">知识图谱</span>
        <div class="filter-header-right">
          <BarChartOutlined class="filter-stats-icon" />
          <UpOutlined v-if="!graphCollapsed" class="collapse-icon" />
          <DownOutlined v-else class="collapse-icon" />
        </div>
      </div>
      <div class="filter-body" v-show="!graphCollapsed">
        <div class="filter-disabled-hint" v-if="!allowGraphSelect">
          <InfoCircleOutlined /> 切换到"混合检索"或"知识图谱检索"以选择
        </div>
        <div 
          v-for="option in graphOptionsWithStats" 
          :key="option.value"
          class="filter-item"
          :class="{ 
            'disabled': !allowGraphSelect, 
            'selected': selectedGraph === option.value 
          }"
          @click="selectGraphOption(option.value)"
        >
          <a-checkbox 
            :checked="selectedGraph === option.value"
            :disabled="!allowGraphSelect"
            @click.stop
            @change="() => selectGraphOption(option.value)"
          />
          <span class="filter-label">{{ option.name }}</span>
          <span class="filter-count" v-if="option.entityCount !== undefined">
            ({{ formatCount(option.entityCount) }})
          </span>
          <a-tooltip v-if="option.isTruncated" title="数据量较大，统计可能不完全准确">
            <ExclamationCircleOutlined class="truncated-warning" />
          </a-tooltip>
        </div>
        <div class="filter-empty" v-if="graphOptionsWithStats.length === 0">
          暂无可用知识图谱
        </div>
      </div>
    </div>

    <!-- 当前选择摘要 -->
    <div class="selection-summary">
      <div class="summary-row">
        <span class="summary-label">检索模式:</span>
        <span class="summary-value mode-tag">{{ retrievalModeLabel }}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">知识库:</span>
        <span class="summary-value">{{ kbSummary }}</span>
      </div>
      <div class="summary-row">
        <span class="summary-label">图谱:</span>
        <span class="summary-value">{{ graphSummary }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { 
  BarChartOutlined, 
  UpOutlined, 
  DownOutlined, 
  InfoCircleOutlined,
  ExclamationCircleOutlined 
} from '@ant-design/icons-vue';
import { databaseApi } from '@/apis/knowledge_api';
import { lightragApi } from '@/apis/graph_api';

// Props
const props = defineProps({
  retrievalMode: {
    type: String,
    default: 'mix'
  },
  modelValue: {
    type: Object,
    default: () => ({ kbIds: [], graph: 'neo4j' })
  }
});

// Emits
const emit = defineEmits(['update:modelValue']);

// 折叠状态
const kbCollapsed = ref(false);
const graphCollapsed = ref(false);

// 数据
const kbOptionsRaw = ref([]);
const graphOptionsRaw = ref([]);
const graphStats = ref({});

// 选择状态 - 从 modelValue 同步
const selectedKbIds = computed({
  get: () => props.modelValue.kbIds || [],
  set: (val) => emit('update:modelValue', { ...props.modelValue, kbIds: val })
});

const selectedGraph = computed({
  get: () => props.modelValue.graph || 'neo4j',
  set: (val) => emit('update:modelValue', { ...props.modelValue, graph: val })
});

// 是否允许选择
const allowKbSelect = computed(() => ['mix', 'local'].includes(props.retrievalMode));
const allowGraphSelect = computed(() => ['mix', 'global'].includes(props.retrievalMode));

// 带统计信息的知识库选项
const kbOptionsWithStats = computed(() => {
  return kbOptionsRaw.value.map(db => ({
    value: db.db_id,
    name: db.name || db.db_id,
    fileCount: db.files ? Object.keys(db.files).length : 0,
    kb_type: db.kb_type
  }));
});

// 读取图谱别名（与GraphView保持一致）
const loadGraphAliases = () => {
  try {
    const raw = localStorage.getItem('graph_aliases');
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
};
const graphAliases = ref(loadGraphAliases());

// 带统计信息的图谱选项
const graphOptionsWithStats = computed(() => {
  return graphOptionsRaw.value.map(db => {
    const stats = graphStats.value[db.db_id];
    const alias = graphAliases.value[db.db_id];
    return {
      value: db.db_id,
      name: alias || db.name || db.db_id,
      entityCount: stats?.total_nodes,
      relationCount: stats?.total_edges,
      isTruncated: stats?.is_truncated || false
    };
  });
});


// 格式化数量显示
const formatCount = (count) => {
  if (count === undefined || count === null) return '?';
  if (count >= 10000) {
    return (count / 10000).toFixed(2) + '万';
  }
  return count.toString();
};

// 检索模式标签
const retrievalModeLabels = {
  mix: '混合检索',
  local: '知识库检索',
  global: '知识图谱检索',
  llm: '大模型检索'
};
const retrievalModeLabel = computed(() => retrievalModeLabels[props.retrievalMode] || '检索模式');

// 摘要信息
const kbSummary = computed(() => {
  if (!allowKbSelect.value) return '由模式决定';
  if (!selectedKbIds.value.length) return '全部知识库';
  const labels = kbOptionsWithStats.value
    .filter(opt => selectedKbIds.value.includes(opt.value))
    .map(opt => opt.name);
  const preview = labels.slice(0, 2).join('、');
  return labels.length > 2 ? `${preview} 等${labels.length}个` : preview || '全部知识库';
});

const graphSummary = computed(() => {
  if (!allowGraphSelect.value) return '由模式决定';
  const found = graphOptionsWithStats.value.find(g => g.value === selectedGraph.value);
  return found?.name || '未选择图谱';
});

// 切换知识库选择
const toggleKbSelection = (value) => {
  if (!allowKbSelect.value) return;
  const current = [...selectedKbIds.value];
  const index = current.indexOf(value);
  if (index > -1) {
    current.splice(index, 1);
  } else {
    current.push(value);
  }
  selectedKbIds.value = current;
};

const handleKbCheckChange = (value, checked) => {
  if (!allowKbSelect.value) return;
  const current = [...selectedKbIds.value];
  const index = current.indexOf(value);
  if (checked && index === -1) {
    current.push(value);
  } else if (!checked && index > -1) {
    current.splice(index, 1);
  }
  selectedKbIds.value = current;
};

// 选择图谱
const selectGraphOption = (value) => {
  if (!allowGraphSelect.value) return;
  selectedGraph.value = value;
};

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const res = await databaseApi.getDatabases();
    kbOptionsRaw.value = res?.databases || [];
  } catch (error) {
    console.error('加载知识库列表失败:', error);
    kbOptionsRaw.value = [];
  }
};

// 加载知识图谱列表和统计信息
const loadGraphOptions = async () => {
  try {
    // 获取 LightRAG 数据库列表
    const res = await lightragApi.getDatabases();
    graphOptionsRaw.value = res?.data?.databases || res?.databases || [];
    
    // 为每个图谱获取统计信息
    for (const db of graphOptionsRaw.value) {
      try {
        const stats = await lightragApi.getStats(db.db_id);
        if (stats?.data) {
          graphStats.value[db.db_id] = stats.data;
        }
      } catch (e) {
        console.warn(`获取图谱 ${db.db_id} 统计信息失败:`, e);
      }
    }
  } catch (error) {
    console.error('加载知识图谱列表失败:', error);
    graphOptionsRaw.value = [];
  }
};

// 初始化
onMounted(() => {
  loadKnowledgeBases();
  loadGraphOptions();
});

// 监听检索模式变化
watch(() => props.retrievalMode, (newMode) => {
  if (!allowKbSelect.value) {
    selectedKbIds.value = [];
  }
  if (!allowGraphSelect.value) {
    // 不清空图谱选择，保持上次选择
  } else if (!selectedGraph.value && graphOptionsWithStats.value.length > 0) {
    selectedGraph.value = graphOptionsWithStats.value[0].value;
  }
});
</script>

<style lang="less" scoped>
.cnki-resource-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cnki-filter-group {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
  
  .filter-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #fafafa;
    cursor: pointer;
    user-select: none;
    border-bottom: 1px solid #f0f0f0;
    
    &:hover {
      background: #f5f5f5;
    }
    
    .filter-title {
      font-weight: 600;
      color: #1a1a1a;
      font-size: 14px;
    }
    
    .filter-header-right {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .filter-stats-icon {
        color: #1890ff;
        font-size: 14px;
      }
      
      .collapse-icon {
        color: #999;
        font-size: 12px;
        transition: transform 0.2s;
      }
    }
  }
  
  .filter-body {
    padding: 8px 0;
    max-height: 280px;
    overflow-y: auto;
    
    .filter-disabled-hint {
      padding: 8px 16px;
      color: #999;
      font-size: 12px;
      background: #fffbe6;
      border-bottom: 1px solid #fff1b8;
      display: flex;
      align-items: center;
      gap: 6px;
      
      .anticon {
        color: #faad14;
      }
    }
    
    .filter-item {
      display: flex;
      align-items: center;
      padding: 8px 16px;
      cursor: pointer;
      transition: background 0.15s;
      
      &:hover:not(.disabled) {
        background: #f0f7ff;
      }
      
      &.disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      &.selected {
        background: #e6f4ff;
      }
      
      .filter-label {
        flex: 1;
        margin-left: 8px;
        color: #1890ff;
        font-size: 14px;
        
        &:hover {
          text-decoration: underline;
        }
      }
      
      .filter-count {
        color: #999;
        font-size: 13px;
        margin-left: 4px;
      }
      
      .truncated-warning {
        color: #faad14;
        margin-left: 4px;
        font-size: 12px;
      }
    }
    
    .filter-empty {
      padding: 16px;
      text-align: center;
      color: #999;
      font-size: 13px;
    }
  }
}

.selection-summary {
  background: #f6f8fa;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  padding: 12px 16px;
  
  .summary-row {
    display: flex;
    align-items: center;
    margin-bottom: 6px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .summary-label {
      color: #666;
      font-size: 12px;
      min-width: 70px;
    }
    
    .summary-value {
      color: #333;
      font-size: 13px;
      
      &.mode-tag {
        background: #e6f4ff;
        color: #1890ff;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
      }
    }
  }
}
</style>
