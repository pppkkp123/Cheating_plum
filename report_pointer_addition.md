# 指標功能補充說明

## 一、補充目的

原本 Small-C 解譯器已經支援基本變數、陣列、函式、流程控制與運算式。本次補充指標功能，使程式可以處理 `int *p`、`&x`、`*p` 等常見指標語法。

## 二、語法分析修改

Parser 新增以下能力：

1. 宣告時可以讀取 `*`：
   - `int *ptr;`
   - `void set_value(int *p, int value)`

2. 運算式中可以使用：
   - `&x`：取得變數位置
   - `*ptr`：取出指標指向的變數值
   - `*ptr = 99`：透過指標修改原本變數

## 三、記憶體模型

本系統使用簡化記憶體模型。每個變數都會被包裝成一個 `Cell`，每個 `Cell` 都有一個假的 address。

例如：

```c
int x;
int *ptr;
x = 10;
ptr = &x;
*ptr = 99;
```

內部狀態可以理解成：

```text
x   -> Cell(address=1000, value=10)
ptr -> Cell(address=1004, value=PointerValue(指向 x 的 Cell))
```

執行 `*ptr = 99` 時，解譯器會先找到 `ptr` 指向的 `Cell`，再把該 `Cell` 的值改成 99，所以 `x` 的值也會跟著改變。

## 四、執行期錯誤處理

新增三種指標錯誤偵測：

1. Null pointer dereference

```c
int *p;
printf("%d\n", *p);
```

輸出：

```text
Error: null pointer dereference
```

2. Dereference non-pointer value

```c
int x;
x = 10;
printf("%d\n", *x);
```

輸出：

```text
Error: cannot dereference non-pointer value
```

3. Address of rvalue

```c
int *p;
p = &(10 + 20);
```

輸出：

```text
Error: left side of assignment must be a variable, array element, or pointer dereference
```

## 五、測試檔

新增以下測試：

- `tests/pointer_basic.sc`
- `tests/pointer_basic.expected`
- `tests/pointer_function.sc`
- `tests/pointer_function.expected`
- `tests/pointer_array.sc`
- `tests/pointer_array.expected`
- `tests/error_null_pointer.sc`
- `tests/error_null_pointer.expected`
- `tests/error_non_pointer.sc`
- `tests/error_non_pointer.expected`
- `tests/error_address_rvalue.sc`
- `tests/error_address_rvalue.expected`

可使用：

```bash
python run_tests.py
```

一次檢查所有 `.expected` 輸出是否符合。
