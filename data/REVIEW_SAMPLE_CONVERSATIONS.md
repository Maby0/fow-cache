# Conversation label review sample (20 pairs)

For each pair: would ONE reply be correct for the final user message of both conversations?

## 1. conv-retail-003 (context_swap, short) label: DIFFERENT

Note: One is moving a restaurant table to 8pm; the other means swapping to an 8pm performance, a different action with different fees and availability.

**A (cached)**

1. user: Hiya, we've got a table for 4 at Olivetto on Friday at 7pm.
2. assistant: Lovely, I can see that booking. Anything you'd like to change?
3. user: can I change it to 8?

**B (new)**

1. user: Hiya, I've got two tickets for the Saturday matinee of Paper Lanterns at the Gaiety.
2. assistant: Lovely, I can see those tickets. Anything you'd like to change?
3. user: Can I change it to 8?

## 2. conv-billing-005 (context_swap, medium) label: DIFFERENT

Note: Adding a partner means a Tunely Duo music plan in one and an IronWorks Couples gym membership (with a club transfer) in the other.

**A (cached)**

1. user: Hi, quick question about my Tunely account
2. assistant: Hi! Happy to help, what would you like to know?
3. user: I'm on the Individual plan, £11.99. Is there a way to share with others?
4. assistant: Yes, the Duo plan covers two people for £15.99 and the Family plan covers up to six for £18.99.
5. user: my partner lives with me, does that matter?
6. assistant: For Duo and Family, everyone needs to live at the same address, so that works fine.
7. user: ok can I add my partner to it?

**B (new)**

1. user: Hi, question about my IronWorks membership
2. assistant: Hi! What can I help with?
3. user: I'm on the Solo membership at £34 a month. Do you do anything for couples?
4. assistant: We do, the Couples membership is £58 a month for two people at the same home club.
5. user: my partner's already a member at a different branch, does that matter?
6. assistant: They'd need to switch their home club to match yours, but their existing membership can be converted.
7. user: ok can I add my partner to it?

## 3. conv-retail-010 (context_swap, long) label: DIFFERENT

Note: A Flex flight fare is refundable minus a fee; the festival ticket is non-refundable (resale only), so the yes/no flips.

**A (cached)**

1. user: hello I booked flights to Malaga with you, Flex fare, going 12 June
2. assistant: Hi! I can see your return flights to Malaga on the Flex fare, outbound 12 June. How can I help?
3. user: can I pick seats now or only at check-in
4. assistant: On Flex, seat selection is included, so you can choose seats now in Manage Booking.
5. user: nice. how much hold luggage do I get
6. assistant: Flex includes one 23kg hold bag per person.
7. user: and my golf clubs?
8. assistant: Golf bags count as sports equipment: £45 each way, up to 20kg.
9. user: ok might leave them. when does check in open
10. assistant: Online check-in opens 30 days before departure and closes 2 hours before.
11. user: my work might send me to a conference that week though
12. assistant: Ah, fingers crossed it works out!
13. user: is it refundable?

**B (new)**

1. user: hi i bought a weekend camping ticket for Brightwater Festival in July
2. assistant: Hi! Yes, I can see your weekend camping ticket for Brightwater, 18-20 July. What can I help with?
3. user: when do the gates open
4. assistant: Campsite gates open at 10am on Friday 18th.
5. user: can I bring a gas stove
6. assistant: Small camping stoves are fine in the general campsite but not in the arena.
7. user: is there a cash machine on site
8. assistant: There are a couple, but the site is mostly cashless, so bring a card.
9. user: and can my cousin who's 15 come
10. assistant: Under-16s need their own child ticket and must be with an adult over 18.
11. user: my work might send me to a conference that week though
12. assistant: Ah, fingers crossed it works out!
13. user: is it refundable?

## 4. conv-retail-011 (detail_swap, short) label: DIFFERENT

Note: One order is already out for delivery (address can't be changed), the other is still being packed (it can).

**A (cached)**

1. user: Hi, can you check order 70452 for me? I need to change something
2. assistant: Sure. Order 70452 is out for delivery today with Parcelnet.
3. user: can i still change the address?

**B (new)**

1. user: Hi, can you check order 70425 for me? I need to change something
2. assistant: Sure. Order 70425 is still being packed at our warehouse.
3. user: can i still change the address?

## 5. conv-retail-017 (detail_swap, medium) label: DIFFERENT

Note: The Friday late show is 18+ (adult material) while the Saturday matinee is all ages, so the yes/no flips.

**A (cached)**

1. user: Hi I'm looking at tickets for Marvo the Magnificent at the Regent, the Friday late show
2. assistant: Hi! The Friday 9:30pm show still has seats from £22.
3. user: what's it like, is it a proper magic show
4. assistant: Yes, close-up magic, mind-reading and a bit of comedy, about 90 minutes.
5. user: sounds fun, any good seats in the circle?
6. assistant: There are a few together in row C of the circle.
7. user: can I bring my 12 year old?

**B (new)**

1. user: Hi I'm looking at tickets for Marvo the Magnificent at the Regent, the Saturday matinee
2. assistant: Hi! The Saturday 2:30pm show still has seats from £22.
3. user: what's it like, is it a proper magic show
4. assistant: Yes, close-up magic, mind-reading and a bit of comedy, about 90 minutes.
5. user: sounds fun, any good seats in the circle?
6. assistant: There are a few together in row C of the circle.
7. user: can I bring my 12 year old?

## 6. conv-billing-020 (detail_swap, long) label: DIFFERENT

Note: A 7-year-old dog can get Lifetime cover; a 9-year-old is past the 8th-birthday cutoff and only gets Senior cover.

**A (cached)**

1. user: Hi, I've got a Covera pet policy for my cat Mabli and I've just adopted a dog
2. assistant: Congratulations! What breed and age is the dog?
3. user: he's a 7 year old springer spaniel called Rolo
4. assistant: Lovely. Just so you know, new Lifetime policies can start for dogs up to their 8th birthday. After that we offer Senior cover instead.
5. user: ok. her premium went up a lot this year btw
6. assistant: Premiums for cats often rise as they age. Mabli's on Lifetime £4,000, which renews in June.
7. user: fair enough. do you cover dental?
8. assistant: Dental is covered for accidents only, not routine cleaning or gum disease.
9. user: ok. does having two pets get me a discount?
10. assistant: Yes, there's a 10% multi-pet discount on each policy.
11. user: nice. does Rolo need a vet check first?
12. assistant: No vet check is needed, but any condition he's had in the last 2 years would be excluded.
13. user: ok, can I add him to my policy?

**B (new)**

1. user: Hi, I've got a Covera pet policy for my cat Mabli and I've just adopted a dog
2. assistant: Congratulations! What breed and age is the dog?
3. user: he's a 9 year old springer spaniel called Rolo
4. assistant: Lovely. Just so you know, new Lifetime policies can start for dogs up to their 8th birthday. After that we offer Senior cover instead.
5. user: ok. her premium went up a lot this year btw
6. assistant: Premiums for cats often rise as they age. Mabli's on Lifetime £4,000, which renews in June.
7. user: fair enough. do you cover dental?
8. assistant: Dental is covered for accidents only, not routine cleaning or gum disease.
9. user: ok. does having two pets get me a discount?
10. assistant: Yes, there's a 10% multi-pet discount on each policy.
11. user: nice. does Rolo need a vet check first?
12. assistant: No vet check is needed, but any condition he's had in the last 2 years would be excluded.
13. user: ok, can I add him to my policy?

## 7. conv-long-billing-006 (detail_swap, very_long) label: DIFFERENT

Note: 'Freeze it' targets the Mastercard credit card ending 3829 in A but the Visa debit card ending 6150 in B; each later says the other card is safe.

**A (cached)**

1. user: hi I think I've lost my fernhill credit card, the mastercard. had it at the pub last night and now can't find it
2. assistant: Sorry to hear that. I can see two cards on your profile: the Fernhill Mastercard credit card ending 3829 and the Visa debit card ending 6150. Your Fernhill Mastercard credit card ending 3829's last transaction was £23.40 at The Wheatsheaf at 21:47 last night, and there's been nothing since. I can freeze the credit card while you look for it and unfreeze it instantly if it turns up. Would you like me to?
3. user: hang on, I want to ring the pub first and I've got some other questions
4. assistant: No problem. There's no suspicious activity, so take your time and just tell me when you want it frozen.
5. user: what's the difference between freezing and cancelling
6. assistant: Freezing is temporary: it blocks new card payments and cash withdrawals, but the card stays valid, so if you find it you can unfreeze it in seconds. Cancelling stops the card permanently and we send a replacement with a new number, which takes 3-5 working days. If you think it's just misplaced, freezing is usually the better first step.
7. user: will my direct debits still go out if its frozen
8. assistant: Yes. Direct debits and standing orders come from the account rather than the card, so they're unaffected. Some regular card payments like subscriptions may be declined while a card is frozen, so it's best not to leave it frozen for weeks.
9. user: and apple pay?
10. assistant: Apple Pay uses the same card behind the scenes, so it stops working for that card while it's frozen. Your other card on Apple Pay would work as normal.
11. user: ok that's fine. the pub doesn't open til 12 so I'll ring then
12. assistant: Sounds like a plan. Pubs usually keep lost cards behind the bar for a few days before shredding them.
13. user: unrelated but my credit card statement says minimum payment £25 but I owe like £600, should I just pay the minimum
14. assistant: You can, but it's not the cheapest way. Your credit card's purchase rate is 24.9% APR, so if you only pay £25 a month most of it goes on interest. Paying the full statement balance by the due date means no interest on purchases at all.
15. user: how long would it take on the minimum
16. assistant: On a £600 balance at 24.9%, paying only the minimum would take roughly three years and cost around £230 in interest, assuming no new spending. Paying £60 a month would clear it in under a year with about £70 of interest.
17. user: ok that's grim. I'll do more than the minimum
18. assistant: Good call. You can set up a direct debit for a fixed amount or the full balance in the app under Credit card > Repayments.
19. user: can you do the full balance one
20. assistant: Done. From your next statement, the full statement balance will be collected by direct debit on the due date, the 17th, so you won't pay purchase interest.
21. user: my debit card is definitely fine btw, it's in my phone case, it's just the mastercard thats gone
22. assistant: Good, the debit card stays exactly as it is then.
23. user: also my contactless limit seems low, it declined at tesco for £110
24. assistant: The UK contactless limit is £100 per transaction, so anything over that needs chip and PIN, or Apple Pay, which has no fixed limit where the shop accepts it. It's set nationally rather than by us. You can lower your own limit in the app if you'd like it stricter.
25. user: oh it was just over then
26. assistant: Yes, by £10. It's a common one.
27. user: while you're here, can I get my credit limit put up? it's £1500
28. assistant: You're eligible to request an increase in the app under Credit card > Credit limit. It's a soft search that won't affect your credit score, and the decision is usually instant. We'd never increase it without asking you first.
29. user: I'll wait until I've paid this off probably
30. assistant: That's sensible. Keeping the balance low compared with your limit can help your credit score a little too.
31. user: is there a fee if I use the credit card abroad
32. assistant: The Fernhill Mastercard has a 2.99% non-sterling fee on purchases abroad, and cash withdrawals cost 3% plus interest from the day you take the cash. For cash, the debit card is usually cheaper.
33. user: ok good to know, off to Krakow in november
34. assistant: Lovely. If you're offered the choice, paying in złoty rather than pounds usually gets you a better rate.
35. user: oh the pub just texted back, they haven't got it
36. assistant: Sorry, that's annoying. It may still turn up at home or in a coat pocket, which is very common. Freezing it now means it's safe either way.
37. user: if I find it in a few days I can just unfreeze it yeah
38. assistant: Exactly. Tap 'Unfreeze' in the app and it works again straight away. If it hasn't turned up after a week or so, we'd recommend cancelling and ordering a replacement.
39. user: fine. thanks for being so patient
40. assistant: No problem at all.
41. user: ok freeze it

**B (new)**

1. user: hi I think I've lost my fernhill debit card, the visa one. had it at the pub last night and now can't find it
2. assistant: Sorry to hear that. I can see two cards on your profile: the Fernhill Mastercard credit card ending 3829 and the Visa debit card ending 6150. Your Visa debit card ending 6150's last transaction was £23.40 at The Wheatsheaf at 21:47 last night, and there's been nothing since. I can freeze the debit card while you look for it and unfreeze it instantly if it turns up. Would you like me to?
3. user: hang on, I want to ring the pub first and I've got some other questions
4. assistant: No problem. There's no suspicious activity, so take your time and just tell me when you want it frozen.
5. user: what's the difference between freezing and cancelling
6. assistant: Freezing is temporary: it blocks new card payments and cash withdrawals, but the card stays valid, so if you find it you can unfreeze it in seconds. Cancelling stops the card permanently and we send a replacement with a new number, which takes 3-5 working days. If you think it's just misplaced, freezing is usually the better first step.
7. user: will my direct debits still go out if its frozen
8. assistant: Yes. Direct debits and standing orders come from the account rather than the card, so they're unaffected. Some regular card payments like subscriptions may be declined while a card is frozen, so it's best not to leave it frozen for weeks.
9. user: and apple pay?
10. assistant: Apple Pay uses the same card behind the scenes, so it stops working for that card while it's frozen. Your other card on Apple Pay would work as normal.
11. user: ok that's fine. the pub doesn't open til 12 so I'll ring then
12. assistant: Sounds like a plan. Pubs usually keep lost cards behind the bar for a few days before shredding them.
13. user: unrelated but my credit card statement says minimum payment £25 but I owe like £600, should I just pay the minimum
14. assistant: You can, but it's not the cheapest way. Your credit card's purchase rate is 24.9% APR, so if you only pay £25 a month most of it goes on interest. Paying the full statement balance by the due date means no interest on purchases at all.
15. user: how long would it take on the minimum
16. assistant: On a £600 balance at 24.9%, paying only the minimum would take roughly three years and cost around £230 in interest, assuming no new spending. Paying £60 a month would clear it in under a year with about £70 of interest.
17. user: ok that's grim. I'll do more than the minimum
18. assistant: Good call. You can set up a direct debit for a fixed amount or the full balance in the app under Credit card > Repayments.
19. user: can you do the full balance one
20. assistant: Done. From your next statement, the full statement balance will be collected by direct debit on the due date, the 17th, so you won't pay purchase interest.
21. user: the credit card's fine btw, I keep that one at home in a drawer, it's just the visa thats gone
22. assistant: Good, the credit card stays exactly as it is then.
23. user: also my contactless limit seems low, it declined at tesco for £110
24. assistant: The UK contactless limit is £100 per transaction, so anything over that needs chip and PIN, or Apple Pay, which has no fixed limit where the shop accepts it. It's set nationally rather than by us. You can lower your own limit in the app if you'd like it stricter.
25. user: oh it was just over then
26. assistant: Yes, by £10. It's a common one.
27. user: while you're here, can I get my credit limit put up? it's £1500
28. assistant: You're eligible to request an increase in the app under Credit card > Credit limit. It's a soft search that won't affect your credit score, and the decision is usually instant. We'd never increase it without asking you first.
29. user: I'll wait until I've paid this off probably
30. assistant: That's sensible. Keeping the balance low compared with your limit can help your credit score a little too.
31. user: is there a fee if I use the credit card abroad
32. assistant: The Fernhill Mastercard has a 2.99% non-sterling fee on purchases abroad, and cash withdrawals cost 3% plus interest from the day you take the cash. For cash, the debit card is usually cheaper.
33. user: ok good to know, off to Krakow in november
34. assistant: Lovely. If you're offered the choice, paying in złoty rather than pounds usually gets you a better rate.
35. user: oh the pub just texted back, they haven't got it
36. assistant: Sorry, that's annoying. It may still turn up at home or in a coat pocket, which is very common. Freezing it now means it's safe either way.
37. user: if I find it in a few days I can just unfreeze it yeah
38. assistant: Exactly. Tap 'Unfreeze' in the app and it works again straight away. If it hasn't turned up after a week or so, we'd recommend cancelling and ordering a replacement.
39. user: fine. thanks for being so patient
40. assistant: No problem at all.
41. user: ok freeze it

## 8. conv-retail-023 (intent_flip, short) label: DIFFERENT

Note: 'The second one' books 9pm in one chat and 8:15pm in the other.

**A (cached)**

1. user: Have you got a table for two at Saffron Lane this Saturday?
2. assistant: Yes, I have 7pm or 9pm available. Which would you prefer?
3. user: the second one

**B (new)**

1. user: Have you got a table for two at Saffron Lane this Saturday?
2. assistant: Yes, I have 6:30pm or 8:15pm available. Which would you prefer?
3. user: the second one

## 9. conv-billing-024 (intent_flip, medium) label: DIFFERENT

Note: 'Yes do that' confirms a 2-month freeze in one and a medical cancellation in the other.

**A (cached)**

1. user: I've broken my ankle so can't use the gym for a while
2. assistant: Sorry to hear that! I hope it heals quickly.
3. user: thanks. I'm with PulseFit on the £32 plan
4. assistant: Thanks. Do you know roughly how long you'll be out?
5. user: doctor says about 8 weeks
6. assistant: In that case I can freeze your membership for 2 months at £5 a month, with no notice needed. Shall I set that up?
7. user: yes do that

**B (new)**

1. user: I've broken my ankle so can't use the gym for a while
2. assistant: Sorry to hear that! I hope it heals quickly.
3. user: thanks. I'm with PulseFit on the £32 plan
4. assistant: Thanks. Do you know roughly how long you'll be out?
5. user: doctor says about 8 weeks
6. assistant: As you're in your first 3 months, you can cancel on medical grounds with a doctor's note and no notice period. Shall I start that?
7. user: yes do that

## 10. conv-services-030 (intent_flip, long) label: DIFFERENT

Note: 'yes' confirms 10 instalments of £187.20 in A but 12 instalments of £156 in B.

**A (cached)**

1. user: I've just moved into Marsh Vale and set up council tax, account 40177258
2. assistant: Thanks, I've found your account. Your annual bill is £1,872, payable in 10 monthly instalments from November to August.
3. user: can i pay by direct debit
4. assistant: Yes. Direct debits can be taken on the 1st, 15th or 28th of the month.
5. user: do I get a single person discount, it's just me
6. assistant: Yes, if you're the only adult living there you get 25% off. That's already been applied to the bill I quoted.
7. user: oh nice. and when do bin collections start for new addresses
8. assistant: Your property's already on the round, so collections continue as normal.
9. user: great. ten payments is a lot each month though
10. assistant: You can choose to spread the bill over 12 months instead, which lowers each instalment.
11. user: ok. I get paid on the 28th
12. assistant: Thanks. Shall I set up the direct debit on the 28th, keeping the 10 instalments?
13. user: yes

**B (new)**

1. user: I've just moved into Marsh Vale and set up council tax, account 40177258
2. assistant: Thanks, I've found your account. Your annual bill is £1,872, payable in 10 monthly instalments from November to August.
3. user: can i pay by direct debit
4. assistant: Yes. Direct debits can be taken on the 1st, 15th or 28th of the month.
5. user: do I get a single person discount, it's just me
6. assistant: Yes, if you're the only adult living there you get 25% off. That's already been applied to the bill I quoted.
7. user: oh nice. and when do bin collections start for new addresses
8. assistant: Your property's already on the round, so collections continue as normal.
9. user: great. ten payments is a lot each month though
10. assistant: You can choose to spread the bill over 12 months instead, which lowers each instalment.
11. user: ok. I get paid on the 28th
12. assistant: Thanks. Shall I set up the direct debit on the 28th and spread it over 12 instalments instead of 10?
13. user: yes

## 11. conv-services-033 (same_context_reworded, short) label: SAME

Note: Same fault at the same address; the reporting steps are the same.

**A (cached)**

1. user: The streetlight outside 22 Beech Grove has been out for a week
2. assistant: Thanks for letting us know. Street lighting faults in Marsh Vale can be reported to us directly.
3. user: how do I report it?

**B (new)**

1. user: Hi, there's a broken streetlight outside my house, 22 Beech Grove, it's been off for about a week
2. assistant: Thanks. You can report street lighting faults to Marsh Vale council directly.
3. user: How do I report it?

## 12. conv-billing-037 (same_context_reworded, medium) label: SAME

Note: Same facts (comprehensive, 15cm crack needs replacing, £75 replacement excess) in a different order; the answer is £75 in both.

**A (cached)**

1. user: a stone cracked my windscreen on the motorway
2. assistant: Sorry to hear that. Do you have comprehensive cover with Shieldwell?
3. user: yes comprehensive
4. assistant: Good, windscreen cover is included, with a £75 excess for a replacement or £0 for a repair.
5. user: the crack is about 15cm long
6. assistant: That's too long to repair, so it'll need replacing.
7. user: so what will I pay?

**B (new)**

1. user: I've got comprehensive with Shieldwell and a stone has cracked my windscreen, about 15cm
2. assistant: Sorry about that. A 15cm crack is too long to repair, so it'll need replacing.
3. user: is windscreen covered?
4. assistant: Yes, glass cover is included on comprehensive. Repairs have no excess, replacements have a £75 excess.
5. user: right
6. assistant: Would you like help booking it in?
7. user: What will I pay?

## 13. conv-services-039 (same_context_reworded, long) label: SAME

Note: Same address, same valid permit, same replacement EV; the vehicle change steps are identical.

**A (cached)**

1. user: Hi, I've got a residents parking permit for 40 Hartfield Street and I've just changed my car
2. assistant: Thanks. Is the new car replacing the old one, or will you have both?
3. user: replacing, sold the old one last week
4. assistant: Okay. Your existing permit can be transferred to the new vehicle rather than buying a new one.
5. user: is there a charge
6. assistant: There's no charge to change the vehicle on a permit, as long as the permit is still valid.
7. user: it runs till march
8. assistant: Great, then it's still valid.
9. user: the new car's electric if that matters
10. assistant: Thanks. Electric vehicles get a discount when you next renew, but it doesn't affect the change itself.
11. user: ok good to know
12. assistant: Is there anything else you'd like to know?
13. user: how do I change the car on it?

**B (new)**

1. user: I sold my old car and bought an electric one. I have a resident permit for Hartfield Street, number 40
2. assistant: Thanks for letting us know. Is your permit still in date?
3. user: yeah valid till march
4. assistant: Great. You don't need a new permit, you can transfer the existing one to the new car.
5. user: does that cost anything
6. assistant: No, changing the vehicle on a valid permit is free.
7. user: and the electric thing?
8. assistant: Electric vehicles get a discounted price at renewal, but there's no change to your current permit.
9. user: ok so I just swap it over
10. assistant: That's right, the new car replaces the old one on the permit.
11. user: cool
12. assistant: Anything else I can help with?
13. user: how do I change the car on the permit?

## 14. conv-long-services-013 (same_context_reworded, very_long) label: SAME

Note: Same facts in different wording and order: bank details changed on 14 Oct, verified within 2 working days, October cut-off the 18th, payday the 28th; so yes, October pay goes to the new account in both. Side chat differs and never moves those dates.

**A (cached)**

1. user: hi, I've switched banks and just updated my bank details in the HR system. will my pay go to the new account?
2. assistant: Hi, thanks for updating them. I can see the change was submitted today, 14 October. Bank detail changes are checked by the payroll team within 2 working days, as a fraud precaution.
3. user: and when's the deadline for this months payroll?
4. assistant: The cut-off for October payroll is 18 October, and payday is 28 October. Any change that's been checked and approved before the cut-off applies to that month's pay.
5. user: ok. my old account is closing at the end of the month btw
6. assistant: Thanks, that's useful to know. If a payment ever goes to a closed account, the bank returns it to us and we reissue it, but that can take a few days, so it's best avoided.
7. user: ok. also how quickly do expense claims get paid? I did some mileage
8. assistant: Expense claims approved by your manager in time for the monthly payroll are paid with that month's salary. Mileage is reimbursed at 45p a mile for the first 10,000 business miles in the tax year, then 25p.
9. user: my manager hasnt approved it yet, its been a week
10. assistant: It's showing as awaiting approval with Tom Bellamy. I can send him an automatic reminder from the system if you like?
11. user: yes please
12. assistant: Done, he'll get a reminder email now.
13. user: when do the payslips go up online?
14. assistant: Payslips are published in the HR system 3 working days before payday.
15. user: also why is there a student loan deduction on mine? I thought I'd paid it off
16. assistant: We deduct student loan repayments based on instructions from HMRC. When you've finished repaying, the Student Loans Company tells HMRC, who send us a stop notice, and that can lag a bit. If you think you've overpaid, contact the Student Loans Company directly, as they handle refunds.
17. user: I'll check my account with them
18. assistant: Good idea. Once we get a stop notice from HMRC, the deductions end from the next pay run.
19. user: where do i find my pension statement
20. assistant: Your annual pension statement comes from the pension provider, Aldgate Life, rather than from us. You can log in to their member portal with your National Insurance number to see your balance and contributions any time.
21. user: never logged in, didnt know it existed
22. assistant: Lots of people don't! It's worth a look, and you can also say who should receive it if anything happens to you.
23. user: oh yeah, I should do that
24. assistant: It's under "Nominate beneficiaries" on their portal.
25. user: can I give to charity through payroll?
26. assistant: Yes, through Payroll Giving. Donations come out of your gross pay before tax, so it costs you less than giving the same amount directly. Sign up in the HR system under Benefits > Payroll Giving.
27. user: nice. I lost my P45 from my last job, does that matter?
28. assistant: Not now. We used it, or the starter checklist, to set up your tax code when you joined. HMRC updates your code directly, so you don't need the old P45 any more.
29. user: ok good. random, are we getting a pay rise this year?
30. assistant: I can't share anything about the pay review until it's announced. Pay reviews are usually communicated in March and take effect in April.
31. user: worth a try lol
32. assistant: Ha, of course!
33. user: the canteen card top up, does that come out of wages?
34. assistant: No, the canteen card is topped up separately by card at the kiosk. It isn't linked to payroll.
35. user: is there a way to get paid weekly instead of monthly
36. assistant: Salaried staff at Halden are paid monthly only, I'm afraid. Weekly pay is just for hourly-paid site staff.
37. user: ok. back to the bank thing
38. assistant: Sure.
39. user: will i get a text or anything to say its done?
40. assistant: Yes, you'll get an email once the new details are verified and active.
41. user: ok cool, so will october's pay go into the new account then?

**B (new)**

1. user: Hello. Quick one: my October pay day is the 28th right, and what's the cut-off for changes?
2. assistant: Hello. Yes, payday is 28 October, and the cut-off for any changes to October payroll is the 18th.
3. user: ok. I updated my bank account details in the system this morning because I've moved banks, my old account shuts end of October
4. assistant: Thanks. I can see the update submitted today, 14 October. For security, payroll verifies new bank details within 2 working days before they go live, and anything approved before the cut-off is used for that month's pay.
5. user: why do you verify them?
6. assistant: It's to protect against payment diversion fraud, where someone tries to change an employee's bank details to steal their pay. We check the change was made by you, usually with a text code or a quick call.
7. user: makes sense. random question, what's the overtime rate on weekends?
8. assistant: For eligible staff, Saturday overtime is paid at time and a half and Sunday at double time. It needs to be pre-approved by your manager.
9. user: does it all go in the same month
10. assistant: It's paid in the month it's approved, as long as it's approved in time for that month's payroll.
11. user: ok. I've heard about an electric car scheme?
12. assistant: Yes, the EV salary sacrifice scheme. You lease an electric car through payroll, before tax and National Insurance, which can save a lot compared with leasing privately. The lease includes insurance and maintenance, and there's a calculator in the HR system under Benefits.
13. user: what if I leave the company
14. assistant: If you leave during the lease there can be an early termination charge, though the scheme includes some protection, for example for redundancy. The details are in the scheme guide before you sign up.
15. user: ok i'll read it properly first
16. assistant: Definitely worth it.
17. user: will my christmas bonus be taxed loads?
18. assistant: Bonuses are taxed like your normal pay, through PAYE, so they're added to that month's earnings. If the bonus pushes you into a higher band for that month you may see more tax taken, but it usually evens out across the year.
19. user: ugh ok
20. assistant: I know, it's never quite as much as you hope after tax!
21. user: i'm getting married next spring, how do I change my surname on payroll?
22. assistant: Congratulations! Update your name in the HR system under Personal details and upload a copy of your marriage certificate. Payroll updates it for the next pay run, and you'll need to tell HMRC as well.
23. user: what's the employee assistance thing? someone mentioned it
24. assistant: The Employee Assistance Programme is a free, confidential service for staff and their families. It offers 24/7 phone support, counselling sessions, and help with money, legal or work worries. The number's on the intranet homepage, and we never find out who's used it.
25. user: good to know, wedding planning is stressful
26. assistant: I can imagine! They do financial guidance too, which might be handy.
27. user: haha yes
28. assistant: Anything else I can help with?
29. user: does sick pay get paid the same way
30. assistant: Yes, company sick pay and statutory sick pay are both paid through payroll with your normal salary.
31. user: and holiday pay?
32. assistant: Same, holiday is just paid as normal salary while you're off.
33. user: lovely
34. assistant: Good stuff.
35. user: oh and can I still see my old payslips from before I changed banks
36. assistant: Yes, all your previous payslips stay in the HR system under Pay > Payslips, whichever account they were paid into.
37. user: just the bank details really
38. assistant: Of course.
39. user: will someone actually call me?
40. assistant: It'll usually be a text with a code, but sometimes a call from the payroll team. Either way it'll come from a number listed on the intranet.
41. user: ok, so will this month's pay go into my new account?

## 15. conv-retail-042 (irrelevant_history, short) label: SAME

Note: Check-in time is fixed hotel policy, unaffected by earlier chat about EV charging or the spa.

**A (cached)**

1. user: Have you got EV chargers at the Larkfield Hotel?
2. assistant: Yes, two 7kW chargers in the car park, free for guests.
3. user: What time is check-in at the Larkfield?

**B (new)**

1. user: can I book a massage in the Larkfield spa?
2. assistant: Yes, treatments can be booked through reception or on our website.
3. user: What time is check-in at the Larkfield?

## 16. conv-services-046 (irrelevant_history, medium) label: SAME

Note: Hollybank's prescription delivery service is a standalone chain-wide question.

**A (cached)**

1. user: Hi, do you have hand sanitiser in stock?
2. assistant: Yes, all Hollybank branches stock hand sanitiser in 50ml and 500ml bottles.
3. user: great what about the big pump ones
4. assistant: The 500ml pump bottles are usually by the tills.
5. user: cheers
6. assistant: You're welcome.
7. user: Do you do a prescription delivery service?

**B (new)**

1. user: Is the Harbour Street branch open on bank holidays?
2. assistant: Harbour Street opens 10am to 4pm on most bank holidays, but closes on Christmas Day and Boxing Day.
3. user: and Mill Lane?
4. assistant: Mill Lane is closed on all bank holidays.
5. user: ok thanks
6. assistant: No problem.
7. user: Do you do a prescription delivery service?

## 17. conv-services-050 (irrelevant_history, long) label: SAME

Note: The monthly payroll cut-off is a fixed company fact; promotion or P60 chat doesn't change it.

**A (cached)**

1. user: Hi, I've just been promoted, when does the new salary kick in
2. assistant: Congratulations! Salary changes take effect from the date on your change letter.
3. user: letter says 1st november
4. assistant: Then your November pay will be at the new salary.
5. user: will my pension contributions go up too
6. assistant: Yes, contributions are a percentage of salary, so they'll increase automatically.
7. user: ok. and my car allowance?
8. assistant: Car allowance is set by grade, so if your new role is a different grade it may change too. Your change letter will say.
9. user: it says it stays the same
10. assistant: Then that stays as it is.
11. user: cool thanks
12. assistant: You're welcome, and well done.
13. user: What's the payroll cut-off date each month?

**B (new)**

1. user: How do I get a copy of last year's P60?
2. assistant: You can download it from the HR portal under Pay > Documents.
3. user: found it. can I also see old payslips
4. assistant: Yes, payslips from the last six years are in the same section.
5. user: great. also I want to pay more into my pension
6. assistant: You can increase your contribution in the portal under Pay > Pension.
7. user: does it come out before tax
8. assistant: Yes, our pension scheme uses salary sacrifice, so contributions are taken before tax and National Insurance.
9. user: nice. what's the max
10. assistant: You can sacrifice salary as long as your pay stays above the National Minimum Wage.
11. user: ok fair
12. assistant: Anything else?
13. user: not really. oh actually
14. assistant: Go ahead.
15. user: What's the payroll cut-off date each month?

## 18. conv-retail-053 (same_context_extra_chatter, short) label: SAME

Note: Same booking and occasion; the side question about the lamb doesn't change the cakeage policy answer.

**A (cached)**

1. user: We've booked a table at Little Bramble for Saturday, it's my husband's 40th.
2. assistant: Lovely, happy early birthday to him! What can I help with?
3. user: Can we bring our own cake?

**B (new)**

1. user: We've booked a table at Little Bramble for Saturday, it's my husband's 40th. We came for our anniversary last year and the lamb was incredible, is it still on?
2. assistant: Thank you! Yes, the lamb's still on the menu. What else can I help with?
3. user: can we bring our own cake?

## 19. conv-retail-056 (same_context_extra_chatter, medium) label: SAME

Note: Same card reference and address; the Tesco chat doesn't change the redelivery/collection options.

**A (cached)**

1. user: I've got a missed delivery card from Parcelnet, they came while I was out
2. assistant: Sorry you missed them. Do you have the card reference?
3. user: yes PN-CARD-7731
4. assistant: Thanks. Is the address on the card correct?
5. user: yes
6. assistant: Good, that makes it simple.
7. user: what are my options?

**B (new)**

1. user: I've got a missed delivery card from Parcelnet, ugh I literally popped to Tesco for ten minutes
2. assistant: Typical timing, sorry! Do you have the card reference?
3. user: yes PN-CARD-7731, address on it is right
4. assistant: Thanks. Did you get your shopping done at least?
5. user: ha yes, ran out of milk
6. assistant: Always the way!
7. user: What are my options?

## 20. conv-services-058 (same_context_extra_chatter, long) label: SAME

Note: Same Gmail forwarding setup; B adds praise, a widget-colour side question and small talk.

**A (cached)**

1. user: Hi, we want our support@ emails to land in Brightdesk as tickets
2. assistant: You can do that by forwarding your support address to your Brightdesk inbound address. Which email provider do you use?
3. user: Google Workspace
4. assistant: Great. In Gmail settings for support@, add a forwarding address and paste in your Brightdesk inbound address.
5. user: where do I find the inbound address
6. assistant: It's under Admin > Channels > Email, and looks like yourcompany@inbound.brightdesk.io.
7. user: ok got it. will replies come from support@ or the brightdesk one
8. assistant: Replies will come from support@ once you verify the domain under Admin > Channels > Email > Sender.
9. user: how do i verify
10. assistant: Add the SPF and DKIM records shown there to your DNS.
11. user: ok our IT guy can do that
12. assistant: Perfect.
13. user: Gmail is asking me for a confirmation code for the forwarding, where do I find that?

**B (new)**

1. user: Hey! We just switched to Brightdesk from our old helpdesk, loving it so far honestly. We want our support@ emails to land in Brightdesk as tickets
2. assistant: Glad you're enjoying it! You can do that by forwarding your support address to your Brightdesk inbound address. Which email provider do you use?
3. user: Google Workspace
4. assistant: Great. In Gmail settings for support@, add a forwarding address and paste in your Brightdesk inbound address.
5. user: where do I find the inbound address
6. assistant: It's under Admin > Channels > Email, and looks like yourcompany@inbound.brightdesk.io.
7. user: ok got it. side note, is there a way to change the colour of the chat widget? marketing are being picky
8. assistant: Yes, you can change the widget colour under Admin > Widget > Appearance.
9. user: great. will replies come from support@ or the brightdesk one
10. assistant: Replies will come from support@ once you verify the domain under Admin > Channels > Email > Sender.
11. user: how do i verify
12. assistant: Add the SPF and DKIM records shown there to your DNS.
13. user: ok our IT guy can do that, he's off today though, typical
14. assistant: Ha, always the way!
15. user: Gmail is asking me for a confirmation code for the forwarding, where do I find that?
