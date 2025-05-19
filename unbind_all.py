from keyboard_event import *

def unbind(f=None):
    print("unbinding all keys...")
    if f is None:
        f=ReleaseKey
    for i in range(512):
        f(i)
        
if __name__=="__main__":
    unbind(ReleaseKey)