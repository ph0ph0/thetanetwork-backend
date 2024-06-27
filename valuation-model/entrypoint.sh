#!/bin/bash

# Check for NVIDIA GPU
if command -v nvidia-smi &> /dev/null
then
    echo "NVIDIA GPU detected, installing CUDA-based PyTorch"
    pip install torch==1.7.1+cu110 torchvision==0.8.2+cu110 -f https://download.pytorch.org/whl/torch_stable.html
else
    echo "No NVIDIA GPU detected, installing CPU-based PyTorch"
    pip install torch==1.7.1 torchvision==0.8.2
fi

# Install CLIP
pip install git+https://github.com/openai/CLIP.git

# Run the application
exec python src/main.py
