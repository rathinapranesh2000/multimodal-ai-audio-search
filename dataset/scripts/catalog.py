"""Original two-speaker interviews for the golden set.

These scripts are the audio source. They are not ground-truth labels.
Search indexes only the Whisper transcript after diarization and redaction.
"""

from __future__ import annotations

INTERVIEWS = [
    {
        "slug": "harbor-pricing",
        "title": "Harbor plan pricing interview",
        "voices": ["en-US-GuyNeural", "en-US-JennyNeural"],
        "anchors": [
            {
                "phrase": "Harbor Plan",
                "category": "exact",
                "query": "What did they say about the Harbor Plan?",
            },
            {
                "phrase": "seat-based billing",
                "category": "semantic",
                "query": "How is the subscription price calculated for each person?",
            },
            {
                "phrase": "forty-two dollars",
                "category": "exact",
                "query": "What price did the guest quote per seat?",
            },
            {
                "phrase": "eu-central",
                "category": "speaker",
                "query": "What did Speaker 01 say about the deployment region?",
            },
        ],
        "pairs": [
            (
                "Thanks for sitting down. What plan did your team actually buy?",
                "We bought the Harbor Plan after the pilot. It is the only plan that includes the audit log and the shared workspace. The starter plan was cheaper, but it hid the audit log.",
            ),
            (
                "How does the bill grow when you add people?",
                "Harbor uses seat-based billing. Every active editor is one seat. Viewers are free. We refused the usage meter because finance could not predict it.",
            ),
            (
                "What number should I remember for the renewal?",
                "The quote on the table was forty-two dollars per editor each month, billed annually. That figure is only for the Harbor Plan, not for the storage add-on.",
            ),
            (
                "Where will the production workspace live?",
                "The guest asked for eu-central. The host had offered a United States region first. The guest said the customer contract requires the recording data to stay in eu-central.",
            ),
            (
                "Did storage change the price?",
                "Storage is a separate add-on at nine dollars per terabyte. It is not part of the forty-two dollar seat. We almost mixed those two numbers in the slide, and finance caught it.",
            ),
            (
                "What worried the buyer about the contract?",
                "The buyer was worried about auto-renewal. They wanted a thirty-day notice before the Harbor Plan renewed. Legal wrote that notice into the order form.",
            ),
            (
                "How did the pilot influence the decision?",
                "During the pilot, three editors shared one login. That broke the audit log. Seat-based billing forces a real login per editor, which is why they accepted the higher price.",
            ),
            (
                "Was there a discount?",
                "They were offered a ten percent discount if they paid the whole year up front. They declined it because procurement can only approve quarterly payments.",
            ),
            (
                "What did they say about competitors?",
                "A competitor offered a cheaper unlimited plan. The guest said unlimited was a trap because exports were throttled. They stayed with Harbor because the export stayed fast.",
            ),
            (
                "Any last condition before signature?",
                "The last condition was a named success manager for the first ninety days. After that, the account falls back to the normal Harbor queue. That condition is written in the statement of work.",
            ),
        ],
    },
    {
        "slug": "ledger-migration",
        "title": "Ledger database migration",
        "voices": ["en-US-AndrewNeural", "en-US-AriaNeural"],
        "anchors": [
            {
                "phrase": "logical replication",
                "category": "semantic",
                "query": "How are they copying the database without a long outage?",
            },
            {
                "phrase": "March twelfth",
                "category": "exact",
                "query": "When is the production cutover?",
            },
            {
                "phrase": "staging ledger",
                "category": "hard_negative",
                "query": "What did they decide about the production database cutover?",
            },
            {
                "phrase": "PostgreSQL",
                "category": "cross_file",
                "query": "Which recording explains the database migration, not just a region name?",
            },
        ],
        "pairs": [
            (
                "Give me the shape of the migration in one pass.",
                "We are leaving the old ledger and moving the books to PostgreSQL. The method is logical replication, not a dump and restore. A dump would have meant a long outage, and the shop cannot stop taking orders.",
            ),
            (
                "When does production move?",
                "The production cutover is March twelfth, starting at one in the morning local time. That is the production database, not the practice copy. The maintenance page goes up only for that window.",
            ),
            (
                "What is the staging ledger for, then?",
                "The staging ledger is a rehearsal. We already failed a practice cutover there on purpose. Staging is not the system customers write to. Please do not describe staging as the March twelfth event.",
            ),
            (
                "Why PostgreSQL instead of staying put?",
                "The old engine could not add a column without a lock that froze checkout. PostgreSQL lets us add the nullable column online. That single limitation drove the choice.",
            ),
            (
                "How do you know replication is healthy?",
                "We watch replication lag. If lag stays under two seconds for a full business day, the cutover is allowed. If lag spikes, March twelfth slips by a week.",
            ),
            (
                "Who signs the go decision?",
                "The guest owns the go decision for the production database. The host only confirms that the backup snapshot finished. One person must say go, so the call is not a committee.",
            ),
            (
                "What happens to the old primary after cutover?",
                "The old primary becomes read-only for fourteen days. It is a rollback path, not a second place to write. Writes after March twelfth go only to PostgreSQL.",
            ),
            (
                "Did anyone suggest a different night?",
                "Someone suggested a Friday. The guest rejected Friday because a failed cutover would sit all weekend. March twelfth is a Tuesday so the on-call team is in the building.",
            ),
            (
                "How are sequences handled?",
                "Sequences are copied before the trigger flip. Missing that step would reuse invoice numbers. The checklist item is literally called sequence floor, and it blocks the cutover.",
            ),
            (
                "What should a searcher not confuse?",
                "People keep mixing the staging ledger with the production cutover. Staging already happened. The production move is March twelfth and uses logical replication into PostgreSQL.",
            ),
        ],
    },
    {
        "slug": "lumen-support",
        "title": "Lumen support outage review",
        "voices": ["en-GB-RyanNeural", "en-GB-SoniaNeural"],
        "anchors": [
            {
                "phrase": "ticket 4812",
                "category": "exact",
                "query": "What happened in ticket 4812?",
            },
            {
                "phrase": "edge cache",
                "category": "semantic",
                "query": "Why were customers seeing a stale message?",
            },
            {
                "phrase": "Lisbon",
                "category": "speaker",
                "query": "What did Speaker 01 say about the Lisbon site?",
            },
        ],
        "pairs": [
            (
                "Which ticket are we reviewing?",
                "This review is ticket 4812. It is the banner incident, not the login incident from last month. If a note says login, it is the wrong ticket.",
            ),
            (
                "What did customers actually see?",
                "Customers saw a stale banner that said the service was down, even after the repair. The origin was healthy. The edge cache kept the old banner for forty minutes.",
            ),
            (
                "Where did the bad cache live?",
                "The stale banner was served from the Lisbon pop. Other cities had already refreshed. Lisbon kept the old object because the purge list skipped that site.",
            ),
            (
                "How long was the user impact?",
                "The origin fault lasted six minutes. The visible banner lasted forty minutes because of the edge cache. Those are two different clocks, and the report must keep them apart.",
            ),
            (
                "What was the fix?",
                "The fix was a targeted purge of the banner object, then a config change so Lisbon is on the default purge list. We did not restart the whole network.",
            ),
            (
                "Who noticed it first?",
                "A support agent in the Lisbon queue noticed the banner still showing after the status page went green. That agent opened ticket 4812. Monitoring did not page, because the origin probes were green.",
            ),
            (
                "What will we change in the runbook?",
                "The runbook now says to purge the edge cache before declaring the incident over. A green origin is not enough. The closer must fetch the banner from Lisbon and read it.",
            ),
            (
                "Was any customer data exposed?",
                "No customer data was exposed. The banner was a static sentence. The embarrassment was accuracy, not a leak. Please do not describe ticket 4812 as a breach.",
            ),
            (
                "What is the follow-up owner?",
                "The guest owns the purge-list change. The host owns the runbook sentence. Both must be done before the next Friday review.",
            ),
            (
                "Give me the one-line lesson.",
                "The lesson from ticket 4812 is that an edge cache can outlive the outage. Check Lisbon, not only the origin, before you tell customers the banner is gone.",
            ),
        ],
    },
    {
        "slug": "cedar-curriculum",
        "title": "Cedar seminar curriculum",
        "voices": ["en-US-ChristopherNeural", "en-US-AvaNeural"],
        "anchors": [
            {
                "phrase": "field notebook",
                "category": "semantic",
                "query": "What do students have to write during the outdoor weeks?",
            },
            {
                "phrase": "week nine",
                "category": "exact",
                "query": "When is the oral defense?",
            },
            {
                "phrase": "Cedar Seminar",
                "category": "cross_file",
                "query": "Which class requires an oral defense in week nine?",
            },
        ],
        "pairs": [
            (
                "What course are we redesigning?",
                "We are redesigning the Cedar Seminar. It is a field course, not the indoor lecture with the same department code. The seminar meets outside for half the term.",
            ),
            (
                "What do students produce each week outdoors?",
                "Each outdoor week they add pages to a field notebook. The notebook is handwritten. Typed slides do not count. The instructor reads three pages every Friday.",
            ),
            (
                "When is the oral defense?",
                "The oral defense is in week nine. Students explain one page from the field notebook out loud. Week nine is not the written exam. The written exam was removed.",
            ),
            (
                "Why drop the written exam?",
                "The written exam rewarded people who stayed indoors and memorized terms. The Cedar Seminar is about observation. The oral defense checks that they were actually outside.",
            ),
            (
                "How long is the defense?",
                "Each defense is eight minutes, plus four minutes of questions. The clock is visible. A defense that runs long loses the question time, not the next student's slot.",
            ),
            (
                "What is an automatic fail?",
                "A missing field notebook is an automatic fail. A messy notebook can still pass. The rule is about presence of the notes, not about handwriting.",
            ),
            (
                "Can a student defend a partner's notes?",
                "No. The oral defense must use pages that student wrote. Sharing a notebook was tried once and it collapsed the grading. That exception is closed.",
            ),
            (
                "What equipment is required?",
                "Students bring a pencil and the field notebook. Phones stay in the bag during the outdoor hour. The instructor does not grade photographs.",
            ),
            (
                "How is the grade split?",
                "Sixty percent is the field notebook and forty percent is the week nine oral defense. There is no midterm. Publishing a blog does not add points.",
            ),
            (
                "What should a later search not mix up?",
                "Do not mix the Cedar Seminar with the indoor methods lecture. Only the seminar has the field notebook and the week nine oral defense.",
            ),
        ],
    },
    {
        "slug": "north-pier",
        "title": "North Pier flood workshop",
        "voices": ["en-AU-WilliamNeural", "en-AU-NatashaNeural"],
        "anchors": [
            {
                "phrase": "tide sensor",
                "category": "semantic",
                "query": "What device tells them when the water is rising?",
            },
            {
                "phrase": "public workshop",
                "category": "exact",
                "query": "When is the public workshop about the flood gate?",
            },
            {
                "phrase": "North Pier",
                "category": "cross_file",
                "query": "Where is the flood gate being discussed?",
            },
        ],
        "pairs": [
            (
                "Which site is this plan for?",
                "This plan is only for North Pier. The south dock is a different project with a different budget. If someone says south dock, they are in the wrong meeting.",
            ),
            (
                "What structure is being added?",
                "We are adding a flood gate at the mouth of North Pier. It stays open for boats on ordinary days and closes when the tide sensor crosses the mark.",
            ),
            (
                "How does the sensor decide?",
                "The tide sensor sits on the outer piling. When water reaches the painted mark for ten minutes, the gate is allowed to close. A single splash does not count.",
            ),
            (
                "When can residents ask questions?",
                "The public workshop is on the first Thursday of next month, in the hall beside North Pier. That workshop is for questions. It is not the construction start.",
            ),
            (
                "What did people fear last time?",
                "Last time, fishers feared the gate would trap boats. The design now closes only after a harbor master confirms the channel is clear. The tide sensor alone cannot trap a boat.",
            ),
            (
                "Who pays for the gate?",
                "The city capital budget pays for the gate. The sensor maintenance is paid from the harbor fee. Those are two checks, and the workshop should not blur them.",
            ),
            (
                "Is the painted mark already chosen?",
                "The painted mark is one meter and twenty centimeters above the average high tide. The guest read that number from the survey. It is not a guess from the host.",
            ),
            (
                "What happens in a false alarm?",
                "If the gate closes and the water never reaches the street, the harbor master files a false-alarm note. Three false alarms in a season force a review of the tide sensor mark.",
            ),
            (
                "When does construction start?",
                "Construction starts the week after the public workshop, if the workshop does not surface a safety block. The start is not the same day as the workshop.",
            ),
            (
                "Summarize the decision.",
                "North Pier gets a flood gate controlled by a tide sensor, with a human confirm before the gate shuts. Residents hear the plan at the public workshop before any piling is driven.",
            ),
        ],
    },
    {
        "slug": "kite-onboarding",
        "title": "Kite Notes onboarding",
        "voices": ["en-US-EricNeural", "en-US-MichelleNeural"],
        "anchors": [
            {
                "phrase": "shadow session",
                "category": "semantic",
                "query": "How do new hires watch a real customer call?",
            },
            {
                "phrase": "day four checklist",
                "category": "exact",
                "query": "What has to be true on the day four checklist?",
            },
            {
                "phrase": "mentor pair",
                "category": "hard_negative",
                "query": "What is the shadow session for, as opposed to the mentor pair?",
            },
        ],
        "pairs": [
            (
                "What product is this onboarding for?",
                "This onboarding is for Kite Notes. It is the support tool, not the design tool with a similar icon. New hires who open the design tool are in the wrong curriculum.",
            ),
            (
                "How do they hear a real customer?",
                "On day two they join a shadow session. They listen to one live call and may not speak. The shadow session is observation. It is not a practice call with a teammate.",
            ),
            (
                "What is the mentor pair, then?",
                "The mentor pair is a weekly meeting with a named coworker. It is for questions after the call. People confuse it with the shadow session. The shadow session has a customer. The mentor pair does not.",
            ),
            (
                "What does day four require?",
                "The day four checklist requires three things: a finished shadow session, a written note of the customer's request, and a login to Kite Notes that can view a ticket. Missing one item blocks day five.",
            ),
            (
                "Can they take a call on day three?",
                "No. Day three is still practice inside the team. The first live speaking role is day six, after the checklist. Speaking early was tried and the customer heard a wrong refund rule.",
            ),
            (
                "What note do they have to write?",
                "The note must name the customer's request in one sentence and name the article they would open. A vague note such as customer was upset does not pass the day four checklist.",
            ),
            (
                "How are mentors chosen?",
                "Mentors volunteer for a month. A new hire does not pick a friend. The mentor pair is assigned, and the mentor must have passed the same checklist last quarter.",
            ),
            (
                "What tool permission is enough?",
                "View permission in Kite Notes is enough for day four. Edit permission waits until day six. Giving edit early let a trainee close a ticket by mistake.",
            ),
            (
                "What is the failure we keep citing?",
                "The failure we cite is the wrong refund rule on a live call. That is why the shadow session is silent and why the day four checklist exists. It is not a story about the design tool.",
            ),
            (
                "Close with the sequence.",
                "Sequence for Kite Notes: shadow session on day two, mentor pair during the week, day four checklist, first spoken call on day six. Skip a step and the manager resets the week.",
            ),
        ],
    },
]


def _with_extras(interviews: list[dict]) -> list[dict]:
    from dataset.scripts.extras import EXTRAS

    for interview in interviews:
        interview["pairs"] = [*interview["pairs"], *EXTRAS[interview["slug"]]]
    return interviews


INTERVIEWS = _with_extras(INTERVIEWS)
