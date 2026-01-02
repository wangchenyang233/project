import Cookies from 'js-cookie';

const TokenKey = 'vue3-frontend-token';
const RefreshTokenKey = 'vue3-frontend-refresh-token';

/**
 * 设置JWT令牌
 * @param {string} token - 访问令牌
 * @param {string} refreshToken - 刷新令牌
 */
export function setToken(token, refreshToken) {
  Cookies.set(TokenKey, token, { expires: 7 }); // 7天过期
  Cookies.set(RefreshTokenKey, refreshToken, { expires: 30 }); // 30天过期
}

/**
 * 获取访问令牌
 * @returns {string|null} - 访问令牌
 */
export function getToken() {
  return Cookies.get(TokenKey);
}

/**
 * 获取刷新令牌
 * @returns {string|null} - 刷新令牌
 */
export function getRefreshToken() {
  return Cookies.get(RefreshTokenKey);
}

/**
 * 移除JWT令牌
 */
export function removeToken() {
  Cookies.remove(TokenKey);
  Cookies.remove(RefreshTokenKey);
}

/**
 * 检查是否存在令牌
 * @returns {boolean} - 是否存在令牌
 */
export function hasToken() {
  return !!getToken();
}