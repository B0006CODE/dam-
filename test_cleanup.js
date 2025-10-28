// 测试任务清理功能的脚本
// 在浏览器控制台中运行此脚本来测试清理功能

console.log('=== 测试任务清理功能 ===');

// 1. 检查当前任务列表
console.log('1. 获取当前任务列表...');
fetch('/api/tasks', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('user_token')
  }
})
.then(response => response.json())
.then(data => {
  console.log('当前任务数量:', data.tasks?.length || 0);
  if (data.tasks && data.tasks.length > 0) {
    console.log('任务状态分布:');
    const statusCount = {};
    data.tasks.forEach(task => {
      statusCount[task.status] = (statusCount[task.status] || 0) + 1;
    });
    console.table(statusCount);

    // 显示一些任务示例
    console.log('任务示例:');
    console.log(data.tasks.slice(0, 3));
  }
})
.catch(error => {
  console.error('获取任务列表失败:', error);
});

// 2. 测试清理失败任务
console.log('\n2. 测试清理失败任务...');
fetch('/api/tasks/cleanup', {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('user_token')
  },
  body: JSON.stringify({
    status: 'failed'
  })
})
.then(response => {
  console.log('清理失败任务响应状态:', response.status);
  return response.json();
})
.then(data => {
  console.log('清理失败任务结果:', data);
})
.catch(error => {
  console.error('清理失败任务失败:', error);
});

// 3. 测试清理旧任务（超过30天，确保不会误删）
console.log('\n3. 测试清理旧任务（超过30天）...');
const thirtyDaysAgo = new Date();
thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

fetch('/api/tasks/cleanup', {
  method: 'DELETE',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('user_token')
  },
  body: JSON.stringify({
    older_than: thirtyDaysAgo.toISOString()
  })
})
.then(response => {
  console.log('清理旧任务响应状态:', response.status);
  return response.json();
})
.then(data => {
  console.log('清理旧任务结果:', data);
})
.catch(error => {
  console.error('清理旧任务失败:', error);
});

console.log('\n=== 测试脚本执行完成 ===');
console.log('请检查后端日志以获取详细的调试信息。');