import gi
from Views.MainWindow import MainWindow

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


style_provider = Gtk.CssProvider()
style_provider.load_from_path("./styles.css")
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

mainWindow = MainWindow()
mainWindow.connect("destroy", Gtk.main_quit)
mainWindow.connect("delete-event", Gtk.main_quit)
mainWindow.show_all()

Gtk.main()
