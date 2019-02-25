if __name__ == "__main__":
    from maproom import *
    from landmarks import *
    import pygame


    screen = pygame.display.set_mode((340 * 10, 425 * 10),)
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, 340 * 10, 425 * 10))
      
    eg2 = ElevGrid(("uktopo.tga", "veg2.tga", "river.tga", "roads2.tga"),)

    fullDict = eg2.landDict()

    Destination.setLandDict(fullDict)
    fullList = fullDict.values()

    for land in fullList:
        inx, iny = land.coordinates
        x = inx * 10
        y = iny * 10
        if land.elevation == 0:
            alternColour = (255, 255, 255)
        else:
            alternColour = (0, 0, 0)
        #screen.set_at((x, y), alternColour)
        pygame.draw.rect(screen, alternColour, (x, y, 10, 10))
    
    for us in initialUs:
        x, y = landmarkDict[us]
        pygame.draw.rect(screen, (255, 99, 95), (x * 10, y * 10, 34, 52))
        pygame.draw.rect(screen, (0, 0, 0), (x * 10, y * 10, 34, 52), 1)
        pygame.display.flip()
    for them in initialThem:
        x, y = landmarkDict[them]
        pygame.draw.rect(screen, (95, 99, 255), (x * 10, y * 10, 34, 52))
        pygame.draw.rect(screen, (0, 0, 0), (x * 10, y * 10, 34, 52), 1)
        pygame.display.flip() 
    for wales in initialWales:
        x, y = landmarkDict[wales]
        pygame.draw.rect(screen, (91, 255, 91), (x * 10, y * 10, 34, 52))
        pygame.draw.rect(screen, (0, 0, 0), (x * 10, y * 10, 34, 52), 1)
        pygame.display.flip()      
    for northhumber in initialNorthumberland:
        x, y = landmarkDict[northhumber]
        pygame.draw.rect(screen, (139, 143, 0), (x * 10, y * 10, 34, 52))
        pygame.draw.rect(screen, (0, 0, 0), (x * 10, y * 10, 34, 52), 1)
        pygame.display.flip()
    for corn in initialCornwall:
        x, y = landmarkDict[corn]
        pygame.draw.rect(screen, (143, 4, 143), (x * 10, y * 10, 34, 52))
        pygame.draw.rect(screen, (0, 0, 0), (x * 10, y * 10, 34, 52), 1)
        pygame.display.flip()
    for scott in initialScotland:
        x, y = landmarkDict[scott]
        pygame.draw.rect(screen, (0, 143, 139), (x * 10, y * 10, 34, 52))
        pygame.draw.rect(screen, (0, 0, 0), (x * 10, y * 10, 34, 52), 1)
        pygame.display.flip()
    for ind in initialIndependent:
        x, y = landmarkDict[ind]
        pygame.draw.rect(screen, (123, 127, 123), (x * 10, y * 10, 34, 52))
        pygame.draw.rect(screen, (0, 0, 0), (x * 10, y * 10, 34, 52), 1)
        pygame.display.flip()         
        
    #while True:
    #    pygame.display.flip()
        
    pygame.image.save(screen, "outline.bmp")


    if False:

        CROP_LEFT       = 66
        BORDER_THICK_X  = 35
        BORDER_THICK_Y  = 70
        OUT_WIDTH       = 336 - CROP_LEFT + 2 * BORDER_THICK_X
        OUT_HEIGHT      = 418 + BORDER_THICK_Y + BORDER_THICK_X
        OUT_FILE_SUFFIX = ".bmp"
        PAGE_BOUND      = 100

        screen = pygame.display.set_mode((PAGE_BOUND * 2 + OUT_WIDTH * 3, PAGE_BOUND * 2 + OUT_HEIGHT * 3),)
        cellPosition = 1
        page = 1
        screen.fill((255, 255, 255),)
        for landname in landmarkDict.keys():
            OUT_FILE = "".join([landname.lower().replace(' ', ''), OUT_FILE_SUFFIX])
            print OUT_FILE
            citySurf = pygame.image.load(OUT_FILE)
            if cellPosition == 1 or cellPosition == 4 or cellPosition == 7:
                xOff = 0
            elif cellPosition == 2 or cellPosition == 5 or cellPosition == 8:
                xOff = OUT_WIDTH
            else:
                xOff = 2 * OUT_WIDTH
            if cellPosition == 1 or cellPosition == 2 or cellPosition == 3:
                yOff = 0
            elif cellPosition == 4 or cellPosition == 5 or cellPosition == 6:
                yOff = OUT_HEIGHT
            else:
                yOff = 2 * OUT_HEIGHT         
            screen.blit(citySurf, (xOff + PAGE_BOUND, yOff + PAGE_BOUND))
            pygame.display.flip()
            if cellPosition == 9:
                cellPosition = 1
                pageName = str(page) + OUT_FILE_SUFFIX
                if page < 10:
                    pageName = "0" + pageName
                page += 1
                pygame.image.save(screen, pageName)
                screen.fill((255, 255, 255),)
            else:
                cellPosition += 1

        pageName = str(page) + OUT_FILE_SUFFIX
        page += 1
        if len(pageName) == 1:
            pageName = "0" + pageName
        pygame.image.save(screen, pageName)

        
    if False:


        CIRCLE_COLOUR   = (251, 255, 0)
        INNER_RADIUS    = 2
        OUTER_RADIUS    = 21
        THICKNESS       = 2
        CROP_LEFT       = 66
        BORDER_THICK_X  = 35
        BORDER_THICK_Y  = 70
        BOUNDS_THICK    = 7
        TEXT_OFFSET_X   = 21
        TEXT_OFFSET_Y   = 21
        OUT_WIDTH       = 336 - CROP_LEFT + 2 * BORDER_THICK_X
        OUT_HEIGHT      = 418 + BORDER_THICK_Y + BORDER_THICK_X
        OUT_FILE_SUFFIX = ".bmp"

        pygame.font.init()

        landmarkFont = pygame.font.SysFont('garamond', 28, bold=1, italic=0)

        eg2 = ElevGrid(("uktopo.tga", "veg2.tga", "river.tga", "roads2.tga"),)

        fullDict = eg2.landDict()

        Destination.setLandDict(fullDict)
        fullList = fullDict.values()
        highestPeak = max([land.elevation for land in fullList])    
        BACKGROUND_COLOUR = (0, 0, 51)
        MIN_SATURATION = 0.1
        SATURATION_COEFFS = [0.958, 0.338, -1.181]
        MIN_COLOUR_VALUE = 0.25
        screen = pygame.display.set_mode((OUT_WIDTH, OUT_HEIGHT),)

        for landname, (landx, landy) in landmarkDict.items():
            screenLandX = landx - CROP_LEFT + BORDER_THICK_X
            if screenLandX > BORDER_THICK_X:
                landcoords = (screenLandX, landy + BORDER_THICK_Y)
                pygame.draw.rect(screen, BACKGROUND_COLOUR, (0, 0, OUT_WIDTH, OUT_HEIGHT))
                for land in fullList:
                    inx, iny = land.coordinates
                    x = inx - CROP_LEFT + BORDER_THICK_X
                    if x > BORDER_THICK_X:
                        y = iny + BORDER_THICK_Y
                        if land.elevation == 0:
                            alternColour = BACKGROUND_COLOUR
                        else:
                            colourValueRange = 1.0 - MIN_COLOUR_VALUE
                            relativeElevation = land.elevation / highestPeak
                            colourValue = MIN_COLOUR_VALUE + relativeElevation * colourValueRange
                            baseSaturation = ( SATURATION_COEFFS[0] 
                                             + SATURATION_COEFFS[1] * colourValue 
                                             + SATURATION_COEFFS[2] * colourValue * colourValue )
                            if hasattr(land, 'relativeSaturation'):
                                baseSaturation *= land.relativeSaturation
                            colourSaturation = max(MIN_SATURATION, min(1.0, baseSaturation))           
                            chroma = colourValue * colourSaturation
                            if hasattr(land, 'hueDrift'):
                                huePrime = ((land.hue + relativeElevation * land.hueDrift) % 360.0) / 60.0
                            else:
                                huePrime = (land.hue % 360.0) / 60.0
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
                            alternColour = (255.0 * (colourBase[0] + chromaGap), 
                                            255.0 * (colourBase[1] + chromaGap), 
                                            255.0 * (colourBase[2] + chromaGap))
                        screen.set_at((x, y), alternColour)  
                pygame.draw.circle(screen, CIRCLE_COLOUR, landcoords, INNER_RADIUS)
                pygame.draw.circle(screen, CIRCLE_COLOUR, landcoords, OUTER_RADIUS, THICKNESS)
                pygame.draw.rect(screen, (0, 0, 0), (0, 0, OUT_WIDTH, OUT_HEIGHT), BOUNDS_THICK)
                textSurface = landmarkFont.render(landname, True, (255, 255, 255))
                screen.blit(textSurface, (TEXT_OFFSET_X, TEXT_OFFSET_Y))        
                OUT_FILE = "".join([landname.lower().replace(' ', ''), OUT_FILE_SUFFIX])
                pygame.display.flip()    
                pygame.image.save(screen, OUT_FILE)        
