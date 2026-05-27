# Fire & Smoke Detection System

基于 YOLOv8m 的火灾与烟雾目标检测系统。在 D-Fire 数据集上训练（21,527 张图片），支持图片、视频和实时摄像头推理。

## 训练结果

**最佳模型**: `runs/detect/runs/detect/fire_smoke_yolov8m_20260526_2202/weights/best.pt`

| 指标 | 整体 | smoke | fire |
|:----:|:----:|:-----:|:----:|
| mAP@50 | **0.789** | 0.864 | 0.715 |
| mAP@50-95 | 0.468 | 0.549 | 0.387 |
| Precision | 0.797 | 0.844 | 0.749 |
| Recall | 0.725 | 0.808 | 0.642 |

**测试集 (test) 结果:**

| 指标 | 整体 | smoke | fire |
|:----:|:----:|:-----:|:----:|
| mAP@50 | **0.710** | 0.779 | 0.642 |
| Precision | 0.776 | 0.832 | 0.720 |
| Recall | 0.749 | 0.815 | 0.683 |

**推理速度** (RTX 5060 Ti, imgsz=640):

| 后端 | 延迟 | FPS |
|:----|:----:|:---:|
| PyTorch FP16 | 7.6 ms | 132 |
| TensorRT FP16 | 4.2 ms | 241 |

## 环境配置

```bash
# 激活 conda 环境
conda activate myPytorch

# 验证 GPU
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

| 组件 | 版本/规格 |
|------|-----------|
| Python | 3.9.23 |
| PyTorch | 2.9.0+cu128 |
| Ultralytics | 8.4.39 |
| GPU | NVIDIA GeForce RTX 5060 Ti (16 GB) |

## 数据集

[D-Fire Dataset](https://github.com/gaiasd/DFireDataset) — 21,527 张图片，26,557 个标注框。

| 类别 | ID | 训练集实例 | 测试集实例 |
|------|----|-----------|-----------|
| smoke | 0 | 9,550 | 2,315 |
| fire | 1 | 11,814 | 2,878 |

标注格式: YOLO (归一化坐标 .txt)。约 45.7% 的图像为负样本（无火灾/烟雾）。

### 目录结构

```
train/
  images/    (17,221 jpg)
  labels/    (17,221 txt)
test/
  images/    (4,306 jpg)
  labels/    (4,306 txt)
```

## 快速开始

### 1. 准备数据分割

```bash
# PowerShell (推荐)
& "D:\anaconda3\envs\myPytorch\python.exe" -u split_train_val.py
```

从训练集中按 90/10 比例分层分割出验证集，输出 `data/train.txt` 和 `data/val.txt`。

### 2. 训练

```bash
# YOLOv8m (推荐)
conda run -n myPytorch python train.py --model yolov8m.pt --config configs/train_yolov8m.yaml

# YOLOv8l (更高精度)
conda run -n myPytorch python train.py --model yolov8l.pt --config configs/train_yolov8l.yaml

# 从检查点恢复训练
conda run -n myPytorch python train.py --model yolov8m.pt --resume
```

训练日志和检查点保存在 `runs/detect/fire_smoke_*/` 下。

TensorBoard 监控：
```bash
tensorboard --logdir runs/detect
```

### 3. 评估

```bash
# 在测试集上评估
conda run -n myPytorch python val.py --model runs/detect/<experiment>/weights/best.pt --split test

# 在验证集上评估
conda run -n myPytorch python val.py --model runs/detect/<experiment>/weights/best.pt --split val

# 自定义阈值
conda run -n myPytorch python val.py --model best.pt --conf 0.3 --iou 0.5 --save-json
```

### 4. 推理

```bash
# 单张图片
conda run -n myPytorch python predict.py --model best.pt --source samples/input/fire1.jpg --save

# 图片目录
conda run -n myPytorch python predict.py --model best.pt --source test/images/ --save --save-json

# 视频
conda run -n myPytorch python predict.py --model best.pt --source video.mp4 --save

# 摄像头
conda run -n myPytorch python predict.py --model best.pt --source webcam --show
```

## 训练超参数

| 参数 | YOLOv8m | YOLOv8l |
|------|---------|---------|
| Batch size | 38 | 16 |
| Image size | 640 | 640 |
| Epochs | 100 (early stop @81) | 200 |
| Optimizer | SGD | SGD |
| Learning rate | 0.01 | 0.01 |
| LR schedule | Cosine | Cosine |
| Warmup epochs | 3 | 3 |
| Momentum | 0.937 | 0.937 |
| Weight decay | 0.0005 | 0.0005 |
| AMP | Enabled | Enabled |
| Mosaic | Epochs 0-10 | Epochs 0-10 |
| EMA | 0.9999 | 0.9999 |

## 模型导出

```bash
# ONNX (FP16)
conda run -n myPytorch python export_model.py --model best.pt --format onnx

# TensorRT (FP16)
conda run -n myPytorch python export_model.py --model best.pt --format engine --half

# ONNX + TensorRT + benchmark
conda run -n myPytorch python export_model.py --model best.pt --format all --benchmark
```

**TensorRT 推理速度**: 4.2 ms/张 (241 FPS) — 相比 PyTorch FP16 (7.6 ms, 132 FPS) 加速约 1.8 倍。

## 项目结构

```
├── data.yaml              # YOLO 数据集配置
├── split_train_val.py     # 训练/验证集分割
├── train.py               # 训练脚本
├── val.py                 # 评估脚本
├── predict.py             # 推理脚本
├── export_model.py        # ONNX/TensorRT 导出
├── configs/
│   ├── train_yolov8m.yaml
│   └── train_yolov8l.yaml
├── utils/
│   ├── dataset.py         # 数据集分析工具
│   └── visualization.py   # 结果可视化
├── data/
│   ├── train.txt          # 训练图像路径
│   └── val.txt            # 验证图像路径
├── samples/
│   ├── input/             # 推理测试图片
│   └── output/            # 推理结果
└── runs/                  # 训练输出（自动生成）
```

## 常见问题

**CUDA out of memory**: 减小 batch size (`--batch 16`) 或使用更小的模型变体。

**中文路径问题**: 所有脚本内部使用 `pathlib.Path` 处理路径，兼容中文路径。若遇到问题，确认文件编码为 UTF-8。

**训练中断恢复**: 使用 `--resume` 参数从最近检查点继续训练。

**TensorRT 导出失败**: 确保已安装 TensorRT (`pip install tensorrt`)，且 CUDA 版本匹配。若路径中含中文，TensorRT 的 C++ ONNX 解析器会因编码问题报错，可将模型复制到纯英文路径（如 `E:\best.pt`）后重新导出。

**TensorRT 引擎加载失败**: 预编译的 `.engine` 文件不受中文路径影响，可直接加载使用。
