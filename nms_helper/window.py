"""Ventana de aplicación: la misma interfaz web dentro de una ventana propia.

En Windows usa **pywebview** sobre WebView2 (el runtime viene con Windows 10/11
y con Edge). Es opcional a propósito: si no está instalado, `run.py` cae al
navegador y todo sigue funcionando con la stdlib sola.

    pip install pywebview
"""
from __future__ import annotations

import sys

from .paths import ICON_FILE

TITULO = "NMS Helper"
FONDO = "#0a0e17"


def disponible() -> bool:
    try:
        import webview  # noqa: F401
    except Exception:  # noqa: BLE001 - que falte o esté roto, da igual
        return False
    return True


def motivo() -> str:
    """Qué falta para poder abrir la ventana (para el aviso al usuario)."""
    try:
        import webview  # noqa: F401
    except ImportError:
        return ("no está instalado pywebview (pip install pywebview)")
    except Exception as exc:  # noqa: BLE001
        return f"pywebview no se puede usar: {exc}"
    if sys.platform != "win32":
        return "la ventana con WebView2 solo está preparada para Windows"
    return ""


def _poner_icono(ventana) -> None:
    """Icono propio en la barra de tareas (si la ventana lo permite)."""
    if not ICON_FILE.exists():
        return
    try:
        import ctypes
        hwnd = int(getattr(ventana.native, "Handle", 0) or 0)
        if not hwnd:
            return
        user32 = ctypes.windll.user32
        # IMAGE_ICON=1, LR_LOADFROMFILE|LR_DEFAULTSIZE=0x10|0x40
        hicon = user32.LoadImageW(None, str(ICON_FILE), 1, 0, 0, 0x10 | 0x40)
        if not hicon:
            return
        user32.SendMessageW(hwnd, 0x0080, 1, hicon)   # WM_SETICON, ICON_BIG
        user32.SendMessageW(hwnd, 0x0080, 0, hicon)   # ICON_SMALL
    except Exception:  # noqa: BLE001 - el icono es un extra, nunca un fallo
        pass


def abrir(url: str, ancho: int = 1320, alto: int = 860) -> None:
    """Abre la ventana y **no vuelve hasta que se cierre**.

    Al cerrarse, `webview.start()` regresa y quien llama apaga el servidor.
    """
    import webview

    ventana = webview.create_window(
        TITULO, url, width=ancho, height=alto,
        min_size=(940, 620), background_color=FONDO, text_select=True,
    )
    _poner_icono(ventana)
    try:
        webview.start(debug=False)
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo abrir la ventana: {exc}")
        print("Se abrirá en el navegador.")
        import webbrowser
        webbrowser.open(url)
        _esperar_hasta_que_se_cierre()


def _esperar_hasta_que_se_cierre() -> None:
    import time
    print("Ctrl+C para salir.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
