from copy import copy

bridgeDict = {"Apprehension Point" : (267, 265),
"Awkward Point" : (225, 365),
"Bacon Hollow" : (242, 373),
"Badger's Gate" : (276, 264),
"Bat Cave" : (249, 282),
"Betz Snoring" : (241, 291),
"Bohane's Nest" : (252, 344),
"Bradey's Ark" : (260, 344),
"Breakneck Point" : (219, 261),
"Chancy Bridge" : (215, 193),
"Cheesequake Mill" : (249, 296),
"Chignall Smeally" : (272, 284),
"Court Owen" : (235, 305),
"Creaky Bridge" : (228, 350),
"Crumbling Point" : (258, 315),
"Crumbly Bridge" : (278, 289),
"Doubtful Bridge" : (253, 253),
"Duntisbourne Leer" : (278, 305),
"East Gate" : (273, 213),
"Elf Bridge" : (252, 364),
"Floodgate" : (290, 330),
"Frail Bridge" : (260, 286),
"Gooseneck Ridge" : (223, 269),
"Gophers Wenlock" : (248, 368),
"Greasy Bridge" : (285, 329),
"Hambone Mill" : (260, 373),
"Haphazard Point" : (240, 241),
"Hedgehog Ridge" : (262, 371),
"Hehir Eaves" : (302, 352),
"Hoyland Susie" : (256, 306),
"Interim Bridge" : (189, 339),
"Knife Bridge" : (219, 332),
"Langkilde Wallop" : (272, 373),
"Long Bridge" : (272, 267),
"Loose Bridge" : (238, 213),
"Maginn Herring" : (305, 370),
"Michael's Gout" : (264, 316),
"Moss Bridge" : (241, 202),
"Nice Bridge" : (211, 318),
"Nine Mile Mill" : (266, 356),
"Nine Mole Hill" : (254, 356),
"Nissan's Row" : (233, 206),
"Oiled Bridge" : (258, 239),
"Old Washaway" : (257, 294),
"Oxen Hollow" : (248, 362),
"Petulant Point" : (226, 206),
"Poxon's Molehill" : (232, 358),
"Puddle Hill" : (241, 296),
"Ramshackle Point" : (225, 255),
"Ransom Hill" : (279, 362),
"Ratnam Hythe" : (294, 361),
"Rickety Point" : (280, 327),
"Shaky Bridge" : (264, 320),
"Shrew Hollow" : (234, 343),
"Sietsma's Bumpstead" : (276, 338),
"Slick Bridge" : (268, 328),
"Slippery Gate" : (247, 312),
"Smith's Bump" : (240, 251),
"South Bridge" : (232, 374),
"Splendid Bridge" : (212, 278),
"Stoats' Hammer" : (239, 193),
"Stopgap Bridge" : (221, 254),
"Straw Bridge" : (311, 315),
"Susie's Anthill" : (275, 356),
"Swell Bridge" : (313, 301),
"Thorny Point" : (210, 323),
"Tick Hollow" : (231, 269),
"Tom's Gurney" : (226, 282),
"Tottering Gate" : (280, 295),
"Treacherous Bridge" : (244, 360),
"Trumpet Mill" : (222, 375),
"Turnip Hill" : (222, 377),
"Unstable Point" : (272, 342),
"Vertigo Point" : (258, 250),
"Wallowleigh Bridge" : (249, 348),
"Washout Bridge" : (196, 267),
"Weak Bridge" : (185, 269),
"Weasel Hollow" : (235, 301),
"West Bridge" : (228, 332),
"Wobbly Bridge" : (217, 224),
"Woodgate" : (211, 306),
"Yaphet Kotto" : (254, 358),
"Zig Zag Ridge" : (246, 301)}

cityDict = {"Ahmedsbath" : (226, 386),
"Ainsley-on-Tharp" : (179, 396),
"Allergen-by-the-Sea" : (217, 220),
"Ashby-on-Humidor" : (290, 333),
"Betws-y-Moel" : (226, 291),
"Bishops Itchington" : (125, 104),
"Blakey Stoke" : (194, 398),
"Bogcester" : (152, 48),
"Brigand's Eden" : (251, 373),
"Burnside" : (280, 373),
"Burnt Ox" : (310, 291),
"Butter Hollow" : (294, 308),
"Butterfield" : (222, 384),
"Caerperlewygol" : (213, 285),
"Clifton-over-Sands" : (236, 323),
"Colinsbrough" : (150, 126),
"Crayton" : (274, 272),
"Crosley-in-Oblongshire" : (226, 184),
"Dalton-upon-Gyden" : (238, 203),
"Damp Wellan" : (283, 308),
"Dixon Arms" : (322, 299),
"Drabcester" : (131, 110),
"Dwfrbwlch" : (210, 320),
"East Hograve" : (154, 99),
"Exultation" : (217, 215),
"Fahey-on-Kubrick" : (261, 352),
"Freyja's Hof" : (290, 374),
"Frige's Mount" : (239, 188),
"Frisby-on-the-Sly" : (236, 355),
"Folly Gate" : (272, 279),
"Gatemouth" : (200, 386),
"Ginforth" : (330, 317),
"Gingham-on-Kinski" : (261, 325),
"Greater Kimbrough" : (249, 288),
"Grove of Dyfed" : (169, 372),
"Grove of Gwynedd" : (181, 278),
"Gum Neck" : (270, 236),
"Gwalad-yr-Ahmed" : (189, 342),
"Hammond Regis" : (296, 379),
"Hickingbotham" : (238, 343),
"Hog Ben" : (217, 189),
"Hopton Wafers" : (258, 375),
"Jacobs Folly" : (103, 25),
"Jodhpurs-on-the-Wakely" : (257, 365),
"Johnstones Regret" : (309, 294),
"Kymford" : (315, 304),
"Letterhead" : (197, 113),
"Lintberry" : (287, 317),
"Little Bogcester" : (148, 55),
"Little Rhombus" : (130, 76),
"Littlefield" : (288, 376),
"London" : (301, 341),
"Marshbourne" : (156, 62),
"Maybelleburgh" : (323, 326),
"Meat Camp" : (171, 56),
"Merthyr Phyrne" : (212, 272),
"Milton-on-Sea" : (310, 375),
"Moles' Basket" : (293, 314),
"Mutiny Woulds" : (324, 365),
"Nether Poppleton" : (147, 112),
"Nobread" : (153, 122),
"Ox Sock" : (264, 358),
"Palebottom" : (296, 312),
"Pinnebog" : (169, 213),
"Poppleton Coldfield" : (149, 109),
"Poxons Detour" : (168, 100),
"Prunedale" : (282, 219),
"Rendell-upon-Tindiht" : (253, 235),
"Rohan-on-Sykes" : (297, 368),
"Sandwich Landing" : (120, 104),
"Shankly Mallet" : (223, 261),
"Short Asgard" : (294, 316),
"Sockburn" : (137, 414),
"Sour Biscuit" : (235, 310),
"Surly" : (281, 323),
"Sykesford Forum" : (302, 362),
"Tanbark-on-Guy" : (177, 188),
"Thunor's Gate" : (297, 319),
"Thunor's Pillar" : (284, 312),
"Tingle Heath" : (270, 231),
"Toad Hop" : (137, 139),
"Two Man" : (117, 62),
"Tyrstead" : (209, 161),
"Ullr's Cross" : (256, 311),
"Upper Aidanbry" : (126, 73),
"Waksberg" : (279, 275),
"Wallowleigh" : (239, 346),
"Wetmouth" : (289, 311),
"Wheat Rust" : (331, 302),
"Witenagemot of Sussex" : (262, 380),
"Witenagemot of Wessex" : (228, 362),
"Woden's Brow" : (292, 308),
"Wonton-upon-Gate" : (199, 384)}

landmarkDict = copy(bridgeDict)
landmarkDict.update(cityDict)

initialUs = ["Ahmedsbath",
"Allergen-by-the-Sea",
"Brigand's Eden",
"Burnside",
"Butterfield",
"Clifton-over-Sands",
"Crosley-in-Oblongshire",
"Dalton-upon-Gyden",
"Exultation",
"Freyja's Hof",
"Frige's Mount",
"Frisby-on-the-Sly",
"Greater Kimbrough",
"Gum Neck",
"Hammond Regis",
"Hickingbotham",
"Hog Ben",
"Hopton Wafers",
"Jodhpurs-on-the-Wakely",
"Littlefield",
"Milton-on-Sea",
"Prunedale",
"Rendell-upon-Tindiht",
"Shankly Mallet",
"Sour Biscuit",
"Tingle Heath",
"Wallowleigh",
"Witenagemot of Sussex",
"Witenagemot of Wessex",]

initialThem = ["Ashby-on-Humidor",
"Burnt Ox",
"Butter Hollow",
"Crayton",
"Damp Wellan",
"Dixon Arms",
"Fahey-on-Kubrick",
"Folly Gate",
"Ginforth",
"Gingham-on-Kinski",
"Johnstones Regret",
"Kymford",
"Lintberry",
"London",
"Maybelleburgh",
"Moles' Basket",
"Mutiny Woulds",
"Ox Sock",
"Palebottom",
"Rohan-on-Sykes",
"Short Asgard",
"Surly",
"Sykesford Forum",
"Thunor's Gate",
"Thunor's Pillar",
"Ullr's Cross",
"Waksberg",
"Wetmouth",
"Wheat Rust",
"Woden's Brow"]

initialWales = ["Betws-y-Moel",
"Caerperlewygol",
"Dwfrbwlch",
"Grove of Dyfed",
"Grove of Gwynedd",
"Gwalad-yr-Ahmed",
"Merthyr Phyrne"]

initialCornwall = ["Ainsley-on-Tharp",
"Blakey Stoke",
"Gatemouth",
"Sockburn",
"Wonton-upon-Gate"]

initialScotland = ["Bishops Itchington",
"Bogcester",
"Colinsbrough",
"Drabcester",
"East Hograve",
"Letterhead",
"Little Bogcester",
"Little Rhombus",
"Marshbourne",
"Meat Camp",
"Nether Poppleton",
"Nobread",
"Poppleton Coldfield",
"Poxons Detour",
"Sandwich Landing",
"Toad Hop",
"Two Man",
"Upper Aidanbry"]

initialIndependent = ["Jacobs Folly",
"Pinnebog"]

initialNorthumberland = ["Tanbark-on-Guy",
"Tyrstead"]



if __name__ == "__main__":
    from maproom import *
   
    xOffRange = range(-25, 26)
    yOffRange = range(-25, 26)
   
    Unit.start()

    for identity, unitObj in Unit.roster.items():
        x, y = unitObj.coordinates
        for xOff in xOffRange:
            xTarget = x + xOff
            if xTarget > 0:
                for yOff in yOffRange:
                    yTarget = y + yOff
                    if yTarget > 0:
                        coord = xTarget, yTarget
                        targetTile = Destination.landDict[(coord)]
                        if (not isinstance(targetTile, Water)) or isinstance(targetTile, River):
                            d = Destination(coord)
                            print d.findPath((x, y), True)
        Destination.savePathLookup()

    pairs = landmarkDict.items()
    for key, coord in pairs:
        d = Destination(key)
        observer2 = Unit(1, coord, key)
        Messenger.savePerfectMap(observer2, testForDouble=False, showMessengers=False)
        del observer2
        noPathYet = True
        strikes = 0
        for inkey, incoord in pairs:
            if inkey != key:
                print inkey, "\t",
                path = d.findPath(incoord, True)
                if noPathYet:
                    if path:
                        noPathYet = False
                    else:
                        if strikes > 1:
                            break
                        strikes += 1
        Destination.savePathLookup()
            

        
    """ 
    from math import sqrt
    
    def distance(markone, marktwo):
        x1, y1 = cityDict[markone]
        x2, y2 = cityDict[marktwo]
        xDisp = x1 - x2
        yDisp = y1 - y2
        return sqrt(xDisp * xDisp + yDisp * yDisp)
        
    print distance("Burnside", "Hog Ben") * 2.5    
    """
    
    
    """
    
    results = []
    for key in cityDict.keys():
        results.append((distance("Thunor's Pillar", key), key),)
        
    results.sort()
    
    for key, value in results:
        print int(key), value
        
    import pygame
    
    #pygame.font.init()
    #cityFont = pygame.font.SysFont('garamond', 12, bold=1, italic=0)
    
    screen = pygame.display.set_mode((340 * 3, 425 * 3),)
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, 340 * 3, 425 * 3))
    
    #for key, (xin, yin) in cityDict.items():
    #    x = xin * 3
    #    y = yin * 3
    #    markText = "".join(["        ", key])
    #    textSurface = cityFont.render(markText, True, (255, 255, 255))
    #    screen.blit(textSurface, (x, y)) 
    for us in initialUs:
        x, y = cityDict[us]
        pygame.draw.rect(screen, (255, 99, 95), (x * 3, y * 3, 16, 16))
        pygame.draw.rect(screen, (0, 0, 0), (x * 3, y * 3, 16, 16), 1)
        pygame.display.flip()
    for them in initialThem:
        x, y = cityDict[them]
        pygame.draw.rect(screen, (95, 99, 255), (x * 3, y * 3, 16, 16))
        pygame.draw.rect(screen, (0, 0, 0), (x * 3, y * 3, 16, 16), 1)
        pygame.display.flip() 
    for wales in initialWales:
        x, y = cityDict[wales]
        pygame.draw.rect(screen, (91, 255, 91), (x * 3, y * 3, 16, 16))
        pygame.draw.rect(screen, (0, 0, 0), (x * 3, y * 3, 16, 16), 1)
        pygame.display.flip()      
    for northhumber in initialNorthumberland:
        x, y = cityDict[northhumber]
        pygame.draw.rect(screen, (139, 143, 0), (x * 3, y * 3, 16, 16))
        pygame.draw.rect(screen, (0, 0, 0), (x * 3, y * 3, 16, 16), 1)
        pygame.display.flip()
    for corn in initialCornwall:
        x, y = cityDict[corn]
        pygame.draw.rect(screen, (143, 4, 143), (x * 3, y * 3, 16, 16))
        pygame.draw.rect(screen, (0, 0, 0), (x * 3, y * 3, 16, 16), 1)
        pygame.display.flip()
    for scott in initialScotland:
        x, y = cityDict[scott]
        pygame.draw.rect(screen, (0, 143, 139), (x * 3, y * 3, 16, 16))
        pygame.draw.rect(screen, (0, 0, 0), (x * 3, y * 3, 16, 16), 1)
        pygame.display.flip()
    for ind in initialIndependent:
        x, y = cityDict[ind]
        pygame.draw.rect(screen, (123, 127, 123), (x * 3, y * 3, 16, 16))
        pygame.draw.rect(screen, (0, 0, 0), (x * 3, y * 3, 16, 16), 1)
        pygame.display.flip()         
        
    pygame.image.save(screen, "initialcities.bmp")

"""
