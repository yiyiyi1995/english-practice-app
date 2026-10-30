# Third-Party Notices

## ts-fsrs

The vocabulary review scheduler uses [open-spaced-repetition/ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs), distributed under the MIT License.

- Vendored browser build: `vendor/ts-fsrs.umd.js`
- License copy: `vendor/ts-fsrs.LICENSE`

Copyright (c) 2022 Open Spaced Repetition

## CEFR English word-list data

The files under `data/` are sourced from:

- Project: [lratusa/wordmaster-wordlists](https://github.com/lratusa/wordmaster-wordlists)
- Files: `english/cefr_a1.json` through `english/cefr_c2.json`
- Retrieved: 2026-10-23

The upstream project states that its word lists are available under the MIT License and identifies the underlying CEFR vocabulary profile data as originating from CEFR-J / Octanove sources under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

To preserve the upstream attribution and share-alike requirements, the CEFR data files in this repository are distributed under CC BY-SA 4.0. The application source code remains licensed under the repository's MIT License.

Changes made in this repository are limited to selecting and loading the data locally; the downloaded JSON records are otherwise preserved as provided by the upstream project.

## Commute feed metadata

`data/commute.json` contains titles, short descriptions, dates and links obtained from public RSS feeds. Audio and full articles remain hosted by and linked to their original publishers:

- [BBC Global News Podcast](https://www.bbc.co.uk/programmes/p02nq0gn)
- [BBC 6 Minute English](https://www.bbc.co.uk/learningenglish/english/features/6-minute-english)
- [Practical AI](https://changelog.com/practicalai)
- [BBC World News](https://www.bbc.com/news/world)
- [MIT Technology Review — Artificial Intelligence](https://www.technologyreview.com/topic/artificial-intelligence/)
- [OpenAI News](https://openai.com/news/)

All podcast recordings, article text, trademarks and feed metadata remain the property of their respective publishers. Inclusion in this project does not place third-party content under the repository's MIT License.
