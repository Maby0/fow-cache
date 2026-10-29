// The two scripted demos: every message, reply and (illustrative) Jev score. Prices and
// thresholds are fow-cache's own.
const PRICE = { turn: 0.0056, facts: 0.00023, candidate: 0.000842 };
const WHOLE_T = 0.70, RW_T = 0.15, PLAIN_T = 0.90;

const SCENARIOS = {
  "demo-1": {
    bot: "MyGym · support bot",
    intro: "<b>Two people, one question.</b> User 1 asks first, so the answer is generated and stored. User 2 asks the same thing in different words: the embedding search finds User 1's entry, Jev confirms the answer fits, and User 2 gets it without a model call.",
    turns: [
      { id: "a1", side: "L", user: "How much is a membership?",
        reply: "A standard membership is £34.99 a month on a rolling contract, or £29.99 a month if you sign up for 12 months. Both include every class, the pool and the sauna, and there's no joining fee this month.",
        llmSec: 4.6 },
      { id: "a2", side: "R", user: "what does it cost to join the gym?",
        cand: "a1", sim: 0.83, whole: 0.96, rw: 0.94, guardSec: 1.2,
        rewrites: ["How much does a MyGym membership cost?", "How much does it cost to join MyGym?"],
        note: "A paraphrase. A plain cache at 0.90 similarity would have missed it and paid for a full call." }
    ]
  },
  "demo-2": {
    bot: "MyGym · support bot",
    intro: "<b>Two members cancelling the same membership, one detail apart:</b> User 1 paid for a 12-month contract upfront, User 2 is on a rolling monthly one. Every message is looked up. Some cached answers fit both chats, some don't, and the last message is identical in both.",
    turns: [
      { id: "b1", side: "L", user: "Hi, I want to cancel my MyGym membership.",
        reply: "Sorry to see you go. Are you on a rolling monthly membership or a 12-month contract?", llmSec: 3.1 },
      { id: "b2", side: "R", user: "how do I cancel my gym membership?",
        cand: "b1", sim: 0.91, whole: 0.95, rw: 0.97, guardSec: 1.1,
        rewrites: ["How do I cancel my MyGym membership?", "How do I cancel my MyGym membership?"],
        note: "Different wording, same request. Nothing earlier in either chat changes the answer." },
      { id: "b3", side: "L", user: "12-month contract, paid upfront.",
        reply: "Thanks. Upfront 12-month memberships are refunded for the unused months, so you'd get £149.95 back for the 5 months left. Shall I cancel it now?", llmSec: 4.2 },
      { id: "b4", side: "R", user: "Rolling monthly, paid by direct debit.",
        cand: "b3", sim: 0.80, whole: 0.09, guardSec: 0.4,
        reply: "Thanks. Rolling memberships need one month's notice, so your last payment is on 1 December and you can use the gym until 31 December. Shall I cancel it now?", llmSec: 4.4,
        note: "Different contract. User 1's answer promises a £149.95 refund User 2 isn't owed." },
      { id: "b5", side: "L", user: "Before I do, what happens to my booked classes?",
        reply: "Any classes booked after your membership ends are cancelled automatically, and you'll get an email for each one. Bookings before then stay as they are.", llmSec: 3.8 },
      { id: "b6", side: "R", user: "wait, will my class bookings get cancelled?",
        cand: "b5", sim: 0.88, whole: 0.86, rw: 0.95, guardSec: 1.3,
        rewrites: ["What happens to my booked MyGym classes if I cancel?", "Will my MyGym class bookings be cancelled if I cancel?"],
        note: "The contracts differ, but this answer doesn't depend on them, so it is safe to reuse. A plain cache missed this one (0.88)." },
      { id: "b7", side: "L", user: "OK, yes, cancel it.",
        reply: "Done. Your 12-month membership is cancelled and £149.95 will be refunded to your card within 5 to 7 working days.", llmSec: 3.5 },
      { id: "b8", side: "R", user: "OK, yes, cancel it.",
        cand: "b7", sim: 1.00, whole: 0.76, rw: 0.02, guardSec: 1.4,
        rewrites: ["Cancel my MyGym 12-month contract now.", "Cancel my MyGym rolling monthly membership now."],
        reply: "Done. Your membership is cancelled. Your last direct debit is on 1 December and you can use the gym until 31 December.", llmSec: 3.6,
        ghost: "That refund belongs to User 1's 12-month contract. User 2 is on a rolling membership and is owed nothing.",
        note: "The hard case: identical final messages, and the whole-conversation check passed. Rewriting each side into a standalone request exposes the difference." }
    ]
  }
};
