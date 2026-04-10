# smalltalk-vending

Static, dependency-free frontend for a Korean small-talk vending machine UI.

## Correction Pass

This version explicitly corrects the earlier mismatch with the request:

- Rebuilt the app around a more realistic vending machine silhouette: tall blue cabinet, large left glass window, narrow right control area, and bottom pickup door
- Replaced abstract topic cards with stocked shelf items that read more like cans and bottles behind glass
- Removed visible English branding, English topic names, and A1/B2-style labels from the interface
- Kept the existing behavior: topic selection, Korean prompt output, random/행운 actions, and local history
- Shifted the right side toward a real machine feel with a small display, numeric-style buttons, and payment hardware details

## Features

- Desktop-style vending machine UI (`index.html`)
- Mobile-first vending machine UI (`mobile.html`)
- Eight Korean small-talk topics shown as shelf products
- 3-5 Korean conversation starters per dispense
- Topic selection from the product window or the control pad
- `랜덤`, `행운`, and `확인` actions
- Local-only history stored in `localStorage`
- Runs directly in the browser with no build step

## Run

Option 1:

```bash
python3 -m http.server 4173
```

Then open one of these:

- Desktop: `http://localhost:4173/index.html`
- Mobile: `http://localhost:4173/mobile.html`

Option 2:

Open `index.html` or `mobile.html` directly in a browser.

## Validation

JavaScript syntax:

```bash
node --check app.js
```

Lightweight static sanity check:

```bash
node - <<'NODE'
const fs = require('fs');
const js = fs.readFileSync('app.js', 'utf8');
['index.html', 'mobile.html'].forEach((file) => {
  const html = fs.readFileSync(file, 'utf8');
  ['topic-grid','selection-pad','prompt-window','history-list','machine-status','confirm-button','coin-button','pickup-toggle'].forEach((id) => {
    if (!html.includes(`id="${id}"`)) throw new Error(`${file}: Missing ${id}`);
  });
  ['A1','B2','labelEn','conversation vending machine'].forEach((text) => {
    if (html.includes(text) || js.includes(text)) throw new Error(`${file}: Unexpected legacy label ${text}`);
  });
});
console.log('static structure ok');
NODE
```

## Notes

- No backend is used.
- All history remains in the current browser only.
- `mobile.html` is a dedicated mobile layout, not just a squeezed desktop page.
