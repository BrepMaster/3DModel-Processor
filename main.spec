# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],  # 添加当前目录到路径
    binaries=[],
    datas=[
        # DGL 相关
        ('D:/anaconda3/envs/uvnet/Lib/site-packages/dgl', 'dgl'),

        # SciPy 相关
        ('D:/anaconda3/envs/uvnet/Lib/site-packages/scipy', 'scipy'),

        # VTK 相关 - 修正路径
        ('D:/anaconda3/envs/uvnet/Lib/site-packages/vtkmodules', 'vtkmodules'),
        ('D:/anaconda3/envs/uvnet/Lib/site-packages/vtk.libs', 'vtk.libs'),

        # 项目文件
        ('dataset_processor.py', '.'),
        ('ui_window.py', '.'),
        ('visualization.py', '.'),
        ('help_functions.py', '.'),
        ('model_processor.py', '.'),
        ('file_operations.py', '.'),
        ('graph_processor.py', '.'),
        ('statistics_analyzer.py', '.'),
        ('system_tools.py', '.')
    ],
    hiddenimports=[
        # 基础依赖
        'scipy', 'scipy.special', 'scipy.special._cdflib', 'scipy.special._ufuncs',
        'numpy', 'pandas',

        # DGL 相关
        'dgl', 'dgl.backend',

        # VTK 相关
        'vtkmodules',
        'vtkmodules.util',
        'vtkmodules.util.numpy_support',
        'vtkmodules.all',
        'vtkmodules.qt',

        # 项目模块
        'dataset_processor', 'ui_window', 'visualization',
        'help_functions', 'model_processor', 'file_operations',
        'graph_processor', 'statistics_analyzer', 'system_tools'
    ],
    hookspath=['hooks'],  # 钩子目录
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无命令行窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)