# Small-C 互動式解譯器專題報告

## 一、作業目標

本專題實作一個使用 Python 撰寫的 Small-C 互動式解譯器。使用者可以透過命令列輸入 Small-C 程式碼，並使用 `LOAD`、`SAVE`、`LIST`、`CHECK`、`RUN`、`TRACE`、`VARS`、`FUNCS` 等指令進行程式管理、語法檢查與執行。

## 二、系統架構

本系統分成以下模組：

1. `lexer.py`：負責詞法分析，將原始程式碼轉換成 token。
2. `parser.py`：負責語法分析，將 token 轉換成 AST。
3. `ast_nodes.py`：定義 AST 節點資料結構。
4. `interpreter.py`：負責執行 AST，包含變數、流程控制、函式呼叫與運算。
5. `memory.py`：管理作用域、變數儲存與一維陣列。
6. `sc_builtins.py`：實作 `printf`、`strlen`、`abs`、`max`、`min` 等內建函式。
7. `repl.py`：提供互動式命令介面。
8. `main.py`：程式進入點。

## 三、支援功能

本系統目前支援：

- `int`、`char`、`void`
- 變數宣告與指派
- 一維陣列
- 函式定義與呼叫
- 遞迴函式
- 算術、比較、邏輯與位元運算
- `if / else`
- `while`
- `for`
- `break`
- `continue`
- `return`
- `printf` 等常用內建函式
- 互動式指令操作

## 四、程式流程

程式執行時，使用者可以直接進入互動式介面，或透過命令列指定 `.sc` 檔案。若進入互動式介面，可以用 `APPEND` 或 `LOAD` 建立程式碼，再使用 `CHECK` 進行語法檢查，最後使用 `RUN` 執行 `main()` 函式。

執行流程如下：

```text
Small-C Source
      ↓
Lexer 詞法分析
      ↓
Parser 語法分析
      ↓
AST 抽象語法樹
      ↓
Interpreter 執行
      ↓
輸出結果
```

## 五、測試案例

本專案提供以下測試檔：

1. `tests/basic.sc`：基本四則運算與 `printf`
2. `tests/variables.sc`：變數宣告、指派與複合指派
3. `tests/if_loop.sc`：`if / else`、`while`、`for`
4. `tests/array.sc`：一維陣列寫入與讀取
5. `tests/function.sc`：遞迴函式 Fibonacci
6. `tests/sort.sc`：Bubble sort 綜合測試

## 六、錯誤處理

本系統將錯誤分為三類：

1. `LexError`：詞法錯誤，例如無法辨識的字元。
2. `ParseError`：語法錯誤，例如缺少分號或括號。
3. `RuntimeSmallCError`：執行期錯誤，例如除以零、變數未宣告、陣列越界。

## 七、目前限制

本系統是 Small-C 解譯器的簡化版，目前尚未完整實作：

- 指標
- `scanf`
- 多維陣列
- 完整 `char[]` 字串記憶體模型
- 前置處理器 `#define`

## 八、心得與改進方向

透過本次專題，可以了解解譯器的基本架構，包含詞法分析、語法分析、AST 建立與執行階段。未來可以進一步加入完整的記憶體模型，讓指標、字串與陣列更接近 C 語言的實際行為，也可以補上 `scanf`、`#define` 與更完整的錯誤提示，使系統更接近完整 Small-C 互動式解譯器。
