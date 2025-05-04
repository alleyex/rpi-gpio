# DS18B20 溫度感測器

![DS18B20 溫度感測器](pic/DS18B20.jpg)

## 簡介

DS18B20 是一款數位溫度感測器，由 Maxim Integrated 公司生產。它使用 1-Wire 通訊協定，可以通過單一數據線進行通訊。

## 主要特點

- 測量範圍：-55°C 到 +125°C
- 精度：±0.5°C（-10°C 到 +85°C 範圍內）
- 數位輸出，無需額外的 ADC 轉換
- 每個感測器都有唯一的 64 位元序列號
- 可程式化解析度：9 到 12 位元
- 工作電壓：3.0V 到 5.5V

## 接線方式

DS18B20 通常有三個引腳：
1. GND：接地
2. DQ：數據線
3. VDD：電源（3.0V 到 5.5V）

## 樹莓派 5 設定步驟

### 1. 硬體連接
- 將 DS18B20 的 GND 連接到樹莓派的 GND
- 將 DS18B20 的 VDD 連接到樹莓派的 3.3V
- 將 DS18B20 的 DQ 連接到樹莓派的 GPIO4（或其他 GPIO 引腳）
- 在 DQ 和 3.3V 之間連接一個 4.7kΩ 的上拉電阻

### 2. 系統設定
1. 開啟終端機，編輯設定檔：
   ```bash
   sudo nano /boot/config.txt
   ```

2. 在檔案末尾添加以下行：
   ```
   dtoverlay=w1-gpio,gpio=4
   ```

3. 重新啟動樹莓派：
   ```bash
   sudo reboot
   ```

### 3. 測試感測器
1. 重新啟動後，檢查感測器是否被識別：
   ```bash
   ls /sys/bus/w1/devices/
   ```
   您應該會看到類似 `28-xxxxxxxxxxxx` 的目錄名稱

2. 讀取溫度數據：
   ```bash
   cat /sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave
   ```
   輸出中的 `t=` 後面的數字就是溫度值（需要除以 1000 得到攝氏溫度）

## 應用場景

- 環境監控
- 工業控制
- 溫度測量系統
- 物聯網（IoT）應用
- 智能家居系統

## 注意事項

- 在一般使用時需要接上拉電阻（通常為 4.7kΩ），但在樹莓派上使用時，由於 GPIO 引腳內部已有上拉電阻，通常不需要額外連接
- 在長距離傳輸時需要注意信號衰減
- 多個感測器可以並聯在同一條數據線上
- 確保樹莓派和 DS18B20 的電源供應穩定
- 每個 DS18B20 感測器在製造時就已經被賦予了唯一的 64 位元序列號，可以通過序列號來區分和讀取不同感測器的數據

### GPIO 引腳使用注意事項

1. 特殊功能引腳：
   - GPIO2 和 GPIO3 預設用於 I2C，雖可作為 GPIO 使用，但要小心與 I2C 裝置衝突
   - GPIO14 和 GPIO15 預設是 UART，使用前要確認不會干擾序列通訊

2. 電壓限制：
   - 不要把電壓超過 3.3V 的訊號直接接到 GPIO！
   - Raspberry Pi 的 GPIO 是 3.3V 容忍度，超過可能損壞 Pi

3. 建議使用的 GPIO 引腳：
   - GPIO4（預設）
   - GPIO17
   - GPIO18
   - GPIO22
   - GPIO23
   - GPIO24
   - GPIO25
   - GPIO27

4. 其他注意事項：
   - 使用前請確認 GPIO 引腳沒有被其他功能使用
   - 建議在 `/boot/config.txt` 中明確設定要使用的 GPIO 引腳
   - 修改設定後需要重新啟動樹莓派
   - 使用高速通訊或特殊協定（如 1-Wire）使用非預設 GPIO 引腳時，建議仍然連接 4.7kΩ 的上拉電阻

## TemperatureSensor 使用範例

### 基本使用

以下是一個使用 TemperatureSensor 類別的基本範例：

```python
from ds18 import TemperatureSensor

# 建立感測器實例（使用預設的 GPIO4）
sensor = TemperatureSensor()

# 或者指定其他 GPIO 引腳
sensor = TemperatureSensor(gpio_pin=17)  # 使用 GPIO17

# 讀取溫度
temperature, timestamp = sensor.read_temperature()
print(f"目前溫度：{temperature:.2f}°C")
print(f"讀取時間：{timestamp}")
```

### 進階使用

TemperatureSensor 類別提供了更多進階功能，例如重試機制和錯誤處理：

```python
from ds18 import TemperatureSensor
import time

# 建立感測器實例，設定重試參數和 GPIO 引腳
sensor = TemperatureSensor(
    gpio_pin=17,        # 使用 GPIO17
    retry_interval=2,   # 重試間隔為 2 秒
    max_retries=5       # 最多重試 5 次
)

try:
    while True:
        # 使用重試機制讀取溫度
        result = sensor.read_temperature_with_retry()
        
        if result is not None:
            temperature, timestamp = result
            print(f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] 溫度：{temperature:.2f}°C")
        else:
            print("無法讀取溫度，請檢查感測器連接")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n程式已停止")
```

### 類別方法說明

1. `__init__(gpio_pin=4, retry_interval=1, max_retries=3)`
   - 初始化感測器
   - `gpio_pin`: 使用的 GPIO 引腳編號（預設為 4）
   - `retry_interval`: 重試間隔時間（秒）
   - `max_retries`: 最大重試次數

2. `read_temperature()`
   - 讀取當前溫度
   - 返回：(溫度值, 時間戳記) 或 None

3. `read_temperature_with_retry()`
   - 使用重試機制讀取溫度
   - 在失敗時會自動重試
   - 返回：(溫度值, 時間戳記) 或 None

### 注意事項

1. 使用前請確保：
   - 已正確安裝 `w1thermsensor` 套件
   - 已正確設定 1-Wire 介面
   - 感測器已正確連接

2. 安裝必要套件：
   ```bash
   pip install w1thermsensor
   ```

3. 程式需要 root 權限執行：
   ```bash
   sudo python3 your_script.py
   ```

4. 錯誤處理：
   - 程式會自動處理感測器初始化失敗的情況
   - 提供詳細的錯誤訊息
   - 支援重試機制

5. 日誌記錄：
   - 程式會自動記錄重要事件
   - 包含時間戳記和錯誤訊息
   - 方便除錯和監控 