# Small-C 互動式解譯器

這是一份可執行的 Python 版 Small-C 簡化解譯器骨架，適合作為期末專題基礎版本。

## 1. 執行方式

進入資料夾後執行：

```bash
python main.py
```

或直接執行測試檔：

```bash
python main.py tests/basic.sc
python main.py tests/variables.sc
python main.py tests/if_loop.sc
python main.py tests/array.sc
python main.py tests/function.sc
python main.py tests/sort.sc
```

## 2. REPL 指令

```text
NEW
LOAD <file>
SAVE <file>
LIST
APPEND
INSERT <line> <code>
DELETE <line>
CHECK
RUN
TRACE ON
TRACE OFF
VARS
FUNCS
HELP
EXIT
```

## 3. 已支援的 Small-C 語法

- `int`、`char`、`void`
- 全域變數、區域變數
- 一維陣列，例如 `int arr[10];`
- 函式定義與呼叫
- 遞迴函式
- 算術運算：`+ - * / %`
- 比較運算：`< <= > >= == !=`
- 邏輯運算：`&& || !`
- 位元運算：`& | ^ ~`
- 指派運算：`= += -= *= /= %=`
- 自增自減：`++ --`
- `if / else`
- `while`
- `for`
- `break`
- `continue`
- `return`

## 4. 已支援的內建函式

- `printf`
- `putchar`
- `getchar`
- `strlen`
- `strcpy`，簡化為回傳複製後字串
- `strcmp`
- `strcat`
- `abs`
- `max`
- `min`
- `pow`
- `rand`
- `srand`

## 5. 專案架構

```text
main.py          程式入口
repl.py          互動式命令介面
lexer.py         詞法分析器
parser.py        語法分析器
ast_nodes.py     AST 節點定義
interpreter.py   解譯執行核心
memory.py        變數、陣列與作用域管理
sc_builtins.py      內建函式
errors.py        錯誤類別
tests/           測試 Small-C 程式
```

## 6. 目前簡化限制

這份版本是「可執行骨架」，不是完整 C 編譯器，因此有以下限制：

1. 指標 `*ptr`、取址 `&x` 尚未完整實作。
2. `scanf` 尚未完整實作。
3. 陣列只支援一維整數陣列。
4. `char[]` 字串陣列尚未完整模擬成 C 的記憶體。
5. `#define` 僅建議作為加分功能後續加入。
6. 函式參數使用值傳遞，陣列作為參數尚未完整支援。

## 7. 建議後續加分方向

- 加上 `scanf`
- 加上真正的指標與記憶體位址模型
- 加上 `char[]` 字串記憶體
- 加上 `#define`
- 加上更完整的錯誤行號與除錯 TRACE
- 加上圖形化或網頁版介面
