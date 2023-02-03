import gi
from Controllers.FixtureGridController import FixtureGridController
from Views.FixtureView import FixtureView

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class FixtureGridView(Gtk.HBox):
    BOX_SPACING = 30
    ROW_NUMBER = 3

    def __init__(self):
        super().__init__()

        self._fixtureViews = []
        self._fixtureController = FixtureGridController()

        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.START)
        self.set_spacing(FixtureGridView.BOX_SPACING)
        self.get_style_context().add_class("FixtureGridView")

        self.set_fixtures(self._fixtureController.get_fixtures())

    def set_fixtures(self, fixtures):
        self.create_fixture_views(fixtures)
        for fixtureView in self._fixtureViews:
            for fixture in fixtures:
                if fixtureView.equals(fixture):
                    fixtureView.set_fixture(fixture)

    def create_fixture_views(self, fixtures):
        if len(self._fixtureViews) > 0:
            return

        for fixture in fixtures:
            self._fixtureViews.append(FixtureView(fixture))

        vBox = Gtk.VBox()
        for i in range(len(self._fixtureViews)):
            if i % FixtureGridView.ROW_NUMBER == 0:
                vBox = Gtk.VBox(spacing=30)
                self.add(vBox)
            vBox.add(self._fixtureViews[i])

    def interact(self):
        self._fixtureController.start_watch_yield(self.set_fixtures)
