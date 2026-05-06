# 5-Minute Video Presentation Script
**Paper:** LLMs Get Lost In Multi-Turn Conversation (ICLR 2026)

---

## 0:00 - 0:45 | Introduction & Title Slide
"Hello everyone, I’m Karthik Kovi. Today I’ll be presenting the paper 'LLMs Get Lost In Multi-Turn Conversation,' which received the Outstanding Paper Award at ICLR 2026. 

We all use LLMs like ChatGPT or Gemini as conversational interfaces. We assume that if a model is smart enough to solve a task in one go, it should definitely be able to solve it over a few turns of chat. This paper proves that this assumption is actually wrong. In fact, most state-of-the-art models 'get lost' during the conversation."

## 0:45 - 1:30 | Main Objectives
"The main objective of this study was to evaluate LLMs in a realistic multi-turn setting. Most benchmarks today give the AI a perfectly detailed instruction at the start. But in real life, users often start with a vague idea and clarify it over several turns. 

The researchers wanted to see if models maintain their 'Aptitude'—their raw intelligence—while facing the 'Unreliability' that comes with a multi-turn dialogue."

## 1:30 - 2:30 | Methods: Sharding
"To test this, the authors created a framework called 'Sharding.' They took high-quality single-turn tasks (like coding or math problems) and broke them into small pieces or 'shards' of information.

In their simulation, a 'User AI' reveals only one shard at a time. The 'Assistant AI' has to keep track of every detail revealed so far to reach the correct solution. They tested over 15 different models, including GPT-4o and Gemini, across 200,000 simulated conversations."

## 2:30 - 3:30 | Results: The Performance Drop
"The results were startling. Across all models, there was a universal performance drop of 39% when moving from single-turn to multi-turn. 

What’s even more interesting is that it didn’t matter how big the model was. Even the most powerful models like Gemini 2.5 Pro and GPT-4.1 suffered significantly. Even reasoning models that 'think' before they speak, like DeepSeek-R1, got lost just as easily. The authors found that this degradation starts happening in conversations as short as just two turns."

## 3:30 - 4:15 | Aptitude vs. Reliability
"So, why does this happen? The paper makes a key distinction between Aptitude and Reliability. 

The models don't lose their intelligence—their Aptitude remains high. However, their Reliability collapses. They get 'lost' because they prematurely try to solve the problem using wrong assumptions. Once they take that wrong turn, they tend to over-rely on their own previous mistakes and can't recover. They essentially confuse themselves with their own verbosity."

## 4:15 - 5:00 | Conclusion & Recommendations
"The implications are huge. For us as users, the researchers recommend: 'If time allows, try again.' If a chat is going nowhere, starting a fresh conversation is often better than trying to fix the current one. 

For model builders, the call to action is clear: we need to stop just chasing higher IQ scores on single-turn benchmarks and start prioritizing multi-turn reliability. 

Thank you for listening!"
