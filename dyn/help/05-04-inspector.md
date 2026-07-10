# 检查器

检查器位于主窗口右侧，以 JSON 格式展示当前选中元素的完整数据。

## 显示

示例：

```json
{
  "id": "abc123...",
  "name": "烟花 1",
  "start_tick": 80,
  "duration_ticks": 20,
  "type": "double_layer",
  "position": {"x": 10.0, "y": 85.0, "z": -5.0},
  "inner_color": {
    "start": {"r": 0, "g": 0, "b": 255},
    "end": {"r": 0, "g": 0, "b": 255}
  },
  "outer_color": {
    "start": {"r": 255, "g": 0, "b": 0},
    "end": {"r": 255, "g": 50, "b": 0}
  },
  "angles": {"horizontal": 30.0, "vertical": 30.0},
  "params": {"speed": 10.0}
}
```

未选中元素时，检查器显示为空。
