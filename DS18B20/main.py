from w1thermsensor import W1ThermSensor
import time
from typing import Optional, Tuple
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TemperatureSensor:
    def __init__(self, retry_interval: int = 1, max_retries: int = 3):
        """
        初始化溫度感測器
        
        Args:
            retry_interval (int): 重試間隔（秒）
            max_retries (int): 最大重試次數
        """
        self.sensor = None
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.initialize_sensor()

    def initialize_sensor(self) -> bool:
        """
        初始化感測器
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.sensor = W1ThermSensor()
            logger.info("溫度感測器初始化成功")
            return True
        except Exception as e:
            logger.error(f"初始化感測器時發生錯誤: {e}")
            self.sensor = None
            return False

    def read_temperature(self) -> Optional[Tuple[float, datetime]]:
        """
        讀取溫度
        
        Returns:
            Optional[Tuple[float, datetime]]: (溫度值, 讀取時間) 或 None（如果讀取失敗）
        """
        if self.sensor is None:
            logger.warning("嘗試重新初始化感測器...")
            if not self.initialize_sensor():
                return None

        try:
            temperature_c = self.sensor.get_temperature()
            return temperature_c, datetime.now()
        except Exception as e:
            logger.error(f"讀取溫度時發生錯誤: {e}")
            return None

    def read_temperature_with_retry(self) -> Optional[Tuple[float, datetime]]:
        """
        重試讀取溫度
        
        Returns:
            Optional[Tuple[float, datetime]]: (溫度值, 讀取時間) 或 None（如果所有重試都失敗）
        """
        for attempt in range(self.max_retries):
            result = self.read_temperature()
            if result is not None:
                return result
            if attempt < self.max_retries - 1:
                logger.warning(f"重試讀取溫度 ({attempt + 1}/{self.max_retries})...")
                time.sleep(self.retry_interval)
        return None

def format_temperature(temperature: float) -> str:
    """
    格式化溫度顯示
    
    Args:
        temperature (float): 溫度值
        
    Returns:
        str: 格式化後的溫度字串
    """
    return f"{temperature:.2f}°C"

def main():
    """
    主程式
    """
    sensor = TemperatureSensor()
    
    try:
        while True:
            result = sensor.read_temperature_with_retry()
            if result is not None:
                temperature, timestamp = result
                print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] 目前溫度：{format_temperature(temperature)}")
            else:
                print("無法讀取溫度，請檢查感測器連接")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程式已停止")
    except Exception as e:
        logger.error(f"程式執行時發生錯誤: {e}")

if __name__ == "__main__":
    main()