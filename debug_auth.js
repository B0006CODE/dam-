// 检查用户认证状态的调试脚本
// 在浏览器控制台中运行此脚本来检查登录状态

console.log('=== 用户认证状态检查 ===');

// 检查 localStorage 中的用户信息
const token = localStorage.getItem('user_token');
const userId = localStorage.getItem('user_id');
const username = localStorage.getItem('username');
const userRole = localStorage.getItem('user_role');

console.log('Token:', token ? '已设置' : '未设置');
console.log('用户ID:', userId);
console.log('用户名:', username);
console.log('用户角色:', userRole);

// 检查是否为管理员
const isAdmin = userRole === 'admin' || userRole === 'superadmin';
console.log('是否为管理员:', isAdmin);

// 检查当前页面
console.log('当前页面:', window.location.href);

// 尝试获取用户信息
if (token) {
    fetch('/api/auth/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('认证失败');
        }
    })
    .then(user => {
        console.log('服务器验证的用户信息:', user);
        console.log('用户角色:', user.role);
        console.log('是否为管理员:', user.role === 'admin' || user.role === 'superadmin');
    })
    .catch(error => {
        console.error('获取用户信息失败:', error);
    });
} else {
    console.log('未找到登录令牌，请先登录');
}

console.log('=== 检查结束 ===');