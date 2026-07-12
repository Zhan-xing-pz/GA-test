# CRAG Benchmark Skill

Use this skill when answering CRAG benchmark questions. CRAG questions are designed to test verified tool use: use the CRAG mock API tools when the answer requires external data.

## Execution Contract

The only executable GA tool in this route is `code_run`. Do not emit native CRAG tool calls directly. Import `call_crag_tool` from `crag_toolkit` and pass the CRAG tool name as a string.

```python
from crag_toolkit import call_crag_tool

print(call_crag_tool(
    tool_name="finance_get_ticker_by_name",
    arguments={"query": "Apple"},
))
```

The wrapper returns one JSON object:

```text
{"ok": true, "tool_name": "...", "arguments": {...}, "observation": "..."}
```

On failure it returns:

```text
{"ok": false, "tool_name": "...", "arguments": {...}, "error": "..."}
```

Read `observation` before choosing the next action. `list_crag_tools()` can be used in `code_run` to inspect schemas, but the complete reference is listed below.

## Working Rules

1. Read the question and `query_time`.
2. Select a domain-specific tool before using Open-domain entity search. Do not treat Open KG as the default for finance, movie, music, or sports questions.
3. Extract exact names, dates, years, ranks, tickers, IDs, and attributes from the question. Dates must use the format required by the selected tool.
4. Inspect every observation. If it is empty or ambiguous, change the entity, arguments, or tool; never repeat the same failed call with identical arguments.
5. Use `query_time` for time-sensitive questions. Do not substitute current real-world information.
6. When sufficient evidence has been collected, return only a concise answer. If the available tools cannot support an answer after reasonable attempts, return `I don't know`.

## Tool Reference

### Universal

```text
list_crag_tools()
-> tool schema list
-- Inspect the currently available CRAG tool names, parameter schemas, and descriptions.

answer
-> plain final text
-- Do not call this through crag_toolkit. Write the final answer directly in natural text.
```

### Finance

```text
finance_get_company_name(query: str)
-> str[]
-- Search for company names matching a query.

finance_get_ticker_by_name(query: str)
-> str | null
-- Get a stock ticker from a company name.

finance_get_price_history(ticker_name: str)
-> {[timestamp]: {Open, High, Low, Close, Volume}}
-- Get one year of daily OHLCV price history for a ticker.

finance_get_detailed_price_history(ticker_name: str)
-> {[timestamp]: {Open, High, Low, Close, Volume}}
-- Get five days of minute-level OHLCV price history for a ticker.

finance_get_dividends_history(ticker_name: str)
-> {[timestamp]: float}
-- Get dividend payment history for a ticker.

finance_get_market_capitalization(ticker_name: str)
-> float
-- Get a company's market capitalization.

finance_get_eps(ticker_name: str)
-> float | null
-- Get earnings per share (EPS).

finance_get_pe_ratio(ticker_name: str)
-> float | null
-- Get price-to-earnings ratio (PE).

finance_get_info(ticker_name: str)
-> {symbol, shortName, exchange, currency, currentPrice, marketCap, industry, sector, ...}
-- Get general financial and company information.
```

For a finance question with a company name rather than a ticker, normally call `finance_get_ticker_by_name` first.

### Movie

```text
movie_get_person_info(person_name: str)
-> {name, acted_movies, directed_movies, birthday, oscar_awards, ...}
-- Search the movie database for an actor or director using the person name.

movie_get_movie_info(movie_name: str)
-> {title, release_date, budget, revenue, rating, genres, oscar_awards, cast, crew, ...}
-- Search the movie database for a title using the movie name.

movie_get_year_info(year: str)
-> {movies, oscar_awards}
-- Get movies and Oscar awards for a year from 1990 through 2021. Use a four-digit year, for example `"1992"`.

movie_get_movie_info_by_id(movie_id: int)
-> {title, release_date, budget, revenue, rating, genres, ...}
-- Get movie details by a movie ID returned by another lookup.

movie_get_person_info_by_id(person_id: int)
-> {name, acted_movies, directed_movies, birthday, oscar_awards, ...}
-- Get person details by a person ID returned by another lookup.
```

### Music

```text
music_search_artist_entity_by_name(artist_name: str)
-> str[]
-- Fuzzy-search music artists and return at most 10 matching names.

music_search_song_entity_by_name(song_name: str)
-> str[]
-- Fuzzy-search songs and return at most 10 matching names.

music_get_billboard_rank_date(rank: int, date?: str)
-> {song, artist} | {[date]: {song, artist}}
-- Get the song and artist at a Billboard rank on a date. Use `YYYY-MM-DD` when a date is provided.

music_get_billboard_attributes(date: str, attribute: str, song_name: str)
-> str | int
-- Get a Billboard attribute for a song on a date. `attribute` can be `rank_last_week`, `weeks_in_chart`, `top_position`, or `rank`.

music_grammy_get_best_artist_by_year(year: int)
-> str
-- Get the Grammy Best New Artist for a year from 1958 through 2019.

music_grammy_get_award_count_by_artist(artist_name: str)
-> int
-- Get an artist's Grammy award count from 1958 through 2019.

music_grammy_get_award_count_by_song(song_name: str)
-> int
-- Get a song's Grammy award count from 1958 through 2019.

music_grammy_get_best_song_by_year(year: int)
-> str
-- Get the Grammy Song of the Year for a year from 1958 through 2019.

music_grammy_get_award_date_by_artist(artist_name: str)
-> int[]
-- Get the Grammy award years for an artist.

music_grammy_get_best_album_by_year(year: int)
-> str
-- Get the Grammy Album of the Year for a year from 1958 through 2019.

music_grammy_get_all_awarded_artists()
-> str[]
-- Get all Grammy Best New Artist winners from 1958 through 2019.

music_get_artist_birth_place(artist_name: str)
-> str
-- Get an artist's birth place as a two-letter ISO-3166 country code.

music_get_artist_birth_date(artist_name: str)
-> str
-- Get an artist's birth date, or a band's formation date.

music_get_members(band_name: str)
-> str[]
-- Get a band's members.

music_get_lifespan(artist_name: str)
-> {birth, death}
-- Get an artist's birth and death dates.

music_get_song_author(song_name: str)
-> str
-- Get a song's author.

music_get_song_release_country(song_name: str)
-> str
-- Get a song's release country as a two-letter ISO-3166 country code.

music_get_song_release_date(song_name: str)
-> str
-- Get a song's release date in `YYYY-MM-DD` format.

music_get_artist_all_works(artist_name: str)
-> str[]
-- Get all works by an artist, including songs and albums.
```

### Sports

```text
sports_soccer_get_games_on_date(date: str, team_name?: str)
-> [{venue, result, goals, opponent, captain, ...}]
-- Get soccer matches on a date. Use `YYYY-MM-DD`; optionally narrow to a team.

sports_nba_get_games_on_date(date: str, team_name?: str)
-> [{game_id, teams, win_loss, points, ...}]
-- Get NBA games on a date. Use `YYYY-MM-DD`; optionally narrow to a team. Save returned `game_id` values for play-by-play lookup.

sports_nba_get_play_by_play_data_by_game_ids(game_ids: str[])
-> [{event, time, player, ...}]
-- Get NBA play-by-play records for one or more `game_id` values returned by `sports_nba_get_games_on_date`.
```

Sports questions about a particular game should normally use `sports_nba_get_games_on_date` or `sports_soccer_get_games_on_date` first, then use NBA game IDs for play-by-play data when event-level evidence is needed.

### Open Domain

```text
open_search_entity_by_name(query: str)
-> str[]
-- Search encyclopedia entity names and return at most 10 candidates.

open_get_entity(entity: str)
-> {summary, structured_summary, raw_wiki}
-- Get detailed encyclopedia information for an exact entity name returned by search.
```

Use Open-domain tools for general encyclopedic questions or to resolve an entity name. Do not keep retrying Open search for a finance, movie, music, or sports question when domain-specific tools are available.

## Final Answer Rules

- Return only the answer, not chain-of-thought or tool traces.
- Keep answers short: usually a name, date, number, yes/no, or short phrase.
- If multiple items are requested, separate them clearly with commas.
- Do not claim that a fact is unavailable until the relevant domain-specific tools have been tried.
