const HISTORY_KEY = 'smalltalk-vending-history';

const topics = [
  {
    id: 'coffee',
    slot: 1,
    labelKo: '커피 수다',
    subLabel: '따뜻한 한마디',
    packageType: 'can',
    color: '#8f5a3c',
    lightColor: '#c49273',
    prompts: [
      '오늘 커피 드셨어요? 요즘 어떤 메뉴를 제일 자주 드세요?',
      '아침에 커피 한 잔 하면 좀 살아나는 편이세요?',
      '카페 가면 늘 시키는 고정 메뉴 있으세요?',
      '요즘 맛있게 마신 커피나 디저트 있으면 추천해 주세요.',
      '집에서 내려 마시는 쪽이세요, 아니면 카페 쪽이세요?'
    ]
  },
  {
    id: 'weather',
    slot: 2,
    labelKo: '날씨 이야기',
    subLabel: '가볍게 꺼내기',
    packageType: 'bottle',
    color: '#5d8fd9',
    lightColor: '#93bff7',
    prompts: [
      '오늘 날씨가 생각보다 괜찮네요. 나오실 때 어떠셨어요?',
      '요즘은 아침저녁이 달라서 옷 입기 애매하지 않아요?',
      '비 오는 날 좋아하세요, 아니면 맑은 날이 더 좋으세요?',
      '날씨 좋을 때 가볍게 산책하는 편이세요?',
      '이번 주는 날씨 때문에 계획 바뀐 적 있으셨어요?'
    ]
  },
  {
    id: 'lunch',
    slot: 3,
    labelKo: '점심 메뉴',
    subLabel: '회사 근처 화제',
    packageType: 'can',
    color: '#d97a4f',
    lightColor: '#f4b089',
    prompts: [
      '점심 뭐 드셨어요? 만족스러운 메뉴였나요?',
      '근처에서 자주 가는 점심 맛집 있으세요?',
      '점심은 든든한 한식이 좋으세요, 가벼운 메뉴가 좋으세요?',
      '혼밥도 편하신 편이에요, 아니면 같이 먹는 게 좋으세요?',
      '오늘 저녁까지 생각나게 하는 점심 메뉴가 있으셨나요?'
    ]
  },
  {
    id: 'weekend',
    slot: 4,
    labelKo: '주말 계획',
    subLabel: '편하게 묻기',
    packageType: 'bottle',
    color: '#c0578e',
    lightColor: '#e297bc',
    prompts: [
      '주말에는 보통 푹 쉬는 편이세요, 아니면 바쁘게 보내세요?',
      '이번 주말에 딱 하나 하고 싶은 게 있다면 뭐예요?',
      '주말 아침은 평일보다 여유 있게 시작하시는 편이세요?',
      '주말마다 챙겨 하는 루틴 같은 게 있으세요?',
      '집콕 주말이 더 좋으세요, 밖에 나가는 주말이 더 좋으세요?'
    ]
  },
  {
    id: 'hobbies',
    slot: 5,
    labelKo: '취미 이야기',
    subLabel: '요즘 빠진 것',
    packageType: 'can',
    color: '#52a57d',
    lightColor: '#8ad7ae',
    prompts: [
      '요즘 쉬는 시간에 가장 많이 하는 취미가 뭐예요?',
      '한번 시작하면 시간 가는 줄 모르는 취미 있으세요?',
      '예전에는 안 했는데 요즘 새로 재미 붙인 게 있으세요?',
      '취미는 혼자 즐기는 쪽이세요, 같이 하는 쪽이세요?',
      '남에게 꼭 추천하고 싶은 취미 하나만 고르면 뭐예요?'
    ]
  },
  {
    id: 'work',
    slot: 6,
    labelKo: '업무 리듬',
    subLabel: '오늘의 템포',
    packageType: 'bottle',
    color: '#6c6ab1',
    lightColor: '#a3a1ed',
    prompts: [
      '오늘은 비교적 집중이 잘 되는 날이세요?',
      '일할 때 꼭 필요한 나만의 루틴 같은 게 있으세요?',
      '바쁜 날은 어떻게 리듬 조절하시는 편이에요?',
      '업무 중간에 머리 식힐 때 보통 뭘 하세요?',
      '최근에 일하면서 작게라도 뿌듯했던 순간 있으셨어요?'
    ]
  },
  {
    id: 'movies',
    slot: 7,
    labelKo: '영화 한 편',
    subLabel: '가볍게 추천',
    packageType: 'can',
    color: '#b64d4d',
    lightColor: '#dc8b8b',
    prompts: [
      '최근에 본 영화나 드라마 중에 기억에 남는 거 있으세요?',
      '영화는 집에서 보는 편이세요, 극장에서 보는 편이세요?',
      '가볍게 보기 좋은 장르 하나만 고르면 뭐 고르세요?',
      '다시 봐도 좋은 작품이 있으시면 어떤 거예요?',
      '주말에 보기 좋은 영화 추천 하나 받아도 될까요?'
    ]
  },
  {
    id: 'travel',
    slot: 8,
    labelKo: '여행 이야기',
    subLabel: '어디든 떠나기',
    packageType: 'bottle',
    color: '#3c9f9a',
    lightColor: '#76d7d2',
    prompts: [
      '요즘 가장 가고 싶은 여행지는 어디세요?',
      '여행 가면 계획형이세요, 즉흥형이세요?',
      '짧게 다녀오기 좋은 국내 장소 추천하실 곳 있으세요?',
      '여행에서 음식이 중요한 편이세요, 풍경이 중요한 편이세요?',
      '최근에 다녀온 곳 중에 다시 가고 싶은 곳이 있으세요?'
    ]
  }
];

const topicGrid = document.getElementById('topic-grid');
const selectionPad = document.getElementById('selection-pad');
const promptWindow = document.getElementById('prompt-window');
const historyList = document.getElementById('history-list');
const activeTopicLabel = document.getElementById('active-topic-label');
const selectionReadout = document.getElementById('selection-readout');
const paymentAmount = document.getElementById('payment-amount');
const paymentNote = document.getElementById('payment-note');
const coinSlot = document.getElementById('coin-slot');
const coinButton = document.getElementById('coin-button');
const confirmButton = document.getElementById('confirm-button');
const cancelButton = document.getElementById('cancel-button');
const clearButton = document.getElementById('clear-button');
const machineStatus = document.getElementById('machine-status');
const statusDetail = document.getElementById('status-detail');
const dispenseSlot = document.getElementById('dispense-slot');
const dispenseCan = document.getElementById('dispense-can');
const dispenseCanLabel = document.getElementById('dispense-can-label');
const pickupToggle = document.getElementById('pickup-toggle');
const pickupDoor = document.querySelector('.pickup-door');
const flowSteps = Array.from(document.querySelectorAll('.flow-step'));

const COIN_AMOUNT = 100;

let selectedTopicId = null;
let history = loadHistory();
let dispenseTimer = null;
let insertedAmount = 0;
let pickupDoorOpen = false;
let dispensedTopicId = null;
let pendingDispense = null;

function shuffle(list) {
  const copy = [...list];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const randomIndex = Math.floor(Math.random() * (index + 1));
    [copy[index], copy[randomIndex]] = [copy[randomIndex], copy[index]];
  }
  return copy;
}

function pickPromptBatch(topic) {
  const count = Math.min(topic.prompts.length, Math.floor(Math.random() * 3) + 3);
  return shuffle(topic.prompts).slice(0, count);
}

function formatTime(isoString) {
  return new Intl.DateTimeFormat('ko-KR', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(isoString));
}

function loadHistory() {
  try {
    const stored = window.localStorage.getItem(HISTORY_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveHistory() {
  window.localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function getTopicById(topicId) {
  return topics.find((topic) => topic.id === topicId) || topics[0];
}

function getTopicBySlot(slot) {
  return topics.find((topic) => topic.slot === slot) || null;
}

function updateFlowStep(stepIndex) {
  flowSteps.forEach((step, index) => {
    step.classList.toggle('is-active', index === stepIndex - 1);
  });
}

function updateSelection(topic, sourceLabel = '상품 선택') {
  selectedTopicId = topic.id;
  activeTopicLabel.textContent = topic.labelKo;
  selectionReadout.textContent = `${topic.slot}번`;
  machineStatus.textContent = '선택됨';
  statusDetail.textContent = `${sourceLabel} · ${topic.labelKo} 선택 완료. 이제 100원을 넣고 배출 버튼을 눌러 주세요.`;
  updateFlowStep(2);
  renderTopics();
}

function updatePaymentUi() {
  paymentAmount.textContent = `${insertedAmount}원`;
  if (insertedAmount > 0) {
    paymentNote.textContent = `${insertedAmount}원이 들어 있습니다. 상품 한 개당 100원씩 차감됩니다.`;
  } else {
    paymentNote.textContent = '상품을 고른 뒤 100원을 넣고 배출 버튼을 눌러 주세요.';
  }
}

function resetPaymentState() {
  insertedAmount = 0;
  updatePaymentUi();
  coinSlot.classList.remove('is-loaded');
}

function insertCoin() {
  insertedAmount += COIN_AMOUNT;
  updatePaymentUi();
  coinSlot.classList.remove('is-loaded');
  void coinSlot.offsetWidth;
  coinSlot.classList.add('is-loaded');
  machineStatus.textContent = '결제 대기';

  if (selectedTopicId) {
    const topic = getTopicById(selectedTopicId);
    statusDetail.textContent = `${topic.labelKo} 선택 완료. 배출 버튼을 누르면 바로 내려옵니다.`;
    updateFlowStep(2);
    return;
  }

  statusDetail.textContent = '동전이 들어갔습니다. 이제 상품을 고르거나 번호를 선택해 주세요.';
  updateFlowStep(1);
}

function clearSelection() {
  selectedTopicId = null;
  activeTopicLabel.textContent = '상품을 골라 주세요';
  selectionReadout.textContent = '없음';
  machineStatus.textContent = insertedAmount > 0 ? '결제 대기' : '대기 중';
  statusDetail.textContent =
    insertedAmount > 0
      ? `동전 ${insertedAmount}원이 들어 있습니다. 이제 원하는 상품을 골라 주세요.`
      : '먼저 상품을 고른 뒤 결제하고, 마지막에 수령 버튼으로 문장을 꺼내 주세요.';
  updateFlowStep(1);
  renderTopics();
}

function setPickupDoor(open) {
  pickupDoorOpen = open;
  pickupDoor.classList.toggle('is-open', open);
  pickupToggle.textContent = open ? '수령 완료' : '수령하기';
}

function clearDispensedItem() {
  dispensedTopicId = null;
  pendingDispense = null;
  dispenseSlot.classList.remove('has-item');
  dispenseCanLabel.textContent = '';
  setPickupDoor(false);
}

function startDispenseAnimation(topic) {
  if (dispenseTimer) {
    window.clearTimeout(dispenseTimer);
  }

  dispensedTopicId = topic.id;
  setPickupDoor(false);
  dispenseSlot.classList.remove('is-dispensing');
  dispenseSlot.classList.remove('has-item');
  void dispenseSlot.offsetWidth;
  dispenseCan.style.setProperty('--can-color', topic.color);
  dispenseCan.style.setProperty('--can-color-light', topic.lightColor);
  dispenseCanLabel.textContent = topic.labelKo;
  dispenseSlot.classList.add('has-item');
  dispenseSlot.classList.add('is-dispensing');

  dispenseTimer = window.setTimeout(() => {
    dispenseSlot.classList.remove('is-dispensing');
  }, 1600);
}

function renderTopics() {
  topicGrid.innerHTML = '';
  selectionPad.innerHTML = '';

  for (let rowIndex = 0; rowIndex < topics.length; rowIndex += 2) {
    const row = document.createElement('div');
    row.className = 'shelf-row';

    topics.slice(rowIndex, rowIndex + 2).forEach((topic) => {
      const isActive = topic.id === selectedTopicId;
      const item = document.createElement('button');
      item.type = 'button';
      item.className = `stock-item${isActive ? ' is-active' : ''}`;
      item.style.setProperty('--topic-color', topic.color);
      item.style.setProperty('--topic-color-light', topic.lightColor);
      item.innerHTML = `
        <div class="item-pack${topic.packageType === 'bottle' ? ' bottle-shape' : ''}">
          <div class="item-label">
            <strong>${topic.labelKo}</strong>
            <span>${topic.subLabel}</span>
          </div>
        </div>
        <span class="item-select">선택 ${topic.slot}</span>
      `;
      item.addEventListener('click', () => {
        updateSelection(topic, '진열창 선택');
      });
      row.appendChild(item);
    });

    topicGrid.appendChild(row);
  }

  for (let number = 1; number <= 9; number += 1) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'key-button';

    if (number <= topics.length) {
      const topic = getTopicBySlot(number);
      const isActive = topic && topic.id === selectedTopicId;
      button.className = `key-button${isActive ? ' is-active' : ''}`;
      button.textContent = String(number);
      button.addEventListener('click', () => updateSelection(topic, '번호 선택'));
    } else {
      button.textContent = String(number);
      button.disabled = true;
      button.classList.add('is-disabled');
    }

    selectionPad.appendChild(button);
  }

  const zeroButton = document.createElement('button');
  zeroButton.type = 'button';
  zeroButton.className = 'key-button is-disabled';
  zeroButton.textContent = '0';
  zeroButton.disabled = true;
  selectionPad.appendChild(zeroButton);

  const emptyButton = document.createElement('button');
  emptyButton.type = 'button';
  emptyButton.className = 'key-button is-disabled';
  emptyButton.textContent = '';
  emptyButton.setAttribute('aria-hidden', 'true');
  emptyButton.disabled = true;
  selectionPad.appendChild(emptyButton);

  const infoButton = document.createElement('button');
  infoButton.type = 'button';
  infoButton.className = 'key-button info-key';
  infoButton.textContent = '안내';
  infoButton.addEventListener('click', () => {
    machineStatus.textContent = '이용 안내';
    statusDetail.textContent = '1단계 상품 선택 → 2단계 결제 → 3단계 수령 순서로 이용하면 됩니다.';
  });
  selectionPad.appendChild(infoButton);
}

function renderPrompts(topic, prompts) {
  promptWindow.innerHTML = '';

  prompts.forEach((prompt, index) => {
    const card = document.createElement('article');
    card.className = 'prompt-card';
    card.style.animationDelay = `${index * 70}ms`;
    card.innerHTML = `
      <h3>${topic.labelKo}</h3>
      <p>${prompt}</p>
    `;
    promptWindow.appendChild(card);
  });
}

function renderHistory() {
  historyList.innerHTML = '';

  if (!history.length) {
    const emptyState = document.createElement('p');
    emptyState.className = 'empty-history';
    emptyState.textContent = '아직 꺼낸 기록이 없습니다.';
    historyList.appendChild(emptyState);
    return;
  }

  history.forEach((entry) => {
    const item = document.createElement('article');
    item.className = 'history-item';
    item.innerHTML = `
      <div class="history-meta">
        <strong>${entry.topicLabel}</strong>
        <time datetime="${entry.timestamp}">${formatTime(entry.timestamp)}</time>
      </div>
      <p>${entry.prompt}</p>
    `;
    historyList.appendChild(item);
  });
}

function dispenseTopic(topicId, sourceLabel = '직접 선택') {
  const topic = getTopicById(topicId);
  const prompts = pickPromptBatch(topic);
  const timestamp = new Date().toISOString();
  const entries = prompts.map((prompt, index) => ({
    topicId: topic.id,
    topicLabel: topic.labelKo,
    prompt,
    timestamp: new Date(new Date(timestamp).getTime() + index * 1000).toISOString()
  }));

  selectedTopicId = topic.id;
  activeTopicLabel.textContent = topic.labelKo;
  selectionReadout.textContent = `${topic.slot}번`;
  pendingDispense = { topic, prompts, entries, sourceLabel };

  if (insertedAmount >= COIN_AMOUNT) {
    insertedAmount -= COIN_AMOUNT;
  }

  startDispenseAnimation(topic);
  renderTopics();
  promptWindow.innerHTML = '<p class="empty-history">배출구에서 꺼내면 문장이 나타납니다.</p>';
  updatePaymentUi();
  clearSelection();

  machineStatus.textContent = '배출 완료';
  statusDetail.textContent =
    insertedAmount > 0
      ? `${sourceLabel} · ${topic.labelKo}가 배출되었습니다. 이제 수령하기를 눌러 문장을 확인하세요. 남은 금액은 ${insertedAmount}원입니다.`
      : `${sourceLabel} · ${topic.labelKo}가 배출되었습니다. 이제 수령하기를 눌러 문장을 확인하세요.`;
  updateFlowStep(3);

  if (insertedAmount > 0) {
    paymentNote.textContent = `남은 ${insertedAmount}원입니다. 먼저 상품을 꺼낸 뒤 한 개 더 선택할 수 있습니다.`;
  } else {
    paymentNote.textContent = '먼저 상품을 꺼낸 뒤 다시 이용하려면 100원을 넣어 주세요.';
  }
}

function clearHistory() {
  history = [];
  window.localStorage.removeItem(HISTORY_KEY);
  machineStatus.textContent = '기록 비움';
  statusDetail.textContent = '최근 기록을 비웠습니다.';
  renderHistory();
}

coinButton.addEventListener('click', insertCoin);
pickupToggle.addEventListener('click', () => {
  if (!dispensedTopicId || !pendingDispense) {
    machineStatus.textContent = '대기 중';
    statusDetail.textContent = '아직 배출된 상품이 없습니다. 먼저 상품을 고르고 결제해 주세요.';
    setPickupDoor(false);
    updateFlowStep(selectedTopicId ? 2 : 1);
    return;
  }

  const { topic, prompts, entries } = pendingDispense;
  setPickupDoor(true);
  history = entries.concat(history).slice(0, 18);
  saveHistory();
  renderPrompts(topic, prompts);
  renderHistory();
  clearDispensedItem();

  machineStatus.textContent = insertedAmount > 0 ? '수령 완료' : '대기 중';
  statusDetail.textContent =
    insertedAmount > 0
      ? `상품 수령 완료. 문장이 공개되었습니다. 남은 ${insertedAmount}원으로 다음 상품을 바로 고를 수 있습니다.`
      : '상품 수령 완료. 문장이 공개되었습니다. 다음 이용을 위해 다시 100원을 넣어 주세요.';
  updateFlowStep(1);
});
cancelButton.addEventListener('click', clearSelection);
confirmButton.addEventListener('click', () => {
  if (!selectedTopicId) {
    machineStatus.textContent = '선택 필요';
    statusDetail.textContent = '먼저 상품을 선택해 주세요. 진열창을 누르거나 번호 패드를 사용하면 됩니다.';
    updateFlowStep(1);
    return;
  }

  if (insertedAmount < COIN_AMOUNT) {
    machineStatus.textContent = '결제 필요';
    statusDetail.textContent = '아직 결제가 안 됐습니다. 100원을 넣은 뒤 배출 버튼을 눌러 주세요.';
    paymentNote.textContent = '결제가 필요합니다. 위 버튼으로 100원을 넣어 주세요.';
    updateFlowStep(2);
    return;
  }

  dispenseTopic(selectedTopicId, '확인 완료');
});
clearButton.addEventListener('click', clearHistory);

renderTopics();
renderHistory();
clearSelection();
clearDispensedItem();
updatePaymentUi();
