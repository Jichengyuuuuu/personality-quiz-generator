import { scoreQuiz } from "./scoring.js";

const byId = (id) => document.getElementById(id);
const screens = ["loading", "intro", "question", "calculating", "result", "error"];
const state = { quiz: null, experience: null, questions: [], optionOrders: {}, answers: {}, index: 0, latestResult: null };

function showScreen(name) {
  for (const screen of screens) byId(`${screen}-screen`).hidden = screen !== name;
}

function shuffle(items) {
  const copy = [...items];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
  }
  return copy;
}

function makeList(target, items) {
  target.replaceChildren(...items.map((text) => {
    const item = document.createElement("li");
    item.textContent = text;
    return item;
  }));
}

function applyTheme() {
  const theme = state.experience.theme;
  document.documentElement.style.setProperty("--background", theme.background_color);
  document.documentElement.style.setProperty("--text", theme.text_color);
  document.documentElement.style.setProperty("--accent", theme.accent_color);
}

function renderIntro() {
  const intro = state.experience.screens.intro;
  byId("intro-eyebrow").textContent = intro.eyebrow ?? `${state.quiz.duration.minutes} 分钟测试`;
  byId("quiz-title").textContent = state.quiz.title;
  byId("quiz-promise").textContent = state.quiz.promise;
  byId("quiz-meta").textContent = `${state.quiz.questions.length} 道题 · 约 ${state.quiz.duration.minutes} 分钟`;
  byId("start-button").textContent = intro.start_label;
  byId("quiz-disclaimer").textContent = intro.disclaimer;
  document.title = state.quiz.title;
}

function begin() {
  state.answers = {};
  state.index = 0;
  state.latestResult = null;
  state.questions = state.experience.interaction.shuffle_questions ? shuffle(state.quiz.questions) : [...state.quiz.questions];
  state.optionOrders = Object.fromEntries(
    state.questions.map((question) => [
      question.id,
      state.experience.interaction.shuffle_options ? shuffle(question.options) : [...question.options],
    ]),
  );
  renderQuestion();
}

function renderQuestion() {
  showScreen("question");
  const question = state.questions[state.index];
  const config = state.experience.screens.questions;
  const options = state.optionOrders[question.id];
  const progress = ((state.index + 1) / state.questions.length) * 100;
  byId("progress-label").textContent = `${state.index + 1} / ${state.questions.length}`;
  byId("progress-bar").style.width = `${progress}%`;
  byId("question-kicker").textContent = `QUESTION ${String(state.index + 1).padStart(2, "0")}`;
  byId("question-text").textContent = question.text;
  byId("back-button").hidden = !config.allow_back;
  byId("back-button").disabled = state.index === 0;
  byId("option-list").replaceChildren(...options.map((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `option${state.answers[question.id] === option.id ? " selected" : ""}`;
    button.textContent = option.text;
    button.addEventListener("click", () => selectOption(question.id, option.id));
    return button;
  }));
  const nextButton = byId("next-button");
  nextButton.textContent = state.index === state.questions.length - 1 ? "查看结果" : "下一题";
  nextButton.hidden = state.experience.interaction.auto_advance || !state.answers[question.id];
  byId("question-text").focus();
}

function selectOption(questionId, optionId) {
  state.answers[questionId] = optionId;
  if (state.experience.interaction.auto_advance) advance();
  else renderQuestion();
}

function advance() {
  if (!state.answers[state.questions[state.index].id]) return;
  if (state.index === state.questions.length - 1) return finish();
  state.index += 1;
  renderQuestion();
}

function goBack() {
  if (state.index === 0) return;
  state.index -= 1;
  renderQuestion();
}

function finish() {
  showScreen("calculating");
  const calculating = state.experience.screens.calculating ?? { duration_ms: 0, messages: ["正在生成结果……"] };
  byId("calculating-message").textContent = calculating.messages?.[0] ?? "正在生成结果……";
  window.setTimeout(() => {
    try {
      state.latestResult = scoreQuiz(state.quiz, state.answers);
      renderResult();
    } catch (error) {
      showError(error);
    }
  }, Number(calculating.duration_ms ?? 0));
}

function renderResult() {
  const scored = state.latestResult;
  const result = state.quiz.results.find((item) => item.id === scored.primary.id);
  byId("result-symbol").textContent = result.visual?.symbol ?? "✦";
  byId("result-symbol").style.color = result.visual?.accent_color ?? state.experience.theme.accent_color;
  byId("result-name").textContent = result.name;
  byId("result-hook").textContent = result.hook;
  byId("result-description").textContent = result.description;
  makeList(byId("strength-list"), result.strengths);
  makeList(byId("tradeoff-list"), result.tradeoffs);
  byId("share-line").textContent = result.share_line;

  const secondaryPanel = byId("secondary-result");
  if (scored.secondary && state.experience.screens.result.show_secondary) {
    secondaryPanel.hidden = false;
    secondaryPanel.textContent = `你的隐藏副人格是：${scored.secondary.name}（${scored.secondary.match}% 匹配）`;
  } else {
    secondaryPanel.hidden = true;
  }

  const dimensionPanel = byId("dimension-panel");
  dimensionPanel.hidden = !state.experience.screens.result.show_dimensions;
  dimensionPanel.replaceChildren(...scored.evidence.map((item) => {
    const group = document.createElement("div");
    const label = document.createElement("div");
    label.className = "dimension-label";
    const name = document.createElement("span");
    name.textContent = item.name;
    const value = document.createElement("span");
    value.textContent = `${item.lean} · ${Math.round(item.score)}`;
    label.append(name, value);
    const track = document.createElement("div");
    track.className = "dimension-track";
    const fill = document.createElement("span");
    fill.style.width = `${item.score}%`;
    track.append(fill);
    group.append(label, track);
    return group;
  }));

  const actions = state.experience.screens.result.actions;
  byId("share-button").hidden = !actions.includes("share");
  byId("restart-button").hidden = !actions.includes("restart");
  byId("copy-status").textContent = "";
  showScreen("result");
}

function formatTemplate(template, result) {
  return template
    .replaceAll("{result_name}", result.name)
    .replaceAll("{share_line}", result.share_line)
    .replaceAll("{result_hook}", result.hook)
    .replaceAll("{quiz_title}", state.quiz.title);
}

async function shareResult() {
  const result = state.quiz.results.find((item) => item.id === state.latestResult.primary.id);
  const title = formatTemplate(state.experience.share.title_template, result);
  const text = formatTemplate(state.experience.share.text_template, result);
  try {
    if (navigator.share) {
      await navigator.share({ title, text });
      byId("copy-status").textContent = "分享面板已打开。";
    } else {
      await navigator.clipboard.writeText(`${title}\n${text}`);
      byId("copy-status").textContent = "结果文案已复制。";
    }
  } catch (error) {
    if (error.name !== "AbortError") byId("copy-status").textContent = "暂时无法分享，请手动复制结果。";
  }
}

function restart() {
  state.answers = {};
  state.index = 0;
  state.latestResult = null;
  showScreen("intro");
}

function showError(error) {
  byId("error-message").textContent = `${error.message}。请确认 quiz.json 与 experience.json 可以通过校验。`;
  showScreen("error");
}

async function initialize() {
  try {
    const [quizResponse, experienceResponse] = await Promise.all([fetch("./quiz.json"), fetch("./experience.json")]);
    if (!quizResponse.ok || !experienceResponse.ok) throw new Error("配置文件读取失败");
    [state.quiz, state.experience] = await Promise.all([quizResponse.json(), experienceResponse.json()]);
    applyTheme();
    renderIntro();
    showScreen("intro");
  } catch (error) {
    showError(error);
  }
}

byId("start-button").addEventListener("click", begin);
byId("back-button").addEventListener("click", goBack);
byId("next-button").addEventListener("click", advance);
byId("share-button").addEventListener("click", shareResult);
byId("restart-button").addEventListener("click", restart);
initialize();
