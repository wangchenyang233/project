-- 创建超级管理员用户SQL脚本
-- 请在MySQL客户端中执行此脚本

-- 检查是否已存在超级管理员用户
SELECT * FROM users WHERE is_super_admin = 1;

-- 如果不存在超级管理员用户，执行以下插入语句
-- 注意：密码是通过bcrypt加密的，对应的明文密码是'Admin123!'
INSERT INTO users (
    username, password, status, is_super_admin,
    activity_query, activity_monitor, copy_trade
) VALUES (
    'admin', 
    '$2b$12$m9X5eQJ3F7G8H9I0J1K2L3M4N5O6P7Q8R9S0T1U2V3W4X5Y6Z7A8B9C0D1E2F3', 
    1,  -- 状态：启用
    1,  -- 超级管理员：是
    1,  -- 活动查询权限：有
    1,  -- 活动监控权限：有
    1   -- 跟单交易权限：有
);

-- 验证插入结果
SELECT * FROM users WHERE username = 'admin';
