import pygame

def render_text_centered(surface, text, font, rect, color):
    """
    Metni verilen dikdörtgenin tam ortasına çizer.
    Eğer metin sığmazsa otomatik olarak küçültür.
    """
    text_surf = font.render(text, True, color)
    
    # Metin kutudan taşarsa küçült (Scale down)
    if text_surf.get_width() > rect.width - 10:
        ratio = (rect.width - 10) / text_surf.get_width()
        new_w = int(text_surf.get_width() * ratio)
        new_h = int(text_surf.get_height() * ratio)
        text_surf = pygame.transform.smoothscale(text_surf, (new_w, new_h))

    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)