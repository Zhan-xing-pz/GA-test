# CRAG Benchmark Skill

Use this skill when answering CRAG benchmark questions. CRAG questions are designed to test tool use: answer only after using the provided search results and/or the CRAG mock API tools when needed.

## Core Loop

For each question:

1. Read the question, domain, query_time, and any search_results file/content.
2. Decide the next CRAG tool and its arguments from the question and previous observations.
3. Call the tool through `memory/crag_toolkit.py` using `code_run`.
4. Inspect the observation.
5. If the observation supports a concise answer, provide the final answer only.
6. If not, call another CRAG tool with improved arguments.
7. If evidence is still insufficient after reasonable attempts, answer `I don't know`.

Do not answer from general world knowledge when a CRAG tool or the provided search results should verify the fact.

## Tool Call Format

Use `code_run` with Python. The stable interface is:

```python
from crag_toolkit import call_crag_tool

print(call_crag_tool(
    tool_name="finance_get_ticker_by_name",
    arguments={"query": "Apple"},
    search_results_file="path/to/search_results.json"
))
```

Arguments:

- `tool_name`: exact CRAG tool name.
- `arguments`: JSON-like dict matching that tool's parameters.
- `search_results_file`: optional path to the current sample's search results JSON. Use this for `web_search` and pass it for other calls when available.

The toolkit returns a JSON string with either:

```json
{"ok": true, "tool_name": "...", "arguments": {...}, "observation": "..."}
```

or:

```json
{"ok": false, "tool_name": "...", "arguments": {...}, "error": "..."}
```

Treat `observation` as the tool result for the next reasoning step.

## Common Tool Names And Parameters

Universal:

- `web_search({"query": "..."})`: search within the sample's provided search snippets.
- `answer` is not a mock API call. Do not call it through the toolkit; just final-answer in natural text.

Finance:

- `finance_get_company_name({"query": "..."})`
- `finance_get_ticker_by_name({"query": "..."})`
- `finance_get_price_history({"ticker_name": "..."})`
- `finance_get_detailed_price_history({"ticker_name": "..."})`
- `finance_get_dividends_history({"ticker_name": "..."})`
- `finance_get_market_capitalization({"ticker_name": "..."})`
- `finance_get_eps({"ticker_name": "..."})`
- `finance_get_pe_ratio({"ticker_name": "..."})`
- `finance_get_info({"ticker_name": "..."})`

Movie:

- `movie_get_person_info({"person_name": "..."})`
- `movie_get_movie_info({"movie_name": "..."})`
- `movie_get_year_info({"year": "YYYY"})`
- `movie_get_movie_info_by_id({"movie_id": 123})`
- `movie_get_person_info_by_id({"person_id": 123})`

Music:

- `music_search_artist_entity_by_name({"artist_name": "..."})`
- `music_search_song_entity_by_name({"song_name": "..."})`
- `music_get_billboard_rank_date({"rank": 1, "date": "YYYY-MM-DD"})`
- `music_get_billboard_attributes({"date": "YYYY-MM-DD", "attribute": "...", "song_name": "..."})`
- `music_grammy_get_best_artist_by_year({"year": 2010})`
- `music_grammy_get_award_count_by_artist({"artist_name": "..."})`
- `music_grammy_get_award_count_by_song({"song_name": "..."})`
- `music_grammy_get_best_song_by_year({"year": 2010})`
- `music_grammy_get_award_date_by_artist({"artist_name": "..."})`
- `music_grammy_get_best_album_by_year({"year": 2010})`
- `music_grammy_get_all_awarded_artists({})`
- `music_get_artist_birth_place({"artist_name": "..."})`
- `music_get_artist_birth_date({"artist_name": "..."})`
- `music_get_members({"band_name": "..."})`
- `music_get_lifespan({"artist_name": "..."})`
- `music_get_song_author({"song_name": "..."})`
- `music_get_song_release_country({"song_name": "..."})`
- `music_get_song_release_date({"song_name": "..."})`
- `music_get_artist_all_works({"artist_name": "..."})`

Sports:

- `sports_soccer_get_games_on_date({"date": "YYYY-MM-DD", "team_name": "..."})`
- `sports_nba_get_games_on_date({"date": "YYYY-MM-DD", "team_name": "..."})`
- `sports_nba_get_play_by_play_data_by_game_ids({"game_ids": ["..."]})`

Open:

- `open_search_entity_by_name({"query": "..."})`
- `open_get_entity({"entity": "..."})`

## Parameter Strategy

- Extract exact entity names, dates, years, ranks, tickers, IDs, and attributes from the question.
- If a finance question gives a company name, first get the ticker unless the ticker is explicit.
- If a question needs current or time-sensitive evidence, use `query_time` and the available CRAG data; do not assume today's real-world date.
- If the first tool result is empty or ambiguous, use `web_search` or an entity search tool to normalize the entity name before trying the specific tool again.
- Do not repeat the same failed tool call with the same arguments.

## Final Answer Rules

- Return only the answer, not the reasoning.
- Keep answers short: usually a name, date, number, yes/no, or short phrase.
- If multiple items are requested, separate them clearly with commas.
- If the evidence does not support an answer, return `I don't know`.
