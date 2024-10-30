#!/bin/bash

# 设置变量
MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
MINICONDA_PATH="$HOME/miniconda3"
ENV_NAME="dit"
REQUIREMENTS_FILE="requirements.txt"

# 检查Miniconda是否已安装
if [ -d "$MINICONDA_PATH" ]; then
    echo "Miniconda已经安装在 $MINICONDA_PATH"
else
    echo "正在下载并安装Miniconda..."
    curl -LO $MINICONDA_URL
    bash Miniconda3-latest-MacOSX-arm64.sh -b -p $MINICONDA_PATH
    rm Miniconda3-latest-MacOSX-arm64.sh
fi

# 初始化conda
echo "正在初始化conda..."
source $MINICONDA_PATH/bin/activate
conda init zsh bash

# 检查虚拟环境是否存在
if conda info --envs | grep -q $ENV_NAME; then
    echo "环境 $ENV_NAME 已存在,正在删除..."
    conda env remove -n $ENV_NAME -y
fi

# 创建虚拟环境
echo "正在创建虚拟环境..."
conda create -n $ENV_NAME python=3.11 -y

# 激活虚拟环境
echo "正在激活虚拟环境..."
source $MINICONDA_PATH/bin/activate $ENV_NAME

# 安装requirements.txt中的包
echo "正在安装所需的包..."
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r $REQUIREMENTS_FILE
else
    echo "警告: $REQUIREMENTS_FILE 文件不存在。跳过包安装。"
fi

echo "安装完成！您现在可以使用 'conda activate $ENV_NAME' 来激活环境。"