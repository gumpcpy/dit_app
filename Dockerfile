FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install xattr

RUN pip install paddlepaddle==2.6.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install paddleocr==2.9.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

# RUN pip install paddle==1.0.2 -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install opencv-python-headless==4.10.0.84 -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install opencv-python==4.10.0.84 -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install opencv-contrib-python==4.10.0.84 -i https://pypi.tuna.tsinghua.edu.cn/simple

# RUN pip install --no-cache-dir PyQt5
#-i https://pypi.tuna.tsinghua.edu.cn/simple

# RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     python3-dev \
#     qt5-default \
#     && rm -rf /var/lib/apt/lists/*


#python py/QTakeMovHD/QTakeRawNameMapping.py 
#docker run -v /Users/gump/Documents/_Proj/dc_qvh:/app -it  dit_app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .
CMD ["bash"]

# 運行程序
# CMD ["python", "your_script_name.py"]

# 構建Docker鏡像:
# 在包含Dockerfile的目錄中運行以下命令:
# docker build -t your-image-name .
# docker build -t dit_app .

# 運行Docker容器:
# 構建完成後,可以使用以下命令運行容器:
# docker run -it --rm -v /path/to/input/folder:/app/input -v /path/to/output/folder:/app/output ocr-vfx-app


# "registry-mirrors": [
# "https://docker.rainbond.cc",
# "https://registry.hub.docker.com",
# "http://hubmirror.c.163.com",
# "https://docker.mirrors.ustc.edu.cn",
# "https://registry.docker-cn.com"
# ]