# 基于 YOLOv8m 的火灾与烟雾实时检测系统

## 摘要

火灾是威胁人民生命财产安全的主要灾害之一，早期检测与预警对于火灾防控至关重要。本文提出并实现了一套基于 YOLOv8m (You Only Look Once version 8 medium) 的火灾与烟雾实时检测系统。该系统在 D-Fire 公开数据集上进行训练与评估，采用迁移学习策略从 COCO 预训练权重初始化模型参数。实验结果表明，模型在测试集上达到了 71.0% 的 mAP@50 和 42.1% 的 mAP@50-95，其中烟雾类别的检测精度 (84.4%) 显著高于火焰类别 (74.9%)。为满足实际部署需求，本文进一步设计了完整的 Web 应用系统，采用 FastAPI 后端与 React 前端架构，支持图像、视频及实时摄像头的多模态检测，并提供了 TensorRT 推理加速能力，在 NVIDIA RTX 5060 Ti 上可达 241 FPS 的推理速度。该系统兼具高检测精度与实时性能，为火灾预警提供了一套完整的技术解决方案。

**关键词**: 火灾检测；烟雾检测；YOLOv8m；目标检测；深度学习；实时推理

---

## 1. 引言

火灾是一种发生频率高、破坏性强的灾害，对生态环境、社会经济和人民安全构成严重威胁。根据应急管理部的统计，中国每年发生数十万起火灾事故，造成了大量人员伤亡和财产损失。传统的火灾检测主要依赖感烟传感器、感温传感器等物理探测设备，这些方法存在响应延迟大、覆盖范围有限、易受环境干扰等局限性。

随着计算机视觉和深度学习技术的快速发展，基于视频图像的火灾检测方法逐渐成为研究热点。相比于传统传感器，视觉检测具有响应速度快、覆盖范围广、可提供空间位置信息等优势。然而，火灾与烟雾的视觉检测也面临诸多挑战：(1) 火焰形态多变，颜色和纹理差异大；(2) 烟雾呈半透明状，边界模糊难以定位；(3) 复杂背景中的类火焰物体（如灯光、反射）易造成误报；(4) 实际应用对实时性有较高要求。

YOLO (You Only Look Once) [1] 系列模型作为单阶段目标检测算法的代表，以其优异的检测速度与精度的平衡著称。YOLOv8 [2] 作为 Ultralytics 在 2023 年发布的最新版本，在检测头、损失函数和训练策略等方面进行了全面改进。本文选取 YOLOv8m (medium) 版本，在保证检测精度的同时兼顾推理速度，旨在构建一套高精度、实时可用的火灾与烟雾检测系统。

本文的主要贡献包括：

- 在 D-Fire 数据集上系统性地训练和评估了 YOLOv8m 模型，分析了不同类别的检测性能差异；
- 设计了完整的后端-前端 Web 应用系统，支持图像、视频和实时摄像头的多模态检测；
- 实现了 TensorRT 推理加速，极大提升了模型在实际场景中的部署性能；
- 构建了完整的历史记录管理、数据分析与可视化功能，便于实际应用中的回溯与决策支持。

---

## 2. 相关工作

### 2.1 传统火灾检测方法

传统的火灾检测方法主要基于物理传感器，包括感烟式、感温式、感光式和气体传感器式。这些方法通过监测环境中的烟雾浓度、温度变化、特定光谱辐射或燃烧产生的化学物质来判定火灾是否发生 [3]。尽管这些方法技术成熟、成本较低，但存在明显的局限性：响应时间较长（需要烟雾或热量扩散到传感器位置）、覆盖范围有限（点式检测）、在开阔空间或高大空间中效果不佳。

基于图像处理的技术也被广泛应用于早期火灾检测，主要利用火焰和烟雾的颜色、纹理、运动和形状特征 [4]。常用方法包括颜色空间变换（如 RGB 到 HSV、YCbCr）、背景减除法、光流法以及小波变换等。然而，这些手工特征的方法在面对复杂环境时鲁棒性不足，难以适应多样化的火灾场景。

### 2.2 基于深度学习的火灾检测

近年来，卷积神经网络 (CNN) 在目标检测领域取得了突破性进展。基于深度学习的目标检测方法主要分为两阶段和单阶段两大类。两阶段方法以 Faster R-CNN [5] 为代表，首先生成候选区域，再进行分类与回归，精度较高但速度较慢。单阶段方法以 YOLO [1] 和 SSD [6] 为代表，直接在特征图上预测类别和位置，实现了端到端的快速检测。

在火灾检测领域，研究者们对多种深度学习模型进行了探索。Frizzi 等人 [7] 提出基于 CNN 的火灾检测方法，在视频帧上进行逐帧分类。Muhammad 等人 [8] 提出了基于 SqueezeNet 的轻量级火灾检测网络。Li 等人 [9] 对 YOLOv5 进行改进用于火灾检测。D-Fire 数据集 [10] 的提出为火灾和烟雾检测提供了标准化的评估基准，促进了该领域的研究发展。

### 2.3 YOLOv8 架构

YOLOv8 [2] 是 Ultralytics 在 2023 年发布的目标检测框架，在 YOLOv5 的基础上进行了多项重要改进。其核心架构包括：

- **骨干网络 (Backbone)**：采用 CSPDarknet 结构，通过跨阶段局部连接 (Cross Stage Partial) 提高梯度流动效率，减少计算量。
- **颈部网络 (Neck)**：使用 FPN+PAN (特征金字塔网络 + 路径聚合网络) 结构，实现多尺度特征的融合。
- **检测头 (Head)**：采用解耦检测头 (Decoupled Head)，将分类和回归任务分离到不同的分支，提高收敛速度和检测精度。
- **损失函数**：分类损失使用二元交叉熵损失 (BCE Loss)，回归损失使用 CIoU (Complete IoU) 损失和 DFL (Distribution Focal Loss) [11] 的组合。
- **无锚框检测 (Anchor-Free)**：YOLOv8 采用无锚框设计，直接在特征图上的每个位置预测目标，减少了超参数和先验框的依赖。

YOLOv8 提供 n、s、m、l、x 多种规格，其中 m (medium) 版本在速度与精度之间取得了良好的平衡，适合作为火灾检测的基础模型。

---

## 3. 方法

### 3.1 数据集

本研究采用 D-Fire 数据集 [10] 进行模型的训练与评估。D-Fire 是一个专门用于火灾和烟雾检测的公开数据集，由来自多个来源的图像组成，涵盖森林火灾、建筑火灾、工业火灾等多种场景。

数据集的基本统计信息如下：

| 属性 | 数值 |
|---|---|
| 总图像数 | 21,527 张 |
| 总标注框数 | 26,557 个 |
| 类别数 | 2 (fire, smoke) |
| 负样本比例 | ~45.7% |
| 训练集 | 17,221 张 |
| 测试集 | 4,306 张 |

数据集的划分遵循官方提供的训练/测试划分方案，并进一步从训练集中按 90:10 分层抽样出验证集，确保各类别在验证集中的比例与训练集一致。

### 3.2 模型与训练配置

**基础模型**: 采用 YOLOv8m 作为检测模型，使用在 COCO 数据集上预训练的权重进行迁移学习初始化。YOLOv8m 包含约 25.9M 参数，在检测精度与推理速度之间具有良好的平衡。

**训练超参数**:

| 参数 | 取值 |
|---|---|
| 图像尺寸 | 640 × 640 |
| 批量大小 (batch size) | 38 |
| 优化器 | SGD |
| 初始学习率 (lr0) | 0.01 |
| 最终学习率 (lrf) | 0.01 |
| 动量 (momentum) | 0.937 |
| 权重衰减 (weight decay) | 0.0005 |
| 学习率调度 | 余弦退火 (Cosine Annealing) |
| 预热轮数 (warmup epochs) | 3 |
| 总训练轮数 (epochs) | 100 |
| 早停轮数 (patience) | 81 |
| 混合精度训练 (AMP) | 启用 |
| 指数移动平均 (EMA) | 启用 (decay=0.9999) |
| 随机种子 | 42 |

**数据增强策略**: 训练过程中应用了多种数据增强技术以提升模型的泛化能力：

- **HSV 色彩抖动**: H=0.015, S=0.7, V=0.4
- **平移 (Translation)**: ±10%
- **缩放 (Scale)**: ±50%
- **水平翻转 (Flip)**: 50% 概率
- **马赛克增强 (Mosaic)**: 100% 概率 (前 10 个 epoch 后关闭)

**损失函数配置**:

| 损失项 | 权重 |
|---|---|
| 边框回归损失 (box) | 7.5 |
| 分类损失 (cls) | 0.5 |
| 分布聚焦损失 (dfl) | 1.5 |

### 3.3 训练流程

模型训练的完整流程如下：

1. **数据准备**: 将 D-Fire 数据集转换为 YOLO 格式，确保类别映射为 0 (fire) 和 1 (smoke)
2. **权重初始化**: 加载 COCO 预训练的 YOLOv8m 权重作为初始参数
3. **模型训练**: 使用 SGD 优化器和余弦退火学习率调度进行 100 轮训练，前 3 轮进行学习率预热
4. **早停策略**: 当验证集上的 mAP@50 在连续指定轮数内不再提升时停止训练
5. **模型选择**: 保存验证集上性能最佳的模型权重 (best.pt)
6. **模型导出**: 将最佳模型导出为 ONNX (FP16) 和 TensorRT FP16 engine 格式

### 3.4 推理加速

为满足实时检测需求，本文对训练好的模型进行了推理加速优化：

1. **ONNX 导出**: 将 PyTorch 模型导出为 ONNX 格式，FP16 精度，支持动态批处理
2. **TensorRT 优化**: 在 ONNX 基础上进一步优化为 TensorRT FP16 engine，利用 layer fusion、kernel auto-tuning 和内存优化等技术
3. **推理序列化**: 在 Web 服务中，通过 asyncio.Lock 和 ThreadPoolExecutor 确保 GPU 推理的线程安全

---

## 4. 系统架构设计

本文设计的火灾与烟雾检测系统采用前后端分离的 Web 架构，整体系统架构如图 1 所示。

```
+-------------------+       +---------------------+       +----------------+
|                   |  REST |                     |  SQL  |                |
|   React 前端      |<----->|   FastAPI 后端       |<----->|   SQLite 数据库  |
|   (TypeScript)    |  API  |   (Python)          |       |                |
|                   |       |                     |       +----------------+
|  - 仪表盘         |       |  - 检测服务          |
|  - 图像检测        |       |  - 图像/视频处理      |
|  - 视频检测        |       |  - GPU 推理 (YOLO)   |
|  - 历史记录        |       |  - 统计服务          |
+-------------------+       +---------------------+
                                   |
                          +-------------------+
                          |   NVIDIA GPU       |
                          |  (RTX 5060 Ti)     |
                          |  TensorRT / PyTorch |
                          +-------------------+
```

### 4.1 后端服务

后端基于 FastAPI 框架构建，采用异步编程 (asyncio) 模型，充分发挥 Python 的 I/O 并发能力。主要模块包括：

- **检测服务 (Detector Service)**: 模型加载与推理的核心组件，采用线程安全的单例模式管理模型实例，优先加载 TensorRT engine，失败时回退至 PyTorch
- **图像处理服务 (Image Service)**: 处理图像上传、模型推理、结果可视化（绘制边界框）、缩略图生成等
- **视频处理服务 (Video Service)**: 异步处理视频文件，按帧步长进行抽帧检测，生成带有检测标注的输出视频和检测时间线
- **文件服务 (File Service)**: 负责文件上传验证、磁盘存储、路径管理
- **数据库服务 (DB Service)**: 基于 SQLAlchemy 异步 ORM 的历史记录持久化
- **统计服务 (Stats Service)**: 基于数据库聚合查询的统计分析与仪表盘数据生成

### 4.2 前端应用

前端采用 React 18 + TypeScript + Vite 构建，使用 Tailwind CSS 进行样式管理，暗色模式默认。主要功能页面包括：

- **仪表盘 (Dashboard)**: 展示系统运行状态、检测统计概览、类别分布和最近检测活动
- **图像检测 (Image Detection)**: 支持拖放上传，提供置信度/IoU 阈值调节滑块，结果支持标注视图和并排对比
- **视频检测 (Video Detection)**: 异步视频处理，支持进度轮询，结果播放器附带检测时间线柱状图
- **历史记录 (History)**: 支持分页、筛选、搜索和删除的历史管理功能

### 4.3 数据库设计

系统使用 SQLite 作为持久化存储，主要表结构如下：

**detection_records** (检测记录):
- id (UUID 主键), type (image/video), filename
- original_path, annotated_path, thumbnail_path
- image_width, image_height
- total_count, smoke_count, fire_count, max_confidence
- processing_time_ms, created_at

**detection_results** (检测结果):
- id (自增主键), record_id (外键，级联删除)
- class_id, class_name, confidence
- bbox_x1, bbox_y1, bbox_x2, bbox_y2
- frame_index, timestamp_sec

### 4.4 API 设计

后端提供 RESTful API 接口，主要端点如下：

| 端点 | 方法 | 功能 |
|---|---|---|
| `/api/health` | GET | 系统健康检查，返回 GPU 和模型状态 |
| `/api/detect/image` | POST | 图像检测 (文件上传) |
| `/api/detect/video` | POST | 视频检测提交 (异步处理) |
| `/api/detect/video/{task_id}` | GET | 视频检测任务状态轮询 |
| `/api/stats` | GET | 仪表盘统计数据 |
| `/api/history` | GET | 分页历史记录查询 |
| `/api/history/{record_id}` | GET | 单条记录详情 |
| `/api/history/{record_id}` | DELETE | 删除记录 |

---

## 5. 实验结果与分析

### 5.1 评估指标

本文采用目标检测领域的标准评估指标：

- **Precision (精确率)**: $Precision = \frac{TP}{TP + FP}$
- **Recall (召回率)**: $Recall = \frac{TP}{TP + FN}$
- **mAP@50**: IoU 阈值为 0.5 时的平均精度均值 (mean Average Precision)
- **mAP@50-95**: IoU 阈值从 0.5 到 0.95 (步长 0.05) 的 mAP 平均值

### 5.2 训练集评估结果

模型在训练完成后，在验证集上的评估结果如下：

| 指标 | 总体 | smoke | fire |
|---|---|---|---|
| mAP@50 | **0.789** | 0.864 | 0.715 |
| mAP@50-95 | 0.468 | 0.549 | 0.387 |
| Precision | 0.797 | 0.844 | 0.749 |
| Recall | 0.725 | 0.808 | 0.642 |

从结果可以看出：(1) 烟雾类别的检测性能整体优于火焰类别，这可能是由于烟雾在图像中占据的像素面积通常更大、特征更明显；(2) 火焰类别的召回率较低 (64.2%)，说明模型对于小面积或形态不典型的火焰存在漏检问题；(3) mAP@50-95 相比 mAP@50 有较大下降，说明检测框的定位精度仍有提升空间。

### 5.3 测试集评估结果

在官方 D-Fire 测试集上的评估结果如下：

| 指标 | 数值 |
|---|---|
| mAP@50 | 0.710 |
| mAP@50-95 | 0.421 |
| Precision | 0.776 |
| Recall | 0.749 |

测试集性能相比验证集有所下降，属于正常现象，下降幅度在可接受范围内。

### 5.4 推理性能

在 NVIDIA GeForce RTX 5060 Ti (16GB VRAM) 上对不同推理后端的性能进行了对比测试 (输入尺寸 640×640)：

| 推理后端 | 精度 | 延迟 | FPS |
|---|---|---|---|
| PyTorch | FP16 | 7.6 ms | 132 |
| TensorRT | FP16 | 4.2 ms | 241 |

TensorRT 推理加速效果显著，相较于原生 PyTorch 推理，延迟降低了 44.7%，吞吐量提升了 82.6%。这主要得益于 TensorRT 的算子融合、内存优化和自动调优等编译优化技术。

### 5.5 检测效果分析

系统在实际图像和视频样本上的检测效果分析如下：

- **大尺度目标**: 对于占据较大画面比例的火焰或烟雾区域，模型能够稳定检测，置信度通常高于 0.7
- **小尺度目标**: 对于远处或面积较小的火焰，模型检测置信度有所下降，偶有漏检
- **光照条件**: 在正常光照和弱光条件下均能保持较好的检测性能
- **负样本**: 对于无火灾/烟雾的图像，模型的误报率较低，显示出良好的区分能力
- **视频检测**: 在连续视频帧上，检测结果具有较好的时序一致性，无明显抖动

---

## 6. 结论与展望

### 6.1 工作总结

本文设计并实现了一套基于 YOLOv8m 的火灾与烟雾实时检测系统，主要工作包括：

1. 以 YOLOv8m 为骨干网络，在 D-Fire 数据集上训练了火灾与烟雾检测模型，mAP@50 达到 71.0%，实现了可靠的检测性能；
2. 设计了完整的 Web 应用系统，采用 FastAPI + React 前后端分离架构，支持图像、视频等多种检测模式；
3. 实现了 TensorRT 推理加速，推理延迟低至 4.2 ms (241 FPS)，满足实时检测需求；
4. 构建了历史记录管理和统计分析功能，为实际应用提供了完整的数据支持。

### 6.2 存在的不足

尽管本系统在检测性能和系统功能方面均取得了较好的效果，但仍存在以下不足：

1. 火焰类别的小目标检测性能仍有提升空间，召回率偏低；
2. 数据集主要包含开阔场景的火灾图像，对于室内、隧道等特殊场景的适应性尚未充分验证；
3. 系统尚未针对边缘计算设备进行适配和优化；
4. 缺乏多摄像头协同检测与时空融合机制。

### 6.3 未来工作展望

基于现有工作的不足，未来可在以下方向进行改进和拓展：

1. **模型优化**: 引入注意力机制 (如 CBAM、GAM) 或多尺度特征增强模块，提升小目标检测能力；
2. **数据集扩展**: 收集更多室内、城市等场景的火灾数据，提高模型的场景适应性；
3. **边缘部署**: 针对 Jetson 等边缘设备进行模型量化和部署优化；
4. **多模态融合**: 结合红外热成像等多模态信息，提高检测的鲁棒性和全天候工作能力；
5. **跟踪与预警**: 集成目标跟踪算法 (如 ByteTrack)，实现火灾蔓延趋势分析和智能预警决策；
6. **持续学习**: 实现在线增量学习机制，使模型能够在部署后持续适应新场景。

---

## 参考文献

[1] Redmon, J., Divvala, S., Girshick, R., & Farhadi, A. (2016). You Only Look Once: Unified, Real-Time Object Detection. *Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*.

[2] Ultralytics. (2023). YOLOv8: A State-of-the-Art Real-Time Object Detector. https://github.com/ultralytics/ultralytics

[3] Fonollosa, J., Solórzano, A., & Marco, S. (2018). Chemical Sensor Systems and Associated Algorithms for Fire Detection: A Review. *Sensors*, 18(2), 553.

[4] Çelik, T., & Demirel, H. (2009). Fire Detection in Video Sequences Using a Generic Color Model. *Fire Safety Journal*, 44(2), 147-158.

[5] Ren, S., He, K., Girshick, R., & Sun, J. (2015). Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks. *Advances in Neural Information Processing Systems (NeurIPS)*.

[6] Liu, W., Anguelov, D., Erhan, D., Szegedy, C., Reed, S., Fu, C. Y., & Berg, A. C. (2016). SSD: Single Shot MultiBox Detector. *European Conference on Computer Vision (ECCV)*.

[7] Frizzi, S., Kaabi, R., Bouchouicha, M., Ginoux, J. M., Moreau, E., & Fnaiech, F. (2016). Convolutional Neural Network for Video Fire and Smoke Detection. *IECON 2016 - 42nd Annual Conference of the IEEE Industrial Electronics Society*.

[8] Muhammad, K., Ahmad, J., & Baik, S. W. (2018). Early Fire Detection Using Convolutional Neural Networks and Surveillance Video. *IEEE Access*, 6, 49790-49801.

[9] Li, P., & Zhao, W. (2020). Image Fire Detection Algorithms Based on Convolutional Neural Networks. *Case Studies in Thermal Engineering*, 19, 100625.

[10] D-Fire Dataset. https://github.com/gaiasd/DFireDataset

[11] Li, X., Wang, W., Wu, L., Chen, S., Hu, X., Li, J., Tang, J., & Yang, J. (2020). Generalized Focal Loss: Learning Qualified and Distributed Bounding Boxes for Dense Object Detection. *Advances in Neural Information Processing Systems (NeurIPS)*.
