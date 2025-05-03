import time
import logging
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from typing import Optional

# 配置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sg90.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SG90')

class SG90:
    # 常數定義
    DEFAULT_FREQUENCY = 50  # Hz
    MIN_ANGLE = 0
    MAX_ANGLE = 90
    MIN_PULSE_WIDTH = 1000  # 微秒 (0度)
    MAX_PULSE_WIDTH = 2000  # 微秒 (90度)
    PULSE_PERIOD = 20000    # 微秒 (50Hz 週期)
    MAX_DUTY_CYCLE = 65535  # PCA9685 16位元最大值

    def __init__(self, channel: int = 0, frequency: int = DEFAULT_FREQUENCY):
        """
        初始化 SG90 伺服馬達控制器

        Args:
            channel (int): PCA9685 的通道號碼 (0-15)
            frequency (int): PWM 頻率，預設為 50Hz

        Raises:
            ValueError: 當通道號碼或頻率超出有效範圍時
        """
        logger.info(f"初始化 SG90 伺服馬達控制器 - 通道: {channel}, 頻率: {frequency}Hz")
        if not 0 <= channel <= 15:
            logger.error(f"無效的通道號碼: {channel}")
            raise ValueError("通道號碼必須在 0 到 15 之間")
        if frequency <= 0:
            logger.error(f"無效的頻率: {frequency}")
            raise ValueError("頻率必須大於 0")

        self._channel = channel
        self._frequency = frequency
        self._initialize_hardware()

    def _initialize_hardware(self) -> None:
        """初始化硬體設備"""
        try:
            logger.info("開始初始化硬體設備")
            self.i2c = busio.I2C(SCL, SDA)
            self.pca = PCA9685(self.i2c)
            self.pca.frequency = self._frequency
            self.servo_channel = self.pca.channels[self._channel]
            logger.info("硬體初始化成功")
        except Exception as e:
            logger.error(f"硬體初始化失敗: {str(e)}")
            raise RuntimeError(f"硬體初始化失敗: {str(e)}")

    def _calculate_duty_cycle(self, angle: float) -> int:
        """
        計算指定角度對應的 duty cycle 值

        Args:
            angle (float): 目標角度 (0~90)

        Returns:
            int: 計算出的 duty cycle 值
        """
        # 計算脈衝寬度（微秒）
        pulse_width = self.MIN_PULSE_WIDTH + (angle / self.MAX_ANGLE) * (self.MAX_PULSE_WIDTH - self.MIN_PULSE_WIDTH)
        # 轉換為 duty cycle
        return int((pulse_width / self.PULSE_PERIOD) * self.MAX_DUTY_CYCLE)

    def set_angle(self, angle: float) -> int:
        """
        設定伺服馬達角度

        Args:
            angle (float): 目標角度 (0~90)

        Returns:
            int: 實際設定的 duty cycle 值

        Raises:
            ValueError: 當角度超出有效範圍時
        """
        logger.info(f"嘗試設定角度: {angle}度")
        if not self.MIN_ANGLE <= angle <= self.MAX_ANGLE:
            logger.error(f"角度超出範圍: {angle}度")
            raise ValueError(f"角度必須在 {self.MIN_ANGLE} 到 {self.MAX_ANGLE} 度之間")

        duty_cycle = self._calculate_duty_cycle(angle)
        self.servo_channel.duty_cycle = duty_cycle
        
        # 計算實際脈衝寬度（用於除錯）
        pulse_width = (duty_cycle / self.MAX_DUTY_CYCLE) * self.PULSE_PERIOD
        logger.info(f"設定角度: {angle}度, 脈衝寬度: {pulse_width:.1f}us, duty_cycle: {duty_cycle}")
        
        return duty_cycle

    def get_current_angle(self) -> Optional[float]:
        """
        根據當前 duty cycle 計算馬達角度

        Returns:
            Optional[float]: 當前角度，如果無法計算則返回 None
        """
        try:
            duty_cycle = self.servo_channel.duty_cycle
            pulse_width = (duty_cycle / self.MAX_DUTY_CYCLE) * self.PULSE_PERIOD
            angle = ((pulse_width - self.MIN_PULSE_WIDTH) / 
                    (self.MAX_PULSE_WIDTH - self.MIN_PULSE_WIDTH)) * self.MAX_ANGLE
            current_angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, angle))
            logger.debug(f"當前角度: {current_angle}度")
            return current_angle
        except Exception as e:
            logger.error(f"獲取當前角度時發生錯誤: {str(e)}")
            return None

    def cleanup(self) -> None:
        """
        清理資源，釋放 I2C 與 PCA9685
        """
        logger.info("開始清理資源")
        try:
            self.pca.deinit()
            self.i2c.deinit()
            logger.info("資源清理成功")
        except Exception as e:
            logger.error(f"清理資源時發生錯誤: {str(e)}")

if __name__ == "__main__":
    # 測試程式碼
    logger.info("開始執行測試程式")
    servo = SG90(channel=1)
    try:
        # 從 0 度每次增加 5 度，測試到 90 度
        for angle in range(0, 91, 5):
            servo.set_angle(angle)
            time.sleep(1)
            current_angle = servo.get_current_angle()
            logger.info(f"測試 - 當前角度: {current_angle}度")
    finally:
        servo.cleanup()
        logger.info("測試程式結束")