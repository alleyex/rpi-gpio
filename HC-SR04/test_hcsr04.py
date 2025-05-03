#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock, patch
import time

# 在導入 HCSR04 之前先模擬 DistanceSensor
mock_distance_sensor = MagicMock()
with patch('gpiozero.DistanceSensor', mock_distance_sensor):
    from hcsr04 import HCSR04

class TestHCSR04(unittest.TestCase):
    """HC-SR04 感測器測試類別"""
    
    def setUp(self):
        """設置測試環境"""
        # 重置 mock
        mock_distance_sensor.reset_mock()
        
        # 設置模擬感測器
        self.mock_sensor = MagicMock()
        self.mock_sensor.distance = 1.0
        mock_distance_sensor.return_value = self.mock_sensor
        
        # 創建感測器實例
        self.hcsr04 = HCSR04()
    
    def test_initialization(self):
        """測試初始化"""
        mock_distance_sensor.assert_called_once_with(
            trigger=23,
            echo=24
        )
    
    def test_get_distance(self):
        """測試單次距離測量"""
        # 設置模擬回傳值
        self.mock_sensor.distance = 0.5  # 50 公分
        
        # 測試距離測量
        distance = self.hcsr04.get_distance()
        self.assertEqual(distance, 50.0)
    
    def test_get_average_distance(self):
        """測試多次距離測量平均值"""
        # 設置模擬回傳值
        self.mock_sensor.distance = 0.3  # 30 公分
        
        # 測試平均距離
        with patch('time.sleep') as mock_sleep:
            average = self.hcsr04.get_average_distance(samples=3)
            # 在 3 個樣本之間需要 3 次延遲
            self.assertEqual(mock_sleep.call_count, 3)
        
        self.assertEqual(average, 30.0)
    
    def test_close(self):
        """測試感測器關閉功能"""
        self.hcsr04.close()
        self.mock_sensor.close.assert_called_once()

if __name__ == '__main__':
    unittest.main() 