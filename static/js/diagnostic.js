(() => {
  "use strict";
  const byId = id => document.getElementById(id);
  if (!byId("diagnostic-start")) return;
  const questions = [
    ["Where do you usually get stuck?", ["Writing the first message", "Moving beyond small talk", "Suggesting a date"]],
    ["What caught your attention in her profile?", ["A hobby", "A photo or place", "There isn’t much to go on"]],
    ["What feels most like you?", ["Light and playful", "Curious and thoughtful", "Simple and direct"]]
  ];
  const examples = [
    [
      ["Your profile mentions hiking. Which trail deserves a repeat visit?", "What’s one trail you’d happily hike again?", "Do you have a favorite local hiking trail?"],
      ["That mountain view looks worth the climb. Where was it?", "What was the highlight of the trip in your photo?", "Where was your travel photo taken?"],
      ["Important weekend question: new coffee spot or a familiar favorite?", "What’s something you’ve enjoyed doing lately?", "What do you like doing on weekends?"]
    ],
    [
      ["You mentioned hiking earlier. Are you team sunrise start or team extra sleep?", "What got you interested in hiking?", "What do you enjoy most about hiking?"],
      ["That trip you mentioned sounds like a story. Best moment or funniest mishap?", "What made that place memorable for you?", "Would you visit that place again?"],
      ["You mentioned a busy week. What’s your go-to way to switch off?", "You said you enjoy cooking. What do you like making most?", "You mentioned a new hobby. How’s it going?"]
    ],
    [
      ["I’ve enjoyed talking about our coffee favorites. Want to compare notes over coffee this weekend?", "I’ve enjoyed our conversation. Would you like to meet for coffee this weekend?", "Would you like to grab coffee on Saturday?"],
      ["We’ve covered travel spots—want to try a local coffee spot together this weekend?", "I’ve enjoyed hearing your travel stories. Would you like to continue over coffee?", "Would you like to meet for coffee this weekend?"],
      ["I’ve enjoyed this chat. Want to take it from the inbox to a coffee shop this weekend?", "I’ve enjoyed getting to know you here. Would you be interested in meeting for coffee?", "Would you like to meet for coffee sometime this week?"]
    ]
  ];
  let step = 0;
  let answers = [];
  const show = id => ["diagnostic-intro", "diagnostic-questions", "diagnostic-result"].forEach(key => { byId(key).hidden = key !== id; });
  function question() {
    show("diagnostic-questions");
    byId("diagnostic-progress").textContent = `QUESTION ${step + 1} OF 3`;
    byId("diagnostic-bar").style.width = `${(step + 1) / 3 * 100}%`;
    byId("diagnostic-question").textContent = questions[step][0];
    byId("diagnostic-options").replaceChildren();
    questions[step][1].forEach((label, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "diagnostic__option";
      button.textContent = label;
      button.addEventListener("click", () => {
        answers[step] = index;
        if (step < 2) { step++; question(); } else result();
      });
      byId("diagnostic-options").append(button);
    });
    byId("diagnostic-back").hidden = step === 0;
    byId("diagnostic-question").focus({preventScroll: true});
  }
  function result() {
    show("diagnostic-result");
    const [stage, detail, tone] = answers;
    byId("diagnostic-result-title").textContent = ["Start with something she chose to share.", "Follow a detail already in the conversation.", "Make a clear, low-pressure invitation."][stage];
    byId("diagnostic-advice").textContent = [
      detail === 2 ? "A sparse profile doesn’t give you much context. Try one simple question about everyday interests." : "Use a real profile detail and ask something you actually want to know. Here’s an example to adapt:",
      "Build on something she actually said. The example below assumes that topic has already come up; replace it with your real conversation.",
      "If you’ve both been engaged in the conversation, suggest a simple plan. Leave room for her to decline, and respect her answer."
    ][stage];
    byId("diagnostic-example").textContent = examples[stage][detail][tone];
    byId("diagnostic-why").textContent = [
      "Why this works as a starting point: it uses a specific detail and gives her one easy thing to respond to. Use a detail that is actually in her profile.",
      "Why this works as a starting point: it follows a topic already shared instead of jumping to an unrelated question. Use the real details of your chat.",
      "Why this works as a starting point: it proposes a simple plan and makes the question clear. It only fits a mutually engaged conversation."
    ][stage];
    byId("diagnostic-bridge").textContent = [
      "Your focus: the first message. The starter guide develops this exact skill with a framework, examples and practice.",
      "Your focus: moving beyond small talk. The starter guide focuses on opening conversations; the Complete Library also includes The Reply Decoder for the next stage.",
      "Your focus: suggesting a date. The starter guide focuses on first messages; the Complete Library adds From Chat to First Date for clear, low-pressure invitations."
    ][stage];
    byId("sales-content").hidden = false;
    document.body.classList.remove("diagnostic-locked");
    byId("diagnostic-unlock-note")?.remove();
    byId("diagnostic-result-title").focus({preventScroll: true});
  }
  byId("diagnostic-start").hidden = false;
  byId("diagnostic-start").addEventListener("click", question);
  byId("diagnostic-back").addEventListener("click", () => { step--; question(); });
  byId("diagnostic-restart").addEventListener("click", () => { step = 0; answers = []; question(); });
})();
