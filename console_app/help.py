
overview = "Command tool to interact with (my) AI-generated prompts repository API."
basic_info = """
---------------------

Usage: [command] [args]

---------------------

BASIC COMMANDS:
	register, login, logout:
		They to what you would expect.
    
    mine:
        To interact with stuff created by the user(You).
        
        :[available args]
            s (scenario):
                Gets your scenarios. Public or not.
            st (scenarios tagged with):
                Gets your scenarios tagged with an specific tag.
            f (folder)
               -XXX-
               Gets your folders, can be filtered by tag as well 
               (ft)
            

    get:
    	(get) content publicly available or users.
    	
        :[available args]
            Mostly the same as the \"mine\" command, just with 
            public content.
        
        u (user):
            Shows all users in the platform
        us (user scenarios):
            pretty self explanatory, differs from \"mine\" in 
            the fact that only gets public content.
        uf (user folders):
            -XXX-
        
        f (folder)
            -XXX-
            Public folders, can be tagged (ft)
        fs (folder scenarios)
            -XXX-
            Get a particualr folder details, including children folders 
            and scenarios

    make, edit, delete:
         s (scenario):
            Performs said operations using a file (scenario.txt) to 
            make/edit your scenario and post it (published or not). 
            It can also include worlinfo (worldinfo.txt). However, once 
            you create a WI entry, you can not edit the keys via \"edit s\" 
            command, if you do so you will not be able to edit the entry again, 
            and the keys will not even update!
            
            Also, I just realized that you can only add one-line 
            prompts, AN and moemory. Whoops
         
         f (folder):
            -XXX-
            Same as before, just without the .txt files.

    clear:
        clears the screen (duh).
"""
advanced_info = """
QUICK COMMANDS:
    !: 
        \"!\" followed by a name looks for a particular scenario to show, 
        
        Ex: !loli hentai

    #: 
        \"#\" followed by a tag shows public content with that particular tag
        
        Ex: #guro
    
    u:
        Just \"u\", without args. Looks for a user and shows his scenarios.

-------------
SPECIAL COMMANDS:

    rate:
        Used in a scenario detail view to rate it (0-5) and add a review.
        If you want to edit or delete it you will have to go to the scenario ratings.

    add:
        -XXX-
        Used to add WI to the scenario you are looking at.

    make, edit, delete:
        used in particular views to perform those actions.
"""
