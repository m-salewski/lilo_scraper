
def verbprint(verb):

    def meth(text):

        if verb:
            print(text)
            
        return None
    
    return meth
