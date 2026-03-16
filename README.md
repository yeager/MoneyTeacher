# MoneyTeacher - Interaktiv kassaövning

Lär dig hantera svenska pengar! MoneyTeacher är en pedagogisk app som tränar betalning och växelberäkning med svenska mynt och sedlar.

## Funktioner

- **Betalövning** — Betala rätt belopp med mynt och sedlar
- **Växelövning** — Räkna ut rätt växel tillbaka
- **10 svårighetsnivåer** — Från enkla runda tal till svårare belopp
- **Handlingsguide** — Steg-för-steg-strategier för kassahantering
- **Statistik** — Spåra dina framsteg med träffsäkerhet och streak

## Svenska valörer

- **Mynt:** 1 kr, 2 kr, 5 kr, 10 kr
- **Sedlar:** 20 kr, 50 kr, 100 kr, 200 kr, 500 kr

## Installation

### Krav

- Python 3.8+
- GTK4
- libadwaita
- PyGObject

### Installera på Linux

```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1

# Fedora
sudo dnf install python3-gobject gtk4 libadwaita

# Arch
sudo pacman -S python-gobject gtk4 libadwaita
```

### Kör appen

```bash
python3 -m moneyteacher.main
```

### Installera som paket

```bash
pip install .
moneyteacher
```

## Användning

1. Välj övningsläge (Betalning eller Växel)
2. Tryck **Ny uppgift** för att få ett nytt belopp
3. Klicka på mynt/sedlar för att betala (betalläge)
4. Skriv in rätt växelbelopp (växelläge)
5. Tryck **Klar!** för att kontrollera ditt svar

## Licens

MIT
