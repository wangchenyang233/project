import requests
import time
import logging
from flask import current_app

# 设置日志记录器
logger = logging.getLogger(__name__)

class PolymarketAPIError(Exception):
    """Polymarket API请求异常"""
    pass

class RequestUtil:
    def __init__(self, base_url=None):
        # 使用应用配置中的API URL，如果没有则使用默认URL
        self.base_url = base_url or current_app.config.get('DATA_API_URL', 'https://data-api.polymarket.com')
    
    def make_request(self, endpoint, method='GET', params=None, data=None, retries=3):
        """发送HTTP请求并处理异常
        
        Args:
            endpoint: API端点路径
            method: 请求方法（GET、POST等）
            params: 查询参数
            data: 请求体数据
            retries: 重试次数
        
        Returns:
            API响应的JSON数据
        
        Raises:
            PolymarketAPIError: API请求失败时抛出
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                logger.debug(f"Request: {method} {url}, params: {params}, data: {data}")
                
                # 完全按照示例脚本的方式发送请求，不使用会话，不设置任何请求头
                if method.upper() == 'GET':
                    response = requests.get(url, params=params, timeout=10)
                else:
                    response = requests.request(method, url, params=params, data=data, timeout=10)
                
                # 检查响应状态码
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # 处理频率限制
                    logger.warning(f"Rate limit exceeded. Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    # 其他错误状态码
                    logger.error(f"API request failed with status {response.status_code}: {response.text[:500]}...")  # 只记录前500个字符
                    raise PolymarketAPIError(
                        f"API请求失败: {response.status_code} {response.text[:200]}..."
                    )
            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timeout. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error: {str(e)}")
                if attempt == retries - 1:
                    raise PolymarketAPIError(f"网络请求失败: {str(e)}")
                time.sleep(2 ** attempt)
        
        # 重试次数耗尽
        logger.error(f"Max retries ({retries}) exceeded for {url}")
        raise PolymarketAPIError(f"API请求重试次数耗尽")
    
    def fetch_latest_trades(self, params=None):
        """获取Polymarket最新交易数据
        
        Args:
            params: 动态传入的查询参数
                示例: {
                    'user': '0xa59c570a9eca148da55f6e1f47a538c0c600bb62',
                    'limit': 50,
                    'type': 'TRADE'
                }
        
        Returns:
            最新交易数据列表
        """
        # 完全按照参考脚本的方式实现
        url = "https://data-api.polymarket.com/activity"
        
        # 设置默认参数，与参考脚本保持一致
        default_params = {
            'limit': 50,
            'type': 'TRADE',  # 只返回（BUY / SELL），不包括 SPLIT / MERGE / REDEEM
            'sortBy': 'TIMESTAMP',  # 按照时间排序
            'sortDirection': 'DESC'  # 最新的在最前
        }
        
        # 合并默认参数和传入参数
        if params:
            default_params.update(params)
        
        logger.info(f"Sending request to {url} with params: {default_params}")
        
        # 直接使用requests.get，不使用会话，与参考脚本完全一致
        response = requests.get(url, params=default_params, timeout=10)
        logger.info(f"API response status: {response.status_code}")
        logger.info(f"API response headers: {dict(response.headers)}")
        logger.info(f"API response content: {response.text[:500]}...")
        
        try:
            response.raise_for_status()  # 检查响应状态
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise
        
        # 解析API响应
        data = response.json()
        logger.info(f"Parsed API response: {data}")
        
        # 处理两种可能的响应格式：
        # 1. 直接返回交易数组
        # 2. 返回带有value字段的对象
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'value' in data:
            return data['value']
        else:
            logger.warning(f"Unexpected API response format: {type(data)}")
            return []

# 全局实例（延迟初始化）
request_util = None

# 导出便捷函数
def fetch_latest_trades(params=None):
    """获取最新交易的便捷函数"""
    global request_util
    # 如果实例尚未初始化，创建新实例
    if request_util is None:
        request_util = RequestUtil()
    return request_util.fetch_latest_trades(params)
