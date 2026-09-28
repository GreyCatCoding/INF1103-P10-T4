# Project Outline

## Problem Statement

Keyword and regex blocklists, which are often used by third-party companies to moderate user-generated content (UGC) on platforms, face limitations when handling content that requires interpreting context, user dispositions, and evolving slang.

Such limitations result in a queue of false positives and false negatives, which moderators are tasked to manually account for and review. This causes manpower and organisational strain and directly contributes to inconsistent and unruly decision-making.


## Proposed Solution

We propose a terminal-based system that helps human moderators make informed decisions on reported UGC.

The system involves analysing each report with sufficient situational and dispositional context and applies predefined business rules to recommend a review priority and their courses of action.


## Target Users

Safety moderator analysts and their respective moderator teams are impacted as they are the primary group of users who directly interact with the UGC.

They are responsible for handling the queue of reported content and flagging them accurately, as well as taking the appropriate further action. They will have increased efficiency and accuracy when handling reported content, as well as a reduced workload, with our system significantly diminishing false positives and false negatives that need to be manually reviewed.

Operation managers within the third-party companies and the hiring companies are also directly impacted as they are responsible for deploying and maintaining our system to streamline report queues and reduce the moderator team's workload across client platforms.


## User Inputs

Each reported UGC will be structured as a JSON record. When users provide the data needed to structure the JSON, the following fields must be provided:

1. **Required fields:** report ID, reported user ID, reported content text, content type, and report reason.
2. **Context fields:** parent post or comment, comment replies, captions, and hashtags where relevant.
3. **Dispositional fields:** previous violation flags, previous report count, and user's account age in days.

The inputs require standard validation, where required text cannot be empty, IDs must follow chosen formats, counts must be non-negative integers, and content type and report reason must use approved options.


## Use of AI

The AI API is exclusively called in the AI Manager and will interpret meaning from content and provide structured context based on the given inputs.

It will not be given any logic or business rules to provide definitive conclusions on the inputs. Therefore, it will not be able to recommend further actions or assign review priorities.

The AI Manager will:

- Build the prompt.
- Call the AI API.
- Parse the given data from the user inputs.
- Validate its JSON schema.
- Provide a feedback loop and manual interference to handle invalid responses or errors to ensure the system is error resilient.

The AI will generate structured context output using the prompt. This output helps provide in-depth contextual and dispositional information on the reported content, which can be leveraged by the Logic Manager to make more informed decisions.

The AI helps to solve the aforementioned faults in keyword and regex blocklists through multiple means:

1. Quotations can be identified by analysing the intent of the content.
2. Deliberate obfuscation of languages can be identified to help detect slang from different forms of communication, such as Singlish and emojis used to express certain slang.
3. Contextual evidence can be extracted.


## Business Rules

Python functions will be used to evaluate, score, and route the outputs to help decide the review priority and recommended further action to be taken, with a final layer of manual decision-making to approve further actions.

There will be multi-condition rules that utilise multiple fields from the AI output. For example, context dependency and target type may be used to determine a P1 priority and apply the predefined deterministic business rules in the Logic Manager.

| Priority | Meaning | Action to be Taken |
|---|---|---|
| **P1** | Severe/Repeat offender | Remove user with human confirmation |
| **P2** | Harmful regardless of context; can be taken seriously at face value without added context to situation | Remove content with human confirmation |
| **P3** | Harmful without further context; can be taken lightly with added context to situation | Warn user and/or prompt human review |
| **P4** | Low severity | Monitor user |