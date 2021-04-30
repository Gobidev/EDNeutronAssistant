import tkinter as tk
import tkinter.ttk as ttk
import json
import requests
import threading
import urllib.parse


class SystemAutocompleteCombobox(ttk.Combobox):

    def __init__(self, *args, **kwargs):
        ttk.Combobox.__init__(self, *args, **kwargs)
        self.completion_list = []
        self.hits = []
        self.hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self.completion_list

    def set_completion_list(self, completion_list):
        self.completion_list = sorted(completion_list, key=str.lower)
        self.hits = []
        self.hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self.completion_list

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())

        hits = []
        for element in self.completion_list:
            if element.lower().startswith(self.get().lower()):
                hits.append(element)

        if hits != self.hits:
            self.hit_index = 0
            self.hits = hits

        if hits == self.hits and self.hits:
            self.hit_index = (self.hit_index + delta) % len(self.hits)

        if self.hits:
            self.delete(0, tk.END)
            self.insert(0, self.hits[self.hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):

        threading.Thread(target=self.update_completion_list).start()

        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        if event.keysym == "Left":
            if self.position < self.index(tk.END):
                self.delete(self.position, tk.END)
            else:
                self.position = self.position - 1
                self.delete(self.position, tk.END)
        if event.keysym == "Right":
            self.position = self.index(tk.END)
        if len(event.keysym) == 1:
            self.autocomplete()

    def update_completion_list(self):
        self.set_completion_list(
            json.loads(requests.get(
                f"https://www.spansh.co.uk/api/systems?q={urllib.parse.quote_plus(self.get())}").text))
        print(self.completion_list)
