import wx
frame = None

def reportAngle(device, angle):
    global frame
    if not frame:
        print angle
    else:
        frame.displayAngle(angle)

def showAngleMeter():
    global frame
    frame = AngleMeterFrame(root)

class AngleMeterFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "LightHSV Swing Angle", style = wx.DEFAULT_FRAME_STYLE)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.panel = AngleMeterPanel(self)
        self.Show(True)

    def onClose(self, event):
        self.Destroy()

    def displayAngle(self, angle):
        # Display the new angle
        self.panel.text.SetLabel('%d' % angle)

        # Update the gauge
        self.panel.gauge.SetValue(angle)
        self.Refresh()
        
class AngleMeterPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.AngleMeterFrame = parent
        box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(box)
        
        self.text = wx.StaticText(self, -1, "0", (30, 20))
        font = wx.Font(48, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial")
        self.text.SetFont(font)
        box.Add(self.text, 1, wx.ALIGN_CENTER)
        
        self.gauge = wx.Gauge(self, 0, 255, (10, 75), (360, 25))
        self.gauge.SetValue(0)
