import { apiGet, apiPost } from './base'

/**
 * 鍥炬暟鎹簱API妯″潡
 * 鍖呭惈LightRAG鍥剧煡璇嗗簱鍜孨eo4j鍥炬暟鎹簱涓ょ鎺ュ彛
 * 閲囩敤鍛藉悕绌洪棿鍒嗙粍妯″紡锛屾竻鏅板尯鍒嗘帴鍙ｇ被鍨? */

// =============================================================================
// === LightRAG鍥剧煡璇嗗簱鎺ュ彛鍒嗙粍 ===
// =============================================================================

export const lightragApi = {
  /**
   * 鑾峰彇LightRAG鐭ヨ瘑鍥捐氨瀛愬浘鏁版嵁
   * @param {Object} params - 鏌ヨ鍙傛暟
   * @param {string} params.db_id - LightRAG鏁版嵁搴揑D
   * @param {string} params.node_label - 鑺傜偣鏍囩锛?*"鑾峰彇鍏ㄥ浘锛?   * @param {number} params.max_depth - 鏈€澶ф繁搴?   * @param {number} params.max_nodes - 鏈€澶ц妭鐐规暟
   * @returns {Promise} - 瀛愬浘鏁版嵁
   */
  getSubgraph: async (params) => {
    const { db_id, node_label = "*", max_depth = 2, max_nodes = 100 } = params

    if (!db_id) {
      throw new Error('db_id is required')
    }

    const queryParams = new URLSearchParams({
      db_id: db_id,
      node_label: node_label,
      max_depth: max_depth.toString(),
      max_nodes: max_nodes.toString()
    })

    return await apiGet(`/api/graph/lightrag/subgraph?${queryParams.toString()}`, {}, true)
  },

  /**
   * 鑾峰彇鎵€鏈夊彲鐢ㄧ殑LightRAG鏁版嵁搴?   * @returns {Promise} - LightRAG鏁版嵁搴撳垪琛?   */
  getDatabases: async () => {
    return await apiGet('/api/graph/lightrag/databases', {}, true)
  },

  /**
   * 鑾峰彇LightRAG鍥捐氨鏍囩鍒楄〃
   * @param {string} db_id - LightRAG鏁版嵁搴揑D
   * @returns {Promise} - 鏍囩鍒楄〃
   */
  getLabels: async (db_id) => {
    if (!db_id) {
      throw new Error('db_id is required')
    }

    const queryParams = new URLSearchParams({
      db_id: db_id
    })

    return await apiGet(`/api/graph/lightrag/labels?${queryParams.toString()}`, {}, true)
  },

  /**
   * 鑾峰彇LightRAG鍥捐氨缁熻淇℃伅
   * @param {string} db_id - LightRAG鏁版嵁搴揑D
   * @returns {Promise} - 缁熻淇℃伅
   */
  getStats: async (db_id) => {
    if (!db_id) {
      throw new Error('db_id is required')
    }

    const queryParams = new URLSearchParams({
      db_id: db_id
    })

    return await apiGet(`/api/graph/lightrag/stats?${queryParams.toString()}`, {}, true)
  }
}

// =============================================================================
// === Generic graph endpoints (paged subgraph) ===
// =============================================================================

export async function getPagedSubgraph(params) {
  const {
    db_id,
    center = '*',
    depth = 2,
    limit = 200,
    page = 1,
    fields = 'compact',
  } = params || {}

  if (!db_id) throw new Error('db_id is required')

  const qp = new URLSearchParams({
    db_id: String(db_id),
    center: String(center),
    depth: String(depth),
    limit: String(limit),
    page: String(page),
    fields: String(fields),
  })

  return await apiGet(`/api/graph/subgraph?${qp.toString()}`, {}, true)
}

// =============================================================================
// === Neo4j鍥炬暟鎹簱鎺ュ彛鍒嗙粍 ===
// =============================================================================

export const neo4jApi = {
  /**
   * 鑾峰彇Neo4j鍥炬暟鎹簱鏍蜂緥鑺傜偣
   * @param {string} kgdb_name - Neo4j鏁版嵁搴撳悕绉帮紙榛樿涓?neo4j'锛?   * @param {number} num - 鑺傜偣鏁伴噺
   * @returns {Promise} - 鏍蜂緥鑺傜偣鏁版嵁
   */
  getSampleNodes: async (kgdb_name = 'neo4j', num = 100) => {
    const queryParams = new URLSearchParams({
      kgdb_name: kgdb_name,
      num: num.toString()
    })

    return await apiGet(`/api/graph/neo4j/nodes?${queryParams.toString()}`, {}, true)
  },

  /**
   * 鏍规嵁瀹炰綋鍚嶇О鏌ヨNeo4j鍥捐妭鐐?   * @param {string} entity_name - 瀹炰綋鍚嶇О
   * @returns {Promise} - 鑺傜偣鏁版嵁
   */
  queryNode: async (entity_name) => {
    if (!entity_name) {
      throw new Error('entity_name is required')
    }

    const queryParams = new URLSearchParams({
      entity_name: entity_name
    })

    return await apiGet(`/api/graph/neo4j/node?${queryParams.toString()}`, {}, true)
  },

  /**
   * 閫氳繃JSONL鏂囦欢娣诲姞鍥捐氨瀹炰綋鍒癗eo4j
   * @param {string} file_path - JSONL鏂囦欢璺緞
   * @param {string} kgdb_name - Neo4j鏁版嵁搴撳悕绉帮紙榛樿涓?neo4j'锛?   * @returns {Promise} - 娣诲姞缁撴灉
   */
  addEntities: async (file_path, kgdb_name = 'neo4j') => {
    return await apiPost('/api/graph/neo4j/add-entities', {
      file_path: file_path,
      kgdb_name: kgdb_name
    }, {}, true)
  },

  /**
   * 涓篘eo4j鍥捐氨鑺傜偣娣诲姞宓屽叆鍚戦噺绱㈠紩
   * @param {string} kgdb_name - Neo4j鏁版嵁搴撳悕绉帮紙榛樿涓?neo4j'锛?   * @returns {Promise} - 绱㈠紩缁撴灉
   */
  indexEntities: async (kgdb_name = 'neo4j') => {
    return await apiPost('/api/graph/neo4j/index-entities', {
      kgdb_name: kgdb_name
    }, {}, true)
  },

  /**
   * 鑾峰彇Neo4j鍥炬暟鎹簱淇℃伅
   * @returns {Promise} - 鍥炬暟鎹簱淇℃伅
   */
  getInfo: async () => {
    return await apiGet('/api/graph/neo4j/info', {}, true)
  }
}

// =============================================================================
// === 宸ュ叿鍑芥暟鍒嗙粍 ===
// =============================================================================

/**
 * 鏍规嵁瀹炰綋绫诲瀷鑾峰彇棰滆壊
 * @param {string} entityType - 瀹炰綋绫诲瀷
 * @returns {string} - 棰滆壊鍊? */
export const getEntityTypeColor = (entityType) => {
  const colorMap = {
    'person': '#FF6B6B',      // 绾㈣壊 - 浜虹墿
    'organization': '#4ECDC4', // 闈掕壊 - 缁勭粐
    'location': '#45B7D1',    // 钃濊壊 - 鍦扮偣
    'geo': '#45B7D1',         // 钃濊壊 - 鍦扮悊浣嶇疆
    'event': '#96CEB4',       // 缁胯壊 - 浜嬩欢
    'category': '#FFEAA7',    // 榛勮壊 - 鍒嗙被
    'equipment': '#DDA0DD',   // 绱壊 - 璁惧
    'athlete': '#FF7675',     // 绾㈣壊 - 杩愬姩鍛?    'record': '#FD79A8',      // 绮夎壊 - 璁板綍
    'year': '#FDCB6E',        // 姗欒壊 - 骞翠唤
    'UNKNOWN': '#B2BEC3',     // 鐏拌壊 - 鏈煡
    'unknown': '#B2BEC3'      // 鐏拌壊 - 鏈煡
  }

  return colorMap[entityType] || colorMap['unknown']
}

/**
 * 鏍规嵁鏉冮噸璁＄畻杈圭殑绮楃粏
 * @param {number} weight - 鏉冮噸鍊? * @param {number} minWeight - 鏈€灏忔潈閲? * @param {number} maxWeight - 鏈€澶ф潈閲? * @returns {number} - 杈圭殑绮楃粏
 */
export const calculateEdgeWidth = (weight, minWeight = 1, maxWeight = 10) => {
  const minWidth = 1
  const maxWidth = 5
  const normalizedWeight = (weight - minWeight) / (maxWeight - minWeight)
  return minWidth + normalizedWeight * (maxWidth - minWidth)
}

// =============================================================================
// === 鍏煎鎬у鍑猴紙鍙€夛紝鐢ㄤ簬骞虫粦杩佺Щ锛?==
// =============================================================================

// 淇濇寔鍚戝悗鍏煎鐨勫鍑猴紝鍚庣画鍙互绉婚櫎
export const getGraphNodes = async (params = {}) => {
  console.warn('getGraphNodes is deprecated, use neo4jApi.getSampleNodes instead')
  return neo4jApi.getSampleNodes(params.kgdb_name || 'neo4j', params.num || 100)
}

export const getGraphNode = async (params = {}) => {
  console.warn('getGraphNode is deprecated, use neo4jApi.queryNode instead')
  return neo4jApi.queryNode(params.entity_name)
}

export const addByJsonl = async (file_path, kgdb_name = 'neo4j') => {
  console.warn('addByJsonl is deprecated, use neo4jApi.addEntities instead')
  return neo4jApi.addEntities(file_path, kgdb_name)
}

export const indexNodes = async (kgdb_name = 'neo4j') => {
  console.warn('indexNodes is deprecated, use neo4jApi.indexEntities instead')
  return neo4jApi.indexEntities(kgdb_name)
}

export const getGraphStats = async () => {
  console.warn('getGraphStats is deprecated, use neo4jApi.getInfo instead')
  return neo4jApi.getInfo()
}

// 保持旧的分组导出，便于批量替换
export const graphApi = {
  getSubgraph: getPagedSubgraph,
  getDatabases: lightragApi.getDatabases,
  getLabels: lightragApi.getLabels,
  getStats: lightragApi.getStats,
  ...neo4jApi
}

