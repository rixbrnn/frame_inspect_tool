"""
Mapeamento centralizado de identificadores internos para rótulos em português.

Usado por scripts que geram figuras para o TCC. Aplicar antes da plotagem.
Modos DLSS, acrônimos técnicos (SSIM, PSNR, LPIPS, FLIP, MDD, etc) e nomes
oficiais de jogos permanecem inalterados conforme convenção do trabalho.
"""

# Nome oficial completo (preferido em rótulos verticais ou contexto curto)
GAME_DISPLAY_NAMES = {
    "blackmyth_medium": "Black Myth: Wukong",
    "cod_mw2_extreme": "Call of Duty: MW2",
    "cyberpunk": "Cyberpunk 2077",
    "cyberpunk_low": "Cyberpunk 2077",
    "forza_extreme": "Forza Horizon 5",
    "forza_motorsport_ultra": "Forza Motorsport",
    "marvel_rivals_low": "Marvel Rivals",
    "rdr2_ultra": "Red Dead Redemption 2",
    "returnal_epic": "Returnal",
    "tomb_raider_highest_scene_1": "Tomb Raider",
    "watch_dogs_legion_very_high": "Watch Dogs Legion",
}

# Versão abreviada para heatmaps e gráficos com pouco espaço
GAME_DISPLAY_NAMES_SHORT = {
    "blackmyth_medium": "Black Myth",
    "cod_mw2_extreme": "CoD: MW2",
    "cyberpunk": "Cyberpunk 2077",
    "cyberpunk_low": "Cyberpunk 2077",
    "forza_extreme": "Forza H5",
    "forza_motorsport_ultra": "Forza MS",
    "marvel_rivals_low": "Marvel Rivals",
    "rdr2_ultra": "RDR2",
    "returnal_epic": "Returnal",
    "tomb_raider_highest_scene_1": "Tomb Raider",
    "watch_dogs_legion_very_high": "Watch Dogs L.",
}


def display_name(game_id, short=False):
    """Retorna o nome oficial do jogo a partir do identificador interno."""
    table = GAME_DISPLAY_NAMES_SHORT if short else GAME_DISPLAY_NAMES
    return table.get(game_id, game_id)


def display_names(game_ids, short=False):
    """Aplica display_name a uma lista/iter de identificadores."""
    return [display_name(g, short=short) for g in game_ids]


def translate_comparison(label):
    """
    Traduz um rótulo de comparação tipo '1080p_DLAA_vs_Balanced'
    para '1080p — DLAA vs Balanced'.
    Modos DLSS permanecem em inglês conforme convenção.
    """
    # Substitui o primeiro underscore (após resolução) por em-dash com espaços,
    # e demais por espaços simples.
    if "_" not in label:
        return label
    parts = label.split("_", 1)
    rest = parts[1].replace("_", " ")
    return f"{parts[0]} — {rest}"
