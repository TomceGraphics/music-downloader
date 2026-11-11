"""Small reusable widgets. Everything uses the tokens in ui/theme.py."""
import customtkinter as ctk

from . import icons
from .theme import (C_BLUE, C_BLUE_HOV, C_BORDER, C_DIM, C_GREEN, C_HOVER, C_INPUT, C_SECONDARY,
                    C_SURFACE, C_TEXT, F, R_LG, R_MD, S2, S3, S4)


class Label(ctk.CTkLabel):
    def __init__(self, parent, text, size=13, weight="normal", color=C_TEXT, **kw):
        super().__init__(parent, text=text, font=F(size, weight), text_color=color, **kw)


def ghost_btn(parent, text, command, width=80, height=34, color=C_TEXT, icon=None) -> ctk.CTkButton:
    """Quiet secondary button (raised fill, optional icon)."""
    return ctk.CTkButton(parent, text=text, command=command, font=F(12), width=width, height=height,
                         fg_color=C_INPUT, hover_color=C_HOVER, text_color=color, corner_radius=R_MD,
                         image=icons.get(icon), compound="left")


def primary_btn(parent, text, command, width=120, height=46, icon=None) -> ctk.CTkButton:
    """The one accent-coloured button on a screen."""
    return ctk.CTkButton(parent, text=text, command=command, font=F(13, "bold"), width=width, height=height,
                         fg_color=C_BLUE, hover_color=C_BLUE_HOV, text_color="#ffffff", corner_radius=R_MD,
                         image=icons.get(icon), compound="left")


def text_input(parent, placeholder="", textvariable=None, height=34) -> ctk.CTkEntry:
    kw = {"textvariable": textvariable} if textvariable else {}
    return ctk.CTkEntry(parent, placeholder_text=placeholder, font=F(13), height=height, fg_color=C_INPUT,
                        border_color=C_BORDER, border_width=1, text_color=C_TEXT,
                        placeholder_text_color=C_DIM, corner_radius=R_MD, **kw)


def section(parent, text: str, pack_side: str = "top") -> None:
    """Small uppercase label."""
    lbl = Label(parent, text.upper(), size=10, weight="bold", color=C_SECONDARY)
    if pack_side == "top":
        lbl.pack(anchor="w")
    else:
        lbl.pack(side=pack_side)


class Card(ctk.CTkFrame):
    """Rounded surface with a title; put content in card.body."""
    def __init__(self, parent, title: str):
        super().__init__(parent, fg_color=C_SURFACE, corner_radius=R_LG)
        Label(self, title.upper(), size=10, weight="bold", color=C_SECONDARY).pack(anchor="w", padx=S4, pady=(S3, S2))
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="x", padx=S4, pady=(0, S4))


class StatusPill(ctk.CTkFrame):
    """Small rounded status: coloured dot + text."""
    def __init__(self, parent):
        super().__init__(parent, fg_color=C_INPUT, corner_radius=14, height=28)
        self.dot = ctk.CTkFrame(self, width=8, height=8, corner_radius=4, fg_color=C_GREEN)
        self.dot.pack(side="left", padx=(S3, S2), pady=S3)
        self.text = Label(self, "ready", size=12, color=C_SECONDARY)
        self.text.pack(side="left", padx=(0, S3))

    def set_text(self, text: str):
        self.text.configure(text=text)

    def set_dot(self, color):
        self.dot.configure(fg_color=color)

