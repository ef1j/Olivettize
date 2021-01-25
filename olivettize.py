"""
olivettize.py
Input a text ascii image and generate the simulated printout using character images.
This version will make an image size to reproduce IBM 1403 output and will respond
to form feed characters and Fortran carriage control characters
Based on earlier programs "makeimage2.py" and "ibm1403.py".
 
e.m.f. January 2021

1/5/2021   Implemented image blending for overstrike of single characters
1/11/2021  Added notes on page size; save images as 1200dpi
1/17/2021  Rewritten to use an object class "PrintPage", enable printing title at bottom
1/22/2021  Removed code to print at bottom of page
           introduced pagewidth and pageheight, able to print multiple pages
"""


from PIL import Image, ImageEnhance, ImageChops
Image.MAX_IMAGE_PIXELS = 110486672 # my image size exceeds the DOS warning
import sys, math

"""
A PrintPage is an image object that represents an 8.5x11" paper at 1200dpi.
The cursor is stored by column and row. 
Methods of the class include adding ("printing") a character image to the page.
"""
class PrintPage:
    # IBM1403 paper is 14-7/8" wide and 11" high
    # Olivetti Te-318 is 8.5" wide and 11" high with a printable area
    pagerows = 66
    pagecols = 85
    pagewidth = pagecols*120
    pageheight = pagerows*200 # this was 201
    
    def __init__(self,number):
        # page number
        self.number = number
        # make blank image page (10chars/in, 6 rows/in)
        mode, size, color = 'L', (self.pagewidth, self.pageheight), 255
        self.img = Image.new(mode, size, color)

        # start at top left corner of page
        self.column = 0
        self.row = 0

        # initial offset
        if number == 1: self.voffset = 2
        else: self.voffset = 0
        self.hoffset = 3

    def printchar(self,char):
        # I have 4 versions of the character set for some variation, so files are nnNN
        # nn = 0-3, NN = ASCII value
        if char != ' ': # space character, just advance
            charfile = "chars/" + "{0:02n}".format(self.row % 3) + "{0:02n}".format(char) + ".jpg"
            try:
                with Image.open(charfile) as charimg:
                    width, height = charimg.size
                    imgx = (self.column+self.hoffset)*width
                    imgy = (self.row+self.voffset)*height
                    tempimg = self.img.crop((imgx,imgy,imgx+width,imgy+height))
                    tempimg = ImageChops.darker(tempimg, charimg)
                    self.img.paste(tempimg,(imgx,imgy,imgx+width,imgy+height))
            except OSError:
                print("Error opening character file", charfile, " line ",self.row)
        if self.column <= 79: self.column += 1

"""
 Main program
"""
if __name__ == '__main__':
    """ 
    The text file for an ASCII image is typically 132 columns wide and 66 rows long
    the paper is 14 7/8" wide and 11" long. So the initial indent should be 8 chars
    """
    
    # I'm expecting the text file as the first agument
    # open the file as a binary to capture the CR's
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        try:
            with open(filename, mode='rb') as textfile:
                # initialize the page
                numpage = 1
                page = PrintPage(numpage)
                output = []
                
                # process each line of the text file
                # Rewrite to use the FORTRAN carriage control characters
                for line in textfile:
                    # process each character in line
                    for byte in line:
                        if byte == 10: # new line
                            page.row += 1
                            page.column = 0
                            if page.row == page.pagerows - page.voffset:
                                output.append(page)
                                numpage += 1 # add a page
                                page = PrintPage(numpage)
                        elif byte == 13: # carriage return - overstrike
                            page.column = 0
                        elif byte == 12: # form feed
                            output.append(page)
                            numpage += 1
                            page = PrintPage(numpage)
                        else:
                            # draw each character on the page
                            char = int(byte)
                            if char > 95: char -= 32 # Olivetti only prints 32-95 (0x20-0x59)
                            page.printchar(char)

                # flush the last page to the output
                if numpage > 0:
                    output.append(page)

                pdf = []
                for page in output:
                    print("Printing page ", page.number, " of ", numpage)
                    page.img = page.img.resize((page.pagewidth//2,page.pageheight//2))
                    pdf.append(page.img)
                    # page.img.save(filename.split('.')[0] + '_O_' + str(page.number) + ".jpg", "JPEG", dpi=(600,600))

                print ("Saving PDF...")
                pdf[0].save(filename.split('.')[0] + '.pdf', "PDF", resolution=600.0, save_all=True, append_images=pdf[1:])

                textfile.close()
                
        except OSError:
            print("Error opening", filename)
    else:
        print("\nusage: olivettize.py filename \n")
