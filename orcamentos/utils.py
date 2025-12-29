import math

def calcular_imposicao(papel_largura, papel_altura, item_largura, item_altura, margem_papel=5):
    """
    Calcula o melhor aproveitamento (Normal ou Rotacionado).
    Retorna um dicionário com os dados para desenho e quantidade.
    """
    # Área útil do papel (descontando margem técnica da máquina/pinça)
    area_w = papel_largura - (margem_papel * 2)
    area_h = papel_altura - (margem_papel * 2)

    if item_largura <= 0 or item_altura <= 0 or area_w <= 0 or area_h <= 0:
        return None

    # CENÁRIO 1: Item na orientação original
    cols_1 = math.floor(area_w / item_largura)
    rows_1 = math.floor(area_h / item_altura)
    total_1 = cols_1 * rows_1

    # CENÁRIO 2: Item rotacionado (90 graus)
    cols_2 = math.floor(area_w / item_altura)
    rows_2 = math.floor(area_h / item_largura)
    total_2 = cols_2 * rows_2

    # Decide o vencedor
    melhor_cenario = {
        'total': 0,
        'cols': 0,
        'rows': 0,
        'item_w_final': item_largura, # Para desenho
        'item_h_final': item_altura,  # Para desenho
        'orientacao': 'original'
    }

    if total_1 >= total_2:
        melhor_cenario.update({'total': total_1, 'cols': cols_1, 'rows': rows_1})
    else:
        melhor_cenario.update({
            'total': total_2, 
            'cols': cols_2, 
            'rows': rows_2,
            'item_w_final': item_altura, # Inverte para desenhar
            'item_h_final': item_largura,
            'orientacao': 'rotacionado'
        })
    
    # Calcula dimensões finais do grid e offset para centralização
    grid_w = melhor_cenario['cols'] * melhor_cenario['item_w_final']
    grid_h = melhor_cenario['rows'] * melhor_cenario['item_h_final']
    
    # Centraliza no papel
    offset_x = (papel_largura - grid_w) / 2
    offset_y = (papel_altura - grid_h) / 2

    # Gera lista de posições absolutas de cada retângulo
    rectangles = []
    for row in range(melhor_cenario['rows']):
        for col in range(melhor_cenario['cols']):
            rectangles.append({
                'x': offset_x + (col * melhor_cenario['item_w_final']),
                'y': offset_y + (row * melhor_cenario['item_h_final'])
            })

    melhor_cenario.update({
        'grid_w': grid_w,
        'grid_h': grid_h,
        'offset_x': offset_x,
        'offset_y': offset_y,
        'rectangles': rectangles
    })
    
    return melhor_cenario