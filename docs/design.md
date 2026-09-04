# System wizualny JANMED

Zasady słowne. Podgląd na żywo: [`design.html`](design.html) - otwórz plik
bezpośrednio z repo albo `python3 build.py --drafts` i wejdź na
`/_drafts/design.html`.

**Jedno źródło prawdy to `css/styles.css`.** Storybook nie ma własnych wartości -
czyta ten sam arkusz co produkcja. Jeśli storybook i strona wyglądają inaczej,
ktoś nadpisał styl lokalnie i to jest błąd do cofnięcia.

---

## Skąd się wzięły te wartości

Nie z gustu. Kolory to zmienne globalne Elementora zmierzone na starej stronie,
zanim ją wyłączyliśmy. Jedyna zmiana merytoryczna to `--blue`: oryginalny
`#4597BA` daje z bielą **3.29:1**, czyli nie przechodzi AA dla tekstu.
Do tekstu i linków używamy przyciemnionego `#2C6A87` (**5.97:1**), a oryginalny
odcień został przy plamach dekoracyjnych.

To rozstrzyga konflikt, który będzie wracał: **przy tekście wygrywa dostępność,
przy dekoracji wygrywa wierność oryginałowi.** Znaczna część odwiedzających to
osoby starsze, czytające na telefonie w trudnym momencie.

---

## Kolor

| Token | Wartość | Do czego |
| --- | --- | --- |
| `--ink` | `#001A25` | Nagłówki, ciemne sekcje, stopka |
| `--body` | `#41565F` | Tekst czytany |
| `--muted` | `#5F757F` | Tekst drugorzędny, lead, podpisy |
| `--bg` | `#FAFAF9` | Tło strony |
| `--surface` | `#FFFFFF` | Karty i pola |
| `--crimson` | `#D32359` | **Wyłącznie CTA** |
| `--blue` | `#2C6A87` | Linki, kickery na jasnym |
| `--blue-mid` | `#4597BA` | Tylko dekoracja: skos, punktory, poświata |
| `--blue-light` | `#6EC1E4` | Akcenty **tylko na ciemnym tle** |
| `--cyan` | `#2AD4FF` | Logo, ikony wartości, punktory hero |
| `--line` / `--line-2` | `#E4E9EB` / `#CFD9DD` | Hairline'y |
| `--line-dark` | `rgba(255,255,255,.12)` | Linia na ciemnym |

Zasady:

* **Jeden karmazyn na ekran.** To jest ta jedna rzecz, którą chcemy, żeby człowiek
  zrobił. Dwa karmazynowe przyciski obok siebie kasują sens obu.
* Czerń nigdy nie jest czysta, biel nigdy nie jest tłem strony.
* Gradient, jeśli w ogóle, to jeden odcień razy jasność. Nigdy tęcza.
* Nowy kolor dokładamy dopiero wtedy, gdy da się powiedzieć, czego nie da się
  zrobić istniejącymi. Zwykle da się.

---

## Typografia

Dwa kroje, oba self-hostowane w `assets/fonts/` (180 KB łącznie, bez odpytywania
Google Fonts - co przy stronie medycznej upraszcza też rozdział o cookies).

* **Poppins** - display i interfejs: nagłówki, kickery, przyciski, numery telefonów.
* **Inter** - wszystko, co się czyta dłużej niż trzy słowa.

| Klasa | Rozmiar | Waga | Tracking | LH |
| --- | --- | --- | --- | --- |
| `.h-hero` | `clamp(2.35rem, 1.2rem + 4.4vw, 4rem)` | 600 | −0.032em | 1.03 |
| `.h-section` | `clamp(1.9rem, 1.1rem + 2.6vw, 2.75rem)` | 600 | −0.028em | 1.07 |
| `.h-card` | `1.25rem` | 600 | −0.018em | 1.3 |
| `.kicker` | `0.8125rem` | 500 | **+0.14em** uppercase | 1.2 |
| `.lede` | `clamp(1.0625rem, 1rem + 0.3vw, 1.1875rem)` | 400 | - | 1.65 |
| `body` | `17px` (16px mobile) | 400 | - | 1.7 |

Zasady:

* **Nagłówek zawsze z ujemnym letter-spacingiem.** Zero to najszybszy sposób,
  żeby strona wyglądała na domyślną.
* Line-height nagłówka ≤ 1.1, body 1.6-1.7. Odwrotnie niż podpowiada intuicja.
* Kicker to jedyne miejsce z dodatnim trackingiem - przy wersalikach 13px
  to konieczność, nie ozdoba.
* Trzeci krój = nie. Gramy wagą i rozmiarem.

### Pauzy

Na tej stronie używamy **zwykłego dywizu `-`**. Bez `—` i bez `–`, także
w zakresach godzin i lat. Długa pauza to najczęstszy sygnał tekstu pisanego
przez model językowy i nie chcemy go tu mieć.

Wyjątek: treść artykułów w `content/posts/` i `content/pages/` pochodzi
z oryginalnej strony i została nietknięta - tam pauzy są autorskie.

---

## Przestrzeń

| Token | Wartość |
| --- | --- |
| `--container` | 1120px |
| `--prose` | 720px |
| `--section` | `clamp(72px, 9vw, 128px)` |
| `--gutter` | `clamp(20px, 4vw, 40px)` |
| `--header-h` | 76px / 68px mobile |

Odstęp pionowy jest głównym narzędziem hierarchii - nie ramki, nie tła, nie cienie.
Jeśli wahasz się między ciaśniej a luźniej, wybierz luźniej.

### Jedna szerokość, bez wyjątków

**Tekst i karty zaczynają się zawsze na lewej krawędzi `.container`.** Logo
w belce, nagłówek hero, karty kontaktowe i stopka stoją na jednej linii - inaczej
strona robi schody i widać to z drugiego końca pokoju.

Jedyny wyjątek to **kadr z filmem w hero**: jego lewa krawędź siedzi na linii
siatki (tam, gdzie kończy się kolumna tekstu), a prawa wychodzi do krawędzi
ekranu. Służy do tego token `--bleed` - dokładnie tyle, ile brakuje od krawędzi
treści do krawędzi ekranu.

Sam hero ma **dokładnie wysokość ekranu pod belką** (`min-height: 100svh - --header-h`).
Pasek zaufania na dole ma stałą wysokość (`--trust-h`), więc całe dopasowanie
do ekranu bierze na siebie górna część - tekst i kadr. Pasek jest biały na całą
szerokość: biel sama odcina go od ciepłego tła hero, więc linia jest tylko pod nim
i idzie od krawędzi do krawędzi ekranu, bo zamyka ekran, a nie kolumnę treści. Kadr dostaje `margin-right: calc(-1 * var(--bleed))`
i ujemny `margin-block`, żeby sięgnąć też góry i dołu sekcji. Żaden inny element
nie ma prawa tego robić; `body` ma `overflow-x: clip`, żeby taki zabieg nigdy
nie zrobił poziomego suwaka.

Odstęp pod nagłówkiem sekcji jest jeden (`.section-head`, `clamp(32px, 3.4vw, 44px)`)
niezależnie od tego, czy pod nagłówkiem jest lead, czy od razu karty.
Kotwice sekcji mają ujemny `scroll-margin-top` o wartość górnego paddingu sekcji -
skok w „Kontakt" ma pokazać nagłówek, a nie pusty padding nad nim.

---

## Kształt i głębia

Jedna szkoła: miękka. `--r-card` 14px, `--r-sm` 10px, `--r-btn` 8px,
`--r-pill` 999px. Nie mieszamy więcej niż dwóch promieni na ekranie.

Głębia idzie przez hairline'y. Cienie są bardzo niskiego krycia (0.04-0.09)
i mają bazę tonowaną w `--ink`, nigdy w czystej czerni:

```css
--sh-1: 0 1px 2px rgba(0,26,37,.04);
--sh-2: 0 1px 2px rgba(0,26,37,.04), 0 12px 32px rgba(0,26,37,.06);
--sh-3: 0 2px 4px rgba(0,26,37,.05), 0 24px 56px rgba(0,26,37,.09);
```

---

## Przyciski

`.btn` - karmazyn, wersaliki, waga 600, tracking +0.075em, promień 8px.

| Modyfikator | Kiedy |
| --- | --- |
| *(brak)* | Akcja główna. Jedna na kontekst. |
| `.btn--ghost` | Akcja poboczna **na jasnym tle** |
| `.btn--ghost-light` | Akcja poboczna **na ciemnym tle** |
| `.btn--blue` | Rzadko, gdy karmazyn byłby zbyt krzykliwy |
| `.btn--sm` | Pasek cookies, ciasne miejsca |

### Adres e-mail jako przycisk

Nie ma osobnego przycisku „Wyślij e-mail" - **adres sam jest przyciskiem**.
`.btn.copy-btn` w `.copy-wrap` kopiuje wartość z `data-copy` do schowka
i pokazuje `.copy-note` na 2.6 s.

Dwie rzeczy są tu ważne:

* `.copy-btn` wygląda jak każdy inny przycisk (kształt, wysokość, promień),
  tylko bez wersalików - adres e-mail pisany kapitalikami przestaje być adresem.
* `.copy-note` jest **pozycjonowane absolutnie nad przyciskiem**. Wcześniej
  wjeżdżało w układ i rozpychało kartę w momencie kliknięcia; teraz lewituje
  i nic pod nim nie drgnie. Etykieta ma `role="status"`, więc czytniki ekranu
  ogłaszają ją same, a ścieżka awaryjna (brak schowka) pokazuje adres w treści
  komunikatu, żeby dało się go przepisać ręcznie.

---

## Rytm sekcji

Strona oddycha naprzemiennie jasnym i ciemnym. **Nigdy dwie ciemne sekcje
pod rząd** bez czegoś jasnego pomiędzy.

* `.section` - domyślna, tło strony
* `.section--dark` - ink, tekst `--on-dark-2`, nagłówki białe
  (sekcja „Wesprzyj działalność hospicjum" jest **jasna** - tak było
  na oryginalnej stronie i tak zostaje)
* `.section--tinted` - delikatny wash pod sekcją kontaktu
* `.section--misja` - `padding-bottom: 0` plus `overflow: hidden`;
  wycięta postać wychodzi wprost z tła sekcji, bez ramki i bez karty
* `.section--flush` - treść startująca zaraz pod nagłówkiem strony albo okruszkami
* `.page-hero--figure` - ten sam chwyt co w misji, ale w nagłówku podstrony:
  siatka `tekst | postać`, postać przycięta dolną krawędzią sekcji i podświetlona
  poświatą zamiast obrysu. **Rozmiar postaci liczy się od wysokości sekcji**
  (`--figure-h: calc(var(--figure-min-h) + X)`, `width: auto`), nie od wysokości
  ekranu - powiększenie postaci ma wypełnić nagłówek, a nie rozciągnąć go w dół.
  Kolumna wyznacza tylko lewą krawędź: obraz może wyjść poza prawą krawędź
  ekranu, ale nigdy nie wchodzi na tekst. Poświata to **koło na środku zdjęcia**,
  nie elipsa i nie przesunięta w bok

---

## Ruch

Animujemy **wyłącznie `opacity` i `transform`**.
`--ease: cubic-bezier(.16, 1, .3, 1)`, `--dur: 420ms`.

* Wejście w kadr: fade + 14px w górę, 700ms
* **Jedno tempo dla całej strony:** krok opóźnienia to 80 ms, najwyżej trzy kroki
  (`stagger()` w `build.py`). Sekcje nie mają prawa animować się w różnym rytmie
* Obserwator startuje po dwóch klatkach - inaczej elementy widoczne od razu
  dostają klasę przed pierwszym malowaniem i pojawiają się bez animacji
* `.reveal--media` (kadry i zdjęcia): samo przejaśnienie, bez ruchu - obraz
  przesuwający się w kadrze czyta się jak usterka, nie jak animacja
* Hover karty: `translateY(-3px)` i mocniejszy cień
* Hover zdjęcia w karcie: `scale(1.035)` przez 700ms
* Nawigacja: podkreślenie `scaleX` z lewej krawędzi

Dwie rzeczy nienegocjowalne:

1. **`prefers-reduced-motion` wyłącza wszystko.** Na stronie hospicjum to nie jest
   opcja do rozważenia.
2. **Bezpiecznik czasowy na scroll-reveal.** Jeśli `IntersectionObserver` nie
   zadziała (ukryta karta, nietypowa przeglądarka, błąd JS), po 3s treść pokazuje
   się i tak. Treść nie ma prawa zniknąć przez animację - przekonaliśmy się o tym
   w praktyce, gdy podgląd w ukrytym panelu nigdy nie odpalił obserwera i cała
   strona była pusta.

---

## Ikony

Cztery ikony wartości (`templates/icons/*.svg`) są wzorcem dla wszystkich
kolejnych. Nowa ikona pasuje do zestawu, jeśli trzyma się pięciu rzeczy:

| Cecha | Wartość |
| --- | --- |
| Konstrukcja | **wypełnienia, nie kontury** - żadnego `stroke`, całość na `<path fill>` |
| viewBox | ok. `0 0 48 48`, rysunek wpisany w kwadrat 42-48 px |
| Kolor główny | `currentColor` - dziedziczy po `.value__icon` (czyli `--ink`) |
| Akcent | dokładnie **jeden** element w `var(--icon-accent, #2AD4FF)` |
| Atrybuty | `aria-hidden="true" focusable="false" fill="none"`, `clip-rule="evenodd"` |

Akcent to jedno miejsce w rysunku, nie druga warstwa: serce, iskra, dach.
Ikona bez akcentu wygląda na wyciętą z innego zestawu, ikona z dwoma akcentami
przestaje mieć punkt zaczepienia dla oka.

Rozmiar w układzie: 42 px (`.value__icon svg`), odstęp pod ikoną 22 px.
Ikony interfejsowe (strzałka, kopiuj, info) to osobna rodzina - **te są konturowe**,
`stroke-width: 1.4-1.8`, 14-22 px, i mieszkają w `build.py` jako stałe.

---

## Obrazy

* Zdjęcia sytuacyjne: JPEG, maksymalnie 1600-1800px, jakość 68-80.
* Portrety wycięte z tła: WebP z alfą + PNG jako `<picture>` fallback tam, gdzie
  WebP istnieje; nowsze wycinki jadą na razie jako samo PNG (na tej maszynie nie
  ma enkodera WebP - `sips` go nie robi, `cwebp` nie jest zainstalowany).
  Wycinanie: `docs/cutout-tla.swift` (Vision, lokalnie, bez wysyłania nigdzie).
  Skrypt przyjmuje opcjonalny numer instancji - zdjęcie z dwiema osobami ma dwie,
  więc `swift docs/cutout-tla.swift zdjecie.jpg out.png 1` wycina samą pierwszą
  postać, przyciętą do jej obrysu.
* Każdy `<img>` ma `width`, `height` i `alt`. Obrazek dekoracyjny wewnątrz
  linku z tytułem dostaje `alt=""` - inaczej czytnik czyta to dwa razy.
* Pierwsze trzy karty w siatce ładują się `fetchpriority="high"`, reszta leniwie.

---

## Zanim dodasz nowy token

1. Sprawdź, czy istniejący nie wystarczy. Zwykle wystarcza.
2. Jeśli naprawdę nie - dopisz go do bloku `:root` w `css/styles.css`
   **i dodaj próbkę w `design.html`**. Token bez próbki za pół roku nie istnieje.
3. Kolor tekstu: policz kontrast przed dodaniem. Próg to 4.5:1.
