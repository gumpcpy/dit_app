<!--
 * @Author: gumpcpy gumpcpy@gmail.com
 * @Date: 2024-10-29 18:37:21
 * @LastEditors: gumpcpy gumpcpy@gmail.com
 * @LastEditTime: 2024-10-29 18:46:19
 * @Description: 
-->
## 程式名稱 版本
    dit app
    v1.0 (2024-10-29)
    
## 程式目的
    QTake錄製的檔案名稱 Ex.[#sc_SHOT-0490_1_A] db14058e-000497-1.mov
    希望可以產生csv報表 把sc shot take note 以及識別mov檔案的檔名 
    可以選擇要不要複製一份檔案 以及直接改名
    
## 安裝方式
    如果是mac intel 芯片 則使用 setup_intel.sh
    如果是mac m1/m2 芯片 則使用 setup_m1m2.sh
    (要打開這兩個檔案的權限  chmod +x setup_m1m2.sh)
    會安裝 miniconda, 建立虛擬環境:dit, 安裝本專案需要的packages

## 使用方式
cd 進入有dit_app的目錄

    cd APP_PATH
    
啟動虛擬環境

    conda activate dit

執行程式

    python QT_QTakeOCR2CSV.py

    