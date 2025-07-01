"""
帮助功能模块
包含所有工具功能的帮助信息
"""

def get_data_processing_help(mode: str) -> str:
    """获取数据集处理功能的帮助信息"""
    help_texts = {
        '划分数据集': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">划分数据集功能说明</h2>
                <p>将输入目录中的数据集按类别划分为训练集和测试集</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录（应包含按类别组织的子文件夹）</li>
                    <li>设置测试集比例（0-1之间的小数）</li>
                    <li>选择输出目录</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                <p>在输出目录生成train.txt和test.txt文件，包含训练集和测试集文件名列表</p>
            </div>
            """,
        '根据文件名划分到子文件夹': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">文件名分类功能说明</h2>
                <p>根据文件名中的前缀将文件分类到不同子文件夹</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录（包含要分类的文件）</li>
                    <li>选择输出目录</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">文件名格式要求</h3>
                <p>文件名应包含下划线分隔的前缀（如"cat_001.jpg"），文件将按前缀分类到不同子文件夹</p>
            </div>
            """,
        '按后缀提取文件到目标目录': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">按后缀提取功能说明</h2>
                <p>从输入目录及其子目录中提取指定后缀的文件到目标目录</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录</li>
                    <li>设置要提取的文件后缀（多个后缀用逗号分隔，如".jpg,.png"）</li>
                    <li>选择输出目录</li>
                    <li>点击"开始处理"</li>
                </ol>
            </div>
            """,
        '统计子文件夹中的文件数量': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">文件统计功能说明</h2>
                <p>统计输入目录中各子文件夹的文件数量</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录</li>
                    <li>可选：设置要统计的文件后缀（默认统计所有文件）</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                <p>显示每个子文件夹的文件数量和总文件数</p>
            </div>
            """,
        '删除大文件（按大小）': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">删除大文件功能说明</h2>
                <p>删除输入目录中超过指定大小的文件</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录</li>
                    <li>设置大小阈值（MB）</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #e74c3c; margin-top: 15px; margin-bottom: 5px;">注意</h3>
                <p>此操作不可逆，请谨慎使用！</p>
            </div>
            """,
        '删除文件夹（文件数小于阈值）': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">删除空文件夹功能说明</h2>
                <p>删除文件数量小于阈值的文件夹</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录</li>
                    <li>设置文件数量下限</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #e74c3c; margin-top: 15px; margin-bottom: 5px;">注意</h3>
                <p>此操作不可逆，请谨慎使用！</p>
            </div>
            """,
        '根据txt文件组织数据集': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">根据txt文件组织数据集功能说明</h2>
                <p>根据train.txt和test.txt文件将文件组织到train和test文件夹中</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录（应包含按类别组织的子文件夹）</li>
                    <li>选择train.txt文件（包含训练集文件名列表）</li>
                    <li>选择test.txt文件（包含测试集文件名列表）</li>
                    <li>选择输出目录</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                <p>在输出目录中创建与输入目录相同的结构，但每个子文件夹下会有train和test子文件夹，分别包含对应的文件</p>
            </div>
            """,
        '分析数据集平衡性': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">数据集平衡性分析功能说明</h2>
                <p>分析数据集中各类别的样本分布情况，评估数据集是否平衡</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择输入目录（应包含按类别组织的子文件夹）</li>
                    <li>可选：选择输出目录（用于保存分析报告）</li>
                    <li>点击"开始分析"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>显示各类别的样本数量和占比</li>
                    <li>计算数据集不平衡比例</li>
                    <li>提供平衡性评估和建议</li>
                    <li>可选生成文本报告</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">不平衡比例评估标准</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>&lt;2:1 : 平衡</li>
                    <li>2:1-10:1 : 中等不平衡</li>
                    <li>≥10:1 : 严重不平衡</li>
                </ul>
            </div>
            """,
        '删除指定后缀的文件': """
                <div style="font-size: 14px; line-height: 1.6;">
                    <h2 style="color: #2c3e50; margin-bottom: 10px;">删除指定后缀文件功能说明</h2>
                    <p>删除输入目录及其子目录中所有匹配指定后缀的文件</p>

                    <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                    <ol style="margin-top: 5px; padding-left: 20px;">
                        <li>选择输入目录</li>
                        <li>设置要删除的文件后缀（多个后缀用逗号分隔，如".tmp,.log"）</li>
                        <li>勾选"确认删除操作"复选框</li>
                        <li>点击"开始处理"</li>
                    </ol>

                    <h3 style="color: #e74c3c; margin-top: 15px; margin-bottom: 5px;">注意事项</h3>
                    <ul style="margin-top: 5px; padding-left: 20px;">
                        <li>此操作不可逆，请谨慎使用！</li>
                        <li>操作前请确保已备份重要文件</li>
                        <li>支持递归删除子目录中的匹配文件</li>
                        <li>不区分大小写匹配后缀</li>
                    </ul>
                </div>
                """,
        '对比两个路径差异': """
                <div style="font-size: 14px; line-height: 1.6;">
                    <h2 style="color: #2c3e50; margin-bottom: 10px;">路径对比功能说明</h2>
                    <p>比较两个目录中的文件差异</p>

                    <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                    <ol style="margin-top: 5px; padding-left: 20px;">
                        <li>选择第一个路径</li>
                        <li>选择第二个路径</li>
                        <li>设置对比选项（文件名、大小、修改时间、内容）</li>
                        <li>点击"开始处理"</li>
                    </ol>

                    <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                    <ul style="margin-top: 5px; padding-left: 20px;">
                        <li>仅在路径1存在的文件列表</li>
                        <li>仅在路径2存在的文件列表</li>
                        <li>文件名相同但大小不同的文件列表</li>
                        <li>文件名相同但修改时间不同的文件列表</li>
                        <li>文件名相同但内容不同的文件列表</li>
                    </ul>

                    <h3 style="color: #e74c3c; margin-top: 15px; margin-bottom: 5px;">注意事项</h3>
                    <ul style="margin-top: 5px; padding-left: 20px;">
                        <li>内容对比会比较文件的二进制内容，大文件可能需要较长时间</li>
                        <li>修改时间比较精确到秒级</li>
                        <li>结果会显示文件的相对路径</li>
                    </ul>
                </div>
                """
    }
    return help_texts.get(mode, "<div style='font-size: 14px;'>暂无此功能的帮助信息</div>")


def get_graph_processing_help(mode: str) -> str:
    """获取图数据处理功能的帮助信息"""
    help_texts = {
        "选择单个文件加载图结构": """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">加载图结构功能说明</h2>
                <p>加载并显示单个.bin图结构文件的详细信息</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>点击"浏览..."选择.bin文件</li>
                    <li>文件信息将自动显示在输出区域</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">显示信息包括</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>文件路径和名称</li>
                    <li>节点数量和边数量</li>
                    <li>节点和边的特征维度</li>
                </ul>
            </div>
            """,
        "统计路径下最大点/边数量的文件": """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">统计最大图结构功能说明</h2>
                <p>统计目录中节点和边数量最多的图结构文件</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择包含.bin文件的目录</li>
                    <li>统计结果将显示在输出区域</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出信息包括</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>节点最多的文件及其节点数</li>
                    <li>边最多的文件及其边数</li>
                </ul>
            </div>
            """,
        "统计路径下每个类别的信息": """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">类别统计功能说明</h2>
                <p>统计目录中各子类别图结构的信息并导出Excel</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择包含按类别组织的.bin文件的目录</li>
                    <li>选择输出Excel文件路径</li>
                    <li>点击"执行操作"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">统计信息包括</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>每个类别的模型数量</li>
                    <li>节点数量的统计信息（平均、标准差、最小、最大）</li>
                    <li>边数量的统计信息（平均、标准差、最小、最大）</li>
                </ul>
            </div>
            """
    }
    return help_texts.get(mode, "<div style='font-size: 14px;'>暂无此功能的帮助信息</div>")


def get_model_processing_help(mode: str) -> str:
    """获取3D模型处理功能的帮助信息"""
    help_texts = {
        "STEP转STL": """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">STEP转STL功能说明</h2>
                <p>将STEP格式的3D模型转换为STL格式</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择包含STEP文件的输入目录</li>
                    <li>选择STL文件输出目录</li>
                    <li>设置网格质量(1-10)</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #e74c3c; margin-top: 15px; margin-bottom: 5px;">注意事项</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>需要安装OpenCASCADE库</li>
                    <li>转换过程可能需要较长时间</li>
                </ul>
            </div>
            """,
        "STL转点云": """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">STL转点云功能说明</h2>
                <p>从STL模型生成点云数据</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择包含STL文件的输入目录</li>
                    <li>选择点云输出目录</li>
                    <li>设置采样点数量</li>
                    <li>选择是否包含法线数据</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出格式</h3>
                <p>每行包含3个坐标值(x,y,z)，如果包含法线则追加3个法线值(nx,ny,nz)</p>
            </div>
            """,
        "STL转多视图": """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">STL转多视图功能说明</h2>
                <p>为3D模型生成多视角渲染图像</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择包含STL文件的输入目录</li>
                    <li>选择图像输出目录</li>
                    <li>设置视图数量和图像尺寸</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出格式</h3>
                <p>每个模型生成N张PNG图像，文件名格式为"模型名_序号.png"</p>
            </div>
            """,
        "STEP转DGL图结构": """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">STEP转DGL图结构功能说明</h2>
                <p>将STEP格式的3D模型转换为DGL图结构(.bin)</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择包含STEP文件的输入目录</li>
                    <li>选择输出目录</li>
                    <li>设置采样参数(曲线U、曲面UV)</li>
                    <li>设置并行进程数</li>
                    <li>点击"开始处理"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出格式</h3>
                <p>每个STEP文件生成一个DGL图结构文件(.bin)</p>
                
                <h3 style="color: #e74c3c; margin-top: 15px; margin-bottom: 5px;">注意事项</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>需要安装occwl和dgl库</li>
                    <li>转换过程可能需要较长时间</li>
                    <li>支持多进程并行处理</li>
                </ul>
            </div>
            """
    }
    return help_texts.get(mode, "<div style='font-size: 14px;'>暂无此功能的帮助信息</div>")


def get_system_help(mode: str) -> str:
    """获取系统工具的帮助信息"""
    help_texts = {
        '日志分析工具': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">日志分析工具功能说明</h2>
                <p>分析应用程序日志文件，提取错误、警告统计信息</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择日志文件或日志目录</li>
                    <li>设置分析时间范围（可选）</li>
                    <li>点击"开始分析"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>错误/警告数量统计</li>
                    <li>按时间分布的频率图表</li>
                    <li>常见错误类型排名</li>
                    <li>详细错误列表</li>
                </ul>
            </div>
            """,
        '系统资源监控': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">系统资源监控功能说明</h2>
                <p>实时显示系统资源使用情况</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">监控指标</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>CPU使用率（总体和每个核心）</li>
                    <li>内存使用情况（总量/已用/可用）</li>
                    <li>磁盘使用情况（读写速度、空间使用）</li>
                    <li>网络流量（上传/下载速度）</li>
                </ul>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">功能特点</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>实时刷新（可设置刷新频率）</li>
                    <li>历史数据图表</li>
                    <li>资源使用警报阈值</li>
                </ul>
            </div>
            """
    }
    return help_texts.get(mode, "<div style='font-size: 14px;'>暂无此功能的帮助信息</div>")


def get_visualization_help(mode: str) -> str:
    """获取可视化功能的帮助信息"""
    help_texts = {
        '数据集可视化': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">数据集可视化功能说明</h2>
                <p>可视化数据集的类别分布情况，显示各类别的样本数量</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择数据集目录（应包含按类别组织的子文件夹）</li>
                    <li>点击"可视化数据集"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>显示各类别的样本数量柱状图</li>
                    <li>自动排序并显示样本最多的前20个类别</li>
                    <li>其他类别合并为"其他"显示</li>
                </ol>
            </div>
            """,
        '图数据可视化': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">图数据可视化功能说明</h2>
                <p>可视化图结构的基本信息，包括节点和边的数量</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择.bin图结构文件</li>
                    <li>点击"可视化图结构"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">输出结果</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>显示图结构的基本信息（节点数、边数）</li>
                    <li>显示节点与边数量比例的饼图</li>
                </ol>
            </div>
            """,
        '3D模型可视化': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">3D模型可视化功能说明</h2>
                <p>可视化STL模型或点云数据</p>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>选择模型文件（.stl或点云.txt文件）</li>
                    <li>点击"可视化模型"</li>
                </ol>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">支持的文件格式</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>STL文件：显示3D网格模型</li>
                    <li>点云文件：包含x,y,z坐标的文本文件，每行一个点</li>
                </ul>
                
                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">交互操作</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>鼠标左键：旋转模型</li>
                    <li>鼠标右键：平移模型</li>
                    <li>鼠标滚轮：缩放模型</li>
                </ul>
            </div>
            """
    }
    return help_texts.get(mode, "<div style='font-size: 14px;'>暂无此功能的帮助信息</div>")


def get_visualization_help(mode: str) -> str:
    """获取可视化功能的帮助信息"""
    help_texts = {
        # ... 保持原有其他帮助信息不变 ...
        '3D模型对比': """
            <div style="font-size: 14px; line-height: 1.6;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">3D模型对比功能说明</h2>
                <p>比较两个3D模型并可视化它们之间的差异</p>

                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">使用方法</h3>
                <ol style="margin-top: 5px; padding-left: 20px;">
                    <li>点击"浏览..."选择第一个模型文件</li>
                    <li>点击"浏览..."选择第二个模型文件</li>
                    <li>差异视图将自动显示两个模型之间的差异</li>
                </ol>

                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">支持的文件格式</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>STL文件：3D网格模型</li>
                    <li>点云文件：包含x,y,z坐标的文本文件</li>
                </ul>

                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">差异视图说明</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>颜色映射显示两个模型之间的距离差异</li>
                    <li>蓝色表示差异较小，红色表示差异较大</li>
                    <li>颜色条显示差异距离的标尺</li>
                </ul>

                <h3 style="color: #3498db; margin-top: 15px; margin-bottom: 5px;">交互操作</h3>
                <ul style="margin-top: 5px; padding-left: 20px;">
                    <li>鼠标左键：旋转模型</li>
                    <li>鼠标右键：平移模型</li>
                    <li>鼠标滚轮：缩放模型</li>
                </ul>
            </div>
            """
    }
    return help_texts.get(mode, "<div style='font-size: 14px;'>暂无此功能的帮助信息</div>")
