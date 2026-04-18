import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Phase 1: Bootstrap CDN
content = content.replace(
    '  <script src="https://unpkg.com/sortablejs@1.15.2/Sortable.min.js"></script>\n  <link rel="stylesheet" href="style.css" />',
    '  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">\n  <script src="https://unpkg.com/sortablejs@1.15.2/Sortable.min.js"></script>\n  <link rel="stylesheet" href="style.css" />'
)
content = content.replace(
    '</script>\n</body>',
    '</script>\n<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>\n</body>'
)

# Phase 2: API path fix + Bootstrap Offcanvas init
content = content.replace(
    "  const API = 'http://localhost:5000/api';",
    "  const API = '/api';"
)
content = content.replace(
    "  let TWD_RATE = parseFloat(localStorage.getItem('twd_rate') || '0.21');",
    "  let TWD_RATE = parseFloat(localStorage.getItem('twd_rate') || '0.21');\n\n  /* ── Bootstrap Offcanvas instances ─────────────────────────────────── */\n  const bsModal = () => bootstrap.Offcanvas.getOrCreateInstance(document.getElementById('modal'));\n  const bsTripModal = () => bootstrap.Offcanvas.getOrCreateInstance(document.getElementById('trip-modal'));\n  const bsExpenseModal = () => bootstrap.Offcanvas.getOrCreateInstance(document.getElementById('expense-modal'));\n  const bsTransitSheet = () => bootstrap.Offcanvas.getOrCreateInstance(document.getElementById('transit-sheet'));"
)

# Phase 3: Form class replacements - Itinerary modal
old_itinerary_form = '''      <input type="hidden" id="edit-item-id" />
      <div class="form-group">
        <label class="form-label">景點名稱 *</label>
        <input class="form-input" id="f-name" type="text" placeholder="例：淺草寺" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">日期</label>
          <input class="form-input" id="f-date" type="date" />
        </div>
        <div class="form-group">
          <label class="form-label">時間</label>
          <input class="form-input" id="f-time" type="text" placeholder="09:00" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">類型</label>
        <select class="form-select" id="f-type">
          <option value="">— 選擇 —</option>
          <option>🏛️ 景點</option>
          <option>🍽️ 餐廳</option>
          <option>🚉 交通</option>
          <option>🏨 住宿</option>
          <option>🛍️ 購物</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">地址</label>
        <input class="form-input" id="f-address" type="text" placeholder="地址" />
      </div>
      <div class="form-group">
        <label class="form-label">Google Maps 連結</label>
        <input class="form-input" id="f-maps" type="url" placeholder="https://maps.google.com/..." />
      </div>
      <div class="form-group">
        <label class="form-label">預估費用（JPY）</label>
        <input class="form-input" id="f-cost" type="number" placeholder="0" />
      </div>
      <div class="form-group">
        <label class="form-label">備註</label>
        <textarea class="form-textarea" id="f-notes" placeholder="備註..."></textarea>
      </div>
      <div class="form-group" id="f-done-row" style="display:none;">
        <label style="display:flex;align-items:center;gap:8px;cursor:pointer;font-size:14px;">
          <input type="checkbox" id="f-done" style="width:18px;height:18px;accent-color:var(--purple1);" />
          已完成
        </label>
      </div>
      <div class="btn-row" id="modal-btn-row">
        <button class="btn btn-primary" id="modal-save-btn">儲存</button>
      </div>'''

new_itinerary_form = '''      <input type="hidden" id="edit-item-id" />
      <div class="mb-3">
        <label class="form-label small fw-semibold">景點名稱 *</label>
        <input class="form-control" id="f-name" type="text" placeholder="🔍 搜尋景點名稱..." autocomplete="off" />
      </div>
      <div class="row g-2">
        <div class="col mb-3">
          <label class="form-label small fw-semibold">日期</label>
          <input class="form-control" id="f-date" type="date" />
        </div>
        <div class="col mb-3">
          <label class="form-label small fw-semibold">時間</label>
          <input class="form-control" id="f-time" type="text" placeholder="09:00" />
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label small fw-semibold">類型</label>
        <select class="form-select" id="f-type">
          <option value="">— 選擇 —</option>
          <option>🏛️ 景點</option>
          <option>🍽️ 餐廳</option>
          <option>🚉 交通</option>
          <option>🏨 住宿</option>
          <option>🛍️ 購物</option>
        </select>
      </div>
      <div class="mb-3">
        <label class="form-label small fw-semibold">地址</label>
        <input class="form-control" id="f-address" type="text" placeholder="地址" />
      </div>
      <div class="mb-3">
        <label class="form-label small fw-semibold">Google Maps 連結</label>
        <input class="form-control" id="f-maps" type="url" placeholder="https://maps.google.com/..." />
      </div>
      <div class="mb-3">
        <label class="form-label small fw-semibold">預估費用（JPY）</label>
        <input class="form-control" id="f-cost" type="number" placeholder="0" />
      </div>
      <div class="mb-3">
        <label class="form-label small fw-semibold">備註</label>
        <textarea class="form-control" id="f-notes" placeholder="備註..." rows="3"></textarea>
      </div>
      <div class="mb-3" id="f-done-row" style="display:none;">
        <label class="d-flex align-items-center gap-2" style="cursor:pointer;font-size:14px;">
          <input type="checkbox" id="f-done" style="width:18px;height:18px;accent-color:var(--purple1);" />
          已完成
        </label>
      </div>
      <div class="d-flex gap-2 mt-4" id="modal-btn-row">
        <button class="btn btn-danger flex-fill" id="modal-save-btn">儲存</button>
      </div>'''

content = content.replace(old_itinerary_form, new_itinerary_form)

# Trip modal form
old_trip_form = '''      <input type="hidden" id="t-id" />
      <div class="form-group">
        <label class="form-label">旅程名稱 *</label>
        <input class="form-input" id="t-name" type="text" placeholder="例：2025 東京之旅" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">出發日期</label>
          <input class="form-input" id="t-start" type="date" />
        </div>
        <div class="form-group">
          <label class="form-label">回程日期</label>
          <input class="form-input" id="t-end" type="date" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">人數</label>
          <input class="form-input" id="t-people" type="number" placeholder="2" />
        </div>
        <div class="form-group">
          <label class="form-label">總預算（TWD）</label>
          <input class="form-input" id="t-budget" type="number" placeholder="50000" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">狀態</label>
        <select class="form-select" id="t-status">
          <option value="計畫中">計畫中</option>
          <option value="確認">確認</option>
          <option value="完成">完成</option>
        </select>
      </div>
      <div class="btn-row" id="trip-btn-row">
        <button class="btn btn-primary" id="trip-save-btn">建立旅程</button>
      </div>'''

new_trip_form = '''      <input type="hidden" id="t-id" />
      <div class="mb-3">
        <label class="form-label small fw-semibold">旅程名稱 *</label>
        <input class="form-control" id="t-name" type="text" placeholder="例：2025 東京之旅" />
      </div>
      <div class="row g-2">
        <div class="col mb-3">
          <label class="form-label small fw-semibold">出發日期</label>
          <input class="form-control" id="t-start" type="date" />
        </div>
        <div class="col mb-3">
          <label class="form-label small fw-semibold">回程日期</label>
          <input class="form-control" id="t-end" type="date" />
        </div>
      </div>
      <div class="row g-2">
        <div class="col mb-3">
          <label class="form-label small fw-semibold">人數</label>
          <input class="form-control" id="t-people" type="number" placeholder="2" />
        </div>
        <div class="col mb-3">
          <label class="form-label small fw-semibold">總預算（TWD）</label>
          <input class="form-control" id="t-budget" type="number" placeholder="50000" />
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label small fw-semibold">狀態</label>
        <select class="form-select" id="t-status">
          <option value="計畫中">計畫中</option>
          <option value="確認">確認</option>
          <option value="完成">完成</option>
        </select>
      </div>
      <div class="d-flex gap-2 mt-4" id="trip-btn-row">
        <button class="btn btn-danger flex-fill" id="trip-save-btn">建立旅程</button>
      </div>'''

content = content.replace(old_trip_form, new_trip_form)

# Expense modal form
old_expense_form = '''      <input type="hidden" id="e-id" />
      <div class="form-group">
        <label class="form-label">項目名稱 *</label>
        <input class="form-input" id="e-name" type="text" placeholder="例：晚餐" />
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">金額（JPY）</label>
          <input class="form-input" id="e-amount" type="number" placeholder="0" />
        </div>
        <div class="form-group">
          <label class="form-label">日期</label>
          <input class="form-input" id="e-date" type="date" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">類別</label>
          <select class="form-select" id="e-category">
            <option value="">— 選擇 —</option>
            <option>🍽️ 餐飲</option>
            <option>🚌 交通</option>
            <option>🏨 住宿</option>
            <option>🎡 娛樂</option>
            <option>🛍️ 購物</option>
            <option>💊 醫療</option>
            <option>📦 其他</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">付款人</label>
          <input class="form-input" id="e-payer" type="text" placeholder="姓名" />
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">備註</label>
        <textarea class="form-textarea" id="e-notes" placeholder="備註..." style="min-height:56px;"></textarea>
      </div>
      <div class="btn-row" id="expense-btn-row">
        <button class="btn btn-primary" id="expense-save-btn">儲存</button>
      </div>'''

new_expense_form = '''      <input type="hidden" id="e-id" />
      <div class="mb-3">
        <label class="form-label small fw-semibold">項目名稱 *</label>
        <input class="form-control" id="e-name" type="text" placeholder="例：晚餐" />
      </div>
      <div class="row g-2">
        <div class="col mb-3">
          <label class="form-label small fw-semibold">金額（JPY）</label>
          <input class="form-control" id="e-amount" type="number" placeholder="0" />
        </div>
        <div class="col mb-3">
          <label class="form-label small fw-semibold">日期</label>
          <input class="form-control" id="e-date" type="date" />
        </div>
      </div>
      <div class="row g-2">
        <div class="col mb-3">
          <label class="form-label small fw-semibold">類別</label>
          <select class="form-select" id="e-category">
            <option value="">— 選擇 —</option>
            <option>🍽️ 餐飲</option>
            <option>🚌 交通</option>
            <option>🏨 住宿</option>
            <option>🎡 娛樂</option>
            <option>🛍️ 購物</option>
            <option>💊 醫療</option>
            <option>📦 其他</option>
          </select>
        </div>
        <div class="col mb-3">
          <label class="form-label small fw-semibold">付款人</label>
          <input class="form-control" id="e-payer" type="text" placeholder="姓名" />
        </div>
      </div>
      <div class="mb-3">
        <label class="form-label small fw-semibold">備註</label>
        <textarea class="form-control" id="e-notes" placeholder="備註..." rows="2"></textarea>
      </div>
      <div class="d-flex gap-2 mt-4" id="expense-btn-row">
        <button class="btn btn-danger flex-fill" id="expense-save-btn">儲存</button>
      </div>'''

content = content.replace(old_expense_form, new_expense_form)

# Phase 4: Modal -> Offcanvas HTML structure
content = content.replace(
    '<div id="modal-overlay">\n  <div id="modal">\n    <div class="modal-handle"></div>\n    <div class="modal-header">\n      <span class="modal-title" id="modal-title">新增行程</span>\n      <button class="modal-close" id="modal-close-btn">✕</button>\n    </div>\n    <div class="modal-body">',
    '<div class="offcanvas offcanvas-bottom" id="modal" tabindex="-1" style="border-radius:22px 22px 0 0;max-height:92vh;">\n  <div class="modal-handle"></div>\n  <div class="offcanvas-header border-bottom pb-3">\n    <span class="fw-bold fs-6" id="modal-title">新增行程</span>\n    <button type="button" class="btn-close" id="modal-close-btn" data-bs-dismiss="offcanvas"></button>\n  </div>\n  <div class="offcanvas-body">'
)

content = content.replace(
    '    </div>\n  </div>\n</div>\n\n<!-- ── TRIP MODAL',
    '  </div>\n</div>\n\n<!-- ── TRIP MODAL'
)

content = content.replace(
    '<div id="trip-modal-overlay">\n  <div id="trip-modal">\n    <div class="modal-handle"></div>\n    <div class="modal-header">\n      <span class="modal-title" id="trip-modal-title">新增旅程</span>\n      <button class="modal-close" id="trip-modal-close">✕</button>\n    </div>\n    <div class="modal-body">',
    '<div class="offcanvas offcanvas-bottom" id="trip-modal" tabindex="-1" style="border-radius:22px 22px 0 0;max-height:85vh;">\n  <div class="modal-handle"></div>\n  <div class="offcanvas-header border-bottom pb-3">\n    <span class="fw-bold fs-6" id="trip-modal-title">新增旅程</span>\n    <button type="button" class="btn-close" id="trip-modal-close" data-bs-dismiss="offcanvas"></button>\n  </div>\n  <div class="offcanvas-body">'
)

content = content.replace(
    '<div id="expense-modal-overlay">\n  <div id="expense-modal">\n    <div class="modal-handle"></div>\n    <div class="modal-header">\n      <span class="modal-title">新增費用</span>\n      <button class="modal-close" id="expense-modal-close">✕</button>\n    </div>\n    <div class="modal-body">',
    '<div class="offcanvas offcanvas-bottom" id="expense-modal" tabindex="-1" style="border-radius:22px 22px 0 0;max-height:85vh;">\n  <div class="modal-handle"></div>\n  <div class="offcanvas-header border-bottom pb-3">\n    <span class="fw-bold fs-6">新增費用</span>\n    <button type="button" class="btn-close" id="expense-modal-close" data-bs-dismiss="offcanvas"></button>\n  </div>\n  <div class="offcanvas-body">'
)

content = content.replace(
    '<div id="transit-overlay">\n  <div id="transit-sheet">\n    <div class="modal-handle"></div>\n    <div class="modal-header">',
    '<div class="offcanvas offcanvas-bottom" id="transit-sheet" tabindex="-1" style="border-radius:22px 22px 0 0;max-height:78vh;">\n  <div class="modal-handle"></div>\n  <div class="offcanvas-header border-bottom pb-3">'
)

content = content.replace(
    '      <button class="modal-close" id="transit-close-btn">✕</button>',
    '    <button type="button" class="btn-close" id="transit-close-btn" data-bs-dismiss="offcanvas"></button>'
)

# Remove old overlay click listeners (Bootstrap handles backdrop)
old_overlay_listeners = '''  document.getElementById('modal-overlay').addEventListener('click', e => {
    if (e.target === document.getElementById('modal-overlay')) closeModal();
  });
  document.getElementById('trip-modal-overlay').addEventListener('click', e => {
    if (e.target === document.getElementById('trip-modal-overlay')) closeTripModal();
  });
  document.getElementById('expense-modal-overlay').addEventListener('click', e => {
    if (e.target === document.getElementById('expense-modal-overlay')) closeExpenseModal();
  });
  document.getElementById('transit-overlay').addEventListener('click', e => {
    if (e.target === document.getElementById('transit-overlay')) closeTransitSheet();
  });'''

content = content.replace(old_overlay_listeners, '  // Bootstrap Offcanvas handles backdrop click automatically')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("done")
