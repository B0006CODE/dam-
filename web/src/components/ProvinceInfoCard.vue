<template>
  <transition name="slide-in">
    <div v-if="province" class="province-info-card">
      <div class="card-header">
        <h2>{{ province }}</h2>
        <button @click="$emit('close')" class="close-btn">
          <span>✕</span>
        </button>
      </div>

      <div class="card-content">
        <!-- Statistics Overview -->
        <div class="stats-overview">
          <div class="stat-item">
            <div class="stat-label">水库总数</div>
            <div class="stat-value">{{ stats?.totalCount || 0 }}</div>
          </div>
        </div>

        <!-- Dam Types Chart -->
        <div v-if="stats?.damTypes && Object.keys(stats.damTypes).length > 0" class="chart-section">
          <h3>坝型分布</h3>
          <div class="chart-grid">
            <div 
              v-for="(count, type) in stats.damTypes" 
              :key="type"
              class="chart-bar-item"
            >
              <div class="bar-label">{{ type }}</div>
              <div class="bar-container">
                <div 
                  class="bar-fill"
                  :style="{ width: `${(count / stats.totalCount) * 100}%` }"
                ></div>
                <span class="bar-value">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Basin Distribution -->
        <div v-if="stats?.basins && Object.keys(stats.basins).length > 0" class="chart-section">
          <h3>流域分布</h3>
          <div class="chart-grid">
            <div 
              v-for="(count, basin) in stats.basins" 
              :key="basin"
              class="chart-bar-item"
            >
              <div class="bar-label">{{ basin }}</div>
              <div class="bar-container">
                <div 
                  class="bar-fill basin"
                  :style="{ width: `${(count / stats.totalCount) * 100}%` }"
                ></div>
                <span class="bar-value">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Reservoir List -->
        <div class="reservoir-list-section">
          <h3>水库列表 ({{ provinceReservoirs.length }})</h3>
          <div class="reservoir-list">
            <div 
              v-for="reservoir in provinceReservoirs" 
              :key="reservoir.id"
              class="reservoir-item"
              @click="$emit('reservoirClick', reservoir)"
            >
              <div class="reservoir-name">{{ reservoir.name }}</div>
              <div class="reservoir-meta">
                <span v-if="reservoir.damType" class="meta-tag">{{ reservoir.damType }}</span>
                <span v-if="reservoir.type" class="meta-tag">{{ reservoir.type }}</span>
                <span v-if="reservoir.capacity" class="meta-tag">
                  {{ reservoir.capacity.toLocaleString() }} 万方
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { getReservoirsByProvince, loadProvinceStats, loadReservoirs } from '@/data/reservoirData';
import type { Reservoir, ProvinceStats, ProvinceStatsMap } from '@/data/reservoirData';

// Props
interface Props {
  province: string | null;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
  close: [];
  reservoirClick: [reservoir: Reservoir];
}>();

// State
const provinceStatsData = ref<ProvinceStatsMap>({});
const reservoirsData = ref<Reservoir[]>([]);

// Load data
const loadData = async () => {
  try {
    [provinceStatsData.value, reservoirsData.value] = await Promise.all([
      loadProvinceStats(),
      loadReservoirs()
    ]);
  } catch (error) {
    console.error('Failed to load data:', error);
  }
};

loadData();

// Computed
const stats = computed(() => {
  return props.province ? provinceStatsData.value[props.province] : null;
});

const provinceReservoirs = computed(() => {
  return props.province ? getReservoirsByProvince(reservoirsData.value, props.province) : [];
});
</script>

<style scoped>
.province-info-card {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 380px;
  max-height: calc(100vh - 120px);
  background: rgba(6, 42, 92, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  z-index: 100;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 136, 255, 0.1));
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.card-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #00d4ff;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.close-btn {
  background: transparent;
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #00d4ff;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-size: 18px;
}

.close-btn:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: #00d4ff;
  transform: scale(1.1);
}

.card-content {
  padding: 20px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.card-content::-webkit-scrollbar {
  width: 6px;
}

.card-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.card-content::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 3px;
}

.card-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
}

.stats-overview {
  margin-bottom: 24px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 8px;
}

.stat-label {
  font-size: 13px;
  color: #8ab4f8;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #00d4ff;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.chart-section {
  margin-bottom: 24px;
}

.chart-section h3 {
  font-size: 16px;
  color: #ffffff;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.chart-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chart-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bar-label {
  font-size: 13px;
  color: #8ab4f8;
  font-weight: 500;
}

.bar-container {
  position: relative;
  height: 28px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #0088ff);
  border-radius: 4px;
  transition: width 0.6s ease;
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.bar-fill.basin {
  background: linear-gradient(90deg, #00ff88, #00cc66);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.bar-value {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  font-weight: 600;
  color: #ffffff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.reservoir-list-section {
  margin-top: 24px;
}

.reservoir-list-section h3 {
  font-size: 16px;
  color: #ffffff;
  margin: 0 0 12px 0;
  font-weight: 600;
}

.reservoir-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.reservoir-item {
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reservoir-item:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: #00d4ff;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
}

.reservoir-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 6px;
}

.reservoir-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 3px;
  color: #8ab4f8;
}

/* Animations */
.slide-in-enter-active,
.slide-in-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-in-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.slide-in-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
