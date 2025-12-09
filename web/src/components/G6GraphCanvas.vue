<template>
  <div class="g6-graph-container" ref="rootEl">
    <div class="g6-canvas" ref="container"></div>
    <div class="slots">
      <div v-if="$slots.top" class="overlay top">
        <slot name="top" />
      </div>
      <div class="content">
        <slot name="content" />
      </div>
      <div v-if="$slots.bottom" class="overlay bottom">
        <slot name="bottom" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue';
import { Graph } from '@antv/g6';
import { buildNodeColorMap, filterByDimensions } from '@/utils/nodeColorMapper';

const props = defineProps({
  graphData: { type: Object, required: true, default: () => ({ nodes: [], edges: [] }) },
  labelField: { type: String, default: 'name' },
  autoFit: { type: Boolean, default: true },
  autoResize: { type: Boolean, default: true },
  layoutOptions: { type: Object, default: () => ({}) },
  nodeStyleOptions: { type: Object, default: () => ({}) },
  edgeStyleOptions: { type: Object, default: () => ({}) },
  enableFocusNeighbor: { type: Boolean, default: true },
  sizeByDegree: { type: Boolean, default: true },
  highlightKeywords: { type: Array, default: () => [] },
  hiddenDimensions: { type: Array, default: () => [] }
});

const emit = defineEmits(['ready', 'node-click', 'edge-click', 'canvas-click', 'data-rendered']);

const container = ref(null);
const rootEl = ref(null);
let graphInstance = null;
let initTimer = null;

const layoutType = computed(() => props.layoutOptions.type || 'force');
const normalizedKeywords = computed(() =>
  (props.highlightKeywords || [])
    .filter(Boolean)
    .map((kw) => String(kw).toLowerCase())
);

const textMeasureCtx = (() => {
  if (typeof document === 'undefined') return null;
  const canvas = document.createElement('canvas');
  return canvas.getContext('2d');
})();

const measureTextWidth = (text, font) => {
  if (!textMeasureCtx) return text.length * 12;
  textMeasureCtx.font = font;
  return textMeasureCtx.measureText(text || '').width;
};

const wrapText = (text, maxWidth, font) => {
  if (!text) return [''];
  if (!textMeasureCtx) return [text];

  textMeasureCtx.font = font;
  const lines = [];
  let current = '';

  for (const ch of text) {
    const tentative = current + ch;
    if (textMeasureCtx.measureText(tentative).width <= maxWidth || !current) {
      current = tentative;
    } else {
      lines.push(current);
      current = ch;
    }
  }
  if (current) lines.push(current);
  return lines;
};

// 自适应尺寸与包裹的边界参数
const MIN_NODE_SIZE = 52;
const MAX_NODE_SIZE = 240;
const WRAP_MIN_WIDTH = 32;
const WRAP_MAX_WIDTH = 260;
const TEXT_PADDING = 14;
const FONT_SIZE_MAX = 14;
const FONT_SIZE_MIN = 11;

const getLayoutConfig = () => {
  if (layoutType.value === 'circular') {
    return {
      type: 'circular',
      startAngle: 0,
      endAngle: Math.PI * 2,
      radius: null,
      animation: false
    };
  }

  return {
    type: 'force',
    linkDistance: 180,
    nodeStrength: 800,
    edgeStrength: 80,
    preventOverlap: true,
    nodeSize: (d) => d?.size || 32,
    damping: 0.9,
    maxSpeed: 80,
    gravity: 25,
    factor: 1,
    interval: 0.02,
    animation: false
  };
};

const buildGraphData = () => {
  const { nodes = [], edges = [] } = filterByDimensions(
    props.graphData.nodes || [],
    props.graphData.edges || [],
    props.hiddenDimensions
  );

  const colorMap = buildNodeColorMap(nodes, edges);
  const degrees = new Map();
  nodes.forEach((n) => degrees.set(String(n.id), 0));
  edges.forEach((e) => {
    const s = String(e.source_id);
    const t = String(e.target_id);
    degrees.set(s, (degrees.get(s) || 0) + 1);
    degrees.set(t, (degrees.get(t) || 0) + 1);
  });

  const keywordSet = normalizedKeywords.value;
  const matchedNodes = new Set();

  const normalizeLabel = (node) => {
    const label =
      node?.[props.labelField] ||
      node?.name ||
      node?.id ||
      node?.label ||
      '';
    return String(label);
  };

  const nodeData = nodes.map((node) => {
    const id = String(node.id);
    const label = normalizeLabel(node);
    const isMatched =
      keywordSet.length > 0 &&
      keywordSet.some((kw) => label.toLowerCase().includes(kw));

    if (isMatched) matchedNodes.add(id);

    const degree = degrees.get(id) || 0;

    // 文本驱动的自适应尺寸，必要时缩小字体以适配最大直径
    const computeLayout = (diameter, fontSize, degreeBase) => {
      const wrapWidth = Math.max(WRAP_MIN_WIDTH, Math.min(WRAP_MAX_WIDTH, diameter * 0.72));
      const fontSpec = `700 ${fontSize}px Microsoft YaHei, sans-serif`;
      const lines = wrapText(label, wrapWidth, fontSpec);
      const maxLineWidth = Math.max(...lines.map((l) => measureTextWidth(l, fontSpec)), fontSize);
      const textHeight = lines.length * (fontSize + 4);
      const neededByWidth = maxLineWidth / 0.72 + TEXT_PADDING;
      const neededByHeight = textHeight / 0.72 + TEXT_PADDING;
      const requiredDiameter = Math.max(degreeBase, neededByWidth, neededByHeight);
      return { wrapWidth, lines, requiredDiameter, fontSize };
    };

    let fontSize = FONT_SIZE_MAX;
    let degreeBase = props.sizeByDegree ? Math.min(48 + degree * 1.2, 110) : 60;
    let layout = computeLayout(Math.max(degreeBase, MIN_NODE_SIZE), fontSize, degreeBase);
    if (layout.requiredDiameter > degreeBase + 1) {
      layout = computeLayout(layout.requiredDiameter, fontSize, degreeBase);
    }
    // 如果仍超出最大直径，逐步缩小字体重算，直到适配或到达最小字号
    while (layout.requiredDiameter > MAX_NODE_SIZE && fontSize > FONT_SIZE_MIN) {
      fontSize -= 1;
      degreeBase = props.sizeByDegree ? Math.min(48 + degree * 1.2, 110) : 60;
      layout = computeLayout(Math.max(degreeBase, MIN_NODE_SIZE), fontSize, degreeBase);
      if (layout.requiredDiameter > degreeBase + 1) {
        layout = computeLayout(layout.requiredDiameter, fontSize, degreeBase);
      }
    }

    const wrappedLabel = layout.lines.join('\n');
    const nodeSize = Math.max(MIN_NODE_SIZE, Math.min(MAX_NODE_SIZE, layout.requiredDiameter));
    const colorInfo = colorMap.get(id) || { color: '#3b82f6', dimension: 'default' };
    const muted = keywordSet.length > 0 && !isMatched;

    return {
      id,
      data: node,
      size: nodeSize,
      style: {
        size: nodeSize,
        r: nodeSize / 2,
        fill: colorInfo.color,
        stroke: isMatched ? '#e0ecff' : '#c2d7ff',
        lineWidth: isMatched ? 2 : 1.3,
        shadowColor: 'rgba(0, 0, 0, 0.18)',
        shadowBlur: 10,
        shadowOffsetY: 3,
        opacity: muted ? 0.2 : 1,
        labelText: wrappedLabel,
        labelPlacement: 'center',
        labelTextAlign: 'center',
        labelFill: '#ffffff',
        labelFontSize: fontSize,
        labelFontWeight: 700,
        labelFontFamily: 'Microsoft YaHei, sans-serif',
        labelIsBillboard: false, // 随缩放缩放，避免缩小时文字溢出
        labelWordWrap: true,
        labelWordWrapWidth: layout.wrapWidth,
        labelMaxWidth: layout.wrapWidth,
        labelMaxLines: Math.max(layout.lines.length, 1),
        labelTextOverflow: 'clip',
        labelLineHeight: fontSize + 4,
        labelPadding: 4,
        labelBackground: false,
        ...props.nodeStyleOptions
      }
    };
  });

  const edgeData = edges
    .map((edge, idx) => {
      const sourceId = String(edge.source_id);
      const targetId = String(edge.target_id);
      if (!degrees.has(sourceId) || !degrees.has(targetId)) return null;

      const connectsHighlight =
        keywordSet.length === 0 ||
        matchedNodes.has(sourceId) ||
        matchedNodes.has(targetId);

      // 选择优先使用中文的关系文案，避免中英叠加
      const rawLabel =
        edge.r || edge.relation || edge.label || edge.name || edge.type || '';
      // 仅保留中文，彻底避免中英叠加
      const chineseOnly = (rawLabel.match(/[\u4e00-\u9fa5]+/g) || []).join('');
      const labelText = chineseOnly || '';

      return {
        id: edge.id ? String(edge.id) : `e-${idx}-${sourceId}-${targetId}`,
        source: sourceId,
        target: targetId,
        data: edge,
        style: {
          stroke: '#ffffff',
          opacity: connectsHighlight ? 0.95 : 0.25,
          lineWidth: connectsHighlight ? 1.4 : 1,
          endArrow: true,
          arrowSize: 8,
          labelText,
          labelPlacement: 'center',
          labelFill: '#ffffff',
          labelFontSize: 10,
          labelBackground: true,
          labelBackgroundFill: 'rgba(15, 31, 61, 0.5)',
          labelPadding: 2,
          labelAutoRotate: false,
          labelTextAlign: 'center',
          labelTextBaseline: 'middle',
          ...props.edgeStyleOptions
        }
      };
    })
    .filter(Boolean);

  return { nodes: nodeData, edges: edgeData };
};

const applyGraphData = async () => {
  if (!graphInstance) return;

  const data = buildGraphData();
  graphInstance.setData(data);
  graphInstance.setLayout(getLayoutConfig());
  await graphInstance.render();
  if (props.autoFit && typeof graphInstance.fitView === 'function') {
    await graphInstance.fitView({ padding: 32 }, false);
  }
  emit('data-rendered');
};

const bindEvents = () => {
  if (!graphInstance) return;

  graphInstance.on('node:click', ({ id }) => {
    emit('node-click', { id, data: graphInstance.getNodeData(id) });
    if (props.enableFocusNeighbor && graphInstance.focusElement) {
      graphInstance.focusElement(id, { duration: 200 });
    }
  });

  graphInstance.on('edge:click', ({ id }) => {
    emit('edge-click', { id, data: graphInstance.getEdgeData(id) });
  });

  graphInstance.on('canvas:click', () => {
    emit('canvas-click');
    if (props.enableFocusNeighbor && graphInstance.focusElement) {
      graphInstance.focusElement([], { duration: 150 });
    }
  });
};

const initGraph = () => {
  if (!container.value) return;
  const { offsetWidth: width, offsetHeight: height } = container.value;

  if (width === 0 || height === 0) {
    initTimer = window.setTimeout(initGraph, 200);
    return;
  }

  if (graphInstance) {
    graphInstance.destroy();
    graphInstance = null;
  }

  graphInstance = new Graph({
    container: container.value,
    width,
    height,
    autoFit: props.autoFit ? 'view' : undefined,
    autoResize: props.autoResize,
    background: '#0f172a',
    animation: false,
    zoomRange: [0.15, 5],
    behaviors: [
      'drag-canvas',
      'zoom-canvas',
      { type: 'drag-element', key: 'drag-element' },
      props.enableFocusNeighbor ? { type: 'focus-element', degree: 1 } : null
    ].filter(Boolean),
    node: {
      type: 'circle',
      style: {
        fill: '#2b8af7',
        stroke: '#c8dcff',
        lineWidth: 1.4,
        labelPlacement: 'center',
        labelFill: '#ffffff',
        labelFontSize: 12,
        labelFontWeight: 700,
        labelFontFamily: 'Microsoft YaHei, sans-serif',
        labelWordWrap: true,
        labelMaxWidth: '90%',
        shadowColor: 'rgba(0, 0, 0, 0.25)',
        shadowBlur: 12,
        shadowOffsetY: 4
      }
    },
    edge: {
      type: 'line',
      style: {
        stroke: '#e6edf7',
        opacity: 0.7,
        lineWidth: 1.2,
        endArrow: true,
        arrowSize: 10,
        labelPlacement: 'center',
        labelFontSize: 10,
        labelFill: '#dbeafe'
      }
    },
    layout: getLayoutConfig()
  });

  bindEvents();
  applyGraphData();
  emit('ready', { graph: graphInstance });
};

watch(
  () => props.graphData,
  () => nextTick(() => applyGraphData()),
  { deep: true }
);

watch(
  () => [props.hiddenDimensions, props.layoutOptions, props.highlightKeywords],
  () => nextTick(() => applyGraphData()),
  { deep: true }
);

onMounted(() => {
  nextTick(() => initGraph());
});

onUnmounted(() => {
  if (initTimer) window.clearTimeout(initTimer);
  if (graphInstance) {
    graphInstance.destroy();
    graphInstance = null;
  }
});

const refreshGraph = () => applyGraphData();
const fitView = () => graphInstance?.fitView?.({ padding: 32 });
const fitCenter = () => graphInstance?.fitCenter?.({ duration: 200 });
const getInstance = () => ({ graph: graphInstance });
const focusNode = (id) => graphInstance?.focusElement?.(id, { duration: 200 });
const clearFocus = () => graphInstance?.focusElement?.([], { duration: 150 });
const applyHighlightKeywords = () => applyGraphData();
const clearHighlights = () => applyGraphData();

defineExpose({
  refreshGraph,
  fitView,
  fitCenter,
  getInstance,
  focusNode,
  clearFocus,
  applyHighlightKeywords,
  clearHighlights
});
</script>

<style lang="less" scoped>
.g6-graph-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at 20% 15%, rgba(78, 134, 204, 0.15) 0%, rgba(12, 28, 51, 0) 45%),
    linear-gradient(135deg, #0f1f3d 0%, #0c1730 100%);
  overflow: hidden;

  .g6-canvas {
    width: 100%;
    height: 100%;
  }

  .slots {
    pointer-events: none;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    z-index: 10;

    .overlay {
      width: 100%;
      flex-shrink: 0;
      flex-grow: 0;
      pointer-events: auto;

      &.top {
        top: 0;
      }
      &.bottom {
        bottom: 0;
      }
    }

    .content {
      pointer-events: none;
      flex: 1;
    }

    .content * {
      pointer-events: none;
    }
  }
}
</style>
