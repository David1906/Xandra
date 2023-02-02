import gi
from Views.FixtureGridView import FixtureGridView

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    ICON_FULLPATH = "./Resources/icon.png"
    BOX_SPACING = 30

    def __init__(self):
        super().__init__(title="Xandra - FBT")

        self.set_default_size(400, 600)

        self.box = Gtk.HBox()
        self.box.set_halign(Gtk.Align.CENTER)
        self.box.set_valign(Gtk.Align.START)
        self.add(self.box)

        fixtureGridView = FixtureGridView()
        self.box.add(fixtureGridView)
        fixtureGridView.interact()
        self.set_icon_from_file(MainWindow.ICON_FULLPATH)
