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

const selectedSeedNodeIds = new Set();
const highlightedNodeIds = new Set();
const highlightedEdgeIds = new Set();

const layoutType = computed(() => props.layoutOptions.type || 'force');
const normalizedKeywords = computed(() =>
  (props.highlightKeywords || [])
    .filter(Boolean)
    .map((kw) => String(kw).toLowerCase())
);

const getEdgeSourceId = (edge) =>
  edge?.source_id ?? edge?.sourceId ?? edge?.source ?? edge?.from ?? edge?.start;

const getEdgeTargetId = (edge) =>
  edge?.target_id ?? edge?.targetId ?? edge?.target ?? edge?.to ?? edge?.end;

const hasElement = (id) => {
  if (!graphInstance || id == null) return false;
  try {
    return !!graphInstance.getElementData?.(String(id));
  } catch {
    return false;
  }
};

const applyCumulativeHighlights = async () => {
  if (!graphInstance) return;

  const existingSeeds = Array.from(selectedSeedNodeIds).filter((id) => {
    try {
      return !!graphInstance.getNodeData?.(id);
    } catch {
      return false;
    }
  });

  selectedSeedNodeIds.clear();
  existingSeeds.forEach((id) => selectedSeedNodeIds.add(id));

  const nextHighlightedNodes = new Set();
  const nextHighlightedEdges = new Set();

  selectedSeedNodeIds.forEach((seedId) => {
    const edges = graphInstance.getRelatedEdgesData?.(seedId, 'both') || [];
    edges.forEach((edge) => {
      const edgeId = edge?.id != null ? String(edge.id) : '';
      if (edgeId) nextHighlightedEdges.add(edgeId);
      const sourceId = edge?.source != null ? String(edge.source) : '';
      const targetId = edge?.target != null ? String(edge.target) : '';
      if (sourceId && !selectedSeedNodeIds.has(sourceId)) nextHighlightedNodes.add(sourceId);
      if (targetId && !selectedSeedNodeIds.has(targetId)) nextHighlightedNodes.add(targetId);
    });
  });

  const updates = {};

  const clearIfStale = (id, nextSet) => {
    if (!nextSet.has(id) && hasElement(id)) updates[id] = [];
  };

  highlightedNodeIds.forEach((id) => clearIfStale(id, nextHighlightedNodes));
  highlightedEdgeIds.forEach((id) => clearIfStale(id, nextHighlightedEdges));

  const ensureState = (id, state) => {
    if (!hasElement(id)) return;
    updates[id] = state;
  };

  selectedSeedNodeIds.forEach((id) => ensureState(id, ['selected']));
  nextHighlightedNodes.forEach((id) => ensureState(id, ['active']));
  nextHighlightedEdges.forEach((id) => ensureState(id, ['active']));

  highlightedNodeIds.clear();
  highlightedEdgeIds.clear();
  nextHighlightedNodes.forEach((id) => highlightedNodeIds.add(id));
  nextHighlightedEdges.forEach((id) => highlightedEdgeIds.add(id));

  if (Object.keys(updates).length > 0) {
    await graphInstance.setElementState(updates, false);
  }
};

const addSeedHighlight = async (id) => {
  if (!graphInstance || id == null) return;
  const seedId = String(id);
  if (!seedId) return;
  selectedSeedNodeIds.add(seedId);
  await applyCumulativeHighlights();
};

const clearSeedHighlights = async () => {
  const updates = {};
  [...selectedSeedNodeIds, ...highlightedNodeIds, ...highlightedEdgeIds].forEach((id) => {
    if (hasElement(id)) updates[id] = [];
  });
  selectedSeedNodeIds.clear();
  highlightedNodeIds.clear();
  highlightedEdgeIds.clear();
  if (graphInstance && Object.keys(updates).length > 0) {
    await graphInstance.setElementState(updates, false);
  }
};

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

const getLayoutConfig = (nodeSizeById) => {
  const { type: _ignoredType, ...userOptions } = props.layoutOptions || {};

  if (layoutType.value === 'circular') {
    return {
      type: 'circular',
      startAngle: 0,
      endAngle: Math.PI * 2,
      radius: null,
      animation: false,
      ...userOptions,
      type: 'circular',
      animation: false,
    };
  }

  const getNodeSize = (node, fallbackId) => {
    if (fallbackId != null && nodeSizeById?.get?.(String(fallbackId))) {
      return nodeSizeById.get(String(fallbackId));
    }
    const dataSize = node?.data?.size ?? node?.data?.style?.size;
    if (typeof dataSize === 'number') return dataSize;
    if (Array.isArray(dataSize)) return Math.max(...dataSize);
    if (dataSize && typeof dataSize === 'object' && dataSize.width && dataSize.height) {
      return Math.max(dataSize.width, dataSize.height);
    }
    return 64;
  };

  const defaultLinkDistance = (edge, source, target) => {
    const sourceId = source?.id ?? edge?.source;
    const targetId = target?.id ?? edge?.target;
    const sourceSize = getNodeSize(source, sourceId);
    const targetSize = getNodeSize(target, targetId);
    const min = (sourceSize + targetSize) / 2 + 220;
    return Math.max(300, min);
  };

  return {
    type: 'force',
    linkDistance: defaultLinkDistance,
    nodeStrength: 2200,
    edgeStrength: 35,
    preventOverlap: true,
    collideStrength: 1,
    nodeSize: (node) => node?.data?.size ?? node?.data?.style?.size ?? 32,
    nodeSpacing: 48,
    damping: 0.9,
    maxSpeed: 120,
    gravity: 2,
    factor: 2,
    coulombDisScale: 0.004,
    interval: 0.02,
    maxIteration: 3000,
    minMovement: 0.1,
    animation: false,
    ...userOptions,
    type: 'force',
    animation: false,
  };
};

const buildGraphData = () => {
  const { nodes = [], edges = [] } = filterByDimensions(
    props.graphData.nodes || [],
    props.graphData.edges || [],
    props.hiddenDimensions
  );

  const isDenseGraph = edges.length >= 300;

  const colorMap = buildNodeColorMap(nodes, edges);
  const degrees = new Map();
  nodes.forEach((n) => degrees.set(String(n.id), 0));
  edges.forEach((edge) => {
    const s = getEdgeSourceId(edge);
    const t = getEdgeTargetId(edge);
    if (s == null || t == null) return;
    const sId = String(s);
    const tId = String(t);
    if (degrees.has(sId)) degrees.set(sId, (degrees.get(sId) || 0) + 1);
    if (degrees.has(tId)) degrees.set(tId, (degrees.get(tId) || 0) + 1);
  });

  const keywordSet = normalizedKeywords.value;
  const matchedNodes = new Set();

  const normalizeLabel = (node) => {
    const label =
      node?.[props.labelField] ||
      node?.name ||
      node?.label ||
      node?.id ||
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

  const parallelOffsetByEdgeIdx = new Map();
  const parallelGroups = new Map();
  edges.forEach((edge, idx) => {
    const sourceRaw = getEdgeSourceId(edge);
    const targetRaw = getEdgeTargetId(edge);
    if (sourceRaw == null || targetRaw == null) return;
    const sourceId = String(sourceRaw);
    const targetId = String(targetRaw);
    if (!degrees.has(sourceId) || !degrees.has(targetId)) return;

    const pairKey =
      sourceId < targetId ? `${sourceId}::${targetId}` : `${targetId}::${sourceId}`;
    const group = parallelGroups.get(pairKey) || [];
    group.push(idx);
    parallelGroups.set(pairKey, group);
  });

  parallelGroups.forEach((indices) => {
    if (!Array.isArray(indices) || indices.length <= 1) return;
    const mid = (indices.length - 1) / 2;
    const step = 22;
    indices.forEach((edgeIdx, pos) => {
      parallelOffsetByEdgeIdx.set(edgeIdx, (pos - mid) * step);
    });
  });

  const edgeData = edges
    .map((edge, idx) => {
      const sourceRaw = getEdgeSourceId(edge);
      const targetRaw = getEdgeTargetId(edge);
      if (sourceRaw == null || targetRaw == null) return null;

      const sourceId = String(sourceRaw);
      const targetId = String(targetRaw);
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

      const curveOffset = parallelOffsetByEdgeIdx.get(idx) || 0;
      const labelOffsetY = Math.max(-16, Math.min(16, curveOffset * 0.35));

      return {
        id: edge.id ? String(edge.id) : `e-${idx}-${sourceId}-${targetId}`,
        source: sourceId,
        target: targetId,
        type: 'line',
        data: edge,
        style: {
          stroke: '#ffffff',
          opacity:
            keywordSet.length === 0
              ? isDenseGraph
                ? 0.22
                : 0.38
              : connectsHighlight
                ? 0.75
                : 0.18,
          lineWidth:
            keywordSet.length === 0
              ? isDenseGraph
                ? 1
                : 1.4
              : connectsHighlight
                ? 1.9
                : 1.2,
          endArrow: false,
          ...(labelOffsetY ? { labelOffsetY } : {}),
          labelText,
          labelPlacement: 'center',
          labelFill: '#ffffff',
          labelFontSize: 10,
          labelOpacity:
            keywordSet.length === 0
              ? isDenseGraph
                ? 0.6
                : 0.92
              : connectsHighlight
                ? 1
                : 0.55,
          labelBackground: false,
          labelBackgroundFill: 'rgba(15, 31, 61, 0.72)',
          labelBackgroundOpacity: 0.75,
          labelPadding: 3,
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
  const nodeSizeById = new Map(
    (data.nodes || []).map((n) => [String(n.id), n?.size || n?.style?.size || 32])
  );
  graphInstance.setLayout(getLayoutConfig(nodeSizeById));
  await graphInstance.render();
  if (selectedSeedNodeIds.size > 0) {
    await applyCumulativeHighlights();
  }
  if (props.autoFit && typeof graphInstance.fitView === 'function') {
    await graphInstance.fitView({ padding: 32 }, false);
  }
  emit('data-rendered');
};

const bindEvents = () => {
  if (!graphInstance) return;

  graphInstance.on('node:click', (event) => {
    const id = event?.target?.id;
    if (id == null) return;
    emit('node-click', { id, data: graphInstance.getNodeData(id) });
    if (props.enableFocusNeighbor && graphInstance.focusElement) {
      graphInstance.focusElement(id, { duration: 200 });
    }
    if (props.enableFocusNeighbor) {
      void addSeedHighlight(id);
    }
  });

  graphInstance.on('edge:click', (event) => {
    const id = event?.target?.id;
    if (id == null) return;
    emit('edge-click', { id, data: graphInstance.getEdgeData(id) });
  });

  graphInstance.on('canvas:click', () => {
    emit('canvas-click');
    if (props.enableFocusNeighbor && graphInstance.focusElement) {
      graphInstance.focusElement([], { duration: 150 });
    }
    void clearSeedHighlights();
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
      {
        type: 'drag-element',
        key: 'drag-element',
        animation: false,
        dropEffect: 'none',
        hideEdge: 'all',
        state: '__drag_selected__'
      }
    ].filter(Boolean),
    node: {
      type: 'circle',
      state: {
        inactive: { opacity: 0.18, labelOpacity: 0.18 },
        active: { opacity: 1, lineWidth: 2.4, stroke: '#ffffff' },
        selected: { opacity: 1, lineWidth: 4, stroke: '#ffffff' },
      },
    },
    edge: {
      type: 'line',
      style: {
        increasedLineWidthForHitTesting: 6,
      },
      state: {
        inactive: { opacity: 0.18, labelOpacity: 0.55, labelBackground: false, endArrow: false },
        active: {
          opacity: 0.9,
          lineWidth: 2.2,
          labelOpacity: 1,
          labelBackground: true,
          zIndex: 1,
        },
        selected: {
          opacity: 0.95,
          lineWidth: 3,
          labelOpacity: 1,
          labelBackground: true,
          zIndex: 2,
        },
      },
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
