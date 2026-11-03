"""Parser leve de valores em INSERT MySQL (strings entre aspas simples)."""

from __future__ import annotations


def parse_mysql_value_list(inner: str) -> list[str | int]:
    inner = inner.strip()
    if inner.startswith('('):
        inner = inner[1:]
    if inner.endswith(')'):
        inner = inner[:-1]
    elif inner.endswith(');'):
        inner = inner[:-2]

    vals: list[str | int] = []
    i = 0
    n = len(inner)
    while i < n:
        while i < n and inner[i] in ' \t\n\r':
            i += 1
        if i >= n:
            break
        if inner[i] == "'":
            i += 1
            buf: list[str] = []
            while i < n:
                ch = inner[i]
                if ch == '\\' and i + 1 < n:
                    buf.append(inner[i + 1])
                    i += 2
                    continue
                if ch == "'":
                    if i + 1 < n and inner[i + 1] == "'":
                        buf.append("'")
                        i += 2
                        continue
                    i += 1
                    break
                buf.append(ch)
                i += 1
            vals.append(''.join(buf))
        elif inner[i].isdigit() or (inner[i] == '-' and i + 1 < n and inner[i + 1].isdigit()):
            j = i + (1 if inner[i] == '-' else 0)
            while j < n and inner[j].isdigit():
                j += 1
            vals.append(int(inner[i:j]))
            i = j
        else:
            raise ValueError(f'Caractere inesperado na posição {i}: {inner[i:i+20]!r}')
        while i < n and inner[i] in ' \t\n\r':
            i += 1
        if i < n and inner[i] == ',':
            i += 1
    return vals
