"""
Tener las funciones escritas en este archivo en un buffer de texto 
puede causar problemas de indentacion en algunos editores debido a
las secuencias de escape
"""
def clear(): print("\033[H\033[2J", end="", flush=True)

def altscreen(set: bool):
    seq = "\033[?1049h" if set else "\033[?1049l"
    print(seq, end="", flush=True)
