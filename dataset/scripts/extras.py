"""Extra turns that carry new details, not copies of the first answer."""

EXTRAS: dict[str, list[tuple[str, str]]] = {
    "harbor-pricing": [
        (
            "Walk me through a renewal they almost got wrong.",
            "Last year someone added the storage add-on into the seat price and the quote jumped without a reason. Finance split them again: forty-two dollars for the Harbor Plan seat, and nine dollars per terabyte for storage. The guest said that split has to stay visible on the order form.",
        ),
        (
            "What does a viewer cost?",
            "A viewer is free on the Harbor Plan. The moment that person edits a page, they become a seat and seat-based billing starts. The guest was firm that a shared login is not a workaround, because the audit log needs a real name on every edit.",
        ),
        (
            "Why was the United States region rejected?",
            "The host offered a United States region because it was the default. The guest refused it. The customer contract says the recordings stay in eu-central. Moving them later would be a second project, so they wanted the region right on day one.",
        ),
        (
            "What did legal change in the order form?",
            "Legal added a thirty-day notice before the Harbor Plan can auto-renew. Without that sentence, procurement would not sign. The notice is email to the buying alias, not a phone call, and it has to go out before the invoice is created.",
        ),
        (
            "How long is the named success manager included?",
            "The named success manager lasts ninety days from the kickoff, not from the signature. After ninety days the account uses the normal Harbor queue. The guest asked for the date to be printed in the statement of work so it cannot drift.",
        ),
        (
            "What export problem did the competitor have?",
            "The cheaper unlimited plan throttled exports after a few gigabytes. During the pilot, a full workspace export on Harbor finished the same afternoon. That speed, not the logo, is why they stayed. Unlimited was treated as a marketing word.",
        ),
        (
            "Did they accept the ten percent prepay discount?",
            "They did not. Procurement can approve quarterly payments only. A yearly prepay, even with ten percent off, was outside the policy. The guest asked the host not to put the discount back into the final slide.",
        ),
        (
            "What broke during the pilot?",
            "Three editors shared one login, so the audit log showed a single person doing everyone's work. Seat-based billing stops that. The guest said they would rather pay forty-two dollars and have a true log than save money and fail an audit.",
        ),
        (
            "Is the starter plan still on the table?",
            "No. The starter plan hides the audit log, and the audit log is the reason they came. The Harbor Plan is the purchase. Any later comparison should not treat the starter price as the agreed price.",
        ),
        (
            "What should I write down as the commercial fact?",
            "Write this: Harbor Plan, seat-based billing, forty-two dollars per editor each month, storage extra at nine dollars per terabyte, data in eu-central, thirty-day renewal notice, and a success manager for ninety days. Viewers stay free.",
        ),
        (
            "Who is allowed to add a seat?",
            "Only the workspace owner can add a seat. An editor cannot invite another editor. That rule was added after the pilot, because a contractor invited two people and the bill moved before finance saw it.",
        ),
        (
            "What happens if an editor leaves?",
            "A removed editor frees the seat at the next quarterly invoice, not in the middle of the month. The guest accepted that delay. They did not want mid-month credits, because the ledger team cannot post them.",
        ),
    ],
    "ledger-migration": [
        (
            "Describe the failed practice cutover.",
            "On the staging ledger they flipped the trigger before the sequence floor was copied. New invoices reused old numbers. Nothing customer-facing broke, because staging is not production. The guest still called it a failed rehearsal and put sequence floor on the blocking list.",
        ),
        (
            "What lag number allows March twelfth to proceed?",
            "Replication lag must stay under two seconds for a full business day. Logical replication into PostgreSQL is the pipe. If the lag spikes on the day before, the production cutover slips a week. A green check at noon is not enough.",
        ),
        (
            "Why not a dump and restore?",
            "A dump would freeze checkout for the length of the copy. The shop takes orders overnight. Logical replication lets the old engine keep serving while PostgreSQL catches up. That is the whole reason the method was chosen.",
        ),
        (
            "What does the old primary do after the flip?",
            "It becomes read-only for fourteen days. It is a rollback copy, not a second writer. Any write after March twelfth goes to PostgreSQL only. The host will revoke the old write role before the maintenance page comes down.",
        ),
        (
            "Why was Friday rejected?",
            "A Friday failure would sit until Monday. March twelfth is a Tuesday so the people who can roll back are in the building. The guest was the one who rejected Friday. The host had liked it because traffic is lighter.",
        ),
        (
            "Who says go?",
            "The guest says go for the production database. The host only confirms the backup snapshot finished. They do not want a committee on the call. If the guest is absent, the cutover does not start.",
        ),
        (
            "What column problem forced the engine change?",
            "The old engine locked the ledger when a column was added, and checkout froze. PostgreSQL can add the nullable column online. They are not moving for fashion. They are moving because a schema change cannot stop orders.",
        ),
        (
            "What is explicitly not the March twelfth event?",
            "The staging ledger rehearsal is not the March twelfth event. Staging already happened, and it failed on purpose around sequences. Anyone who searches for the production cutover should ignore notes that only mention the staging ledger.",
        ),
        (
            "What time does the maintenance page go up?",
            "One in the morning local time on March twelfth. The page stays up only for the production window. The guest wants the status text to say production database, so nobody thinks the staging ledger is moving again.",
        ),
        (
            "How are invoice numbers protected?",
            "The sequence floor is copied before the trigger flip. The checklist item blocks the cutover until the floor on PostgreSQL is higher than the last production invoice. Skipping it is what broke the staging ledger.",
        ),
        (
            "What would cause a one-week slip?",
            "Lag over two seconds, a missing snapshot, or the guest not on the call. Any one of those slips March twelfth by a week. A cosmetic report bug does not slip it. They separated blockers from annoyances.",
        ),
        (
            "Give me the sentence a search should find.",
            "The production cutover is March twelfth, using logical replication into PostgreSQL, with the staging ledger left behind as a rehearsal that already happened. The old primary stays read-only for fourteen days.",
        ),
    ],
    "lumen-support": [
        (
            "Separate the two clocks for me.",
            "The origin fault lasted six minutes. The banner customers saw lasted forty minutes. Ticket 4812 is about that gap. The extra thirty-four minutes were the edge cache, not a second outage. The report has to show both clocks.",
        ),
        (
            "Why did monitoring stay green?",
            "The probes hit the origin, and the origin was healthy after six minutes. They never fetched the banner from the Lisbon pop. A green probe cannot see a stale object sitting at the edge. That is why no page fired.",
        ),
        (
            "Who opened the ticket?",
            "A support agent in the Lisbon queue opened ticket 4812 after the status page was already green and the banner was still up. The agent is the start of the timeline. Monitoring is not.",
        ),
        (
            "What exactly was purged?",
            "Only the banner object. They did not restart the network and they did not purge the whole site. The guest said a wide purge would have been theater. The host agreed after seeing the cache key.",
        ),
        (
            "What config change follows the purge?",
            "Lisbon is added to the default purge list. It had been skipped by an old exception from a network test. The guest owns that change. Until it lands, a human must remember Lisbon by hand.",
        ),
        (
            "What does the closer have to do now?",
            "The closer fetches the banner from Lisbon and reads the sentence before declaring the incident over. A green origin is not the close condition. The runbook sentence is the host's task, due before Friday's review.",
        ),
        (
            "Was this a breach?",
            "No. The banner was a static sentence and no customer data moved. Calling ticket 4812 a breach would be false. The harm was telling people the service was down when it was not.",
        ),
        (
            "Which incident is easy to confuse with this one?",
            "The login incident from last month. Different ticket, different symptom, different fix. If the notes mention passwords or sign-in, they are not about ticket 4812. This review is the stale banner only.",
        ),
        (
            "Why did other cities look fine?",
            "Other cities had refreshed the banner. Lisbon kept the old object because the purge list skipped that pop. A customer in another city would have seen the true status. Geography mattered.",
        ),
        (
            "What is the one check that would have caught it?",
            "Fetch the banner from the Lisbon pop after the origin is green. If the sentence still says the service is down, the edge cache is wrong. Ticket 4812 exists because nobody did that fetch.",
        ),
        (
            "When is the follow-up due?",
            "Both the purge-list change and the runbook sentence are due before the next Friday review. The guest owns the list. The host owns the sentence. Neither is optional.",
        ),
        (
            "Close the lesson in one line.",
            "An edge cache can outlive the outage. For ticket 4812, check Lisbon before you tell customers the banner is gone.",
        ),
    ],
    "cedar-curriculum": [
        (
            "What counts as the notebook?",
            "Handwritten pages in the field notebook. Typed slides, a blog, and phone photos do not count. The instructor reads three pages every Friday during the outdoor half of the Cedar Seminar. Missing pages are not a style problem. They are an absence.",
        ),
        (
            "What did the written exam reward?",
            "It rewarded people who stayed indoors and memorized terms. The Cedar Seminar is about being outside. That is why the written exam was removed and the week nine oral defense took its place.",
        ),
        (
            "How is the eight minutes enforced?",
            "A visible clock. The student gets eight minutes to explain one page, then four minutes of questions. If they run long, they lose the questions, not the next student's slot. The guest was strict about that.",
        ),
        (
            "Can messy handwriting pass?",
            "Yes. The automatic fail is a missing field notebook, not ugly writing. A complete messy notebook can pass. An elegant empty one cannot. The host repeated that so students stop asking for a typing exception.",
        ),
        (
            "Why can't partners share a notebook?",
            "They tried it. Grading collapsed because nobody could tell who observed what. The oral defense must use pages that student wrote. The exception is closed and it will not be reopened for a medical note without a separate process.",
        ),
        (
            "What stays in the bag?",
            "Phones stay in the bag during the outdoor hour. The instructor does not grade photographs. A pencil and the field notebook are the kit. The guest said a phone photo is not an observation.",
        ),
        (
            "How is the grade split, exactly?",
            "Sixty percent field notebook, forty percent week nine oral defense. No midterm and no points for publishing a blog. The indoor methods lecture has a different split, and it should not be quoted for this seminar.",
        ),
        (
            "What is the indoor course people mix up with this?",
            "The methods lecture with the same department code. It meets inside and still has a written test. Only the Cedar Seminar has the field notebook and the week nine defense. A search that says lecture is the wrong course.",
        ),
        (
            "What does the student explain out loud?",
            "One page they wrote in the field notebook. Not a summary of the whole term, and not a partner's page. The guest said the point is to show they were present on that day, in that place.",
        ),
        (
            "When does the instructor read work?",
            "Three pages every Friday in the outdoor weeks. Week nine is the defense, not the Friday reading. Students who wait until week nine to start the notebook have already missed the Friday checks.",
        ),
        (
            "Is there any extra credit?",
            "No. A blog, a photo set, or a longer paper does not add points. The grade is the notebook and the defense. The host asked twice, and the guest declined both times.",
        ),
        (
            "Give me the fact that identifies this course.",
            "Cedar Seminar, handwritten field notebook, oral defense in week nine, phones away, sixty percent notes and forty percent defense. That combination is not the indoor lecture.",
        ),
    ],
    "north-pier": [
        (
            "What is out of scope for this meeting?",
            "The south dock. It has another budget and another drawing. This plan is North Pier only. If a question is about the south dock crane, it waits for the other team. The guest stopped the host from combining the slides.",
        ),
        (
            "How does the gate behave on an ordinary day?",
            "It stays open so boats can pass. It closes only when the tide sensor has seen the painted mark for ten minutes and the harbor master confirms the channel is clear. A splash does not close it. A person still has to agree.",
        ),
        (
            "Where is the sensor?",
            "On the outer piling at North Pier. Not on the street and not on the south dock. The guest read the location from the survey. The host had almost drawn it on the inner wall, which would have measured the wrong water.",
        ),
        (
            "What is the painted mark?",
            "One meter and twenty centimeters above the average high tide. That number came from the survey, not from a guess in the room. Three false alarms in a season force a review of that mark.",
        ),
        (
            "What scared the fishers?",
            "They feared the gate would shut and trap boats. The earlier sketch let the tide sensor close the gate alone. The new rule requires the harbor master to confirm the channel is clear first. The sensor cannot trap a boat by itself.",
        ),
        (
            "Who writes which check?",
            "The city capital budget pays for the flood gate. The harbor fee pays for tide sensor maintenance. Two checks. The public workshop should show both, or residents will think the fee is buying the concrete.",
        ),
        (
            "What is the workshop for, and what is it not?",
            "The public workshop is questions, on the first Thursday of next month, in the hall beside North Pier. It is not the construction start. Construction is the following week, and only if the workshop does not raise a safety block.",
        ),
        (
            "What is a false alarm?",
            "The gate closes and the water never reaches the street. The harbor master files a note. Three of those notes in a season reopen the tide sensor mark. A real flood is not a false alarm, even if the street stays dry for an hour.",
        ),
        (
            "What blocks the first piling?",
            "A safety issue raised at the public workshop. If the workshop is quiet, piling starts the next week. The start is not the Thursday of the workshop. The guest wants those dates on different lines of the notice.",
        ),
        (
            "Why ten minutes and not one?",
            "One minute of water on the mark can be a wake from a ferry. Ten minutes means the tide is actually there. The guest picked ten after the fishers described wakes hitting the piling. The host had proposed one minute.",
        ),
        (
            "What does the harbor master confirm?",
            "That the channel is clear of boats before the flood gate moves. The tide sensor does not see boats. It only sees water on the mark. The human confirm is the difference from the sketch people feared.",
        ),
        (
            "Summarize the North Pier decision.",
            "A flood gate at North Pier, a tide sensor on the outer piling, a painted mark one meter and twenty centimeters up, a harbor master confirm, and a public workshop on the first Thursday before any piling.",
        ),
    ],
    "kite-onboarding": [
        (
            "Which product is easy to open by mistake?",
            "The design tool with the similar icon. Kite Notes is the support tool. The curriculum does not cover the design tool. A new hire who spends day one in the design tool has not started, and the manager resets that day.",
        ),
        (
            "What may the new hire do on the shadow session?",
            "Listen. They may not speak. The shadow session is one live customer call on day two. It is not a role play. The customer is real, which is why silence is the rule. The wrong refund rule was spoken once, and that ended the experiment.",
        ),
        (
            "How is the mentor pair different?",
            "The mentor pair is a weekly meeting with an assigned coworker and no customer. It is for questions after the call. People keep merging the two. If a customer is on the line, it is the shadow session. If it is two employees, it is the mentor pair.",
        ),
        (
            "What are the three checklist lines?",
            "A finished shadow session, a written note of the customer's request, and a Kite Notes login that can view a ticket. That is the day four checklist. Miss one line and day five does not start. The note cannot say only that the customer was upset.",
        ),
        (
            "What must the note contain?",
            "One sentence naming the request, and the name of the article they would open. Vague sympathy does not pass. The guest reads the note out loud in the mentor pair and sends it back if the request is missing.",
        ),
        (
            "When may they speak to a customer?",
            "Day six, after the checklist. Day three is still practice inside the team. Speaking on day three was how a trainee quoted the wrong refund rule on a live call. That story is why the silent shadow session exists.",
        ),
        (
            "What permission is enough on day four?",
            "View permission in Kite Notes. Edit permission waits until day six. Edit access on day four let a trainee close a ticket by mistake. The host will not grant edit early, even if the mentor asks.",
        ),
        (
            "How is a mentor chosen?",
            "They volunteer for a month and they must have passed the same checklist last quarter. The new hire does not pick a friend. The mentor pair is assigned. A volunteer who skipped the checklist last quarter is not eligible.",
        ),
        (
            "What happens if a step is skipped?",
            "The manager resets the week. There is no partial credit for a charming trainee. Shadow session, mentor pair, day four checklist, first spoken call on day six. The sequence is the curriculum.",
        ),
        (
            "What is the failure everyone should remember?",
            "The wrong refund rule, said out loud to a real customer. It was not a design-tool story and it was not a mentor-pair story. It happened because someone spoke during what should have been a silent shadow session.",
        ),
        (
            "Can the article name be skipped if the note is kind?",
            "No. Kindness without the request and the article fails the day four checklist. The guest said kindness is not a ticket. The host agreed to stop accepting those notes.",
        ),
        (
            "State the sequence a search should retrieve.",
            "Kite Notes onboarding: silent shadow session on day two, assigned mentor pair during the week, day four checklist, view-only access until day six, first spoken customer call on day six.",
        ),
    ],
}
