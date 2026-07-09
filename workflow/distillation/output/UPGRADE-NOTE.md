# 历史蒸馏产物 · 升级说明

> 本目录下所有 `*.skill/` 子目录是按 **v1 方法论**（"三阶 × 坡度" 9宫格正交矩阵）生成的历史蒸馏快照。

## v1 vs v2 方法论对照

| 维度 | v1（历史快照） | v2（现行方法论） |
|-----|--------------|---------------|
| 思考结构 | 三阶方法论 × 坡度理解 = 9宫格正交矩阵，9块易重复 | 三阶合一，3阶段主线，无重复 |
| 是什么 | 描述性定义（属加种差，描述外延） | **本质定义先行**（揭示本质属性，必须通过本质检验） |
| 类-属性-方法-路由 | "项目=类"隐喻硬接 | **由本质定义锚定**，每一层必须能回溯到本质 |
| 顿悟触发 | 无 | 阶段1一句话点破 + 阶段2反常识根因 + 阶段3视角升级 |
| 递归深入 | 每层重做完整三阶 | 只重做阶段1（重新找子概念的本质定义） |

## 处理策略

- **保留快照**：v1 产物作为历史快照保留，不回头改写（避免破坏其历史价值）
- **不强制升级**：v1 产物仍可使用，其核心心智模型/启发式/路由依然有效
- **重新蒸馏走v2**：如需重新蒸馏某个对象（例如用新材料重新蒸馏张雪峰），将自动采用 v2 模板，输出会包含本质检验、顿悟触发点等新结构
- **混用提示**：在调用 v1 产物时，可手动补"本质定义+反常识根因+视角升级"三个顿悟触发点，使其更接近 v2 体感

## 涉及的 v1 历史快照

按人物/话题蒸馏的 12 个 Skill：

1. `charliemunger.skill/` — 查理·芒格
2. `darwin.skill/` — 达尔文
3. `einstein.skill/` — 爱因斯坦
4. `kongzi.skill/` — 孔子
5. `laozi.skill/` — 老子
6. `law-application.skill/` — 法律适用（话题蒸馏）
7. `luxun.skill/` — 鲁迅
8. `nihaixia.skill/` — 倪海夏
9. `pusuzhidao.skill/` — 朴素之道
10. `socrates.skill/` — 苏格拉底
11. `wangyangming.skill/` — 王阳明
12. `xunzi.skill/` — 荀子
13. `zhangxuefeng.skill/` — 张雪峰
14. `zhugeliang.skill/` — 诸葛亮

## 升级路径

如果希望把某个 v1 产物升级到 v2，有两种方式：

### 方式A：增量补丁（轻量）
保留 v1 的 research/ 目录不变，仅重写 essence/ 下三个文件：
- `01-what-essence.md` → 加入本质定义 + 本质检验表 + 类归属
- `02-why-root-causes.md` → 加入反常识根因
- `03-how-system.md` → 加入视角升级收尾，并改"项目=类"为"由本质定义锚定"

### 方式B：完全重蒸馏（重量）
按 [../templates/distillation-skill.md](../templates/distillation-skill.md)（v2 模板）从头走蒸馏流程，输出全新的 v2 Skill。

---

*本说明由本质工坊 v2 方法论升级自动生成。详细方法论见 [../../cognitive/general-logic/references/methodology.md](../../cognitive/general-logic/references/methodology.md)*
