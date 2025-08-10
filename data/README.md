# Static Dataset

The following dataset are static and can be manually updated before running Python bot.

## Dataset

* `character_nfl_mapping.json` - (Character x NFL Team Key) Pair
* `characters.json` - Characters info
    * TO BE DETERMINED
* `nfl_Teams.json` - NFL Teams info
    * `id` is used to find specific team when calling NFL API
* `storyline.json` - Gameweek storyline
    * Contains template for the following
        * Small win (1-15 points)
        * Big win (+15 points)
        * Ties
        * Upcoming games (yet to be played)