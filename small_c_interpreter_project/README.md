# Small-C 互動式解譯器 Pointer 版

這是 Python 實作的 Small-C 簡化版互動式解譯器，已補上基本指標功能。

## 執行方式

```bash
python main.py
```

或直接執行測試檔：

```bash
python main.py tests/pointer_basic.sc
python main.py tests/pointer_function.sc
python main.py tests/pointer_array.sc
```

## 一鍵測試

```bash
python run_tests.py
```

## 已支援功能

- `int`、`char`、`void`
- 全域變數、區域變數
- 一維陣列
- 函式定義與呼叫
- 遞迴
- `if / else`
- `while`
- `for`
- `break / continue / return`
- 算術、比較、邏輯、位元運算
- `printf` 等內建函式
- 指標簡化支援：
  - `int *p;`
  - `p = &x;`
  - `*p = 99;`
  - `printf("%d", *p);`
  - `void set_value(int *p) { *p = 10; }`
  - `p = &arr[1];` 和 `*p = 88;`

## 指標實作方式

本版本不是使用真正的 C 記憶體位址，而是用 Python 物件模擬。每個變數都會被包成一個 `Cell`，而每個 `Cell` 都有假位址。

```text
int x;      -> Cell(value=0, address=1000)
int *p;     -> Cell(value=PointerValue(NULL), address=1004)
p = &x;     -> p.value 指向 x 的 Cell
*p = 99;    -> 修改 p 指向的 Cell，所以 x 也會變成 99
```

## 測試檔與 .expected

`tests/` 裡每個 `.sc` 都有對應 `.expected`，可用 `python run_tests.py` 自動比對。

新增指標測試：

- `pointer_basic.sc`
- `pointer_function.sc`
- `pointer_array.sc`
- `error_null_pointer.sc`
- `error_non_pointer.sc`
- `error_address_rvalue.sc`

## 目前限制

- 沒有完整 C 記憶體模型
- 沒有完整 pointer arithmetic，例如 `p + 1` 不會真的移到下一個元素
- 沒有多維陣列
- `scanf` 尚未完整實作
- `char[]` 字串記憶體模型尚未完整實作
- `#define` 尚未完整實作
