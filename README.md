Examples
========

## Set up
    Python 2.7.14 (v2.7.14:84471935ed, Sep 16 2017, 20:25:58) [MSC v.1500 64 bit (AMD64)] on win32
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from maproom import *
    pygame 1.9.4
    Hello from the pygame community. https://www.pygame.org/contribute.html
    >>> Unit.start()
    Building elevation grid
    Building vegetation grid
            Expanding vegetation grid
    Building river grid
    Building road grid
    
    Writing land dictionary
    
    Loading lookup table for Destination.findPath()
    initialising Unit: Churls A
    initialising Unit: Churls A-messenger
    initialising Unit: Churls B
    initialising Unit: Churls B-messenger
    initialising Unit: Churls C
    initialising Unit: Churls C-messenger
    initialising Unit: Churls D
    initialising Unit: Churls D-messenger
    initialising Unit: Churls E
    initialising Unit: Churls E-messenger
    initialising Unit: Churls F
    initialising Unit: Churls F-messenger
    initialising Unit: Huscarls A
    initialising Unit: Huscarls A-messenger
    initialising Unit: Huscarls B
    initialising Unit: Huscarls B-messenger
    initialising Unit: Huscarls C
    initialising Unit: Huscarls C-messenger
    initialising Unit: Kentish Royal Guard
    initialising Unit: Kentish Royal Guard-messenger
    initialising Unit: Knights Ecstatic
    initialising Unit: Knights Ecstatic-messenger
    initialising Unit: Skirmishers A
    initialising Unit: Skirmishers A-messenger
    initialising Unit: Skirmishers B
    initialising Unit: Skirmishers B-messenger
    initialising Unit: Thanes A
    initialising Unit: Thanes A-messenger
    initialising Unit: Thanes B
    initialising Unit: Thanes B-messenger
    initialising Unit: Thanes C
    initialising Unit: Thanes C-messenger
    initialising Unit: Honey Eaters 1
    initialising Unit: Honey Eaters 1-messenger
    initialising Unit: Honey Eaters 2
    initialising Unit: Honey Eaters 2-messenger
    initialising Unit: King's Guard
    initialising Unit: King's Guard-messenger
    initialising Unit: Mercian Guard 1
    initialising Unit: Mercian Guard 1-messenger
    initialising Unit: Mercian Guard 2
    initialising Unit: Mercian Guard 2-messenger
    initialising Unit: Mercian Guard 3
    initialising Unit: Mercian Guard 3-messenger
    initialising Unit: Mercian Guard 4
    initialising Unit: Mercian Guard 4-messenger
    initialising Unit: Mercian Guard 5
    initialising Unit: Mercian Guard 5-messenger
    initialising Unit: Mercian Guard 6
    initialising Unit: Mercian Guard 6-messenger
    >>> Unit.showUnits()
    Honey Eaters 2-messenger at (256, 311)
    Thanes B-messenger at (239, 346)
    Skirmishers A at (270, 231)
    Mercian Guard 6-messenger at (246, 301)
    Mercian Guard 3-messenger at (261, 325)
    Honey Eaters 1-messenger at (261, 352)
    Churls F-messenger at (235, 310)
    Huscarls C at (262, 380)
    Huscarls B at (238, 343)
    Huscarls A at (223, 261)
    Skirmishers B at (280, 373)
    Churls C-messenger at (249, 288)
    Mercian Guard 5-messenger at (283, 308)
    Mercian Guard 4-messenger at (274, 272)
    King's Guard at (297, 368)
    Churls A-messenger at (251, 373)
    Kentish Royal Guard-messenger at (290, 374)
    Skirmishers B-messenger at (280, 373)
    Churls B-messenger at (249, 282)
    Skirmishers A-messenger at (270, 231)
    Honey Eaters 1 at (261, 352)
    Mercian Guard 1 at (264, 358)
    Mercian Guard 3 at (261, 325)
    Mercian Guard 2 at (302, 362)
    Mercian Guard 5 at (283, 308)
    Mercian Guard 4 at (274, 272)
    Huscarls A-messenger at (223, 261)
    Mercian Guard 6 at (246, 301)
    Thanes A at (257, 365)
    Honey Eaters 2 at (256, 311)
    Thanes C at (249, 296)
    Thanes B at (239, 346)
    Knights Ecstatic-messenger at (231, 269)
    Churls F at (235, 310)
    Churls E at (223, 269)
    Churls D at (241, 296)
    Churls C at (249, 288)
    Churls B at (249, 282)
    Churls A at (251, 373)
    Mercian Guard 1-messenger at (264, 358)
    Huscarls B-messenger at (238, 343)
    Mercian Guard 2-messenger at (302, 362)
    Kentish Royal Guard at (290, 374)
    Thanes C-messenger at (249, 296)
    Knights Ecstatic at (231, 269)
    Thanes A-messenger at (257, 365)
    Churls E-messenger at (223, 269)
    Churls D-messenger at (241, 296)
    King's Guard-messenger at (297, 368)
    Huscarls C-messenger at (262, 380)
    >>>
    
## Orders
    >>> andy = Commander(1, "Shankly Mallet", "Andy")
    >>> andy.command("Huscarls A")
    >>> andy.command("Churls F")
    >>> andy.command("Churls E")
    >>> andy.command("Knights Ecstatic")
    >>> andy.giveOrder("Knights Ecstatic", "Sockburn", Order.proceed)
    adding new order to outbox
    True
    >>> andy.giveOrder("Churls F", "Sour Biscuit", Order.proceed)
    adding new order to outbox
    True

## Run
    >>> Unit.showNext()
    1331-02-21 09:12:00
    new report for osric
    
    1331-02-21 09:18:00
    new report for osric
    
    1331-02-21 09:24:00
    new report for osric
    
    1331-02-21 09:30:00
    new report for osric
    
    1331-02-21 09:36:00
    new report for osric
    
    1331-02-21 09:42:00
    new report for osric
    
    1331-02-21 09:48:00
    new report for osric
    
    1331-02-21 09:54:00
    new report for osric
    
    1331-02-21 10:00:00
    new report for osric
    
    1331-02-21 10:06:00
    new report for osric
    
    1331-02-21 10:12:00
    new report for osric
    
    1331-02-21 10:18:00
    new report for osric
    
    1331-02-21 10:24:00
    new report for osric
    
    1331-02-21 10:30:00
    new report for osric
    
    1331-02-21 10:36:00
    new report for osric
    
    1331-02-21 10:42:00
    new report for osric
    
    1331-02-21 10:48:00
    new report for osric
    
    1331-02-21 10:54:00
    new report for osric
    
    1331-02-21 11:00:00
    new report for osric
    
    1331-02-21 11:06:00
    new report for osric
    
    1331-02-21 11:12:00
    new report for osric
    
    1331-02-21 11:18:00
    new report for osric
    
    1331-02-21 11:24:00
    new report for osric
    
    1331-02-21 11:30:00
    new report for osric
    
    1331-02-21 11:36:00
    new report for osric
    
    1331-02-21 11:42:00
    new report for osric
    
    1331-02-21 11:48:00
    new report for osric
    
    1331-02-21 11:54:00
    new report for osric
    
    1331-02-21 12:00:00
    new report for osric
    
    1331-02-21 12:06:00
    new report for osric
    
    1331-02-21 12:12:00
    new report for osric
    
    1331-02-21 12:18:00
    new report for osric
    
    1331-02-21 12:24:00
    new report for osric
    
    1331-02-21 12:30:00
    new report for osric
    
    1331-02-21 12:36:00
    new report for osric
    
    1331-02-21 12:42:00
    new report for osric
    
    1331-02-21 12:48:00
    new report for osric
    
    1331-02-21 12:54:00
    new report for osric
    
    1331-02-21 13:00:00
    new report for osric
    
    1331-02-21 13:06:00
    new report for osric
    
    1331-02-21 13:12:00
    new report for osric
    
    1331-02-21 13:18:00
    new report for osric
    
    1331-02-21 13:24:00
    new report for osric
    new report for osric
    
    1331-02-21 13:30:00
    new report for osric
    
    1331-02-21 13:36:00
    new report for osric
    
    1331-02-21 13:42:00
    new report for osric
    
    1331-02-21 13:48:00
    new report for osric
    
    1331-02-21 13:54:00
    new report for osric
    
    1331-02-21 14:00:00
    new report for osric
    
    1331-02-21 14:06:00
    new report for osric
    
    1331-02-21 14:12:00
    new report for osric
    
    1331-02-21 14:18:00
    new report for osric
    
    1331-02-21 14:24:00
    new report for osric
    new report for osric
    
    1331-02-21 14:30:00
    new report for osric
    
    1331-02-21 14:36:00
    new report for osric
    
    1331-02-21 14:42:00
    new report for osric
    
    1331-02-21 14:48:00
    new report for osric
    
    1331-02-21 14:54:00
    new report for osric
    
    1331-02-21 15:00:00
    new report for osric
    
    1331-02-21 15:06:00
    new report for osric
    
    1331-02-21 15:12:00
    new report for osric
    
    1331-02-21 15:18:00
    new report for osric
    
    1331-02-21 15:24:00
    new report for osric
    
    1331-02-21 15:30:00
    new report for osric
    
    1331-02-21 15:36:00
    new report for osric
    new report for osric
    
    1331-02-21 15:42:00
    new report for osric
    
    1331-02-21 15:48:00
    new report for osric
    
    1331-02-21 15:54:00
    new report for osric
    
    1331-02-21 16:00:00
    new report for osric
    
    1331-02-21 16:06:00
    new report for osric
    
    1331-02-21 16:12:00
    new report for osric
    
    1331-02-21 16:18:00
    new report for osric
    
    1331-02-21 16:24:00
    new report for osric
    
    1331-02-21 16:30:00
    new report for osric
    
    1331-02-21 16:36:00
    new report for osric
    
    1331-02-21 16:42:00
    new report for osric
    
    1331-02-21 16:48:00
    new report for osric
    
    1331-02-21 16:54:00
    new report for osric
    
    1331-02-21 17:00:00
    new report for osric
    
    1331-02-21 17:06:00
    new report for osric
    
    1331-02-21 17:12:00
    new report for osric
    
    1331-02-21 17:18:00
    new report for osric
    
    1331-02-21 17:24:00
    new report for osric
    
    1331-02-21 17:30:00
    new report for osric
    
    1331-02-21 17:36:00
    new report for osric
    
    1331-02-21 17:42:00
    new report for osric
    
    1331-02-21 17:48:00
    new report for osric
    new report for osric
    
    1331-02-21 17:54:00
    new report for osric
    
    1331-02-22 08:00:00
    Weekly resolution
    new report for osric
    
    >>>