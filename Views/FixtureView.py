import gi
import subprocess

from Controllers.FixtureController import FixtureController

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class FixtureView(Gtk.Box):
    def __init__(self, fixture):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.fixture = fixture
        self._fixtureController = FixtureController()

        self.get_style_context().add_class("FixtureView")

        vBox = Gtk.VBox(spacing=10)
        vBox.set_halign(Gtk.Align.CENTER)
        self.add(vBox)

        self.lblId = Gtk.Label()
        self.lblId.get_style_context().add_class("h1")
        vBox.add(self.lblId)

        self.btnStart = Gtk.Button(label="Start")
        self.btnStart.connect("clicked", self.on_btnStart_clicked)
        vBox.add(self.btnStart)

        boxTraceability = Gtk.Box(spacing=10)
        lblTraceability = Gtk.Label(label="Traceability")
        boxTraceability.pack_start(lblTraceability, True, True, 0)
        self.switch = Gtk.Switch(state=True)
        boxTraceability.pack_start(self.switch, True, True, 0)
        vBox.add(boxTraceability)

        self.lblIp = Gtk.Label()
        self.lblIp.get_style_context().add_class("h4")
        vBox.add(self.lblIp)

        self.lblYield = Gtk.Label()
        self.lblYield.get_style_context().add_class("h4")
        vBox.add(self.lblYield)

        self.set_fixture(fixture)

    def set_fixture(self, fixture):
        self.fixture = fixture
        self.lblId.set_label(f"Fixture {fixture.id}")
        self.lblYield.set_label(f"Yield: {fixture.yieldRate}%")
        self.lblIp.set_label(f"Ip: {fixture.ip}")
        self.btnStart.set_sensitive(fixture.isDisabled() == False)

        if fixture.isDisabled():
            self.get_style_context().add_class("error")
            self.get_style_context().remove_class("warning")
        elif fixture.isWarning():
            self.get_style_context().add_class("warning")
            self.get_style_context().remove_class("error")
        else:
            self.get_style_context().remove_class("warning")
            self.get_style_context().remove_class("error")

    def on_btnStart_clicked(self, widget):
        self._fixtureController.launch_fct_host_control(self.fixture, self.switch.get_state())

    def equals(self, fixture):
        return fixture.id == self.fixture.id
