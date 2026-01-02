import hashlib
import logging

# 设置日志记录器
logger = logging.getLogger(__name__)

class DedupUtil:
    @staticmethod
    def get_unique_key(data):
        """生成数据的唯一标识
        
        优先使用transactionHash作为唯一标识，如果不存在，则基于（timestamp+asset+side+size+price）生成
        
        Args:
            data: 交易数据字典，包含transactionHash或（timestamp、asset、side、size、price）字段
        
        Returns:
            唯一标识字符串
        """
        # 检查是否包含transactionHash字段
        if 'transactionHash' in data and data['transactionHash']:
            logger.debug(f"Using transactionHash as unique key: {data['transactionHash']}")
            return data['transactionHash']
        
        # 如果没有transactionHash，使用其他字段组合生成
        required_fields = ['timestamp', 'asset', 'side', 'size', 'price']
        
        # 检查是否包含所有必要字段
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            logger.warning(f"Missing required fields for unique key generation: {missing_fields}")
            # 如果缺少字段，生成一个基于可用字段的唯一标识
            available_fields = {k: v for k, v in data.items() if k in required_fields and v}
            key_data = '-'.join([f"{k}:{v}" for k, v in sorted(available_fields.items())])
        else:
            # 组合所有必要字段
            key_data = f"{data['timestamp']}-{data['asset']}-{data['side']}-{data['size']}-{data['price']}"
        
        # 使用SHA-256生成唯一哈希
        unique_hash = hashlib.sha256(key_data.encode('utf-8')).hexdigest()
        logger.debug(f"Generated unique hash from fields: {unique_hash}")
        
        return unique_hash
    
    @staticmethod
    def deduplicate_data(data_list):
        """对交易数据列表进行去重
        
        Args:
            data_list: 交易数据字典列表
        
        Returns:
            去重后的交易数据列表
        """
        if not data_list:
            return []
        
        unique_data = {}
        duplicates_count = 0
        
        for data in data_list:
            try:
                unique_key = DedupUtil.get_unique_key(data)
                if unique_key not in unique_data:
                    unique_data[unique_key] = data
                else:
                    duplicates_count += 1
                    logger.debug(f"Duplicate found with key: {unique_key}")
            except Exception as e:
                logger.error(f"Error generating unique key for data {data}: {str(e)}")
                # 保留无法生成唯一标识的数据
                unique_data[hashlib.sha256(str(data).encode('utf-8')).hexdigest()] = data
        
        logger.info(f"Deduplication completed: {len(data_list)} original, {len(unique_data)} unique, {duplicates_count} duplicates removed")
        return list(unique_data.values())

# 导出便捷函数
def get_unique_key(data):
    """生成数据唯一标识的便捷函数"""
    return DedupUtil.get_unique_key(data)

def deduplicate_data(data_list):
    """数据去重的便捷函数"""
    return DedupUtil.deduplicate_data(data_list)
