#!/usr/bin/env python3
"""MoneyTeacher - Interaktiv kassaövning för svenska valörer."""

import gi
import json
import random
import os
from moneyteacher.i18n import _

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk, Pango

# Svenska valörer
MYNT = [1, 2, 5, 10]
SEDLAR = [20, 50, 100, 200, 500]
ALLA_VALOERER = MYNT + SEDLAR

# Färger för valörer
VALÖR_FÄRGER = {
    1: "#C0A060",
    2: "#C0A060",
    5: "#C0A060",
    10: "#C0A060",
    20: "#4A90D9",
    50: "#E8A838",
    100: "#6DBE6D",
    200: "#D4A844",
    500: "#D05050",
}

STATS_FILE = os.path.expanduser("~/.local/share/moneyteacher/stats.json")


def load_stats():
    try:
        with open(STATS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"rätt": 0, "fel": 0, "nivå": 1, "streak": 0}


def save_stats(stats):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def skapa_pris(nivå):
    """Generera ett slumpmässigt pris baserat på nivå."""
    if nivå <= 2:
        return random.choice([5, 10, 15, 20, 25, 30, 50])
    elif nivå <= 4:
        return random.randint(1, 10) * 5
    elif nivå <= 6:
        return random.randint(10, 99)
    else:
        return random.randint(20, 500)


class MoneyTeacherApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="se.moneyteacher.app")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.stats = load_stats()
        self.pris = 0
        self.betalt = 0
        self.läge = "betala"  # "betala" eller "växla"

        # Huvudfönster
        self.win = Adw.ApplicationWindow(application=app)
        self.win.set_title("MoneyTeacher - Kassaövning")
        self.win.set_default_size(700, 700)

        # Header bar
        header = Adw.HeaderBar()
        self.läge_knapp = Gtk.Button(label=_("Switch to: Switching exercise")
        self.läge_knapp.connect("clicked", self.byt_läge)
        header.pack_end(self.läge_knapp)

        self.guide_knapp = Gtk.Button(label=_("Guide")
        self.guide_knapp.connect("clicked", self.visa_guide)
        header.pack_end(self.guide_knapp)

        # Huvudlayout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.append(header)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(16)
        content.set_margin_bottom(16)
        content.set_margin_start(16)
        content.set_margin_end(16)

        # Statistik-rad
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        stats_box.set_halign(Gtk.Align.CENTER)
        self.stats_label = Gtk.Label()
        self.stats_label.add_css_class("caption")
        stats_box.append(self.stats_label)
        content.append(stats_box)

        # Nivå-rad
        nivå_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        nivå_box.set_halign(Gtk.Align.CENTER)
        nivå_label = Gtk.Label(label=_("Level:")
        nivå_box.append(nivå_label)
        self.nivå_spin = Gtk.SpinButton.new_with_range(1, 10, 1)
        self.nivå_spin.set_value(self.stats["nivå"])
        self.nivå_spin.connect("value-changed", self.nivå_ändrad)
        nivå_box.append(self.nivå_spin)
        content.append(nivå_box)

        # Prisvisning
        self.pris_frame = Gtk.Frame()
        pris_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        pris_box.set_margin_top(16)
        pris_box.set_margin_bottom(16)
        pris_box.set_margin_start(16)
        pris_box.set_margin_end(16)

        self.uppgift_label = Gtk.Label(label=_("Press \'New task\' to start!")
        self.uppgift_label.add_css_class("title-3")
        pris_box.append(self.uppgift_label)

        self.pris_label = Gtk.Label(label=_("")
        self.pris_label.add_css_class("title-1")
        pris_box.append(self.pris_label)

        self.betalt_label = Gtk.Label(label=_("")
        self.betalt_label.add_css_class("title-4")
        pris_box.append(self.betalt_label)

        self.feedback_label = Gtk.Label(label=_("")
        pris_box.append(self.feedback_label)

        self.pris_frame.set_child(pris_box)
        content.append(self.pris_frame)

        # Valör-knappar: Mynt
        mynt_label = Gtk.Label(label=_("Mynt")
        mynt_label.add_css_class("heading")
        mynt_label.set_halign(Gtk.Align.START)
        content.append(mynt_label)

        mynt_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mynt_box.set_halign(Gtk.Align.CENTER)
        self.valör_knappar = []
        for v in MYNT:
            btn = self._skapa_valör_knapp(v, är_mynt=True)
            mynt_box.append(btn)
        content.append(mynt_box)

        # Valör-knappar: Sedlar
        sedel_label = Gtk.Label(label=_("Sedlar")
        sedel_label.add_css_class("heading")
        sedel_label.set_halign(Gtk.Align.START)
        content.append(sedel_label)

        sedel_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        sedel_box.set_halign(Gtk.Align.CENTER)
        for v in SEDLAR:
            btn = self._skapa_valör_knapp(v, är_mynt=False)
            sedel_box.append(btn)
        content.append(sedel_box)

        # Knappar
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        action_box.set_halign(Gtk.Align.CENTER)
        action_box.set_margin_top(8)

        self.ny_knapp = Gtk.Button(label=_("New uppgift")
        self.ny_knapp.add_css_class("suggested-action")
        self.ny_knapp.add_css_class("pill")
        self.ny_knapp.connect("clicked", self.ny_uppgift)
        action_box.append(self.ny_knapp)

        self.nollställ_knapp = Gtk.Button(label=_("Reset to zero")
        self.nollställ_knapp.add_css_class("pill")
        self.nollställ_knapp.connect("clicked", self.nollställ)
        action_box.append(self.nollställ_knapp)

        self.klar_knapp = Gtk.Button(label=_("Complete!")
        self.klar_knapp.add_css_class("pill")
        self.klar_knapp.connect("clicked", self.kontrollera)
        action_box.append(self.klar_knapp)

        content.append(action_box)

        # Växel-svar (för växelläge)
        self.växel_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.växel_box.set_halign(Gtk.Align.CENTER)
        self.växel_box.set_margin_top(8)
        växel_label2 = Gtk.Label(label=_("Switch back:")
        self.växel_box.append(växel_label2)
        self.växel_entry = Gtk.Entry()
        self.växel_entry.set_input_purpose(Gtk.InputPurpose.NUMBER)
        self.växel_entry.set_width_chars(8)
        self.växel_entry.connect("activate", lambda e: self.kontrollera(None))
        self.växel_box.append(self.växel_entry)
        self.växel_box.append(Gtk.Label(label=_("kr"))
        self.växel_box.set_visible(False)
        content.append(self.växel_box)

        # Tips-sektion
        self.tips_label = Gtk.Label(label=_("")
        self.tips_label.set_wrap(True)
        self.tips_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.tips_label.set_margin_top(8)
        self.tips_label.add_css_class("dim-label")
        content.append(self.tips_label)

        # Scrollbar för innehåll
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_child(content)

        main_box.append(scroll)
        self.win.set_content(main_box)

        # CSS
        css = Gtk.CssProvider()
        css.load_from_string("""
            .mynt-knapp {
                min-width: 70px;
                min-height: 70px;
                border-radius: 50%;
                font-weight: bold;
                font-size: 16px;
            }
            .sedel-knapp {
                min-width: 100px;
                min-height: 55px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }
            .rätt { color: #2ECC71; font-weight: bold; font-size: 18px; }
            .fel { color: #E74C3C; font-weight: bold; font-size: 18px; }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.uppdatera_stats_label()
        self.win.present()

    def _skapa_valör_knapp(self, valör, är_mynt):
        label = f"{valör} kr"
        btn = Gtk.Button(label=label)
        btn.add_css_class("mynt-knapp" if är_mynt else "sedel-knapp")
        btn.connect("clicked", self.valör_klickad, valör)
        btn.set_tooltip_text(f"Lägg till {valör} kr")
        self.valör_knappar.append(btn)
        return btn

    def valör_klickad(self, button, valör):
        if self.pris == 0:
            return
        self.betalt += valör
        self.uppdatera_betalt()

    def uppdatera_betalt(self):
        if self.läge == "betala":
            kvar = max(0, self.pris - self.betalt)
            self.betalt_label.set_text(f"Betalt: {self.betalt} kr  |  Kvar: {kvar} kr")
            if self.betalt >= self.pris:
                self.betalt_label.set_text(
                    f"Betalt: {self.betalt} kr  ✓"
                )
        else:
            self.betalt_label.set_text(f"Kunden betalar: {self.betalt} kr")

    def ny_uppgift(self, button):
        nivå = int(self.nivå_spin.get_value())
        self.pris = skapa_pris(nivå)
        self.betalt = 0
        self.feedback_label.set_text("")
        self.feedback_label.remove_css_class("rätt")
        self.feedback_label.remove_css_class("fel")
        self.tips_label.set_text("")

        if self.läge == "betala":
            self.uppgift_label.set_text("Betala exakt rätt belopp:")
            self.pris_label.set_text(f"{self.pris} kr")
            self.betalt_label.set_text("Betalt: 0 kr  |  Kvar: {0} kr".format(self.pris))
            self.växel_box.set_visible(False)
            self._visa_tips_betala()
        else:
            # Växelövning: kunden ger en sedel/mynt som är mer än priset
            möjliga = [v for v in ALLA_VALOERER if v > self.pris]
            if not möjliga:
                möjliga = [500, 1000]
            kund_betalar = random.choice(möjliga)
            self.betalt = kund_betalar
            self.uppgift_label.set_text(f"Priset är {self.pris} kr. Kunden betalar:")
            self.pris_label.set_text(f"{kund_betalar} kr")
            self.betalt_label.set_text(f"Hur mycket växel tillbaka?")
            self.växel_box.set_visible(True)
            self.växel_entry.set_text("")
            self.växel_entry.grab_focus()
            self._visa_tips_växel()

    def nollställ(self, button):
        if self.läge == "betala":
            self.betalt = 0
            if self.pris > 0:
                self.betalt_label.set_text(f"Betalt: 0 kr  |  Kvar: {self.pris} kr")
            self.feedback_label.set_text("")
            self.feedback_label.remove_css_class("rätt")
            self.feedback_label.remove_css_class("fel")

    def kontrollera(self, button):
        if self.pris == 0:
            return

        if self.läge == "betala":
            self._kontrollera_betalning()
        else:
            self._kontrollera_växel()

    def _kontrollera_betalning(self):
        self.feedback_label.remove_css_class("rätt")
        self.feedback_label.remove_css_class("fel")

        if self.betalt == self.pris:
            self.feedback_label.set_text("Helt rätt! Bra jobbat! 🎉")
            self.feedback_label.add_css_class("rätt")
            self.stats["rätt"] += 1
            self.stats["streak"] += 1
            if self.stats["streak"] >= 5 and self.stats["nivå"] < 10:
                self.stats["nivå"] += 1
                self.nivå_spin.set_value(self.stats["nivå"])
                self.tips_label.set_text("🎯 Nivå upp! Du är duktig!")
        elif self.betalt > self.pris:
            över = self.betalt - self.pris
            self.feedback_label.set_text(f"För mycket! {över} kr för mycket.")
            self.feedback_label.add_css_class("fel")
            self.stats["fel"] += 1
            self.stats["streak"] = 0
        else:
            kvar = self.pris - self.betalt
            self.feedback_label.set_text(f"För lite! Det saknas {kvar} kr.")
            self.feedback_label.add_css_class("fel")
            self.stats["fel"] += 1
            self.stats["streak"] = 0

        self.uppdatera_stats_label()
        save_stats(self.stats)

    def _kontrollera_växel(self):
        self.feedback_label.remove_css_class("rätt")
        self.feedback_label.remove_css_class("fel")

        try:
            svar = int(self.växel_entry.get_text().strip())
        except ValueError:
            self.feedback_label.set_text("Skriv ett tal!")
            self.feedback_label.add_css_class("fel")
            return

        rätt_växel = self.betalt - self.pris
        if svar == rätt_växel:
            self.feedback_label.set_text(f"Rätt! {self.betalt} - {self.pris} = {rätt_växel} kr 🎉")
            self.feedback_label.add_css_class("rätt")
            self.stats["rätt"] += 1
            self.stats["streak"] += 1
            if self.stats["streak"] >= 5 and self.stats["nivå"] < 10:
                self.stats["nivå"] += 1
                self.nivå_spin.set_value(self.stats["nivå"])
        else:
            self.feedback_label.set_text(
                f"Fel! Rätt svar: {self.betalt} - {self.pris} = {rätt_växel} kr"
            )
            self.feedback_label.add_css_class("fel")
            self.stats["fel"] += 1
            self.stats["streak"] = 0

        self.uppdatera_stats_label()
        save_stats(self.stats)

    def uppdatera_stats_label(self):
        totalt = self.stats["rätt"] + self.stats["fel"]
        procent = (
            round(self.stats["rätt"] / totalt * 100) if totalt > 0 else 0
        )
        self.stats_label.set_text(
            f"Rätt: {self.stats['rätt']}  |  Fel: {self.stats['fel']}  |  "
            f"Träffsäkerhet: {procent}%  |  Streak: {self.stats['streak']}"
        )

    def nivå_ändrad(self, spin):
        self.stats["nivå"] = int(spin.get_value())
        save_stats(self.stats)

    def byt_läge(self, button):
        if self.läge == "betala":
            self.läge = "växla"
            self.läge_knapp.set_label("Byt till: Betalövning")
        else:
            self.läge = "betala"
            self.läge_knapp.set_label("Byt till: Växelövning")
        self.pris = 0
        self.betalt = 0
        self.pris_label.set_text("")
        self.betalt_label.set_text("")
        self.feedback_label.set_text("")
        self.feedback_label.remove_css_class("rätt")
        self.feedback_label.remove_css_class("fel")
        self.uppgift_label.set_text("Tryck 'Ny uppgift' för att börja!")
        self.växel_box.set_visible(False)
        self.tips_label.set_text("")

    def _visa_tips_betala(self):
        nivå = int(self.nivå_spin.get_value())
        if nivå <= 2:
            tips = [
                f"Tips: Börja med de största valörerna!",
                f"Tips: {self.pris} kr = ? × 10 kr + ? × 5 kr + ? × 1 kr",
            ]
        elif nivå <= 4:
            tips = [
                "Tips: Tänk i tior och femmor först.",
                "Tips: Dela upp beloppet i delar du kan.",
            ]
        else:
            tips = [
                "Tips: Vilken sedel kommer närmast utan att gå över?",
                "Tips: Börja stort, fyll i med småmynt.",
            ]
        self.tips_label.set_text(random.choice(tips))

    def _visa_tips_växel(self):
        rätt = self.betalt - self.pris
        nivå = int(self.nivå_spin.get_value())
        if nivå <= 3:
            self.tips_label.set_text(
                f"Tips: Räkna upp från priset till det kunden betalade.\n"
                f"{self.pris} + ? = {self.betalt}"
            )
        else:
            self.tips_label.set_text(
                f"Tips: {self.betalt} − {self.pris} = ?"
            )

    def visa_guide(self, button):
        dialog = Adw.Dialog()
        dialog.set_title("Handlingsguide")
        dialog.set_content_width(450)
        dialog.set_content_height(500)

        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        guide_text = [
            ("Steg 1: Betalning", [
                "1. Läs priset noggrant",
                "2. Börja med den största valören som inte överstiger priset",
                "3. Fyll på med mindre valörer tills du når rätt summa",
                "4. Dubbelkolla att totalen stämmer",
            ]),
            ("Steg 2: Växelberäkning", [
                "1. Kunden ger dig pengar — notera beloppet",
                "2. Räkna: Betalt − Pris = Växel",
                "3. Eller räkna upp: Pris + ? = Betalt",
                "4. Ge tillbaka med så få mynt/sedlar som möjligt",
            ]),
            ("Steg 3: Strategier", [
                "• 'Räkna-upp-metoden': Börja vid priset, räkna uppåt",
                "  Ex: Pris 37 kr, betalt 50 kr → 37+3=40, 40+10=50 → 13 kr",
                "• 'Subtraktionsmetoden': Dra av direkt",
                "  Ex: 50 − 37 = 13 kr",
                "• Öva båda metoderna och använd den du gillar bäst!",
            ]),
            ("Svenska valörer", [
                "Mynt: 1 kr, 2 kr, 5 kr, 10 kr",
                "Sedlar: 20 kr, 50 kr, 100 kr, 200 kr, 500 kr, 1000 kr",
            ]),
        ]

        for rubrik, punkter in guide_text:
            lbl = Gtk.Label(label=rubrik)
            lbl.add_css_class("title-4")
            lbl.set_halign(Gtk.Align.START)
            box.append(lbl)
            for p in punkter:
                pl = Gtk.Label(label=p)
                pl.set_halign(Gtk.Align.START)
                pl.set_wrap(True)
                pl.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
                box.append(pl)
            box.append(Gtk.Separator())

        scroll.set_child(box)
        toolbar_view.set_content(scroll)
        dialog.set_child(toolbar_view)
        dialog.present(self.win)


def main():
    app = MoneyTeacherApp()
    app.run(None)


if __name__ == "__main__":
    main()
