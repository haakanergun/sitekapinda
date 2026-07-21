(() => {
  "use strict";

  const STATUS_LABELS = Object.freeze({
    new: "New",
    contacted: "Contacted",
    interested: "Interested",
    approved: "Approved",
    not_interested: "Not interested",
    do_not_contact: "Do not contact",
  });
  const STORAGE_KEY = "sitekapinda:synthetic-sales-ops:v1";
  const SAFE_DESKTOP_MOCKUP = /^mockups\/[A-Za-z0-9][A-Za-z0-9._-]*-desktop\.png$/;
  const SAFE_MOBILE_MOCKUP = /^mockups\/[A-Za-z0-9][A-Za-z0-9._-]*-mobile\.png$/;
  const panelData = window.SITEKAPINDA_PANEL_DATA || { records: [] };

  const state = {
    records: Array.isArray(panelData.records) ? panelData.records : [],
    changes: readChanges(),
    selectedId: null,
    query: "",
    statusFilter: "all",
    categoryFilter: "all",
    previewKey: null,
  };

  const els = {
    total: document.querySelector("#metric-total"),
    open: document.querySelector("#metric-open"),
    contacted: document.querySelector("#metric-contacted"),
    interested: document.querySelector("#metric-interested"),
    search: document.querySelector("#search"),
    statusFilter: document.querySelector("#status-filter"),
    categoryFilter: document.querySelector("#category-filter"),
    leadList: document.querySelector("#lead-list"),
    detailName: document.querySelector("#detail-name"),
    detailMeta: document.querySelector("#detail-meta"),
    empty: document.querySelector("#empty-state"),
    detailContent: document.querySelector("#detail-content"),
    statusPill: document.querySelector("#status-pill"),
    contactedCheck: document.querySelector("#contacted-check"),
    statusSelect: document.querySelector("#status-select"),
    note: document.querySelector("#note"),
    save: document.querySelector("#save-status"),
    copy: document.querySelector("#copy-message"),
    feedback: document.querySelector("#save-feedback"),
    phone: document.querySelector("#phone-display"),
    websiteEvidence: document.querySelector("#website-evidence"),
    evidenceScore: document.querySelector("#evidence-score"),
    nextAction: document.querySelector("#next-action"),
    selectionReason: document.querySelector("#selection-reason"),
    createdAt: document.querySelector("#created-at"),
    previewHeading: document.querySelector("#preview-heading"),
    previewDescription: document.querySelector("#preview-description"),
    previewGrid: document.querySelector("#preview-grid"),
    previewState: document.querySelector("#preview-state"),
    refresh: document.querySelector("#refresh"),
  };

  function readChanges() {
    try {
      const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      return value && typeof value === "object" && !Array.isArray(value) ? value : {};
    } catch {
      return {};
    }
  }

  function safeStatus(value) {
    return Object.hasOwn(STATUS_LABELS, value) ? value : "new";
  }

  function statusFor(record) {
    return safeStatus(state.changes[record.id]?.status || record.status);
  }

  function detailsFor(record) {
    const change = state.changes[record.id];
    return change && typeof change === "object" ? change : {};
  }

  function escapeHtml(value = "") {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function filteredRecords() {
    const query = state.query.trim().toLocaleLowerCase("en-US");
    return state.records.filter((record) => {
      const category = record.category || "Other";
      const haystack = `${record.businessName} ${category} ${record.location}`.toLocaleLowerCase("en-US");
      return (
        (!query || haystack.includes(query)) &&
        (state.statusFilter === "all" || state.statusFilter === statusFor(record)) &&
        (state.categoryFilter === "all" || state.categoryFilter === category)
      );
    });
  }

  function renderMetrics() {
    const counts = state.records.reduce(
      (result, record) => {
        const status = statusFor(record);
        result.total += 1;
        if (status === "new") result.open += 1;
        if (status !== "new") result.contacted += 1;
        if (status === "interested" || status === "approved") result.interested += 1;
        return result;
      },
      { total: 0, open: 0, contacted: 0, interested: 0 }
    );
    els.total.textContent = counts.total;
    els.open.textContent = counts.open;
    els.contacted.textContent = counts.contacted;
    els.interested.textContent = counts.interested;
  }

  function renderCategoryFilter() {
    const categories = [...new Set(state.records.map((record) => record.category || "Other"))]
      .sort((a, b) => a.localeCompare(b, "en"));
    els.categoryFilter.innerHTML = `<option value="all">All categories</option>${categories
      .map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`)
      .join("")}`;
  }

  function renderLeadList() {
    const records = filteredRecords();
    if (!records.some((record) => record.id === state.selectedId)) {
      state.selectedId = records.length ? records[0].id : null;
    }
    els.leadList.innerHTML = records.length
      ? records.map((record) => {
          const status = statusFor(record);
          const score = Number.isFinite(record.score) ? `${record.score}/100` : "Unscored";
          const hasDesktop = SAFE_DESKTOP_MOCKUP.test(record.desktopMockup || "");
          const hasMobile = SAFE_MOBILE_MOCKUP.test(record.mobileMockup || "");
          const previewLabel = hasDesktop && hasMobile
            ? "Desktop + mobile mockups"
            : (hasDesktop || hasMobile ? "Partial mockup set" : "Mockups unavailable");
          return `
            <button class="lead-item ${state.selectedId === record.id ? "is-active" : ""}" type="button" data-id="${escapeHtml(record.id)}">
              <span class="status-badge ${status}">${STATUS_LABELS[status]}</span>
              <strong>${escapeHtml(record.businessName)}</strong>
              <span class="lead-meta"><span>${escapeHtml(record.category || "Other")}</span><span>${escapeHtml(record.location || "Local area")}</span></span>
              <span class="lead-line"><span>${score}</span><span>${previewLabel}</span></span>
            </button>`;
        }).join("")
      : `<p class="feedback">No leads match these filters.</p>`;
  }

  function selectedRecord() {
    return state.records.find((record) => record.id === state.selectedId);
  }

  function formatDate(value) {
    if (!value) return "";
    const date = new Date(value);
    return Number.isNaN(date.valueOf()) ? String(value) : date.toLocaleDateString("en-US");
  }

  function renderPreviews(record) {
    const desktopMockup = typeof record.desktopMockup === "string" && SAFE_DESKTOP_MOCKUP.test(record.desktopMockup)
      ? record.desktopMockup
      : "";
    const mobileMockup = typeof record.mobileMockup === "string" && SAFE_MOBILE_MOCKUP.test(record.mobileMockup)
      ? record.mobileMockup
      : "";
    const previewKey = JSON.stringify([record.id, desktopMockup, mobileMockup]);
    if (state.previewKey === previewKey) return;
    state.previewKey = previewKey;

    const safeBusinessName = escapeHtml(record.businessName);
    if (desktopMockup || mobileMockup) {
      const cards = [];
      els.previewHeading.textContent = "Static responsive mockups";
      els.previewDescription.textContent = "Dedicated local PNG assets present the proposed desktop and mobile directions without loading executable page content.";
      els.previewState.textContent = desktopMockup && mobileMockup ? "Desktop + mobile PNG" : "Partial mockup set";

      if (desktopMockup) {
        cards.push(`
        <article class="preview-card desktop-mockup-card">
          <div class="browser-bar" aria-hidden="true">
            <span class="browser-dots"><i></i><i></i><i></i></span>
            <span class="browser-address">sitekapinda.local · desktop concept</span>
          </div>
          <div class="mockup-scroll desktop-mockup-scroll">
            <img class="preview-image desktop-mockup-image" src="${escapeHtml(desktopMockup)}" alt="Static desktop mockup of ${safeBusinessName}" loading="lazy" decoding="async" referrerpolicy="no-referrer">
          </div>
          <div class="preview-caption"><strong>Desktop mockup</strong><span>Static PNG · scroll to inspect</span></div>
        </article>`);
      } else {
        cards.push(missingPreviewCard("Desktop mockup"));
      }

      if (mobileMockup) {
        cards.push(`
        <article class="preview-card phone-mockup-card">
          <div class="preview-caption preview-caption-top"><strong>Mobile mockup</strong><span>Dedicated phone composition</span></div>
          <div class="phone-stage">
            <div class="phone-device">
              <div class="mobile-speaker" aria-hidden="true"></div>
              <div class="phone-screen mockup-scroll">
                <img class="preview-image mobile-mockup-image" src="${escapeHtml(mobileMockup)}" alt="Static mobile mockup of ${safeBusinessName}" loading="lazy" decoding="async" referrerpolicy="no-referrer">
              </div>
              <div class="mobile-home-indicator" aria-hidden="true"></div>
            </div>
          </div>
        </article>`);
      } else {
        cards.push(missingPreviewCard("Mobile mockup"));
      }

      els.previewGrid.innerHTML = cards.join("");
      return;
    }

    els.previewHeading.textContent = "Mockups unavailable";
    els.previewDescription.textContent = "No packaged desktop or mobile mockup is available for this lead.";
    els.previewState.textContent = "No static assets";
    els.previewGrid.innerHTML = `
      <div class="preview-empty">
        <div>
          <strong>No static mockups are available for this lead.</strong>
          <p>Add both approved PNG assets to review the desktop and mobile directions here.</p>
        </div>
      </div>`;
  }

  function missingPreviewCard(label) {
    return `
      <div class="preview-empty preview-empty-compact">
        <div><strong>${escapeHtml(label)} unavailable.</strong><p>Add the matching local PNG to complete this preview set.</p></div>
      </div>`;
  }

  function renderDetail() {
    const record = selectedRecord();
    if (!record) {
      els.empty.hidden = false;
      els.detailContent.hidden = true;
      return;
    }

    const status = statusFor(record);
    const details = detailsFor(record);
    els.empty.hidden = true;
    els.detailContent.hidden = false;
    els.detailName.textContent = record.businessName;
    els.detailMeta.textContent = `${record.category || "Other"} · ${record.location || "Local area"}`;
    els.statusPill.textContent = STATUS_LABELS[status];
    els.statusPill.className = status;
    els.contactedCheck.checked = status !== "new";
    els.statusSelect.value = status;
    els.note.value = Object.hasOwn(details, "note") ? details.note : (record.note || "");
    els.feedback.textContent = details.savedAt ? `Saved locally ${new Date(details.savedAt).toLocaleString("en-US")}` : "";
    els.phone.textContent = record.phone || "Not recorded";
    els.websiteEvidence.textContent = record.websiteEvidence || "Not recorded";
    els.evidenceScore.textContent = Number.isFinite(record.score) ? `${record.score}/100` : "Unscored";
    els.nextAction.textContent = record.nextActionAt || "Human review";
    els.createdAt.textContent = formatDate(record.createdAt);
    els.selectionReason.textContent = record.selectionReason || "No lead rationale is available.";
    renderPreviews(record);
  }

  function render() {
    renderMetrics();
    renderLeadList();
    renderDetail();
  }

  function saveSelectedStatus() {
    const record = selectedRecord();
    if (!record) return;
    const status = safeStatus(els.statusSelect.value);
    state.changes[record.id] = {
      status,
      note: els.note.value.trim(),
      savedAt: new Date().toISOString(),
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.changes));
      render();
      els.feedback.textContent = "Saved in this browser only.";
    } catch {
      els.feedback.textContent = "Browser storage is unavailable; the pipeline data was not changed.";
    }
  }

  function buildMessage(record) {
    return `Hi, this is SiteKapında. Our deterministic review identified a website opportunity for ${record.businessName}, so we prepared a private local concept before asking you to commit. May I share the preview for your review?`;
  }

  async function copyText(value) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(value);
      return;
    }
    const temporary = document.createElement("textarea");
    temporary.value = value;
    temporary.setAttribute("readonly", "");
    temporary.style.position = "fixed";
    temporary.style.opacity = "0";
    document.body.appendChild(temporary);
    temporary.select();
    document.execCommand("copy");
    temporary.remove();
  }

  els.leadList.addEventListener("click", (event) => {
    const button = event.target.closest(".lead-item");
    if (!button) return;
    state.selectedId = button.dataset.id;
    render();
  });

  els.search.addEventListener("input", () => {
    state.query = els.search.value;
    render();
  });

  els.statusFilter.addEventListener("change", () => {
    state.statusFilter = els.statusFilter.value;
    render();
  });

  els.categoryFilter.addEventListener("change", () => {
    state.categoryFilter = els.categoryFilter.value;
    render();
  });

  els.contactedCheck.addEventListener("change", () => {
    els.statusSelect.value = els.contactedCheck.checked ? "contacted" : "new";
  });

  els.statusSelect.addEventListener("change", () => {
    els.contactedCheck.checked = els.statusSelect.value !== "new";
  });

  els.save.addEventListener("click", saveSelectedStatus);
  els.copy.addEventListener("click", async () => {
    const record = selectedRecord();
    if (!record) return;
    try {
      await copyText(buildMessage(record));
      els.feedback.textContent = "Outreach copied.";
    } catch {
      els.feedback.textContent = "Select and copy the outreach text from your browser clipboard controls.";
    }
  });

  els.refresh.addEventListener("click", () => {
    state.query = "";
    state.statusFilter = "all";
    state.categoryFilter = "all";
    els.search.value = "";
    els.statusFilter.value = "all";
    els.categoryFilter.value = "all";
    render();
  });

  if (state.records.length) state.selectedId = state.records[0].id;
  renderCategoryFilter();
  render();
})();
