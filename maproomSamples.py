import pygame, string
import maproom

MIN_SATURATION    = 0.1
SATURATION_COEFFS = [0.958, 0.338, -1.181]
MIN_COLOUR_VALUE  = 0.2
SAMPLES_PER_PAGE  = 24
OFFSET            = 24
PREFIX            = 'huesample'
SUFFIX            = '.bmp'
HEIGHT            = 40
WIDTH             = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT * SAMPLES_PER_PAGE * 2), 0, 24)
pygame.font.init()
gara = pygame.font.SysFont('garamond', 12, bold=0, italic=0)
lower = 0
upper = HEIGHT
pcount = 0
frame = 0
colourValueRange = 1.0 - MIN_COLOUR_VALUE
widthPlusOne = WIDTH + 1
floatWidth = float(WIDTH)

listOfLandKinds = maproom.AdoptionType.classIndex.values()

for landKind in listOfLandKinds:
    pcount += 1
    textSurface = gara.render(landKind.__name__, True, (255, 255, 255))
    screen.blit(textSurface, (0, lower))
    pygame.display.flip()
    for landelevation in range(0, widthPlusOne):
        relativeElevation = landelevation / floatWidth
        colourValue = MIN_COLOUR_VALUE + relativeElevation * colourValueRange
        baseSaturation = ( SATURATION_COEFFS[0] 
                         + SATURATION_COEFFS[1] * colourValue 
                         + SATURATION_COEFFS[2] * colourValue * colourValue )
        if hasattr(landKind, 'relativeSaturation'):
            baseSaturation *= landKind.relativeSaturation        
        colourSaturation = max(MIN_SATURATION, min(1.0, baseSaturation))           
        chroma = colourValue * colourSaturation
        if hasattr(landKind, 'hueDrift'):
            huePrime = ((landKind.hue + relativeElevation * landKind.hueDrift) % 360.0) / 60.0
        else:
            huePrime = (landKind.hue % 360.0) / 60.0
        xTerm = chroma * (1.0 - abs((huePrime % 2.0) - 1.0))
        if huePrime < 1.0:
            colourBase = (chroma, xTerm, 0.0)
        else:
            if huePrime < 2.0:
                colourBase = (xTerm, chroma, 0.0)
            else:
                if huePrime < 3.0:
                    colourBase = (0.0, chroma, xTerm)
                else:
                    if huePrime < 4.0:
                        colourBase = (0.0, xTerm, chroma)
                    else:
                        if huePrime < 5.0:
                            colourBase = (xTerm, 0.0, chroma)
                        else:
                            colourBase = (chroma, 0.0, xTerm)
        chromaGap = colourValue - chroma
        colour = (255.0 * (colourBase[0] + chromaGap), 
                  255.0 * (colourBase[1] + chromaGap), 
                  255.0 * (colourBase[2] + chromaGap))
        pygame.draw.line(screen, colour, (landelevation, lower + OFFSET), (landelevation, upper + OFFSET))
    pygame.display.flip()
    lower += HEIGHT * 2
    upper += HEIGHT * 2
    if pcount == SAMPLES_PER_PAGE or landKind == listOfLandKinds[-1]:
        frame += 1
        pcount = 0
        frameNumber = string.zfill(frame, 2)
        filename = PREFIX + frameNumber + SUFFIX
        lower = 0
        upper = HEIGHT
        pygame.image.save(screen, filename)
        pygame.draw.rect(screen,(0,0,0),(0,0,WIDTH, HEIGHT * SAMPLES_PER_PAGE * 2))
