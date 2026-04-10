#!/usr/bin/env python3
"""
UE Material Blueprint Text Generator
=====================================
从简洁的节点定义 JSON 生成完整的 UE 材质编辑器可粘贴文本。

用法:
  python ue_material_bp_gen.py input.json            # 输出到 stdout
  python ue_material_bp_gen.py input.json -o out.txt  # 输出到文件

输入 JSON 格式见底部 SCHEMA 说明和 generate_from_dict() 文档。
"""

import json, sys, argparse

# ─── Pin 模板常量 ───────────────────────────────────────────────
_INPUT_PIN = (
    'CustomProperties Pin ('
    'PinId={pin_id},'
    'PinName="{name}",'
    'PinType.PinCategory="optional",'
    'PinType.PinSubCategory="red",'
    'PinType.PinSubCategoryObject=None,'
    'PinType.PinSubCategoryMemberReference=(),'
    'PinType.PinValueType=(),'
    'PinType.ContainerType=None,'
    'PinType.bIsReference=False,'
    'PinType.bIsConst=False,'
    'PinType.bIsWeakPointer=False,'
    'PinType.bIsUObjectWrapper=False,'
    'PinType.bSerializeAsSinglePrecisionFloat=False,'
    '{default_value}'
    '{linked_to}'
    'PersistentGuid=00000000000000000000000000000000,'
    'bHidden=False,'
    'bNotConnectable={not_connectable},'
    'bDefaultValueIsReadOnly=False,'
    'bDefaultValueIsIgnored=False,'
    'bAdvancedView=False,'
    'bOrphanedPin=False,)'
)

_OUTPUT_PIN = (
    'CustomProperties Pin ('
    'PinId={pin_id},'
    'PinName="Output",'
    'PinFriendlyName=NSLOCTEXT("MaterialGraphNode", "Space", " "),'
    'Direction="EGPD_Output",'
    'PinType.PinCategory="",'
    'PinType.PinSubCategory="",'
    'PinType.PinSubCategoryObject=None,'
    'PinType.PinSubCategoryMemberReference=(),'
    'PinType.PinValueType=(),'
    'PinType.ContainerType=None,'
    'PinType.bIsReference=False,'
    'PinType.bIsConst=False,'
    'PinType.bIsWeakPointer=False,'
    'PinType.bIsUObjectWrapper=False,'
    'PinType.bSerializeAsSinglePrecisionFloat=False,'
    '{linked_to}'
    'PersistentGuid=00000000000000000000000000000000,'
    'bHidden=False,'
    'bNotConnectable=False,'
    'bDefaultValueIsReadOnly=False,'
    'bDefaultValueIsIgnored=False,'
    'bAdvancedView=False,'
    'bOrphanedPin=False,)'
)

# ─── 节点类型注册表 ────────────────────────────────────────────
# key: 短名 → (ExpressionClass尾缀, 默认输入Pin名列表, 有无Value Pin(bNotConnectable))
NODE_TYPES = {
    # 无输入源节点
    "Constant":             {"cls": "MaterialExpressionConstant",             "inputs": [],                                     "value_pin": True},
    "Constant2Vector":      {"cls": "MaterialExpressionConstant2Vector",      "inputs": [],                                     "value_pin": True},
    "Constant3Vector":      {"cls": "MaterialExpressionConstant3Vector",      "inputs": [],                                     "value_pin": True},
    "ScalarParameter":      {"cls": "MaterialExpressionScalarParameter",      "inputs": [],                                     "value_pin": True},
    "VectorParameter":      {"cls": "MaterialExpressionVectorParameter",      "inputs": [],                                     "value_pin": True},
    "TextureCoordinate":    {"cls": "MaterialExpressionTextureCoordinate",    "inputs": [],                                     "value_pin": False},
    "RealTime":             {"cls": "MaterialExpressionRealTime",             "inputs": [],                                     "value_pin": False},
    "Time":                 {"cls": "MaterialExpressionTime",                 "inputs": [],                                     "value_pin": False},
    # 单输入
    "Floor":                {"cls": "MaterialExpressionFloor",                "inputs": ["Input"],                              "value_pin": False},
    "Frac":                 {"cls": "MaterialExpressionFrac",                 "inputs": ["Input"],                              "value_pin": False},
    "Sine":                 {"cls": "MaterialExpressionSine",                 "inputs": ["Input"],                              "value_pin": False},
    "Cosine":               {"cls": "MaterialExpressionCosine",               "inputs": ["Input"],                              "value_pin": False},
    "Abs":                  {"cls": "MaterialExpressionAbs",                  "inputs": ["Input"],                              "value_pin": False},
    "OneMinus":             {"cls": "MaterialExpressionOneMinus",             "inputs": ["Input"],                              "value_pin": False},
    "Saturate":             {"cls": "MaterialExpressionSaturate",             "inputs": ["Input"],                              "value_pin": False},
    "ComponentMask":        {"cls": "MaterialExpressionComponentMask",        "inputs": ["Input"],                              "value_pin": False},
    # 双输入
    "Add":                  {"cls": "MaterialExpressionAdd",                  "inputs": ["A", "B"],                             "value_pin": False},
    "Subtract":             {"cls": "MaterialExpressionSubtract",             "inputs": ["A", "B"],                             "value_pin": False},
    "Multiply":             {"cls": "MaterialExpressionMultiply",             "inputs": ["A", "B"],                             "value_pin": False},
    "Divide":               {"cls": "MaterialExpressionDivide",              "inputs": ["A", "B"],                             "value_pin": False},
    "DotProduct":           {"cls": "MaterialExpressionDotProduct",           "inputs": ["A", "B"],                             "value_pin": False},
    "CrossProduct":         {"cls": "MaterialExpressionCrossProduct",         "inputs": ["A", "B"],                             "value_pin": False},
    "AppendVector":         {"cls": "MaterialExpressionAppendVector",         "inputs": ["A", "B"],                             "value_pin": False},
    "Max":                  {"cls": "MaterialExpressionMax",                  "inputs": ["A", "B"],                             "value_pin": False},
    "Min":                  {"cls": "MaterialExpressionMin",                  "inputs": ["A", "B"],                             "value_pin": False},
    "Power":                {"cls": "MaterialExpressionPower",                "inputs": ["Base", "Exponent"],                   "value_pin": False},
    # 三输入
    "LinearInterpolate":    {"cls": "MaterialExpressionLinearInterpolate",    "inputs": ["A", "B", "Alpha"],                    "value_pin": False},
    "Clamp":                {"cls": "MaterialExpressionClamp",                "inputs": ["Input", "Min", "Max"],                "value_pin": False},
    # 五输入
    "If":                   {"cls": "MaterialExpressionIf",                   "inputs": ["A", "B", "A>B", "A==B", "A<B"],       "value_pin": False},
    # 特殊
    "StaticSwitchParameter":{"cls": "MaterialExpressionStaticSwitchParameter","inputs": ["A", "B"],                             "value_pin": False},
    "FunctionInput":        {"cls": "MaterialExpressionFunctionInput",        "inputs": ["Preview"],                            "value_pin": False},
    "FunctionOutput":       {"cls": "MaterialExpressionFunctionOutput",       "inputs": ["A"],                                  "value_pin": False, "no_output": True},
    "TextureSample":        {"cls": "MaterialExpressionTextureSample",        "inputs": ["Coordinates"],                        "value_pin": False},
    "MaterialFunctionCall": {"cls": "MaterialExpressionMaterialFunctionCall", "inputs": [],                                     "value_pin": False, "dynamic_inputs": True},
    "Custom":               {"cls": "MaterialExpressionCustom",              "inputs": [],                                     "value_pin": False, "dynamic_inputs": True},
}

# ─── GUID 生成 ─────────────────────────────────────────────────
class GuidAllocator:
    """递增生成 32 位十六进制 GUID，数字右对齐补零确保唯一"""
    def __init__(self, prefix="A"):
        self._prefix = prefix
        self._counter = 0
    def next(self):
        self._counter += 1
        # 前缀1字符 + 31位十六进制右对齐零填充 → 保证唯一
        return (self._prefix + format(self._counter, '031X')).upper()

# ─── 核心生成逻辑 ──────────────────────────────────────────────
def _make_guid32(prefix, idx):
    body = format(idx, 'X')
    return (prefix + body).ljust(32, '0')[:32].upper()

def _expr_path(node_name, expr_cls, expr_idx):
    return f"/Script/Engine.{expr_cls}'{node_name}.{expr_cls}_{expr_idx}'"

def generate_from_dict(data):
    """
    从简洁 JSON 字典生成完整 UE 蓝图复制文本。

    JSON Schema:
    {
      "nodes": [
        {
          "name": "MaterialGraphNode_Const",    // 节点名（唯一）
          "type": "Constant",                   // 节点类型（见 NODE_TYPES）
          "pos": [-200, 0],                     // [X, Y] 位置
          "props": {"R": 0.75},                 // Expression 属性（类型特有）
          "inputs": {                           // 输入连接 {PinName: 源节点名}
            "A": "MaterialGraphNode_Const"      // 或 null 表示未连接
          },
          "input_pins": ["P (V2)"],             // 仅 dynamic_inputs 节点：自定义输入Pin名
          "default_values": {"A": "0.0"}        // 可选：覆盖输入Pin默认值
        }
      ],
      "connections": [                          // 可选：显式连接列表（替代 inputs 字段）
        ["SourceNode.Output", "TargetNode.A"]   // "节点名.Pin名" 格式
      ]
    }

    简化规则:
    - 省略 inputs 中未连接的 Pin
    - pos 默认 [0,0]
    - props 根据节点类型设置 Expression 属性
    - GUID/PinId 全部自动生成
    - 双向 LinkedTo 自动补全
    """
    nodes_def = data.get("nodes", [])

    # 1) 分配 GUID
    pin_alloc = GuidAllocator("A")
    node_guid_alloc = GuidAllocator("B")
    expr_guid_alloc = GuidAllocator("C")

    # 构建节点数据
    nodes = {}
    # expr_idx 计数器（按 Expression 类型）
    expr_counters = {}

    for nd in nodes_def:
        name = nd["name"]
        ntype = nd["type"]
        tinfo = NODE_TYPES[ntype]
        cls = tinfo["cls"]

        # Expression 索引
        idx = expr_counters.get(cls, 0)
        expr_counters[cls] = idx + 1

        pos = nd.get("pos", [0, 0])
        props = nd.get("props", {})
        input_conns = nd.get("inputs", {})
        custom_input_pins = nd.get("input_pins", [])
        default_values = nd.get("default_values", {})

        # 确定输入 Pin 列表
        if tinfo.get("dynamic_inputs") and custom_input_pins:
            input_pin_names = custom_input_pins
        else:
            input_pin_names = list(tinfo["inputs"])

        # 分配 Pin GUID
        pins = {}

        # Value pin (for constants/parameters, bNotConnectable=True)
        if tinfo["value_pin"]:
            pid = pin_alloc.next()
            pins["__value__"] = {"id": pid, "name": "Value", "not_connectable": True}

        # Input pins
        for pname in input_pin_names:
            pid = pin_alloc.next()
            pins[pname] = {"id": pid, "name": pname, "not_connectable": False}

        # Output pin
        has_output = not tinfo.get("no_output", False)
        if has_output:
            pid = pin_alloc.next()
            pins["Output"] = {"id": pid, "name": "Output", "is_output": True}

        nodes[name] = {
            "name": name,
            "type": ntype,
            "cls": cls,
            "expr_idx": idx,
            "pos": pos,
            "props": props,
            "input_conns": input_conns,
            "default_values": default_values,
            "pins": pins,
            "node_guid": node_guid_alloc.next(),
            "expr_guid": expr_guid_alloc.next(),
            "has_output": has_output,
        }

    # 2) 处理 connections 字段（如果有）
    extra_conns = data.get("connections", [])
    for conn in extra_conns:
        src_parts = conn[0].rsplit(".", 1)
        dst_parts = conn[1].rsplit(".", 1)
        src_node = src_parts[0]
        dst_node = dst_parts[0]
        dst_pin = dst_parts[1] if len(dst_parts) > 1 else "Input"
        nodes[dst_node]["input_conns"][dst_pin] = src_node

    # 3) 构建双向 LinkedTo 映射
    # linked_to[node_name][pin_name] = [(target_node, target_pin_id), ...]
    linked_to = {n: {} for n in nodes}

    for name, nd in nodes.items():
        for pin_name, src_node_name in nd["input_conns"].items():
            if src_node_name is None:
                continue
            src_nd = nodes[src_node_name]
            # 源的 Output Pin → 目标的 Input Pin
            src_out_id = src_nd["pins"]["Output"]["id"]
            dst_in_id = nd["pins"][pin_name]["id"]

            # Output → Input
            linked_to[src_node_name].setdefault("Output", []).append((name, dst_in_id))
            # Input → Output
            linked_to[name].setdefault(pin_name, []).append((src_node_name, src_out_id))

    # 4) 生成文本
    lines = []
    for name, nd in nodes.items():
        cls = nd["cls"]
        idx = nd["expr_idx"]
        expr_name = f"{cls}_{idx}"
        px, py = nd["pos"]

        # Expression 引用路径
        expr_ref = f"/Script/Engine.{cls}'{expr_name}'"

        # --- Begin Object ---
        lines.append(f'Begin Object Class=/Script/UnrealEd.MaterialGraphNode Name="{name}"')

        # Inner Expression Object
        lines.append(f'   Begin Object Class=/Script/Engine.{cls} Name="{expr_name}"')
        lines.append(f'   End Object')
        lines.append(f'   Begin Object Name="{expr_name}"')

        # Expression 属性
        # 自动添加 Expression= 引用（输入连接）
        expr_input_map = _get_expr_input_names(nd["type"])
        for pin_name, src_node_name in nd["input_conns"].items():
            if src_node_name is None:
                continue
            expr_pin_name = _pin_to_expr_name(pin_name)
            if expr_pin_name:
                src_nd = nodes[src_node_name]
                src_expr_path = _expr_path(src_node_name, src_nd["cls"], src_nd["expr_idx"])
                lines.append(f'      {expr_pin_name}=(Expression="{src_expr_path}")')

        # 自定义属性
        for k, v in nd["props"].items():
            if isinstance(v, str) and not v.startswith('(') and not v.startswith('/') and not v.startswith('FunctionInput'):
                lines.append(f'      {k}="{v}"')
            else:
                lines.append(f'      {k}={v}')

        lines.append(f'      MaterialExpressionEditorX={px}')
        lines.append(f'      MaterialExpressionEditorY={py}')
        lines.append(f'      MaterialExpressionGuid={nd["expr_guid"]}')
        lines.append(f'   End Object')

        # Node-level properties
        lines.append(f'   MaterialExpression="{expr_ref}"')
        lines.append(f'   NodePosX={px}')
        lines.append(f'   NodePosY={py}')
        lines.append(f'   NodeGuid={nd["node_guid"]}')

        # bCanRenameNode for parameters
        if nd["type"] in ("ScalarParameter", "VectorParameter", "StaticSwitchParameter"):
            lines.append(f'   bCanRenameNode=True')

        # --- CustomProperties Pin ---
        for pin_key, pin_info in nd["pins"].items():
            if pin_key == "__value__":
                # Value pin (bNotConnectable=True)
                dv = nd["default_values"].get("Value", _get_value_default(nd))
                lt_str = _format_linked_to(linked_to[name].get("__value__", []))
                dv_str = 'DefaultValue="' + str(dv) + '",'
                pin_text = _INPUT_PIN.format(pin_id=pin_info["id"], name="Value", default_value=dv_str, linked_to=lt_str, not_connectable="True")
                lines.append('   ' + pin_text)
            elif pin_info.get("is_output"):
                lt_str = _format_linked_to(linked_to[name].get("Output", []))
                pin_text = _OUTPUT_PIN.format(pin_id=pin_info["id"], linked_to=lt_str)
                lines.append('   ' + pin_text)
            else:
                pname = pin_info["name"]
                dv = nd["default_values"].get(pname, "0.0")
                lt_str = _format_linked_to(linked_to[name].get(pname, []))
                dv_str = 'DefaultValue="' + str(dv) + '",'
                pin_text = _INPUT_PIN.format(pin_id=pin_info["id"], name=pname, default_value=dv_str, linked_to=lt_str, not_connectable="False")
                lines.append('   ' + pin_text)

        lines.append(f'End Object')
        lines.append('')

    return '\n'.join(lines).rstrip()


def _format_linked_to(targets):
    if not targets:
        return ''
    parts = ','.join(f'{n} {pid}' for n, pid in targets)
    return f'LinkedTo=({parts},),'


def _get_value_default(nd):
    """从 props 推断 Value pin 的默认值字符串"""
    props = nd["props"]
    if "R" in props and "G" in props and "B" in props:
        return f'{props["R"]}'
    if "R" in props and "G" in props:
        return f'{props["R"]},{props["G"]}'
    if "R" in props:
        return str(props["R"])
    if "DefaultValue" in props:
        v = props["DefaultValue"]
        if isinstance(v, (int, float)):
            return str(v)
        return str(v)
    return "0.0"


def _pin_to_expr_name(pin_name):
    """Pin 名 → Expression 属性名映射"""
    mapping = {
        "A": "A", "B": "B", "Alpha": "Alpha",
        "Input": "Input", "Coordinates": "Coordinates",
        "Min": "Min", "Max": "Max",
        "Base": "Base", "Exponent": "Exponent",
        "A>B": "AGreaterThanB", "A==B": "AEqualsB", "A<B": "ALessThanB",
    }
    return mapping.get(pin_name, pin_name)


def _get_expr_input_names(ntype):
    tinfo = NODE_TYPES.get(ntype, {})
    return tinfo.get("inputs", [])


# ─── CLI ────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate UE Material Blueprint text from compact JSON")
    parser.add_argument("input", help="Input JSON file path")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = generate_from_dict(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
