def build(panel):
    chooser = wx.CheckListBox(  # A11Y-SR-1-OK: state in label
        panel, choices=['a'])
