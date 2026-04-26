# Camera Calibration Lab

一个用于练习相机标定的 Python 小项目，包含：

- 单目标定
- 双目标定
- 标定结果导出
- 角点检测可视化
- 去畸变预览
- 基础测试

项目默认使用棋盘格标定板，依赖 `OpenCV` 和 `NumPy`。

## 目录结构

```text
camera-calibration-lab/
  README.md
  environment.yml
  requirements.txt
  camera_calibration_lab/
    __init__.py
    boards.py
    cli.py
    io_utils.py
    mono.py
    stereo.py
    visualization.py
  tests/
    test_boards.py
    test_io_utils.py
    test_mono.py
    test_stereo.py
    test_visualization.py
```

## 安装依赖

### 使用 conda

```bash
conda env create -f environment.yml
conda activate camera-calibration-lab
```

### 使用 venv

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 数据组织

### 单目标定

```text
data/
  mono/
    left/
      001.jpg
      002.jpg
```

### 双目标定

```text
data/
  stereo/
    left/
      001.jpg
      002.jpg
    right/
      001.jpg
      002.jpg
```

左右图文件名需要一一对应。

## 参数说明

- `rows`：棋盘格内角点行数
- `cols`：棋盘格内角点列数
- `square-size`：单个方格边长，单位自定，推荐毫米

例如：

- 标定板内角点为 `6 x 9`
- 每格边长 `25mm`

则命令中填写：

- `--rows 6`
- `--cols 9`
- `--square-size 25.0`

## 单目标定

```bash
python -m camera_calibration_lab.cli mono ^
  --images data/mono/left ^
  --rows 6 ^
  --cols 9 ^
  --square-size 25.0 ^
  --output outputs/mono_left.json
```

命令完成后会输出：

- 总图片数
- 有效图片数
- 被跳过的图片数
- 重投影误差

## 双目标定

```bash
python -m camera_calibration_lab.cli stereo ^
  --left-images data/stereo/left ^
  --right-images data/stereo/right ^
  --rows 6 ^
  --cols 9 ^
  --square-size 25.0 ^
  --output outputs/stereo.json
```

命令完成后会输出：

- 总配对数
- 有效配对数
- 被跳过的配对数
- 立体标定误差

## 输出内容

单目标定输出：

- 相机内参矩阵
- 畸变系数
- 图像尺寸
- 重投影误差
- 总图片数 `total_images`
- 有效图片数 `valid_images`
- 参与标定的图片列表 `used_images`
- 被跳过的图片列表 `rejected_images`
- 标定板参数 `board`
- 输入目录 `image_dir`

双目标定输出：

- 左右相机内参矩阵
- 左右畸变系数
- 旋转矩阵 `R`
- 平移向量 `T`
- 本质矩阵 `E`
- 基础矩阵 `F`
- 立体标定误差
- 总配对数 `total_pairs`
- 有效配对数 `valid_pairs`
- 成功配对列表 `used_pairs`
- 失败配对列表 `rejected_pairs`
- 标定板参数 `board`
- 左右输入目录

标定阶段会校验所有有效样本的图像分辨率是否一致；如果混入不同尺寸图片，程序会直接报错并停止输出结果。

## 角点可视化

```bash
python -m camera_calibration_lab.cli visualize-corners ^
  --image assets/IMG_20260321_231713.jpg ^
  --rows 8 ^
  --cols 11 ^
  --square-size 1.5 ^
  --output outputs/corners_preview.jpg
```

输出图会直接把检测到的棋盘格角点绘制出来。

## 去畸变可视化

```bash
python -m camera_calibration_lab.cli visualize-undistort ^
  --image assets/IMG_20260321_231713.jpg ^
  --calibration outputs/mono_assets.json ^
  --output outputs/undistort_preview.jpg
```

输出图会将原图和去畸变结果横向拼接，便于直接对比。

## 批量导出角点结果

```bash
python -m camera_calibration_lab.cli batch-visualize-corners ^
  --images assets ^
  --rows 8 ^
  --cols 11 ^
  --square-size 1.5 ^
  --output-dir outputs/corners_batch ^
  --summary outputs/corners_batch_summary.json ^
  --visualize true
```

这个命令会：

- 遍历目录中的所有图片
- 为每张图导出一张带角点标注的结果图
- 生成一份汇总 JSON，标明每张图是否检测成功

如果你只想看每张图的 `true/false` 结果，不生成可视化图片：

```bash
python -m camera_calibration_lab.cli batch-visualize-corners ^
  --images assets ^
  --rows 8 ^
  --cols 11 ^
  --square-size 1.5 ^
  --output-dir outputs/corners_batch ^
  --summary outputs/corners_batch_summary.json ^
  --visualize false
```

## 运行测试

```bash
python -m unittest discover -s tests -v
```

## 当前验证结果

在项目环境 `D:\ProgramData\miniconda3\envs\camera-calibration-lab\python.exe` 下已验证：

- `python -m unittest discover -s tests -v` 通过
- `mono --images assets --rows 8 --cols 11 --square-size 1.5` 可正常输出结果
- `batch-visualize-corners --visualize false` 可正常生成摘要
- `visualize-undistort` 可正常导出去畸变对比图

## 后续可扩展

- 支持 ChArUco 标定板
- 支持保存去畸变结果
- 支持双目标定后的极线校正与视差图生成
- 支持 ROS 图像话题输入
