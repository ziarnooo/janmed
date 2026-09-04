# Formularz zgłoszeniowy - inwentarz pól

Formularz żyje w **Tally** (`tally.so/embed/5B4vYb`) i jest osadzony na
[/formularz-zgloszeniowy-do-hospicjum-domowego/](../dist/formularz-zgloszeniowy-do-hospicjum-domowego/).
Ten plik to spis tego, co formularz zbiera - na wypadek migracji albo audytu RODO.

> **Uwaga.** Formularz zbiera dane szczególnej kategorii (art. 9 RODO): PESEL,
> skierowanie, kartę informacyjną ze szpitala. Przeniesienie go „na nasze" to nie
> jest zadanie frontendowe - patrz sekcja na końcu.

## Krok 1 - pacjent

| Pole | Typ | Wymagane |
| --- | --- | --- |
| Imię pacjenta | tekst | tak |
| Nazwisko pacjenta | tekst | tak |
| Numer PESEL pacjenta | tekst | tak |
| Do której placówki chcesz zgłosić pacjenta? | wybór: Olkusz / Kazimierza Wielka / Pińczów | tak |
| Forma zgłoszenia | wybór: Zeskanuje skierowanie / Wpisze kod skierowania | tak |
| → skan skierowania | plik, limit 10 MB | zależne |
| → kod skierowania | tekst | zależne |

Tekst pomocniczy: „Wgraj skan skierowania papierowego **lub** przepisz *kod
skierowania* ze skierowania elektronicznego. Oryginał skierowania papierowego
należy przekazać lekarzowi podczas pierwszej wizyty."

## Krok 2 - adres pacjenta

| Pole | Typ | Wymagane |
| --- | --- | --- |
| Ulica | tekst | tak |
| Numer domu | tekst | tak |
| Numer mieszkania | tekst | nie |
| Kod pocztowy | tekst | tak |
| Miasto | tekst | tak |
| Telefon kontaktowy do pacjenta | tekst | nie |

## Krok 3 - opiekun

| Pole | Typ | Wymagane |
| --- | --- | --- |
| Imię opiekuna | tekst | tak |
| Nazwisko opiekuna | tekst | tak |
| Pokrewieństwo | tekst | tak |
| Telefon kontaktowy do opiekuna | tekst | tak |
| E-mail do opiekuna | e-mail | tak |

## Krok 4 - dokumenty

| Pole | Typ | Wymagane |
| --- | --- | --- |
| Skan/zdjęcia (dwustronnie) legitymacji emeryta/rencisty | plik, limit 10 MB | tak |
| Skan ostatniej KARTY INFORMACYJNEJ ze szpitala (wszystkie strony) | plik, limit 10 MB | tak |

## Krok 5 - potwierdzenie

> **Formularz wysłano**
> Skontaktujemy się z Państwem w możliwie najkrótszym czasie, aby omówić dalsze
> kroki opieki.
> W razie pilnych pytań prosimy o kontakt telefoniczny.

CTA: „Wróć na stronę główną" · „Wspomóż działalność hospicjum"

## Gdyby kiedyś schodzić z Tally

Statyczna strona na GitHub Pages nie ma backendu, więc dane i tak muszą trafić do
jakiegoś procesora. Minimalny wariant, który nie jest gorszy od Tally:

1. Endpoint po stronie serwera w UE (np. funkcja na Scaleway / Hetzner / OVH),
   HTTPS, rate limiting, bez logowania treści zgłoszeń.
2. Szyfrowanie plików w spoczynku, dostęp tylko dla rejestracji hospicjum.
3. Retencja - automatyczne kasowanie po X dniach od przyjęcia/odrzucenia.
4. Umowa powierzenia z każdym dostawcą (hosting, storage, poczta) i wpis do
   rejestru czynności przetwarzania.
5. Aktualizacja polityki prywatności o nowego procesora.

Do czasu, aż powyższe będzie ustalone z IOD-em, formularz zostaje na Tally.
