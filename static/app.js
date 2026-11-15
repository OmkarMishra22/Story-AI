/**
 * Story AL — Narrative World Engine
 * Client Application Script (Warm Literary Atelier Edition)
 */

// Application State
const state = {
  currentView: 'overview',
  activeCategory: 'all',
  searchQuery: '',
  entries: [],
  notes: [],
  stats: {},
  project: {},
  aiStatus: { mode: 'demo', has_api_key: false },
  audioStatus: { has_cloud_tts: false, mode: 'demo_browser_tts' },
  audioScene: null,
  activeVoiceEngine: 'edge-tts',
  voiceCatalog: {},
  audioPlaylist: [],
  expressiveness: 0.75,
  isAudioPlaying: false,
  currentAudioLineIndex: -1,
  voiceFilter: 'all',
  isAllVoicesPreviewing: false,
  allVoicesPreviewIndex: -1,
  currentShowcasePlayingVoiceId: null,
  chatHistory: [],
  sampleDrafts: [],
  sampleQuestions: [],
  isSubmittingChat: false,
  isAnalyzingContinuity: false,
  isGeneratingScenes: false,
  editingEntryId: null
};

// Category Colors & Metadata (Warm, Handcrafted Literary Palette)
const CATEGORY_META = {
  character: {
    label: 'Character',
    plural: 'Characters',
    badgeClass: 'badge-character',
    accentColor: '#b8738a',
    icon: `<svg class="w-3.5 h-3.5 mr-1 text-[#f3c9d7]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`
  },
  place: {
    label: 'Location',
    plural: 'Locations',
    badgeClass: 'badge-place',
    accentColor: '#589977',
    icon: `<svg class="w-3.5 h-3.5 mr-1 text-[#aae0c3]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>`
  },
  event: {
    label: 'Event',
    plural: 'Events',
    badgeClass: 'badge-event',
    accentColor: '#e5a953',
    icon: `<svg class="w-3.5 h-3.5 mr-1 text-[#fed99b]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>`
  },
  rule: {
    label: 'World Rule',
    plural: 'World Rules',
    badgeClass: 'badge-rule',
    accentColor: '#c94a4a',
    icon: `<svg class="w-3.5 h-3.5 mr-1 text-[#fca5a5]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`
  }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  setupNavigation();
  setupEventListeners();

  // Initialize Smooth Audio Engine on first user gesture
  const initAudioOnce = () => {
    initSmoothAudioEngine();
    window.removeEventListener('click', initAudioOnce);
    window.removeEventListener('keydown', initAudioOnce);
  };
  window.addEventListener('click', initAudioOnce, { once: true });
  window.addEventListener('keydown', initAudioOnce, { once: true });

  await refreshSystemStatus();
  await loadCanonEntries();
  await loadDraftNotes();
  await loadSamples();
  await loadAudioScene();
  initializeChatGreeting();
});

// ============================================================================
// Navigation Management
// ============================================================================
function setupNavigation() {
  const navButtons = document.querySelectorAll('.nav-link');
  navButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = btn.dataset.view;
      switchView(targetView);
    });
  });

  // Handle URL hash if present
  const hash = window.location.hash.replace('#', '');
  if (['overview', 'story-bible', 'ask-lorekeeper', 'continuity-check', 'next-scene', 'audio-studio'].includes(hash)) {
    switchView(hash);
  }
}

function switchView(viewName) {
  state.currentView = viewName;
  window.location.hash = viewName;

  // Update nav buttons
  document.querySelectorAll('.nav-link').forEach(btn => {
    if (btn.dataset.view === viewName) {
      btn.classList.add('bg-[#2a241f]', 'text-[#faf8f5]', 'border-[#4e4338]');
      btn.classList.remove('text-[#c9c1b5]', 'border-transparent');
    } else {
      btn.classList.remove('bg-[#2a241f]', 'text-[#faf8f5]', 'border-[#4e4338]');
      btn.classList.add('text-[#c9c1b5]', 'border-transparent');
    }
  });

  // Update view visibility
  document.querySelectorAll('.view-section').forEach(sec => {
    sec.classList.add('hidden');
  });

  const activeSection = document.getElementById(viewName === 'next-scene' ? 'next-scene' : (viewName === 'audio-studio' ? 'audio-studio' : `view-${viewName}`));
  if (activeSection) {
    activeSection.classList.remove('hidden');
  }

  // View-specific initializations
  if (viewName === 'story-bible') {
    renderStoryBible();
  } else if (viewName === 'overview') {
    renderOverview();
  } else if (viewName === 'next-scene') {
    renderDraftNotes();
  } else if (viewName === 'audio-studio') {
    renderAudioStudio();
    if (!state.audioPlaylist || !state.audioPlaylist.length) {
      warmUpAudioScene();
    }
  }
}

// ============================================================================
// API Calls & Data Sync
// ============================================================================
async function refreshSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    state.project = data.project || {};
    state.stats = data.stats || {};
    state.aiStatus = data.ai || { mode: 'demo' };
    renderStatusBadge();
    renderOverview();
  } catch (err) {
    console.error('Failed to fetch status:', err);
  }
}

async function loadCanonEntries() {
  try {
    const res = await fetch('/api/canon');
    const data = await res.json();
    state.entries = data.entries || [];
    renderStoryBible();
    renderOverview();
  } catch (err) {
    console.error('Failed to load canon entries:', err);
  }
}

async function loadDraftNotes() {
  try {
    const res = await fetch('/api/notes');
    const data = await res.json();
    state.notes = data.notes || [];
    renderDraftNotes();
  } catch (err) {
    console.error('Failed to load draft notes:', err);
  }
}

async function loadSamples() {
  try {
    const res = await fetch('/api/samples');
    const data = await res.json();
    state.sampleDrafts = data.drafts || [];
    state.sampleQuestions = data.questions || [];
    renderSampleQuestions();
    renderSampleDraftButtons();
  } catch (err) {
    console.error('Failed to load sample questions & drafts:', err);
  }
}

async function loadAudioScene() {
  try {
    const [sceneRes, statusRes, voicesRes] = await Promise.all([
      fetch('/api/audio/scene'),
      fetch('/api/audio/status'),
      fetch('/api/audio/voices')
    ]);
    state.audioScene = await sceneRes.json();
    state.audioStatus = await statusRes.json();
    state.voiceCatalog = await voicesRes.json();
    if (state.audioScene && state.audioScene.playlist && state.audioScene.playlist.length > 0) {
      state.audioPlaylist = state.audioScene.playlist;
      prewarmSceneAudioDurations();
    }
    renderAudioStudio();
  } catch (err) {
    console.error('Failed to load audio scene:', err);
  }
}

// ============================================================================
// Renderers
// ============================================================================
function renderStatusBadge() {
  const badgeContainer = document.getElementById('ai-status-badge');
  if (!badgeContainer) return;

  const isLive = state.aiStatus.mode === 'live_ai' && state.aiStatus.has_api_key;
  if (isLive) {
    badgeContainer.innerHTML = `
      <div class="flex items-center space-x-2 bg-[#1b2820] border border-[#2b4434] text-[#aae0c3] px-3 py-1.5 rounded-full text-xs font-medium cursor-pointer" onclick="openSettingsModal()">
        <span class="w-2 h-2 rounded-full bg-[#589977] animate-pulse"></span>
        <span>Story Memory: Gemini AI</span>
      </div>
    `;
  } else {
    badgeContainer.innerHTML = `
      <div class="flex items-center space-x-2 bg-[#2d251c] border border-[#4a3928] text-[#fed99b] px-3 py-1.5 rounded-full text-xs font-medium cursor-pointer" onclick="openSettingsModal()" title="Running offline with saved Story Bible. Click to configure API keys.">
        <span class="w-2 h-2 rounded-full bg-[#e5a953]"></span>
        <span>Story Memory: Active (Using saved facts)</span>
      </div>
    `;
  }
}

function renderOverview() {
  const total = state.entries.length;
  const chars = state.entries.filter(e => e.category === 'character').length;
  const places = state.entries.filter(e => e.category === 'place').length;
  const events = state.entries.filter(e => e.category === 'event').length;
  const rules = state.entries.filter(e => e.category === 'rule').length;
  const notesCount = state.notes ? state.notes.length : (state.stats.notes || 2);

  const statTotalEl = document.getElementById('overview-stat-total');
  if (statTotalEl) statTotalEl.textContent = total;
  const statCharsEl = document.getElementById('overview-stat-chars');
  if (statCharsEl) statCharsEl.textContent = chars;
  const statPlacesEl = document.getElementById('overview-stat-places');
  if (statPlacesEl) statPlacesEl.textContent = places;
  const statEventsEl = document.getElementById('overview-stat-events');
  if (statEventsEl) statEventsEl.textContent = events;
  const statRulesEl = document.getElementById('overview-stat-rules');
  if (statRulesEl) statRulesEl.textContent = rules;
  const statNotesEl = document.getElementById('overview-stat-notes');
  if (statNotesEl) statNotesEl.textContent = notesCount;

  // Render recent canon highlights
  const highlightsContainer = document.getElementById('overview-recent-entries');
  if (highlightsContainer) {
    const highlights = state.entries.slice(0, 4);
    highlightsContainer.innerHTML = highlights.map(e => {
      const meta = CATEGORY_META[e.category] || CATEGORY_META.rule;
      return `
        <div class="p-3.5 rounded-xl bg-[#231e1a] border border-[#38312b] hover:border-[#4d443b] transition">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs px-2.5 py-0.5 rounded-full font-medium ${meta.badgeClass}">${meta.label}</span>
            <span class="text-xs text-[#8c8275] font-story italic">#${e.id.split('-').slice(1).join('-')}</span>
          </div>
          <h4 class="text-sm font-semibold text-[#f5ede0] mb-1">${escapeHtml(e.name)}</h4>
          <p class="text-xs text-[#a4998c] line-clamp-2">${escapeHtml(e.description)}</p>
        </div>
      `;
    }).join('');
  }
}

function filterBibleCategory(cat) {
  state.activeCategory = cat;
  updateCategoryPills();
  renderStoryBible();
}

function renderStoryBible() {
  const container = document.getElementById('story-bible-entries');
  if (!container) return;

  const query = state.searchQuery.toLowerCase().trim();
  const cat = state.activeCategory;

  const filtered = state.entries.filter(e => {
    if (cat !== 'all' && e.category !== cat) return false;
    if (!query) return true;
    const haystack = (e.name + ' ' + e.description + ' ' + (e.role || '') + ' ' + (e.goal || '') + ' ' + (e.relationships || '') + ' ' + (e.defining_detail || '') + ' ' + (e.tags || []).join(' ')).toLowerCase();
    return haystack.includes(query);
  });

  const countBadge = document.getElementById('story-bible-count-badge');
  if (countBadge) countBadge.textContent = `${filtered.length} of ${state.entries.length} entries recorded`;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center text-[#a4998c] bg-[#1e1b18] rounded-2xl border border-[#38312b] border-dashed">
        <p class="text-base font-story text-[#f5ede0]">No canon entries match your search.</p>
        <p class="text-xs text-[#8c8275] mt-1">Try clearing your search query or add a new entry to your story world.</p>
        <button onclick="openAddEntryModal()" class="mt-4 inline-flex items-center px-4 py-2 bg-[#d96b43] hover:bg-[#c45a33] text-white rounded-xl text-xs font-medium transition">
          + Add New Lore Entry
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(e => renderEntryCard(e)).join('');
}

function renderEntryCard(e) {
  const meta = CATEGORY_META[e.category] || CATEGORY_META.rule;
  const tagsHtml = (e.tags || []).map(t => `<span class="px-2 py-0.5 text-[11px] rounded bg-[#2a241f] text-[#c9c1b5] border border-[#3e362e] font-story italic">${escapeHtml(t)}</span>`).join(' ');

  let extraFieldsHtml = '';
  if (e.category === 'character') {
    if (e.role) {
      extraFieldsHtml += `<div class="text-xs text-[#f3c9d7] font-medium mb-2 flex items-center"><span class="text-[#8c8275] mr-1.5 font-normal">Role:</span> ${escapeHtml(e.role)}</div>`;
    }
    if (e.goal) {
      extraFieldsHtml += `
        <div class="mt-2.5 p-2.5 rounded-xl bg-[#2a1d25] border border-[#4a2b3c] text-xs">
          <span class="font-semibold text-[#f3c9d7] block mb-0.5">Primary Goal:</span>
          <p class="text-[#e2dad2]">${escapeHtml(e.goal)}</p>
        </div>
      `;
    }
    if (e.relationships) {
      extraFieldsHtml += `
        <div class="mt-2 p-2.5 rounded-xl bg-[#231e1a] border border-[#38312b] text-xs">
          <span class="font-semibold text-[#a4998c] block mb-0.5">Key Relationships:</span>
          <p class="text-[#e2dad2]">${escapeHtml(e.relationships)}</p>
        </div>
      `;
    }
  } else if (e.category === 'place' && e.defining_detail) {
    extraFieldsHtml += `
      <div class="mt-2.5 p-2.5 rounded-xl bg-[#1c2921] border border-[#2b4434] text-xs">
        <span class="font-semibold text-[#aae0c3] block mb-0.5">Defining Detail & Environmental Hazard:</span>
        <p class="text-[#e2dad2]">${escapeHtml(e.defining_detail)}</p>
      </div>
    `;
  } else if (e.category === 'rule') {
    extraFieldsHtml += `
      <div class="mt-2.5 p-2.5 rounded-xl bg-[#351c19] border border-[#522924] text-xs">
        <span class="font-semibold text-[#fca5a5] block mb-0.5">Binding Story Law:</span>
        <p class="text-[#fca5a5]/90 italic">Violations in scene drafts will be flagged for author review.</p>
      </div>
    `;
  }

  return `
    <div class="paper-card rounded-2xl p-5 flex flex-col justify-between border border-[#38312b] relative group">
      <div>
        <div class="flex items-start justify-between gap-2 mb-2.5">
          <div class="flex items-center">
            <span class="inline-flex items-center text-xs px-2.5 py-0.5 rounded-full font-medium ${meta.badgeClass}">
              ${meta.icon}
              ${meta.label}
            </span>
          </div>
          <div class="flex items-center space-x-1 opacity-70 group-hover:opacity-100 transition">
            <button onclick="openEditEntryModal('${e.id}')" title="Edit Entry" class="p-1.5 hover:bg-[#342d27] rounded-lg text-[#a4998c] hover:text-[#f6f2ec] transition">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
            </button>
            <button onclick="confirmDeleteEntry('${e.id}', '${escapeHtml(e.name)}')" title="Delete Entry" class="p-1.5 hover:bg-[#351c19] rounded-lg text-[#a4998c] hover:text-[#fca5a5] transition">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            </button>
          </div>
        </div>

        <h3 class="text-base font-story font-bold text-[#faf8f5] mb-1">${escapeHtml(e.name)}</h3>
        <p class="text-xs text-[#c9c1b5] leading-relaxed mb-3">${escapeHtml(e.description)}</p>
        
        ${extraFieldsHtml}
      </div>

      <div class="mt-4 pt-3 border-t border-[#342e28] flex flex-wrap gap-1.5 items-center">
        ${tagsHtml || '<span class="text-[11px] text-[#8c8275] italic">No tags</span>'}
      </div>
    </div>
  `;
}

// ============================================================================
// Feature 3: Ask Your Canon (Grounded Q&A)
// ============================================================================
function initializeChatGreeting() {
  state.chatHistory = [
    {
      role: 'assistant',
      text: "Welcome back to your writing desk. I am **Story AL**, the guardian memory of your fictional world. Ask me about your characters' goals, hazardous places, cataclysms, or world rules. I answer strictly from what you've saved in your Story Bible—and if a detail isn't written down yet, I will tell you clearly rather than making up answers.",
      citations: [],
      grounded: true,
      mode: 'lorekeeper'
    }
  ];
  renderChatMessages();
}

function renderSampleQuestions() {
  const container = document.getElementById('chat-sample-questions');
  if (!container) return;

  container.innerHTML = state.sampleQuestions.map(q => {
    return `
      <button onclick="askPresetQuestion('${escapeHtml(q.question)}')" class="text-left text-xs bg-[#241f1a] hover:bg-[#2e2721] border border-[#3e362e] hover:border-[#e5a953] text-[#c9c1b5] hover:text-[#faf8f5] px-3 py-2 rounded-xl transition group">
        <span class="block text-[10px] text-[#e5a953] font-story italic uppercase tracking-wider mb-0.5">${escapeHtml(q.type)}</span>
        <span class="font-medium">${escapeHtml(q.question)}</span>
      </button>
    `;
  }).join('');
}

function askPresetQuestion(text) {
  const input = document.getElementById('chat-input');
  if (input) {
    input.value = text;
    handleChatSubmit();
  }
}

async function handleChatSubmit() {
  const input = document.getElementById('chat-input');
  if (!input || state.isSubmittingChat) return;

  const question = input.value.trim();
  if (!question) return;

  input.value = '';
  state.isSubmittingChat = true;

  state.chatHistory.push({
    role: 'user',
    text: question
  });
  renderChatMessages();

  const chatMessagesContainer = document.getElementById('chat-messages');
  const tempThinkingId = `thinking-${Date.now()}`;
  const thinkingEl = document.createElement('div');
  thinkingEl.id = tempThinkingId;
  thinkingEl.className = 'flex items-start space-x-3 max-w-2xl mr-auto';
  thinkingEl.innerHTML = `
    <div class="w-8 h-8 rounded-xl bg-[#2e2319] border border-[#523e28] flex items-center justify-center text-[#e5a953] flex-shrink-0 text-xs font-story font-bold">
      LK
    </div>
    <div class="paper-panel p-4 rounded-2xl rounded-tl-none border border-[#38312b] text-sm text-[#a4998c] flex items-center space-x-2">
      <span class="w-2 h-2 rounded-full bg-[#e5a953] animate-pulse"></span>
      <span class="text-xs text-[#a4998c] pl-1">Consulting your Story Bible facts...</span>
    </div>
  `;
  chatMessagesContainer.appendChild(thinkingEl);
  chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });
    const data = await res.json();

    const thinkingNode = document.getElementById(tempThinkingId);
    if (thinkingNode) thinkingNode.remove();

    state.chatHistory.push({
      role: 'assistant',
      text: data.answer || 'No response returned.',
      citations: data.citations || [],
      grounded: data.grounded !== false,
      mode: data.mode || 'demo'
    });

    renderChatMessages();
  } catch (err) {
    console.error('Chat error:', err);
    const thinkingNode = document.getElementById(tempThinkingId);
    if (thinkingNode) thinkingNode.remove();

    state.chatHistory.push({
      role: 'assistant',
      text: "Unable to retrieve canon response right now. Please check your network or server logs.",
      citations: [],
      grounded: false,
      mode: 'error'
    });
    renderChatMessages();
  } finally {
    state.isSubmittingChat = false;
  }
}

function renderChatMessages() {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  container.innerHTML = state.chatHistory.map(msg => {
    if (msg.role === 'user') {
      return `
        <div class="flex items-start justify-end space-x-3 max-w-2xl ml-auto mb-4">
          <div class="bg-[#d96b43] text-white p-3.5 rounded-2xl rounded-tr-none text-sm leading-relaxed shadow-sm">
            ${escapeHtml(msg.text)}
          </div>
          <div class="w-8 h-8 rounded-xl bg-[#2a241f] border border-[#3e362e] flex items-center justify-center text-[#c9c1b5] flex-shrink-0 text-xs font-semibold">
            You
          </div>
        </div>
      `;
    } else {
      const modeBadge = msg.mode === 'live_ai' 
        ? `<span class="text-[10px] px-2 py-0.5 rounded-full bg-[#1b2820] text-[#aae0c3] border border-[#2b4434]">Gemini Grounded</span>`
        : `<span class="text-[10px] px-2 py-0.5 rounded-full bg-[#2d251c] text-[#fed99b] border border-[#4a3928]">Saved Canon Facts</span>`;

      const groundedBadge = msg.grounded === false
        ? `<span class="text-[10px] px-2 py-0.5 rounded-full bg-[#351c19] text-[#fca5a5] border border-[#522924] font-medium">Unspecified in Canon (No Hallucinations)</span>`
        : '';

      const citationsHtml = (msg.citations && msg.citations.length > 0)
        ? `
          <div class="mt-3 pt-2.5 border-t border-[#342e28]">
            <span class="text-[11px] text-[#a4998c] font-semibold uppercase tracking-wider block mb-1.5">Supporting Story Bible Canon:</span>
            <div class="flex flex-wrap gap-1.5">
              ${msg.citations.map(c => {
                const meta = CATEGORY_META[c.category] || CATEGORY_META.rule;
                return `
                  <button onclick="highlightCanonEntry('${c.id}')" class="inline-flex items-center text-xs px-2.5 py-0.5 rounded-full ${meta.badgeClass} hover:opacity-80 transition cursor-pointer" title="Click to view entry in Story Bible">
                    ${meta.icon}
                    ${escapeHtml(c.name)}
                  </button>
                `;
              }).join('')}
            </div>
          </div>
        ` : '';

      return `
        <div class="flex items-start space-x-3 max-w-2xl mr-auto mb-4">
          <div class="w-8 h-8 rounded-xl bg-[#2e2319] border border-[#523e28] flex items-center justify-center text-[#e5a953] flex-shrink-0 text-xs font-story font-bold">
            LK
          </div>
          <div class="paper-panel p-4 rounded-2xl rounded-tl-none border border-[#38312b] text-sm leading-relaxed text-[#ede8e1] shadow-sm flex-1">
            <div class="flex items-center space-x-2 mb-2">
              <span class="text-xs font-semibold text-[#e5a953]">Story AL</span>
              ${modeBadge}
              ${groundedBadge}
            </div>
            
            <div class="text-[#f6f2ec] leading-relaxed font-sans text-sm">
              ${formatMarkdownText(msg.text)}
            </div>

            ${citationsHtml}
          </div>
        </div>
      `;
    }
  }).join('');

  container.scrollTop = container.scrollHeight;
}

function clearChatHistory() {
  initializeChatGreeting();
}

function highlightCanonEntry(entryId) {
  switchView('story-bible');
  state.activeCategory = 'all';
  state.searchQuery = '';
  document.getElementById('bible-search-input').value = '';
  updateCategoryPills();
  renderStoryBible();

  setTimeout(() => {
    const entryEl = Array.from(document.querySelectorAll('#story-bible-entries .paper-card')).find(el => el.innerHTML.includes(entryId));
    if (entryEl) {
      entryEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      entryEl.classList.add('ring-2', 'ring-[#d96b43]');
      setTimeout(() => entryEl.classList.remove('ring-2', 'ring-[#d96b43]'), 2500);
    }
  }, 100);
}

// ============================================================================
// Feature 4: Check Draft for Conflicts
// ============================================================================
function renderSampleDraftButtons() {
  const container = document.getElementById('sample-draft-buttons');
  if (!container) return;

  container.innerHTML = state.sampleDrafts.map((d, idx) => {
    return `
      <button onclick="loadSampleDraft('${d.id}')" class="text-xs px-3 py-1.5 rounded-xl bg-[#241f1a] hover:bg-[#2e2721] border border-[#3e362e] hover:border-[#d96b43] text-[#c9c1b5] hover:text-white transition flex items-center space-x-1.5">
        <span class="w-2 h-2 rounded-full ${idx === 2 ? 'bg-[#589977]' : 'bg-[#e07a5f]'}"></span>
        <span class="font-medium">${escapeHtml(d.title.split(':')[0])}</span>
      </button>
    `;
  }).join('');
}

function loadSampleDraft(draftId) {
  const sample = state.sampleDrafts.find(d => d.id === draftId);
  if (!sample) return;

  const textarea = document.getElementById('continuity-draft-input');
  if (textarea) {
    textarea.value = sample.text;
    updateDraftWordCount();
    const resultsContainer = document.getElementById('continuity-results');
    if (resultsContainer) resultsContainer.classList.add('hidden');
  }
}

function clearDraftText() {
  const textarea = document.getElementById('continuity-draft-input');
  if (textarea) {
    textarea.value = '';
    updateDraftWordCount();
    const resultsContainer = document.getElementById('continuity-results');
    if (resultsContainer) resultsContainer.classList.add('hidden');
  }
}

function updateDraftWordCount() {
  const textarea = document.getElementById('continuity-draft-input');
  const countEl = document.getElementById('draft-word-count');
  if (!textarea || !countEl) return;

  const text = textarea.value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  const chars = text.length;
  countEl.textContent = `${words} words · ${chars} characters`;
}

async function runContinuityCheck() {
  const textarea = document.getElementById('continuity-draft-input');
  const draft = textarea ? textarea.value.trim() : '';

  if (!draft) {
    alert('Please enter or select a story draft scene to check.');
    return;
  }

  const runBtn = document.getElementById('btn-run-continuity');
  const resultsContainer = document.getElementById('continuity-results');
  if (runBtn) {
    runBtn.disabled = true;
    runBtn.innerHTML = `Checking Story Canon...`;
  }

  try {
    const res = await fetch('/api/continuity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ draft })
    });
    const data = await res.json();
    renderContinuityResults(data);
  } catch (err) {
    console.error('Continuity check failed:', err);
    alert('Continuity check failed. Please check server logs.');
  } finally {
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.innerHTML = `
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        Check Draft
      `;
    }
  }
}

function renderContinuityResults(result) {
  const container = document.getElementById('continuity-results');
  if (!container) return;

  container.classList.remove('hidden');

  const isClean = result.clean === true || (result.issues && result.issues.length === 0);
  const issues = result.issues || [];

  if (isClean) {
    container.innerHTML = `
      <div class="p-6 rounded-2xl bg-[#1c2921] border border-[#2e523e]">
        <div class="flex items-start space-x-3">
          <div class="w-9 h-9 rounded-xl bg-[#23382c] border border-[#3e684f] flex items-center justify-center text-[#aae0c3] flex-shrink-0">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
          </div>
          <div>
            <h3 class="text-base font-story font-bold text-[#aae0c3]">Canon Continuity Verified</h3>
            <p class="text-sm text-[#d8d0c5] mt-1">${escapeHtml(result.summary || 'No conflicts found against established rules, places, or character statuses.')}</p>
            <div class="mt-3 inline-flex items-center text-xs text-[#aae0c3] font-story italic bg-[#15221b] px-3 py-1 rounded-lg">
              0 conflicts flagged · This passage aligns with your Story Bible
            </div>
          </div>
        </div>
      </div>
    `;
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    return;
  }

  const issuesHtml = issues.map((issue, idx) => {
    const meta = CATEGORY_META[issue.canon_category] || CATEGORY_META.rule;

    return `
      <div class="paper-card rounded-2xl p-5 border border-[#522924] bg-[#221c1a] mb-4">
        <div class="flex items-start justify-between gap-2 mb-3">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full bg-[#351c19] text-[#fca5a5] border border-[#522924] text-xs font-bold flex items-center justify-center">
              ${idx + 1}
            </span>
            <span class="text-xs font-semibold uppercase tracking-wider text-[#e07a5f]">Potential Story Discrepancy</span>
          </div>
          <button onclick="highlightCanonEntry('${issue.canon_entry_id}')" class="inline-flex items-center text-xs px-2.5 py-1 rounded-full ${meta.badgeClass} hover:opacity-80 transition cursor-pointer" title="View in Story Bible">
            ${meta.icon}
            Conflicting: ${escapeHtml(issue.canon_name)}
          </button>
        </div>

        <div class="mb-3">
          <span class="text-xs text-[#a4998c] font-semibold block mb-1">Passage Under Review:</span>
          <div class="draft-conflict-box text-sm">
            "${escapeHtml(issue.draft_excerpt)}"
          </div>
        </div>

        <div class="mb-3 text-xs leading-relaxed text-[#e2dad2] bg-[#1a1614] p-3 rounded-xl border border-[#342e28]">
          <span class="font-semibold text-[#fca5a5] block mb-0.5">Why this contradicts established canon:</span>
          <p class="text-[#e2dad2]">${escapeHtml(issue.explanation)}</p>
        </div>

        <div class="text-xs leading-relaxed bg-[#2b221a] p-3 rounded-xl border border-[#4a3928]">
          <span class="font-semibold text-[#e5a953] block mb-0.5">Suggestion for the Author:</span>
          <p class="text-[#fed99b]">${escapeHtml(issue.suggestion)}</p>
        </div>
      </div>
    `;
  }).join('');

  container.innerHTML = `
    <div class="p-4 rounded-2xl bg-[#351c19] border border-[#522924] mb-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-xl bg-[#4a2420] border border-[#6b352f] text-[#fca5a5] flex items-center justify-center font-bold text-sm">
          !
        </div>
        <div>
          <h3 class="text-sm font-bold text-[#fca5a5]">${issues.length} Potential Discrepanc${issues.length > 1 ? 'ies' : 'y'} Flagged</h3>
          <p class="text-xs text-[#fed99b]/80">These are friendly review suggestions to help keep your story rules consistent.</p>
        </div>
      </div>
      <span class="text-[11px] text-[#fed99b] px-2.5 py-1 bg-[#231513] rounded-lg border border-[#44231f]">
        ${result.mode === 'live_ai' ? 'Gemini AI Review' : 'Canon Rule Checker'}
      </span>
    </div>
    <div class="space-y-3">
      ${issuesHtml}
    </div>
  `;

  container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================================================
// Feature 5: Next-Scene Suggestions & Draft Notes
// ============================================================================
async function generateNextScenes() {
  const charSelect = document.getElementById('next-scene-char-select');
  const sitInput = document.getElementById('next-scene-situation-input');
  const character = charSelect ? charSelect.value : 'Lyra Vance';
  const situation = sitInput ? sitInput.value.trim() : '';

  const genBtn = document.getElementById('btn-generate-scenes');
  if (genBtn) {
    genBtn.disabled = true;
    genBtn.innerHTML = 'Thinking of ideas...';
  }

  try {
    const res = await fetch('/api/next_scene', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ character, situation })
    });
    const data = await res.json();
    renderNextSceneCards(data.scenes || [], character);
  } catch (err) {
    console.error('Failed to generate scenes:', err);
    alert('Failed to generate scene ideas. Please try again.');
  } finally {
    if (genBtn) {
      genBtn.disabled = false;
      genBtn.innerHTML = `
        <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
        Generate 3 Ideas
      `;
    }
  }
}

function renderNextSceneCards(scenes, character) {
  const container = document.getElementById('next-scene-cards');
  if (!container) return;

  if (scenes.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-12 text-center text-[#a4998c] bg-[#1e1b18] rounded-2xl border border-[#38312b]">
        <p class="text-sm font-story">Click 'Generate 3 Ideas' above to explore directions for ${escapeHtml(character)}.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = scenes.map(s => {
    return `
      <div class="paper-card rounded-2xl p-5 border border-[#443a30] flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-[11px] px-2.5 py-0.5 rounded-full font-medium ${s.type && s.type.includes('Action') ? 'badge-rule' : (s.type && s.type.includes('Lore') ? 'badge-event' : 'badge-character')}">
              ${escapeHtml(s.type || 'Scene Direction')}
            </span>
            <span class="text-[10px] text-[#e5a953] italic">Draft Idea · Non-Canon</span>
          </div>

          <h4 class="text-base font-story font-bold text-[#faf8f5] mb-1.5">${escapeHtml(s.title)}</h4>
          <p class="text-xs text-[#e2dad2] leading-relaxed mb-3">${escapeHtml(s.what_happens)}</p>

          <div class="p-2.5 rounded-xl bg-[#1b1715] border border-[#342e28] text-xs">
            <span class="font-semibold text-[#e5a953] block mb-0.5">Why it fits your story:</span>
            <p class="text-[#a4998c]">${escapeHtml(s.why_it_fits)}</p>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-[#342e28] flex items-center justify-between">
          <button onclick="copySceneToClipboard('${escapeHtml(s.title)}', '${escapeHtml(s.what_happens)}')" class="text-xs text-[#a4998c] hover:text-[#faf8f5] transition flex items-center">
            <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
            Copy Text
          </button>
          <button onclick="saveSceneToNotes('${escapeHtml(s.title)}', '${escapeHtml(s.what_happens)}', '${escapeHtml(character)}', '${escapeHtml(s.why_it_fits)}')" class="px-3 py-1.5 bg-[#d96b43] hover:bg-[#c45a33] text-white rounded-lg text-xs font-medium transition flex items-center">
            Save to Notes
          </button>
        </div>
      </div>
    `;
  }).join('');
}

async function saveSceneToNotes(title, text, character, why_it_fits) {
  try {
    const res = await fetch('/api/notes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        text,
        character,
        why_it_fits,
        category: 'Scene Idea'
      })
    });
    const data = await res.json();
    state.notes = data.notes || [];
    renderDraftNotes();
    alert(`"${title}" saved to your Draft Notes notebook.`);
  } catch (err) {
    alert('Failed to save note: ' + err.message);
  }
}

function copySceneToClipboard(title, text) {
  const content = `${title}\n\n${text}`;
  navigator.clipboard.writeText(content).then(() => {
    alert('Copied scene text to clipboard!');
  }).catch(() => {
    alert('Unable to copy automatically.');
  });
}

function renderDraftNotes() {
  const container = document.getElementById('saved-notes-container');
  const countBadge = document.getElementById('saved-notes-count-badge');
  if (!container) return;

  if (countBadge) {
    countBadge.textContent = `${state.notes.length} note${state.notes.length === 1 ? '' : 's'} saved`;
  }

  if (state.notes.length === 0) {
    container.innerHTML = `
      <div class="py-8 text-center text-[#8c8275] italic font-story text-sm">
        No draft notes saved yet. Click 'Save to Notes' on any scene idea to keep it here.
      </div>
    `;
    return;
  }

  container.innerHTML = state.notes.map(n => {
    return `
      <div class="p-3.5 rounded-xl bg-[#231e1a] border border-[#38312b] flex items-start justify-between gap-4">
        <div>
          <div class="flex items-center space-x-2 mb-1">
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-[#352a1e] text-[#fed99b] border border-[#594228] font-story italic">${escapeHtml(n.category || 'Draft Idea')}</span>
            <span class="text-xs text-[#f3c9d7] font-medium">${escapeHtml(n.character || 'General')}</span>
            <span class="text-[11px] text-[#8c8275]">• ${escapeHtml(n.created_at || 'Saved')}</span>
          </div>
          <h4 class="text-sm font-semibold text-[#f5ede0] mb-1">${escapeHtml(n.title)}</h4>
          <p class="text-xs text-[#c9c1b5] leading-relaxed font-story text-sm">${escapeHtml(n.text)}</p>
          ${n.why_it_fits ? `<p class="text-[11px] text-[#e5a953] mt-1 italic">Why it fits: ${escapeHtml(n.why_it_fits)}</p>` : ''}
        </div>
        <button onclick="deleteDraftNote('${n.id}')" title="Remove note" class="p-1 hover:bg-[#351c19] text-[#8c8275] hover:text-[#fca5a5] rounded-lg transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
        </button>
      </div>
    `;
  }).join('');
}

async function deleteDraftNote(noteId) {
  if (!confirm('Remove this note from your notebook?')) return;
  try {
    const res = await fetch(`/api/notes/${noteId}`, { method: 'DELETE' });
    const data = await res.json();
    state.notes = data.notes || [];
    renderDraftNotes();
  } catch (err) {
    alert('Failed to delete note: ' + err.message);
  }
}

// ============================================================================
// Feature 6: Voice Studio (ElevenLabs Storyteller AI Voices Voice Library)
// ============================================================================

// Emotion Detection & Badge Helper (Global Scope)
function getEmotionBadge(delivery) {
  const d = (delivery || '').toLowerCase();
  if (d.includes('whisper') || d.includes('secret') || (d.includes('hushed') && !d.includes('story'))) {
    return '🤫 Tense Whisper';
  }
  if (d.includes('fierce') || d.includes('warning') || d.includes('urgent') || d.includes('danger') || d.includes('sharp')) {
    return '🔥 Fierce Warning';
  }
  if (d.includes('sardonic') || d.includes('rasp') || d.includes('grin') || d.includes('drawl') || d.includes('smuggler')) {
    return '😏 Sardonic Rasp';
  }
  if (d.includes('solemn') || d.includes('ancient') || d.includes('grave') || d.includes('curator')) {
    return '📜 Solemn Elder';
  }
  return '🎭 Atmospheric Storyteller';
}

function applyEmotionPreset(speakerKey, presetTone) {
  const input = document.getElementById(`delivery-input-${speakerKey}`);
  if (input) input.value = presetTone;
  updateDeliveryNote(speakerKey, presetTone);
}

function setExpressiveness(level) {
  state.expressiveness = Math.round(level * 100) / 100;

  // Sync range slider if needed
  const slider = document.getElementById('emotion-slider');
  if (slider && Math.abs(parseFloat(slider.value) - state.expressiveness) > 0.01) {
    slider.value = state.expressiveness;
  }

  // Determine emotional tier & icon
  let tierLabel = 'Dramatic';
  let tierIcon = '🎭';
  if (state.expressiveness <= 0.40) {
    tierLabel = 'Calm';
    tierIcon = '🍃';
  } else if (state.expressiveness <= 0.65) {
    tierLabel = 'Subtle';
    tierIcon = '💬';
  } else if (state.expressiveness <= 0.85) {
    tierLabel = 'Dramatic';
    tierIcon = '🎭';
  } else if (state.expressiveness <= 0.95) {
    tierLabel = 'Intense';
    tierIcon = '⚡';
  } else {
    tierLabel = 'Fever Pitch';
    tierIcon = '🔥';
  }

  const pct = Math.round(state.expressiveness * 100);
  const labelEl = document.getElementById('emotion-level-label');
  if (labelEl) {
    labelEl.textContent = `${tierIcon} ${tierLabel} (${pct}%)`;
  }

  // Update preset pill styles
  ['035', '055', '075', '095'].forEach(id => {
    const btn = document.getElementById(`btn-express-${id}`);
    if (btn) {
      const btnVal = parseFloat(id) / 100;
      if (Math.abs(state.expressiveness - btnVal) <= 0.10) {
        btn.className = 'text-[10px] px-2 py-0.5 rounded-lg bg-[#d96b43] text-white font-semibold transition shadow-sm';
      } else {
        btn.className = 'text-[10px] px-2 py-0.5 rounded-lg text-[#a4998c] hover:text-white transition';
      }
    }
  });

  const statusEl = document.getElementById('audio-current-status-text');
  if (statusEl) {
    statusEl.textContent = `— Emotion Level adjusted to ${pct}% [${tierLabel}]. Click "Audition Level" or play the scene.`;
  }
}

async function auditionCurrentEmotion() {
  stopAudioScene();
  stopAllVoicePreviews();

  const scene = state.audioScene || {};
  const activeChar = 'Lyra Vance';
  const voiceId = scene.characters?.[activeChar]?.voice_id || '21m00Tcm4TlvDq8ikWAM';
  const delivery = scene.characters?.[activeChar]?.tone || 'Tense whisper, cautious and urgent';

  const statusEl = document.getElementById('audio-current-status-text');
  const speakerEl = document.getElementById('audio-current-speaker');
  const moodTag = document.getElementById('audio-active-mood-tag');

  const pct = Math.round(state.expressiveness * 100);
  if (speakerEl) speakerEl.textContent = `Auditioning Emotion: ${pct}%`;
  if (moodTag) {
    moodTag.textContent = `${pct}% Emotion`;
    moodTag.classList.remove('hidden');
  }
  if (statusEl) statusEl.textContent = `— Synthesizing line at ${pct}% emotional expressiveness...`;

  try {
    const res = await fetch('/api/audio/synthesize_line', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: "The pressure seals are trembling... listen to the hull, we cannot stay here!",
        voice_id: voiceId,
        rate: 1.0,
        pitch: 1.0,
        delivery: delivery,
        expressiveness: state.expressiveness
      })
    });
    const data = await res.json();
    const audioEl = document.getElementById('lore-audio-element');
    if (data.audio_url && audioEl) {
      if (statusEl) statusEl.textContent = `— [${data.emotion_label || 'Emotional'}] Performed at ${pct}% Expressiveness`;
      audioEl.src = data.audio_url;
      audioEl.volume = 1.0;
      audioEl.play().catch(e => console.warn('Audition play error:', e));
      audioEl.onended = () => {
        stopSmoothWaveVisualizer();
        updateSmoothAudioProgress();
        if (speakerEl) speakerEl.textContent = 'Ready';
        if (moodTag) moodTag.classList.add('hidden');
        if (statusEl) statusEl.textContent = '— Press "Play Full Scene" or play individual lines below';
      };
    }
  } catch (err) {
    console.error('Emotion audition error:', err);
    if (statusEl) statusEl.textContent = `— Error: ${err.message}`;
  }
}

function renderAudioStudio() {
  const scene = state.audioScene;
  if (!scene) return;

  // Update Dynamic Scene Title & Location
  const titleEl = document.getElementById('audio-scene-title');
  if (titleEl && scene.title) titleEl.textContent = scene.title;
  const locEl = document.getElementById('audio-scene-location');
  if (locEl && scene.location) locEl.textContent = scene.location;

  // Render Studio Engine Status Badge
  const engineBadge = document.getElementById('audio-engine-badge');
  if (engineBadge) {
    engineBadge.innerHTML = `
      <span class="text-xs px-3 py-1.5 rounded-full bg-[#1b251e] text-[#aae0c3] border border-[#2b3a30] font-medium flex items-center shadow-sm">
        <span class="w-1.5 h-1.5 rounded-full bg-[#4ade80] mr-1.5"></span>
        Voice Studio Ready
      </span>
    `;
  }

  // Get Storyteller voices
  const voices = Array.isArray(state.voiceCatalog) 
    ? state.voiceCatalog 
    : (state.audioStatus?.voices || []);

// Render Casting Grid with Character Crests and Dynamic Equalizers
  const castingGrid = document.getElementById('audio-casting-grid');
  if (castingGrid) {
    const chars = [
      {
        name: 'Narrator',
        avatar: '🎙️',
        subtitle: 'The World Chronicler',
        role: 'Atmospheric Storyteller',
        voiceId: scene.narrator_voice?.voice_id || 'JBFqnCBsd6RMkjVDRZzb',
        tone: scene.narrator_voice?.tone || 'Warm, measured, and atmospheric British storytelling',
        key: 'narrator',
        accentBadge: 'badge-audio',
        cardBorder: 'hover:border-[#e5a953]',
        presets: [
          'Hushed storytelling',
          'Solemn chronicle',
          'Dramatic suspense'
        ]
      },
      {
        name: 'Lyra Vance',
        avatar: '📜',
        subtitle: 'Aether-Cartographer',
        role: 'Exiled Cartographer & Scholar',
        voiceId: scene.characters?.['Lyra Vance']?.voice_id || '21m00Tcm4TlvDq8ikWAM',
        tone: scene.characters?.['Lyra Vance']?.tone || 'Tense whisper, urgent and cautious',
        key: 'Lyra Vance',
        accentBadge: 'badge-character',
        cardBorder: 'hover:border-[#f43f5e]',
        presets: [
          'Tense whisper, cautious',
          'Fierce warning, sharp',
          'Curious scholar'
        ]
      },
      {
        name: 'Captain Kaelen',
        avatar: '⚓',
        subtitle: 'Deep-Water Smuggler',
        role: 'Deep-Water Sky-Smuggler',
        voiceId: scene.characters?.['Captain Kaelen']?.voice_id || 'N2lVS1w4EtoT3dr4eOWO',
        tone: scene.characters?.['Captain Kaelen']?.tone || 'Dry, low rasp with quiet confidence',
        key: 'Captain Kaelen',
        accentBadge: 'badge-place',
        cardBorder: 'hover:border-[#10b981]',
        presets: [
          'Dry, casual rasp',
          'Low sardonic grin',
          'Gravelly smuggler'
        ]
      }
    ];

    castingGrid.innerHTML = chars.map(c => {
      // Find current voice meta
      const currentVoice = voices.find(v => v.id === c.voiceId) || voices[0] || {};

      const voiceOptionsHtml = voices.map(v => {
        const isSelected = v.id === c.voiceId ? 'selected' : '';
        return `<option value="${escapeHtml(v.id)}" ${isSelected}>${escapeHtml(v.name)} [${escapeHtml(v.accent || '')}]</option>`;
      }).join('');

      return `
        <div id="cast-card-${escapeHtml(c.key)}" class="p-4 rounded-xl bg-[#211b17] border border-[#383028] space-y-3 transition-craft ${c.cardBorder} relative overflow-hidden group shadow-md">
          <div class="flex items-center justify-between pb-2 border-b border-[#2d251f]">
            <div class="flex items-center space-x-2.5">
              <div class="w-8 h-8 rounded-lg bg-[#2c221a] flex items-center justify-center text-base border border-[#443528] shadow-inner">
                ${c.avatar}
              </div>
              <div>
                <div class="flex items-center space-x-1.5">
                  <span class="text-xs font-bold text-[#faf8f5]">${escapeHtml(c.name)}</span>
                  <div id="char-speaker-pulse-${escapeHtml(c.key)}" class="hidden flex items-end space-x-0.5 h-3" title="Speaking now">
                    <span class="w-0.5 h-2 bg-[#e5a953] animate-pulse"></span>
                    <span class="w-0.5 h-3 bg-[#e5a953] animate-pulse"></span>
                    <span class="w-0.5 h-1.5 bg-[#e5a953] animate-pulse"></span>
                  </div>
                </div>
                <div class="text-[10px] text-[#e5a953] font-medium">${escapeHtml(c.subtitle)}</div>
              </div>
            </div>
            <button onclick="previewSpeakerVoice('${escapeHtml(c.key)}')" title="Audition voice sample" class="text-[11px] px-2.5 py-1 rounded-lg bg-[#301c22] hover:bg-[#42222d] text-[#fca5a5] hover:text-white border border-[#5c2836] transition flex items-center shadow-sm">
              <svg class="w-3 h-3 mr-1 text-[#f87171]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path></svg>
              Audition
            </button>
          </div>

          <div>
            <label class="block text-[10px] font-semibold text-[#fca5a5] uppercase tracking-wider mb-1 flex items-center justify-between">
              <span>Character Voice</span>
              <span class="text-[9px] text-[#8c8275] font-normal normal-case">${escapeHtml(currentVoice.archetype || '')}</span>
            </label>
            <select onchange="updateSpeakerVoice('${escapeHtml(c.key)}', this.value)" class="w-full text-xs bg-[#171311] border border-[#3e322d] rounded-lg px-2.5 py-1.5 text-[#ede8e1] focus:outline-none focus:border-[#f87171]">
              ${voiceOptionsHtml}
            </select>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="block text-[10px] font-semibold text-[#8c8275] uppercase tracking-wider">Delivery & Emotion</label>
              <span class="text-[9px] text-[#fca5a5] italic">${getEmotionBadge(c.tone)}</span>
            </div>
            <input type="text" id="delivery-input-${escapeHtml(c.key)}" value="${escapeHtml(c.tone)}" onchange="updateDeliveryNote('${escapeHtml(c.key)}', this.value)" class="w-full text-xs bg-[#171311] border border-[#38312b] rounded-lg px-2.5 py-1.5 text-[#ede8e1] focus:outline-none focus:border-[#d96b43]" placeholder="e.g. Hushed whisper, urgent and cautious">
            
            <div class="flex flex-wrap items-center gap-1 mt-2">
              <span class="text-[9px] text-[#786c5f] uppercase tracking-wider mr-1">Presets:</span>
              ${c.presets.map(p => `
                <button type="button" onclick="applyEmotionPreset('${escapeHtml(c.key)}', '${escapeHtml(p)}')" class="text-[10px] px-2 py-0.5 rounded bg-[#2a221d] hover:bg-[#3d2f25] text-[#fed99b] border border-[#4a392b] transition shadow-sm">
                  ${escapeHtml(p)}
                </button>
              `).join('')}
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Render Script Lines with Screenplay Cards & Real-Time Tracking
  const scriptContainer = document.getElementById('audio-script-lines');
  if (scriptContainer && scene.lines) {
    scriptContainer.innerHTML = scene.lines.map((line, idx) => {
      const isNarrator = line.speaker === 'Narrator';
      const isLyra = line.speaker.includes('Lyra');
      const avatar = isNarrator ? '🎙️' : (isLyra ? '📜' : '⚓');
      const speakerBadgeClass = isNarrator ? 'badge-audio' : (isLyra ? 'badge-character' : 'badge-place');
      const emotionBadge = getEmotionBadge(line.delivery);

      return `
        <div id="audio-line-${idx}" class="p-4 rounded-xl bg-[#211b17] border border-[#383028] transition-craft flex items-start justify-between gap-4 hover:border-[#4d3f32] shadow-sm relative group">
          <div class="flex-1">
            <div class="flex items-center space-x-2 mb-2 flex-wrap gap-y-1">
              <span class="text-[11px] px-2.5 py-0.5 rounded-full font-semibold ${speakerBadgeClass} flex items-center shadow-sm">
                <span class="mr-1">${avatar}</span>
                ${escapeHtml(line.speaker)}
              </span>
              <span class="text-[10px] px-2 py-0.5 rounded-md bg-[#2d1b22] text-[#fca5a5] border border-[#4a2632] font-semibold">${emotionBadge}</span>
              <span class="text-[11px] text-[#8c8275] italic">"${escapeHtml(line.delivery)}"</span>
            </div>
            <p class="text-sm text-[#f6f2ec] font-story text-base leading-relaxed tracking-wide">
              ${escapeHtml(line.text)}
            </p>
          </div>
          <button id="btn-line-${idx}" onclick="playSingleLine(${idx})" class="flex-shrink-0 text-xs px-3.5 py-2 bg-[#2a1e22] hover:bg-[#38262d] text-[#fca5a5] hover:text-white rounded-xl transition border border-[#4d2834] flex items-center shadow-sm transform hover:-translate-y-0.5 active:translate-y-0">
            <svg class="w-3.5 h-3.5 mr-1.5 text-[#f87171]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path></svg>
            Play Line
          </button>
        </div>
      `;
    }).join('');
  }

  // Render All 16 Voices Showcase Gallery
  renderVoiceShowcase();

  // Render Multi-Segmented Scene Timeline & Clock
  renderSceneSegments();
  updateSceneDurationDisplay();
}

// ============================================================================
// Smooth Audio Master & Dynamic Web Audio Equalizer (Studio Polish)
// ============================================================================
let smoothAudioCtx = null;
let smoothGainNode = null;
let smoothCompressor = null;
let smoothAnalyser = null;
let smoothVisualizerId = null;
let isSmoothAudioHooked = false;

function initSmoothAudioEngine() {
  if (isSmoothAudioHooked) return;
  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl) return;

  // Scrubber, time & visualizer event listeners on native audio element
  audioEl.addEventListener('play', () => {
    startSmoothWaveVisualizer();
  });

  audioEl.addEventListener('pause', () => {
    stopSmoothWaveVisualizer();
  });

  audioEl.addEventListener('ended', () => {
    stopSmoothWaveVisualizer();
  });

  audioEl.addEventListener('timeupdate', () => {
    updateSmoothAudioProgress();
  });

  audioEl.addEventListener('loadedmetadata', () => {
    updateSmoothAudioDuration();
  });

  isSmoothAudioHooked = true;
}

function formatAudioTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function updateSmoothAudioProgress() {
  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl) return;
  const current = audioEl.currentTime || 0;
  const duration = audioEl.duration || 0;

  const curEl = document.getElementById('audio-time-current');
  if (curEl) curEl.textContent = formatAudioTime(current);

  const fillEl = document.getElementById('audio-scrubber-fill');
  if (fillEl && duration > 0) {
    const pct = (current / duration) * 100;
    fillEl.style.width = `${Math.min(100, Math.max(0, pct))}%`;
  }
}

function updateSmoothAudioDuration() {
  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl) return;
  const totalEl = document.getElementById('audio-time-total');
  if (totalEl && audioEl.duration) {
    totalEl.textContent = formatAudioTime(audioEl.duration);
  }
}

function seekAudioProgress(e) {
  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl || !audioEl.duration) return;

  const track = document.getElementById('audio-scrubber-track');
  if (!track) return;

  const rect = track.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const pct = Math.max(0, Math.min(1, clickX / rect.width));
  audioEl.currentTime = pct * audioEl.duration;
  updateSmoothAudioProgress();
}

function smoothFadeIn(targetGain = 1.0, durationMs = 40) {
  const audioEl = document.getElementById('lore-audio-element');
  if (audioEl) {
    audioEl.volume = Math.max(0.1, Math.min(1.0, targetGain));
  }
}

function smoothFadeOut(durationMs = 40) {
  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl) return Promise.resolve();
  audioEl.volume = 1.0;
  return Promise.resolve();
}

function startSmoothWaveVisualizer() {
  const waveContainer = document.getElementById('audio-wave-anim');
  if (waveContainer) waveContainer.classList.add('wave-animating');

  const canvas = document.getElementById('audio-wave-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  if (smoothVisualizerId) {
    cancelAnimationFrame(smoothVisualizerId);
    smoothVisualizerId = null;
  }

  const bufferLength = smoothAnalyser ? smoothAnalyser.frequencyBinCount : 32;
  const dataArray = new Uint8Array(bufferLength);

  function renderWave() {
    smoothVisualizerId = requestAnimationFrame(renderWave);
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    if (smoothAnalyser) {
      smoothAnalyser.getByteFrequencyData(dataArray);
    } else {
      for (let i = 0; i < bufferLength; i++) {
        dataArray[i] = Math.floor(70 + Math.sin(Date.now() / 150 + i) * 50);
      }
    }

    const numBars = Math.min(24, bufferLength / 2);
    const barWidth = Math.floor(width / numBars) - 1.5;
    let x = 2;

    for (let i = 0; i < numBars; i++) {
      const val = dataArray[i] || 0;
      const barHeight = Math.max(3, (val / 255) * (height - 3));
      
      const grad = ctx.createLinearGradient(0, height, 0, 0);
      grad.addColorStop(0, '#d96b43');
      grad.addColorStop(1, '#e5a953');
      ctx.fillStyle = grad;

      ctx.beginPath();
      if (ctx.roundRect) {
        ctx.roundRect(x, height - barHeight, Math.max(2, barWidth), barHeight, [2, 2, 0, 0]);
      } else {
        ctx.rect(x, height - barHeight, Math.max(2, barWidth), barHeight);
      }
      ctx.fill();
      x += barWidth + 2;
    }
  }

  renderWave();
}

function stopSmoothWaveVisualizer() {
  const waveContainer = document.getElementById('audio-wave-anim');
  if (waveContainer) waveContainer.classList.remove('wave-animating');

  if (smoothVisualizerId) {
    cancelAnimationFrame(smoothVisualizerId);
    smoothVisualizerId = null;
  }

  const canvas = document.getElementById('audio-wave-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

function cleanVoiceName(name) {
  if (!name) return 'Story Voice';
  return name.replace(/\s*\(\s*ElevenLabs\s*\)/gi, '').replace(/\s*\(Official\s*ElevenLabs\)/gi, '').trim();
}

// ============================================================================
// Storyteller Voice Showcase Gallery (All 16 Voices)
// ============================================================================
function renderVoiceShowcase() {
  const container = document.getElementById('all-voices-showcase-grid');
  if (!container) return;

  const voices = Array.isArray(state.voiceCatalog) ? state.voiceCatalog : (state.audioStatus?.voices || []);
  if (!voices || !voices.length) {
    container.innerHTML = '<p class="text-xs text-[#8c8275] italic col-span-4 p-4 text-center">Loading voice catalog...</p>';
    return;
  }

  const filter = state.voiceFilter || 'all';
  const filtered = voices.filter(v => {
    if (filter === 'all') return true;
    if (filter === 'male') return v.gender === 'male';
    if (filter === 'female') return v.gender === 'female';
    if (filter === 'british') return (v.accent || '').toLowerCase().includes('british');
    if (filter === 'american') return (v.accent || '').toLowerCase().includes('american');
    return true;
  });

  container.innerHTML = filtered.map(v => {
    const isPlaying = state.currentShowcasePlayingVoiceId === v.id;
    const accentShort = (v.accent || 'Natural').split('(')[0].trim();
    const cleanName = v.name.includes('—') ? v.name.split('—')[0].trim() : v.name;
    const subtitle = v.name.includes('—') ? v.name.split('—')[1].trim() : (v.archetype || '');

    return `
      <div id="voice-card-${escapeHtml(v.id)}" class="p-3.5 rounded-xl bg-[#231e1a] border ${isPlaying ? 'border-[#f87171] ring-2 ring-[#f87171]/40 bg-[#2d1b22] shadow-lg shadow-[#f87171]/10' : 'border-[#38312b]'} voice-card-smooth hover:border-[#522934] flex flex-col justify-between space-y-3 relative group">
        <div>
          <div class="flex items-start justify-between gap-1 mb-1">
            <span class="text-xs font-bold text-[#faf8f5] leading-tight group-hover:text-[#fca5a5] transition flex items-center">
              ${isPlaying ? '<span class="w-2 h-2 rounded-full bg-[#f87171] animate-ping mr-1.5 inline-block"></span>' : ''}
              ${escapeHtml(cleanName)}
            </span>
            <span class="text-[9px] px-2 py-0.5 rounded-full bg-[#1b1714] text-[#a4998c] border border-[#3e342c] font-medium whitespace-nowrap">${escapeHtml(accentShort)}</span>
          </div>
          <div class="text-[10px] text-[#e5a953] font-medium leading-snug">${escapeHtml(subtitle)}</div>
          <p class="text-[11px] text-[#a4998c] leading-relaxed mt-1.5 line-clamp-2" title="${escapeHtml(v.tone)}">
            ${escapeHtml(v.tone)}
          </p>
        </div>

        <div class="pt-2 border-t border-[#2e2620] space-y-2">
          <button id="btn-showcase-preview-${escapeHtml(v.id)}" onclick="previewSingleVoiceShowcase('${escapeHtml(v.id)}')" class="w-full py-1.5 px-2.5 ${isPlaying ? 'bg-[#4a1f2c] text-white border-[#f87171]' : 'bg-[#2d1f24] hover:bg-[#3d262e] text-[#fca5a5] hover:text-white border-[#522934]'} rounded-lg text-xs font-medium transition border flex items-center justify-center shadow-sm">
            ${isPlaying ? `
              <svg class="w-3.5 h-3.5 mr-1.5 text-white animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
              <span>Auditioning...</span>
            ` : `
              <svg class="w-3.5 h-3.5 mr-1.5 text-[#f87171]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path></svg>
              <span>Audition Voice</span>
            `}
          </button>
          
          <div class="flex items-center justify-between text-[10px] text-[#786c5f]">
            <span class="uppercase tracking-wider">Cast To:</span>
            <div class="flex items-center space-x-1">
              <button type="button" onclick="castVoiceFromShowcase('narrator', '${escapeHtml(v.id)}')" title="Cast as Narrator" class="px-1.5 py-0.5 rounded bg-[#1a1614] hover:bg-[#35251e] text-[#fed99b] hover:text-white transition border border-[#342921]">Narrator</button>
              <button type="button" onclick="castVoiceFromShowcase('Lyra Vance', '${escapeHtml(v.id)}')" title="Cast as Lyra Vance" class="px-1.5 py-0.5 rounded bg-[#1a1614] hover:bg-[#35251e] text-[#f3c9d7] hover:text-white transition border border-[#342921]">Lyra</button>
              <button type="button" onclick="castVoiceFromShowcase('Captain Kaelen', '${escapeHtml(v.id)}')" title="Cast as Captain Kaelen" class="px-1.5 py-0.5 rounded bg-[#1a1614] hover:bg-[#35251e] text-[#aae0c3] hover:text-white transition border border-[#342921]">Kaelen</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function filterVoiceShowcase(type) {
  state.voiceFilter = type;
  ['all', 'male', 'female', 'british', 'american'].forEach(f => {
    const btn = document.getElementById(`vfilter-${f}`);
    if (btn) {
      if (f === type) {
        btn.className = 'px-2.5 py-1 rounded-lg bg-[#3d2f25] text-[#fed99b] border border-[#594228] transition font-medium';
      } else {
        btn.className = 'px-2.5 py-1 rounded-lg bg-[#25201b] text-[#a4998c] hover:text-[#ede8e1] border border-[#38312b] transition font-medium';
      }
    }
  });
  renderVoiceShowcase();
}

async function castVoiceFromShowcase(charKey, voiceId) {
  await updateSpeakerVoice(charKey, voiceId);
  const voices = Array.isArray(state.voiceCatalog) ? state.voiceCatalog : (state.audioStatus?.voices || []);
  const voiceObj = voices.find(v => v.id === voiceId);
  const statusEl = document.getElementById('audio-current-status-text');
  if (statusEl && voiceObj) {
    statusEl.textContent = `— Assigned ${voiceObj.name} to ${charKey}`;
  }
}

async function previewSingleVoiceShowcase(voiceId) {
  stopAllVoicePreviews();
  await stopAudioScene();

  const voices = Array.isArray(state.voiceCatalog) ? state.voiceCatalog : (state.audioStatus?.voices || []);
  const voiceObj = voices.find(v => v.id === voiceId) || {};

  state.currentShowcasePlayingVoiceId = voiceId;
  renderVoiceShowcase();

  const audioEl = document.getElementById('lore-audio-element');
  const speakerEl = document.getElementById('audio-current-speaker');
  const statusEl = document.getElementById('audio-current-status-text');
  const moodTag = document.getElementById('audio-active-mood-tag');

  if (speakerEl) speakerEl.textContent = `Auditioning: ${voiceObj.name || voiceId}`;
  if (moodTag) {
    moodTag.textContent = voiceObj.accent || 'Natural';
    moodTag.classList.remove('hidden');
  }
  if (statusEl) statusEl.textContent = `— Voice Sample [${voiceObj.archetype || 'Voice'}]`;

  const resetUI = () => {
    state.currentShowcasePlayingVoiceId = null;
    renderVoiceShowcase();
    stopSmoothWaveVisualizer();
    updateSmoothAudioProgress();
    if (speakerEl) speakerEl.textContent = 'Ready';
    if (moodTag) moodTag.classList.add('hidden');
    if (statusEl) statusEl.textContent = '— Press "Play Full Scene" or audition voices below';
  };

  const localUrl = `/static/audio_cache/preview_${voiceId}.mp3`;
  if (audioEl) {
    smoothFadeIn(1.0, 50);
    audioEl.src = localUrl;
    audioEl.play().catch(async (e) => {
      console.warn('Local preview playback issue, trying API:', e);
      try {
        const res = await fetch(`/api/audio/preview/${voiceId}`);
        const data = await res.json();
        if (data.audio_url && audioEl) {
          smoothFadeIn(1.0, 50);
          audioEl.src = data.audio_url;
          audioEl.play().catch(err => resetUI());
        } else {
          resetUI();
        }
      } catch (err) {
        resetUI();
      }
    });
    audioEl.onended = resetUI;
    audioEl.onerror = async () => {
      try {
        const res = await fetch(`/api/audio/preview/${voiceId}`);
        const data = await res.json();
        if (data.audio_url && audioEl) {
          smoothFadeIn(1.0, 50);
          audioEl.src = data.audio_url;
          audioEl.play().catch(err => resetUI());
        } else {
          resetUI();
        }
      } catch (err) {
        resetUI();
      }
    };
  }
}

function playAllVoicePreviews() {
  if (state.isAllVoicesPreviewing) {
    stopAllVoicePreviews();
    return;
  }

  stopAudioScene();
  const voices = Array.isArray(state.voiceCatalog) ? state.voiceCatalog : (state.audioStatus?.voices || []);
  if (!voices.length) return;

  state.isAllVoicesPreviewing = true;
  state.allVoicesPreviewIndex = 0;

  const btnText = document.getElementById('btn-preview-all-text');
  const btn = document.getElementById('btn-preview-all-voices');
  if (btnText) btnText.textContent = 'Stop Previews';
  if (btn) btn.className = 'px-4 py-2 bg-[#8c3523] hover:bg-[#732a1b] text-white rounded-xl text-xs font-semibold transition flex items-center shadow-md';

  playShowcaseVoiceAtIndex(0);
}

function stopAllVoicePreviews() {
  state.isAllVoicesPreviewing = false;
  state.allVoicesPreviewIndex = -1;
  state.currentShowcasePlayingVoiceId = null;

  const audioEl = document.getElementById('lore-audio-element');
  if (audioEl) {
    audioEl.pause();
    audioEl.currentTime = 0;
  }
  stopSmoothWaveVisualizer();
  updateSmoothAudioProgress();

  const btnText = document.getElementById('btn-preview-all-text');
  const btn = document.getElementById('btn-preview-all-voices');
  if (btnText) btnText.textContent = 'Preview All 16 Voices';
  if (btn) btn.className = 'px-4 py-2 bg-[#d96b43] hover:bg-[#c45a33] text-white rounded-xl text-xs font-semibold transition flex items-center shadow-md shadow-[#d96b43]/20';

  const speakerEl = document.getElementById('audio-current-speaker');
  const statusEl = document.getElementById('audio-current-status-text');
  const moodTag = document.getElementById('audio-active-mood-tag');
  if (speakerEl) speakerEl.textContent = 'Ready';
  if (moodTag) moodTag.classList.add('hidden');
  if (statusEl) statusEl.textContent = '— Press "Play Full Scene" or audition voices below';

  renderVoiceShowcase();
}

function playShowcaseVoiceAtIndex(idx) {
  if (!state.isAllVoicesPreviewing) return;

  const voices = Array.isArray(state.voiceCatalog) ? state.voiceCatalog : (state.audioStatus?.voices || []);
  if (!voices || idx >= voices.length) {
    stopAllVoicePreviews();
    return;
  }

  state.allVoicesPreviewIndex = idx;
  const v = voices[idx];
  state.currentShowcasePlayingVoiceId = v.id;
  renderVoiceShowcase();

  const card = document.getElementById(`voice-card-${v.id}`);
  if (card) {
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  const speakerEl = document.getElementById('audio-current-speaker');
  const statusEl = document.getElementById('audio-current-status-text');
  const moodTag = document.getElementById('audio-active-mood-tag');
  if (speakerEl) speakerEl.textContent = `${v.name} (${idx + 1}/${voices.length})`;
  if (moodTag) {
    moodTag.textContent = v.accent || 'Studio';
    moodTag.classList.remove('hidden');
  }
  if (statusEl) statusEl.textContent = `— [${v.archetype}] Voice Sample`;

  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl) {
    setTimeout(() => playShowcaseVoiceAtIndex(idx + 1), 500);
    return;
  }

  const localUrl = `/static/audio_cache/preview_${v.id}.mp3`;
  smoothFadeIn(1.0, 50);
  audioEl.src = localUrl;
  audioEl.play().catch(async (e) => {
    console.warn('Local preview play error, trying API:', e);
    try {
      const res = await fetch(`/api/audio/preview/${v.id}`);
      const data = await res.json();
      if (data.audio_url && audioEl) {
        smoothFadeIn(1.0, 50);
        audioEl.src = data.audio_url;
        audioEl.play().catch(err => {
          setTimeout(() => playShowcaseVoiceAtIndex(idx + 1), 400);
        });
      } else {
        setTimeout(() => playShowcaseVoiceAtIndex(idx + 1), 400);
      }
    } catch (err) {
      setTimeout(() => playShowcaseVoiceAtIndex(idx + 1), 400);
    }
  });

  audioEl.onended = () => {
    if (state.isAllVoicesPreviewing) {
      setTimeout(() => {
        playShowcaseVoiceAtIndex(idx + 1);
      }, 420);
    }
  };

  audioEl.onerror = () => {
    if (state.isAllVoicesPreviewing) {
      playShowcaseVoiceAtIndex(idx + 1);
    }
  };
}

async function updateSpeakerVoice(speakerKey, newVoiceId) {
  if (!state.audioScene) return;

  if (speakerKey === 'narrator') {
    state.audioScene.narrator_voice.voice_id = newVoiceId;
  } else if (state.audioScene.characters[speakerKey]) {
    state.audioScene.characters[speakerKey].voice_id = newVoiceId;
  }

  try {
    await fetch('/api/audio/scene', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.audioScene)
    });
  } catch (err) {
    console.error('Failed to save voice assignment:', err);
  }

  renderAudioStudio();
}

async function updateDeliveryNote(characterKey, newTone) {
  if (!state.audioScene) return;
  if (characterKey === 'narrator') {
    state.audioScene.narrator_voice.tone = newTone;
  } else if (state.audioScene.characters[characterKey]) {
    state.audioScene.characters[characterKey].tone = newTone;
  }

  try {
    await fetch('/api/audio/scene', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state.audioScene)
    });
  } catch (err) {
    console.error('Failed to save delivery note:', err);
  }

  renderAudioStudio();
}

// Audition Official ElevenLabs Studio Sample
async function previewSpeakerVoice(speakerKey) {
  stopAllVoicePreviews();
  await stopAudioScene();

  const scene = state.audioScene;
  if (!scene) return;

  const voices = Array.isArray(state.voiceCatalog) 
    ? state.voiceCatalog 
    : (state.audioStatus?.voices || []);

  let voiceId = 'JBFqnCBsd6RMkjVDRZzb';
  if (speakerKey === 'narrator') {
    voiceId = scene.narrator_voice?.voice_id || 'JBFqnCBsd6RMkjVDRZzb';
  } else if (scene.characters?.[speakerKey]?.voice_id) {
    voiceId = scene.characters[speakerKey].voice_id;
  } else if (speakerKey === 'Lyra Vance') {
    voiceId = '21m00Tcm4TlvDq8ikWAM';
  } else if (speakerKey === 'Captain Kaelen') {
    voiceId = 'N2lVS1w4EtoT3dr4eOWO';
  }

  const voiceObj = voices.find(v => v.id === voiceId) || {};
  const audioEl = document.getElementById('lore-audio-element');
  const speakerEl = document.getElementById('audio-current-speaker');
  const statusEl = document.getElementById('audio-current-status-text');
  const moodTag = document.getElementById('audio-active-mood-tag');

  if (speakerEl) speakerEl.textContent = `Auditioning: ${voiceObj.name || speakerKey}`;
  if (moodTag) {
    moodTag.textContent = voiceObj.accent || 'Natural';
    moodTag.classList.remove('hidden');
  }
  if (statusEl) statusEl.textContent = `— Voice Sample [${voiceObj.archetype || 'Voice'}]`;

  const resetUI = () => {
    stopSmoothWaveVisualizer();
    updateSmoothAudioProgress();
    if (speakerEl) speakerEl.textContent = 'Ready';
    if (moodTag) moodTag.classList.add('hidden');
    if (statusEl) statusEl.textContent = '— Press "Play Full Scene" or audition voices below';
  };

  const playApiFallback = async () => {
    try {
      const res = await fetch(`/api/audio/preview/${voiceId}`);
      const data = await res.json();
      if (data.audio_url && audioEl) {
        smoothFadeIn(1.0, 50);
        audioEl.src = data.audio_url;
        audioEl.play().catch(err => resetUI());
      } else {
        synthesizeSamplePhrase();
      }
    } catch (err) {
      synthesizeSamplePhrase();
    }
  };

  const synthesizeSamplePhrase = async () => {
    try {
      if (statusEl) statusEl.textContent = `— Generating voice preview...`;
      const res = await fetch('/api/audio/synthesize_line', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: "In the submerged city of Oakhaven, the bells began to chime.",
          voice_id: voiceId,
          rate: 1.0,
          pitch: 1.0,
          delivery: "Warm, measured, and atmospheric storytelling",
          expressiveness: state.expressiveness || 0.75
        })
      });
      const data = await res.json();
      if (data.audio_url && audioEl) {
        smoothFadeIn(1.0, 50);
        audioEl.src = data.audio_url;
        audioEl.play().catch(err => resetUI());
      } else {
        resetUI();
      }
    } catch (err) {
      console.error('Preview error:', err);
      resetUI();
    }
  };

  const localUrl = `/static/audio_cache/preview_${voiceId}.mp3`;
  if (audioEl) {
    smoothFadeIn(1.0, 50);
    audioEl.src = localUrl;
    audioEl.onended = resetUI;
    audioEl.onerror = () => {
      console.warn('Local preview playback error, falling back to API preview...');
      playApiFallback();
    };
    audioEl.play().catch((e) => {
      console.warn('Local preview playback rejected, trying API fallback:', e);
      playApiFallback();
    });
  }
}

// ============================================================================
// Playback Speed & Background Audio Warmup Controls
// ============================================================================
function setPlaybackSpeed(rate = 1.0) {
  state.audioPlaybackRate = rate;
  const audioEl = document.getElementById('lore-audio-element');
  if (audioEl) audioEl.playbackRate = rate;
}

async function warmUpAudioScene() {
  if (!state.audioScene) return;
  try {
    const res = await fetch('/api/audio/synthesize_scene', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scene: state.audioScene,
        expressiveness: state.expressiveness || 0.75
      })
    });
    const playlist = await res.json();
    if (playlist && playlist.lines && playlist.lines.length > 0) {
      state.audioPlaylist = playlist.lines;
      console.log(`[Audio Studio] Pre-warmed ${playlist.lines.length} lines into memory for 0ms playback!`);
    }
  } catch (err) {
    console.warn('[Audio Studio] Warmup check error:', err);
  }
}

function unlockAutoplayNow() {
  const promptEl = document.getElementById('audio-autoplay-prompt');
  if (promptEl) promptEl.classList.add('hidden');
  
  if (smoothAudioCtx && smoothAudioCtx.state === 'suspended') {
    smoothAudioCtx.resume().catch(() => {});
  }
  
  const audioEl = document.getElementById('lore-audio-element');
  if (audioEl) {
    audioEl.play().catch(() => {});
  }
  
  playPlaylistIndex(state.pendingLineIndex || 0);
}

// ============================================================================
// Multi-Segmented Scene Timeline & 60fps Live Telemetry Engine
// ============================================================================

function estimateLineDuration(item) {
  if (item && item.duration && item.duration > 0) return item.duration;
  if (item && item.size_bytes && item.size_bytes > 0) {
    // 128kbps CBR MP3 is 16,000 bytes/sec
    return Math.max(1.5, Math.round((item.size_bytes / 16000) * 10) / 10);
  }
  const wordCount = ((item && item.text) || '').split(/\s+/).filter(Boolean).length;
  return Math.max(2.0, Math.round((wordCount / 2.2) * 10) / 10);
}

function formatClockTime(secs) {
  if (!isFinite(secs) || secs < 0) secs = 0;
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  const tenths = Math.floor((secs % 1) * 10);
  return `${m}:${s < 10 ? '0' : ''}${s}.${tenths}`;
}

function formatTime(secs) {
  if (!isFinite(secs) || secs < 0) secs = 0;
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

function prewarmSceneAudioDurations() {
  const playlist = state.audioPlaylist || (state.audioScene && state.audioScene.playlist);
  if (!playlist || playlist.length === 0) return;

  state.audioPlaylist = playlist;
  let total = 0;

  playlist.forEach((item, idx) => {
    if (!item.duration) {
      item.duration = estimateLineDuration(item);
      if (item.audio_url) {
        const probe = new Audio();
        probe.preload = 'metadata';
        probe.onloadedmetadata = () => {
          if (probe.duration && isFinite(probe.duration) && probe.duration > 0) {
            item.duration = probe.duration;
            state.sceneTotalDuration = playlist.reduce((acc, l) => acc + (l.duration || estimateLineDuration(l)), 0);
            updateSceneDurationDisplay();
          }
        };
        probe.src = item.audio_url;
      }
    }
    total += item.duration;
  });

  state.sceneTotalDuration = total;
  updateSceneDurationDisplay();
  renderSceneSegments();
}

function updateSceneDurationDisplay() {
  const totalEl = document.getElementById('scene-clock-total');
  if (totalEl && state.sceneTotalDuration) {
    totalEl.textContent = formatClockTime(state.sceneTotalDuration);
  }
}

function renderSceneSegments() {
  const container = document.getElementById('scene-segments-container');
  if (!container) return;

  const playlist = state.audioPlaylist || (state.audioScene && state.audioScene.playlist);
  if (!playlist || playlist.length === 0) {
    container.innerHTML = `
      <div class="col-span-5 h-7 rounded-lg bg-[#201a16] border border-[#3c3127] flex items-center justify-center text-[10px] text-[#786c5f]">
        Loading scene dialogue segments...
      </div>
    `;
    return;
  }

  const currentIdx = state.currentAudioLineIndex ?? -1;

  container.innerHTML = playlist.map((item, idx) => {
    const isNarrator = item.speaker === 'Narrator';
    const isLyra = item.speaker.includes('Lyra');
    const avatar = isNarrator ? '🎙️' : (isLyra ? '📜' : '⚓');
    const shortName = isNarrator ? 'Narrator' : (isLyra ? 'Lyra' : 'Kaelen');
    const durationSec = (item.duration || estimateLineDuration(item)).toFixed(1);

    let extraClass = '';
    let fillWidth = '0%';
    let statusText = `${durationSec}s`;

    if (state.isAudioPlaying) {
      if (idx < currentIdx) {
        extraClass = 'segment-completed';
        fillWidth = '100%';
        statusText = '✓ Done';
      } else if (idx === currentIdx) {
        extraClass = 'segment-active';
        fillWidth = '0%';
        statusText = '🔊 Playing';
      }
    }

    return `
      <div id="scene-seg-${idx}" onclick="jumpToSceneLine(${idx})" class="scene-segment ${extraClass}" title="Click to jump to Line ${idx + 1}: ${escapeHtml(item.speaker)} (${durationSec}s)">
        <div id="seg-fill-${idx}" class="scene-segment-fill" style="width: ${fillWidth};"></div>
        <div class="scene-segment-content">
          <span class="flex items-center space-x-1 truncate">
            <span class="text-xs">${avatar}</span>
            <span class="truncate font-medium text-[10px] sm:text-[11px]">${escapeHtml(shortName)}</span>
          </span>
          <span id="seg-status-${idx}" class="text-[9px] font-mono text-[#8c8275] ml-1">${statusText}</span>
        </div>
      </div>
    `;
  }).join('');
}

function jumpToSceneLine(idx) {
  stopAllVoicePreviews();
  state.isAudioPlaying = true;
  initSmoothAudioEngine();
  
  const playBtn = document.getElementById('btn-play-scene');
  if (playBtn) {
    playBtn.innerHTML = `
      <span class="w-2 h-2 rounded-full bg-white animate-ping mr-2"></span>
      <span>Playing Scene...</span>
    `;
    playBtn.className = 'px-5 py-2.5 bg-gradient-to-r from-[#993b22] to-[#b35928] text-white rounded-xl text-xs font-bold transition flex items-center shadow-lg';
  }

  playPlaylistIndex(idx);
}

function startLiveSceneClock() {
  if (state.sceneClockRafId) {
    cancelAnimationFrame(state.sceneClockRafId);
  }

  function loop() {
    if (!state.isAudioPlaying) return;

    updateLiveSceneClock();
    state.sceneClockRafId = requestAnimationFrame(loop);
  }

  state.sceneClockRafId = requestAnimationFrame(loop);
}

function stopLiveSceneClock() {
  if (state.sceneClockRafId) {
    cancelAnimationFrame(state.sceneClockRafId);
    state.sceneClockRafId = null;
  }
}

function updateLiveSceneClock() {
  const playlist = state.audioPlaylist || (state.audioScene && state.audioScene.playlist);
  if (!playlist || playlist.length === 0) return;

  const currentIdx = state.currentAudioLineIndex ?? 0;
  const audioEl = document.getElementById('lore-audio-element');
  const currentItem = playlist[currentIdx];

  // Sum prior lines' durations
  let priorDuration = 0;
  for (let i = 0; i < currentIdx; i++) {
    priorDuration += (playlist[i].duration || estimateLineDuration(playlist[i]));
  }

  const currentLineElapsed = audioEl ? audioEl.currentTime : 0;
  const currentLineTotal = currentItem ? (currentItem.duration || estimateLineDuration(currentItem)) : 3.0;
  const totalElapsed = priorDuration + currentLineElapsed;
  const totalSceneDuration = state.sceneTotalDuration || playlist.reduce((s, x) => s + (x.duration || estimateLineDuration(x)), 0);

  // Update Clock
  const elapsedEl = document.getElementById('scene-clock-elapsed');
  if (elapsedEl) {
    elapsedEl.textContent = formatClockTime(totalElapsed);
  }

  const totalEl = document.getElementById('scene-clock-total');
  if (totalEl) {
    totalEl.textContent = formatClockTime(totalSceneDuration);
  }

  // Update Percentage
  const pct = Math.min(100, Math.round((totalElapsed / Math.max(1, totalSceneDuration)) * 100));
  const pctEl = document.getElementById('scene-progress-pct');
  if (pctEl) {
    pctEl.textContent = `${pct}%`;
  }

  // Update Line Progress Countdown Badge
  const progressText = document.getElementById('scene-line-progress-text');
  if (progressText && currentItem) {
    const remainingLine = Math.max(0, currentLineTotal - currentLineElapsed);
    progressText.textContent = `Line ${currentIdx + 1} of ${playlist.length}: ${currentItem.speaker} — ${remainingLine.toFixed(1)}s left`;
  }

  // Update active segment fill bar
  const segFill = document.getElementById(`seg-fill-${currentIdx}`);
  if (segFill) {
    const segPct = Math.min(100, (currentLineElapsed / Math.max(0.1, currentLineTotal)) * 100);
    segFill.style.width = `${segPct}%`;
  }

  const segStatus = document.getElementById(`seg-status-${currentIdx}`);
  if (segStatus) {
    segStatus.textContent = `${currentLineElapsed.toFixed(1)}s / ${currentLineTotal.toFixed(1)}s`;
  }

  // Also sync the master progress scrubber
  const scrubberFill = document.getElementById('audio-scrubber-fill');
  if (scrubberFill) {
    scrubberFill.style.width = `${pct}%`;
  }
  const timeCurrent = document.getElementById('audio-time-current');
  if (timeCurrent) {
    timeCurrent.textContent = formatTime(Math.floor(totalElapsed));
  }
  const timeTotal = document.getElementById('audio-time-total');
  if (timeTotal) {
    timeTotal.textContent = formatTime(Math.floor(totalSceneDuration));
  }
}

// Full Scene Playback using ElevenLabs Storyteller Voices
async function playAudioScene() {
  stopAudioScene(false);
  state.isAudioPlaying = true;
  state.currentAudioLineIndex = 0;

  const audioEl = document.getElementById('lore-audio-element');
  const promptEl = document.getElementById('audio-autoplay-prompt');
  if (promptEl) promptEl.classList.add('hidden');

  initSmoothAudioEngine();

  const playBtn = document.getElementById('btn-play-scene');
  if (playBtn) {
    playBtn.innerHTML = `
      <span class="w-2 h-2 rounded-full bg-white animate-ping mr-2"></span>
      <span>Playing Scene...</span>
    `;
    playBtn.className = 'px-5 py-2.5 bg-gradient-to-r from-[#993b22] to-[#b35928] text-white rounded-xl text-xs font-bold transition flex items-center shadow-lg';
  }

  const badge = document.getElementById('audio-now-playing-badge');
  if (badge) badge.classList.remove('hidden');

  const speakerEl = document.getElementById('audio-current-speaker');
  const statusEl = document.getElementById('audio-current-status-text');
  if (speakerEl) speakerEl.textContent = 'Voice Studio';
  if (statusEl) statusEl.textContent = `— Performing dialogue with emotional prosody & natural cadence...`;

  // Pre-warm durations & segments if not done
  if (!state.audioPlaylist || state.audioPlaylist.length === 0) {
    if (state.audioScene && state.audioScene.playlist && state.audioScene.playlist.length > 0) {
      state.audioPlaylist = state.audioScene.playlist;
    }
  }

  prewarmSceneAudioDurations();
  renderSceneSegments();

  // 1. FAST PATH: If playlist is already in memory, play line 0 immediately!
  if (state.audioPlaylist && state.audioPlaylist.length > 0) {
    playPlaylistIndex(0);
    return;
  }

  // 2. NETWORK PATH: Synthesize scene via parallel backend if not yet in memory
  try {
    const res = await fetch('/api/audio/synthesize_scene', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scene: state.audioScene,
        expressiveness: state.expressiveness || 0.75
      })
    });

    const playlist = await res.json();
    state.audioPlaylist = playlist.lines || [];
    prewarmSceneAudioDurations();

    if (state.isAudioPlaying && state.audioPlaylist.length > 0) {
      playPlaylistIndex(0);
    }
  } catch (err) {
    console.error('Failed to synthesize scene:', err);
    if (statusEl) statusEl.textContent = `— Error: ${err.message}`;
    stopAudioScene(true);
  }
}

function playPlaylistIndex(idx) {
  if (!state.isAudioPlaying) return;

  const playlist = state.audioPlaylist || (state.audioScene && state.audioScene.playlist);
  if (!playlist || idx >= playlist.length) {
    // Scene finished naturally!
    stopAudioScene();
    renderSceneSegments();
    document.querySelectorAll('.scene-segment').forEach(s => s.classList.add('segment-completed'));
    document.querySelectorAll('.scene-segment-fill').forEach(f => f.style.width = '100%');
    const elapsedEl = document.getElementById('scene-clock-elapsed');
    const totalEl = document.getElementById('scene-clock-total');
    if (elapsedEl && totalEl) elapsedEl.textContent = totalEl.textContent;
    const pctEl = document.getElementById('scene-progress-pct');
    if (pctEl) pctEl.textContent = '100%';
    const progressText = document.getElementById('scene-line-progress-text');
    if (progressText) progressText.textContent = 'Scene Complete (5 of 5 Lines)';
    return;
  }

  state.currentAudioLineIndex = idx;
  const item = playlist[idx];
  const startTime = performance.now();

  // Update segment classes: completed prior, active current, waiting subsequent
  playlist.forEach((_, i) => {
    const seg = document.getElementById(`scene-seg-${i}`);
    const segFill = document.getElementById(`seg-fill-${i}`);
    const segStatus = document.getElementById(`seg-status-${i}`);
    if (seg) {
      if (i < idx) {
        seg.className = 'scene-segment segment-completed';
        if (segFill) segFill.style.width = '100%';
        if (segStatus) segStatus.textContent = '✓ Done';
      } else if (i === idx) {
        seg.className = 'scene-segment segment-active';
        if (segFill) segFill.style.width = '0%';
        if (segStatus) segStatus.textContent = '🔊 Playing';
      } else {
        seg.className = 'scene-segment';
        if (segFill) segFill.style.width = '0%';
        if (segStatus) segStatus.textContent = `${(playlist[i].duration || estimateLineDuration(playlist[i])).toFixed(1)}s`;
      }
    }
  });

  // Visual karaoke highlight with smooth scroll to center
  document.querySelectorAll('#audio-script-lines > div').forEach((el, i) => {
    if (i === idx) {
      el.classList.add('audio-line-active');
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      el.classList.remove('audio-line-active');
    }
  });

  // Highlight character speaking in casting grid
  ['narrator', 'Lyra Vance', 'Captain Kaelen'].forEach(k => {
    const card = document.getElementById(`cast-card-${k}`);
    const pulse = document.getElementById(`char-speaker-pulse-${k}`);
    const isThisSpeaker = (k === 'narrator' && item.speaker === 'Narrator') ||
                          (k === 'Lyra Vance' && item.speaker.includes('Lyra')) ||
                          (k === 'Captain Kaelen' && item.speaker.includes('Kaelen'));
    if (card) {
      if (isThisSpeaker) card.classList.add('cast-card-speaking');
      else card.classList.remove('cast-card-speaking');
    }
    if (pulse) {
      if (isThisSpeaker) pulse.classList.remove('hidden');
      else pulse.classList.add('hidden');
    }
  });

  const speakerEl = document.getElementById('audio-current-speaker');
  const statusEl = document.getElementById('audio-current-status-text');
  const moodTag = document.getElementById('audio-active-mood-tag');
  const emotionBadge = item.emotion_label || getEmotionBadge(item.delivery);
  if (speakerEl) speakerEl.textContent = `${item.speaker} (Line ${idx + 1} of ${playlist.length})`;
  if (moodTag) {
    moodTag.textContent = emotionBadge;
    moodTag.classList.remove('hidden');
  }
  if (statusEl) statusEl.textContent = `— "${item.delivery}" [${cleanVoiceName(item.voice_name)}]`;

  // Update teleprompter ticker
  const ticker = document.getElementById('scene-teleprompter-ticker');
  if (ticker) {
    ticker.textContent = `Speaking: "${item.text}"`;
  }

  // Pre-buffer NEXT line in RAM for 0ms transition latency!
  if (idx + 1 < playlist.length) {
    const nextItem = playlist[idx + 1];
    const prebufEl = document.getElementById('lore-audio-prebuffer');
    if (prebufEl && nextItem && nextItem.audio_url) {
      prebufEl.src = nextItem.audio_url;
      prebufEl.preload = 'auto';
    }
    const prebufStatus = document.getElementById('scene-prebuffer-status');
    if (prebufStatus) {
      prebufStatus.innerHTML = `
        <span class="w-1.5 h-1.5 rounded-full bg-[#34d399] mr-1 animate-pulse"></span>
        Next: ${escapeHtml(nextItem.speaker)} — Pre-buffered in RAM (0ms transition)
      `;
    }
  } else {
    const prebufStatus = document.getElementById('scene-prebuffer-status');
    if (prebufStatus) {
      prebufStatus.innerHTML = `
        <span class="w-1.5 h-1.5 rounded-full bg-[#34d399] mr-1"></span>
        Final Dialogue Line
      `;
    }
  }

  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl || !item.audio_url) {
    const cadence = Math.max(80, Math.round(140 / (state.audioPlaybackRate || 1.0)));
    setTimeout(() => {
      if (state.isAudioPlaying) playPlaylistIndex(idx + 1);
    }, cadence);
    return;
  }

  audioEl.src = item.audio_url;
  audioEl.playbackRate = state.audioPlaybackRate || 1.0;
  audioEl.volume = 1.0;

  audioEl.onloadedmetadata = () => {
    if (audioEl.duration && isFinite(audioEl.duration) && audioEl.duration > 0) {
      item.duration = audioEl.duration;
    }
  };

  audioEl.onended = () => {
    if (state.isAudioPlaying) {
      // Mark current segment completed right away
      const seg = document.getElementById(`scene-seg-${idx}`);
      const segFill = document.getElementById(`seg-fill-${idx}`);
      const segStatus = document.getElementById(`seg-status-${idx}`);
      if (seg) seg.className = 'scene-segment segment-completed';
      if (segFill) segFill.style.width = '100%';
      if (segStatus) segStatus.textContent = '✓ Done';

      // Fast, snappy conversational pause between characters (140ms scaled with speed)
      const cadence = Math.max(80, Math.round(140 / (state.audioPlaybackRate || 1.0)));
      setTimeout(() => {
        if (state.isAudioPlaying) {
          playPlaylistIndex(idx + 1);
        }
      }, cadence);
    }
  };

  audioEl.onerror = (e) => {
    console.warn(`[Audio Studio] Audio error on line ${idx}:`, e);
    if (state.isAudioPlaying) {
      setTimeout(() => {
        if (state.isAudioPlaying) playPlaylistIndex(idx + 1);
      }, 200);
    }
  };

  const playPromise = audioEl.play();
  if (playPromise !== undefined) {
    playPromise.then(() => {
      const lat = ((performance.now() - startTime) / 1000).toFixed(2);
      const latVal = document.getElementById('scene-latency-val');
      if (latVal) latVal.textContent = `${lat}s (Instant Stream)`;

      startSmoothWaveVisualizer();
      startLiveSceneClock();

      const promptEl = document.getElementById('audio-autoplay-prompt');
      if (promptEl) promptEl.classList.add('hidden');
    }).catch(err => {
      console.warn('Audio play() error:', err);
      if (err.name === 'NotAllowedError') {
        state.pendingLineIndex = idx;
        const promptEl = document.getElementById('audio-autoplay-prompt');
        if (promptEl) promptEl.classList.remove('hidden');
        if (statusEl) statusEl.textContent = '— Audio playback locked by browser. Click "Enable Audio Now" above.';
      } else if (err.name === 'AbortError') {
        console.log('[Audio Studio] Playback aborted or superseded.');
      } else {
        console.error('[Audio Studio] Playback error on line ' + idx, err);
        stopAudioScene(true);
      }
    });
  }
}

// Single Line Playback
async function playSingleLine(index) {
  stopAudioScene(false);

  const scene = state.audioScene;
  if (!scene || !scene.lines || !scene.lines[index]) return;

  const line = scene.lines[index];
  const btn = document.getElementById(`btn-line-${index}`);
  const origBtnContent = `
    <svg class="w-3.5 h-3.5 mr-1.5 text-[#f87171]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path></svg>
    Play Line
  `;

  // Smooth scroll and line highlight
  document.querySelectorAll('#audio-script-lines > div').forEach((el, i) => {
    if (i === index) {
      el.classList.add('audio-line-active');
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      el.classList.remove('audio-line-active');
    }
  });

  // Highlight character in casting grid
  ['narrator', 'Lyra Vance', 'Captain Kaelen'].forEach(k => {
    const card = document.getElementById(`cast-card-${k}`);
    const pulse = document.getElementById(`char-speaker-pulse-${k}`);
    const isThisSpeaker = (k === 'narrator' && line.speaker === 'Narrator') ||
                          (k === 'Lyra Vance' && line.speaker.includes('Lyra')) ||
                          (k === 'Captain Kaelen' && line.speaker.includes('Kaelen'));
    if (card) {
      if (isThisSpeaker) card.classList.add('cast-card-speaking');
      else card.classList.remove('cast-card-speaking');
    }
    if (pulse) {
      if (isThisSpeaker) pulse.classList.remove('hidden');
      else pulse.classList.add('hidden');
    }
  });

  let charTone = line.delivery || '';
  const speakerEl = document.getElementById('audio-current-speaker');
  const statusEl = document.getElementById('audio-current-status-text');
  const moodTag = document.getElementById('audio-active-mood-tag');
  const emotionBadge = getEmotionBadge(charTone);
  if (speakerEl) speakerEl.textContent = line.speaker;
  if (moodTag) {
    moodTag.textContent = emotionBadge;
    moodTag.classList.remove('hidden');
  }
  if (statusEl) statusEl.textContent = `— [${emotionBadge}] "${charTone}"`;

  const audioEl = document.getElementById('lore-audio-element');
  if (!audioEl) return;

  const resetLineUI = () => {
    if (btn) btn.innerHTML = origBtnContent;
    const lineEl = document.getElementById(`audio-line-${index}`);
    if (lineEl) lineEl.classList.remove('audio-line-active');
    ['narrator', 'Lyra Vance', 'Captain Kaelen'].forEach(k => {
      const card = document.getElementById(`cast-card-${k}`);
      const pulse = document.getElementById(`char-speaker-pulse-${k}`);
      if (card) card.classList.remove('cast-card-speaking');
      if (pulse) pulse.classList.add('hidden');
    });
    stopSmoothWaveVisualizer();
    updateSmoothAudioProgress();
    if (speakerEl) speakerEl.textContent = 'Ready';
    if (moodTag) moodTag.classList.add('hidden');
    if (statusEl) statusEl.textContent = '— Press "Play Full Scene" or audition voices below';
  };

  const playAudioFile = (url, voiceName = 'ElevenLabs') => {
    if (btn) {
      btn.innerHTML = `
        <svg class="w-3.5 h-3.5 mr-1 text-[#f87171] animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path></svg>
        Speaking...
      `;
    }
    if (statusEl) statusEl.textContent = `— [${emotionBadge}] "${charTone}" (${cleanVoiceName(voiceName)})`;
    audioEl.src = url;
    audioEl.playbackRate = state.audioPlaybackRate || 1.0;
    audioEl.volume = 1.0;
    audioEl.onended = resetLineUI;
    audioEl.onerror = resetLineUI;
    const p = audioEl.play();
    if (p !== undefined) {
      p.then(() => startSmoothWaveVisualizer()).catch(err => {
        console.warn('Audio play error:', err);
        resetLineUI();
      });
    }
  };

  // FAST PATH: Instant playback from pre-warmed playlist (0ms)
  const cachedItem = (state.audioPlaylist && state.audioPlaylist[index]) ||
                     (state.audioScene && state.audioScene.playlist && state.audioScene.playlist[index]);
  if (cachedItem && cachedItem.audio_url) {
    playAudioFile(cachedItem.audio_url, cleanVoiceName(cachedItem.voice_name));
    return;
  }

  // Network synthesis fallback with timeout safeguard:
  if (btn) {
    btn.innerHTML = `
      <span class="w-2.5 h-2.5 border-2 border-[#fca5a5] border-t-transparent rounded-full animate-spin mr-1.5"></span>
      Loading...
    `;
  }
  let voiceId = 'JBFqnCBsd6RMkjVDRZzb';
  if (line.speaker === 'Narrator') {
    voiceId = scene.narrator_voice?.voice_id || 'JBFqnCBsd6RMkjVDRZzb';
  } else if (scene.characters?.[line.speaker]) {
    voiceId = scene.characters[line.speaker].voice_id || '21m00Tcm4TlvDq8ikWAM';
  }

  const timeoutId = setTimeout(() => {
    resetLineUI();
  }, 4500);

  try {
    const res = await fetch('/api/audio/synthesize_line', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: line.text,
        voice_id: voiceId,
        rate: 1.0,
        pitch: 1.0,
        delivery: charTone,
        expressiveness: state.expressiveness || 0.75
      })
    });
    clearTimeout(timeoutId);
    const data = await res.json();
    if (data.audio_url) {
      playAudioFile(data.audio_url, data.voice_name);
    } else {
      resetLineUI();
    }
  } catch (err) {
    clearTimeout(timeoutId);
    console.error('Failed to play single line:', err);
    resetLineUI();
  }
}

function stopAudioScene(resetUI = true) {
  if (state.isAllVoicesPreviewing) {
    stopAllVoicePreviews();
    return;
  }

  stopLiveSceneClock();
  state.isAudioPlaying = false;
  state.currentAudioLineIndex = -1;

  const audioEl = document.getElementById('lore-audio-element');
  if (audioEl) {
    audioEl.pause();
    audioEl.currentTime = 0;
  }
  const prebufEl = document.getElementById('lore-audio-prebuffer');
  if (prebufEl) {
    prebufEl.pause();
    prebufEl.currentTime = 0;
  }

  stopSmoothWaveVisualizer();
  updateSmoothAudioProgress();

  if (resetUI) {
    document.querySelectorAll('#audio-script-lines > div').forEach(el => {
      el.classList.remove('audio-line-active');
    });

    ['narrator', 'Lyra Vance', 'Captain Kaelen'].forEach(k => {
      const card = document.getElementById(`cast-card-${k}`);
      const pulse = document.getElementById(`char-speaker-pulse-${k}`);
      if (card) card.classList.remove('cast-card-speaking');
      if (pulse) pulse.classList.add('hidden');
    });

    // Reset segments styling
    renderSceneSegments();

    const elapsedEl = document.getElementById('scene-clock-elapsed');
    if (elapsedEl) elapsedEl.textContent = '0:00.0';
    const pctEl = document.getElementById('scene-progress-pct');
    if (pctEl) pctEl.textContent = '0%';
    const lineProgress = document.getElementById('scene-line-progress-text');
    if (lineProgress) lineProgress.textContent = 'Ready (5 Lines)';

    const promptEl = document.getElementById('audio-autoplay-prompt');
    if (promptEl) promptEl.classList.add('hidden');

    const badge = document.getElementById('audio-now-playing-badge');
    if (badge) badge.classList.add('hidden');

    const moodTag = document.getElementById('audio-active-mood-tag');
    if (moodTag) moodTag.classList.add('hidden');

    const speakerEl = document.getElementById('audio-current-speaker');
    const statusEl = document.getElementById('audio-current-status-text');
    if (speakerEl) speakerEl.textContent = 'Ready';
    if (statusEl) statusEl.textContent = '— Press "Play Full Scene" or audition voices below';

    const playBtn = document.getElementById('btn-play-scene');
    if (playBtn) {
      playBtn.innerHTML = `
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span>Play Full Scene</span>
      `;
      playBtn.className = 'px-5 py-2.5 bg-gradient-to-r from-[#d96b43] to-[#e5a953] hover:from-[#c45a33] hover:to-[#d09641] text-white rounded-xl text-xs font-bold transition flex items-center shadow-lg shadow-[#d96b43]/30 transform hover:-translate-y-0.5 active:translate-y-0 active:scale-95';
    }
  }
}

// Fallback browser speech synthesis
function speakBrowserCurrentLine() {
  if (!state.isAudioPlaying) return;
  const scene = state.audioScene;
  if (!scene || !scene.lines || state.currentAudioLineIndex >= scene.lines.length) {
    stopAudioScene();
    return;
  }

  const line = scene.lines[state.currentAudioLineIndex];

  document.querySelectorAll('#audio-script-lines > div').forEach((el, idx) => {
    if (idx === state.currentAudioLineIndex) {
      el.classList.add('audio-line-active');
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
      el.classList.remove('audio-line-active');
    }
  });

  const utterance = new SpeechSynthesisUtterance(line.text);
  const voices = window.speechSynthesis.getVoices();

  if (line.speaker === 'Narrator') {
    utterance.pitch = 0.95;
    utterance.rate = 0.9;
    const v = voices.find(vo => vo.name.includes('Natural') || vo.name.includes('Christopher') || vo.name.includes('David'));
    if (v) utterance.voice = v;
  } else if (line.speaker.includes('Lyra')) {
    utterance.pitch = 1.15;
    utterance.rate = 1.05;
    const v = voices.find(vo => vo.name.includes('Jenny') || vo.name.includes('Zira') || vo.name.includes('Female'));
    if (v) utterance.voice = v;
  } else {
    utterance.pitch = 0.8;
    utterance.rate = 0.95;
    const v = voices.find(vo => vo.name.includes('Guy') || vo.name.includes('Mark') || vo.name.includes('Male'));
    if (v) utterance.voice = v;
  }

  utterance.onend = () => {
    if (state.isAudioPlaying) {
      state.currentAudioLineIndex++;
      setTimeout(speakBrowserCurrentLine, 350);
    }
  };

  utterance.onerror = () => {
    stopAudioScene();
  };

  window.speechSynthesis.speak(utterance);
}

// ============================================================================
// Modal Operations: Add, Edit, Delete Lore Entries
// ============================================================================
function openAddEntryModal() {
  state.editingEntryId = null;
  document.getElementById('modal-entry-title').textContent = 'Add Story Bible Entry';
  document.getElementById('entry-id-field').value = '';
  document.getElementById('entry-category-select').value = 'character';
  document.getElementById('entry-name-input').value = '';
  document.getElementById('entry-desc-input').value = '';
  document.getElementById('entry-tags-input').value = '';
  document.getElementById('entry-role-input').value = '';
  document.getElementById('entry-goal-input').value = '';
  document.getElementById('entry-rel-input').value = '';
  document.getElementById('entry-detail-input').value = '';

  updateModalCategoryFields('character');
  document.getElementById('entry-modal').classList.remove('hidden');
}

function openEditEntryModal(entryId) {
  const entry = state.entries.find(e => e.id === entryId);
  if (!entry) return;

  state.editingEntryId = entryId;
  document.getElementById('modal-entry-title').textContent = 'Edit Story Bible Entry';
  document.getElementById('entry-id-field').value = entry.id;
  document.getElementById('entry-category-select').value = entry.category;
  document.getElementById('entry-name-input').value = entry.name || '';
  document.getElementById('entry-desc-input').value = entry.description || '';
  document.getElementById('entry-tags-input').value = (entry.tags || []).join(', ');
  document.getElementById('entry-role-input').value = entry.role || '';
  document.getElementById('entry-goal-input').value = entry.goal || '';
  document.getElementById('entry-rel-input').value = entry.relationships || '';
  document.getElementById('entry-detail-input').value = entry.defining_detail || '';

  updateModalCategoryFields(entry.category);
  document.getElementById('entry-modal').classList.remove('hidden');
}

function closeEntryModal() {
  document.getElementById('entry-modal').classList.add('hidden');
  state.editingEntryId = null;
}

function updateModalCategoryFields(cat) {
  const charFields = document.getElementById('modal-character-fields');
  const placeFields = document.getElementById('modal-place-fields');

  if (cat === 'character') {
    charFields.classList.remove('hidden');
    placeFields.classList.add('hidden');
  } else if (cat === 'place') {
    charFields.classList.add('hidden');
    placeFields.classList.remove('hidden');
  } else {
    charFields.classList.add('hidden');
    placeFields.classList.add('hidden');
  }
}

async function handleEntryFormSubmit(e) {
  e.preventDefault();

  const id = document.getElementById('entry-id-field').value;
  const category = document.getElementById('entry-category-select').value;
  const name = document.getElementById('entry-name-input').value.trim();
  const description = document.getElementById('entry-desc-input').value.trim();
  const tagsStr = document.getElementById('entry-tags-input').value.trim();
  const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()).filter(Boolean) : [];

  if (!name || !description) {
    alert('Please provide both a Name and Description for this canon entry.');
    return;
  }

  const payload = {
    category,
    name,
    description,
    tags
  };

  if (category === 'character') {
    payload.role = document.getElementById('entry-role-input').value.trim();
    payload.goal = document.getElementById('entry-goal-input').value.trim();
    payload.relationships = document.getElementById('entry-rel-input').value.trim();
  } else if (category === 'place') {
    payload.defining_detail = document.getElementById('entry-detail-input').value.trim();
  }

  const isEditing = Boolean(state.editingEntryId);
  const url = isEditing ? `/api/canon/${state.editingEntryId}` : '/api/canon';
  const method = isEditing ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to save entry.');

    closeEntryModal();
    await loadCanonEntries();
    await refreshSystemStatus();
  } catch (err) {
    alert(err.message);
  }
}

async function confirmDeleteEntry(entryId, entryName) {
  if (!confirm(`Are you sure you want to delete "${entryName}" from the Story Bible?`)) return;

  try {
    const res = await fetch(`/api/canon/${entryId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete entry.');
    await loadCanonEntries();
    await refreshSystemStatus();
  } catch (err) {
    alert(err.message);
  }
}

async function resetSeededCanon() {
  if (!confirm('Reset all Story Bible entries to the default seeded canon? Any custom additions will be restored.')) return;

  try {
    const res = await fetch('/api/canon/reset', { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset canon.');
    await loadCanonEntries();
    await refreshSystemStatus();
    alert('Story Bible restored to default seeded canon.');
  } catch (err) {
    alert(err.message);
  }
}

// ============================================================================
// Settings Modal
// ============================================================================
function openSettingsModal() {
  document.getElementById('settings-modal').classList.remove('hidden');
  const input = document.getElementById('settings-api-key');
  if (input && state.aiStatus && state.aiStatus.has_api_key) {
    input.placeholder = `Configured (${state.aiStatus.masked_key || 'Active'})`;
  }
}

function closeSettingsModal() {
  document.getElementById('settings-modal').classList.add('hidden');
}

async function saveSettings(e) {
  e.preventDefault();
  const keyInput = document.getElementById('settings-api-key')?.value.trim();

  const payload = {};
  if (keyInput) payload.gemini_api_key = keyInput;

  try {
    const res = await fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status) state.aiStatus = data.status;
    if (data.audio_status) state.audioStatus = data.audio_status;
    renderStatusBadge();
    renderAudioStudio();
    closeSettingsModal();
    alert('Settings updated.');
  } catch (err) {
    alert('Failed to update configuration: ' + err.message);
  }
}

// ============================================================================
// Event Listeners Setup
// ============================================================================
function setupEventListeners() {
  document.querySelectorAll('.bible-cat-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      state.activeCategory = tab.dataset.category;
      updateCategoryPills();
      renderStoryBible();
    });
  });

  const searchInput = document.getElementById('bible-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value;
      renderStoryBible();
    });
  }

  const catSelect = document.getElementById('entry-category-select');
  if (catSelect) {
    catSelect.addEventListener('change', (e) => {
      updateModalCategoryFields(e.target.value);
    });
  }

  const entryForm = document.getElementById('entry-form');
  if (entryForm) {
    entryForm.addEventListener('submit', handleEntryFormSubmit);
  }

  const settingsForm = document.getElementById('settings-form');
  if (settingsForm) {
    settingsForm.addEventListener('submit', saveSettings);
  }

  const chatInput = document.getElementById('chat-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleChatSubmit();
      }
    });
  }

  const draftInput = document.getElementById('continuity-draft-input');
  if (draftInput) {
    draftInput.addEventListener('input', updateDraftWordCount);
  }
}

function updateCategoryPills() {
  document.querySelectorAll('.bible-cat-tab').forEach(tab => {
    if (tab.dataset.category === state.activeCategory) {
      tab.classList.add('bg-[#d96b43]', 'text-white');
      tab.classList.remove('bg-[#2a241f]', 'text-[#c9c1b5]');
    } else {
      tab.classList.remove('bg-[#d96b43]', 'text-white');
      tab.classList.add('bg-[#2a241f]', 'text-[#c9c1b5]');
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatMarkdownText(text) {
  if (!text) return '';
  let formatted = escapeHtml(text);
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
  formatted = formatted.replace(/\n\n/g, '<br/><br/>').replace(/\n/g, '<br/>');
  return formatted;
}
