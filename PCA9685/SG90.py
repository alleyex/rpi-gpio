import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

class SG90:
    def __init__(self, channel=0, frequency=50):
        """
        初始化 SG90 伺服馬達控制器

        Args:
            channel (int): PCA9685 的通道號碼 (0-15)
            frequency (int): PWM 頻率，預設為 50Hz
        """
        # 初始化 I2C 通訊
        self.i2c = busio.I2C(SCL, SDA)
        # 初始化 PCA9685 控制器
        self.pca = PCA9685(self.i2c)
        # 設定 PWM 頻率為 50Hz（伺服馬達標準）
        self.pca.frequency = frequency
        # 取得指定通道的 PWM 輸出
        self.servo_channel = self.pca.channels[channel]
        
    def set_angle(self, angle):
        """
        設定伺服馬達角度

        Args:
            angle (float): 目標角度 (0~90)
        """
        # 檢查角度是否在允許範圍內
        if angle < 0 or angle > 90:
            raise ValueError("角度必須在 0 到 90 度之間")
        
        # 定義脈衝寬度範圍（單位：微秒）
        min_us = 1000  # 0度時的脈衝寬度（1ms）
        max_us = 2000  # 90度時的脈衝寬度（2ms）
        # 線性對應角度到脈衝寬度
        pulse_us = min_us + (angle / 90.0) * (max_us - min_us)
        # 將脈衝寬度轉換為 duty_cycle（PCA9685 16位元，0~65535）
        # 20ms 週期（50Hz），所以 duty_cycle = (脈衝寬度 / 20000) * 65535
        duty_cycle = int((pulse_us / 20000.0) * 65535)
        # 設定 PWM 輸出
        self.servo_channel.duty_cycle = duty_cycle
        # 印出目前設定資訊
        print(f"設定角度: {angle}度, 脈衝寬度: {pulse_us:.1f}us, duty_cycle: {duty_cycle}")
        return duty_cycle
            
    def cleanup(self):
        """
        清理資源，釋放 I2C 與 PCA9685
        """
        self.pca.deinit()
        self.i2c.deinit()

if __name__ == "__main__":
    # 測試程式碼
    servo = SG90()
    try:
        # 從 0 度每次增加 5 度，測試到 90 度
        angle = 0
        while angle <= 90:
            servo.set_angle(angle)  # 設定馬達角度
            time.sleep(1)          # 停留 1 秒觀察
            angle += 5             # 增加 5 度
    finally:
        # 程式結束時釋放資源
        servo.cleanup()