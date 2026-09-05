import sys 

def Beep(x:int , y:int) -> None:
    if sys.platform == 'win32':
        import winsound
        winsound.Beep(x, y)
        
    elif sys.platform == 'linux':
        pass 
        
