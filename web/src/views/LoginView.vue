<template>
  <!-- 鐧诲綍椤甸潰鏍瑰鍣紝鏍规嵁鏈嶅姟鍣ㄧ姸鎬佸姩鎬佹坊鍔犳牱寮忕被 -->
  <div class="login-view" :class="{ 'has-alert': serverStatus === 'error' }">
    <!-- 鏈嶅姟鐘舵€佸紓甯告椂鐨勯《閮ㄦ彁绀烘潯 -->
    <div v-if="serverStatus === 'error'" class="server-status-alert">
      <div class="alert-content">
        <exclamation-circle-outlined class="alert-icon" />
        <div class="alert-text">
          <div class="alert-title">鏈嶅姟绔繛鎺ュけ璐?/div>
          <div class="alert-message">{{ serverError }}</div>
        </div>
        <a-button type="link" size="small" @click="checkServerHealth" :loading="healthChecking">
          閲嶈瘯
        </a-button>
      </div>
    </div>



    <!-- 鐧诲綍椤甸潰涓昏甯冨眬 -->
    <div class="login-layout">
      <!-- 宸︿晶鍝佺墝褰㈣薄鍥剧墖鍖哄煙 -->
      <div class="login-image-section">
        <img :src="loginBgImage" alt="鐧诲綍鑳屾櫙" class="login-bg-image" />
        <div class="image-overlay">
          <div class="brand-info">
             <h1 class="brand-title">{{ brandName }}</h1>
             <p class="brand-subtitle">{{ brandSubtitle }}</p>
             <p class="brand-description">{{ brandDescription }}</p>
           </div>
          <div class="brand-copyright">
            <p>{{ infoStore.footer?.copyright || 'Smart Water' }}. {{ infoStore.branding?.copyright || '鐗堟潈鎵€鏈? }}</p>
          </div>
        </div>
      </div>

      <!-- 鍙充晶鐧诲綍琛ㄥ崟鍖哄煙 -->
      <!-- 鍙充晶鐧诲綍琛ㄥ崟鍖哄煙 -->
      <div class="login-form-section">
        <!-- 鐧诲綍妗嗗鍣?-->
        <div class="login-container">
          <!-- 鐧诲綍妗嗗ご閮細鏄剧ず娆㈣繋璇拰鍝佺墝淇℃伅 -->
          <header class="login-header">
            <p class="login-title">娆㈣繋鐧诲綍</p>
            <h1 class="login-brand">{{ brandName }}</h1>
            <p v-if="!isFirstRun && brandSubtitle" class="login-subtitle">{{ brandSubtitle }}</p>
          </header>

          <!-- 鐧诲綍鍐呭鍖哄煙锛氬寘鍚〃鍗?-->
          <div class="login-content" :class="{ 'is-initializing': isFirstRun }">
            <!-- 鍒濆鍖栫鐞嗗憳琛ㄥ崟 -->
            <div v-if="isFirstRun" class="login-form login-form--init">
              <h2>绯荤粺鍒濆鍖栵紝璇峰垱寤鸿秴绾х鐞嗗憳</h2>
              <a-form
                :model="adminForm"
                @finish="handleInitialize"
                layout="vertical"
              >
                <a-form-item
                  label="鐢ㄦ埛ID"
                  name="user_id"
                  :rules="[
                    { required: true, message: '璇疯緭鍏ョ敤鎴稩D' },
                    {
                      pattern: /^[a-zA-Z0-9_]+$/,
                      message: '鐢ㄦ埛ID鍙兘鍖呭惈瀛楁瘝銆佹暟瀛楀拰涓嬪垝绾?
                    },
                    {
                      min: 3,
                      max: 20,
                      message: '鐢ㄦ埛ID闀垮害蹇呴』鍦?-20涓瓧绗︿箣闂?
                    }
                  ]"
                >
                  <a-input
                    v-model:value="adminForm.user_id"
                    placeholder="璇疯緭鍏ョ敤鎴稩D锛?-20涓瓧绗︼級"
                    :maxlength="20"
                  />
                </a-form-item>



                <a-form-item
                  label="瀵嗙爜"
                  name="password"
                  :rules="[{ required: true, message: '璇疯緭鍏ュ瘑鐮? }]"
                >
                  <a-input-password v-model:value="adminForm.password" prefix-icon="lock" />
                </a-form-item>

                <a-form-item
                  label="纭瀵嗙爜"
                  name="confirmPassword"
                  :rules="[
                    { required: true, message: '璇风‘璁ゅ瘑鐮? },
                    { validator: validateConfirmPassword }
                  ]"
                >
                  <a-input-password v-model:value="adminForm.confirmPassword" prefix-icon="lock" />
                </a-form-item>

                <a-form-item>
                  <a-button type="primary" html-type="submit" :loading="loading" block>鍒涘缓绠＄悊鍛樿处鎴?/a-button>
                </a-form-item>
              </a-form>
            </div>

            <!-- 鐧诲綍琛ㄥ崟 -->
            <div v-else class="login-form">
              <a-form
                :model="loginForm"
                @finish="handleLogin"
                layout="vertical"
              >
                <a-form-item
                  label="鐧诲綍璐﹀彿"
                  name="loginId"
                  :rules="[{ required: true, message: '璇疯緭鍏ョ敤鎴稩D' }]"
                >
                  <a-input v-model:value="loginForm.loginId" placeholder="璇疯緭鍏ョ敤鎴稩D">
                    <template #prefix>
                      <user-outlined />
                    </template>
                  </a-input>
                </a-form-item>

                <a-form-item
                  label="瀵嗙爜"
                  name="password"
                  :rules="[{ required: true, message: '璇疯緭鍏ュ瘑鐮? }]"
                >
                  <a-input-password v-model:value="loginForm.password">
                    <template #prefix>
                      <lock-outlined />
                    </template>
                  </a-input-password>
                </a-form-item>

                <a-form-item>
                  <div class="login-options" style="justify-content: flex-end;">
                    <a class="forgot-password" @click="showDevMessage">蹇樿瀵嗙爜?</a>
                  </div>
                </a-form-item>

                <a-form-item>
                  <a-button
                    type="primary"
                    html-type="submit"
                    :loading="loading"
                    :disabled="isLocked"
                    block
                  >
                    <span v-if="isLocked">璐︽埛宸查攣瀹?{{ formatTime(lockRemainingTime) }}</span>
                    <span v-else>鐧诲綍</span>
                  </a-button>
                </a-form-item>

                <!-- 绗笁鏂圭櫥褰曢€夐」
                <div class="third-party-login">
                  <div class="divider">
                    <span>鍏朵粬鐧诲綍鏂瑰紡</span>
                  </div>
                  <div class="login-icons">
                    <a-tooltip title="寰俊鐧诲綍">
                      <a-button shape="circle" class="login-icon" @click="showDevMessage">
                        <template #icon><wechat-outlined /></template>
                      </a-button>
                    </a-tooltip>
                    <a-tooltip title="浼佷笟寰俊鐧诲綍">
                      <a-button shape="circle" class="login-icon" @click="showDevMessage">
                        <template #icon><qrcode-outlined /></template>
                      </a-button>
                    </a-tooltip>
                    <a-tooltip title="椋炰功鐧诲綍">
                      <a-button shape="circle" class="login-icon" @click="showDevMessage">
                        <template #icon><thunderbolt-outlined /></template>
                      </a-button>
                    </a-tooltip>
                  </div>
                </div> -->
              </a-form>
            </div>

            <!-- 閿欒鎻愮ず -->
            <div v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </div>
          </div>

          <!-- 椤佃剼 -->
          <!-- <div class="login-footer">
            <a href="#" @click.prevent>鑱旂郴鎴戜滑</a>
            <a href="#" @click.prevent>浣跨敤甯姪</a>
            <a href="#" @click.prevent>闅愮鏀跨瓥</a>
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Vue 鏍稿績鍔熻兘瀵煎叆
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
// 璺敱鍔熻兘瀵煎叆
import { useRouter } from 'vue-router';
// 鐘舵€佺鐞嗕粨搴撳鍏?
import { useUserStore } from '@/stores/user';
import { useInfoStore } from '@/stores/info';
import { useAgentStore } from '@/stores/agent';
// UI 缁勪欢搴撳鍏?
import { message } from 'ant-design-vue';
// API 鎺ュ彛瀵煎叆
import { healthApi } from '@/apis/system_api';
// 鍥炬爣缁勪欢瀵煎叆
import { UserOutlined, LockOutlined, WechatOutlined, QrcodeOutlined, ThunderboltOutlined, ExclamationCircleOutlined } from '@ant-design/icons-vue';

// 鍒濆鍖栬矾鐢卞拰鐘舵€佷粨搴?
const router = useRouter();
const userStore = useUserStore();
const infoStore = useInfoStore();
const agentStore = useAgentStore();

// 鍝佺墝灞曠ず鏁版嵁
// 鍝佺墝灞曠ず鏁版嵁璁＄畻灞炴€?
// 鐧诲綍鑳屾櫙鍥撅紝浼樺厛浣跨敤閰嶇疆鐨勮儗鏅紝鍚﹀垯浣跨敤榛樿鑳屾櫙
const loginBgImage = computed(() => {
  return infoStore.organization?.login_bg || '/login-bg.jpg';
});
// 鍝佺墝鍚嶇О锛屼紭鍏堜娇鐢ㄩ厤缃殑鍚嶇О锛屽惁鍒欎娇鐢ㄩ粯璁ゅ悕绉?
const brandName = computed(() => {
  const rawName = infoStore.branding?.name ?? '';
  const trimmed = rawName.trim();
  return trimmed || 'AI 椹卞姩鐨勬櫤鑳芥按鍒╅棶绛斿钩鍙?;
});
// 鍝佺墝鍓爣棰?
const brandSubtitle = computed(() => {
  const rawSubtitle = infoStore.branding?.subtitle ?? '';
  const trimmed = rawSubtitle.trim();
  return trimmed || '澶фā鍨嬮┍鍔ㄧ殑鐭ヨ瘑搴撶鐞嗗伐鍏?;
});
// 鍝佺墝鎻忚堪
const brandDescription = computed(() => {
  const rawDescription = infoStore.branding?.description ?? '';
  const trimmed = rawDescription.trim();
  return trimmed || '缁撳悎鐭ヨ瘑搴撲笌鐭ヨ瘑鍥捐氨锛屾彁渚涙洿鍑嗙‘銆佹洿鍏ㄩ潰鐨勫洖绛?;
});

// 鐘舵€?
// 椤甸潰鐘舵€佸彉閲?
const isFirstRun = ref(false); // 鏄惁棣栨杩愯锛堥渶瑕佸垵濮嬪寲绠＄悊鍛橈級
const loading = ref(false); // 琛ㄥ崟鎻愪氦鍔犺浇鐘舵€?
const errorMessage = ref(''); // 閿欒鎻愮ず淇℃伅
const serverStatus = ref('loading'); // 鏈嶅姟鍣ㄨ繛鎺ョ姸鎬侊細loading, ok, error
const serverError = ref(''); // 鏈嶅姟鍣ㄩ敊璇俊鎭?
const healthChecking = ref(false); // 鍋ュ悍妫€鏌ュ姞杞界姸鎬?

// 鐧诲綍閿佸畾鐩稿叧鐘舵€佸彉閲?
const isLocked = ref(false); // 璐︽埛鏄惁琚攣瀹?
const lockRemainingTime = ref(0); // 閿佸畾鍓╀綑鏃堕棿锛堢锛?
const lockCountdown = ref(null); // 鍊掕鏃跺畾鏃跺櫒寮曠敤

// 鐧诲綍琛ㄥ崟
const loginForm = reactive({
  loginId: '', // 鐢ㄦ埛ID鐧诲綍
  password: ''
});

// 绠＄悊鍛樺垵濮嬪寲琛ㄥ崟
const adminForm = reactive({
  user_id: '', // 鐩存帴杈撳叆user_id
  password: '',
  confirmPassword: ''
});

// 寮€鍙戜腑鍔熻兘鎻愮ず
// 鏄剧ず鍔熻兘寮€鍙戜腑鎻愮ず
const showDevMessage = () => {
  message.info('璇ュ姛鑳芥鍦ㄥ紑鍙戜腑锛屾暚璇锋湡寰咃紒');
};

// 娓呯悊閿佸畾鍊掕鏃跺櫒
const clearLockCountdown = () => {
  if (lockCountdown.value) {
    clearInterval(lockCountdown.value);
    lockCountdown.value = null;
  }
};

// 鍚姩閿佸畾鍊掕鏃?
const startLockCountdown = (remainingSeconds) => {
  clearLockCountdown();
  isLocked.value = true;
  lockRemainingTime.value = remainingSeconds;

  lockCountdown.value = setInterval(() => {
    lockRemainingTime.value--;
    if (lockRemainingTime.value <= 0) {
      clearLockCountdown();
      isLocked.value = false;
      errorMessage.value = '';
    }
  }, 1000);
};

// 鏍煎紡鍖栨椂闂存樉绀?
const formatTime = (seconds) => {
  if (seconds < 60) {
    return `${seconds}绉抈;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}鍒?{remainingSeconds}绉抈;
  } else if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}灏忔椂${minutes}鍒嗛挓`;
  } else {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    return `${days}澶?{hours}灏忔椂`;
  }
};

// 瀵嗙爜纭楠岃瘉
const validateConfirmPassword = async (rule, value) => {
  if (value === '') {
    throw new Error('璇风‘璁ゅ瘑鐮?);
  }
  if (value !== adminForm.password) {
    throw new Error('涓ゆ杈撳叆鐨勫瘑鐮佷笉涓€鑷?);
  }
};

// 澶勭悊鐧诲綍
// 澶勭悊鐧诲綍鎻愪氦閫昏緫
const handleLogin = async () => {
  // 濡傛灉褰撳墠琚攣瀹氾紝涓嶅厑璁哥櫥褰?
  if (isLocked.value) {
    message.warning(`璐︽埛琚攣瀹氾紝璇风瓑寰?${formatTime(lockRemainingTime.value)}`);
    return;
  }

  try {
    // 璁剧疆鍔犺浇鐘舵€佸苟娓呴櫎閿欒淇℃伅
    loading.value = true;
    errorMessage.value = '';
    clearLockCountdown();

    // 璋冪敤 store 鐨勭櫥褰曟柟娉?
    await userStore.login({
      loginId: loginForm.loginId,
      password: loginForm.password
    });

    message.success('鐧诲綍鎴愬姛');

    // 鑾峰彇閲嶅畾鍚戣矾寰勶紙濡傛灉瀛樺湪锛?
    const redirectPath = sessionStorage.getItem('redirect') || '/';
    sessionStorage.removeItem('redirect'); // 娓呴櫎閲嶅畾鍚戜俊鎭?

    // 鏍规嵁鐢ㄦ埛瑙掕壊鍐冲畾閲嶅畾鍚戠洰鏍?
    if (redirectPath === '/') {
      // 濡傛灉鏄鐞嗗憳锛岀洿鎺ヨ烦杞埌鏅鸿兘浣撶鐞嗛〉闈?
      if (userStore.isAdmin) {
        router.push('/agent');
        return;
      }

      // 鏅€氱敤鎴疯烦杞埌榛樿鏅鸿兘浣撻〉闈?
      try {
        await agentStore.initialize();
      } catch (error) {
        console.error('鑾峰彇鏅鸿兘浣撲俊鎭け璐?', error);
      }
      router.push('/agent');
      return;
    } else {
      // 璺宠浆鍒板叾浠栭璁剧殑璺緞
      router.push(redirectPath);
    }
  } catch (error) {
    console.error('鐧诲綍澶辫触:', error);

    // 妫€鏌ユ槸鍚︽槸閿佸畾閿欒锛圚TTP 423锛?
    if (error.status === 423) {
      // 灏濊瘯浠庡搷搴斿ご涓幏鍙栧墿浣欐椂闂?
      let remainingTime = 0;
      if (error.headers && error.headers.get) {
        const lockRemainingHeader = error.headers.get('X-Lock-Remaining');
        if (lockRemainingHeader) {
          remainingTime = parseInt(lockRemainingHeader);
        }
      }

      // 濡傛灉娌℃湁浠庡ご涓幏鍙栧埌锛屽皾璇曚粠閿欒娑堟伅涓В鏋?
      if (remainingTime === 0) {
        const lockTimeMatch = error.message.match(/(\d+)\s*绉?);
        if (lockTimeMatch) {
          remainingTime = parseInt(lockTimeMatch[1]);
        }
      }

      // 濡傛灉鑾峰彇鍒颁簡鍓╀綑鏃堕棿锛屽惎鍔ㄥ€掕鏃?
      if (remainingTime > 0) {
        startLockCountdown(remainingTime);
        errorMessage.value = `鐢变簬澶氭鐧诲綍澶辫触锛岃处鎴峰凡琚攣瀹?${formatTime(remainingTime)}`;
      } else {
        errorMessage.value = error.message || '璐︽埛琚攣瀹氾紝璇风◢鍚庡啀璇?;
      }
    } else {
      // 鍏朵粬鐧诲綍閿欒
      errorMessage.value = error.message || '鐧诲綍澶辫触锛岃妫€鏌ョ敤鎴峰悕鍜屽瘑鐮?;
    }
  } finally {
    // 鏃犺鎴愬姛澶辫触锛屽彇娑堝姞杞界姸鎬?
    loading.value = false;
  }
};

// 澶勭悊鍒濆鍖栫鐞嗗憳
const handleInitialize = async () => {
  try {
    loading.value = true;
    errorMessage.value = '';

    if (adminForm.password !== adminForm.confirmPassword) {
      errorMessage.value = '涓ゆ杈撳叆鐨勫瘑鐮佷笉涓€鑷?;
      return;
    }

    await userStore.initialize({
      user_id: adminForm.user_id,
      password: adminForm.password
    });

    message.success('绠＄悊鍛樿处鎴峰垱寤烘垚鍔?);
    router.push('/agent');
  } catch (error) {
    console.error('鍒濆鍖栧け璐?', error);
    errorMessage.value = error.message || '鍒濆鍖栧け璐ワ紝璇烽噸璇?;
  } finally {
    loading.value = false;
  }
};

// 妫€鏌ユ槸鍚︽槸棣栨杩愯
const checkFirstRunStatus = async () => {
  try {
    loading.value = true;
    const isFirst = await userStore.checkFirstRun();
    isFirstRun.value = isFirst;
  } catch (error) {
    console.error('妫€鏌ラ娆¤繍琛岀姸鎬佸け璐?', error);
    errorMessage.value = '绯荤粺鍑洪敊锛岃绋嶅悗閲嶈瘯';
  } finally {
    loading.value = false;
  }
};

// 妫€鏌ユ湇鍔″櫒鍋ュ悍鐘舵€?
const checkServerHealth = async () => {
  try {
    healthChecking.value = true;
    const response = await healthApi.checkHealth();
    if (response.status === 'ok') {
      serverStatus.value = 'ok';
    } else {
      serverStatus.value = 'error';
      serverError.value = response.message || '鏈嶅姟绔姸鎬佸紓甯?;
    }
  } catch (error) {
    console.error('妫€鏌ユ湇鍔″櫒鍋ュ悍鐘舵€佸け璐?', error);
    serverStatus.value = 'error';
    serverError.value = error.message || '鏃犳硶杩炴帴鍒版湇鍔＄锛岃妫€鏌ョ綉缁滆繛鎺?;
  } finally {
    healthChecking.value = false;
  }
};

// 缁勪欢鎸傝浇鏃?
// 缁勪欢鎸傝浇鏃剁殑鐢熷懡鍛ㄦ湡閽╁瓙
onMounted(async () => {
  // 濡傛灉鐢ㄦ埛宸茬櫥褰曪紝鐩存帴璺宠浆鍒版櫤鑳戒綋椤甸潰
  if (userStore.isLoggedIn) {
    router.push('/agent');
    return;
  }

  // 棣栧厛妫€鏌ユ湇鍔″櫒鍋ュ悍鐘舵€?
  await checkServerHealth();

  // 妫€鏌ョ郴缁熸槸鍚︽槸棣栨杩愯锛堟槸鍚﹂渶瑕佸垵濮嬪寲锛?
  await checkFirstRunStatus();
});

// 缁勪欢鍗歌浇鏃剁殑鐢熷懡鍛ㄦ湡閽╁瓙
onUnmounted(() => {
  // 娓呯悊閿佸畾鍊掕鏃跺櫒锛岄槻姝㈠唴瀛樻硠婕?
  clearLockCountdown();
});
</script>

<style lang="less" scoped>
/* 鐧诲綍椤甸潰鏁翠綋瀹瑰櫒 */
.login-view {
  height: 100vh;
  width: 100%;
  position: relative;
  padding-top: 0;
  background: transparent; /* 浣跨敤鍏ㄥ眬鑳屾櫙 */

  /* 褰撴湁椤堕儴璀﹀憡鏉℃椂鐨勬牱寮忚皟鏁?*/
  &.has-alert {
    padding-top: 60px;
  }
}

/* 椤堕儴鎿嶄綔鎸夐挳鍖哄煙 */
.login-top-action {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 10;
}

.back-home-btn {
  color: var(--text-secondary);
  font-size: 14px;
  padding: 0 8px;

  &:hover,
  &:focus {
    color: var(--main-color);
    background-color: transparent;
  }
}

/* 鐧诲綍甯冨眬瀹瑰櫒锛氬乏鍙冲垎鏍?*/
.login-layout {
  display: flex;
  min-height: 100%;
  width: 100%;
  background: transparent; /* 閫忔槑锛屾樉绀?body 鑳屾櫙 */
}

/* 宸︿晶鍥剧墖鍖哄煙鏍峰紡 */
.login-image-section {
  flex: 0 0 52%; /* 鍗犳嵁 52% 瀹藉害 */
  position: relative;
  overflow: hidden;
  max-height: 100vh;
  border-right: var(--glass-border); /* 娣诲姞鍙充晶杈规 */

  /* 鑳屾櫙鍥剧墖鏍峰紡 */
  .login-bg-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    filter: brightness(0.7) contrast(1.1); /* 闄嶄綆浜害锛屽鍔犲姣斿害 */
  }

  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(to right, rgba(6, 42, 92, 0.8), rgba(6, 42, 92, 0.4)); /* 钃濊壊娓愬彉閬僵 */
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 72px 64px 36px;
    backdrop-filter: blur(2px);
  }

  .brand-info {
    text-align: left;
    color: var(--text-primary);
    max-width: 520px;

    .brand-title {
      font-size: 52px;
      font-weight: 700;
      margin-bottom: 20px;
      text-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand-subtitle {
      font-size: 24px;
      font-weight: 500;
      margin-bottom: 24px;
      opacity: 0.92;
      text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
      line-height: 1.4;
      color: var(--text-primary);
    }

    .brand-description {
      font-size: 18px;
      line-height: 1.6;
      margin: 0;
      opacity: 0.82;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
      color: var(--text-secondary);
    }
  }

  .brand-copyright {
    align-self: flex-start;

    p {
      margin: 0;
      font-size: 14px;
      color: var(--text-disabled);
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
      font-weight: 400;
    }
  }
}

/* 鍙充晶琛ㄥ崟鍖哄煙鏍峰紡 */
.login-form-section {
  flex: 1; /* 鍗犳嵁鍓╀綑瀹藉害 */
  min-width: 420px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 64px 72px;
  background: transparent;
}

/* 鐧诲綍妗嗗鍣ㄦ牱寮?*/
.login-container {
  width: 100%;
  max-width: 560px;
  padding: 50px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border-radius: 24px;
  border: 1px solid var(--glass-border);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  display: flex;
  flex-direction: column;
  gap: 32px;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;

  &:hover {
    box-shadow: 
      0 20px 40px -10px rgba(6, 182, 212, 0.2),
      0 0 0 1px rgba(6, 182, 212, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.08);
    border-color: rgba(6, 182, 212, 0.3);
  }
}

.login-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}

.login-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--main-color);
  text-transform: uppercase;
}

.login-brand {
  margin: 0;
  font-size: 30px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.25;
}

.login-subtitle {
  margin: 0;
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.login-content {
  display: flex;
  flex-direction: column;
  gap: 24px;

  &.is-initializing {
    gap: 28px;
  }
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;

  :deep(.ant-form) {
    width: 100%;
  }

  :deep(.ant-form-item) {
    margin-bottom: 18px;
  }

  :deep(.ant-form-item-label > label) {
    color: var(--text-secondary);
  }

  :deep(.ant-input) {
    padding: 10px 11px;
    height: auto;
    background-color: rgba(6, 42, 92, 0.3);
    color: var(--text-primary);
    border-radius: 8px;
    transition: all 0.3s ease;

    &:hover {
      border-color: rgba(6, 182, 212, 0.5);
      background-color: rgba(15, 23, 42, 0.9);
    }

    &:focus-within, &.ant-input-affix-wrapper-focused {
      border-color: var(--main-color);
      background-color: rgba(15, 23, 42, 0.9);
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
    }

    input {
      background-color: transparent;
      color: var(--text-primary);
      &::placeholder {
        color: var(--text-disabled);
      }
    }

    .anticon {
      color: var(--text-tertiary);
      transition: color 0.2s ease;
    }

    &:hover .anticon,
    &:focus-within .anticon {
      color: var(--text-secondary);
    }
  }

  :deep(.ant-input-password) {
    .ant-input-suffix {
      .anticon {
        cursor: pointer;
        &:hover {
          color: var(--main-color);
        }
      }
    }
  }

  :deep(.ant-btn) {
    font-size: 16px;
    font-weight: 500;
    padding: 12px 16px;
    height: auto;
    background: linear-gradient(135deg, var(--main-color) 0%, var(--main-active) 100%);
    border: none;
    border-radius: 8px;
    box-shadow: 0 4px 14px 0 rgba(6, 182, 212, 0.35);
    transition: all 0.3s ease;

    &:hover:not(:disabled) {
      background: linear-gradient(135deg, var(--main-hover) 0%, var(--main-color) 100%);
      box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
      transform: translateY(-2px);
    }

    &:active:not(:disabled) {
      transform: translateY(0);
      box-shadow: 0 2px 8px rgba(6, 182, 212, 0.3);
    }

    &:disabled {
      background: rgba(107, 114, 128, 0.5);
      box-shadow: none;
      cursor: not-allowed;
    }
  }
}

.login-form--init {
  padding: 24px;
  border-radius: 18px;
  background: rgba(6, 182, 212, 0.05);
  border: 1px solid rgba(6, 182, 212, 0.2);

  h2 {
    margin-bottom: 16px;
    font-size: 22px;
    font-weight: 600;
    color: var(--main-color);
    text-align: left;
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 12px;
  flex-wrap: wrap;

  :deep(.ant-checkbox-wrapper) {
    color: var(--text-secondary);
  }

  .forgot-password {
    color: var(--main-color);
    font-size: 14px;

    &:hover {
      color: var(--main-hover);
    }
  }
}

.init-tips {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px 18px;
  margin-bottom: 20px;
  text-align: left;

  p {
    margin: 4px 0;
    font-size: 13px;
    color: var(--main-700);
    line-height: 1.45;

    &:first-child {
      margin-top: 0;
    }

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.error-message {
  margin-top: 16px;
  padding: 10px 12px;
  background-color: var(--stats-error-bg);
  border: 1px solid rgba(220, 38, 38, 0.25);
  border-radius: 8px;
  color: var(--stats-error-color);
  font-size: 14px;
}

.third-party-login {
  margin-top: 20px;

  .divider {
    position: relative;
    text-align: center;
    margin: 16px 0;

    &::before, &::after {
      content: '';
      position: absolute;
      top: 50%;
      width: calc(50% - 60px);
      height: 1px;
      background-color: var(--gray-200);
    }

    &::before {
      left: 0;
    }

    &::after {
      right: 0;
    }

    span {
      display: inline-block;
      padding: 0 12px;
      background-color: var(--gray-0);
      position: relative;
      color: var(--gray-600);
      font-size: 14px;
    }
  }

  .login-icons {
    display: flex;
    justify-content: center;
    margin-top: 16px;

    .login-icon {
      margin: 0 12px;
      width: 42px;
      height: 42px;
      color: var(--gray-600);
      border: 1px solid var(--gray-300);
      transition: color 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;

      &:hover {
        color: var(--main-color);
        border-color: var(--main-color);
        background-color: var(--main-20);
      }
    }
  }
}


.login-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--gray-150);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;

  a {
    color: var(--gray-600);
    cursor: pointer;

    &:hover {
      color: var(--main-color);
    }
  }
}

.server-status-alert {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 12px 20px;
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
  color: white;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(255, 77, 79, 0.3);

  .alert-content {
    display: flex;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;

    .alert-icon {
      font-size: 20px;
      margin-right: 12px;
      color: white;
    }

    .alert-text {
      flex: 1;

      .alert-title {
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 2px;
      }

      .alert-message {
        font-size: 14px;
        opacity: 0.9;
      }
    }

    :deep(.ant-btn-link) {
      color: white;
      border-color: white;

      &:hover {
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
      }
    }
  }
}
</style>
