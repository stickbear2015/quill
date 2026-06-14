def build(self):
    dialog = wx.Dialog(self)
    buttons.AddStretchSpacer(1)
    root.Add(buttons, 0, wx.ALL | wx.EXPAND, 8)
    dialog.Destroy()
