# verify 机制指南 (v1.3)

> 每个 T-ID 必须在 TASK.md 写明 verify 方式，本文档讲解怎么写。

---

## 三层验证金字塔

```
       ┌──────────────┐
       │  E2E 验证     │  主理人 review PR（人工 verify 关键路径）
       ├──────────────┤
       │  集成验证     │  verify_tXXX.sh（每个 T-ID 的端到端脚本）
       ├──────────────┤
       │  单元测试     │  tests/ 目录（自动跑）
       └──────────────┘
```

### 何时用哪一层？

| 场景 | 用哪层 | 例子 |
|------|--------|------|
| 纯函数、算法 | 单元测试 | 关键词清洗、JSON 解析、字符串处理 |
| 模块集成 | verify.sh | 数据库迁移、文件批量处理、API 端到端 |
| 用户体验 | E2E（主理人 review） | UI 改动、交互流程、可视化效果 |

---

## verify.sh 编写规范

### 命名

- 格式：`verify_t{T-ID}.sh`
- 例：`verify_t001.sh`、`verify_t002.sh`
- 放在项目根目录或 `verify/` 子目录

### 模板

```bash
#!/bin/bash
# verify_t001.sh
# 用途：验证 T-001 关键词清洗功能
# 作者：执行者
# 日期：2026-06-04

set -e  # 任何错误立即退出

echo "=== T-001 验证开始 ==="

# 1. 准备测试数据
mkdir -p /tmp/verify_t001
echo "Hello, World!" > /tmp/verify_t001/input.txt

# 2. 执行被测代码
python src/keyword_processor.py /tmp/verify_t001/input.txt > /tmp/verify_t001/output.txt

# 3. 断言输出
expected="hello world"
actual=$(cat /tmp/verify_t001/output.txt)
if [ "$actual" != "$expected" ]; then
    echo "FAIL: expected '$expected', got '$actual'"
    exit 1
fi

echo "=== T-001 验证通过 ==="
```

### 规范

- ✅ 必须 `set -e`（失败立即退出）
- ✅ 必须有清晰的成功/失败输出
- ✅ exit code：0 = 通过，非 0 = 失败
- ✅ 临时文件用 `/tmp/verify_tXXX/`（避免污染项目）
- ✅ 跑完后清理临时文件（用 `trap` 或最后手动 rm）
- ✅ 必须可重复跑（不依赖外部状态）
- ❌ 不要 hard-code 路径（如 `/Users/jesse/...`）
- ❌ 不要 `rm -rf` 项目目录

### 进阶：参数化

如果 verify 复杂，可以加参数：

```bash
#!/bin/bash
# verify_t001.sh [--keep-tmp]

set -e
KEEP_TMP=0
[ "$1" = "--keep-tmp" ] && KEEP_TMP=1

TMPDIR=$(mktemp -d -t verify_t001.XXXXXX)
trap "[ $KEEP_TMP -eq 0 ] && rm -rf $TMPDIR" EXIT

# ... 用 $TMPDIR 代替 /tmp/verify_t001
```

---

## tests/ 目录约定

### 框架选择

| 语言 | 推荐框架 |
|------|----------|
| Python | `pytest` |
| Node | `jest` / `vitest` |
| Go | 标准库 `testing` |
| 通用 | `unittest`（Python 标准库） |

### 文件命名

- `test_<模块名>.py`
- 一个模块对应一个测试文件
- 复杂模块可拆 `test_<模块名>_<子功能>.py`

### 示例（pytest）

```python
# tests/test_keyword_processor.py
import pytest
from src.keyword_processor import clean_keywords


def test_clean_normal_input():
    """普通输入：小写化 + 切分"""
    assert clean_keywords(["Hello", "World"]) == ["hello", "world"]


def test_clean_empty_input():
    """边界：空列表"""
    assert clean_keywords([]) == []


def test_clean_unicode():
    """边界：Unicode 字符"""
    assert clean_keywords(["你好", "世界"]) == ["你好", "世界"]


def test_clean_with_punctuation():
    """边界：含标点"""
    assert clean_keywords(["hello!", "world?"]) == ["hello", "world"]


@pytest.mark.parametrize("input,expected", [
    (["A", "B"], ["a", "b"]),
    (["X", "Y", "Z"], ["x", "y", "z"]),
])
def test_clean_various(input, expected):
    """参数化测试"""
    assert clean_keywords(input) == expected
```

### 跑测试的命令

```bash
# 跑单个文件
pytest tests/test_keyword_processor.py -v

# 跑全量
pytest tests/ -v

# 带覆盖率
pytest tests/ --cov=src --cov-report=html
```

---

## 5. Next.js + Vitest + React Testing Library 专章（v1.4 新增）

> **适用项目**：用 Next.js + pnpm/npm 的项目。Next.js 14+ App Router 优先用 Vitest（原生 ESM 支持，配置更少）。

### 5.1 为什么 Vitest（不是 Jest）

| 维度 | Vitest | Jest |
|------|--------|------|
| 启动速度 | 极快（Vite 生态） | 较慢 |
| ESM 支持 | 原生 | 需配置 |
| Next.js 14+ 兼容 | 完美 | 需 babel-jest 额外配置 |
| 配置复杂度 | 低 | 中 |

**结论**：新项目用 Vitest，老 Jest 项目可继续 Jest（不强制迁移）。

### 5.2 安装

```bash
pnpm add -D vitest @vitejs/plugin-react @testing-library/react \
  @testing-library/jest-dom @testing-library/user-event \
  jsdom @vitest/coverage-v8
```

### 5.3 vitest.config.ts 模板

```ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      include: ['app/**', 'lib/**', 'components/**'],
      exclude: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
    },
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './') },
  },
})
```

### 5.4 vitest.setup.ts 模板

```ts
import '@testing-library/jest-dom/vitest'
```

### 5.5 package.json scripts

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage"
  }
}
```

### 5.6 单元测试示例（纯函数）

```ts
// lib/keyword.ts
export function cleanKeywords(input: string[]): string[] {
  return input.map(s => s.toLowerCase().trim()).filter(Boolean)
}
```

```ts
// tests/lib/keyword.test.ts
import { describe, it, expect } from 'vitest'
import { cleanKeywords } from '@/lib/keyword'

describe('cleanKeywords', () => {
  it('lowercase and trim', () => {
    expect(cleanKeywords(['Hello', ' World '])).toEqual(['hello', 'world'])
  })

  it('filters empty strings', () => {
    expect(cleanKeywords(['a', '', '  ', 'b'])).toEqual(['a', 'b'])
  })

  it('handles unicode', () => {
    expect(cleanKeywords(['你好', '世界'])).toEqual(['你好', '世界'])
  })
})
```

### 5.7 组件测试示例（RTL）

```tsx
// components/Button.tsx
'use client'
export function Button({ onClick, children }: { onClick: () => void; children: React.ReactNode }) {
  return <button onClick={onClick}>{children}</button>
}
```

```tsx
// tests/components/Button.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '@/components/Button'

describe('Button', () => {
  it('renders children', () => {
    render(<Button onClick={() => {}}>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Click</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })
})
```

### 5.8 跑测试命令

```bash
pnpm test                # 跑全量（CI 模式）
pnpm test:watch          # 监听模式（开发用）
pnpm test:coverage       # 全量 + 覆盖率
pnpm test Button         # 跑匹配 "Button" 的文件
```

### 5.9 与 PR 模板的对应

PR 模板的"自动 verify"区（v1.4 改）：
- `- [ ] 跑 pnpm test tests/<T-ID 对应文件> 通过`
- `- [ ] 全量回归 pnpm test 通过`
- `- [ ] 覆盖率不低于 v1.4 基线`

**T-ID 没填 `unit-test` 字段的，PR 模板对应的 `pnpm test` 复选框不能勾选**——这是 v1.4 的硬约束。

---

## verify 与 PR 的关系

```
T-XXX 完成
    ↓
跑 verify_tXXX.sh   ←  必须通过
    ↓
跑 pytest tests/    ←  必须通过
    ↓
手动验证关键路径    ←  至少 1 个
    ↓
填到 PR 描述的"验证方式"区（勾选复选框）
    ↓
开 PR
```

**重要**：verify 失败的 T-ID **不能开 PR**，必须先修。

---

## 回归测试

PR merge 后，下次执行者启动会自动跑：

| 触发时机 | 范围 | 触发者 |
|----------|------|--------|
| 执行者启动时 | 抽样（最近 3 个 T-ID 的 verify） | 定时任务 |
| PR merge 后 | 全量（所有 T-ID 的 verify + 全量 tests） | 下次执行者启动 |
| 主理人手动 | 全量 | `bash regression.sh`（如有） |

回归流程：

```bash
# 1. 跑抽样
for t in $(ls verify_t*.sh | tail -3); do
    bash "$t" || echo "FAIL: $t"
done

# 2. 跑全量
pytest tests/ -v

# 3. 写入 REGRESSION.md
# （执行者自动写）
```

如果发现回归：

- 创建 `T-FIX-XXX` 任务
- 优先级 P0
- 标记问题来源（被哪个 PR 引入）

---

## 常见问题

### Q: verify.sh 写得很长怎么办？

A: 把逻辑拆到 tests/，verify.sh 只做"准备 + 执行 + 断言"三件事。

### Q: verify 需要外部依赖（数据库、API）怎么办？

A: 用 docker-compose 起测试环境，verify.sh 里 `docker-compose up -d` 然后跑测试。

```bash
#!/bin/bash
set -e
docker-compose -f docker-compose.test.yml up -d
trap "docker-compose -f docker-compose.test.yml down" EXIT
# ... 跑测试
```

### Q: 怎么知道 verify 覆盖了所有情况？

A: 写 verify 时问自己"如果这个函数有 bug，哪些测试会失败？" 答不出来的就是缺测试。

### Q: verify.sh 和 tests/ 重复了怎么办？

A: 不重复。tests/ 测单个函数，verify.sh 测端到端流程。两者粒度不同。

### Q: 性能测试算 verify 吗？

A: 算。可以加一个 `verify_tXXX_perf.sh`，标记为性能验证。

### Q: 怎么调试 verify 失败？

A: 跑 verify 时加 `bash -x verify_tXXX.sh` 看每一步执行。

---

## 验证清单（自检用）

每次开 PR 前，检查：

- [ ] TASK.md 的 T-ID 写了 verify 方式
- [ ] verify_tXXX.sh 创建并通过
- [ ] tests/ 目录对应单元测试通过
- [ ] 手动验证至少 1 个关键场景
- [ ] PR 描述的"验证方式"区复选框全部勾选
- [ ] verify 失败的 T-ID 不开 PR
