from PIL import Image

def analyze_image():
    img = Image.open('/home/rajesh/Documents/GitHub/homexo/static/icons/nri.png').convert('RGBA')
    width, height = img.size
    
    tl = img.getpixel((0,0))
    tr = img.getpixel((width-1, 0))
    bl = img.getpixel((0, height-1))
    br = img.getpixel((width-1, height-1))
    center = img.getpixel((width//2, height//2))
    
    print(f"Top-Left: {tl}")
    print(f"Top-Right: {tr}")
    print(f"Bottom-Left: {bl}")
    print(f"Bottom-Right: {br}")
    print(f"Center: {center}")

analyze_image()
