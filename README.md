<!--
 * @Author: gumpcpy gumpcpy@gmail.com
 * @Date: 2024-10-29 18:37:21
 * @LastEditors: gumpcpy gumpcpy@gmail.com
 * @LastEditTime: 2024-10-31 04:58:49
 * @Description: 
-->
## 程式名稱 版本
    dit app
    v1.0 (2024-10-29)
    
## 程式目的
    QTakeOCR2CSV
        的目的是可以指定一個folder，程式會辨識左下角的卡號，以及解析QTake MOV的檔名和標籤顏色
        然後生成一個 csv檔案，放在folder裡面。
        有兩個可選項：複製一份原始的檔名的mov到跟他同級的目錄 Ex 20241030 會複製到 20241030_BK
        以免改變檔名之後發生同檔名覆蓋。
        另一個選項是修改選擇的folder的檔名。

        QTake錄製的檔案名稱 Ex.[#sc_SHOT-0490_1_A] db14058e-000497-1.mov
        csv報表 原本的QTake檔名 sc shot take note 以及OCR識別mov獲取的檔名 
        可以選擇要不要複製一份檔案 以及直接改名

    WatchFolder
        執行此程式，可選擇一個folder聆聽，如果有新的mov出現在這個folder裡面，就將它複製一份原始擋備份，
        然後改名字。
    
    有兩種版本，一種是有視窗的 QTakeOCR2CSV_QT 以及 WatchFolder_QT
    一種是沒有視窗界面顯示的 QTakeOCR2CSV 以及 WatchFolder
    執行方式一樣: Ex.
    python WatchFolder

## 安裝方式 
### (1) 在本機用miniconda 安裝環境
    如果是mac intel 芯片 則使用 setup_intel.sh
    如果是mac m1/m2 芯片 則使用 setup_m1m2.sh
    (要打開這兩個檔案的權限  chmod +x setup_m1m2.sh)
    會安裝 miniconda, 建立虛擬環境:dit, 安裝本專案需要的packages

### (2) 用 Docker 
    安裝Docker
    docker pull dit_app
    docker run -it --rm -v YOUR_FOLDER_PATH:/app/input dit_app
    表示 把 YOUR_FOLDER_PATH 掛載到 虛擬機的/input 路徑。
    
    Docker要用的程式版本是沒有視窗的版本
## 使用方式
cd 進入有dit_app的目錄

    cd YOUR_APP_PATH
    
啟動虛擬環境

    conda activate dit

執行程式

    python QTakeOCR2CSV.py    
    python WatchFolder.py
    python QTakeOCR2CSV_QT.py    
    python WatchFolder_QT.py

    