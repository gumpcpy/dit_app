#!/bin/bash
###
 # @Author: gumpcpy gumpcpy@gmail.com
 # @Date: 2024-10-29 18:32:00
 # @LastEditors: gumpcpy gumpcpy@gmail.com
 # @LastEditTime: 2024-10-31 04:19:39
 # @Description: 
 # 下載Mac M 芯片版本的 miniconda
 # 安裝虛擬環境 dit
 # 安裝需要的 packages
### 

# Set Var
MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
MINICONDA_PATH="$HOME/miniconda3"
ENV_NAME="dit"
REQUIREMENTS_FILE="requirements.txt"

# Check if Miniconda is installed
if [ -d "$MINICONDA_PATH" ]; then
    echo "Miniconda已經安裝在 $MINICONDA_PATH"
else
    echo "正在下載並安裝Miniconda..."
    curl -LO $MINICONDA_URL
    bash Miniconda3-latest-MacOSX-arm64.sh -b -p $MINICONDA_PATH
    rm Miniconda3-latest-MacOSX-arm64.sh
fi

# Initial conda
echo "正在初始化conda..."
source $MINICONDA_PATH/bin/activate
conda init zsh bash

# Check if env exist
if conda info --envs | grep -q $ENV_NAME; then
    echo "环境 $ENV_NAME 已存在,正在删除..."
    conda env remove -n $ENV_NAME -y
fi

# Create env
echo "正在建立env..."
conda create -n $ENV_NAME python=3.11 -y

# Activate env
echo "正在activate env..."
source $MINICONDA_PATH/bin/activate $ENV_NAME

# Install Requirements.txt 
echo "正在安装Requirement..."
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r $REQUIREMENTS_FILE
else
    echo "警告: $REQUIREMENTS_FILE 不存在。跳過安装"
fi

echo "安裝完成！现在可以使用 'conda activate $ENV_NAME' Activate Env"