# How Packit team does Kanban?

Packit team follows the Kanban methodology but does not just use a board with `todo`/`wip`/`done` columns. We have a couple of extra columns and rules. Let's take a look!

## Packit Kanban Board

The current board is publicly available at https://github.com/orgs/packit/projects/7.

### Card states (board columns)

#### `new`

This is a column where all the new cards are added (automatically for public repositories, via GitHub action for private ones). At the beginning of each [Standup meeting](./meetings#Standup), a [triaging](#Triage) of new unassigned cards happens resulting in either moving the card away into one of the other states or assigning a team member to further investigate and finish the triaging. Also, the card can be moved back to the `new` column if we realise the card is not clear or needs attention (e.g. to verify its relevance). This can happen when going through old cards during [Standup](./meetings#Standup).

#### `backlog`

This is a pile of cards that have been basically categorized but are not a current priority (such cards are present in the `priority-backlog`), or it is not within our capacity to finish them within the next 3 months. The order of this column is not maintained.

#### `priority-backlog`

This is an ordered list of categorized cards that the team is considering for the upcoming work. Their priority is determined based on impact, user value, urgency and current team plans and capacity. The team revisits the epic-level priorities quarterly and the cards in the `priority-backlog` should be finished in 3 months. This means the number of cards needs to be maintained to be below ~50.

#### `refined`

This column consists of cards prepared to be worked on next when someone has capacity. The tasks should be actionable right away and doable by anyone. To get a card to this state a [refining process](#Refine) is used.

#### `in-progress`

When a card is taken by someone from a `refined` column, it is assigned to that person and moved to this column. This is the list of cards that are being actively worked on.

#### `in-review`

These tasks are nearly finished, being reviewed and polished.

#### `done`

This is the column where all the done cards result.

### Card labels

Here is a list of labels we use to categorize cards to help ourselves navigate through the backlog and plan our work.
Note that there is no priority label since this consists of multiple factors like _impact_ and _gain_. Combined with the urgency, our current plans (based on demand) and capacity, this is visible from the place on the board.

#### Area

These labels help to group related cards across all the projects. The area can determine a target git-forge (e.g. `area/github`/`area/gitlab`), service being integrated (e.g. `area/testing-farm` or `area/copr`) or a shared code-level logic (e.g. `area/config` or `area/database`).

#### Complexity

This is a rough estimation of how much time is expected for this card to be done. Mainly to separate epics from single cards. Epics covers work consisting of multiple tasks, usually taking more time and being discussed in quarterly meetings.

#### Gain

This determines the value it gives to affected users.

- `gain/high`: significant change for the user, e.g.:
  - New users can start using Packit.
  - Significant time is saved for the user when the task is done.
  - A user might stop using Packit when not available.
- `gain/low`: change not so important to start/stop using Packit, e.g.:
  - If `workaround-exists` (separate label).
  - User can fully benefit from Packit without the card being done.

#### Impact

These labels determine the size of a user group affected by this card combined with a frequency. To make this comparable, it is based on generic user roles like `upstream-developer` or `fedora-maintainer`. This means we won't mark a card as high-impactful when all (but a few in reality) users of a rare functionality are affected.

This needs to be combined with frequency -- this means how often they can benefit from a new feature or how often an issue is hit.

- `impact/high`: Many users are affected by this card and the occurrence is significant.
- `impact/low`: The card affects only a few users and/or rarely-used features. The issues are not hit often.

#### `blocked`

This label is used to show that we can't move this card/work forward because of an external reason. For a reason, this is not a board state since the card can be blocked on various states of the development.

#### `resource-reduction`

This label marks tasks that can lead to better resource utilisation. (Without significant functional loss, fewer resources can be spent.)

#### `discuss`

This label helps us gather cards to be discussed in weekly architecture meetings.

### Story points

Despite using Kanban, we use the Fibonnacci sequence numbers as story points similarly to Scrum to estimate the card's complexity, uncertanity and effort. As described in the [section about Refinement meeting](meetings#refinement), the main purpose of the sizing in our team is to bring up discussion and find differences in the task understanding. As with regular Kanban where all the cards are made similar in time, we split all cards that can take more than a few days by not allowing cards with more than 5 story points.

#### Story point scale

This is how we think about the scale:

- `1`: Very simple card done in ~20 minutes. Everything is clear and straightforward. No unknown at all.
- `2`: Easy card, a bit of thought required, but the ask is clear, well defined and should take at most a day to finish. Complications are not expected.
- `3`: Average task requiring a couple of days to finish. A bit of unknown is possible but usually does not require much interaction with anyone else and the outcome is clearly defined.
- `5`: Well-defined but complex card that can take a week to finish. Can span across multiple projects, usually requires some extra discussion and updating as part of the review process.
- `8`: This is a complex task that can take someone more than a week to finish. We avoid such cards since such cards usually contain a lot of unknowns and can easily take multiple weeks to finish for real.

#### Action items / for discussion (Section to be removed before merging.)

##### To remove:

- `needs-info` (`new` state)
- `needs-design` (not used)
- `pinned`
- `triaged`
- `invalid`
- `RHOSC`, `GSOC`
- Is `has-release-notes` still relevant?
- Do `wontfix` and `invalid` labels provide any value when the issue is closed and marked as not planned with a comment?

##### Edits

- Rename `area/refactor` to `area/technical-debt`.
- Rename `testing` to `area/testing`

##### Questions

- Do we need complexity?
- Do we need `kind/documentation`? (We have a separate project for doc-only cards and don't mention this explicitly on other cards.)

### Grooming process cheat sheet:

### Triage

:::note

Process of handling new cards and categorizing them.

:::

1. Triaging
   1. **_Is the card not valid or out of our scope?_** => Politely provide reasoning and close the issue as not planned.
   2. **_Do we have a related card for this?_** => Link the relevant cards, and add to an epic if applicable. Link and close in favour of a duplicate issue if applicable.
   3. **_Do we need to get more information from the requester? Is it necessary for a team-member to take a look?_** => Assign a person to continue with the discussion and leave it in the `new` column.
   4. **_Is the task actionable and do we have a clear understanding of the card's purpose and the solution direction??_** => Enhance the title and description, if needed, and move outside of the `new` column.
   5. **_Does the issue come from an external person and there is a chance of contributing this?_** => Politely ask if the requester would be able to contribute this with our help.
2. Labelling
   1. **_Can we get a new Packit user or allow an already onboarded user to start using another Packit's functionality? Can this influence the decision of a user whether Packit will be integrated in the future?_** => Add `gain/high` label.
      **_Is there a workaround or the feature is not significant to the user?_** => use `gain/low`.
   2. **_Is this affecting many users from a role group (e.g. Fedora maintainers, Upstream developers, etc.)? Can this bring a significant number of new users?_** => Add `impact/high`, add `impact/low` otherwise.
   3. Add a `demo` label to tasks that are worth presenting to the team or users.
   4. Add `area/*`, `kind/*` and other suitable labels if needed.
   5. Add a deadline if applicable.
3. Prioritising
   1. **_Is there a strict deadline? Did we break anything crucial? Are we significantly blocking users?_** => [Refine the card](#Refine) right away and move to the `refined` column.
   2. **_Is there a `gain/high` and `impact/high` label? Do we need/want to finish this within ~3 months? Is this part of our current high-level plans for the quarter?_** => Move to the `priority-backlog` column.
   3. **_Is there a workaround? Doesn't the task make a user start/stop using Packit? Or, otherwise. _** => move to the `backlog` column.

### Refine

(=prepare card for work)

1. Clarification, make sure that
   1. It is clear what needs to be done and there is a definition of done.
   2. Everyone in the team understands the task to an extent of being able to work on the card themselves.
      (Suggest splitting (i.e. _breakdown_) or brainstorming, if needed.)
   3. No one has any objections to the card itself or the chosen way.
2. Vote about the time estimation (return to the previous step in case new concerns are raised).
   1. Voting is done via hands and by using a Fibonacci sequence number.
   2. If the vote is not united, discuss the reasons and the card in more detail so there is an agreement.
   3. Split the card if the team is thinking about picking `8` (=more than a week) as a time estimate.
   4. Fill the result in card details.
   5. Move the card to the `refined` column and reorder if needed.
