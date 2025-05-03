"""
DS18B20 溫度感測器讀取程式

這個程式使用 DS18B20 溫度感測器來讀取環境溫度。
主要功能包括：
- 初始化溫度感測器
- 讀取溫度值
- 錯誤處理和重試機制
- 溫度值的格式化顯示
- 日誌記錄

使用方式：
1. 確保 DS18B20 感測器已正確連接到 Raspberry Pi
2. 執行此程式即可開始讀取溫度
3. 按 Ctrl+C 可停止程式

依賴套件：
- w1thermsensor: 用於與 DS18B20 感測器通訊
- logging: 用於記錄程式執行狀態
- datetime: 用於記錄溫度讀取時間
"""

from w1thermsensor import W1ThermSensor
import time
from typing import Optional, Tuple
import logging
from datetime import datetime

# 設定日誌格式和等級
# 日誌格式包含時間戳記、日誌等級和訊息內容
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TemperatureSensor:
    """
    溫度感測器類別
    
    這個類別封裝了與 DS18B20 溫度感測器的所有互動，
    包括初始化、讀取溫度和錯誤處理等功能。
    
    屬性：
        sensor: W1ThermSensor 實例
        retry_interval: 重試間隔時間（秒）
        max_retries: 最大重試次數
    """
    def __init__(self, retry_interval: int = 1, max_retries: int = 3):
        """
        初始化溫度感測器
        
        Args:
            retry_interval (int): 重試間隔（秒），預設為 1 秒
            max_retries (int): 最大重試次數，預設為 3 次
        """
        self.sensor = None
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.initialize_sensor()

    def initialize_sensor(self) -> bool:
        """
        初始化感測器
        
        嘗試建立與 DS18B20 感測器的連接。
        如果初始化失敗，會記錄錯誤並返回 False。
        
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
        
        從感測器讀取當前溫度值，並記錄讀取時間。
        如果感測器未初始化，會嘗試重新初始化。
        如果讀取失敗，會記錄錯誤並返回 None。
        
        Returns:
            Optional[Tuple[float, datetime]]: 
                - 成功時返回 (溫度值, 讀取時間)
                - 失敗時返回 None
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
        
        在讀取失敗時進行多次重試，直到成功或達到最大重試次數。
        每次重試之間會等待指定的間隔時間。
        
        Returns:
            Optional[Tuple[float, datetime]]: 
                - 成功時返回 (溫度值, 讀取時間)
                - 所有重試都失敗時返回 None
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
    
    將溫度值格式化為易讀的字串，保留兩位小數並加上攝氏度符號。
    
    Args:
        temperature (float): 溫度值
        
    Returns:
        str: 格式化後的溫度字串，例如 "25.50°C"
    """
    return f"{temperature:.2f}°C"

def main():
    """
    主程式
    
    建立溫度感測器實例並持續讀取溫度值。
    每秒讀取一次溫度並顯示結果。
    可以通過 Ctrl+C 中斷程式執行。
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