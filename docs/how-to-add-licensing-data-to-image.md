
*Draft*

It should also be possible to do this using [XMP files](https://wiki.creativecommons.org/wiki/XMP) which can be generated after selecting the license on the [Creative Commons Website](https://creativecommons.org/choose/)

# Adding licensing to image

1. Install [exiftool](http://owl.phy.queensu.ca/~phil/exiftool/)

2. `exiftool -attributionName="Torgny Dellsén" ./icon.png`

3. `exiftool -attributionWebsite="http://torgnydellsen.zenfolio.com/" ./icon.png`

4. `exiftool -WebStatement="http://torgnydellsen.zenfolio.com/" ./icon.png`

5. Verify that the exif data has been updated
<pre>
sunyata@sunyata-Aspire-ES1-131:~/PycharmProjects/buddhist-well-being-pyqt5$ exiftool icon.png 
ExifTool Version Number         : 10.10
File Name                       : icon.png
Directory                       : .
File Size                       : 2.3 kB
File Modification Date/Time     : 2016:10:18 16:24:08+02:00
File Access Date/Time           : 2016:10:18 16:24:08+02:00
File Inode Change Date/Time     : 2016:10:18 16:24:08+02:00
File Permissions                : rw-rw-r--
File Type                       : PNG
File Type Extension             : png
MIME Type                       : image/png
Image Width                     : 24
Image Height                    : 24
Bit Depth                       : 8
Color Type                      : RGB
Compression                     : Deflate/Inflate
Filter                          : Adaptive
Interlace                       : Noninterlaced
Significant Bits                : 8 8 8
XMP Toolkit                     : Image::ExifTool 10.10
<b>Attribution Name                : Torgny Dellsén</b>
<b>License                         : http://creativecommons.org/licenses/by-sa/4.0/</b>
<b>Web Statement                   : http://torgnydellsen.zenfolio.com/</b>
Image Size                      : 24x24
Megapixels                      : 0.000576
sunyata@sunyata-Aspire-ES1-131:~/PycharmProjects/buddhist-well-being-pyqt5$ 
</pre>

