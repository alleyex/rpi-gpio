# 5V 單通道繼電器模組（JQC-3FF-S-Z）

![Relay Module](JQC-3FF-S-Z(a).jpg)

## 簡介
本模組為 5V 單通道繼電器模組，適用於樹莓派、Arduino 等單板電腦或微控制器，可用於控制高壓/大電流設備。

## 規格限制
- 工作電壓：5V DC
- 控制訊號電壓：高電位觸發（建議 3.3V~5V）
- 最大切換電壓：250V AC / 30V DC
- 最大切換電流：10A（AC）/ 10A（DC）
- 建議負載不可超過標示最大值，長時間大電流建議降載使用

## 接線說明
- **VCC**：接 5V 電源
- **GND**：接地
- **IN**：訊號輸入腳，接至開發板 GPIO（可自訂腳位）
- **繼電器端子**：可接 AC/DC 負載

## 安裝方式
1. 安裝 Python 套件：
   ```bash
   pip install RPi.GPIO
   ```
2. 將 `jqc.py` 複製到你的專案目錄。

## 使用範例
```python
from jqc import RelayModule
import time

relay = RelayModule(17)  # 這裡可改成你要的 GPIO 腳位
relay.on()   # 啟動繼電器
print('Relay ON')
time.sleep(5)
relay.off()  # 關閉繼電器
print('Relay OFF')
relay.cleanup()
```

## 腳位可自訂
初始化 `RelayModule` 時，可傳入任意 GPIO 腳位編號，彈性控制。

## 注意事項
- 操作高壓（如市電）時，請務必注意人身安全，避免觸電危險。
- 請勿超過繼電器標示的最大電壓/電流（如10A 250VAC），以免損壞模組或引發危險。
- 樹莓派 GPIO 輸出為 3.3V，部分繼電器模組可能需要 5V 訊號，請確認模組支援 3.3V 邏輯或使用電平轉換。
- 切換大電流負載時，建議加裝保險絲或保護電路。
- 操作時請勿用手直接觸碰繼電器輸出端子。

---

如有問題歡迎提出！ 