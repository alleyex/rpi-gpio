#!/usr/bin/env python3
from gpiozero import DistanceSensor
import time
import logging

# 設置日誌格式和級別
# level=logging.INFO: 設定日誌級別為 INFO，會顯示 INFO 及以上級別的訊息
# format: 設定日誌格式，包含時間、級別和訊息內容
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HCSR04:
    """
    HC-SR04 超音波距離感測器類別
    
    這個類別封裝了 HC-SR04 超音波感測器的基本功能，包括：
    - 初始化感測器
    - 測量單次距離
    - 計算多次測量的平均值
    - 安全關閉感測器
    
    使用 gpiozero 庫來控制 GPIO 腳位，簡化了底層操作。
    """
    
    def __init__(self, trigger_pin=23, echo_pin=24):
        """
        初始化 HC-SR04 感測器
        
        參數:
            trigger_pin (int): Trigger 腳位的 BCM 編號，預設為 23
                - 這個腳位用於發送超音波脈衝
            echo_pin (int): Echo 腳位的 BCM 編號，預設為 24
                - 這個腳位用於接收回波信號
                
        注意事項:
            - 使用 BCM 編號而不是物理腳位編號
            - 確保腳位連接正確，避免短路
        """
        try:
            # 創建 DistanceSensor 實例，使用指定的 GPIO 腳位
            self.sensor = DistanceSensor(
                trigger=trigger_pin,
                echo=echo_pin
            )
            logger.info(f"HC-SR04 感測器初始化成功 (Trigger: {trigger_pin}, Echo: {echo_pin})")
        except Exception as e:
            logger.error(f"HC-SR04 感測器初始化失敗: {str(e)}")
            raise
    
    def get_distance(self):
        """
        測量單次距離
        
        回傳:
            float: 測得的距離，單位為公分
            
        注意事項:
            - 返回的距離值已經從公尺轉換為公分
            - 測量範圍通常在 2-400 公分之間
            - 超出範圍的測量可能不準確
        """
        try:
            # 使用 gpiozero 的 distance 屬性獲取距離（單位：公尺）
            # 乘以 100 轉換為公分
            distance = self.sensor.distance * 100
            logger.debug(f"測量距離: {distance:.2f} 公分")
            return distance
        except Exception as e:
            logger.error(f"距離測量失敗: {str(e)}")
            raise
    
    def get_average_distance(self, samples=3, delay=0.1):
        """
        進行多次測量並回傳平均值，以獲得更穩定的結果
        
        參數:
            samples (int): 測量次數，預設為 3
                - 建議使用奇數次測量，避免極端值影響
            delay (float): 每次測量之間的延遲時間（秒），預設為 0.1
                - 給予感測器足夠的恢復時間
                
        回傳:
            float: 平均距離，單位為公分
            
        注意事項:
            - 多次測量可以減少單次測量的誤差
            - 延遲時間過短可能影響測量準確性
        """
        try:
            distances = []
            for i in range(samples):
                distance = self.get_distance()
                distances.append(distance)
                logger.debug(f"第 {i+1} 次測量: {distance:.2f} 公分")
                if i < samples - 1:  # 最後一次測量後不需要延遲
                    time.sleep(delay)
            
            # 計算所有測量值的平均值
            average = sum(distances) / len(distances)
            logger.info(f"平均距離: {average:.2f} 公分 (共 {samples} 次測量)")
            return average
        except Exception as e:
            logger.error(f"平均距離計算失敗: {str(e)}")
            raise
    
    def close(self):
        """
        安全關閉感測器
        
        注意事項:
            - 在程式結束前務必調用此方法
            - 釋放 GPIO 資源，避免資源洩漏
            - 確保感測器正確關閉，避免硬體損壞
        """
        try:
            self.sensor.close()
            logger.info("HC-SR04 感測器已關閉")
        except Exception as e:
            logger.error(f"關閉感測器失敗: {str(e)}")
            raise

if __name__ == "__main__":
    # 範例使用程式碼
    # 創建感測器實例
    sensor = HCSR04()
    try:
        # 持續測量距離
        while True:
            # 使用平均測量來獲得更穩定的結果
            # samples=5: 進行 5 次測量
            # delay=0.1: 每次測量間隔 0.1 秒
            dist = sensor.get_average_distance(samples=5, delay=0.1)
            print(f"距離：{dist:.2f} 公分")
            time.sleep(1)  # 每秒更新一次測量結果
    except KeyboardInterrupt:
        # 當使用者按下 Ctrl+C 時，優雅地結束程式
        print("\n程式已停止")
    finally:
        # 確保感測器被正確關閉
        sensor.close() 