from datetime import datetime, date
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap import Style
from ttkbootstrap.dialogs import Messagebox, QueryDialog
from tkcalendar import Calendar
import json
import os
from tkinter import simpledialog

class FoodItem:
    def __init__(self, name, expiry_date, quantity, category):
        self.name = name
        self.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
        self.quantity = quantity
        self.category = category
    
    def to_dict(self):
        """将食物对象转换为字典以便JSON序列化"""
        return {
            'name': self.name,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d'),
            'quantity': self.quantity,
            'category': self.category
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建食物对象"""
        return cls(
            name=data['name'],
            expiry_date=data['expiry_date'],
            quantity=data['quantity'],
            category=data['category']
        )

class FridgeManager:
    def __init__(self):
        self.items = []
        self.data_file = 'fridge_data.json'
        self.load_data()
    
    def save_data(self):
        """保存数据到JSON文件"""
        data = [item.to_dict() for item in self.items]
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        """从JSON文件加载数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = [FoodItem.from_dict(item) for item in data]
        except Exception as e:
            Messagebox.show_error(
                title="错误",
                message=f"加载数据时出错: {str(e)}"
            )
    
    def add_item(self, name, expiry_date, quantity, category):
        """添加食物到冰箱"""
        new_item = FoodItem(name, expiry_date, quantity, category)
        self.items.append(new_item)
        self.save_data()  # 保存更改
    
    def list_all_items(self):
        """列出所有食物"""
        if not self.items:
            print("冰箱是空的！")
            return
        
        print("\n当前冰箱库存:")
        print("名称\t数量\t类别\t过期日期")
        print("-" * 40)
        for item in self.items:
            print(f"{item.name}\t{item.quantity}\t{item.category}\t{item.expiry_date}")
    
    def check_expired(self):
        """检查过期食物"""
        today = date.today()
        expired_items = [item for item in self.items if item.expiry_date < today]
        
        if expired_items:
            print("\n以下食物已过期:")
            for item in expired_items:
                print(f"{item.name} - 过期日期: {item.expiry_date}")
        else:
            print("没有过期食物！")
    
    def remove_item(self, name, quantity):
        """移除食物"""
        for item in self.items:
            if item.name == name:
                if item.quantity <= quantity:
                    self.items.remove(item)
                else:
                    item.quantity -= quantity
                self.save_data()  # 保存更改
                return True
        return False

class FridgeManagerGUI:
    def __init__(self, root):
        self.root = root
        # 使用更现代的主题
        self.style = Style(theme='flatly')  # 改用 flatly 主题，更加现代化
        self.root.title("冰箱食物管理系统")
        self.root.geometry("1000x700")  # 加大窗口尺寸
        self.fridge = FridgeManager()
        
        # 设置主框架
        self.main_frame = ttk.Frame(self.root, padding="30")
        self.main_frame.pack(fill=BOTH, expand=YES)
        
        # 添加更美观的标题
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="🧊 冰箱食物管理系统",  # 添加emoji图标
            font=("Helvetica", 28, "bold"),
            bootstyle="primary"
        )
        title_label.pack(side=LEFT)
        
        # 添加统计信息
        self.stats_label = ttk.Label(
            title_frame,
            text="",
            font=("Helvetica", 12),
            bootstyle="secondary"
        )
        self.stats_label.pack(side=RIGHT, pady=10)
        
        # 创建左右分栏布局
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=BOTH, expand=YES)
        
        # 左侧添加食物区域
        left_frame = ttk.Frame(content_frame, padding="10")
        left_frame.pack(side=LEFT, fill=BOTH, expand=NO)
        
        # 右侧食物列表区域
        right_frame = ttk.Frame(content_frame, padding="10")
        right_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(20, 0))
        
        self.create_add_food_frame(left_frame)
        self.create_food_list_frame(right_frame)
        self.create_action_buttons(left_frame)
        
        # 更新统计信息
        self.update_stats()
        # 刷新列表
        self.refresh_list()

    def create_add_food_frame(self, parent):
        add_frame = ttk.LabelFrame(
            parent,
            text="📝 添加新食物",
            padding="20",
            bootstyle="primary"
        )
        add_frame.pack(fill=X, pady=(0, 10))
        
        # 使用网格布局改善对齐
        fields = [
            ("食物名称:", "name"),
            ("过期日期:", "date"),
            ("数量:", "quantity"),
            ("类别:", "category")
        ]
        
        for i, (label_text, field_type) in enumerate(fields):
            ttk.Label(
                add_frame,
                text=label_text,
                font=("Helvetica", 10)
            ).grid(row=i, column=0, sticky=W, pady=5)
            
            if field_type == "date":
                # 创建日期输入框和日期选择器的容器
                date_frame = ttk.Frame(add_frame)
                date_frame.grid(row=i, column=1, sticky=EW, pady=5, padx=5)
                
                # 创建日期输入框
                self.date_entry = ttk.Entry(date_frame, width=20)
                self.date_entry.pack(side=LEFT, expand=YES, fill=X)
                
                # 设置默认日期为今天
                today = date.today().strftime('%Y-%m-%d')
                self.date_entry.insert(0, today)
                
                # 创建日期选择按钮
                def pick_date():
                    try:
                        # 创建顶层窗口
                        top = ttk.Toplevel(self.root)
                        top.title("选择日期")
                        
                        # 尝试获取当前日期
                        try:
                            current_date = datetime.strptime(self.date_entry.get(), '%Y-%m-%d').date()
                        except:
                            current_date = date.today()
                        
                        # 创建日历控件
                        cal = Calendar(top,
                            selectmode='day',
                            year=current_date.year,
                            month=current_date.month,
                            day=current_date.day,
                            locale='zh_CN',
                            cursor="hand1")
                        cal.pack(padx=10, pady=10)
                        
                        def set_date():
                            date_str = cal.get_date()  # 获取选择的日期
                            # 转换日期格式从 MM/DD/YY 到 YYYY-MM-DD
                            selected_date = datetime.strptime(date_str, '%m/%d/%y')
                            formatted_date = selected_date.strftime('%Y-%m-%d')
                            self.date_entry.delete(0, END)
                            self.date_entry.insert(0, formatted_date)
                            top.destroy()
                        
                        # 添加确认按钮
                        ttk.Button(top, 
                                 text="确认", 
                                 command=set_date,
                                 style="primary.TButton").pack(pady=10)
                        
                        # 设置为模态窗口
                        top.transient(self.root)
                        top.grab_set()
                        
                    except Exception as e:
                        Messagebox.show_error(
                            title="错误",
                            message=f"选择日期时出错: {str(e)}"
                        )
                
                # 添加日期选择按钮
                ttk.Button(
                    date_frame,
                    text="📅",
                    command=pick_date,
                    width=3,
                    bootstyle="primary"
                ).pack(side=LEFT, padx=(5, 0))
            else:
                entry = ttk.Entry(add_frame, width=25)
                entry.grid(row=i, column=1, sticky=EW, pady=5, padx=5)
                setattr(self, f"{field_type}_entry", entry)
        
        # 添加按钮使用渐变色样式
        ttk.Button(
            add_frame,
            text="➕ 添加食物",
            command=self.add_food,
            bootstyle="success-gradient",
            width=20
        ).grid(row=len(fields), column=0, columnspan=2, pady=15)

    def create_food_list_frame(self, parent):
        list_frame = ttk.LabelFrame(
            parent,
            text="📋 食物列表",
            padding="20",
            bootstyle="primary"
        )
        list_frame.pack(fill=BOTH, expand=YES)
        
        # 创建搜索框
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(
            search_frame,
            text="🔍 搜索:",
            font=("Helvetica", 10)
        ).pack(side=LEFT)
        
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_items)
        
        # 改进表格样式
        columns = ("名称", "数量", "类别", "过期日期", "状态")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            bootstyle="primary",
            height=15
        )
        
        # 设置列标题和宽度
        column_widths = {
            "名称": 150,
            "数量": 100,
            "类别": 120,
            "过期日期": 150,
            "状态": 100
        }
        
        for col, width in column_widths.items():
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=width, anchor=CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=VERTICAL,
            command=self.tree.yview,
            bootstyle="primary-round"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def create_action_buttons(self, parent):
        btn_frame = ttk.LabelFrame(
            parent,
            text="⚡ 快捷操作",
            padding="20",
            bootstyle="primary"
        )
        btn_frame.pack(fill=X)
        
        buttons = [
            ("🔍 检查过期", "warning-gradient", self.check_expired),
            ("❌ 移除选中", "danger-gradient", self.remove_selected),
            ("🔄 刷新列表", "info-gradient", self.refresh_list)
        ]
        
        for text, style, command in buttons:
            ttk.Button(
                btn_frame,
                text=text,
                command=command,
                bootstyle=style,
                width=20
            ).pack(pady=5, fill=X)

    def update_stats(self):
        """更新统计信息"""
        total = len(self.fridge.items)
        expired = len([item for item in self.fridge.items 
                      if item.expiry_date < date.today()])
        self.stats_label.configure(
            text=f"总数: {total} | 已过期: {expired}"
        )

    def search_items(self, event=None):
        """搜索功能"""
        search_term = self.search_entry.get().lower()
        self.refresh_list(search_term)

    def refresh_list(self, search_term=""):
        """刷新列表，支持搜索"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        today = date.today()
        for item in self.fridge.items:
            if search_term and search_term not in item.name.lower():
                continue
                
            # 计算状态和样式
            if item.expiry_date < today:
                status = "已过期"
                item_style = "error"  # 使用 ttkbootstrap 的内置样式
            elif (item.expiry_date - today).days <= 3:
                status = "即将过期"
                item_style = "warning"  # 使用 ttkbootstrap 的内置样式
            else:
                status = "正常"
                item_style = "primary"  # 使用 ttkbootstrap 的内置样式
            
            self.tree.insert("", END, values=(
                item.name,
                item.quantity,
                item.category,
                item.expiry_date,
                status
            ), tags=(item_style,))  # 使用 ttkbootstrap 的样式标签
        
        # 配置标签样式
        self.tree.tag_configure("error", foreground="red")
        self.tree.tag_configure("warning", foreground="orange")
        self.tree.tag_configure("primary", foreground="black")
        
        # 更新统计信息
        self.update_stats()

    def sort_treeview(self, col):
        """表格排序功能"""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        l.sort()
        for index, (_, k) in enumerate(l):
            self.tree.move(k, "", index)

    def add_food(self):
        try:
            name = self.name_entry.get()
            expiry_date = self.date_entry.get()  # 直接获取日期字符串
            quantity = int(self.quantity_entry.get())
            category = self.category_entry.get()
            
            if not all([name, expiry_date, category]):
                Messagebox.show_error(
                    title="错误",
                    message="请填写所有字段！"
                )
                return
                
            self.fridge.add_item(name, expiry_date, quantity, category)
            self.refresh_list()
            self.clear_entries()
            Messagebox.show_info(
                title="成功",
                message=f"已添加 {quantity} 个/份 {name}"
            )
        except Exception as e:
            Messagebox.show_error(
                title="错误",
                message=f"添加食物时出错: {str(e)}"
            )

    def clear_entries(self):
        self.name_entry.delete(0, END)
        self.quantity_entry.delete(0, END)
        self.category_entry.delete(0, END)
        # 重置日期为今天
        today = date.today().strftime('%Y-%m-%d')
        self.date_entry.delete(0, END)
        self.date_entry.insert(0, today)

    def check_expired(self):
        try:
            today = date.today()
            expired_items = [item for item in self.fridge.items if item.expiry_date < today]
            
            if expired_items:
                message = "以下食物已过期:\n\n"
                for item in expired_items:
                    message += f"{item.name} - 过期日期: {item.expiry_date}\n"
                Messagebox.show_warning(
                    title="过期提醒",
                    message=message
                )
            else:
                Messagebox.show_info(
                    title="过期提醒",
                    message="没有过期食物！"
                )
        except Exception as e:
            Messagebox.show_error(
                title="错误",
                message=f"检查过期食物时出错: {str(e)}"
            )

    def remove_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_warning(
                title="警告",
                message="请先选择要移除的食物！"
            )
            return
            
        item_values = self.tree.item(selected_item)['values']
        name = item_values[0]
        
        quantity = simpledialog.askinteger(
            "移除食物", 
            f"要移除多少个/份 {name}？",
            parent=self.root,
            minvalue=1
        )
        
        if quantity:
            if self.fridge.remove_item(name, quantity):
                self.refresh_list()
                Messagebox.show_info(
                    title="成功",
                    message=f"已移除 {quantity} 个/份 {name}"
                )
            else:
                Messagebox.show_error(
                    title="错误",
                    message=f"未找到食物: {name}"
                )

# 在文件开头添加样式设置
def setup_styles():
    style = ttk.Style()
    
    # 使用更现代的主题设置，调整颜色以匹配 pulse 主题
    style.configure("Treeview", 
        rowheight=30,
        font=('Helvetica', 10),
        background="#ffffff",
        fieldbackground="#ffffff"
    )

    # 设置选中项的样式 - pulse 主题的主色调
    style.map("Treeview",
        foreground=[("selected", "#ffffff")],
        background=[("selected", "#593196")]  # pulse 主题的紫色
    )

    # 设置表头样式
    style.configure("Treeview.Heading",
        font=('Helvetica', 10, 'bold'),
        background="#f0f0f0",
        foreground="#593196"  # 使用主题的紫色
    )

if __name__ == "__main__":
    # 阻止 tkcalendar 创建额外的根窗口
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    # 创建主窗口，使用 pulse 主题
    setup_styles()
    main_window = ttk.Window(themename="pulse")  # 改用 pulse 主题
    main_window.title("冰箱食物管理系统")
    
    app = FridgeManagerGUI(main_window)
    main_window.mainloop() 