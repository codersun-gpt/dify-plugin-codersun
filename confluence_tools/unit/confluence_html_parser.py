from html.parser import HTMLParser
import re

def extract_language(parameters):
    """从 data-macro-parameters 中提取语言信息"""
    match = re.search(r'language=(\w+)', parameters)
    lang = match.group(1) if match else 'plaintext'
    if lang == 'js':
        print(lang)
    return lang


class ConfluenceHTMLParser(HTMLParser):
    """HTML parser for converting Confluence page content to Markdown format."""
    def __init__(self, add_level_mark: bool = False, mark_prefix: str = "L_"):
        # 设置convert_charrefs=False以确保CDATA内容被正确处理
        super().__init__(convert_charrefs=False)
        super().__init__(convert_charrefs=False)
        # 存储最终 Markdown 的各行
        self.md_lines = []
        # 当前累积的普通文本（或单元格内容）
        self.current_text = ""
        # 是否添加层级标记
        self.add_level_mark = add_level_mark
        self.mark_prefix = mark_prefix
        
        # 代码块相关
        self.in_pre = False
        self.current_code_text = ""
        # 内联代码标记
        self.in_inline_code = False
        # 表格中的pre标签标识
        self.table_pre = False

        # 标题相关
        self.in_heading = False
        self.heading_level = 0

        # 普通表格相关
        self.in_table = False
        self.current_table = []   # 每一项为一行：列表中存放 cell 字典
        # 当前行（列表），每个 cell 为字典 {text, cell_type, rowspan, colspan}
        self.current_row = []
        self.in_cell = False      # 正在处理表格单元格
        self.cell_info = None     # 正在构造的单元格信息

        # 代码宏相关（独立的代码块）
        self.in_code_macro = False
        self.code_macro_language = None

        # 标识是否处于代码块宏 table 中（Confluence 中代码块以 table 包裹）
        self.in_code_table = False
        # 标识是否处于代码块宏单元格中
        self.in_code_cell = False
        # 标识是否处于代码块宏的文本体中
        self.in_code_text_body = False
        # 标识是否处于CDATA中
        self.in_cdata = False
        # 标识是否处于ac:parameter标签中
        self.in_parameter = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        # 优先处理 table 标签：如果有 data-macro-name="code"，视为代码块宏
        if tag == "table":
            if attr_dict.get("data-macro-name") == "code":
                self.flush_current_text()
                # 切换到代码块宏模式，无论是否嵌套在单元格内
                self.in_code_table = True
                self.in_code_macro = True
                self.code_macro_language = extract_language(
                    attr_dict.get("data-macro-parameters", ""))
                # 后续标签（如 <tbody>, <tr>, <td>）内部忽略，等待 <pre>
                return
            else:
                # 普通表格
                self.flush_current_text()
                self.in_table = True
                self.current_table = []
                return

        # 处理代码宏标签
        if tag == "ac:structured-macro" and attr_dict.get("ac:name") == "code":
            self.in_code_cell = True
            return

        # 处理代码宏的语言参数
        if tag == "ac:parameter":
            self.in_parameter = True
            if self.in_code_cell and attr_dict.get("ac:name") == "language":
                self.code_macro_language = None  # 等待handle_data设置语言
            return

        # 处理代码宏的文本体
        if self.in_code_cell and tag == "ac:plain-text-body":
            self.in_code_text_body = True
            if self.in_table and self.in_cell:
                self.cell_info["text"] += f"`{self.code_macro_language} "
            else:
                self.add_line(f"\n```{self.code_macro_language}")
            return

        # 如果当前处于代码块宏 table 内，但标签不是 <pre>，则忽略其内部标签
        if self.in_code_table and tag != "pre":
            return

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.flush_current_text()
            self.in_heading = True
            self.heading_level = int(tag[1])
        elif tag == 'p':
            self.flush_current_text()
        elif tag == 'br':
            self.current_text += "\n"
        elif tag == 'pre':
            self.flush_current_text()
            # 若当前处于代码块宏 table，则按代码块处理
            if self.in_code_table:
                self.in_pre = True
                self.current_code_text = ""
                # 如果嵌套在普通表格单元格中，代码块将追加到 cell 文本中
                if self.in_table and self.in_cell:
                    self.cell_info["text"] += f"`{self.code_macro_language} "
                else:
                    self.add_line(f"\n```{self.code_macro_language}")
                return
            # 普通 pre 标签（可能在表格中或页面中）
            elif self.in_table and self.in_cell:
                self.in_pre = True
                self.current_code_text = ""
                self.table_pre = True
            else:
                self.in_pre = True
                self.current_code_text = ""
                if self.in_code_macro and self.code_macro_language:
                    self.add_line(f"\n```{self.code_macro_language}")
                else:
                    self.add_line("\n```")
        elif tag == 'code':
            # 内联代码
            if not self.in_pre:
                self.current_text += "`"
                self.in_inline_code = True
        elif tag == 'tr':
            if self.in_table:
                self.current_row = []
        elif tag in ['td', 'th']:
            if self.in_table:
                self.in_cell = True
                # 初始化单元格数据，提取 rowspan 与 colspan 属性
                rowspan = int(attr_dict.get("rowspan", "1"))
                colspan = int(attr_dict.get("colspan", "1"))
                self.cell_info = {
                    "text": "",
                    "cell_type": tag,
                    "rowspan": rowspan,
                    "colspan": colspan
                }

    def add_line(self, line):
        """添加行到 markdown 输出中，避免连续空行"""
        # 如果是空行
        if not line.strip():
            # 如果列表为空或者最后一行不是空行，才添加这个空行
            if not self.md_lines or self.md_lines[-1].strip():
                self.md_lines.append(line)
            # 如果最后一行已经是空行，则跳过这个空行，避免连续空行
            return
        
        # 非空行直接添加
        self.md_lines.append(line)

    def unknown_decl(self, data):
        """
        当遇到未知声明时（例如 <![CDATA[...]]>），将其视为数据处理。
        """
        # 检查是否为 CDATA 声明
        if data.startswith("CDATA["):
            content = data[len("CDATA["):]
            if self.in_code_text_body:
                if self.in_table and self.in_cell:
                    # 在表格单元格中，将换行符替换为空格，避免破坏markdown表格格式
                    content = content.replace('\n', ' ')
                    self.cell_info["text"] += content
                else:
                    self.current_code_text += content

    def handle_data(self, data):
        # 如果在parameter标签中且不是language参数，直接返回
        if self.in_parameter:
            if self.code_macro_language is None:
                self.code_macro_language = data
            return

        # 处理代码宏文本体中的内容
        if self.in_code_text_body:
            if "[CDATA[" in data:
                self.in_cdata = True
                data = data.split("[CDATA[")[1]
            if "]]" in data and self.in_cdata:
                self.in_cdata = False
                data = data.split("]]")[0]

            if self.in_table and self.in_cell:
                self.cell_info["text"] += data.replace('\n', ' ')
            else:
                self.current_code_text += data
            return

        # 若处于代码块宏 table 中且在 pre 内，则收集代码文本
        if self.in_code_table and self.in_pre:
            if self.in_table and self.in_cell:
                self.current_code_text += data.replace('\n', ' ')
            else:
                self.current_code_text += data
            return

        # 在普通表格单元格内，将文本追加到当前 cell
        if self.in_table and self.in_cell:
            self.cell_info["text"] += data
        elif self.in_pre:
            # 普通 pre 标签处理
            if hasattr(self, "table_pre") and self.table_pre:
                self.cell_info["text"] += data
            else:
                self.current_code_text += data
        else:
            self.current_text += data

    def handle_endtag(self, tag):
        # 处理代码宏的结束标签
        if tag == "ac:structured-macro" and self.in_code_cell:
            self.in_code_cell = False
            return

        if tag == "ac:parameter":
            self.in_parameter = False
            return

        if tag == "ac:plain-text-body" and self.in_code_text_body:
            self.in_code_text_body = False
            if self.in_table and self.in_cell:
                self.cell_info["text"] += "`"
            else:
                self.add_line(self.current_code_text)
                self.add_line("```\n")
                self.current_code_text = ""
            return

        # 如果处于代码块宏 table 中，但标签不是 pre 或 table，则忽略结束标签
        if self.in_code_table and tag not in ['pre', 'table']:
            return

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading_text = self.current_text.strip()
            # 根据是否添加层级标记生成标题
            if self.add_level_mark:
                self.add_line("\n" + ("#" * self.heading_level) + " " + self.mark_prefix + str(self.heading_level) + " " + heading_text + "\n")
            else:
                self.add_line("\n" + ("#" * self.heading_level) + " " + heading_text + "\n")

            self.current_text = ""
            self.in_heading = False
            self.heading_level = 0
        elif tag == 'p':
            self.add_line(self.current_text.strip() + "\n")
            self.current_text = ""
        elif tag == 'code':
            if self.in_inline_code:
                self.current_text += "`"
                self.in_inline_code = False
        elif tag == 'pre':
            if self.in_code_table:
                self.in_pre = False
                if self.in_table and self.in_cell:
                    # 在表格中使用单行代码格式
                    self.cell_info["text"] += self.current_code_text.replace(
                        '\n', ' ') + "`"
                else:
                    # 页面中使用多行代码块格式
                    self.add_line(self.current_code_text)
                    self.add_line("```\n")
                self.current_code_text = ""
            elif hasattr(self, "table_pre") and self.table_pre:
                self.in_pre = False
                self.table_pre = False
            else:
                self.in_pre = False
                self.add_line(self.current_code_text)
                self.add_line("```\n")
                self.current_code_text = ""
        elif tag == 'table':
            if self.in_code_table:
                # 结束代码块宏 table，不生成表格 Markdown
                self.in_code_table = False
                self.in_code_macro = False
                self.code_macro_language = None
                return
            elif self.in_table:
                self.flush_current_text()
                table_md = self.convert_table_to_markdown(self.current_table)
                # 如果当前在表格单元格内，将生成的表格 Markdown 追加到 cell 文本中
                if self.in_table and self.in_cell:
                    self.cell_info["text"] += "\n" + table_md + "\n"
                else:
                    self.add_line("\n" + table_md + "\n")
                self.in_table = False
                self.current_table = []
                return
        elif tag == 'tr':
            if self.in_table:
                if self.current_row:
                    self.current_table.append(self.current_row)
                self.current_row = []
        elif tag in ['td', 'th']:
            if self.in_table and self.in_cell:
                self.current_row.append(self.cell_info)
                self.in_cell = False
                self.cell_info = None

    def flush_current_text(self):
        if self.current_text.strip():
            self.add_line(self.current_text.strip())
            self.current_text = ""

    def convert_table_to_markdown(self, table):
        """
        将解析后的表格数据转换为 Markdown 表格。
        支持 rowspan 与 colspan（采用简单算法逐行填充跨行单元格）。
        对于包含代码块的单元格，会保留代码块中的换行符。
        """
        if not table:
            return ""
        markdown_table = []
        col_spans = []  # 每一列剩余跨行计数
        num_cols = 0
        for row in table:
            markdown_row = []
            col_index = 0
            # 填充因跨行而空出的单元格
            while col_index < len(col_spans) and col_spans[col_index] > 0:
                markdown_row.append("   ")
                col_spans[col_index] -= 1
                col_index += 1
            for cell in row:
                # 填充前置空白（极端情况）
                while col_index < len(col_spans) and col_spans[col_index] > 0:
                    markdown_row.append("   ")
                    col_spans[col_index] -= 1
                    col_index += 1
                text = cell.get("text", "").strip()
                text = text.replace('\n', ' ')  # 将所有换行符替换为空格
                rowspan = cell.get("rowspan", 1)
                colspan = cell.get("colspan", 1)
                markdown_row.append(text)
                for _ in range(colspan - 1):
                    markdown_row.append("   ")
                for _ in range(colspan):
                    if col_index < len(col_spans):
                        col_spans[col_index] = rowspan - \
                            1 if rowspan > 1 else 0
                    else:
                        col_spans.append(rowspan - 1 if rowspan > 1 else 0)
                    col_index += 1
            while col_index < len(col_spans) and col_spans[col_index] > 0:
                markdown_row.append("   ")
                col_spans[col_index] -= 1
                col_index += 1
            if not markdown_table:
                num_cols = len(markdown_row)
            row_str = "| " + " | ".join(markdown_row) + " |"
            markdown_table.append(row_str)
        if len(markdown_table) > 1:
            header_sep = "| " + " | ".join(["---"] * num_cols) + " |"
            markdown_table.insert(1, header_sep)
        return "\n".join(markdown_table) + "\n"

    def get_markdown(self):
        self.flush_current_text()
        
        # 先将所有行连接起来，然后按行重新分割
        raw_content = "\n".join(self.md_lines)
        all_lines = raw_content.split('\n')
        
        # 处理连续空行，保留一个空行
        cleaned_lines = []
        prev_line_empty = False
        
        for line in all_lines:
            is_empty = not line.strip()
            
            # 如果当前行是空行
            if is_empty:
                # 只有在前一行不是空行时才添加这个空行
                if not prev_line_empty:
                    cleaned_lines.append(line)
                prev_line_empty = True
            else:
                # 非空行直接添加
                cleaned_lines.append(line)
                prev_line_empty = False
        
        return "\n".join(cleaned_lines)