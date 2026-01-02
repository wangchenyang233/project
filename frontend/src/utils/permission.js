import { useUserStore } from '../stores/modules/user';

/**
 * 检查是否为超级管理员
 * @returns {boolean} - 是否为超级管理员
 */
export function isSuperAdmin() {
  const userStore = useUserStore();
  return userStore.role === 'super_admin';
}

/**
 * 检查是否拥有指定模块的权限
 * @param {string} module - 模块名称（如：activity_query、activity_monitor、copy_trade）
 * @returns {boolean} - 是否拥有权限
 */
export function isHasModulePermission(module) {
  const userStore = useUserStore();
  
  // 超级管理员拥有所有权限
  if (isSuperAdmin()) {
    return true;
  }
  
  // 检查用户是否拥有该模块权限
  return userStore.permissions?.[module] || false;
}

/**
 * 检查是否拥有多个模块中的任意一个权限
 * @param {Array<string>} modules - 模块名称数组
 * @returns {boolean} - 是否拥有任意一个权限
 */
export function hasAnyPermission(modules) {
  if (!Array.isArray(modules)) {
    return false;
  }
  
  // 超级管理员拥有所有权限
  if (isSuperAdmin()) {
    return true;
  }
  
  // 检查是否拥有任意一个模块权限
  return modules.some(module => isHasModulePermission(module));
}