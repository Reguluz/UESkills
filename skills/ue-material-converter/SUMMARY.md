# UE材质转换器 Skills包

## 📁 包结构

```
ue-material-converter/
├── skill.json              # Skills包元数据定义
├── prompt.md               # 主要提示词文件（核心逻辑）
├── README.md               # Skills包说明文档
├── config-template.json    # 配置模板（可选）
└── examples/               # 示例和参考
    ├── quickstart.md           # 快速开始指南
    ├── function_reference.md   # GLSL到HLSL函数映射参考
    ├── shadertoy_basics.glsl   # Shadertoy转换示例
    ├── noise_functions.hlsl    # 多函数结构体封装示例
    └── blueprint_example.txt   # 蓝图转换示例
```

## 🎯 核心功能

### 1. 蓝图转HLSL函数
- 分析UE材质蓝图的文本表示
- 将节点连接逻辑转换为HLSL函数
- 保持输入输出参数清晰
- 添加说明注释

### 2. 着色器转Custom节点
- 支持Shadertoy格式
- 支持GLSL格式
- 支持HLSL格式
- 自动处理类型转换
- 自动转换内置函数
- 明确输入输出说明

### 3. 结构体封装
- 对复杂算法使用结构体组织
- 多函数封装
- 清晰的调用层次
- 便于维护和扩展

## 🚀 快速使用

### 方式1: 对话使用
直接在对话中提及需求：
```
请将这个Shadertoy着色器转换为UE Custom节点：
[代码]
```

### 方式2: 斜杠命令
```
/ue-material-converter
```

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| `README.md` | Skills包基本说明 |
| `examples/quickstart.md` | 快速开始教程 |
| `examples/function_reference.md` | 函数映射参考表 |
| `examples/shadertoy_basics.glsl` | Shadertoy转换示例 |
| `examples/noise_functions.hlsl` | 复杂函数封装示例 |
| `examples/blueprint_example.txt` | 蓝图转换示例 |

## 🔧 配置选项

可以通过`config-template.json`自定义：
- UE版本
- 输出格式
- 坐标系统
- 纹理采样方式
- 验证选项
- 命名规范

## ⚠️ 注意事项

1. **UE版本差异**: 不同版本可能有API差异
2. **纹理采样**: 需要同时提供Texture和Sampler
3. **性能**: 避免复杂循环和递归
4. **坐标系**: 注意Y轴方向和UV原点差异

## 📝 支持的转换

### GLSL → HLSL类型
```
vec2/3/4  → float2/3/4
mat2/3/4  → float2x2/3x3/4x4
mix()     → lerp()
fract()   → frac()
texture() → Texture2DSample()
```

### Shadertoy变量
```
iResolution → View.ViewSizeAndInvSize.xy
iTime       → View.RealTime
fragCoord   → View.ViewSizeAndInvSize.xy * UV
```

## 🎓 学习资源

- 查看`examples/`目录获取实际案例
- 参考`function_reference.md`了解函数映射
- 阅读`quickstart.md`学习使用方法

## 📮 反馈和改进

如遇到问题或有改进建议，欢迎反馈：
- 不支持的GLSL/HLSL特性
- 转换错误
- 新功能需求
- 文档改进建议

---

**版本**: 1.0.0
**更新日期**: 2026-04-10
**兼容**: Unreal Engine 5.0+
