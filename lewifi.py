#!/usr/bin/python
# lewifi.py
# by Carl F Karsten

from pythonwifi.iwlibs import Wireless
import wx
from wx.lib.floatcanvas import NavCanvas, FloatCanvas

floorplan = 'carlfloorplan.png'
datafile = 'carlfloorplan.dat'

def wifidata(iface):
    """
    return a list of data about the current wifi conditions.
    """
    stat, qual, discard, missed_beacon = iface.getStatistics()
    return qual

def getifname():
    """
    returns the interface name - typically eth1.
    currently just uses the first wireless one it finds.
    """
    from pythonwifi.iwlibs import getNICnames
    ifaces=getNICnames()
    iface=ifaces[0]
    if len(ifaces)>1:
        print "Found these interfaces: %s" % (ifaces,)
        print "using the first one: %s" % (iface,)

    return iface

class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size = (270, 270))

        self.CreateStatusBar() 

        # Add: the Canvas
        self.Canvas = NavCanvas.NavCanvas(self,-1,
                                     size = (500,500),
                                     ProjectionFun = None,
                                     Debug = 0,
                                     BackgroundColor = "DARK SLATE BLUE",
                                     ).Canvas

        Image = wx.Image(floorplan)
        self.Canvas.AddScaledBitmap(Image, (0,0), Height = Image.GetSize()[1], Position = "tl")

        FloatCanvas.EVT_MOTION(self.Canvas, self.OnMove )
        self.Canvas.Bind(FloatCanvas.EVT_LEFT_DOWN, self.OnMouseEvent)

        self.Center()
        self.plot_file()
        

    def OnMouseEvent(self, event):
        if event.LeftDown():
            # x, y = event.GetX(),event.GetY()
            x, y = tuple(event.Coords)
            x,y=int(x),int(y)

            # get current wifi signal data
            qual = wifidata(self.wifi)
            # qual.quality, qual.signallevel, qual.noiselevel,
            spot=( x,y, qual.quality, qual.signallevel, qual.noiselevel)        
            self.savespot(*spot)
            self.plotspot(*spot)        
            self.Canvas.Draw(True)

    def OnMove(self, event):
        self.SetStatusText("%.2f, %.2f"%tuple(event.Coords))

    def savespot(self, *args):
        print args
        row = ', '.join(str(a) for a in args)
        file(datafile,'a').write( row+"\n" )

    def plotspot(self, x, y, quality, level, noise):
        """
        draws a spot for a data point.
        Signal quality is used to determine color of dot,
        with arbritrary cutoffs at 85 and 65.
        Signal Level is used for the size        
        Noise is the width of the outline, can drown out signal
        """

        # once alpha is working with FloatCanvas, 
        # 2 more bytes of data can be visualized.
        # or at least the floor plan won't get obscured.
        
        qalpha = 128

        if quality>85:
            qColor=wx.Colour(0, 255, 0, qalpha) # green
        elif quality>65:
            qColor=wx.Colour(255, 255, 0, qalpha) # yellow
        else:
            qColor= wx.Colour(255, 0, 0, qalpha) # red

        radius = 3+abs(level)

        nalpha = 128
        nWidth = abs(noise/3)
        nColor = wx.Colour(0, 255, 255, nalpha)

        self.Canvas.AddCircle((x,y), radius,
                         LineColor = nColor,
                         LineWidth = nWidth,
                         FillColor = qColor,
                         )


    def plot_file(self):
        try:
            for row in file(datafile).readlines():
                spot=[int(x) for x in row.split(',')]
                self.plotspot(*spot)
        except IOError, e:
            #  'errno', 'filename', 'message', 'strerror']
            print "Error #%s reading file '%s': %s" % (e.errno, e.filename, e.strerror)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'Wifi Mapper')
        frame.Show(True)
        self.SetTopWindow(frame)
        
        # This needs to be tied to a pretty UI, 
        # and it needs to be moved out of the gui setup.
        ifname=getifname()        
        frame.wifi = Wireless(ifname)

        return True

app = MyApp(0)
app.MainLoop()
