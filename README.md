<div align="center">

# Hospicjum Domowe JANMED

**Bezpłatna opieka paliatywna i hospicyjna w domu pacjenta.**

Lekarz, pielęgniarka, rehabilitant i psycholog przyjeżdżają tam,
gdzie człowiek czuje się bezpiecznie: wśród swoich rzeczy i swoich ludzi.

[**janmed.pl**](https://janmed.pl) · [Zgłoś pacjenta](https://janmed.pl/formularz-zgloszeniowy-do-hospicjum-domowego/) · [Baza wiedzy](https://janmed.pl/baza-wiedzy/) · [Praca](https://janmed.pl/praca/) · [Wesprzyj hospicjum](https://zrzutka.pl/74px3w/pay)

</div>

---

## Dla kogo jesteśmy

Dla osób nieuleczalnie chorych, u których zakończono leczenie przyczynowe,
i dla ich rodzin. Opieka jest finansowana przez Narodowy Fundusz Zdrowia,
więc dla pacjenta i bliskich jest **bezpłatna**. Potrzebne jest skierowanie
od lekarza prowadzącego.

Dojeżdżamy do domów chorych w Olkuszu, Pińczowie i Kazimierzy Wielkiej
oraz w okolicach. Działamy od 2010 roku.

| Placówka | Adres | Telefon |
| --- | --- | --- |
| Hospicjum Olkusz | Króla Kazimierza Wielkiego 64, 32-300 Olkusz | [698 887 816](tel:+48698887816) |
| Hospicjum Pińczów | ul. Batalionów Chłopskich 33, 28-400 Pińczów | [535 043 985](tel:+48535043985) |
| Hospicjum Kazimierza Wielka | ul. Partyzantów 12, 28-500 Kazimierza Wielka | [535 043 985](tel:+48535043985) |

Informacja i rejestracja 8:00-15:00 · [biuro@janmed.pl](mailto:biuro@janmed.pl)

---

## O tym repozytorium

Tu mieszka kod strony [janmed.pl](https://janmed.pl). Strona jest statyczna
i napisana ręcznie: treść w markdownie, generator w czystym Pythonie,
wynik na GitHub Pages. Bez frameworka, bez `node_modules`, bez systemu
zarządzania treścią.

Nie jest to wybór ideologiczny. Strona hospicjum ma się otwierać u kogoś,
kto właśnie wyszedł ze szpitala i szuka pomocy z telefonu, w gorszym zasięgu.

| | |
| --- | --- |
| Strona główna, pierwsze wczytanie | **436 KB** |
| Cały serwis | **2,3 MB** |
| Pliki JavaScript | **2** |
| Zależności zewnętrzne w buildzie | **0** |

Poza wagą pilnujemy kilku rzeczy, które przy tej grupie odbiorców nie są
kosmetyką:

* **Kontrast.** Znaczna część odwiedzających to osoby starsze, więc kolory
  tekstu i linków są dobrane pod WCAG, a nie pod paletę marki.
* **Ruch.** Animacje wyłączają się przy `prefers-reduced-motion`, a bezpiecznik
  pokazuje całą treść po 3 sekundach niezależnie od tego, czy skrypt zadziałał.
  Treść na stronie hospicjum nie ma prawa zostać niewidoczna.
* **Prywatność.** Kroje pisma hostujemy u siebie, odtwarzacz wideo leci
  z `dnt=1` i powstaje dopiero po pierwszym malowaniu strony.
* **Czytelność dla asystentów AI.** Serwis wystawia `llms.txt`, `llms-full.txt`
  i bliźniaczą wersję każdej podstrony w markdownie. Rodzina szukająca
  hospicjum coraz częściej pyta czat, nie wyszukiwarkę.

Dokumentacja techniczna: [`docs/TECHNICZNE.md`](docs/TECHNICZNE.md).
System wizualny: [`docs/design.md`](docs/design.md) plus storybook
[`docs/design.html`](docs/design.html), który czyta produkcyjny arkusz stylów,
więc nie może się z nim rozjechać.

---

<div align="center">

JANMED Sp. z o. o. 2010-2026

</div>
