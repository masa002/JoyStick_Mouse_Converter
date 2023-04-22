import wx
import pygame
import json
import win32api

class KeySettingsDialog(wx.Dialog):
    def __init__(self, parent, config):
        super().__init__(parent, title="Key Settings", size=(300, 200))
        self.config = config

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.key_input = wx.TextCtrl(panel, value=self.config["key"])
        hbox1.Add(wx.StaticText(panel, label="Activation Key:"), flag=wx.RIGHT, border=8)
        hbox1.Add(self.key_input)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(panel, label="Save")
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        hbox2.Add(save_button)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

    def OnSave(self, event):
        self.config["key"] = self.key_input.GetValue()
        self.EndModal(wx.ID_OK)


class MultiplierSettingsDialog(wx.Dialog):
    def __init__(self, parent, config):
        super().__init__(parent, title="Multiplier Settings", size=(300, 200))
        self.config = config

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.multiplier_input = wx.TextCtrl(panel, value=str(self.config["multiplier"]))
        hbox1.Add(wx.StaticText(panel, label="Multiplier:"), flag=wx.RIGHT, border=8)
        hbox1.Add(self.multiplier_input)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(panel, label="Save")
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        hbox2.Add(save_button)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

    def OnSave(self, event):
        self.config["multiplier"] = float(self.multiplier_input.GetValue())
        self.EndModal(wx.ID_OK)

class DeadzoneSettingsDialog(wx.Dialog):
    def __init__(self, parent, config):
        super().__init__(parent, title="Deadzone Settings", size=(300, 200))
        self.config = config

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.deadzone_input = wx.TextCtrl(panel, value=str(self.config["deadzone"]))
        hbox1.Add(wx.StaticText(panel, label="Deadzone:"), flag=wx.RIGHT, border=8)
        hbox1.Add(self.deadzone_input)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(panel, label="Save")
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        hbox2.Add(save_button)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

    def OnSave(self, event):
        self.config["deadzone"] = float(self.deadzone_input.GetValue())
        self.EndModal(wx.ID_OK)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Joystick Mouse Control", size=(400, 300))

        
        self.InitUI()
        self.InitConfig()
        self.Centre()

    def InitUI(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        key_settings_button = wx.Button(panel, label="Stop Key Settings")
        key_settings_button.Bind(wx.EVT_BUTTON, self.OnKeySettings)
        hbox1.Add(key_settings_button)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        multiplier_settings_button = wx.Button(panel, label="Multiplier Settings")
        multiplier_settings_button.Bind(wx.EVT_BUTTON, self.OnMultiplierSettings)
        hbox2.Add(multiplier_settings_button)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        deadzone_settings_button = wx.Button(panel, label="Deadzone Settings")
        deadzone_settings_button.Bind(wx.EVT_BUTTON, self.OnDeadzoneSettings)
        hbox3.Add(deadzone_settings_button)

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        start_button = wx.Button(panel, label="Start")
        start_button.Bind(wx.EVT_BUTTON, self.OnStart)
        hbox4.Add(start_button)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

    def InitConfig(self):
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except:
            self.config = {
                "key": "C",
                "multiplier": 0.7,
                "deadzone": 0.1
            }

    def OnKeySettings(self, event):
        with KeySettingsDialog(self, self.config) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config.update(dlg.config)
                self.OnSave()

    def OnMultiplierSettings(self, event):
        with MultiplierSettingsDialog(self, self.config) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config.update(dlg.config)
                self.OnSave()

    def OnDeadzoneSettings(self, event):
        with DeadzoneSettingsDialog(self, self.config) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config.update(dlg.config)
                self.OnSave()

    def OnSave(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)
        

    def OnStart(self, event):
        self.Hide()
        pygame.init()

        import time
        time.sleep(5)

        # 16進数のキーコードを取得
        key_code = ord(self.config["key"])
        multiplier = self.config["multiplier"]
        deadzone = self.config["deadzone"]

        screen_width, screen_height = pygame.display.list_modes()[0]
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                pass

            if win32api.GetAsyncKeyState(key_code) and 0x8000:
                self.Show()
                pygame.quit()
                return

            joystick_count = pygame.joystick.get_count()
            if joystick_count > 0:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()

                x_axis = joystick.get_axis(0)
                y_axis = joystick.get_axis(1)

                if abs(x_axis) < deadzone:
                    x_axis = 0
                if abs(y_axis) < deadzone:
                    y_axis = 0

                x_axis *= multiplier
                y_axis *= multiplier

                x_pos = int(screen_width // 2 + x_axis * (screen_height // 2))
                y_pos = int(screen_height // 2 + y_axis * (screen_height // 2))
                print(x_pos, y_pos)

                win32api.SetCursorPos((x_pos, y_pos))

            clock.tick(60)

        

if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()

