# UE材质转换器 - 安装和使用指南

## 📦 安装

### 方式1: 手动安装

**Windows:**
```cmd
xcopy /E /I ue-material-converter %USERPROFILE%\.claude\skills\ue-material-converter
```

**macOS/Linux:**
```bash
cp -r ue-material-converter ~/.claude/skills/
```

### 方式2: 复制文件

1. 打开Claude设置目录
   - Windows: `%USERPROFILE%\.claude\`
   - macOS: `~/.claude/`
   - Linux: `~/.claude/`

2. 创建`skills`目录（如果不存在）

3. 将`ue-material-converter`文件夹复制到`skills`目录

### 方式3: 使用Claude Code CLI（如果支持）

```bash
claude skill install ue-material-converter
```

## ✅ 验证安装

1. 重启Claude Code应用

2. 在对话中输入：
   ```
   /ue-material-converter
   ```

3. 应该看到欢迎消息和使用说明

## 🚀 快速开始

### 第一步：准备代码

选择你要转换的代码类型：

- **Shadertoy**: 从shadertoy.com复制的代码
- **GLSL**: OpenGL着色器代码
- **HLSL**: DirectX着色器代码
- **蓝图**: UE材质蓝图的文本表示

### 第二步：请求转换

在Claude对话中输入：

```
请将这段代码转换为UE Custom节点：
[粘贴你的代码]
```

或者使用斜杠命令：
```
/ue-material-converter
```
然后粘贴代码。

### 第三步：使用转换结果

1. 在UE材质编辑器中创建Custom节点
2. 粘贴转换后的HLSL代码
3. 根据说明设置输入引脚
4. 连接到材质属性

## 📚 文档结构

```
ue-material-converter/
│
├── README.md              # 基本介绍
├── SUMMARY.md             # 功能概述
├── INSTALL.md             # 安装指南（本文件）
├── skill.json             # Skills包元数据
├── prompt.md              # 核心转换逻辑
├── config-template.json   # 配置模板
│
└── examples/              # 示例和教程
    ├── quickstart.md          # 快速开始教程
    ├── function_reference.md  # GLSL到HLSL函数映射
    ├── shadertoy_basics.glsl  # Shadertoy基础示例
    ├── noise_functions.hlsl   # 噪声函数示例
    ├── blueprint_example.txt  # 蓝图转换示例
    ├── advanced_raymarching.glsl  # 高级光线步进示例
    └── test_cases.md          # 测试案例集合
```

## 🎯 支持的转换

### 代码格式
| 格式 | 支持状态 | 说明 |
|------|---------|------|
| Shadertoy | ✅ | 完整支持，自动处理uniform变量 |
| GLSL | ✅ | 支持常见GLSL特性 |
| HLSL | ✅ | 支持转换为UE材质HLSL |
| UE蓝图 | ⚠️ | 基础支持，需要文本表示 |

### 转换能力
- ✅ 类型转换（vec → float）
- ✅ 函数名转换（mix → lerp）
- ✅ 矩阵操作（mat → floatNxN）
- ✅ 纹理采样（texture → Texture2DSample）
- ✅ 向量操作（swizzle、点积等）
- ✅ 结构体封装（复杂算法）
- ⚠️ 宏定义（部分支持）
- ⚠️ 预处理器指令（部分支持）

## ⚙️ 配置

复制`config-template.json`为`config.json`并根据需要修改：

```json
{
  "version": "5.3",
  "preferences": {
    "coordinateSystem": "ue_default",
    "namingConvention": "camelCase"
  }
}
```

## 🔧 故障排除

### 问题1: 转换后代码报错

**可能原因**：
- UE版本不兼容
- 代码使用了不支持的特性
- 语法转换错误

**解决方案**：
1. 检查UE版本是否在5.0以上
2. 查看`examples/function_reference.md`确认函数映射
3. 尝试简化原始代码

### 问题2: 材质渲染结果错误

**可能原因**：
- UV坐标范围不正确
- 坐标系差异
- 输入参数类型错误

**解决方案**：
1. 检查UV是否需要转换：`UV = UV * 2.0 - 1.0`
2. 验证输入参数类型
3. 添加调试输出

### 问题3: 性能问题

**解决方案**：
1. 减少循环次数
2. 简化计算
3. 使用材质函数重用
4. 参考`examples/advanced_raymarching.glsl`的优化建议

## 📖 学习资源

1. **快速入门**: 阅读`examples/quickstart.md`
2. **函数参考**: 查看`examples/function_reference.md`
3. **实战案例**: 学习`examples/`目录下的示例
4. **测试验证**: 使用`examples/test_cases.md`测试

## 💡 使用技巧

### 技巧1: 分步转换复杂代码

对于复杂着色器：
1. 先转换核心函数
2. 逐个添加辅助函数
3. 最后组合完整效果

### 技巧2: 使用测试案例

使用`test_cases.md`验证转换是否正确。

### 技巧3: 创建材质函数

将常用的转换结果保存为材质函数以便重用。

## 🆘 获取帮助

遇到问题时提供：
1. 原始代码片段
2. 转换后的代码
3. 完整错误信息
4. UE版本
5. 预期结果和实际结果

## 🔄 更新

要更新Skills包：

```bash
# 备份现有配置
cp ~/.claude/skills/ue-material-converter/config.json ~/.claude/skills_config_backup.json

# 删除旧版本
rm -rf ~/.claude/skills/ue-material-converter

# 复制新版本
cp -r ue-material-converter ~/.claude/skills/

# 恢复配置
cp ~/.claude/skills_config_backup.json ~/.claude/skills/ue-material-converter/config.json
```

## 📝 更新日志

### v1.0.0 (2026-04-10)
- 初始版本
- 支持Shadertoy/GLSL/HLSL转换
- 支持蓝图文本转换
- 支持结构体封装
- 包含完整示例和文档

## 📄 许可

本Skills包遵循与Claude Code相同的许可协议。

---

**祝你使用愉快！🎨**

如有问题或建议，欢迎反馈。
