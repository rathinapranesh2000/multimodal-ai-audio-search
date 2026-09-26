# Candidate review

Hybrid + rerank top 5 over the full ready corpus.
These rows are search candidates for manual labeling. They are not ground truth.

## 1. What did they discuss about hybrid search?

- type: keyword
- file_hint: AI_Engineering_Mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 111.8 | 142.1 | 0.000 | Right. So also, so a lot of more additional components like well, hybrid search, then a re rank, that's a proper rank fusion, then re ranking capabilities. These were added also on top of that. So back when I was scrolling on LinkedIn five… |
| 2 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 174.2 | 205.9 | 0.000 | So yeah, I'm [REDACTED_NAME] on that. But yeah, so there are like since it's a multi -agent orchestration system. So they're like specialized agents for like reading the code, writing the code, generating patches, writing tests and then cr… |
| 3 | llm_systems_interview.wav | SPEAKER_01 | 244.4 | 260.3 | 0.000 | you think this is a pivotal moment? Like out of all the versions of GPT 50 years from now, when they look back on an early system that was really kind of a leap, you know, in a Wikipedia page about the history of artificial intelligence, w… |
| 4 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 299.6 | 323.5 | 0.000 | going to be going through public documents I'm [REDACTED_NAME] blogs and I'm [REDACTED_NAME] YouTube videos wikipedia pages any useful sources of information highly ranked sources of information which have opted in maybe or at least not op… |
| 5 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 79.4 | 111.8 | 0.000 | So like I made this a rag system, which is and for like specific, a product policy related documents on like the regulated documents, compliance documents, because they have a lot of structural elements like labels, headings, and these thi… |

## 2. What metrics did they mention for evaluating retrieval systems?

- type: paraphrase
- file_hint: AI_Engineering_Mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 111.8 | 142.1 | 0.028 | Right. So also, so a lot of more additional components like well, hybrid search, then a re rank, that's a proper rank fusion, then re ranking capabilities. These were added also on top of that. So back when I was scrolling on LinkedIn five… |
| 2 | llm_systems_interview.wav | SPEAKER_01 | 244.4 | 260.3 | 0.001 | you think this is a pivotal moment? Like out of all the versions of GPT 50 years from now, when they look back on an early system that was really kind of a leap, you know, in a Wikipedia page about the history of artificial intelligence, w… |
| 3 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 79.4 | 111.8 | 0.000 | So like I made this a rag system, which is and for like specific, a product policy related documents on like the regulated documents, compliance documents, because they have a lot of structural elements like labels, headings, and these thi… |
| 4 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 299.6 | 323.5 | 0.000 | going to be going through public documents I'm [REDACTED_NAME] blogs and I'm [REDACTED_NAME] YouTube videos wikipedia pages any useful sources of information highly ranked sources of information which have opted in maybe or at least not op… |
| 5 | llm_systems_interview.wav | SPEAKER_00 | 309.1 | 342.3 | 0.000 | more delicious? So we train these models on a lot of text data. And in that process, they learn the underlying something about the underlying representations of what's in here or in there. And they can do amazing things. But when you first… |

## 3. Why can AI coding agents fail in production?

- type: keyword
- file_hint: AI_Engineering_Mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 286.7 | 314.7 | 0.343 | So even if like user was like, let's say the runs failed, they had to be like restarted from again and again. So these are some points. Maybe the elements that we're using as agents, maybe they are not being able to like the inference is n… |
| 2 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 214.1 | 254.0 | 0.029 | That's awesome. Actually, these are very good projects because it's not easy to solve them completely and even good organizations are currently taking up these kind of projects. So I have one question on this. Right. For example, you have… |
| 3 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 254.7 | 286.7 | 0.008 | I think the first one that comes to my mind instantly is that maybe it could not bear the load, not the number of request actors meant for. The second could be there is a thing called context degradation in agents. So like the kind of like… |
| 4 | llm_systems_interview.wav | SPEAKER_01 | 32.6 | 64.2 | 0.003 | We stand on the precipice of fundamental societal transformation where soon nobody knows when, but many including me believe it's within our lifetime. The collective intelligence of the human species begins to pale in comparison by many or… |
| 5 | llm_systems_interview.wav | SPEAKER_00 | 265.2 | 274.0 | 0.003 | It's not like we could say here was the moment where AI went from not happening to happening. And I'd have a very hard time like pinpointing |

## 4. What are the main reasons an agent-based system might fail?

- type: paraphrase
- file_hint: AI_Engineering_Mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 286.7 | 314.7 | 0.585 | So even if like user was like, let's say the runs failed, they had to be like restarted from again and again. So these are some points. Maybe the elements that we're using as agents, maybe they are not being able to like the inference is n… |
| 2 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 254.7 | 286.7 | 0.003 | I think the first one that comes to my mind instantly is that maybe it could not bear the load, not the number of request actors meant for. The second could be there is a thing called context degradation in agents. So like the kind of like… |
| 3 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 214.1 | 254.0 | 0.001 | That's awesome. Actually, these are very good projects because it's not easy to solve them completely and even good organizations are currently taking up these kind of projects. So I have one question on this. Right. For example, you have… |
| 4 | llm_systems_interview.wav | SPEAKER_00 | 390.4 | 399.7 | 0.001 | Maybe just because it's much easier to use, it's much easier to get what you want. You get it right more often the first time and ease of use matters a lot, even if the base capability was there before. |
| 5 | llm_systems_interview.wav | SPEAKER_01 | 127.5 | 158.3 | 0.000 | About distributed economic systems that incentivize the safety and human alignment of this power. About the psychology of the engineers and leaders that deploy AGI. And about the history of human nature. Our capacity for good and evil at s… |

## 5. What did they discuss about the electrical power plan?

- type: keyword
- file_hint: Behavioral_mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | llm_systems_interview.wav | SPEAKER_01 | 95.9 | 127.5 | 0.368 | Orwell's 1984 or the pleasure -fueled mass hysteria of brave new world where, as well as the new technology that undo their capacities to think. That is why these conversations with the leaders, engineers and philosophers, both optimists a… |
| 2 | llm_systems_interview.wav | SPEAKER_01 | 127.5 | 158.3 | 0.263 | About distributed economic systems that incentivize the safety and human alignment of this power. About the psychology of the engineers and leaders that deploy AGI. And about the history of human nature. Our capacity for good and evil at s… |
| 3 | llm_systems_interview.wav | SPEAKER_00 | 277.2 | 298.0 | 0.001 | Well, the history books write about GPT one or two or three or four or seven. That's for them to decide. I don't really know. I think if I had to pick some moment from what we've seen so far, I'd sort of pick chat GPT. You know, it wasn't… |
| 4 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 141.2 | 155.0 | 0.001 | one other thing is do we want this to be as real time as we possibly can or is it absolutely real time or is it fine for the last time this chat what was updated was 2023 or 2022 the models that we are choosing |
| 5 | llm_systems_interview.wav | SPEAKER_01 | 64.2 | 95.9 | 0.000 | know and don't yet know that will empower humans to create, to flourish, to escape the widespread poverty and suffering that exist in the world today and to succeed in that old all -too -human pursuit of happiness. It is terrifying because… |

## 6. How did the candidate demonstrate leadership skills?

- type: speaker_specific
- file_hint: Behavioral_mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Behavioral_mock_Interview.wav | SPEAKER_01 | 109.7 | 118.2 | 0.010 | Okay, so could you dive a little bit more into that first one? Your ability to persuade people, maybe tell me about a time you were able to convince someone to change their mind? |
| 2 | Behavioral_mock_Interview.wav | SPEAKER_01 | 170.1 | 178.2 | 0.001 | Okay, great. So now we'll dive into that second strength you had mentioned. Could you tell me about a time that you demonstrated strong leadership skills? |
| 3 | llm_systems_interview.wav | SPEAKER_01 | 158.3 | 191.8 | 0.001 | Including Sam Altman, Greg Brockman, Ilya Setskever, Wojciech Zaremba, Andre Karpathy, Jakob Pachaki and many others. It means the world that Sam has been totally open with me. Willing to have multiple conversations including challenging o… |
| 4 | Behavioral_mock_Interview.wav | SPEAKER_01 | 95.3 | 101.5 | 0.000 | Awesome, thank you for sharing that. So next, could you tell me about like one or two of your key strengths? |
| 5 | Behavioral_mock_Interview.wav | SPEAKER_00 | 102.4 | 109.4 | 0.000 | So I would say the biggest two would probably be my ability to persuade people and then the second would be leadership. I would say those are the biggest two. |

## 7. How did the candidate handle a difficult or challenging situation?

- type: paraphrase
- file_hint: Behavioral_mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Behavioral_mock_Interview.wav | SPEAKER_01 | 46.1 | 55.1 | 0.013 | Okay, awesome. That's good to know. So now we'll dive into a little bit more behavioral questions. So could you tell me about a time where you solved a difficult problem? |
| 2 | llm_systems_interview.wav | SPEAKER_01 | 158.3 | 191.8 | 0.002 | Including Sam Altman, Greg Brockman, Ilya Setskever, Wojciech Zaremba, Andre Karpathy, Jakob Pachaki and many others. It means the world that Sam has been totally open with me. Willing to have multiple conversations including challenging o… |
| 3 | Behavioral_mock_Interview.wav | SPEAKER_01 | 109.7 | 118.2 | 0.001 | Okay, so could you dive a little bit more into that first one? Your ability to persuade people, maybe tell me about a time you were able to convince someone to change their mind? |
| 4 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 231.3 | 246.9 | 0.000 | okay so retrainings are very rare we might not need to look into it and finally when I'm [REDACTED_NAME] what do we need to do to get the responses are we also looking at how the chatbot has to clean the responses has to make sure nothing… |
| 5 | Behavioral_mock_Interview.wav | SPEAKER_01 | 317.3 | 360.8 | 0.000 | Great. So I think Zia did an amazing job with that interview. There are four main things that I think he did really well. First, he was very poised and confident throughout the entire interview. We were going back and forth. And I was aski… |

## 8. What were the candidate's biggest career goals?

- type: speaker_specific
- file_hint: Behavioral_mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Behavioral_mock_Interview.wav | SPEAKER_00 | 102.4 | 109.4 | 0.054 | So I would say the biggest two would probably be my ability to persuade people and then the second would be leadership. I would say those are the biggest two. |
| 2 | llm_systems_interview.wav | SPEAKER_01 | 158.3 | 191.8 | 0.009 | Including Sam Altman, Greg Brockman, Ilya Setskever, Wojciech Zaremba, Andre Karpathy, Jakob Pachaki and many others. It means the world that Sam has been totally open with me. Willing to have multiple conversations including challenging o… |
| 3 | Behavioral_mock_Interview.wav | SPEAKER_00 | 235.0 | 273.0 | 0.001 | Yeah, I'd say the biggest one is probably my ability to prioritize when there's a lot of conflicting and computing priorities. The big one in that case would be when say there's three or four different projects and all of them are high urg… |
| 4 | llm_systems_interview.wav | SPEAKER_01 | 191.8 | 222.5 | 0.000 | Always with the goal of trying to help in my small way. If I fail, I will work hard to improve. I love you all. This is [REDACTED_NAME] Friedman podcast. To support it, please check out our sponsors in the description. And now, dear friend… |
| 5 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 22.6 | 47.8 | 0.000 | on. So yeah, that would be great. Awesome. So I was looking at your resume. OK, so I find few of interesting projects which you have already did. Right. For example, there is Infra, there is Auto PR and other things as well. Can you briefl… |

## 9. What coding problem involving a string and an array was discussed?

- type: keyword
- file_hint: Google_Coding_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Google_Coding_Interview.wav | SPEAKER_00 | 0.0 | 29.3 | 0.217 | a coding problem and you're going to have about 20 to 30 minutes to solve it. Most importantly, I want to hear how your thought process is throughout this and whether you get the solution or not just communicate effectively throughout this… |
| 2 | Google_Coding_Interview.wav | SPEAKER_00 | 29.3 | 61.1 | 0.006 | A subsequence of a string is a new string generated from the original string with some characters can be none deleted without changing the relative order of the remaining characters. For example, ace is a subsequence of a b c d e. So one e… |
| 3 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 353.8 | 391.0 | 0.003 | It's more about how you are thinking. So I'm [REDACTED_NAME] paste the problem in your chat box. Okay. Let me know once you get this. And first do explain to me what the question is about. Okay. And then if you are comfortable, open any in… |
| 4 | Google_Coding_Interview.wav | SPEAKER_01 | 248.7 | 250.6 | 0.003 | s equal strings and |
| 5 | Google_Coding_Interview.wav | SPEAKER_00 | 61.1 | 74.2 | 0.002 | b b as you can tell cannot be a subsequence of the string. Let me know if you have any questions about this or if you can understand example two as well. So what are your first thoughts? |

## 10. What did they say about lowercase strings and empty strings?

- type: keyword
- file_hint: Google_Coding_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Google_Coding_Interview.wav | SPEAKER_00 | 150.2 | 160.3 | 0.107 | You can assume you'll have proper only lower case English letters it could potentially be an empty string but otherwise they're all gonna be normal. |
| 2 | Google_Coding_Interview.wav | SPEAKER_01 | 161.2 | 163.9 | 0.023 | Okay an empty string would result in a zero. |
| 3 | Google_Coding_Interview.wav | SPEAKER_00 | 130.4 | 133.3 | 0.002 | You can assume lower case only that's a good question. |
| 4 | Google_Coding_Interview.wav | SPEAKER_01 | 119.2 | 129.8 | 0.001 | that also makes sense. One question that I had is that can there be capital letters or can I assume lower case only? |
| 5 | Google_Coding_Interview.wav | SPEAKER_01 | 248.7 | 250.6 | 0.001 | s equal strings and |

## 11. How can you determine whether one string is a substring of another?

- type: paraphrase
- file_hint: Google_Coding_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Google_Coding_Interview.wav | SPEAKER_01 | 197.2 | 228.8 | 0.480 | b d you get the idea right and then put those in a set and then compare if we have valid inputs given our words list so I'll write that down but that kind of seems like a slow solution to me and I know that we can do much better but so cal… |
| 2 | Google_Coding_Interview.wav | SPEAKER_00 | 29.3 | 61.1 | 0.424 | A subsequence of a string is a new string generated from the original string with some characters can be none deleted without changing the relative order of the remaining characters. For example, ace is a subsequence of a b c d e. So one e… |
| 3 | Google_Coding_Interview.wav | SPEAKER_01 | 165.7 | 197.2 | 0.389 | Okay cool that sounds good to me I guess for a brute force solution I'm [REDACTED_NAME] one way we could do this is [REDACTED_NAME] example a b c d e this would result in we could calculate all possible substrings so a a b a c a d a e and… |
| 4 | Google_Coding_Interview.wav | SPEAKER_00 | 61.1 | 74.2 | 0.210 | b b as you can tell cannot be a subsequence of the string. Let me know if you have any questions about this or if you can understand example two as well. So what are your first thoughts? |
| 5 | Google_Coding_Interview.wav | SPEAKER_01 | 228.8 | 245.4 | 0.188 | then compare with words list and this should be I believe that calculating all possible substrings is a 2 to the n operation where n is size of this and |

## 12. What solution approach did the candidate propose for the coding problem?

- type: paraphrase
- file_hint: Google_Coding_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Google_Coding_Interview.wav | SPEAKER_00 | 0.0 | 29.3 | 0.037 | a coding problem and you're going to have about 20 to 30 minutes to solve it. Most importantly, I want to hear how your thought process is throughout this and whether you get the solution or not just communicate effectively throughout this… |
| 2 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 353.8 | 391.0 | 0.002 | It's more about how you are thinking. So I'm [REDACTED_NAME] paste the problem in your chat box. Okay. Let me know once you get this. And first do explain to me what the question is about. Okay. And then if you are comfortable, open any in… |
| 3 | Google_Coding_Interview.wav | SPEAKER_01 | 261.4 | 293.2 | 0.001 | cool so that would be the brute force solution I think another possible solution that I'm [REDACTED_NAME] is that we pre compute location of letter to index so for example we could do taking example of a b a c we could have a hash map of a… |
| 4 | Google_Coding_Interview.wav | SPEAKER_01 | 197.2 | 228.8 | 0.001 | b d you get the idea right and then put those in a set and then compare if we have valid inputs given our words list so I'll write that down but that kind of seems like a slow solution to me and I know that we can do much better but so cal… |
| 5 | Google_Coding_Interview.wav | SPEAKER_01 | 165.7 | 197.2 | 0.001 | Okay cool that sounds good to me I guess for a brute force solution I'm [REDACTED_NAME] one way we could do this is [REDACTED_NAME] example a b c d e this would result in we could calculate all possible substrings so a a b a c a d a e and… |

## 13. What did they discuss about GPT-4?

- type: keyword
- file_hint: llm_systems_interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | llm_systems_interview.wav | SPEAKER_01 | 127.5 | 158.3 | 0.133 | About distributed economic systems that incentivize the safety and human alignment of this power. About the psychology of the engineers and leaders that deploy AGI. And about the history of human nature. Our capacity for good and evil at s… |
| 2 | llm_systems_interview.wav | SPEAKER_01 | 0.0 | 32.6 | 0.028 | of open AI. The company behind GPT -4, JADGPT, Dali, Codex, and many other AI technologies which both individually and together constitute some of the greatest breakthroughs in the history of artificial intelligence, computing, and humanit… |
| 3 | llm_systems_interview.wav | SPEAKER_01 | 95.9 | 127.5 | 0.015 | Orwell's 1984 or the pleasure -fueled mass hysteria of brave new world where, as well as the new technology that undo their capacities to think. That is why these conversations with the leaders, engineers and philosophers, both optimists a… |
| 4 | llm_systems_interview.wav | SPEAKER_01 | 191.8 | 222.5 | 0.003 | Always with the goal of trying to help in my small way. If I fail, I will work hard to improve. I love you all. This is [REDACTED_NAME] Friedman podcast. To support it, please check out our sponsors in the description. And now, dear friend… |
| 5 | llm_systems_interview.wav | SPEAKER_01 | 298.0 | 309.1 | 0.002 | chat GPT? What is RLHF reinforcement learning with human feedback? What was that little magic ingredient to the dish that made it so much |

## 14. What is reinforcement learning from human feedback?

- type: keyword
- file_hint: llm_systems_interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | llm_systems_interview.wav | SPEAKER_01 | 298.0 | 309.1 | 0.368 | chat GPT? What is RLHF reinforcement learning with human feedback? What was that little magic ingredient to the dish that made it so much |
| 2 | llm_systems_interview.wav | SPEAKER_00 | 342.3 | 369.9 | 0.012 | And RLHF is how we take some human feedback. The simplest version of this is [REDACTED_NAME] outputs, ask which one is better than the other, which one the human raiders prefer, and then feed that back into the model with reinforcement lea… |
| 3 | llm_systems_interview.wav | SPEAKER_00 | 478.1 | 479.5 | 0.002 | The pre -training dataset, I guess. |
| 4 | llm_systems_interview.wav | SPEAKER_01 | 433.5 | 478.0 | 0.001 | human guidance. That's a very interesting science. It's going to be a very important science to understand how to make it usable, how to make it wise, how to make it ethical, how to make it aligned in terms of all the kind of stuff we thin… |
| 5 | llm_systems_interview.wav | SPEAKER_01 | 95.9 | 127.5 | 0.001 | Orwell's 1984 or the pleasure -fueled mass hysteria of brave new world where, as well as the new technology that undo their capacities to think. That is why these conversations with the leaders, engineers and philosophers, both optimists a… |

## 15. What is ChatGPT and how does it work?

- type: keyword
- file_hint: llm_systems_interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 267.7 | 299.6 | 0.152 | yoghita with this what I'll do is I will start designing a high -level component diagram and based on that we'll keep coming back to this set of requirements and if we see something is missing or something has to be updated and based on yo… |
| 2 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 80.0 | 92.6 | 0.133 | and some other questions that I have are how quickly do we want a response I think typically chat gpt responds within five to ten seconds is that an acceptable window or are we looking for multiple models which are fast slow and can the us… |
| 3 | llm_systems_interview.wav | SPEAKER_01 | 298.0 | 309.1 | 0.106 | chat GPT? What is RLHF reinforcement learning with human feedback? What was that little magic ingredient to the dish that made it so much |
| 4 | llm_systems_interview.wav | SPEAKER_00 | 277.2 | 298.0 | 0.072 | Well, the history books write about GPT one or two or three or four or seven. That's for them to decide. I don't really know. I think if I had to pick some moment from what we've seen so far, I'd sort of pick chat GPT. You know, it wasn't… |
| 5 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 418.0 | 438.9 | 0.063 | so when I'm [REDACTED_NAME] pages there's two parts to it one is getting the hyperlinks the outgoing hyperlinks to fetch other pages and the second thing is each page will have text so that that text has to be processed there are various w… |

## 16. What are the potential dangers or risks of AI?

- type: paraphrase
- file_hint: llm_systems_interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | llm_systems_interview.wav | SPEAKER_01 | 64.2 | 95.9 | 0.506 | know and don't yet know that will empower humans to create, to flourish, to escape the widespread poverty and suffering that exist in the world today and to succeed in that old all -too -human pursuit of happiness. It is terrifying because… |
| 2 | llm_systems_interview.wav | SPEAKER_01 | 0.0 | 32.6 | 0.190 | of open AI. The company behind GPT -4, JADGPT, Dali, Codex, and many other AI technologies which both individually and together constitute some of the greatest breakthroughs in the history of artificial intelligence, computing, and humanit… |
| 3 | llm_systems_interview.wav | SPEAKER_01 | 32.6 | 64.2 | 0.123 | We stand on the precipice of fundamental societal transformation where soon nobody knows when, but many including me believe it's within our lifetime. The collective intelligence of the human species begins to pale in comparison by many or… |
| 4 | llm_systems_interview.wav | SPEAKER_01 | 127.5 | 158.3 | 0.015 | About distributed economic systems that incentivize the safety and human alignment of this power. About the psychology of the engineers and leaders that deploy AGI. And about the history of human nature. Our capacity for good and evil at s… |
| 5 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 246.9 | 267.7 | 0.003 | I mean that depends on so in this particular exercise we are keeping the intelligence within the models as a black box you can assume that the models are trained they know what they have to do and you are a software engineer who is suppose… |

## 17. How should a chatbot maintain conversation history?

- type: paraphrase
- file_hint: System_Design_of_ChatGPT.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 450.0 | 480.0 | 0.500 | So I mean if I interject you here, right? So basically the question is hopefully you already understood this, but more clarity. So we have told that there is a specific context limit for this LLM. Okay. It could be 4000 in this case or any… |
| 2 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 0.0 | 38.1 | 0.047 | scope it out as we go but for now let's say that you have to design this chatbot which will take prompts from a user will keep the context of prompts going on in one thread and a user can also have multiple chats while the user is in one c… |
| 3 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 231.3 | 246.9 | 0.015 | okay so retrainings are very rare we might not need to look into it and finally when I'm [REDACTED_NAME] what do we need to do to get the responses are we also looking at how the chatbot has to clean the responses has to make sure nothing… |
| 4 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 246.9 | 267.7 | 0.012 | I mean that depends on so in this particular exercise we are keeping the intelligence within the models as a black box you can assume that the models are trained they know what they have to do and you are a software engineer who is suppose… |
| 5 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 155.0 | 172.5 | 0.009 | um it can depend actually you can also give the user a choice to choose a model right whenever they are writing their prompt or you can give a drop down to them which model they want to go for let's say you have different versions of your… |

## 18. How many chats can one user have?

- type: keyword
- file_hint: System_Design_of_ChatGPT.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 38.1 | 49.9 | 0.999 | 50 chats per user and this is [REDACTED_NAME] of the chats in a sense 50 chats in total or is it that at any point in time they can have 50 concurrent chat conversations going on |
| 2 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 49.9 | 80.0 | 0.998 | no for concurrent let's keep that they can have one chat at a time they can log in from multiple devices they can log in from phone from browser one browser two but at a time they can have one chat active in total for that particular user… |
| 3 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 0.0 | 38.1 | 0.994 | scope it out as we go but for now let's say that you have to design this chatbot which will take prompts from a user will keep the context of prompts going on in one thread and a user can also have multiple chats while the user is in one c… |
| 4 | llm_systems_interview.wav | SPEAKER_00 | 277.2 | 298.0 | 0.088 | Well, the history books write about GPT one or two or three or four or seven. That's for them to decide. I don't really know. I think if I had to pick some moment from what we've seen so far, I'd sort of pick chat GPT. You know, it wasn't… |
| 5 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 450.0 | 480.0 | 0.031 | So I mean if I interject you here, right? So basically the question is hopefully you already understood this, but more clarity. So we have told that there is a specific context limit for this LLM. Okay. It could be 4000 in this case or any… |

## 19. How would you design a chatbot that remembers previous conversations?

- type: paraphrase
- file_hint: System_Design_of_ChatGPT.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 0.0 | 38.1 | 0.503 | scope it out as we go but for now let's say that you have to design this chatbot which will take prompts from a user will keep the context of prompts going on in one thread and a user can also have multiple chats while the user is in one c… |
| 2 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 155.0 | 172.5 | 0.006 | um it can depend actually you can also give the user a choice to choose a model right whenever they are writing their prompt or you can give a drop down to them which model they want to go for let's say you have different versions of your… |
| 3 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 246.9 | 267.7 | 0.004 | I mean that depends on so in this particular exercise we are keeping the intelligence within the models as a black box you can assume that the models are trained they know what they have to do and you are a software engineer who is suppose… |
| 4 | llm_systems_interview.wav | SPEAKER_00 | 277.2 | 298.0 | 0.002 | Well, the history books write about GPT one or two or three or four or seven. That's for them to decide. I don't really know. I think if I had to pick some moment from what we've seen so far, I'd sort of pick chat GPT. You know, it wasn't… |
| 5 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 267.7 | 299.6 | 0.001 | yoghita with this what I'll do is I will start designing a high -level component diagram and based on that we'll keep coming back to this set of requirements and if we see something is missing or something has to be updated and based on yo… |

## 20. How can a chatbot provide factual and reliable information?

- type: paraphrase
- file_hint: System_Design_of_ChatGPT.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 205.9 | 213.3 | 0.270 | the live information about what the agent is doing, what task is completed, that can be shown to the users. |
| 2 | AI_Engineering_Mock_Interview.wav | SPEAKER_01 | 450.0 | 480.0 | 0.004 | So I mean if I interject you here, right? So basically the question is hopefully you already understood this, but more clarity. So we have told that there is a specific context limit for this LLM. Okay. It could be 4000 in this case or any… |
| 3 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 155.0 | 172.5 | 0.002 | um it can depend actually you can also give the user a choice to choose a model right whenever they are writing their prompt or you can give a drop down to them which model they want to go for let's say you have different versions of your… |
| 4 | System_Design_of_ChatGPT.wav | SPEAKER_01 | 231.3 | 246.9 | 0.002 | okay so retrainings are very rare we might not need to look into it and finally when I'm [REDACTED_NAME] what do we need to do to get the responses are we also looking at how the chatbot has to clean the responses has to make sure nothing… |
| 5 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 0.0 | 38.1 | 0.002 | scope it out as we go but for now let's say that you have to design this chatbot which will take prompts from a user will keep the context of prompts going on in one thread and a user can also have multiple chats while the user is in one c… |

## 21. How can a retrieval system combine exact matching with meaning-based matching?

- type: cross_file
- file_hint: AI_Engineering_Mock_Interview.wav

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Google_Coding_Interview.wav | SPEAKER_01 | 332.9 | 364.5 | 0.001 | yeah exactly so I can do that right now so take for example a b a c right so this would result in a hash map of a with the values of 1 and 2 0 and 2 and then be the which would result in values of 1 and then c which would be 3 does that ma… |
| 2 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 79.4 | 111.8 | 0.000 | So like I made this a rag system, which is and for like specific, a product policy related documents on like the regulated documents, compliance documents, because they have a lot of structural elements like labels, headings, and these thi… |
| 3 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 174.2 | 205.9 | 0.000 | So yeah, I'm [REDACTED_NAME] on that. But yeah, so there are like since it's a multi -agent orchestration system. So they're like specialized agents for like reading the code, writing the code, generating patches, writing tests and then cr… |
| 4 | Google_Coding_Interview.wav | SPEAKER_01 | 228.8 | 245.4 | 0.000 | then compare with words list and this should be I believe that calculating all possible substrings is a 2 to the n operation where n is size of this and |
| 5 | Google_Coding_Interview.wav | SPEAKER_01 | 197.2 | 228.8 | 0.000 | b d you get the idea right and then put those in a set and then compare if we have valid inputs given our words list so I'll write that down but that kind of seems like a slow solution to me and I know that we can do much better but so cal… |

## 22. What did they say about firing an employee for poor performance?

- type: hard_negative
- file_hint: null

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | llm_systems_interview.wav | SPEAKER_01 | 95.9 | 127.5 | 0.000 | Orwell's 1984 or the pleasure -fueled mass hysteria of brave new world where, as well as the new technology that undo their capacities to think. That is why these conversations with the leaders, engineers and philosophers, both optimists a… |
| 2 | llm_systems_interview.wav | SPEAKER_01 | 64.2 | 95.9 | 0.000 | know and don't yet know that will empower humans to create, to flourish, to escape the widespread poverty and suffering that exist in the world today and to succeed in that old all -too -human pursuit of happiness. It is terrifying because… |
| 3 | Behavioral_mock_Interview.wav | SPEAKER_01 | 224.9 | 233.6 | 0.000 | Awesome. That sounds like a very worthwhile experience. So now that we've talked a little bit about your strengths, maybe you could tell me about a weakness that you face in the workforce. |
| 4 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 286.7 | 314.7 | 0.000 | So even if like user was like, let's say the runs failed, they had to be like restarted from again and again. So these are some points. Maybe the elements that we're using as agents, maybe they are not being able to like the inference is n… |
| 5 | AI_Engineering_Mock_Interview.wav | SPEAKER_00 | 111.8 | 142.1 | 0.000 | Right. So also, so a lot of more additional components like well, hybrid search, then a re rank, that's a proper rank fusion, then re ranking capabilities. These were added also on top of that. So back when I was scrolling on LinkedIn five… |

## 23. How does computer vision or image recognition work?

- type: hard_negative
- file_hint: null

| rank | file | speaker | start_ts | end_ts | score | snippet |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | llm_systems_interview.wav | SPEAKER_01 | 0.0 | 32.6 | 0.001 | of open AI. The company behind GPT -4, JADGPT, Dali, Codex, and many other AI technologies which both individually and together constitute some of the greatest breakthroughs in the history of artificial intelligence, computing, and humanit… |
| 2 | System_Design_of_ChatGPT.wav | SPEAKER_00 | 246.9 | 267.7 | 0.001 | I mean that depends on so in this particular exercise we are keeping the intelligence within the models as a black box you can assume that the models are trained they know what they have to do and you are a software engineer who is suppose… |
| 3 | llm_systems_interview.wav | SPEAKER_00 | 342.3 | 369.9 | 0.001 | And RLHF is how we take some human feedback. The simplest version of this is [REDACTED_NAME] outputs, ask which one is better than the other, which one the human raiders prefer, and then feed that back into the model with reinforcement lea… |
| 4 | llm_systems_interview.wav | SPEAKER_00 | 222.9 | 244.4 | 0.001 | It's a system that we'll look back at and say it was a very early AI. And it will, it's slow, it's buggy, it doesn't do a lot of things very well. But neither did the very earliest computers. And they still pointed a path to something that… |
| 5 | llm_systems_interview.wav | SPEAKER_01 | 191.8 | 222.5 | 0.000 | Always with the goal of trying to help in my small way. If I fail, I will work hard to improve. I love you all. This is [REDACTED_NAME] Friedman podcast. To support it, please check out our sponsors in the description. And now, dear friend… |
