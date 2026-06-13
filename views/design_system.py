# views/design_system.py

# 1. DESIGN TOKENS: TIPOGRAFIA (Centraliza todas as fontes do app)
FONTS = {
    "titulo_secao": ("Arial", 10, "bold"),
    "texto_normal": ("Arial", 10),
    "texto_muted": ("Arial", 9),
    "botao": ("Arial", 10, "bold"),
    "botao_mini": ("Arial", 9, "bold"),
    "console": ("Consolas", 10)
}

# 2. DESIGN TOKENS: ESPAÇAMENTO (Garante que tudo seja simétrico)
SPACING = {
    "padding_janela": 15,
    "gap_pequeno": 5,
    "gap_medio": 10,
    "gap_linhas": 6
}

# 3. DESIGN TOKENS: PALETAS DE CORES (Movido do Model para cá!)
TEMAS = {
    "Dark Purple Edition": {
        "fundo_principal": "#0a0a0c", 
        "fundo_card": "#16161a", 
        "destaque": "#6d28d9",
        "destaque_hover": "#7c3aed", 
        "texto": "#f3f4f6", 
        "texto_muted": "#9ca3af",
        "console_bg": "#020203", 
        "console_fg": "#a78bfa"
    },
    "Cyberpunk Terminal": {
        "fundo_principal": "#000000", 
        "fundo_card": "#0a0f0d", 
        "destaque": "#00ff66",
        "destaque_hover": "#33ff88", 
        "texto": "#cbffd9", 
        "texto_muted": "#00aa44",
        "console_bg": "#000000", 
        "console_fg": "#00ff66"
    },
    "Steel Minimalist": {
        "fundo_principal": "#f3f4f6", 
        "fundo_card": "#ffffff", 
        "destaque": "#1e40af",
        "destaque_hover": "#2563eb", 
        "texto": "#1f2937", 
        "texto_muted": "#4b5563",
        "console_bg": "#1f2937", 
        "console_fg": "#ffffff"
    }
}