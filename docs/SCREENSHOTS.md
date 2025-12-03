# Screenshots Guide

This document provides guidance on capturing screenshots for the Local Council Data Explorer project documentation.

---

## 📸 Required Screenshots

The following screenshots should be captured and added to this folder for complete documentation:

### 1. Dashboard Overview

**Filename:** `dashboard.png`

**Content:** Main application view showing the layout with navigation tabs.

**Capture Instructions:**
- Open the application at `http://localhost:5173` (or Docker at `http://localhost:3000`)
- Ensure the "Bins" tab is selected (default view)
- Capture the full browser viewport

**Recommended Resolution:** 1920 × 1080 (Full HD)

---

### 2. Bin Collections Panel

**Filename:** `bins.png`

**Content:** Bin collections view showing:
- Address display
- Council name
- List of upcoming bin collections
- Chart showing days until each collection
- Any Today/Tomorrow badges if applicable

**Capture Instructions:**
- Navigate to the "Bins" tab
- Wait for data to load
- If mock mode is enabled, default data will appear
- Capture the full panel content

**Recommended Resolution:** 1280 × 800 or full viewport

---

### 3. Planning Applications Panel

**Filename:** `planning.png`

**Content:** Planning applications view showing:
- LPA (Local Planning Authority) name
- List of planning applications
- Application references, addresses, proposals
- Status indicators
- Dates (received, decision if available)

**Capture Instructions:**
- Navigate to the "Planning" tab
- Wait for data to load
- Ensure at least 2-3 applications are visible
- Capture the full panel content

**Recommended Resolution:** 1280 × 900 or full viewport

---

### 4. Air Quality Panel

**Filename:** `air-quality.png`

**Content:** Air quality view showing:
- Area name
- DAQI (Daily Air Quality Index) value
- Summary band (Low/Moderate/High/Very High)
- Pollutant breakdown with values
- Color-coded indicators

**Capture Instructions:**
- Navigate to the "Air Quality" tab
- Wait for data to load
- Capture the full panel including all pollutant readings

**Recommended Resolution:** 1280 × 800 or full viewport

---

### 5. API Documentation (Swagger)

**Filename:** `api-docs.png`

**Content:** Swagger UI showing:
- API title and description
- Available endpoints grouped by category
- At least one expanded endpoint showing parameters

**Capture Instructions:**
- Open `http://localhost:8000/docs`
- Expand one endpoint (e.g., `/api/bins`)
- Capture showing both the endpoint list and expanded details

**Recommended Resolution:** 1920 × 1080

---

### 6. API Documentation (ReDoc) - Optional

**Filename:** `api-redoc.png`

**Content:** ReDoc documentation showing the API reference.

**Capture Instructions:**
- Open `http://localhost:8000/redoc`
- Capture the overview section

**Recommended Resolution:** 1920 × 1080

---

## 📐 Screenshot Specifications

### Recommended Settings

| Setting | Value |
|---------|-------|
| Format | PNG (preferred) or JPEG |
| Quality | Maximum |
| DPI | 144 (Retina) or 72 (standard) |
| Color Mode | RGB |

### Recommended Resolutions

| Screenshot Type | Resolution |
|-----------------|------------|
| Full application | 1920 × 1080 |
| Individual panels | 1280 × 800 |
| Mobile views | 375 × 667 (iPhone) |
| API documentation | 1920 × 1080 |

### Browser Settings for Capture

1. **Hide browser bookmarks bar** for cleaner screenshots
2. **Use incognito/private mode** to avoid extension clutter
3. **Set zoom to 100%** for consistent sizing
4. **Use a neutral browser theme** (light mode recommended)

---

## 🛠️ How to Capture Screenshots

### macOS

- **Full screen:** `Cmd + Shift + 3`
- **Selection:** `Cmd + Shift + 4`
- **Window:** `Cmd + Shift + 4`, then `Space`, then click window

### Windows

- **Full screen:** `Win + PrtScn`
- **Selection:** `Win + Shift + S`
- **Window:** `Alt + PrtScn`

### Browser DevTools

1. Open DevTools (`F12` or `Cmd/Ctrl + Shift + I`)
2. Press `Cmd/Ctrl + Shift + P`
3. Type "screenshot"
4. Select "Capture full size screenshot" or "Capture screenshot"

### Command Line Tools

```bash
# macOS using screencapture
screencapture -T 3 screenshot.png

# Chrome/Chromium headless
chrome --headless --screenshot=output.png --window-size=1920,1080 http://localhost:5173
```

---

## 📁 File Organization

After capturing screenshots, place them in this directory with the following structure:

```
docs/
└── screenshots/
    ├── README.md          # This file
    ├── dashboard.png      # Main dashboard view
    ├── bins.png           # Bin collections panel
    ├── planning.png       # Planning applications panel
    ├── air-quality.png    # Air quality panel
    └── api-docs.png       # Swagger UI documentation
```

---

## 🔄 Updating Main README

After adding screenshots, update the main `README.md` to reference them:

```markdown
## 📸 Screenshots

| Bin Collections | Planning Applications | Air Quality |
|-----------------|----------------------|-------------|
| ![Bins Screenshot](./docs/screenshots/bins.png) | ![Planning Screenshot](./docs/screenshots/planning.png) | ![Air Quality Screenshot](./docs/screenshots/air-quality.png) |
```

---

## ✅ Screenshot Checklist

Use this checklist to ensure all required screenshots are captured:

- [ ] Dashboard overview (`dashboard.png`)
- [ ] Bin collections panel (`bins.png`)
- [ ] Planning applications panel (`planning.png`)
- [ ] Air quality panel (`air-quality.png`)
- [ ] API documentation - Swagger (`api-docs.png`)
- [ ] API documentation - ReDoc (`api-redoc.png`) - *optional*

---

## 📋 Notes

- Screenshots should show **realistic data** (mock mode is fine)
- Avoid showing any **sensitive information** or API keys
- Ensure the application is in a **"clean" state** with loaded data
- Consider capturing both **light and dark modes** if supported
- For portfolio use, ensure screenshots are **visually appealing**

---

*Screenshots help recruiters and users quickly understand the application's functionality without having to set up the project.*
