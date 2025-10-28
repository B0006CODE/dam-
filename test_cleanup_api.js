// 测试任务清理API的脚本
// 在浏览器控制台中运行

console.log('=== 测试任务清理API ===');

// 1. 测试获取任务列表
async function testGetTasks() {
  try {
    const response = await fetch('/api/tasks', {
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('user_token')
      }
    });
    const data = await response.json();
    console.log('任务列表获取成功:', data.tasks?.length || 0, '个任务');
    return data;
  } catch (error) {
    console.error('获取任务列表失败:', error);
    return null;
  }
}

// 2. 测试清理失败任务
async function testCleanupFailed() {
  try {
    console.log('测试清理失败任务...');
    const response = await fetch('/api/tasks/cleanup', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('user_token')
      },
      body: JSON.stringify({
        status: 'failed'
      })
    });

    console.log('清理失败任务响应状态:', response.status);
    const data = await response.json();
    console.log('清理失败任务结果:', data);
    return data;
  } catch (error) {
    console.error('清理失败任务失败:', error);
    return null;
  }
}

// 3. 依次执行测试
async function runTests() {
  console.log('开始测试...');

  // 获取清理前的任务列表
  const beforeData = await testGetTasks();

  // 执行清理
  const cleanupResult = await testCleanupFailed();

  // 获取清理后的任务列表
  console.log('等待2秒后重新获取任务列表...');
  setTimeout(async () => {
    const afterData = await testGetTasks();

    if (beforeData && afterData) {
      const beforeFailed = beforeData.tasks?.filter(t => t.status === 'failed').length || 0;
      const afterFailed = afterData.tasks?.filter(t => t.status === 'failed').length || 0;
      console.log(`失败任务数量变化: ${beforeFailed} → ${afterFailed}`);
    }

    console.log('=== 测试完成 ===');
  }, 2000);
}

// 执行测试
runTests();