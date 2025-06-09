#!/usr/bin/env python3
import datetime
import tkinter as tk


def update_clock():
    now = datetime.datetime.now()
    current_time = now.strftime('%H:%M:%S')
    clock_label.config(text=current_time)

    # Calculate how long until the next full second
    ms_until_next_second = 1000 - now.microsecond // 1000
    root.after(ms_until_next_second, update_clock)

root = tk.Tk()
root.title("Precise Digital Clock")

clock_label = tk.Label(root, font=('Helvetica', 10), bg='black', fg='cyan')
clock_label.pack(padx=1, pady=1)

update_clock()
root.mainloop()
