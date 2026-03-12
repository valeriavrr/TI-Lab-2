import tkinter as tk
from tkinter import filedialog, messagebox
from stream_cipher import StreamCipher
from bitarray import bitarray

class MainForm:
    def __init__(self, root):
        self.root = root
        self.root.title("TI Lab_2")
        self.cipher_logic = StreamCipher()

        self.reg_input_var = tk.StringVar()
        self.reg_input_var.trace_add("write", self.update_length_label)

        self.setup_menu()
        self.setup_ui()

    def handle_cipher(self):
        if len(self.entry_reg.get()) != 25:
            messagebox.showwarning("Внимание", "Длина регистра должна равняться 25 состояниям")
            return
        if len(self.out_plain.get("1.0", tk.END).strip()) == 0:
            messagebox.showwarning("Внимание", "Выберите файл с вашим исходным текстом для шифрования/дешифрования")
            return
        self.cipher_logic.produce_bit_register(self.entry_reg.get())
        self.cipher_logic.produce_bit_key(len(self.cipher_logic.plain_text))
        self.set_readonly_text(self.out_key, self.bit_array_to_str(self.cipher_logic.bit_key))
        self.cipher_logic.cipher()
        self.set_readonly_text(self.out_cipher, self.bit_array_to_str(self.cipher_logic.cipher_bit))

    def setup_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self.open_file)
        file_menu.add_command(label="Сохранить в файл", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        menubar.add_command(label="Очистить поля", command=self.clear_fields)

        self.root.config(menu=menubar)

    def setup_ui(self):
        self.center_window(600, 600)
        tk.Label(self.root, text="Состояние регистра (25 состояний)", font=("Arial", 10, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(10, 0))

        vcmd = (self.root.register(self.validate_bits), '%P')
        self.entry_reg = tk.Entry(self.root, textvariable=self.reg_input_var, validate='key', validatecommand=vcmd)
        self.entry_reg.grid(row=1, column=0, columnspan=3, sticky="we", padx=20, pady=5)

        self.label_len = tk.Label(self.root, text="Длина введенных состояний: 0")
        self.label_len.grid(row=2, column=0, columnspan=3, sticky="w", padx=20)

        self.btn_action = tk.Button(self.root, text="Зашифровать/Дешифровать", command=self.handle_cipher)
        self.btn_action.grid(row=3, column=0, columnspan=3, pady=15)

        tk.Label(self.root, text="Сгенерированный ключ:").grid(row=4, column=0, sticky="w", padx=(40,10))
        self.out_key = tk.Text(self.root,  height=4, width=50, state='disabled')
        self.out_key.grid(row=5, column=0, sticky="nswe", padx=(40,10), pady=(0, 10))

        tk.Label(self.root, text="Исходный файл:").grid(row=6, column=0, sticky="w", padx=(40,10))
        self.out_plain = tk.Text(self.root, height=4, width=50, state='disabled')
        self.out_plain.grid(row=7, column=0, sticky="nswe", padx=(40, 10), pady=(0,10))

        tk.Label(self.root, text="Зашифрованный файл:").grid(row=4, column=1, sticky="w", padx=(10,40))
        self.out_cipher = tk.Text(self.root, height=4, width=30, state='disabled')  # Используем Text для высоты
        self.out_cipher.grid(row=5, column=1, rowspan=3, sticky="nswe", padx=(10, 40), pady=(0, 10))

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(5, weight=1)
        self.root.rowconfigure(7, weight=1)

    def center_window(self, width=700, height=450):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)

        self.root.geometry(f'{width}x{int(height)}+{int(x)}+{int(y)}')

    def validate_bits(self, new_value):
        return all(c in "01" for c in new_value)

    def update_length_label(self, *args):
        length = len(self.reg_input_var.get())
        self.label_len.config(text=f"Длина введенных состояний: {length}")

    def set_readonly_text(self, widget, text):
        widget.config(state='normal')
        if isinstance(widget, tk.Entry):
            widget.delete(0, tk.END)
            widget.insert(0, text)
        else:
            widget.delete(1.0, tk.END)
            widget.insert(tk.END, text)
            widget.config(state='disabled')

    def clear_fields(self):
        self.reg_input_var.set("")

        self.out_cipher.config(state='normal')
        self.out_cipher.delete("1.0", tk.END)
        self.out_cipher.config(state='disabled')

        self.out_key.config(state='normal')
        self.out_key.delete("1.0", tk.END)
        self.out_key.config(state='disabled')

        self.out_plain.config(state='normal')
        self.out_plain.delete("1.0", tk.END)
        self.out_plain.config(state='disabled')

        self.cipher_logic.plain_text = None

    def bit_array_to_str(self, bit_arr):
        length = len(bit_arr)
        if length <= 320:
            return bit_arr.to01()
        else:
            first_part = bit_arr[:160].to01()
            last_part = bit_arr[-160:].to01()
            return f"Первые 20 байт:\n{first_part}\n\nПоследние 20 байт:\n{last_part}"

    def open_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        with open(path, "rb") as f:
            file_bytes = f.read()

        plain_bits = bitarray(endian='little')
        plain_bits.frombytes(file_bytes)

        self.cipher_logic.plain_text = plain_bits
        display_text = self.bit_array_to_str(plain_bits)
        self.set_readonly_text(self.out_plain, display_text)

    def save_file(self):
        path = filedialog.asksaveasfilename()
        if not path: return

        result_bytes = self.cipher_logic.cipher_bit.tobytes()
        with open(path, "wb") as f:
            f.write(result_bytes)

        messagebox.showinfo("Успешно", "Файл сохранен")