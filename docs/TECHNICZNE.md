# Dokumentacja techniczna janmed.pl

Rzeczy, które interesują osobę pracującą z kodem, a nie odwiedzającego stronę.
Krótkie „jak zacząć" jest w [README](../README.md).
Dziennik przepisania strony leży poza repozytorium, w `prywatne/DECYZJE.md`.

---

## Deploy

GitHub Actions (`.github/workflows/deploy.yml`) na każdy push do `main`:
buduje, uruchamia `check.py`, publikuje `dist/` na Pages.

W ustawieniach repo: **Settings → Pages → Source: GitHub Actions**
(nie „Deploy from a branch" - tamten wariant odpala Jekylla).

`CNAME` i `.nojekyll` są generowane do `dist/` przez `build.py`, więc lecą
w artefakcie - bez tego kolejny deploy skasowałby ustawienie własnej domeny.

### Przełączenie domeny z WordPressa

1. Wypchnij repo, sprawdź podgląd pod `*.github.io`.
2. DNS dla `janmed.pl` → rekordy A na `185.199.108-111.153`,
   `www` → CNAME na `<użytkownik>.github.io`.
3. Settings → Pages → Custom domain: `janmed.pl`, zaznacz *Enforce HTTPS*.
4. Dopiero po przepięciu wyłącz stary hosting.

---

## Google Analytics

Ten sam strumień co wcześniej: **G-S24XS3Q9DD** (`ga_id` w `content/site.json`).

Odsłony liczy gtag automatycznie. Każda strona wysyła `content_group`, więc
w GA4 da się filtrować ruch bez żadnej konfiguracji:
`strona-glowna`, `baza-wiedzy`, `artykul`, `praca`, `kontakt`, `formularz`,
`prawne`, `404`.

`js/analytics.js` dokłada zdarzenia, których GA4 samo nie zobaczy:

| Zdarzenie | Kiedy | Parametry |
| --- | --- | --- |
| `donate_click` | klik w link do zrzutki | `miejsce`, `link_url` |
| `form_cta_click` | klik w „Zgłoś pacjenta" | `miejsce` |
| `form_open` | otwarcie formularza | `rodzaj`, `oferta` |
| `form_start` | przejście z 1. kroku dalej | `rodzaj`, `oferta` |
| `form_step` | każdy krok formularza | `krok`, `rodzaj`, `oferta` |
| `form_submit` | formularz wysłany | `rodzaj`, `oferta` |
| `phone_click` | klik w numer telefonu | `miejsce`, `numer`, `placowka` |
| `email_click` | klik w adres e-mail | `miejsce` |
| `article_read` | przewinięcie artykułu do ~75% | `artykul` |
| `job_filter` | filtr ofert po miejscowości | `miejsce` |

`form_step` i `form_submit` przychodzą z Tally przez `postMessage`.

**Do zrobienia raz w panelu GA4**, żeby te dane były widoczne w raportach:

1. *Administracja → Zdarzenia* - po kilku dniach zdarzenia pojawią się na liście;
   oznacz `form_submit`, `donate_click` i `phone_click` jako **kluczowe zdarzenia**.
2. *Administracja → Definicje niestandardowe → Wymiary niestandardowe* -
   dodaj `miejsce`, `krok`, `placowka`, `artykul`, `rodzaj`, `oferta`
   (zakres: zdarzenie).
   Bez tego parametry lecą, ale nie da się po nich filtrować.
3. *Administracja → Grupy treści* nie wymaga konfiguracji - `content_group`
   jest wymiarem wbudowanym.

Podgląd na żywo: *Administracja → DebugView* albo raport *Czas rzeczywisty*.

---

## Formularz zgłoszeniowy

Zostaje na **Tally** (`tally.so/embed/5B4vYb`), osadzony na
`/formularz-zgloszeniowy-do-hospicjum-domowego/`. Zbiera dane szczególnej
kategorii (PESEL, skierowanie, karta informacyjna ze szpitala), więc
przeniesienie go „na nasze" to decyzja o procesorze danych, umowie powierzenia
i retencji - nie o kodzie. Inwentarz pól i szkic migracji:
[`content/formularz-pola.md`](content/formularz-pola.md).

---

## Formularz aplikacyjny (rekrutacja)

Oferty pracy mieszkają w `content/jobs/*.md`, lista pod `/praca/`, każda oferta
pod `/praca/<slug>/`. Formularz aplikacyjny jest **na stronie oferty** - nikogo
nie odsyłamy dalej.

### Dlaczego znowu Tally

Aplikacja niesie CV (plik), dane kontaktowe i zgodę - czyli dokładnie to,
czego statyczna strona na GitHub Pages sama nie przyjmie, bo nie ma backendu.
Tally już tu jest, już jest procesorem naszych danych i umie trzy rzeczy,
których potrzebujemy naraz: **upload pliku, powiadomienie mailem i pola ukryte**.
Dokładanie drugiego dostawcy (Formspree, Getform, własny endpoint) oznaczałoby
drugą umowę powierzenia i drugie miejsce, w którym leżą czyjeś CV - za dużo jak
na jeden formularz.

### Stan na dziś

Formularz **istnieje i jest podpięty**: `tally.so/embed/WOWOpk`, wpisany
w `content/site.json` → `recruitment.tally_embed`. Pola: imię i nazwisko,
telefon, e-mail, CV jako plik (limit 10 MB).

Strona ofert dokleja do adresu osadzenia dwa pola ukryte:

| Parametr | Skąd | Przykład |
| --- | --- | --- |
| `stanowisko` | `position` z front matter oferty (domyślnie tytuł) | `Lekarz` |
| `lokalizacja` | pierwsza pozycja z `places` | `Pińczów` |

Nazwy parametrów siedzą w `recruitment.param_position` i `param_place` -
gdyby pola ukryte w Tally nazywały się inaczej, zmienia się je tam, nie w kodzie.

**Do zrobienia w panelu Tally:**

1. *Integrations → Email notifications* → powiadomienie na `biuro@janmed.pl`.
   Bez tego zgłoszenia leżą tylko w Tally i nikt się o nich nie dowie.
   Warto ustawić *reply-to* na pole z e-mailem kandydata.
2. *Settings → Design* → kolor przycisku na karmazyn `#D32359`; domyślny czarny
   odstaje od reszty strony.
3. Klauzula informacyjna i zgoda na przetwarzanie danych w rekrutacji
   (patrz niżej).

Gdyby `recruitment.tally_embed` wyczyścić, strony ofert wracają do ścieżki
mailowej - działają dalej, tylko bez formularza.

Ścieżka awaryjna jest zawsze: pod formularzem stoi zdanie „Wolisz mailem?"
z adresem i tematem uzupełnionym o nazwę stanowiska.

### Analityka

Ten sam nasłuch, co przy zgłoszeniu pacjenta. Zdarzenia `form_open`,
`form_step`, `form_submit` dostają parametr `rodzaj` (`zgloszenie` albo
`rekrutacja`), a przy rekrutacji dodatkowo `oferta` ze slugiem oferty. Żeby dało
się po tym filtrować, `rodzaj` i `oferta` trzeba raz dodać w GA4 jako wymiary
niestandardowe (zakres: zdarzenie).

### Do sprawdzenia po stronie prawnej

CV to zwykłe dane osobowe, nie szczególna kategoria - ale rekrutacja to osobny
cel przetwarzania. Przed uruchomieniem: klauzula w formularzu, okres retencji
zgłoszeń i akapit o rekrutacji w polityce prywatności.

---

## Co zostało wyrzucone względem WordPressa

* Elementor + Elementor Pro (frontend.min.js, webpack runtime, elements-handlers),
  motyw Hello Elementor, jQuery + jQuery Migrate + jQuery UI - łącznie
  ~15 plików JS, których strona do niczego nie potrzebowała.
* Wtyczkowy CSS Elementora (11 arkuszy `post-*.css`) i ~50 plików fontów
  ładowanych na zapas - używane były cztery kroje.
* Yoast, panel edytora, telemetria wtyczek, pingback, emoji-script, oEmbed.

Zostało: Google Analytics (ten sam strumień) i osadzenie Tally.

## Znane błędy oryginału

Poprawione (opisane w historii commitów), bo dotyczyły kontaktu z hospicjum:

* stopka podpisywała placówkę w Kazimierzy Wielkiej jako „Hospicjum Pińczów",
* całodobowy telefon w *Instrukcji obsługi* linkował do `http://tel.696899705`
  - nieprawidłowy protokół i inny numer niż wyświetlany (698-887-816),
* przycisk „Zgłoś pacjenta" pod artykułami prowadził do `#`,
* „(np. telefonicznie)" linkowało do nieistniejącej strony `/kontakt`,
* „Podstawowe dane pacjenta dostępne w formularzu" prowadziło na stronę główną
  zamiast do formularza.

Zostawione bez zmian (treść, nie błąd techniczny): literówka „Kaziemierza"
w punktach hero oraz adres `https://janmed.pl/kontakt/` wymieniony w tekście
polityki prywatności - do decyzji, czy zmieniamy treść dokumentu.
