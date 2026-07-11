# CRAG Benchmark Skill - Route A (code_run only)

This route exposes only one executable GA tool: `code_run`. Do not emit native CRAG tool calls. To use a CRAG tool, run Python code that imports `call_crag_tool` from `crag_toolkit`.

Example:
```python
from crag_toolkit import call_crag_tool
print(call_crag_tool("open_search_entity_by_name", {"query": "Steve Nash"}))
```

# CRAG Benchmark Skill

Use this skill when answering CRAG benchmark questions. CRAG questions are designed to test tool use: answer only after using the CRAG mock API tools when needed.

## Core Loop

For each question:

1. Read the question and query_time.
2. Decide the next CRAG tool and its arguments from the question and previous observations.
3. Call the tool through `memory/crag_toolkit.py` using `code_run`.
4. Inspect the observation.
5. If the observation supports a concise answer, provide the final answer only.
6. If not, call another CRAG tool with improved arguments.
7. If evidence is still insufficient after reasonable attempts, answer `I don't know`.

Do not answer from general world knowledge when a CRAG tool or the provided search results should verify the fact.


## Important Tool-Use Constraint

The only executable tool available to you is `code_run`. Do not call CRAG tool names as native tools.
For example, never emit a direct tool call named `open_search_entity_by_name`, `finance_get_info`,
`sports_nba_get_games_on_date`, or any other CRAG tool name. Those names are only string values
passed inside Python to `call_crag_tool`.

Correct pattern:

```python
from crag_toolkit import call_crag_tool
print(call_crag_tool("open_search_entity_by_name", {"query": "Steve Nash"}))
```

Incorrect pattern:

```text
open_search_entity_by_name({"query": "Steve Nash"})
```

## Tool Call Format

Use `code_run` with Python. The stable interface is:

```python
from crag_toolkit import call_crag_tool

print(call_crag_tool(
    tool_name="finance_get_ticker_by_name",
    arguments={"query": "Apple"}
))
```

Arguments:

- `tool_name`: exact CRAG tool name.
- `arguments`: JSON-like dict matching that tool's parameters.

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

- `list_crag_tools()` can be used to inspect available tool schemas.
- `answer` is not a mock API call. Do not call it through the toolkit; just final-answer in natural text.

Finance:

- `"finance_get_company_name"` with arguments `{"query": "..."}`
- `"finance_get_ticker_by_name"` with arguments `{"query": "..."}`
- `"finance_get_price_history"` with arguments `{"ticker_name": "..."}`
- `"finance_get_detailed_price_history"` with arguments `{"ticker_name": "..."}`
- `"finance_get_dividends_history"` with arguments `{"ticker_name": "..."}`
- `"finance_get_market_capitalization"` with arguments `{"ticker_name": "..."}`
- `"finance_get_eps"` with arguments `{"ticker_name": "..."}`
- `"finance_get_pe_ratio"` with arguments `{"ticker_name": "..."}`
- `"finance_get_info"` with arguments `{"ticker_name": "..."}`

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

- `"sports_soccer_get_games_on_date"` with date/team arguments
- `"sports_nba_get_games_on_date"` with date/team arguments
- `"sports_nba_get_play_by_play_data_by_game_ids"` with game_ids arguments

Open:

- `"open_search_entity_by_name"` with arguments `{"query": "..."}`
- `"open_get_entity"` with arguments `{"entity": "..."}`

## Parameter Strategy

- Extract exact entity names, dates, years, ranks, tickers, IDs, and attributes from the question.
- If a finance question gives a company name, first get the ticker unless the ticker is explicit.
- If a question needs current or time-sensitive evidence, use `query_time` and the available CRAG data; do not assume today's real-world date.
- If the first tool result is empty or ambiguous, use an entity search/lookup tool to normalize the entity name before trying the specific tool again.
- Do not repeat the same failed tool call with the same arguments.

## Final Answer Rules

- Return only the answer, not the reasoning.
- Keep answers short: usually a name, date, number, yes/no, or short phrase.
- If multiple items are requested, separate them clearly with commas.
- If the evidence does not support an answer, return `I don't know`.
