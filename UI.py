import tkinter as tk
import tkinter.messagebox as msg
import cv2
import PIL.Image, PIL.ImageTk


class MainWindow:

    def __init__(self, title="Main Window", w=800, h=600, font="Microsoft YaHei UI"):
        self.title = title
        self.w = w
        self.h = h
        self.geometry = "%dx%d" % (w, h)
        self.font = font

        self.window = tk.Tk()
        self.window.title(self.title)
        self.window.geometry(self.geometry)

        lab = tk.Label(
            self.window,
            text="人臉管理系統",
            font=(self.font, 24),
            fg="white",
            bg="green",
            height=1
        )
        lab.pack(expand=tk.NO, fill=tk.X)

        frm = tk.Frame(
            self.window,
            bg="red",
            width=100,
            height=100
        )
        frm.pack_propagate(0)
        frm.place(x=10, y=55)

        btn_new = tk.Button(
            frm,
            text="新增用戶",
            font=(self.font, 16),
            command=self.onclick_btn_new
        )
        btn_new.pack(fill=tk.BOTH, expand=tk.YES)

    def run(self):
        self.window.mainloop()

    def onclick_btn_new(self):
        w = NewUserTopLevel(self.title)


class NewUserTopLevel:

    def __init__(self, title="", w=800, h=600, font="Microsoft YaHei UI"):
        self.title = title
        self.w = w
        self.h = h
        self.geometry = "%dx%d" % (w, h)
        self.font = font

        self.window = tk.Toplevel()
        self.window.title = self.title
        self.window.geometry(self.geometry)
        self.window.grab_set()
        self.window.focus()

        lab = tk.Label(
            self.window,
            text="新增用戶",
            font=(self.font, 24),
            fg="white",
            bg="green",
            height=1
        )
        lab.pack(fill=tk.X)

        frm = tk.Frame(
            self.window,
            bg="red",
            width=400,
            height=50
        )
        frm.pack_propagate(0)
        frm.place(x=80, y=55)

        self.txt_name = tk.Entry(
            frm,
            show=None,
            font=(self.font, 24)
        )
        self.txt_name.pack(fill=tk.BOTH, expand=tk.YES)
        self.txt_name.focus()

        frm = tk.Frame(
            self.window,
            bg="red",
            width=100,
            height=50
        )
        frm.pack_propagate(0)
        frm.place(x=420, y=55)

        self.btn_set_name = tk.Button(
            frm,
            text="設置",
            font=(self.font, 16),
            width=100,
            command=self.onclick_btn_set_name
        )
        self.btn_set_name.pack(fill=tk.BOTH, expand=tk.YES)

        self.canvas = tk.Canvas(
            self.window,
            width=640,
            height=480,
            bg='red'
        )
        self.canvas.pack(side=tk.BOTTOM)

    def onclick_btn_set_name(self):
        name = self.txt_name.get()
        name = name.strip()
        if name == "":
            msg.showinfo(title="Message", message="要輸入名稱！")
        else:
            self.txt_name.config(state="disabled")
            self.btn_set_name.config(state="disabled")
            self.cap = cv2.VideoCapture(0)
            self.update()

    def update(self):
        if self.cap.isOpened():
            success, frame = self.cap.read()
            if success:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.frame = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(322, 242, image=self.frame)
        self.window.after(100, self.update)


if __name__ == "__main__":
    MainWindow().run()
