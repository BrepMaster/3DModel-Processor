# 3D Model Processing and Visualization Tool / 3D模型处理与可视化工具

**3D Model Processing and Visualization Tool** is an integrated data processing platform for intelligent manufacturing. It provides end-to-end solutions from raw CAD models to deep learning-ready data, supporting:  
**3D模型处理与可视化工具**是一款面向智能制造的集成化数据处理平台。该工具提供从原始CAD模型到深度学习就绪数据的全流程解决方案，支持：

1) 3D model processing (STEP/STL format conversion, high-precision point cloud sampling, multi-view rendering and BREP feature extraction)  
   三维模型处理（STEP/STL格式互转、高精度点云采样、多视角渲染及BREP特征提取）

2) Smart dataset management (automatic train/validation split, intelligent file organization, data distribution visualization)  
   智能数据集管理（自动划分训练/验证集、智能文件归类、数据分布可视化分析）

3) Graph neural network data construction (BREP-based UV mesh graph generation, graph structure feature statistics)  
   图神经网络数据构建（基于BREP的UV网格图数据生成、图结构特征统计）

4) Interactive visualization (real-time 3D model rendering, feature distribution heatmaps, graph topology display)  
   交互式可视化（三维模型实时渲染、数据特征分布热力图、图结构拓扑展示）

Ideal for: Intelligent mechanical design (CAD/CAM), industrial visual inspection, 3D deep learning scenarios  
特别适用于：机械设计智能化（CAD/CAM）、工业视觉检测、三维深度学习等场景

![image-20250701095628547](https://github.com/BrepMaster/3DModel-Processor\1.png)

## Features / 功能特性

### Dataset Processing Module / 数据集处理模块

- Split dataset into training and test sets / 划分数据集为训练集和测试集
- Classify files into subfolders by filename / 根据文件名将文件分类到子文件夹
- Extract files by extension to target directory / 按后缀提取文件到目标目录
- Count files in subfolders / 统计子文件夹中的文件数量
- Delete large files (by size threshold) / 删除大文件（按大小阈值）
- Delete folders (with file count below threshold) / 删除文件夹（文件数小于设定阈值）
- Organize dataset according to txt file / 根据txt文件组织数据集
- Analyze dataset balance / 分析数据集平衡性
- Delete files by specified extension / 删除指定后缀的文件
- Compare differences between two paths / 对比两个路径差异

### Graph Data Processing Module / 图数据处理模块

- Load single graph file / 加载单个图文件
- Find file with max points/edges in path / 统计路径下最大点/边数量的文件
- Statistics by category in path / 统计路径下每个类别的信息

### 3D Model Processing Module / 3D模型处理模块

- STEP to STL conversion / STEP转STL格式转换
- STL to point cloud sampling / STL转点云采样
- STL to multi-view conversion / STL转多视图
- STEP to DGL graph structure / STEP转DGL图结构

### Visualization Module / 可视化模块

- Dataset category distribution visualization / 数据集类别分布可视化
- Graph structure information visualization / 图结构信息可视化
- 3D model and point cloud visualization / 3D模型和点云可视化

### System Tools / 系统工具

- Log analysis / 日志分析
- System resource monitoring / 系统资源监控

## Usage / 使用说明

### Run Application / 运行应用

```bash
python main.py
```

### Package Project / 项目打包

```bash
pyinstaller main.spec
```

## Project Structure / 项目结构

```
├── file_operations.py        # File operations / 文件操作
├── dataset_processor.py      # Dataset processing / 数据集处理
├── model_processor.py        # 3D model processing / 3D模型处理
├── graph_processor.py        # Graph data processing / 图数据处理
├── statistics_analyzer.py    # Statistical analysis / 统计分析
├── visualization.py          # Visualization / 可视化
├── system_tools.py           # System tools / 系统工具
├── help_functions.py         # Help documentation / 帮助文档
├── main.py                   # Main entry / 主入口
├── application.log           # Runtime logs / 运行日志
└── main.spec                 # Packaging config / 打包配置
```

## Contribution / 参与贡献

1. Fork the project / Fork本项目
2. Create feature branch (`git checkout -b feature/newfeature`) / 创建特性分支
3. Commit changes (`git commit -m 'Add new feature'`) / 提交更改
4. Push to branch (`git push origin feature/newfeature`) / 推送到分支
5. Create Pull Request / 创建Pull Request

## License / 许可证

MIT License

## Contact / 联系方式

For questions please contact me.
