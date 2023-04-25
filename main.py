import wx
import pygame
import json
import win32api
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, config, setting_type):
        self.setting_type = setting_type.lower()
        title = f"{setting_type} Settings"
        super().__init__(parent, title=title, size=(300, 200))
        self.config = config

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # 入力欄の作成
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        value = self.config[self.setting_type]
        self.input = wx.TextCtrl(panel, value=str(value))
        hbox1.Add(wx.StaticText(panel, label=f"{self.setting_type}:"), flag=wx.RIGHT, border=8)
        hbox1.Add(self.input)

        # 保存ボタンの作成
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(panel, label="Save")
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        hbox2.Add(save_button)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

    # 保存ボタンが押されたときの処理
    def OnSave(self, event):
        value = float(self.input.GetValue()) if self.setting_type != "key" else self.input.GetValue()
        self.config[self.setting_type] = value
        self.EndModal(wx.ID_OK)


class GraphFrame(wx.Frame):
    def __init__(self, parent, config):
        title = "Sensivity Settings"
        super(GraphFrame, self).__init__(parent, title=title, size=(600, 500))

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.config = config
        self.points = [(0, 0), (1, 1)]
        self.load_graph_points()
        self.line, = self.axes.plot(*zip(*self.points), marker='o', linestyle='-', color='b')

        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_move)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.selected_point = None
        self.dragging = False

        self.Show()

    def on_click(self, event):
        # 右クリックで点を追加
        if event.button == 3 and event.xdata and event.ydata:
            self.points.append((event.xdata, event.ydata))
            self.points.sort()
            self.redraw()
        
        # 中クリックで点を削除
        elif event.button == 2:
            if len(self.points) > 2:
                point_to_remove = None
                for point in self.points:
                    if abs(point[0] - event.xdata) < 0.05 and abs(point[1] - event.ydata) < 0.05:
                        point_to_remove = point
                        break
                if point_to_remove:
                    self.points.remove(point_to_remove)
                    self.redraw()

        # 左クリックで点を移動
        elif event.button == 1:
            for point in self.points:
                if abs(point[0] - event.xdata) < 0.05 and abs(point[1] - event.ydata) < 0.05:
                    self.selected_point = point
                    self.dragging = True
                    break

        self.save_graph_points()

    def on_move(self, event):
        # first point and end point can't be moved
        print(self.selected_point)
        if self.selected_point == (0, 0) or self.selected_point == (1, 1):
            return
        if self.dragging and self.selected_point:
            if self.selected_point in self.points:
                self.points.remove(self.selected_point)

            # キャンバス範囲外での値を制限する
            x = min(max(event.xdata if event.xdata is not None else 0, 0), 1)
            y = min(max(event.ydata if event.ydata is not None else 0, self.config["deadzone"]), 1)

            if self.selected_point == self.points[0] or self.selected_point == self.points[-1]:
                self.selected_point = (x, y)
            else:
                self.selected_point = (x, y)
                
            self.points.append(self.selected_point)
            self.points.sort()
            self.redraw()

            self.save_graph_points()

    def on_release(self, event):
        if event.button == 1 and self.dragging:
            self.dragging = False
            self.selected_point = None

        self.save_graph_points()

    def redraw(self):
        self.line.set_data(*zip(*self.points))
        self.canvas.draw()

    def load_graph_points(self):
        try:
            with open("config.json", "r") as f:
                self.points = [tuple(point) for point in json.load(f)["graph"]]
        except:
            pass

    def save_graph_points(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
        except:
            data = {}
        with open("config.json", "w") as f:
            data["graph"] = self.points
            json.dump(data, f, indent=4)



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
        sensitivity_plot_button = wx.Button(panel, label="Sensitivity Plot")
        sensitivity_plot_button.Bind(wx.EVT_BUTTON, self.OnSensitivityPlot)
        hbox4.Add(sensitivity_plot_button)

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        start_button = wx.Button(panel, label="Start")
        start_button.Bind(wx.EVT_BUTTON, self.OnStart)
        hbox5.Add(start_button)

        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox4, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add(hbox5, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        panel.SetSizer(vbox)

    def InitConfig(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                del data["graph"]
                self.config = data
        except:
            self.config = {
                "key": "C",
                "multiplier": 0.7,
                "deadzone": 0.1
            }

    def OnSensitivityPlot(self, event):
        GraphFrame(self, self.config)

    def OnKeySettings(self, event):
        with SettingsDialog(self, self.config, "Key") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config.update(dlg.config)
                self.OnSave()

    def OnMultiplierSettings(self, event):
        with SettingsDialog(self, self.config, "Multiplier") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config.update(dlg.config)
                self.OnSave()

    def OnDeadzoneSettings(self, event):
        with SettingsDialog(self, self.config, "Deadzone") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.config.update(dlg.config)
                self.OnSave()

    def OnSave(self):
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
        except:
            data = {}
        with open("config.json", "w") as f:
            data["key"] = self.config["key"]
            data["multiplier"] = self.config["multiplier"]
            data["deadzone"] = self.config["deadzone"]
            json.dump(data, f, indent=4)
        

    def OnStart(self, event):
            self.Hide()
            pygame.init()

            import time
            time.sleep(5)

            key_code = ord(self.config["key"])
            
            with open("config.json", "r") as f:
                points = [tuple(point) for point in json.load(f)["graph"]]

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

                    # deadzoneに基づいて補間値を計算
                    if abs(x_axis) < self.config["deadzone"]:
                        x_axis = 0
                    if abs(y_axis) < self.config["deadzone"]:
                        y_axis = 0


                    # グラフの座標に基づいて補間値を計算
                    for i in range(len(points) - 1):
                        if points[i][0] <= abs(x_axis) < points[i + 1][0]:
                            x_ratio = (abs(x_axis) - points[i][0]) / (points[i + 1][0] - points[i][0])
                            x_axis_sign = np.sign(x_axis)
                            x_axis = x_axis_sign * (points[i][1] + x_ratio * (points[i + 1][1] - points[i][1]))
                        if points[i][0] <= abs(y_axis) < points[i + 1][0]:
                            y_ratio = (abs(y_axis) - points[i][0]) / (points[i + 1][0] - points[i][0])
                            y_axis_sign = np.sign(y_axis)
                            y_axis = y_axis_sign * (points[i][1] + y_ratio * (points[i + 1][1] - points[i][1]))

                    # multiplierに基づいて補間値を計算
                    x_axis *= self.config["multiplier"]
                    y_axis *= self.config["multiplier"]

                    x_pos = int(screen_width // 2 + x_axis * (screen_height // 2))
                    y_pos = int(screen_height // 2 + y_axis * (screen_height // 2))

                    win32api.SetCursorPos((x_pos, y_pos))

                clock.tick(60)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()

