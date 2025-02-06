# Meetings

Our team meetings are organised similarly each week. We have [Standup](#standup) meetings on Monday, Tuesday and Thursday morning and all the other team meetings happen on Thursdays to make our team schedule compact.

:::tip

As part of our role-rotation practice, all the regular weekly meetings are facilitated by the Kanban Lead](./roles#kanban-lead) of the week.

:::

## Standups

We have standups 3 times a week (Mondays, Tuesdays and Thursdays) to talk about what we have been working on, issues we are facing and what we are planning to work on next. Reserve the other 2 days for focus time.

1. Each standup, we start with checking the new cards in our [Kanban board](./kanban#packit-kanban-board). On Mondays, we also go through the blocked cards, cards that haven't had any progress for a while to see if any action can be taken and cards approaching their due-date.
2. To avoid stale issues, we also discuss one of the least recently updated issues from the backlog and check if it's still relevant.
3. We follow with the statuses -- everyone quickly shares what they were working on recently, what are working on and planning to do next. Also if there are any issues or blockers found on the way. This should be a monologue to make the most of the time. Any topic requiring more discussion is left to be discussed elsewhere (separate discussion/meeting or [architecture meeting](#architecture)) or discussed at the end of the standup.
4. For each standup, we have a standup question defined to engage a bit. Everyone answers the question after providing a status. It can be any warm-up question or short activity. Sometimes, it's just for fun, sometimes it allows us to show our current mood or energy level. This also makes us know others more, building a stronger team together.
5. So-called post-standup topics are discussed. To not disturb statuses, any announcement or topic requiring a small discussion/response is left to the end of the meeting.

## Architecture

To not make [Standup](#standup) meetings too long, we've separated the longer discussions into a weekly organised meeting. As the name suggests, the main goal of this meeting is to discuss technical or architectural topics but there is a place to discuss anything. The topics are collected beforehand in a shared document.
For relevant topics (public, open for community input), one can create a discussion thread at [GitHub Discussions](https://github.com/packit/packit/discussions/categories/architecture) and link it in the document. Alternatively, anyone can add a [`discuss` label](./kanban#discuss) to an issue.

[Kanban Lead](./roles#kanban-lead) facilitates the discussion and shows a 5-minute timer for each topic (can be reset if everyone agrees to continue with a discussion). [Kanban Lead](./roles#kanban-lead) is also responsible for note-taking and making a clear conclusion from the discussion including the clear action items. Anyone is welcome to help with the notes since sometimes it's hard to facilitate discussion and make notes at the same time.

Meetings are a safe space. There are no dumb ideas or stupid questions - anyone can ask if they don’t understand something.

:::tip

If there is a strong decision needed, let people provide feedback also offline (either before or after the meeting). Some people might prefer written communication and/or asynchronous communication. Allow them to participate, so the best decision is chosen.

:::

## Refinement meeting

Weekly meetings to prepare our next cards to work on. This is not to **_plan_** the work for the next week as done in Scrum. Kanban is based on a stream of cards going through [the board columns](./kanban#card-states-board-columns). This activity is about moving the card from the top of the backlog (a [priority one](./kanban#priority-backlog) in our case) into the [_refined_ column](./kanban#refined) by following [our refinement process](./kanban#refine).
Basically it's about making sure the task is clearly defined and understood by the team members so they can be taken by anyone to start the real work.

The discussion starts with a quick introduction of the card (done by a [Kanban Lead](./roles#kanban-lead) or a person the most familiar with the task). The card is being updated and the discussion continues until we agree it's clear and can be done in 5 days or less -- to help ourselves reach this agreement, there is a voting going on. We used to do a thumbs-up/down for the following questions:

1. Is this card clear?
2. Is this doable in 5 days or less?

Since there wasn't much disagreement and discussion, we switched to Scrum-like voting by hand about [story points](./kanban#story-points). (A [difference in story points](./kanban#story-point-scale) helps us better find a difference in the understanding.) We collect the story points but it's not the main reason why we do the voting. Be respectful when asking people why they've chosen a different story point number. It's to help everyone with the understanding and also to share the possible risks, not to put someone on the spot!

At the end of the meeting, make sure the order (=priority) of the cards in the _refined_ column is right and respects our priorities as shown on the [epic board](https://github.com/orgs/packit/projects/7/views/29), but also considers any urgent tasks (e.g. maintenance like renewing certificates).

## Retrospectives

Bi-weekly meetings to get a sense of how everyone feels. This is a safe space -- feel free to share anything openly and also be open to listening to others.

Miro board is created by the [Kanban Lead](./roles#kanban-lead) leading the Retrospective at the beginning of the week (ideally Monday morning) to provide time for adding notes to the board in advance.
There's a default Miro board template prepared, but any activity or board can be used to make it more interesting.

Action items from the previous retro board should be included to be discussed and checked.

At the end of the meeting, we revisit our [epics](https://github.com/orgs/packit/projects/7/views/29) and how we are standing on our planned epics for the quarter.
