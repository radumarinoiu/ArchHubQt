I want you to start building the app with the following specs, but let me know if there's anything more you think you need or are unsure about:

# Core Layout
## Main Window
- Has a sidebar on the left
- Has a main viewport (the rest of the layout)

## The sidebar
- Header: I want 3 counters here, total packages installed, number of installed aur packages, number of updates available, side by side on a single line, each with their own bounding box
Then the following need to be a list of headers with sub-options:
- Packages
  - All Packages (installed)
  - Pacman (installed)
  - AUR (installed)
  - Search Packages (this should look like a button but become a search bar when you hover on it)
- Updates
- Mirrors
- Find Orphans
- Clear Cache
- Settings

`By default, you'll have All Packages selected when the app opens, and that's what's going to be open in the main window's viewport.`

# Sidebar Elements that open in the Main Viewport
## The packages page (shared across all the sub-options)
- Package Grid with infinite scroll
- When a package is selected, open a new component for package details.
- If the width allows, keep the package details as a split window on the right part of the main viewport. Keep it as a sidebar as long as 1 package column can still fit on the left, and when it doesn't, make the package details fill the main viewport.

## Package details page
- First row: Version, install size, last updated, maintainer
- Second row - multiple tabs:
  - Details
  - Dependencies, Optional Deps, Conflicts (separate tabs, clickable package names, should allow navigation, but keep a method of going "back")

## Updates Page
- Provide a toggle between pacman-only and all updates (including AUR)
- Provide an Arch News page preview inside the app
- Total Download Size and install size delta after install
- Update Selected / Update all buttons

## Mirrors Page
- Should basically be a small UI for reflector (Arch Linux App)
- Should provide a button to run reflector and render the outputs here
- Do not implement this page yet.

## Find Orphans Page
- Find orphaned packages, similar in style with the updates page but the buttons should be remove selected / remove all

## Clear Cache Page
- First Row/Rows: Simple Cache stats (size, number of packages, old versions, uninstalled, etc.)
- Quick Clean
- Selective Clean

## Settings Page
- Enable/Disable integration of all supported AUR Helpers (if none selected, then hide all AUR functionality in the app)
- Configurable Parallel Downloads
- Pacman Config - Shortcut
- Mirror List - Shortcut